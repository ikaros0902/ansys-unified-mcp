# BGA 幾何參數與陣列分佈技術參考

## 一、錫球鼓形狀（Spheroid）構建方程式

在真實晶片回焊（Reflow）過程中，錫球受到表面張力與封裝體自重影響呈現腰鼓形。在 SpaceClaim 自動化建模中：
1. 建立外徑為 $D_{\text{bga}}$ 的原始球體。
2. 上下以平面切除至高度 $H_{\text{bga}}$。
3. 頂部與底部截面圓形直徑 $D_{\text{pad\_interface}} = \sqrt{D_{\text{bga}}^2 - H_{\text{bga}}^2}$。
4. 銜接圓柱狀焊盤（Pad），提供網格劃分時的面-面連續接觸介面。

---

## 二、陣列模式 (Array Schemes)

1. **矩形標準陣列 (Rule 0)**：
   - 步距：$\Delta X = \text{pitch}_1$，$\Delta Y = \text{pitch}_2$。
   - 總球數：$N_{\text{total}} = N_1 \times N_2$。
2. **交錯式六角陣列 (Rule 2)**：
   - 偶數列：$X = i \cdot \text{pitch}$。
   - 奇數列：$X = (i + 0.5) \cdot \text{pitch}$。
   - $Y$ 向步距：$\Delta Y = \text{pitch} \cdot \sin(60^\circ) = 0.866 \cdot \text{pitch}$。

---

## 三、MCP 工具與常見參數

`geometry_create_bga_array` 在目前已連線的 SpaceClaim Geometry session 建立幾何；尺寸及間距參數均使用 mm。工具會載入套件內的 `bga_array` 腳本資源。此技能目錄下的 `scripts/bga_ball_creator.ironpy` 與 `scripts/bga_array_creator.ironpy` 是腳本範例，不是 MCP 工具的載入路徑。

```python
await geometry_create_bga_array(
    bga_diameter_mm=0.65,
    bga_height_mm=0.51,
    low_pad_d_mm=0.50,
    low_pad_h_mm=0.02,
    high_pad_d_mm=0.50,
    high_pad_h_mm=0.02,
    n_dir1=10,
    n_dir2=10,
    pitch_dir1_mm=1.0,
    pitch_dir2_mm=1.0,
    array_type=0,
    mating_face="bottom",
)
```

| 參數 | 舊技能列出的典型範圍 (mm) | 說明 |
| :--- | :--- | :--- |
| `bga_diameter_mm` | `0.40–0.76` | 錫球自由外徑 |
| `bga_height_mm` | `0.30–0.60` | 回焊後 stand-off 高度 |
| `low_pad_d_mm`, `high_pad_d_mm` | `0.35–0.55` | 下、上焊盤直徑 |
| `pitch_dir1_mm` | `0.80–1.27` | X 向中心距；Y 向另由 `pitch_dir2_mm` 指定 |

以上是原技能記載的常見值，不是工具輸入限制或設計驗收標準；應依封裝規格選值。當需要實體焊盤時，焊盤厚度應為正值以避免退化幾何。大量陣列會增加 SpaceClaim 記憶體需求；原技能以超過 2,000 顆作為考慮分批或分區管理的提醒，實際上限依主機資源與模型而異。
