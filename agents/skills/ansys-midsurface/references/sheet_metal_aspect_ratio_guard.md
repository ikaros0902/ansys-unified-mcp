# 板金薄壁縱橫比防呆機制 (Sheet Metal Aspect Ratio Guard)

## 一、邊界案例背景：2mm × 2mm × 2mm 立方體的誤判陷阱

若一個實體長、寬、高各為 2mm（正方體）：
* 表面積：$6 \times 4\text{ mm}^2 = 24\text{ mm}^2$
* 任一對平行面的面積和：$4 + 4 = 8\text{ mm}^2$，佔總面積比率：
  $$prim\_ratio = \frac{8}{24} = 33.33\%$$
* 若程式碼中板金主面面積比例閾值乘以了寬放係數 0.40（$0.40 \times 0.40 = 0.16 = 16\%$）：
  $$33.33\% \ge 16\%$$
  這將導致 2mm 立方體完全符合厚度（$t=2\text{ mm} \le 3\text{ mm}$）、面積差（$0.0 \le 0.6$）與主面比例（$33\% \ge 16\%$），被**錯誤判定為板金件**，並在厚度 1.0mm 處抽出一片 $2\text{ mm} \times 2\text{ mm}$ 的無效中面！

---

## 二、力學與 FEA 物理本質

在有限元素分析（FEA）與板金成型理論中：
1. **薄壁殼單元假說（Shell Element Assumptions）**：
   要求結構在厚度方向的應力 $\sigma_z \approx 0$（平面應力假說），特徵跨距（Span）必須遠大於厚度（通常要求 $\text{Span} / t \ge 5 \sim 10$）。
2. **立方體實體塊（Bulk Block）**：
   長寬厚皆為 2mm，屬於標準三維實體，三向應力狀態顯著，必須使用實體單元（Solid / Hex / Tet）分析，嚴禁抽取中面。

---

## 三、縱橫比防呆公式與實作

在 `is_sheet_metal_body_classic` 判定中加入第四重硬門檻：

$$\text{Aspect Ratio} = \frac{\sqrt{\max(A_{\text{skin1}}, A_{\text{skin2}})}}{\text{Thickness}} \ge 2.0$$

```python
# Aspect ratio guard
max_skin_area = max(first_area, second_area)
aspect_ratio = (max_skin_area ** 0.5) / thickness if thickness > 0 else 0.0
min_aspect_ratio = globals().get("MIN_SHEET_ASPECT_RATIO", 2.0)

return (thickness <= max_thickness_m and
        rel_diff <= area_diff_ratio and
        prim_ratio >= (main_surf_ratio * 0.40) and
        aspect_ratio >= min_aspect_ratio)
```

### 數值對比：
* **2mm × 2mm × 2mm 立方體**：
  $\text{Aspect Ratio} = \frac{\sqrt{4\text{ mm}^2}}{2\text{ mm}} = 1.0 < 2.0 \implies \mathbf{Solid}$（直接排除）
* **10mm × 10mm × 2mm 薄板**：
  $\text{Aspect Ratio} = \frac{\sqrt{100\text{ mm}^2}}{2\text{ mm}} = 5.0 \ge 2.0 \implies \mathbf{Sheet\ Metal}$（正常通過）
* **微型 5mm × 5mm × 0.5mm 零件**：
  $\text{Aspect Ratio} = \frac{\sqrt{25\text{ mm}^2}}{0.5\text{ mm}} = 10.0 \ge 2.0 \implies \mathbf{Sheet\ Metal}$（正常通過）
