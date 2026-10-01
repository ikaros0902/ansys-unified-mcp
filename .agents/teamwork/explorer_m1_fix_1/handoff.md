# 調查與修復規格交接報告 (Handoff Report) — MechanicalDriver 循環依賴根治

- **代理人 (Agent)**：`explorer_m1_fix_1` (teamwork_preview_explorer)
- **交付類型 (Handoff Type)**：Hard (調研、根因分析、修復方案實證與落地方案全數完成)
- **接收者 (Recipient)**：`b64f9ba5-0d28-4ac0-a95d-862e7b398eaf` (parent)
- **調研目標**：MechanicalDriver 循環依賴 (Circular Import) 根因探查與制定零回歸之修復策略
- **調研結論**：**READY FOR IMPLEMENTATION (已確立最佳解耦修復方案並完成全矩陣實證驗證，可直接交付 Worker 落地)**

---

## 1. Observation (觀察事實)

本探查者嚴格遵守唯讀調研規範，未修改專案任何原始碼，在全新的獨立 Python 直譯器進程與 pytest 環境下直接觀察到以下客觀事實：

### 1.1 乾淨直譯器下逐字報錯堆疊 (Verbatim Traceback)

在全新乾淨的 Python 直譯器進程中分別執行直接匯入指令，觀察到 100% 必然崩潰的現象：

#### 觀察點 1：`from ansys_unified_mcp.products.mechanical import MechanicalDriver`
- **執行指令**：
  ```powershell
  $env:PYTHONPATH="src"; .venv\Scripts\python.exe -c "from ansys_unified_mcp.products.mechanical import MechanicalDriver"
  ```
- **逐字報錯堆疊 (Verbatim Traceback)**：
  ```text
  Traceback (most recent call last):
    File "<string>", line 1, in <module>
      from ansys_unified_mcp.products.mechanical import MechanicalDriver
    File "F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\products\mechanical\__init__.py", line 21, in __getattr__
      from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver
    File "F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\products\mechanical\driver.py", line 20, in <module>
      from ansys_unified_mcp.drivers.base import BaseSolverDriver, SolverDriverError
    File "F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\drivers\__init__.py", line 22, in <module>
      from ansys_unified_mcp.drivers.mechanical_driver import MechanicalDriver
  ImportError: cannot import name 'MechanicalDriver' from 'ansys_unified_mcp.drivers.mechanical_driver' (F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\drivers\mechanical_driver.py)
  ```

#### 觀察點 2：`from ansys_unified_mcp.products.mechanical import *`
- **執行指令**：
  ```powershell
  $env:PYTHONPATH="src"; .venv\Scripts\python.exe -c "from ansys_unified_mcp.products.mechanical import *"
  ```
- **逐字報錯堆疊**：
  ```text
  Traceback (most recent call last):
    File "<string>", line 1, in <module>
      from ansys_unified_mcp.products.mechanical import *
    File "F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\products\mechanical\__init__.py", line 21, in __getattr__
      from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver
    File "F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\products\mechanical\driver.py", line 20, in <module>
      from ansys_unified_mcp.drivers.base import BaseSolverDriver, SolverDriverError
    File "F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\drivers\__init__.py", line 22, in <module>
      from ansys_unified_mcp.drivers.mechanical_driver import MechanicalDriver
  ImportError: cannot import name 'MechanicalDriver' from 'ansys_unified_mcp.drivers.mechanical_driver' (F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\drivers\mechanical_driver.py)
  ```

#### 觀察點 3：`from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver`
- **執行指令**：
  ```powershell
  $env:PYTHONPATH="src"; .venv\Scripts\python.exe -c "from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver"
  ```
- **逐字報錯堆疊**：
  同樣在 `driver.py:20` 觸發 `drivers/__init__.py:22`，拋出完全一致的 `ImportError`。

---

### 1.2 現有程式碼相依檔案之確切位置與機制剖析

檢視涉及循環匯入的四個核心檔案源碼：

1. **`src/ansys_unified_mcp/products/mechanical/__init__.py`**：
   - 第 19–23 行：
     ```python
     def __getattr__(name: str):
         if name == "MechanicalDriver":
             from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver
             return MechanicalDriver
         raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
     ```
   - 第 26–33 行：
     ```python
     __all__ = [
         "MechanicalController",
         "PRODUCT",
         "controller",
         "_esc",
         "api",
         "MechanicalDriver",
     ]
     ```
   - 機制：透過 PEP 562 支援延遲解析 `MechanicalDriver`，並列於 `__all__` 中。當外部執行 `import *` 時，直譯器會走訪 `__all__` 並調用 `__getattr__("MechanicalDriver")`。

2. **`src/ansys_unified_mcp/products/mechanical/driver.py`**：
   - 第 20 行：
     ```python
     from ansys_unified_mcp.drivers.base import BaseSolverDriver, SolverDriverError
     ```
   - 第 33 行：
     ```python
     class MechanicalDriver(BaseSolverDriver):
     ```
   - 機制：為繼承基類 `BaseSolverDriver`，在模組頂層匯入 `drivers.base`。由於 Python 機制，匯入子模組必然先載入父套件 `drivers`。

3. **`src/ansys_unified_mcp/drivers/__init__.py`**：
   - 第 13–24 行：
     ```python
     from ansys_unified_mcp.drivers.base import (
         BaseSolverDriver,
         SolverDriverError,
         SolverExecutionError,
         SolverNotFoundError,
     )
     from ansys_unified_mcp.drivers.fluent_driver import FluentDriver
     from ansys_unified_mcp.drivers.icepak_driver import IcepakDriver
     from ansys_unified_mcp.drivers.lsdyna_driver import LSDynaDriver
     from ansys_unified_mcp.drivers.mechanical_driver import MechanicalDriver
     from ansys_unified_mcp.drivers.optislang_driver import OptislangDriver
     from ansys_unified_mcp.drivers.spaceclaim_driver import SpaceClaimDriver
     ```
   - 機制：在模組頂層**飢渴匯入 (Eager Import)** 所有具象驅動的相容 shim。

4. **`src/ansys_unified_mcp/drivers/mechanical_driver.py`**：
   - 第 1–8 行：
     ```python
     """Backward-compatibility shim for ansys_unified_mcp.drivers.mechanical_driver."""
     import sys
     from ansys_unified_mcp.products.mechanical import driver as _driver

     _this_module = sys.modules[__name__]
     for _k, _v in _driver.__dict__.items():
         if not _k.startswith("__"):
             setattr(_this_module, _k, _v)
     ```
   - 機制：試圖在模組載入期自 `_driver.__dict__` 反射拷貝屬性。

---

### 1.3 順序敏感性實證 (Order Sensitivity Evidence)

- **情況 A（先匯入 drivers）**：
  ```powershell
  $env:PYTHONPATH="src"; .venv\Scripts\python.exe -c "import ansys_unified_mcp.drivers; from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver; print('Success')"
  ```
  - **輸出**：`Success`（Exit code 0）。
  - 原因：先載入 `drivers/__init__.py` 時，`products.mechanical.driver` 首次載入，其在第 20 行匯入 `drivers.base` 時父套件已存在於 `sys.modules`，能一路執行至第 33 行完成 `MechanicalDriver` 定義。
- **情況 B（先匯入 products.mechanical）**：
  - **輸出**：`ImportError` 崩潰（Exit code 1）。
- **廣泛性調查**：
  經測試，`FluentDriver`（`from ansys_unified_mcp.products.fluent.driver import FluentDriver`）與 `OptislangDriver` 亦存在完全相同的崩潰堆疊，證實此為全專案驅動層的結構性共同問題。

---

### 1.4 現有對抗測試套件執行結果

- **執行指令**：
  ```powershell
  .venv\Scripts\pytest.exe tests/adversarial/test_m1_facade_adversarial_challenge.py -v
  ```
- **結果**：`22 passed, 1 failed in 1.92s`。
  失敗測試：`TestM1DynamicImportAndReflexivity::test_circular_import_vulnerability_on_driver_export`。

---

## 2. Logic Chain (推導邏輯鏈)

從上述觀察事實出發，嚴密推導循環依賴閉環成因與修復路徑：

### 2.1 閉環死結之五節點因果鏈
```text
[進入點: products.mechanical]
       │
       ▼ (1) __getattr__("MechanicalDriver")
[products.mechanical.driver] (driver.py)
       │ (driver.py 註冊入 sys.modules，開始自第 1 行線性向下執行)
       │
       ▼ (2) 執行第 20 行: from ansys_unified_mcp.drivers.base import BaseSolverDriver
[drivers] (父套件 __init__.py 尚未載入，Python 強制先執行 drivers/__init__.py)
       │
       ▼ (3) drivers/__init__.py 執行第 22 行: from ansys_unified_mcp.drivers.mechanical_driver import MechanicalDriver
[drivers.mechanical_driver] (mechanical_driver.py)
       │
       ▼ (4) 執行第 3 行: from ansys_unified_mcp.products.mechanical import driver as _driver
             (直譯器發現 products.mechanical.driver 已在 sys.modules，直接返回其半初始化物件)
             執行第 6-8 行: 遍歷 _driver.__dict__
             【死結核心】：此時 driver.py 仍卡在第 20 行，尚未執行到第 33 行的 class MechanicalDriver 定義！
             因此 _driver.__dict__ 內根本沒有 MechanicalDriver！
       │
       ▼ (5) mechanical_driver.py 結束執行，未包含 MechanicalDriver 屬性。
             回到 drivers/__init__.py 第 22 行嘗試 import MechanicalDriver，立即噴出 ImportError！
```

### 2.2 為什麼僅修改 `mechanical_driver.py` 無法解決問題？
- 假設僅在 `drivers/mechanical_driver.py` 中將反射改為 `def __getattr__(name): ...`：
  當 `drivers/__init__.py` 執行第 22 行 `from ansys_unified_mcp.drivers.mechanical_driver import MechanicalDriver` 時，直譯器立即向 `mechanical_driver` 索求 `MechanicalDriver`。
  這會觸發 `mechanical_driver.__getattr__("MechanicalDriver")`，其再去向 `driver.py` 索求屬性。
  但因 `driver.py` 此時仍停留在第 20 行，該屬性依然不存在，依然拋出 `AttributeError` $\rightarrow$ 轉為 `ImportError`。
- **結論**：單純修改 shim 模組無法打斷依賴環。

### 2.3 最佳切斷點：`drivers/__init__.py` 採 PEP 562 延遲導出
- 當 `products.mechanical.driver` 匯入 `drivers.base` 時，它**只需要抽象基類與異常型別**，根本不需要具體的 `MechanicalDriver`、`FluentDriver` 等具象實作！
- 若在 `drivers/__init__.py` 中將具象驅動改為 `__getattr__` 延遲導出：
  1. `driver.py` 匯入 `drivers.base` 時，`drivers/__init__.py` 僅載入 `base.py` 便順利完成初始化。
  2. `driver.py` 繼續執行到第 33 行，完成 `MechanicalDriver` 定義。
  3. 當外界真正需要 `MechanicalDriver` 時，無論是從 `products.mechanical` 或 `drivers` 存取，`MechanicalDriver` 都已是完整就緒的型別物件。
  4. 閉環死結徹底瓦解。

---

## 3. Caveats (限制與注意事項)

1. **SpaceClaim 的命名空間路徑**：
   在 `src/ansys_unified_mcp/drivers/spaceclaim_driver.py` 中，其底層路徑為 `from ansys_unified_mcp.products.geometry import driver`（非 `products.spaceclaim`）。在配置延遲對應字典時需注意對應到 `ansys_unified_mcp.drivers.spaceclaim_driver`。
2. **靜態分析工具 (mypy / pyright / IDE) 相容性**：
   若僅使用 `__getattr__`，部分靜態型別檢查器可能無法感知 `drivers.MechanicalDriver`。必須使用 `if TYPE_CHECKING:` 守衛匯入，達成「執行期零負擔延遲載入、靜態分析期型別完備」。
3. **歷史對抗測試 `test_chapter2_adversarial_verification.py` 斷言遺留**：
   該測試第 86-88 行硬編碼檢查舊檔案 `src/ansys_unified_mcp/products/mechanical.py` 實體存在，因 Milestone 1 要求徹底刪除該舊檔案，該測試目前呈現紅燈。此項屬於測試層對舊架構的硬性殘留，實作者在修復循環依賴之餘，可向審查員或母代理建議同步更新該測試的斷言目標為 `facade.py`。

---

## 4. Conclusion (最終評定結論與實作落地規範)

### 評定結論：**READY FOR IMPLEMENTATION**

本探查者已實證制定出**「三位一體解耦架構方案」**。實作者 (Worker) 只需依序修改下列三個檔案，即可達成 100% 任意順序無死結，並完全通過對抗挑戰。

---

### 具體代碼修改建議 (Worker 落地指南)

#### 修改檔案 1：`src/ansys_unified_mcp/drivers/__init__.py`
**修改意圖**：保留 BaseSolverDriver 與異常類別的直接匯出，將具象驅動改為 PEP 562 延遲導出，搭配 `TYPE_CHECKING` 支援 IDE/mypy。

**完整建議代碼**：
```python
"""ANSYS Unified MCP 2.0 - 統一求解器驅動層 (Drivers Package).

匯出標準求解器驅動類別：
- BaseSolverDriver: 抽象基類
- MechanicalDriver: ANSYS Mechanical / MAPDL 結構與熱分析
- LSDynaDriver: LS-DYNA 顯式動力學與落摔衝擊
- OptislangDriver: optiSLang 參數尋優與 MOP 代理模型
- SpaceClaimDriver: SpaceClaim / Discovery 幾何前處理
- FluentDriver: ANSYS Fluent 計算流體力學
- IcepakDriver: ANSYS Icepak 電子散熱分析
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

from ansys_unified_mcp.drivers.base import (
    BaseSolverDriver,
    SolverDriverError,
    SolverExecutionError,
    SolverNotFoundError,
)

# 支援靜態類型檢查 (IDE 自動補齊與 mypy/pyright)
if TYPE_CHECKING:
    from ansys_unified_mcp.drivers.fluent_driver import FluentDriver
    from ansys_unified_mcp.drivers.icepak_driver import IcepakDriver
    from ansys_unified_mcp.drivers.lsdyna_driver import LSDynaDriver
    from ansys_unified_mcp.drivers.mechanical_driver import MechanicalDriver
    from ansys_unified_mcp.drivers.optislang_driver import OptislangDriver
    from ansys_unified_mcp.drivers.spaceclaim_driver import SpaceClaimDriver

_LAZY_DRIVERS: dict[str, tuple[str, str]] = {
    "MechanicalDriver": ("ansys_unified_mcp.drivers.mechanical_driver", "MechanicalDriver"),
    "FluentDriver": ("ansys_unified_mcp.drivers.fluent_driver", "FluentDriver"),
    "IcepakDriver": ("ansys_unified_mcp.drivers.icepak_driver", "IcepakDriver"),
    "LSDynaDriver": ("ansys_unified_mcp.drivers.lsdyna_driver", "LSDynaDriver"),
    "OptislangDriver": ("ansys_unified_mcp.drivers.optislang_driver", "OptislangDriver"),
    "SpaceClaimDriver": ("ansys_unified_mcp.drivers.spaceclaim_driver", "SpaceClaimDriver"),
}

__all__ = [
    "BaseSolverDriver",
    "SolverDriverError",
    "SolverNotFoundError",
    "SolverExecutionError",
    "MechanicalDriver",
    "LSDynaDriver",
    "OptislangDriver",
    "SpaceClaimDriver",
    "FluentDriver",
    "IcepakDriver",
]


def __getattr__(name: str) -> Any:
    """PEP 562 模組級延遲載入，徹底消除循環依賴死結。"""
    if name in _LAZY_DRIVERS:
        module_path, attr_name = _LAZY_DRIVERS[name]
        mod = importlib.import_module(module_path)
        val = getattr(mod, attr_name)
        globals()[name] = val  # 寫入模組字典，後續存取 O(1) 快取
        return val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """支援 IDE 自動補齊與 dir() 反射。"""
    return sorted(list(globals().keys()) + list(_LAZY_DRIVERS.keys()))
```

---

#### 修改檔案 2：`src/ansys_unified_mcp/drivers/mechanical_driver.py`
**修改意圖**：移除危險的載入期 `_driver.__dict__` 反射遍歷，改為明確宣告匯入核心類別，其餘屬性透明委派。

**完整建議代碼**：
```python
"""Backward-compatibility shim for ansys_unified_mcp.drivers.mechanical_driver."""
from __future__ import annotations

from typing import Any
from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver

__all__ = ["MechanicalDriver"]


def __getattr__(name: str) -> Any:
    from ansys_unified_mcp.products.mechanical import driver as _driver
    val = getattr(_driver, name)
    globals()[name] = val
    return val
```

---

#### 修改檔案 3：`src/ansys_unified_mcp/products/mechanical/__init__.py`
**修改意圖**：在 `__getattr__` 命中時將 `MechanicalDriver` 寫入 `globals()` 快取，符合 Python 最佳實踐並提升重複存取效能。

**修改片段 (第 19–24 行)**：
```python
def __getattr__(name: str):
    if name == "MechanicalDriver":
        from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver
        globals()[name] = MechanicalDriver
        return MechanicalDriver
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

---

## 5. Verification Method (獨立覆核與實證方式)

實作者或審查者可在專案根目錄下依序執行以下實證命令：

### 5.1 乾淨直譯器下 100% 成功驗證 (三種進入點)
```powershell
$env:PYTHONPATH="src"; .venv\Scripts\python.exe -c "from ansys_unified_mcp.products.mechanical import MechanicalDriver; print('P1 OK:', MechanicalDriver)"
$env:PYTHONPATH="src"; .venv\Scripts\python.exe -c "from ansys_unified_mcp.products.mechanical import *; print('P2 OK:', MechanicalDriver)"
$env:PYTHONPATH="src"; .venv\Scripts\python.exe -c "from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver; print('P3 OK:', MechanicalDriver)"
$env:PYTHONPATH="src"; .venv\Scripts\python.exe -c "from ansys_unified_mcp.drivers import MechanicalDriver; print('D1 OK:', MechanicalDriver)"
$env:PYTHONPATH="src"; .venv\Scripts\python.exe -c "from ansys_unified_mcp.drivers.mechanical_driver import MechanicalDriver; print('D2 OK:', MechanicalDriver)"
```
- **預期結果**：全部 Exit code 0，印出對應類別物件，零 `ImportError`。

### 5.2 對抗挑戰測試全數通過驗證
```powershell
.venv\Scripts\pytest.exe tests/adversarial/test_m1_facade_adversarial_challenge.py -v
```
- **預期結果**：`23 passed in ~2s`（原失敗之 `test_circular_import_vulnerability_on_driver_export` 轉為 PASSED）。

### 5.3 既有單元測試零回歸驗證
```powershell
.venv\Scripts\pytest.exe tests/unit/
```
- **預期結果**：`257 passed, 2 skipped` 全數通過。

### 5.4 實證腳本存檔
本探查者已將全矩陣壓測腳本與動態驗證腳本留存於本工作目錄，可供隨時複驗：
- `F:\Ming_python\ansys-unified-mcp\.agents\teamwork\explorer_m1_fix_1\stress_import_matrix.py`（12 組全排列子進程壓測）
- `F:\Ming_python\ansys-unified-mcp\.agents\teamwork\explorer_m1_fix_1\verify_combined_fix.py`（對抗測試整合驗證）
