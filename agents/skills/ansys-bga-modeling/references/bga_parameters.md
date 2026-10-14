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
