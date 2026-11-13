# SpaceClaim ACT Wizard XML 介面人因工程設計規範

## 一、排版與操作心智模型 (Mental Model)

在 SpaceClaim ACT Wizard 開發中，Wizard 介面是用戶配置模擬參數的第一入口。表單屬性（`<property>`）的順序應遵循「主控開關 -> 關聯幾何判定標準 -> 特徵容差 -> 後處理動作」由上至下的自然操作流：

### 推薦架構：
1. **主控檢查開關 (Feature Gate)**：如 `Enable sheet metal check`。
2. **厚度判定範圍 (Core Geometric Limits)**：如 `Maximum thickness`、`Minimum thickness`。緊接在主開關下方，讓使用者清楚明白這是該開關的直接判斷依據。
3. **幾何比例與容差 (Feature Tolerances)**：如 `Main surface ratio`、`Area difference ratio`、`Complex feature threshold`。
4. **完成後處理動作 (Post-Processing Actions)**：如 `Hide source bodies after successful midsurface creation`，統一放置在最底部。

---

## 二、標準 XML 範本

```xml
<extension name="SC_midsurface_Agent" minorversion="1" version="2023" icon="images/Jabil.PNG">
  <imagedirectory>.</imagedirectory>
  <guid>3d8f1a2b-6c4e-4f9a-b2d1-7e5c9a3f6b10</guid>
  <script src="SC_midsurface_Agent.py" compiled="false"/>
  <wizard name="SC_midsurface_Agent" caption="SC Midsurface Agent" version="1" context="SpaceClaim" icon="images/Jabil.PNG">
    <step layout="Layout1@SC_midsurface_Agent" name="Step_1" version="0" caption="Midsurface Creation" HelpFile="help/help1.html">
      <description>Create midsurfaces for the currently selected solid bodies.</description>
      
      <!-- 1. 判定主開關 -->
      <property control="boolean" name="ENABLE_SHEET_METAL_CHECK" caption="Enable sheet metal check" persistent="False" parameterizable="False" default="true" />
      
      <!-- 2. 板金厚度範圍 (直接歸屬於板金判定) -->
      <property control="float" name="MAX_THICKNESS" caption="Maximum thickness (mm)" persistent="False" parameterizable="False" default="3.0" />
      <property control="float" name="MIN_THICKNESS" caption="Minimum thickness (mm)" persistent="False" parameterizable="False" default="0.3" />
      
      <!-- 3. 特徵比例與容差門檻 -->
      <property control="float" name="MAIN_SURFACE_RATIO" caption="Main surface ratio" persistent="False" parameterizable="False" default="0.40" />
      <property control="float" name="AREA_DIFFERENCE_RATIO" caption="Area difference ratio" persistent="False" parameterizable="False" default="0.60" />
      <property control="float" name="COMPLEX_AREA_DIFF" caption="Complex feature area-difference threshold" persistent="False" parameterizable="False" default="0.05" />
      
      <!-- 4. 後處理動作 (完成後是否隱藏實體，置於底部) -->
      <property control="boolean" name="HIDE_NON_SHEET_BODIES" caption="Hide source bodies after successful midsurface creation" persistent="False" parameterizable="False" default="true" />
      
      <componentStyle component="Submit">
        <background-color>#003865</background-color>
      </componentStyle>
      <callbacks>
        <onupdate>onupdateStep</onupdate>
      </callbacks>
    </step>
  </wizard>
</extension>
```

---

## 三、ACT 後端讀取相容性原則

在 Python 腳本中讀取 Wizard 屬性時：
* 必須使用屬性鍵值讀取（如 `_read_wizard_property(props, "MAX_THICKNESS", default)`），切勿依賴索引順序（Index）。
* 如此一來，XML 介面無論如何調整位置或增刪屬性，後端邏輯均能 100% 保持穩定相容。
