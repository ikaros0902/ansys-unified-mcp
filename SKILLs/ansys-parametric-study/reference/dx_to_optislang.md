# DesignXplorer 與 optiSLang 雙軌選型決策矩陣 (dx_to_optislang.md)

本手冊定義 ANSYS Workbench DesignXplorer (DX) 與 optiSLang 的雙軌選型原則與技術遷移決策矩陣。

---

## 一、雙軌選型對比矩陣 (Migration Matrix)

| 評估維度 | Workbench DesignXplorer (DX) | ANSYS optiSLang (高階代理模型與最佳化) | 遷移判定條件 |
| :--- | :--- | :--- | :--- |
| **參數維度承載力** | 適合 $\le 10$ 個設計變數 | 可承載數十至上百個變數（TSI 自動篩選） | 參數數量 $> 10$ 時強制升級 |
| **代理模型架構** | 單一固定模型（多項式、Kriging、神經網路） | **MOP 自適應混合競賽**（Polynomial / Kriging / MLS / MLP） | 響應非線性強或 CoP 要求 $\ge 0.8$ |
| **品質驗證判準** | 傳統決定係數 $R^2$（易過擬合） | **預測係數 CoP (Cross-Validation)**（客觀無偏） | 需確保模型真實泛化能力 |
| **計算容錯與並行** | 依賴 Workbench 串行或本機 RSM 隊列 | 支援強大的容錯、失效樣本略過、分散式叢集並行 | 計算量大或偶發個別樣本求解發散時 |
| **不確定性分析** | 基礎蒙地卡羅 Six Sigma 模組 | 深度穩健性分析 (Robustness)、信賴度分析、自適應抽樣 | 要求量產良率與公差邊界評估 |

---

## 二、客觀驗證完成條件 (Verification Conditions)

1. **設計點更新完整率**：批次更新設計點後，有效收斂點比例必須 $\ge 95\%$；若失敗率 $> 5\%$，必須檢查網格品質或接觸邊界收斂性。
2. **代理模型選型品質門檻**：若採用代理模型進行最佳化，其多重交叉驗證指標必須滿足 $\text{CoP} \ge 0.80$；若 $\text{CoP} < 0.80$，判定模型不可信，必須升級至 optiSLang 或縮小設計空間。
3. **變數顯著性篩選**：升級至 optiSLang 時，必須依據 $\text{TSI} \ge 0.05$ 準則保留關鍵驅動變數，剔除非顯著變數後方可進行 Pareto 多目標尋優。
