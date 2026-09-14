# Remote Point Algorithms & Topology Validation

本手冊為 Session 04: 連線、遠端質量配置與拓撲防呆預檢之底層演算法、防呆機制與檢查腳本實作細節。

---

### 2.1 過度約束防呆與 LS-DYNA Error 20110 消除
- **錯誤機制**：在 LS-DYNA 顯式求解器中，若多個 `Rigid` Remote Points 同時綁定到同一薄板面或共用網格節點，會觸發 `Error 20110: multiple rigid bodies constrain the same node`，造成求解立刻終止。
- **解法**：針對薄板、鈑金螺絲孔或跨越多個孔位的 MPC 連接，強制設定 `Behavior = LoadBehavior.Deformable`：
```python
def create_screw_remote_points(model, all_ns, prefix="Scr_RM_"):
    for ns in all_ns:
        if ns.Entities.Count == 0:
            continue # 過濾空集合
            
        if ns.Name.startswith(prefix) or "SCREW" in ns.Name.upper():
            rp = model.AddRemotePoint()
            rp.Name = ns.Name
            rp.Location = ns
            # 關鍵防呆：設定為 Deformable 避免鎖死自然彎曲模態與觸發 Error 20110
            rp.Behavior = LoadBehavior.Deformable
```

### 2.2 Remote Point (MPC) 與 Remote Mass (集中質量) 區分
1. **Remote Point (MPC)**：
   - 用於模擬實體螺栓緊固行為、連接不同鈑金件孔位或作為約束作用點。
   - 不具備附加重力質量，僅傳遞 6 自由度位移與反力。
2. **Remote Mass (Point Mass)**：
   - 用於模擬未建構幾何細節之輔助模組（如 PCIe 卡配重 520g、電源模組 800g、CPU 散熱器 1000g）。
   - 透過 `model.AddPointMass()` 建立，並填入以公克（g）或公斤（kg）為單位之集中質量與質心座標。

### 2.3 求解前零件拓撲檢查 (Unconstrained Flying Body Topology Check)
在求解前掃描全機所有 Body，驗證每個 Body 至少與一個接觸對、運動副、遠端點或邊界條件相連：
```python
def verify_body_topology(model):
    bodies = model.Geometry.GetChildren(DataModelObjectCategory.Body, True)
    orphan_bodies = []
    
    for b in bodies:
        if b.Suppressed:
            continue
        # 檢查 Body 是否具有幾何實體與正常狀態
        gb = b.GetGeoBody()
        if not gb:
            orphan_bodies.append(b.Name)
            continue
            
    if orphan_bodies:
        print("[CRITICAL ALERT] Found {} unconstrained orphan bodies:".format(len(orphan_bodies)))
        for name in orphan_bodies:
            print(" - " + name)
    else:
        print("[TOPOLOGY CHECK] All active bodies are properly scoped and constrained.")
```

---
