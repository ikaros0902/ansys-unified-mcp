# SpaceClaim / PyGeometry 錯誤紀錄

---

## ERR-SC-001: gRPC TLS 警告

**觸發場景**: 使用 PyGeometry 連線 SpaceClaim 時收到警告。

**警告訊息**:
```
UserWarning: Starting gRPC client without TLS on 127.0.0.1:50051. 
This is INSECURE. Consider using a secure connection.
```

**根因**: 本機開發環境使用 `transport_mode='insecure'`，PyGeometry 預設會發出 TLS 警告。

**處理**: 本機環境可安全忽略。若需消除警告：

```python
import warnings
warnings.filterwarnings("ignore", message="Starting gRPC client without TLS")

from ansys.geometry.core import Modeler
m = Modeler(port=50051, transport_mode='insecure')
```

---

## ERR-SC-002: `rename_object` 不直接支援 Body 重新命名

**觸發場景**: 嘗試透過 PyGeometry `rename_object` 重新命名 Body 但行為不如預期。

**根因**: PyGeometry 的 `geometry_commands.rename_object()` 可能不支援所有物件類型的
重新命名，或需要特定的 object identifier 格式。

**解決方案**: 使用 `design.name` 或直接修改 body 屬性：

```python
design = m.read_existing_design()
if design.bodies:
    body = design.bodies[0]
    # 根據 API 版本嘗試不同方式
    try:
        body.name = "PCB"
    except Exception:
        # 透過 geometry_commands
        m.geometry_commands.rename_object(body.id, "PCB")
```

---

## ERR-SC-003: `read_existing_design` 回傳空設計

**觸發場景**: 連線 SpaceClaim 後呼叫 `m.read_existing_design()` 但沒有任何幾何。

**可能根因**:
1. SpaceClaim 中沒有開啟任何設計
2. 幾何尚未從 Workbench 同步到 SpaceClaim
3. 連線到錯誤的 SpaceClaim 實例

**解決方案**: 確認 SpaceClaim 中有活動的設計，且幾何已匯入。

---

## ERR-SC-004: `transport_mode` 參數未指定或誤設 'wnua' 導致 gRPC 連線超時

**觸發場景**: 呼叫 `geometry_launch` 或以 `ansys.geometry.core.Modeler` 連線 SpaceClaim 時。

**錯誤訊息**:
```text
ValueError: Transport mode must be specified. Use 'transport_mode' parameter with one of the possible options. Options are: 'insecure', 'uds', 'wnua', 'mtls'.
```
或
```text
TimeoutError / context deadline exceeded: MCP tool call timed out after 60s
```

**根因分析**:
1. `ansys-geometry-core >= 0.16.0` 要求初始化 `Modeler` 時必須明確提供 `transport_mode`。
2. 若誤設為 `transport_mode='wnua'`（Windows 具名管道），而 SpaceClaim 內嵌 ApiServer (`Presentation.ApiServerAddIn.dll`) 是以 TCP 50051 進行 insecure 監聽，gRPC 會在嘗試連線具名管道時永久阻塞超時。

**解決方案**:
連線時明確指定 `transport_mode='insecure'` 與 `host='127.0.0.1'`：

```python
from ansys.geometry.core import Modeler

# 正確連線方式 (SpaceClaim 預設監聽 50051 埠號)
m = Modeler(host="127.0.0.1", port=50051, transport_mode="insecure", timeout=15)
```

在 MCP 工具層面，需確保 `geometry_launch` 預設參數為 `host="127.0.0.1"`、`transport_mode="insecure"`、`connect_timeout=15`。

