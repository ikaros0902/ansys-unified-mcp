# 中面抽取後拓撲修復手法 (Midsurface Repair Patterns)

本手冊規範中面抽取完成後常見的拓撲缺陷（間隙、重疊、法向翻轉、厚度資訊遺失）與對應修復手法。所有 API 均已於 `D:\Ikaros\ANSYS-unified-MCP\Documentation_clean\api_kb.sqlite`（SpaceClaim V251 命名空間）查證存在，未查證項目明確標註。

---

## 一、常見缺陷類型與偵測訊號

| 缺陷類型 | 成因 | 偵測訊號 |
| :--- | :--- | :--- |
| **間隙 (Gap)** | 複雜鈑金件多片中面交界處未完全縫合 | 鄰接中面邊緣存在自由邊 (free edge)，`ShareTopology.FindProblemAreas()` 可列出問題區域 |
| **重疊 (Overlap)** | 壓折邊相切鏈判斷有歧義，產生重複或交疊面片 | 同一空間位置存在兩個以上面片，`SharePrepOptions.SeparateOverlaps` 可偵測並分離 |
| **法向不一致 (Normal Flip)** | `AddMatchingFacePairs` 自動模式對複雜拓撲選錯主側面 | 相鄰面法向夾角接近 180°，殼單元分析時方向相依的邊界條件（如壓力、接觸面）會作用錯誤 |
| **非 manifold / 短邊 (Non-manifold / Sliver)** | 鈑金件圓角與直邊交界產生退化幾何 | `SharePrepOptions.RemoveShortEdges` / `RemoveSlivers` 可清理 |
| **厚度資訊遺失** | 抽取中面後，原始實體的厚度資訊不會自動保留在殼體屬性上 | 下游 Mechanical 若未見到 Shell Thickness 來源，預設套用值會導致剛度失真 |

---

## 二、修復流程（依執行順序）

### 1. 拓撲健檢：`ShareTopology` / `ShareTopologyNamedSelection`
```python
# 已於 api_kb.sqlite 查證：ShareTopology.FindAndFix(commandInfo) -> CommandResult
# ShareTopology.FindProblemAreas() -> IList`1
problem_areas = ShareTopology.FindProblemAreas()
if problem_areas:
    result = ShareTopology.FindAndFix(info)
```
`FindProblemAreas()` 回傳問題區域清單（間隙、重疊、非 manifold 連接），可先列出供人工覆核再執行 `Fix` / `FindAndFix`。

### 2. 間隙與重疊批次修復：`SharePrep`
```python
# 已於 api_kb.sqlite 查證：
# SharePrep.Execute(targetBodySel, options: SharePrepOptions, info) -> SharePrepResult
# SharePrepOptions 屬性：Tolerance, SeparateOverlaps, RemoveShortEdges, RemoveSlivers, StitchBodies
opts = SharePrepOptions()
opts.Tolerance = stitch_tolerance_m          # 建議與 max_thickness 同量級或更小
opts.StitchBodies = True                     # 縫合容差內的間隙
opts.SeparateOverlaps = True                 # 分離重疊面
opts.RemoveShortEdges = True                 # 清理退化短邊
opts.RemoveSlivers = True                    # 清理狹長微小面
result = SharePrep.Execute(target_selection, opts, info)
created_bodies = result.CreatedBodies
```
`SharePrep` 作用於整個目標 Body 選取範圍，建議在所有中面抽取完成後、對「同一元件下所有中面」一次性執行，而非逐一處理單片中面。

### 3. 法向校正：`Midsurface.FlipFacePair` / `MidsurfaceOffsetFaces.Flip`
```python
# 已於 api_kb.sqlite 查證：
# CreateMidsurfaceNamedSelection.FlipFacePair(face: IDesignFace) -> Void
# CreateMidsurfaceNamedSelection.FlipFacePair(pair: MidsurfaceOffsetFaces) -> Void
# MidsurfaceOffsetFaces.Flip() -> Void
#
# 判定邏輯：若相鄰中面片法向夾角偏離預期（應同向輻射或一致指向裝配外側）
# 超過容許角度，呼叫 FlipFacePair 或直接對該 MidsurfaceOffsetFaces 物件呼叫 Flip()
if not _normals_consistent(face_pair_group):
    midsurface_cmd.FlipFacePair(target_face)
```
注意：`FlipFacePair` 是在**抽取指令尚未 Execute 前**用來調整配對方向的 API（屬於 `CreateMidsurfaceNamedSelection` / `Midsurface` 指令物件本身）。若中面已經生成完畢（指令已 `Execute()` 完成），法向校正應改用抽取後的面法向直接操作（例如對生成面重新評估 `DesignFaceExtensions.GetFaceNormal` 並決定是否需要幾何翻轉）；此類「抽取完成後」翻轉 API 在既有素材與 `api_kb.sqlite` 中**待 api_search 查證**，目前查無 `UnifyNormals` 或獨立 `FlipFaces` 指令物件，整合腳本預設在 `Execute()` 前以 `FlipFacePair` 校正，避免事後翻轉的不確定性。

### 4. 厚度回填：**待 api_search 查證**
目前 `api_kb.sqlite` 僅查得厚度相關的**篩選/查詢** API（`PowerSelection.Bodies.ByMidsurfaceThickness`、`RelationType.BodiesWithNoMidSurfaceThickness`），用於挑選「尚未設定中面厚度」的 Body，但未查得可供腳本寫入厚度數值的屬性（如假設性的 `Plate.Thickness` 或 `Body.MidsurfaceThickness = value`）。
- **現行可行做法**：抽取時記錄 `thickness`（配對面間距量測值），於報表或交接文件中註明每個中面 Body 對應厚度，交由下游 Mechanical 端在 `Thickness` / `CrossSection` 指派階段（參見 `ansys-mechanical-section-assign` 技能）讀取並寫入 Shell Thickness。
- **嚴禁**：在 SpaceClaim 端臆測呼叫未經查證的厚度寫入 API；若後續查證到確切 API，應以 Diff 形式更新本節並移除「待查證」標記。

### 5. 來源實體隱藏
抽取與修復完成後，依 `hide_source_bodies` 旗標呼叫：
```python
ViewHelper.SetObjectVisibility(BodySelection.Create(body), VisibilityType.Hide, False, False)
```
僅隱藏不刪除，保留原始實體供事後比對或復原。

---

## 三、修復順序建議（避免返工）

1. 先完成**全部**候選 Body 的中面抽取（含簡單/複雜模式判定），再統一執行 `ShareTopology` 健檢。
2. 健檢發現問題後，先跑 `SharePrep`（間隙/重疊/短邊/sliver 一次性批量清理），再逐一檢查法向。
3. 法向校正應在抽取指令 `Execute()` 之前透過 `FlipFacePair` 處理；避免在幾何已生成後再嘗試修正，降低不確定 API 風險。
4. 厚度交接資訊必須在隱藏來源實體**之前**完成記錄（隱藏後仍可查詢幾何但不利於人工覆核量測）。
