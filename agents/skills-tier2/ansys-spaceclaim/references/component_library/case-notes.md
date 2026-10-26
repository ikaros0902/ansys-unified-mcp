# 2026-10-20 Common Part 實測

這份紀錄保存案例事實與證據位置；名稱、數量與容差不是其他專案的預設值。案例資料位於使用者的 `Common_Part` 工作區，不隨本技能複製模型或 BOM。

## Godzilla

來源 `Godzilla/Part/0_t22-godzilla_chassis_l6_asm.scdoc`，已載入 2,546 bodies。

| 代表模型 | 來源 bodies | STEP 重開 bodies | 備註 |
| --- | ---: | ---: | --- |
| PDB_STANDOFF_GDZ | 1 | 1 | 6 個 occurrence；master 本地尺寸 7.35 × 7.35 × 10.35 mm |
| ASB_FAN_9256_YSM | 3 | 3 | 4 組 occurrence，不是 12 組風扇；保留 3 個曲面體 |
| CYP-VR-HEATSINK-FAR | 1 | 1 | 不因名稱 heatsink 就歸入 1U |
| SP7_HEATSINK_GDZ_ASM | 714 | 769 | 19 組子裝配體完整覆蓋；每組面積最大差約 0.0191% |

SP7 來源及匯入各有 4 個 body 無法計算體積；只對可量測部分比較，不能宣稱整體質量已確認。總表面積差約 0.000865%，外形尺寸最大差約 0.2984%。

證據：`Key_Common_Part/Godzilla_STEP_Export/roundtrip_verification.json`、`sp7_body_groups.json`、`export_manifest.json`。正式素材已分別整理至 `Complex_Model/STANDOFF`、`FAN_9256`、`HEATSINK`，避免把 9256 放進 6056 或將未知高度散熱器放進 1U。

## Interstellar

來源 `Interstellar/Part/jvasb1089334_asm.stp`，完整索引為 3,299 元件、282 個唯一元件名及 5,123 bodies。

| 已存模型（檔名前綴 Interstellar_） | 分類 | 來源／匯入 bodies | 分類依據 |
| --- | --- | --- | --- |
| DIMM_DDR5_EGS | DDR5_DIMM | 1 / 1 | 模型名稱、外形及 32 個 occurrence |
| JVPLS1070841 | DDR5_DIMM，假 DIMM | 267 / 267 | BOM 定義 PC/ABS 塑膠 dummy；STEP 含 266 open shells，不能當真實記憶體材料／質量 |
| J33 | DIMM_SLOT | 1 / 1 | 32 個 occurrence；GUI 確認長卡槽與兩端卡扣，未取得供應商料號 |
| K53010-001_ASM_ASM_1 | HEATSINK_1U | 64 / 64 | BOM 明確記載 1U |
| JVHDW1076894 | STANDOFF | 1 / 1 | BOM：M3 圓形支柱，OD5 mm、L11 mm |

上述五件已重新匯入，依本案 5% 驗收容差通過面積、可計算體積與尺寸比對。

`YSMTSO-44671-DT` 是中空五金候選，外觀不足以排除壓鉚螺母；STEP 尺寸誤差約 26–32%，未通過。檔案放入 `Interstellar_STEP_Export/Pending_Review`，沒有列為正式 STANDOFF。後續要求原生另存則產生含整機資料的 `.scdocx`；本次錯誤產物已移除。

BOM 的 `L6` 頁第 19 列有 `JVMIS1081124`（AVC FAN6056），但完整元件及 body 名稱均未命中 `JVMIS1081124`、`JVMIS1065081`、`DFPK0656`、`6056` 或 `FAN`。這只支持未找到對應命名幾何，不能證明任何未命名風扇都不存在。`JVHDW1055521`、`JVHDW1080730`、`JVHDW1082130`、`TY5701` 亦未命中。

證據：`Key_Common_Part/Interstellar_STEP_Export/assembly_inventory.json`、`saved_models_manifest.json`、`unresolved_model_search.json` 與 GUI 預覽。BOM：`Interstellar/Interstellar-L6 BOM-20240418.xlsx`。

## 後續建庫界線

目前存入 `Complex_Model` 的是擷取素材，不等於已簡化且求解器可用的最終資料庫。建庫時再做 GUI 簡化前後對照、工程特徵與材料確認，依所需格式實測存檔。

本專案 `build_standard_database.py` 產生 `Standard_DB/catalog.json`；程式會寫入 catalog，修改前先查當前來源。需要更新量測或規則時，改生成器的來源資料後重新產生，不能只改會被下次覆寫的 JSON。`DIMM_Creation.py` 的現場參數化建模可作掃描／轉換邏輯參考，但不是以料號讀取已存零件的查表資料庫。
