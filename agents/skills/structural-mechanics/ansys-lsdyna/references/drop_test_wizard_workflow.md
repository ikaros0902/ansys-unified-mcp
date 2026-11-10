# Drop Test Wizard 實戰流程與排障 (drop_test_wizard_workflow.md)

本手冊補充 ANSYS Mechanical LS-DYNA 落摔測試的 GUI 操作實戰與特定錯誤排障，與既有理論門檻（`energy_diagnostics.md`、`mass_scaling_rules.md`）互補：那兩份給物理門檻與判斷力庫，本檔給 GUI 操作路徑與踩過的坑。來源：Ansys LS-DYNA Drop Test 官方應用指南（手機落摔案例）。

---

## 一、Drop Test Wizard（全自動化嚮導）vs 標準手動工作流

**Drop Test Wizard** 只需要幾何即可全自動完成以下工作：建立剛性落摔面（construction geometry）、物件與落摔面定向、依落摔高度計算衝擊速度、施加標準重力、全固定約束落摔面、定義落摔面與物件的摩擦 Body Interaction、劃分網格、設定分析結束時間。

**使用時機**：Wizard 適合快速原型與單一物體自由落摔；需要精細控制接觸、分區網格、Mass Scaling 策略的複雜多零件組裝（如手機、PCB 組件）建議走標準手動工作流（Geometry/Material → Connections → Mesh → CFL/Mass Scaling → Boundary/Initial Conditions → Analysis Settings & Solve → Model Check → Model Corrections）。

### Wizard 操作參數範例

- Physics Preference 設為 Explicit，Element Size 設定目標網格尺寸（如 0.003 m），開啟 Capture Curvature。
- LS-DYNA 分支 → Drop Test Wizard：設定 Drop Rotation（物件撞擊角度）、Drop Height（落摔高度）、Frictional Behavior 的 Friction Coefficient（如 0.1）。
- Wizard 完成後會自動產生：Part Transform（定向）、Construction Geometry 落摔面、Frictional Body Interaction、依尺寸設定生成的 Mesh、Drop Height Initial Condition（含自動計算的 Impact Velocity）、Fixed Support（落摔面）、Standard Earth Gravity（-Y）、Deformation/Acceleration Results。

## 二、材料與元件分類原則

- **剛性體（Rigid）**：螺絲、電池包等「只關心質量貢獻、不關心變形」的零件簡化為剛性體，省計算資源。
- **柔性體（Flexible）**：外殼、顯示玻璃、PCB、桿件等真正需要變形行為的零件維持柔性。
- **單層六面體沙漏修正（有限制條件，非無條件適用）**：PCBA、顯示玻璃等單層六面體元素容易產生沙漏效應，案例文件採用改用 **Fully Integrated S/R Solid** 公式（新增 Section 物件，Formulation 選 `Fully Integrated S/R Solid`）消除該部件的沙漏能——完全積分元素不會發生沙漏模式。
  > [!WARNING]
  > 這是「消除沙漏能」與「引入剪切自鎖」的取捨，不是無條件通解。依 `parts_and_sections.md` 的 ELFORM 選型矩陣，標準全積分實體單元（ELFORM=2）在薄壁彎曲時容易產生剪切自鎖（虛假誇大結構剛度），**嚴禁對單層薄壁使用**；PCBA/顯示玻璃落摔時的主要失效模式正是彎曲，剪切自鎖會讓應變量被低估、結果偏不保守，不能因為「只是落摔分析」就忽視這個風險。案例文件沒有說明它用的 `Fully Integrated S/R Solid` 是否已經是本庫 `parts_and_sections.md` 中建議的 **ELFORM=-1/-2 自鎖修正高階全積分單元**（有效緩解剪切自鎖與體積自鎖，計算耗時約為單點積分的 2~4 倍）——如果是同一種公式，案例做法與既有建議一致；如果案例用的是標準 ELFORM=2（無自鎖修正），則應優先改用 ELFORM=-1/-2 取代，而非直接套用案例的做法。寫腳本前應用 `api_validate_script` 或查 LS-DYNA Keyword Manual 確認 Workbench 的 `Fully Integrated S/R Solid` 選項對應的實際 ELFORM 編號。

## 三、網格與 CFL 調優（實戰數值）

- 先用全域尺寸排查，若最小 CFL 步長被局部區域拖垮（如 6.6e-8 s 太小），用 Mesh Controls 針對性處理：全域尺寸放大（如 2.0 mm）、對螺絲/PCBA 等可結構化的部件用 MultiZone 轉六面體（Mapped Mesh Type: Hexa, Free Mesh Type: Not Allowed）、對圓角曲面加 Face Meshing/Face Sizing 捕捉曲率。
- 處理後若元素數大幅下降（例如從原始網格降到約 28000 個元素），Max Time Step 通常會改善，但 Min Time Step 可能仍卡在特定部件（如某個桿件或外殼局部），需要針對該部件再做局部處理。
- 若 CFL 步長調到合理範圍仍不夠快，用 **Automatic Mass Scaling**（Yes，指定 Time Step Size 如 2E-7 s，Safety Factor 0.9，實際步長約為 `Time Step Size × Safety Factor`）。小質量部件（如一根桿件）即使被 Mass Scaling 加倍質量，只要該部件佔總質量比例極低（如 <1%），對**整體模型的質量增加率**影響可忽略。但這只代表全域質量守恆沒問題，不代表該部件自身的局部動態響應（慣性、應力波傳遞速度）不受影響——若該部件本身是關注的評估對象（例如桿件本身的應力/變形是輸出項），仍應個別檢查其質量縮放比例是否超過該部件自身可接受的範圍，不能只看全域佔比就斷定不需要修正。

## 四、接觸與連接配置原則

- **Bonded**：真正固定在一起、不應相對運動的組件（如晶片對 PCB、桿件對下殼）。
- **Frictional**：允許相對滑動但有摩擦的接觸（如落摔面與外殼，摩擦係數常見範圍 0.1~0.15）。
- **多體 Body Interaction**：落摔變形過程中可能互相碰撞的多個零件（如外殼、電池包、PCBA 共 4 個 body）應建立一個涵蓋全部的 Body Interaction，而不是逐對建立大量重複接觸——多個接觸疊加在同一區域會造成行為異常。
- **剛性體連結**：剛性螺絲與 PCBA/下殼的連接用 Rigid Body Additional Nodes（Node Scoping 到對應表面），不要用一般接觸。

## 五、排障：接觸穿透與干涉修正

| 問題 | 修正方式 |
|---|---|
| 兩個零件在建模階段就有初始幾何穿透（Initial Penetration） | 把該接觸的 Behavior 改為 `Program Controlled`（軟體會轉成 `*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE`），再插入 Contact Property，Type 選 `Interference`，可設定 Stiffness Scale Factor（如 1）處理初始穿透 |
| 衝擊瞬間某零件穿透剛性落摔面 | 代表接觸的 Penalty Stiffness 太小；插入 Contact Property，Soft Constraint Formulation 選 `Soft Constraint`，設定 Soft Constraint Scale Factor（如 0.1）提高懲罰剛度 |
| 求解器警告找不到某個 interface 編號對應哪個接觸 | Workbench LS-DYNA 把接觸資料依照 Connections 資料夾裡的順序寫入 `input.k`；打開 `input.k` 用文字編輯器對照接觸定義順序即可找到對應關係 |
| 看到 `*CONTROL_ALE` 警告 | 若模型沒用到 ALE（Arbitrary Lagrangian-Eulerian）方法，這個警告可以忽略 |

## 六、排障：能量診斷

- **初始動能檢查**：核對初始動能是否與「初始速度」和「總質量」算出的理論值一致（$KE = \frac{1}{2}mv^2$），不一致代表初始條件設定有誤。
- **負接觸能（Negative Contact Energy）**：
  - 接觸能分為 Slave Energy（SE）、Master Energy（ME）、Frictional Energy（FE），三者之和即為 glstat 中的 Sliding Energy。SE/ME/FE 的詳細分項預設不會輸出到 `sleout`，需要另外開啟。
  - 有摩擦力存在時，Positive Contact Energy 是正常、預期的現象；若接觸能明顯為負，優先檢查上面「接觸穿透」表格的修正方式，而不是先懷疑公式錯誤。
- **沙漏能偏高**：先確認是哪個 part 貢獻的（逐 part 檢查而非只看全域總量），單層六面體元素（Reduced Integration）是最常見的來源，對策見第二節的 Fully Integrated S/R Solid。

## 七、Initial Velocity 的手動計算案例（不走 Wizard 時）

落摔高度換算初速度公式與擺放原則見 [`initial_boundary.md`](initial_boundary.md) 第一節（$v_0 = -\sqrt{2gh}$）。本案例驗證該公式：1.5 m 落摔高度、重力方向為全域 -Y，官方案例文件算出的衝擊速度約為 -5425 mm/s（施加在 Y 方向的 Initial Velocity），與公式計算結果一致。這與 Wizard 自動計算的 Drop Height Initial Condition 是同一個公式，手動流程下需要自己在 LSDYNA Pre 工具列新增 Initial Velocity 物件並填入計算值。
