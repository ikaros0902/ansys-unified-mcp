# 跨產品線消費差異表 (Cross-Product Consumption Matrix)

本手冊比較同一組 Named Selection 命名規則，在 static structural、thermal、LS-DYNA 顯式三種下游分析類型下，消費端腳本如何解讀並設定物件屬性的差異。命名規則本身在三種分析下**完全相同**，差異僅發生在建立出來物件的屬性配置。

---

## 一、`Connect Topology*`（Bonded Contact）

| 分析類型 | ContactType | PinballRadius 意義 | ShellThicknessEffect | 備註 |
| :--- | :--- | :--- | :--- | :--- |
| **static / modal** | `Bonded` | 搜尋容差，影響接觸偵測範圍；過大可能誤綁不該連接的面 | 依零件是否為殼單元決定，鈑金件常設 `True` 以納入殼厚度效應 | 建議執行 Contact Tool 驗證穿透量（見 `ansys-mechanical-connections`） |
| **thermal** | `Bonded` | 同上，但同時影響熱傳導路徑的幾何範圍 | 通常設 `False`（避免殼厚度效應疊加失真的熱阻計算），熱阻另由 Thermal Contact Resistance 設定補充 | 本技能僅處理幾何介面建立，熱阻數值屬 `ansys-mechanical` 熱分析範疇 |
| **lsdyna_explicit** | 對應 LS-DYNA Keyword 端的局部 `*CONTACT_TIED_*` 或透過 Mechanical Bonded 匯出轉換 | Pinball 影響顯式求解初始綁定搜尋範圍，原始腳本固定 `pinBallRadius*2` | `ShellThicknessEffect = False`（原始腳本固定值，避免顯式求解中殼厚度與接觸搜尋半徑耦合造成的額外複雜度） | 全域自接觸另由 `*CONTACT_AUTOMATIC_SINGLE_SURFACE` 卡片處理，與本規則互不重疊 |

---

## 二、`_Mobile` / `_Reference`（Joint 運動副）

| 分析類型 | Joint Type 常見選型 | UnderDefined 處置 | Behavior 預設 | 備註 |
| :--- | :--- | :--- | :--- | :--- |
| **static / modal** | `Fixed` 或 `Revolute`（依機構鉸鏈需求） | 預設**保留** UnderDefined，不自動 Promote；僅使用者明確要求才 `PromoteToRemotePoint()` | N/A（Joint 本身無 Behavior 屬性，Promote 後才產生 Remote Point 具 Behavior） | Revolute Joint 的旋轉自由度在靜態分析中天然為 UnderDefined，屬正常狀態非錯誤 |
| **thermal** | 通常不建立 Joint（熱分析無機構運動需求），若沿用幾何則多數退化為 `Fixed` 接觸等效處理 | N/A | N/A | 熱分析較少直接消費 `_Mobile`/`_Reference` 命名，此列保留供未來擴充（**待實際案例查證**） |
| **lsdyna_explicit** | `Revolute` / `Cylindrical`（機構衝擊常見，如把手退出機構） | **嚴格禁止**自動 Promote 破壞性降級；`cnt_underdefined_revolute` 計數僅供記錄，顯式求解器可直接處理 UnderDefined 運動副 | N/A | 原始腳本 `rm_joint_creator.py` 明確以註解強調「Strictly block destructive Promote for Revolute joints」 |

---

## 三、單一遠端點（Remote Point，無 Mobile/Reference 後綴）

| 分析類型 | Behavior 選型原則 | DOF 設定 | 備註 |
| :--- | :--- | :--- | :--- |
| **static / modal** | 依工況：集中剛性載荷點用 `Rigid`；避免局部過硬失真用 `Deformable` | 預設 6 DOF 全啟用（`XComponent`~`RotationZ` = `Active`），可依邊界條件需求手動關閉特定自由度 | `MECH_Joint_Creation.py` 原始邏輯固定 `Rigid` + 全 DOF，實務上需依工況覆核是否過度剛化 |
| **thermal** | 多用 `Deformable`，避免虛假高熱傳導路徑（Rigid 遠端點會形成人工高剛度/高傳導捷徑） | 熱分析不涉及旋轉 DOF，僅需確認溫度/熱流施加點正確 Scoping | 熱分析遠端點用途多為熱流率或對流邊界的集中施加點，非結構機構配對 |
| **lsdyna_explicit** | **強制** `Deformable`（螺絲孔、鈑金介面類），`Rigid` 會在多點共用節點時觸發 `Error 20110` | 全 DOF 啟用但顯式求解器會依接觸與材料行為動態響應，非線性大變形工況尤其敏感 | 詳細防呆機制見 `ansys-mechanical-connections/references/contact_verification_and_overconstraint_guard.md` |

---

## 四、`Scr_RM_grp` 系列（含距離分級後綴）

| 分析類型 | 消費方式差異 | 備註 |
| :--- | :--- | :--- |
| **static / modal** | 作為螺絲鎖固點候選群組，直接餵入 Joint 或 Remote Point 建立腳本，不特別區分距離分級 | 距離分級（`_Near`/`_Medium`/`_Far`）主要用於統計報表與人工覆核，非自動分流不同建立邏輯的依據 |
| **thermal** | 用途相同，但額外可能用於判斷螺絲孔周圍是否需要加密網格以捕捉局部溫度梯度（**待實際案例查證**，目前無來源腳本證實此用法） | 標記為待查證，不可當作既有規範引用 |
| **lsdyna_explicit** | 相同候選群組，但下游強制 `Deformable` 遠端點（見上表），且顯式求解對螺絲預緊力建模可能額外需要 `*INITIAL_STRESS` 等關鍵字（屬 LS-DYNA 專屬，超出本技能範疇，交叉引用 `ansys-lsdyna` 技能） | — |

---

## 五、使用原則總結

1. **命名規則一次定義，三處消費**：不應為不同分析類型建立不同的命名規則，而是在消費端（Mechanical ACT 腳本）依分析類型分支設定屬性，命名字串本身保持穩定以利跨產品線重用同一份 SpaceClaim 幾何前處理腳本。
2. **凡標註「待實際案例查證」之列**：代表現有來源腳本未直接證實該用法，僅為合理推論，使用前應先確認目標專案是否有對應腳本佐證，不可直接當作既定規範執行。
