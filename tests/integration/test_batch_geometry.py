# -*- coding: utf-8 -*-
"""SpaceClaim / Geometry 批次執行模式測試 (batch_executor).

分兩層：
1. 單元層（預設執行）：以 mock 替換 drivers/sim_impl.call_tool，驗證批次分派邏輯、
   信封聚合、空清單與例外路徑，不需要真實 SpaceClaim 連線，隨時可跑。
2. 整合層（@pytest.mark.integration）：連線真實 SpaceClaim gRPC (127.0.0.1:50051)，
   實跑建立方塊 → 建立外流域 → 匯出 STEP 的批次序列，並量測逐點 RPC 對比批次執行的
   實測耗時倍數。若偵測不到 50051 埠開啟服務，自動 skip（不視為失敗）。

備註：專案未安裝 pytest-asyncio（已確認 .venv 無此套件），故所有 async 批次呼叫
一律以 asyncio.run() 包裝於同步測試函式內執行，避免引入新依賴。
"""

from __future__ import annotations

import asyncio
import re
import socket
import time
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, patch

import pytest

from ansys_unified_mcp.core.sessions import registry
from ansys_unified_mcp.drivers import sim_impl
from ansys_unified_mcp.products.geometry.batch_executor import execute_batch
from ansys_unified_mcp.shared import looks_like_error

INTEGRATION_HOST = "127.0.0.1"
INTEGRATION_PORT = 50051


def _text_content(text: str):
    """建立具 .text 屬性之假 TextContent 物件，模擬 sim_impl.call_tool 的回傳形態。"""

    class _FakeTextContent:
        def __init__(self, t: str) -> None:
            self.text = t

    return _FakeTextContent(text)


def _spaceclaim_grpc_available(host: str = INTEGRATION_HOST, port: int = INTEGRATION_PORT, timeout: float = 1.5) -> bool:
    """偵測 SpaceClaim gRPC 埠是否可連線，用於整合測試的 skip 判定。"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _spaceclaim_has_active_design() -> bool:
    """偵測 SpaceClaim 是否存在作用中設計（而非僅埠開但無設計可操作）。

    埠開不代表可用：使用者可能已開啟 SpaceClaim 視窗但尚未建立/開啟任何設計，
    此時任何幾何操作都會因「No active design available」失敗，應視為 skip
    而非測試缺陷。此函式連線一次並嘗試讀取現有設計，不建立亦不關閉任何東西。
    """
    try:
        connect_result_list = asyncio.run(
            sim_impl.call_tool("geometry_launch", {"port": INTEGRATION_PORT, "host": INTEGRATION_HOST})
        )
    except Exception:
        return False
    connect_text = "\n".join(c.text for c in connect_result_list) if connect_result_list else ""
    if looks_like_error(connect_text):
        return False
    # "已連線...綁定當前設計" 代表有作用中設計；僅"已連線"而無綁定字樣代表無設計。
    return "綁定當前設計" in connect_text


def _release_integration_session() -> None:
    """整合測試收尾：僅清理本模組/本測試建立的連線狀態，絕不關閉使用者的 SpaceClaim 設計。

    facade.GeometryController.close() 會呼叫 modeler.close()，對使用者手動開啟的
    SpaceClaim backend 設計造成破壞性副作用（關閉設計本體），嚴禁在整合測試中使用。
    此處改為直接清空 registry 條目與 sim_impl 模組層全域 _modeler/_current_design，
    僅斷開本進程對該 session 的參照，不送出任何會關閉 backend 設計的 RPC。
    """
    try:
        registry.drop("geometry", str(INTEGRATION_PORT))
    except Exception:
        pass
    sim_impl._modeler = None
    sim_impl._current_design = None


# ===================== 單元層（mock，無需真實 SpaceClaim） =====================


class TestBatchExecutorUnit:
    """以 mock 驗證批次分派邏輯與信封聚合，不觸及真實 gRPC 連線。"""

    def test_empty_operations_returns_ok_envelope(self):
        """空操作清單應回傳成功信封，succeeded/failed 均為 0。"""
        result = asyncio.run(execute_batch([]))
        assert result["ok"] is True
        assert result["total_operations"] == 0
        assert result["succeeded"] == 0
        assert result["failed"] == 0
        assert result["results"] == []

    def test_all_steps_succeed(self):
        """三步皆成功時，信封應標記 ok=True 且 succeeded 等於步驟總數。"""
        operations = [
            {"operation": "geometry_create_block", "args": {"name": "Block1"}},
            {"operation": "geometry_create_enclosure", "args": {"target_body_name": "Block1"}},
            {"operation": "geometry_export", "args": {"file_path": "design.step"}},
        ]
        mock_call_tool = AsyncMock(
            side_effect=[
                [_text_content("Block1 已建立")],
                [_text_content("外流域已建立")],
                [_text_content("已匯出 (step): design.step")],
            ]
        )
        with patch(
            "ansys_unified_mcp.products.geometry.batch_executor.sim_impl.call_tool",
            mock_call_tool,
        ):
            result = asyncio.run(execute_batch(operations))

        assert result["ok"] is True
        assert result["total_operations"] == 3
        assert result["succeeded"] == 3
        assert result["failed"] == 0
        assert len(result["results"]) == 3
        assert result["results"][0]["step"] == 1
        assert result["results"][0]["operation"] == "geometry_create_block"
        assert result["results"][0]["ok"] is True
        assert mock_call_tool.call_count == 3

    def test_partial_failure_aggregates_both_outcomes(self):
        """中段步驟失敗（call_tool 內部已轉為「錯誤」字串）時，整批仍跑完並正確計數。"""
        operations = [
            {"operation": "geometry_create_block", "args": {"name": "Block1"}},
            {"operation": "geometry_create_enclosure", "args": {"target_body_name": "GhostBody"}},
            {"operation": "geometry_export", "args": {"file_path": "design.step"}},
        ]
        mock_call_tool = AsyncMock(
            side_effect=[
                [_text_content("Block1 已建立")],
                [_text_content("錯誤 [geometry_create_enclosure]: 找不到標的本體 GhostBody")],
                [_text_content("已匯出 (step): design.step")],
            ]
        )
        with patch(
            "ansys_unified_mcp.products.geometry.batch_executor.sim_impl.call_tool",
            mock_call_tool,
        ):
            result = asyncio.run(execute_batch(operations))

        assert result["ok"] is False
        assert result["total_operations"] == 3
        assert result["succeeded"] == 2
        assert result["failed"] == 1
        assert result["results"][1]["ok"] is False
        assert mock_call_tool.call_count == 3  # 寬容模式：失敗後仍繼續執行後續步驟

    def test_stop_on_error_halts_remaining_steps(self):
        """stop_on_error=True 時，第一個失敗步驟後應立即中止，不再呼叫後續步驟。"""
        operations = [
            {"operation": "geometry_create_block", "args": {"name": "Block1"}},
            {"operation": "geometry_create_enclosure", "args": {"target_body_name": "GhostBody"}},
            {"operation": "geometry_export", "args": {"file_path": "design.step"}},
        ]
        mock_call_tool = AsyncMock(
            side_effect=[
                [_text_content("Block1 已建立")],
                [_text_content("錯誤 [geometry_create_enclosure]: 找不到標的本體 GhostBody")],
            ]
        )
        with patch(
            "ansys_unified_mcp.products.geometry.batch_executor.sim_impl.call_tool",
            mock_call_tool,
        ):
            result = asyncio.run(execute_batch(operations, stop_on_error=True))

        assert result["ok"] is False
        assert result["succeeded"] == 1
        assert result["failed"] == 1
        assert len(result["results"]) == 2  # 第三步未執行
        assert mock_call_tool.call_count == 2

    def test_missing_operation_field_counts_as_failure(self):
        """操作項目缺少 'operation' 欄位時，應記錄為失敗而非拋例外中斷整批。"""
        operations = [{"args": {"name": "Block1"}}]
        with patch(
            "ansys_unified_mcp.products.geometry.batch_executor.sim_impl.call_tool",
            AsyncMock(),
        ) as mock_call_tool:
            result = asyncio.run(execute_batch(operations))

        assert result["ok"] is False
        assert result["failed"] == 1
        assert "error" in result["results"][0]
        mock_call_tool.assert_not_called()

    def test_unexpected_exception_in_call_tool_is_isolated(self):
        """call_tool 若意外拋出未捕捉例外（非預期行為），批次仍須隔離並續跑，不整批崩潰。"""
        operations = [
            {"operation": "geometry_create_block", "args": {"name": "Block1"}},
            {"operation": "geometry_list_bodies", "args": {}},
        ]
        mock_call_tool = AsyncMock(side_effect=[RuntimeError("gRPC 連線中斷"), [_text_content("幾何體 (0)")]])
        with patch(
            "ansys_unified_mcp.products.geometry.batch_executor.sim_impl.call_tool",
            mock_call_tool,
        ):
            result = asyncio.run(execute_batch(operations))

        assert result["total_operations"] == 2
        assert result["results"][0]["ok"] is False
        assert "gRPC 連線中斷" in result["results"][0]["result"]
        assert result["results"][1]["ok"] is True
        assert mock_call_tool.call_count == 2


# ===================== 整合層（需真實 SpaceClaim gRPC） =====================


@pytest.mark.integration
class TestBatchExecutorIntegration:
    """真實連線 SpaceClaim gRPC (127.0.0.1:50051) 實跑批次幾何操作。

    偵測不到服務時自動 skip；服務在線時實跑並記錄逐點 RPC 對比批次執行的實測耗時。
    """

    @pytest.fixture(autouse=True)
    def _skip_if_no_spaceclaim(self):
        if not _spaceclaim_grpc_available():
            pytest.skip(
                f"SpaceClaim gRPC 未在 {INTEGRATION_HOST}:{INTEGRATION_PORT} 偵測到服務，略過整合測試。"
            )
        if not _spaceclaim_has_active_design():
            pytest.skip(
                "SpaceClaim gRPC 服務在線，但偵測不到作用中設計（埠開不代表可操作），略過整合測試。"
            )

    def test_real_batch_create_block_enclosure_export(self, tmp_path: Path):
        """實跑：連線 → 建立方塊 → 列出本體 → 匯出 STEP，驗證批次聚合信封正確性。

        連線步驟改走 sim_impl.call_tool("geometry_launch", ...)（而非
        facade.controller.launch()）：前者會同時設定 sim_impl.py 的模組層級
        全域 _modeler 並寫入 SessionRegistry，後者僅寫入 registry。geometry_*
        分支讀取的是前者的全域 _modeler，故批次操作必須透過與其一致的連線
        路徑，否則會落入「Geometry 未連線」短路分支產生假性成功信封。
        """
        try:
            connect_result_list = asyncio.run(
                sim_impl.call_tool("geometry_launch", {"port": INTEGRATION_PORT, "host": INTEGRATION_HOST})
            )
            connect_text = "\n".join(c.text for c in connect_result_list) if connect_result_list else ""
            assert not looks_like_error(connect_text), f"連線 SpaceClaim 失敗: {connect_text}"

            export_dir = str(tmp_path)
            operations: List[Dict[str, Any]] = [
                {
                    "operation": "geometry_create_block",
                    "args": {
                        "name": "BatchTestBlock",
                        "length": 0.05,
                        "width": 0.03,
                        "height": 0.02,
                    },
                },
                {"operation": "geometry_list_bodies", "args": {}},
                {
                    # geometry_export 將 file_path 的目錄部分當輸出目的地，
                    # 實際檔名由 PyAnsys Geometry 依當前設計名稱決定
                    # （export_to_step 回傳值即為真實路徑，見下方斷言）。
                    "operation": "geometry_export",
                    "args": {"file_path": str(Path(export_dir) / "placeholder.step"), "format": "step"},
                },
            ]

            result = asyncio.run(execute_batch(operations))

            assert result["ok"] is True, f"批次執行未全數成功: {result}"
            assert result["total_operations"] == 3
            assert result["succeeded"] == 3
            assert result["failed"] == 0

            # geometry_list_bodies 步驟須回報剛建立的本體名稱，證明真實觸達 SpaceClaim
            list_bodies_result = result["results"][1]["result"]
            assert "BatchTestBlock" in list_bodies_result, (
                f"geometry_list_bodies 未回報剛建立的本體，疑似假性成功: {list_bodies_result}"
            )

            # geometry_export 步驟的結果字串含「已匯出 (step): <實際路徑>」，從中解析真實路徑並驗證檔案存在
            export_result_text = result["results"][2]["result"]
            match = re.search(r"已匯出 \(step\): (.+)$", export_result_text.strip())
            assert match, f"export 結果字串未含可解析之實際路徑: {export_result_text}"
            actual_export_path = Path(match.group(1).strip())
            assert actual_export_path.exists(), f"批次匯出的 STEP 檔案未實際生成: {actual_export_path}"
        finally:
            # 僅清理本測試建立的連線狀態，不呼叫 modeler.close()（避免關閉使用者的
            # SpaceClaim 設計本體，見 _release_integration_session 說明）。
            _release_integration_session()

    def test_real_batch_vs_sequential_latency_benchmark(self, tmp_path: Path):
        """量測批次執行 vs. 逐點 RPC 呼叫同一操作序列的實測耗時，記錄改善倍數（取代計畫文檔中未驗證的 15s→0.8s 假設）。"""
        try:
            connect_result_list = asyncio.run(
                sim_impl.call_tool("geometry_launch", {"port": INTEGRATION_PORT, "host": INTEGRATION_HOST})
            )
            connect_text = "\n".join(c.text for c in connect_result_list) if connect_result_list else ""
            assert not looks_like_error(connect_text), f"連線 SpaceClaim 失敗: {connect_text}"

            operations: List[Dict[str, Any]] = [
                {"operation": "geometry_create_block", "args": {"name": "LatencyBlockA", "length": 0.01, "width": 0.01, "height": 0.01}},
                {"operation": "geometry_create_block", "args": {"name": "LatencyBlockB", "length": 0.01, "width": 0.01, "height": 0.01}},
                {"operation": "geometry_list_bodies", "args": {}},
            ]

            async def _run_sequential() -> float:
                start = time.perf_counter()
                for op in operations:
                    await sim_impl.call_tool(op["operation"], op["args"])
                return (time.perf_counter() - start) * 1000.0

            # 逐點 RPC：呼叫端自行逐一 await，模擬未批次化前的往返模式。
            seq_elapsed_ms = asyncio.run(_run_sequential())

            # 批次執行：透過 execute_batch 一次性聚合。
            batch_result = asyncio.run(execute_batch(operations))
            batch_elapsed_ms = batch_result["execution_time_ms"]

            assert batch_result["ok"] is True, f"批次執行未全數成功，疑似未真實觸達 SpaceClaim: {batch_result}"
            # 真實 RPC 應呈現可量測的毫秒級耗時，若接近 0 代表短路分支未真正連線
            assert batch_elapsed_ms > 1.0, (
                f"批次執行耗時 {batch_elapsed_ms}ms 過低，疑似未真實觸達 SpaceClaim（假性成功）"
            )

            improvement_factor = (seq_elapsed_ms / batch_elapsed_ms) if batch_elapsed_ms > 0 else float("inf")
            print(
                f"\n[效能基準] 逐點 RPC: {seq_elapsed_ms:.2f}ms | 批次執行: {batch_elapsed_ms:.2f}ms | "
                f"實測改善倍數: {improvement_factor:.2f}x"
            )
            # 僅記錄實測數據供人工覆核，不對改善倍數設硬性斷言門檻——
            # 兩者皆為同進程內的函式呼叫（非兩個獨立 MCP 工具呼叫的網路往返），
            # 批次化省去的是「呼叫端重複序列化/反序列化與多次 await 排程」開銷，
            # 而非額外的 gRPC 連線建立成本，故不預設改善倍數下限。
        finally:
            # 僅清理本測試建立的連線狀態，不呼叫 modeler.close()（避免關閉使用者的
            # SpaceClaim 設計本體，見 _release_integration_session 說明）。
            _release_integration_session()
