"""ANSYS Unified MCP 2.0 - DPF 沙盒隔離結果讀取器 (DPFSandboxReader).

落實「終態 (TERMINAL) 後 + Sandbox 副本」隔離原則：
1. 嚴格檢查作業是否處於終態 (SOLVED, FAILED, ABORTED)，未完工則阻斷拋出 JobNotReadyError。
2. 搜尋主 .rst 結果檔並複製至 .dpf_cache/isolated_result.rst，杜絕 Windows 求解器檔案鎖衝突。
3. 透過 ansys.dpf.core.Model 開啟副本進行無頭場數據提取（等效應力、位移、模態頻率）。
4. 在 finally 區塊中嚴格調用 release_streams() 釋放二進位串流與檔案句柄。
5. 實施無伺服器環境之安全回退：allow_synthetic=True 回傳標記指標，allow_synthetic=False 拋出 PostprocessingError。
"""

from __future__ import annotations

import logging
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional, Union

import numpy as np

from ansys_unified_mcp.postprocessing.base import (
    BaseResultReader,
    JobNotReadyError,
    PostprocessingError,
    TERMINAL_STATES,
)

logger = logging.getLogger(__name__)


class DPFSandboxReader(BaseResultReader):
    """基於 PyAnsys DPF 之沙盒隔離結果讀取器。"""

    def locate_primary_rst(self, job_dir: Path) -> Optional[Path]:
        """在作業目錄中定位主要 .rst 結果檔案（排除 .dpf_cache 目錄）。"""
        all_rst: List[Path] = []
        for p in job_dir.rglob("*"):
            if p.is_file() and p.suffix.lower() == ".rst" and ".dpf_cache" not in p.parts:
                all_rst.append(p)

        if not all_rst:
            return None

        # 優先挑選常見主檔名 file.rst 或 solve.rst，其次依檔案大小與修改時間排序
        def _sort_key(path: Path) -> tuple:
            name_lower = path.name.lower()
            is_preferred = name_lower in ("file.rst", "solve.rst")
            try:
                size = path.stat().st_size
                mtime = path.stat().st_mtime
            except OSError:
                size, mtime = 0, 0
            return (is_preferred, size, mtime)

        all_rst.sort(key=_sort_key, reverse=True)
        return all_rst[0]

    def copy_rst_to_cache(self, primary_rst: Path, job_dir: Path) -> Path:
        """將主要 .rst 複製至 .dpf_cache/isolated_result.rst 以隔離檔案鎖。"""
        cache_dir = job_dir / ".dpf_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        dest = cache_dir / "isolated_result.rst"
        shutil.copy2(primary_rst, dest)
        logger.info("已完成 .rst 副本隔離: %s -> %s", primary_rst, dest)
        return dest

    def _extract_field_results(self, model: Any) -> Dict[str, Any]:
        """從 DPF Model 物件提取應力、位移與模態分析結果。"""
        results: Dict[str, Any] = {}

        # 1. 提取 von-Mises 等效應力 (max, min, avg)
        stress_op = None
        if hasattr(model.results, "stress_von_mises"):
            stress_op = model.results.stress_von_mises()
        elif hasattr(model.results, "stress"):
            stress_op = model.results.stress()

        if stress_op is not None:
            stress_fc = stress_op.eval()
            if len(stress_fc) > 0:
                s_data = np.asarray(stress_fc[0].data, dtype=float)
                if s_data.size > 0:
                    results["stress_von_mises"] = {
                        "max": float(np.max(s_data)),
                        "min": float(np.min(s_data)),
                        "avg": float(np.mean(s_data)),
                        "unit": "Pa",
                    }

        # 2. 提取位移場 (total max, ux, uy, uz components)
        if hasattr(model.results, "displacement"):
            disp_op = model.results.displacement()
            disp_fc = disp_op.eval()
            if len(disp_fc) > 0:
                disp_data = np.asarray(disp_fc[0].data, dtype=float)
                if disp_data.ndim == 2 and disp_data.shape[1] >= 3:
                    norms = np.linalg.norm(disp_data[:, :3], axis=1)
                    results["displacement"] = {
                        "total_max": float(np.max(norms)),
                        "ux_max": float(np.max(np.abs(disp_data[:, 0]))),
                        "uy_max": float(np.max(np.abs(disp_data[:, 1]))),
                        "uz_max": float(np.max(np.abs(disp_data[:, 2]))),
                        "unit": "m",
                    }
                elif disp_data.size > 0:
                    results["displacement"] = {
                        "total_max": float(np.max(np.abs(disp_data))),
                        "ux_max": float(np.max(np.abs(disp_data))),
                        "uy_max": 0.0,
                        "uz_max": 0.0,
                        "unit": "m",
                    }

        # 3. 提取模態頻率與質量佔比 (若為模態分析)
        if (
            hasattr(model, "metadata")
            and hasattr(model.metadata, "time_freq_support")
            and model.metadata.time_freq_support is not None
        ):
            tfs = model.metadata.time_freq_support
            frequencies: List[float] = []
            if hasattr(tfs, "frequencies") and tfs.frequencies is not None:
                freq_data = getattr(tfs.frequencies, "data", tfs.frequencies)
                frequencies = [float(f) for f in freq_data]

            if frequencies:
                modal_dict: Dict[str, Any] = {"frequencies": frequencies}
                if hasattr(tfs, "get_cumulative_mass_fractions"):
                    try:
                        cmf = tfs.get_cumulative_mass_fractions()
                        modal_dict["effective_mass_ratio"] = cmf
                    except Exception:
                        pass
                results["modal"] = modal_dict

        return results

    def _synthetic_fallback(self) -> Dict[str, Any]:
        """建立符合標準結構之合成指標回傳字典。"""
        return {
            "is_synthetic": True,
            "mock_reason": "NO_DPF_SERVER_DETECTED",
            "stress_von_mises": {
                "max": 145.6,
                "min": 0.0,
                "avg": 42.5,
                "unit": "MPa",
            },
            "displacement": {
                "total_max": 0.42,
                "ux_max": 0.15,
                "uy_max": 0.22,
                "uz_max": 0.31,
                "unit": "mm",
            },
            "modal": {
                "frequencies": [124.5, 342.1, 567.8],
                "effective_mass_ratio": {"x": 0.92, "y": 0.91, "z": 0.94},
            },
        }

    def read_results(
        self,
        job_dir: Union[Path, str],
        allow_synthetic: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """以「終態 + 沙盒副本」隔離機制讀取 DPF 結果。

        Args:
            job_dir: 作業沙盒目錄。
            allow_synthetic: 若為 True，無伺服器或檔案時回傳合成指標；若為 False，嚴格拋出例外。
            **kwargs: 可選指定 job_status。

        Returns:
            Dict[str, Any]: 包含等效應力、位移、模態等欄位之字典。

        Raises:
            JobNotReadyError: 作業尚未完成。
            PostprocessingError: 缺少結果檔案或 DPF 解析錯誤。
        """
        job_path = Path(job_dir).resolve()
        job_status = kwargs.get("job_status")

        # 1. 檢驗終態閘門
        self.validate_terminal_state(job_path, job_status=job_status)

        # 2. 定位主 .rst 結果檔案
        primary_rst = self.locate_primary_rst(job_path)
        if primary_rst is None or not primary_rst.exists():
            if allow_synthetic:
                logger.info("未找到 .rst 檔案，回傳合成指標 (allow_synthetic=True)")
                return self._synthetic_fallback()
            raise PostprocessingError(
                f"在作業沙盒 '{job_path}' 中找不到可用的 .rst 結果檔案。"
            )

        # 3. 副本隔離至 .dpf_cache/isolated_result.rst
        rst_copy_path = self.copy_rst_to_cache(primary_rst, job_path)

        # 4. 嘗試動態引入 PyAnsys DPF 並載入模型
        try:
            import ansys.dpf.core as dpf
        except ImportError as exc:
            if allow_synthetic:
                return self._synthetic_fallback()
            raise PostprocessingError(f"未安裝 ansys-dpf-core 套件: {exc}") from exc

        model = None
        try:
            model = dpf.Model(str(rst_copy_path))
            field_results = self._extract_field_results(model)

            response: Dict[str, Any] = {
                "is_synthetic": False,
                "rst_path": str(rst_copy_path),
            }
            response.update(field_results)
            return response

        except Exception as exc:
            logger.warning("DPF 模型讀取失敗: %s", exc)
            if allow_synthetic:
                return self._synthetic_fallback()
            raise PostprocessingError(
                f"DPF 讀取結果失敗 (無伺服器或檔案損毀): {exc}"
            ) from exc

        finally:
            # 5. 確保在 finally 區塊中釋放串流與檔案句柄
            if model is not None:
                try:
                    if hasattr(model, "metadata") and hasattr(model.metadata, "release_streams"):
                        model.metadata.release_streams()
                        logger.debug("已成功調用 model.metadata.release_streams()")
                except Exception as rel_exc:
                    logger.warning("release_streams() 釋放時發生例外: %s", rel_exc)
