---
name: ansys-optislang
description: ANSYS optiSLang 參數敏感度分析、MOP 最佳預測元模型與多目標 Pareto 尋優工程主控手冊。當需要進行工程參數敏感度分析 (Sensitivity)、實驗設計 (DoE) 或拉丁超立方抽樣 (LHS)、訓練並評估最佳預測代理模型 MOP (Metamodel of Optimal Prognosis) 與預測係數 (CoP)、依據總靈敏度指數 (TSI) 過濾非關鍵變數進行工程降維、或配置單目標與多目標 Pareto 最佳化尋優 (NLPQLP 梯度法 / NSGA-II 演化演算法) 時使用。觸發關鍵字 (繁中/En): optiSLang, optislang, 代理模型, MOP, 敏感度分析, Sensitivity, 最佳化, Pareto, LHS抽樣, 預測係數, CoP, 總靈敏度指數, TSI, DoE。
---

# ANSYS optiSLang 代理模型與最佳化工程主控手冊

本手冊為 ANSYS optiSLang 參數敏感度分析、MOP 最佳預測元模型與多目標尋優之標準主控規範，依據林明志標準建立「工程 SOP + 子手冊路由 + 判斷力準則 + 自動化腳本」架構。

---

## 一、參數化研究到最佳化的標準 SOP 流程

```mermaid
flowchart TD
    S1[步驟 1: 參數與響應空間定義
定義連續/離散變數區間與機率分佈] --> S2[步驟 2: 實驗設計 DoE / LHS 抽樣
空間填充 DoE；樣本數依維度、非線性、預算及驗證誤差決定]
    S2 --> S3[步驟 3: 敏感度分析與 TSI 篩選降維
計算總靈敏度指數 剔除 TSI < 5% 雜訊變數]
    S3 --> S4[步驟 4: MOP 代理模型自動訓練與評估
多項式/Kriging/MLS 競賽 檢核 CoP >= 0.8]
    S4 -->|驗證不足| S6[自適應補充資訊樣本 / 檢討設計區間]
Pareto 前沿非支配解集搜尋與實體驗證]
    S4 -->|驗證不足| S6[自適應補充資訊樣本 / 檢討設計區間]
    S6 --> S2
```

1. **步驟 1（參數與響應空間）**：梳理 CAD/CAE 輸入參數，明確定義連續或離散範圍及隨機機率分佈（Uniform / Normal）。
2. **步驟 2（DoE 與 LHS 抽樣）**：抽樣方法與點數依維度、交互作用、噪聲、失敗率、計算預算及驗證方式規劃；不存在可保證充分性的通用點數公式。
3. **步驟 3（敏感度與簡化）**：使用目標版本支援的方法，將低影響參數列為候選簡化項；凍結前需確認模型有效範圍與工程目標。
4. **步驟 4（代理模型評估）**：檢視 CoP、交叉驗證/留出誤差、殘差與驗證資料；接受標準須事先定義，不套用通用 CoP 門檻。
5. **步驟 5（Pareto 尋優與覆核）**：將高品質 MOP 導出為 ProxySolver，驅動演化演算法（EA）或梯度法（NLPQLP）獲取 Pareto 前沿解，並對最優折衷解進行 CAE 實體二次覆核。

---

## 二、專精參考手冊路由表 (Router)

| 領域分類 | 專精子手冊路徑 | 核心內容與工程焦點 |
| :--- | :--- | :--- |
| **API 查證** | `api_search(query, product="optislang")` | `ansys.optislang.core.*` 類別/成員存在性查證，避免幻覺 API |
| **實驗設計** | `references/doe_sampling.md` | LHS/DoE 選擇、空間覆蓋與案例化樣本預算。 |
| **敏感度矩陣** | `references/sensitivity_matrix.md` | TSI、相關矩陣與依案例驗證的變數簡化。 |
| **MOP 元模型** | `references/mop_metamodel.md` | MOP 最佳模型競賽架構（多項式/MLS/Kriging/MLP）、最佳子空間搜索、ProxySolver 導出與毫秒級推論。 |
| **最佳化演算法** | `references/optimization_algorithms.md` | 局部梯度法 (`NLPQLPActor`) vs 全域啟發式 (`NOAActor` / `EAActor`)、多目標 Pareto 前沿解集提取。 |
| **判斷力庫** | `references/optislang_judgment.md` | CoP、共線性與驗證誤差的案例化解讀；失敗設計點與外推風險。 |
| **自動化腳本** | `scripts/setup_mop_workflow_demo.py` | 完整 optiSLang 原生 Python 流程建立腳本，內建 CoP 評估、TSI 降維過濾與過擬合警示模組。 |

---

## 三、工程檢核

- DoE 樣本數、CoP、TSI、相關係數與 VIF 是依模型與驗證策略判讀的指標，不採用跨案例固定門檻。
- 設計點失敗須保留失敗狀態；不得以零值填補後參與模型訓練或候選排序。
- 代理模型在設計範圍之外屬外推風險；以真實求解覆核候選最優點並記錄誤差。
- 全域最佳化是否適用，依設計維度、代理模型驗證、限制條件與計算預算決定；沒有固定變數數量禁令。

## 官方範例路由

需重現官方輸入與輸出驗收時，讀取 [references/official_examples.md](references/official_examples.md)；依該文件分開檢查啟動、模型修改與求解授權。
