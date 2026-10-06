---
name: simplify-heatsink
description: 散熱片 (heatsink) 幾何簡化流程。使用者要求「簡化 heatsink / 散熱片」時，確認散熱片 body 名稱（多 body 組件另確認要併入的鰭片/底座/上蓋），呼叫 `geometry_simplify_heatsink`：重建為凸字形方塊組（底板＋上凸＋下凸，無階梯/圓角）、鎖孔為 Y 向直圓柱、移除螺絲/彈簧，並以常見散熱片密度反推簡化體應設定的等效密度（附加於 body 名稱 `_rho<kg/m³>`）。
Use when:
  - 使用者要求簡化散熱片 / heatsink / 鰭片幾何，或要求「保留鎖孔與底面、反推等效密度」。
  - 需調用 MCP 工具：`geometry_simplify_heatsink`（必要時搭配 `geometry_list_bodies`、`geometry_screenshot`）。
  - 限制: 高度軸固定為 world Y（鰭片朝 +Y）；散熱片 body 名稱須由使用者提供或經使用者確認，不可自行猜測。
  - 觸發關鍵字 (繁中/En): 簡化heatsink, 簡化散熱片, 散熱片簡化, 鰭片填實, 等效密度, simplify heatsink.
phase_gate:
  requires: []
  produces: []
---

# 散熱片幾何簡化流程

> [!CAUTION]
> **先確認散熱片 body 名稱再呼叫工具。** 使用者沒給名稱時，用 `geometry_list_bodies` 列出候選
> （名稱含 HS / HEAT / SINK / FIN），請使用者指定；不可自行挑一個就執行。

## 第一步：確認要簡化的散熱片

| 散熱片型態 | 判斷方式 | 參數 |
| :--- | :--- | :--- |
| 單一 body（擠型/壓鑄，螺絲常與本體同 body） | 一個 body 就含底板＋鰭片 | `source=<名稱>` |
| 多 body 組件（銅底＋熱管板＋獨立鰭片＋上蓋） | 鰭片是許多同名 body | `source=<底座名>`、`extra_sources=[鰭片/熱管板/上蓋 名稱或 glob]` |
| 同一散熱片放了多個（各自 component） | 同名 body 出現在不同 component | `all_instances=true`（共用 master 的 instance 只做一次） |
| CPU 散熱片（銅底與框架底面齊平） | 銅底被框架包圍、底面同高 | 加 `contact_body=<銅底名>`：下凸＝銅底、接觸面 NS 只含銅底 |
| 十字形 / 多排鰭片 | 中間鰭片較長、兩側較短 | `fin_box="all"`：上凸包住所有鰭片外框（預設 `largest` 只取最大一排） |

CPU 散熱片範例（1U，兩顆 CPU 各一個 component）：

```
geometry_simplify_heatsink(
  source="1U_CUBASE",
  extra_sources=["EGS_HS_1U_FRAME-FIN_FRAME", "PRT0007", "PRT0008", "ICX_HS_1U_FIN_*"],
  body_densities={"1U_CUBASE": "copper", "PRT000*": "copper"},
  contact_body="1U_CUBASE", fin_box="all", all_instances=true,
  result_name="CPU_HS_1U_sim", named_selection="hs_bottom_cpu")
```
排除：TIM（`K39279-001`）、頂部薄片（`K35889-002`）、螺絲/彈簧（`J93604-*`、`K37*`）、2U 版本（`EGS--2U_*`）。
50 個 body 的組件單顆約 2–3 分鐘；若 SpaceClaim 先前回報內部錯誤（`Object reference not set…`），
重啟 SpaceClaim 後再跑，避免卡死。

- 多 body 組件：`extra_sources` **只放散熱體本身**（底座、熱管板、鰭片、框架、上蓋）；
  **不要放螺絲、彈簧、背板、導熱墊 (TIM)、另一個尺寸版本的散熱片**。不確定時列出該 component 的 body 請使用者勾選。
- 材料不同時用 `body_densities`，例如 `{"1U_CUBASE": "copper"}`（可填 kg/m³ 數值或 aluminum/copper）。
- 其他選填（使用者沒提就用預設）：`material`（aluminum）、`density`、`result_name`（`<source>_sim`）、
  `named_selection`（`hs_bottom`）、`hole_min_dia_mm`（2.5）、`keep_source`（true）。

## 第二步：執行

1. 未連線先 `geometry_launch`；`geometry_list_bodies` 確認名稱存在。
2. 呼叫 `geometry_simplify_heatsink(...)`。工具規則（結果為**凸字形**方塊組，無階梯、無圓角）：
   - 底板 = 包圍盒 X-Z，Y 從鎖孔所在板底 → 鰭片根部。
   - 上凸 = 面積最大的一排鰭片範圍，鰭片根部 → 鰭片頂（只取一塊；螺絲角落留在底板上）。
   - 下凸 = 主接合底面（面積 ≥ 最大朝下層 10% 的最低朝下層）範圍，接觸面 → 板底；蓋到鎖孔時裁成與上凸同範圍。
   - 鎖孔 = 原始完整圓周的 Y 向內凹圓柱（同軸取最小孔徑）→ Y 向直圓柱貫穿；螺絲/彈簧/推銷不保留。
   - 質量 m = Σ ρᵢ·Vᵢ（原始體積）；**ρ_equiv = m / V_sim** 附加於名稱 `_rho<整數>`；主接合底面建 named selection。
   - 結果放在原始 body 所屬 component（共用 master 的各 instance 都會出現）；原始 body 保留。

## 第三步：驗證與回報

1. `geometry_screenshot(file_path=..., view="iso", bodies=[<新 body>])` 與 `view="bottom"` 目視確認：
   凸字形（底板＋上凸＋下凸）、鎖孔為直圓孔、無殘留螺絲。
2. 回報（直接引用工具回傳文字，不可自行編造數值）：原始體積、假設密度、質量、凸字形三方塊範圍、簡化後體積、
   **反推等效密度與新 body 名稱**、鎖孔數與孔徑、named selection 面數。
3. 鎖孔數 = 0、鰭片走向 = none、或「簡化完成 n/m」n < m 時，明確告知使用者並說明可能原因（見下）。

## 常見問題

| 現象 | 可能原因 / 處理 |
| :--- | :--- |
| 鎖孔數 = 0 | 孔徑 < `hole_min_dia_mm`（調小）；或孔壁非完整圓周（開口槽） |
| 鰭片走向 = none（上凸為整個包圍盒） | 找不到垂直鰭片側壁（曲面/斜鰭片）；回報使用者結果為包圍盒近似 |
| 體積異常大 | `extra_sources` 混入了螺絲/另一版本散熱片；重新確認名單 |
| 名稱重複的 named selection | 重跑前先刪除舊的 `hs_bottom` 與舊 `_sim_rho*` body |
