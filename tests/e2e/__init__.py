# -*- coding: utf-8 -*-
"""Tier 3: ANSYS Unified MCP 2.0 合成端到端場景驗收測試套件 (tests/e2e).

本套件包含三大核心高保真合成驗收場景：
1. test_e2e_random_vibration_gate.py: 隨機振動模態質量不足 (<90%) 物理閘門硬性阻斷與自愈處方箋
2. test_e2e_drop_test_hourglass.py: LS-DYNA 落摔衝擊沙漏能超標 (>5%) Watchdog 即時解析與 CircuitBreaker 早期熔斷
3. test_e2e_thermal_warpage_cell_link.py: 回流焊熱-結構翹曲 Workbench TransferData 單元直通、沙盒求解與三位一體報告產出
"""
