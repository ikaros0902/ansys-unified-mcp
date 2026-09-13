---
name: ansys-lsdyna-explicit
description: LS-DYNA 顯式動力學與落摔分析路由指引（已完整收斂至 ansys-lsdyna）。
Use when:
  - 需執行顯式動力學模擬、落摔衝擊 (Drop Test) 或組裝卡片。
  - 觸發關鍵字 (繁中/En): LS-DYNA, 顯式動力學, 落摔分析, Drop Test.
---

# LS-DYNA 顯式動力學分析導引

> [!NOTE]
> **架構整併導引**：
> 本技能已全面收斂至核心主技能 **[`ansys-lsdyna`](../ansys-lsdyna/SKILL.md)**。
> 請直接查閱下列專責模組，無需載入舊版重複文檔：
> - **主控手冊**：[`ansys-lsdyna/SKILL.md`](../ansys-lsdyna/SKILL.md)
> - **材料本構與卡片子手冊**：[`ansys-lsdyna/reference/material_cards.md`](../ansys-lsdyna/reference/material_cards.md)
> - **接觸、沙漏與時間步長子手冊**：[`ansys-lsdyna/reference/contacts_and_timestep.md`](../ansys-lsdyna/reference/contacts_and_timestep.md)
> - **經典落摔自動化腳本**：[`ansys-lsdyna/scripts/run_drop_test_demo.py`](../ansys-lsdyna/scripts/run_drop_test_demo.py)
