# PyMechanical gRPC 連線與遠端腳本 (grpc_connection.md)

本手冊說明如何使用 PyMechanical (`ansys.mechanical.core`) 透過 gRPC 連線 Mechanical 實例並安全執行腳本。

---

## 1. gRPC 連線與多視窗處理

```python
import ansys.mechanical.core as pymech

# 連線至作用中 Mechanical 實例（預設 port 10000）
mc = pymech.connect_to_mechanical(port=10000)
print(mc)

# 若同時開啟多個視窗（如 Static Structural + LS-DYNA），以獨立 port 區分
mc_static = pymech.connect_to_mechanical(port=10000)
mc_lsdyna = pymech.connect_to_mechanical(port=10001)
```

---

## 2. 遠端腳本執行 (`run_python_script`)

```python
result = mc.run_python_script("""
Model = DataModel.Project.Model
mesh = Model.Mesh
print("Mesh nodes:", mesh.Nodes)
""")
print(result)
```

### 執行環境特性：
- `ExtAPI`, `DataModel`, `Model` 預設已注入全域作用域。
- `__name__` 為 `"<string>"`，切勿使用 `if __name__ == "__main__":`。
- `print()` 輸出將被捕獲並作為字串回傳。
