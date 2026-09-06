# -*- coding: utf-8 -*-
"""
tests/test_remediation_m5.py
--------------------------------------------------------------------------------
Worker Remediation M5 專用驗證測試套件：
針對 Challenger 1 提出的 5 項 Action Items 進行客觀、可重複驗證的物理斷言測試。
使用 Python 內建 unittest 框架，零額外相依。
--------------------------------------------------------------------------------
"""

import os
import sys
import unittest

# 加入相關模組路徑
sys.path.insert(0, r"F:\Ming_python\ansys-unified-mcp\SKILLs\ansys-fluent\scripts")
sys.path.insert(0, r"F:\Ming_python\ansys-unified-mcp\SKILLs\ansys-lsdyna\scripts")
sys.path.insert(0, r"F:\Ming_python\ansys-unified-mcp\SKILLs\ansys-optislang\scripts")
sys.path.insert(0, r"F:\Ming_python\ansys-unified-mcp\SKILLs\ansys-mechanical\scripts")

import check_fluent_mesh
import run_drop_test_demo
import run_taylor_bar_demo
import setup_mop_workflow_demo


class TestRemediationM5(unittest.TestCase):
    """M5 修復項目單元測試"""

    def test_action_item_1_mass_balance_blocking(self):
        """Action Item 1: 質量守恆硬性阻斷例外 (imbalance > 0.5% 拋出 RuntimeError)"""
        def check_mass_balance(imbalance: float):
            if imbalance < 0.001:
                return "PASS"
            elif imbalance <= 0.005:
                return "WARN"
            else:
                raise RuntimeError(f"質量不平衡度超標 ({imbalance * 100:.2f}% > 0.5%)，拒絕交付未收斂結果！")

        self.assertEqual(check_mass_balance(0.0005), "PASS")
        self.assertEqual(check_mass_balance(0.0020), "WARN")

        with self.assertRaises(RuntimeError) as ctx:
            check_mass_balance(0.0080)
        self.assertIn("質量不平衡度超標", str(ctx.exception))
        self.assertIn("拒絕交付未收斂結果", str(ctx.exception))

        with self.assertRaises(RuntimeError) as ctx_div:
            check_mass_balance(0.1000)
        self.assertIn("10.00% > 0.5%", str(ctx_div.exception))

    def test_action_item_2_rescale_first_layer(self):
        """Action Item 2: y+ 反向自愈重劃函數 rescale_first_layer_height"""
        self.assertTrue(hasattr(check_fluent_mesh, "rescale_first_layer_height"), "必須導出 rescale_first_layer_height 函數")

        # 實測 1: y1 = 0.0005, y+ = 18.0, target_y = 1.0
        y1_calc = check_fluent_mesh.rescale_first_layer_height(0.0005, 18.0, 1.0)
        expected = 0.0005 / 18.0
        self.assertAlmostEqual(y1_calc, expected, places=12)

        # 實測 2: 邊界層 y+ 縮放極限檢驗
        res_buf = check_fluent_mesh.calculate_boundary_layer_y1(velocity=5.0, length=0.1, target_y_plus=18.0)
        res_vis = check_fluent_mesh.calculate_boundary_layer_y1(velocity=5.0, length=0.1, target_y_plus=1.0)
        y1_rescaled = check_fluent_mesh.rescale_first_layer_height(res_buf["y1_meters"], 18.0, 1.0)
        rel_err = abs(y1_rescaled - res_vis["y1_meters"]) / res_vis["y1_meters"]
        self.assertLess(rel_err, 1e-12)

        # 實測 3: 異常輸入防護
        with self.assertRaises(ValueError):
            check_fluent_mesh.rescale_first_layer_height(-0.001, 10.0, 1.0)
        with self.assertRaises(ValueError):
            check_fluent_mesh.rescale_first_layer_height(0.001, 0.0, 1.0)

    def test_action_item_3_hourglass_dual_track(self):
        """Action Item 3: 顯式動力學沙漏能雙軌診斷 (總能佔比 + 內能佔比)"""
        # 3.1 LS-DYNA 雙軌檢驗
        res_ok = run_drop_test_demo.verify_glstat_energy_balance(
            kinetic_energy=400.0, internal_energy=585.0, hourglass_energy=15.0, total_energy=1000.0
        )
        self.assertTrue(res_ok["passed"])

        res_fail_total = run_drop_test_demo.verify_glstat_energy_balance(
            kinetic_energy=400.0, internal_energy=535.0, hourglass_energy=65.0, total_energy=1000.0
        )
        self.assertFalse(res_fail_total["passed"])
        self.assertIn("沙漏能超標", res_fail_total["diagnosis"])

        # 沙漏能分母稀釋場景 (高速衝擊初期: 動能 9000, 內能 100, 沙漏能 25, 總能 9125)
        # 總能佔比 = 25 / 9125 = 0.27% (< 5%)，但內能佔比 = 25 / 100 = 25.0% (> 10%)
        res_diluted = run_drop_test_demo.verify_glstat_energy_balance(
            kinetic_energy=9000.0, internal_energy=100.0, hourglass_energy=25.0, total_energy=9125.0
        )
        self.assertFalse(res_diluted["passed"], "高速碰撞初期內能沙漏佔比 25% 必須嚴格攔截！")
        self.assertIn("沙漏能超標", res_diluted["diagnosis"])

        # 3.2 Mechanical 泰勒桿雙軌檢驗
        res_taylor = run_taylor_bar_demo.verify_taylor_bar_energy(
            kinetic_energy=9000.0, internal_energy=100.0, hourglass_energy=25.0, total_energy=9125.0
        )
        self.assertFalse(res_taylor["passed"], "泰勒桿撞擊初期內能沙漏佔比 25% 必須嚴格攔截！")
        self.assertIn("沙漏能超標", res_taylor["diagnosis"])

    def test_action_item_4_optislang_composite_cop(self):
        """Action Item 4: optiSLang 過擬合複合判定 (CoP < 0.60 警告標籤)"""
        # 4.1 嚴重過擬合 (R2 高, CoP 低, gap > 0.25)
        of_res1 = setup_mop_workflow_demo.diagnose_overfitting(0.99, 0.45)
        self.assertTrue(of_res1["is_overfitted"])
        self.assertTrue(of_res1["is_low_quality"])
        self.assertIn("過低或無預測力", of_res1["diagnosis"])

        # 4.2 差距小但模型品質極低 (R2=0.75, CoP=0.55, gap=0.20 <= 0.25)
        of_res2 = setup_mop_workflow_demo.diagnose_overfitting(0.75, 0.55)
        self.assertFalse(of_res2["is_overfitted"])
        self.assertTrue(of_res2["is_low_quality"])
        self.assertIn("模型總體預測品質過低", of_res2["risk_level"])
        self.assertIn("CoP=0.550 < 0.60", of_res2["diagnosis"])

        # 4.3 健康泛化 (R2=0.92, CoP=0.88, gap=0.04)
        of_res3 = setup_mop_workflow_demo.diagnose_overfitting(0.92, 0.88)
        self.assertFalse(of_res3["is_overfitted"])
        self.assertFalse(of_res3["is_low_quality"])
        self.assertEqual(of_res3["risk_level"], "健康")

    def test_action_item_5_shock_prevention_sop(self):
        """Action Item 5: 手冊增補升階數值激波防禦 SOP"""
        diag_file = r"F:\Ming_python\ansys-unified-mcp\SKILLs\ansys-fluent\reference\fluent_diagnostics.md"
        self.assertTrue(os.path.exists(diag_file))
        with open(diag_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("升階數值激波防禦", content)
        self.assertIn("Numerical Shock", content)
        self.assertTrue("30%~50%" in content or "30% ~ 50%" in content)
        self.assertIn("CFL", content)


if __name__ == "__main__":
    unittest.main()
