---
name: shock-analysis-workflow
description: ANSYS Mechanical LS-DYNA 衝擊與落摔分析端到端自動化管線編排，協調 8 個模組化 Session 技能。
phase_gate:
  requires: []
  produces: []
---

# 衝擊分析自動化工作流編排手冊 (LS-DYNA)

## 工作流概述
本工作流將 ANSYS Mechanical (LS-DYNA 顯式動力學) 35G 衝擊分析流程全自動化，串接 8 個模組化 Session 專業技能：

1. `01-material-assignment`：基於規則的材料映射 (*PCB*, *CHASSIS*, *SCREW*)。
2. `02-contact-creation`：自動單表面接觸 (*CONTACT_AUTOMATIC_SINGLE_SURFACE) 與 Tied 接觸。
3. `03-mesh-tuning`：網格尺寸控制與嚴格顯式時間步長準則 (dt >= 2e-8 s)。
4. `04-connection-rm`：遠端點 (Remote Point) 與遠端質量 (Remote Mass) MPC 建置。
5. `05-section-assignment`：中面薄殼厚度與實體單元公式 (ELFORM) 指派。
6. `06-constraint-load`：半正弦衝擊脈衝或落摔初速度配置與全域阻尼。
7. `07-solve-monitor`：LS-DYNA 求解器執行與能量平衡比率即時監控 (0.9 ~ 1.1)。
8. `08-post-process-report`：等效應力 (von-Mises)/位移提取、PASS/FAIL 判定與報告生成。

## 執行時序
```
[CAD/具名選擇]
      │
      ▼
[01-材料指派] ──▶ [02-接觸建立] ──▶ [03-網格調優 (dt>=2e-8s)] ──▶ [04-遠端點/質量]
                                                                        │
                                                                        ▼
[08-產出報告] ◀── [07-求解與能量監控] ◀── [06-約束與衝擊載荷] ◀── [05-截面指派]
```
