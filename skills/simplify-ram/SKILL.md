---
name: simplify-ram
description: 引導式 RAM 幾何簡化流程。使用者要求「簡化 RAM」時，先向使用者索取主機板、RAM、socket 三個 body 名稱，取得後才呼叫 `geometry_simplify_ram` / `geometry_simplify_ram_batch`，把 RAM 卡與其 socket 合併成座落於主機板頂面的方塊，並於方塊底面建立 named selection。
Use when:
  - 使用者要求簡化 RAM / DIMM / 記憶體條幾何（含批次、整排、全部 RAM）。
  - 需調用 MCP 工具：`geometry_simplify_ram`、`geometry_simplify_ram_batch`。
  - 限制: 三個 body 名稱必須由使用者提供，嚴禁猜測或自行從 body 清單推斷；高度軸固定為 Y。
  - 觸發關鍵字 (繁中/En): 簡化RAM, 簡化記憶體, 簡化DIMM, RAM簡化, simplify RAM, simplify DIMM.
phase_gate:
  requires: []
  produces: []
---

# RAM 幾何簡化流程

> [!CAUTION]
> **第一步一定是向使用者索取三個 body 名稱。** 取得之前，不得呼叫任何 `geometry_simplify_ram*` 工具，
> 也不得用 `geometry_list_bodies` 的結果自行挑名稱代替詢問。

## 第一步：索取三個 body 名稱（必做）

收到「簡化 RAM」要求後，先回覆並詢問：

> 簡化 RAM 需要三個 body 名稱：
> 1. 主機板名稱（motherboard）？例如 `JVPCB1074973E`
> 2. RAM 卡名稱（ram）？例如 `DIMM_DDR5_EGS`
> 3. Socket 名稱（socket）？例如 `J33`

- 使用者只給了部分名稱 → 繼續追問缺少的，不可用預設值或猜測補上。
- 使用者在原始要求中已明確寫出全部三個名稱 → 複述一次三個名稱讓使用者確認，再往下做。
- 選填參數（使用者沒提就用預設，不必主動詢問）：
  - 單組：`result_name`（預設 `RAM_simplified`）、`named_selection`（預設 `mb_bonded`）
  - 批次：`result_prefix`（預設 `RAM_simplified`）、`ns_prefix`（預設 `mb_bonded`）、`tol_mm`（預設 `2.0`）

## 第二步：確認連線與名稱存在

1. 未連線時先 `geometry_launch`（會自動掃描 50051–50055 尋找已啟動的 SpaceClaim）；模型未開啟則 `geometry_import_file`。
2. 呼叫 `geometry_list_bodies`，確認三個名稱都存在，並數出 RAM 名稱與 socket 名稱各出現幾次。
3. 任一名稱找不到 → 列出最接近的幾個 body 名稱回報使用者，請其更正，**不可自行替換後繼續**。

## 第三步：選擇單組或批次並執行

| 情況 | 工具 |
| :--- | :--- |
| 該 RAM 名稱只出現 1 次 | `geometry_simplify_ram(motherboard, ram, socket, result_name, named_selection)` |
| 該 RAM 名稱出現多次，或使用者說「全部 / 整排 / 批次」 | `geometry_simplify_ram_batch(motherboard, ram, socket, result_prefix, ns_prefix, tol_mm)` |

批次工具依 X 中心就近配對 RAM 與 socket，距離超過 `tol_mm` 的不配對；結果依 X 順序編號 `_01`、`_02`…

工具的幾何規則（高度軸 Y，簡化後為「凸字形」下寬上窄）：
- 下段**寬基座**＝ **socket** 的 X-Z footprint，Y 從主機板頂面 → socket 頂。
- 上段**窄凸柱**＝ **RAM** 的 X-Z footprint，Y 從 socket 頂 → RAM 頂（RAM 包圍盒最大 Y）。
- 兩段**聯集為單一 body**；若 socket 頂不在有效區間（退化），退回單一合併包圍盒方塊。
- 方塊**底面＝主機板頂面**（主機板包圍盒最大 Y），不是 socket 最低面。
- 於**底面（基座底）**建立 named selection；**原始 body 預設抑制**（下游排除）。

## 第四步：驗證與回報

1. 用 `geometry_screenshot(file_path=..., view="iso", bodies=[<主機板>, <新方塊名稱>...])` 拍下結果並目視確認方塊貼在板面上、範圍涵蓋 RAM 與 socket。
2. 回報內容（直接引用工具回傳的文字，不要自行編造數值）：
   - 單組：新方塊名稱、方塊尺寸與 min/max（mm）、主機板頂面 Y 與 RAM 頂 Y、named selection 是否建立成功。
   - 批次：RAM 數、socket 數、配對數、建塊數、建立的 NS 數；配對數少於 RAM 數時，明確告知有 RAM 未配對；有失敗項時逐條列出。
3. named selection 未建立成功（`created=False`）或數量對不上時，明確告知使用者，不得回報為全部成功。

## 常見錯誤

- 「RAM 頂未高於主機板頂面」：名稱給錯（例如把主機板與 RAM 對調）或模型高度軸不是 Y，請使用者核對名稱與模型方向。
- 批次配對數為 0 或偏少：RAM 陣列可能沿 Z 排列（工具只依 X 配對），或 `tol_mm` 太小。
- 手動另開的 SpaceClaim 視窗 MCP 控制不到；確認操作的是 `geometry_launch` 連上的那個實例。
