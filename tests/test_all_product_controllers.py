"""全模組產品控制器 BDD 自動化測試套件 (tests/test_all_product_controllers.py).

涵蓋 9 大全新擴充模組之端對端功能驗收：
- AEDT (HFSS, Maxwell, Q3D)
- Optics (Lumerical, Zemax, Speos)
- Systems (System Coupling CHT, TwinAI ROM)
- Rocky (Rocky DEM)
- Granta (Granta MI)
- Sherlock (Sherlock PoF)
- Motor-CAD (Motor-CAD PMSM)
- Aqwa (Aqwa Marine)
- Chemkin (Chemkin Kinetics)

All comments and docstrings strictly use ASCII English.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from ansys_unified_mcp.products.aedt import tools as aedt_tools
from ansys_unified_mcp.products.optics import tools as optics_tools
from ansys_unified_mcp.products.systems import tools as systems_tools
from ansys_unified_mcp.products.rocky import tools as rocky_tools
from ansys_unified_mcp.products.granta import tools as granta_tools
from ansys_unified_mcp.products.sherlock import tools as sherlock_tools
from ansys_unified_mcp.products.motorcad import tools as motorcad_tools
from ansys_unified_mcp.products.aqwa import tools as aqwa_tools
from ansys_unified_mcp.products.chemkin import tools as chemkin_tools


class TestAllProductControllers(unittest.TestCase):
    """End-to-end BDD validation for all expanded ANSYS product controllers."""

    # 1. AEDT Electromagnetics Tests
    def test_aedt_hfss_patch_antenna(self):
        res = aedt_tools.aedt_solve_hfss(antenna_length_mm=30.0, antenna_width_mm=40.0, er=4.4)
        self.assertTrue(res.get("ok"))
        self.assertIn("resonant_frequency_ghz", res)
        self.assertLess(res["min_return_loss_db"], -10.0)

    def test_aedt_maxwell_magnetic(self):
        res = aedt_tools.aedt_solve_maxwell(current_a=5.0, turns=200, air_gap_mm=1.5, core_area_cm2=4.0)
        self.assertTrue(res.get("ok"))
        self.assertGreater(res.get("attraction_force_n", 0), 0.0)

    def test_aedt_q3d_rlcg(self):
        res = aedt_tools.aedt_extract_rlcg(trace_width_um=200.0, dielectric_height_um=150.0, er=4.4)
        self.assertTrue(res.get("ok"))
        self.assertGreater(res.get("characteristic_impedance_z0_ohm", 0), 0.0)

    # 2. Optics & Photonics Tests
    def test_optics_lumerical_waveguide(self):
        res = optics_tools.optics_solve_lumerical_waveguide(core_index=1.50, cladding_index=1.45, wavelength_um=1.55)
        self.assertTrue(res.get("ok"))
        neff = res.get("effective_index_analytical", 0.0)
        self.assertTrue(1.45 < neff < 1.50)
        self.assertLess(res.get("relative_error_percent", 100.0), 0.1)

    def test_optics_zemax_paraxial(self):
        res = optics_tools.optics_trace_zemax_lens(radii_mm=[50.0, -50.0], thicknesses_mm=[5.0], refractive_indices=[1.0, 1.5168, 1.0])
        self.assertTrue(res.get("ok"))
        self.assertGreater(res.get("effective_focal_length_efl_mm", 0), 0.0)

    def test_optics_speos_photometry(self):
        res = optics_tools.optics_evaluate_speos_photometry(luminous_flux_lumen=1200.0, distance_m=2.5)
        self.assertTrue(res.get("ok"))
        self.assertGreater(res.get("on_axis_illuminance_lux", 0), 0.0)

    # 3. Systems & Digital Twin Tests
    def test_systems_coupling_cht(self):
        res = systems_tools.systems_solve_coupling_cht(t_bulk_k=500.0, h_conv_w_m2k=250.0, l_solid_m=0.02, k_solid_w_mk=20.0, t_cold_k=300.0)
        self.assertTrue(res.get("ok"))
        self.assertTrue(res.get("converged"))
        self.assertLess(res.get("flux_relative_error_pct", 100.0), 1.5)

    def test_systems_twin_rom(self):
        res = systems_tools.systems_run_twin_rom(time_steps=30, dt_s=0.1, input_magnitude=1.0)
        self.assertTrue(res.get("ok"))
        self.assertGreater(res.get("final_rom_state", 0), 0.0)

    # 4. Rocky DEM Tests
    def test_rocky_dem_solve(self):
        res = rocky_tools.rocky_solve(num_particles=50, drop_height_m=0.5, sim_time_s=0.5)
        self.assertTrue(res.get("ok"))
        self.assertEqual(res.get("mass_conservation_pct"), 100.0)

    # 5. Granta MI Materials Tests
    def test_granta_search_and_compliance(self):
        search_res = granta_tools.granta_search_material(query_name="steel")
        self.assertTrue(search_res.get("ok"))
        self.assertGreater(search_res.get("count", 0), 0)

        comp_res = granta_tools.granta_evaluate_compliance(material_id="structural_steel", regulation="RoHS")
        self.assertTrue(comp_res.get("ok"))
        self.assertTrue(comp_res.get("compliant"))

        temp_res = granta_tools.granta_get_temperature_curve(material_id="structural_steel", temperature_c=300.0)
        self.assertTrue(temp_res.get("ok"))
        self.assertLess(temp_res.get("temperature_adjusted_value", 999), temp_res.get("base_value_20c", 0))

    # 6. Sherlock Reliability Tests
    def test_sherlock_thermal_and_vibration_life(self):
        therm_res = sherlock_tools.sherlock_run_thermal_fatigue_life(delta_t_c=80.0, package_diagonal_mm=25.0)
        self.assertTrue(therm_res.get("ok"))
        self.assertGreater(therm_res.get("median_cycles_to_failure_n50", 0), 100)

        vib_res = sherlock_tools.sherlock_run_vibration_life(g_rms=5.0, pcb_natural_freq_hz=120.0)
        self.assertTrue(vib_res.get("ok"))
        self.assertGreater(vib_res.get("vibration_life_hours", 0), 0.0)

    # 7. Motor-CAD PMSM Tests
    def test_motorcad_efficiency(self):
        res = motorcad_tools.motorcad_solve_efficiency_point(pole_pairs=4, flux_linkage_wb=0.05, stator_resistance_ohm=0.10, omega_m_rad_s=300.0, torque_target_nm=15.0)
        self.assertTrue(res.get("ok"))
        self.assertGreater(res.get("electromagnetic_efficiency_pct", 0), 85.0)

    # 8. Aqwa Marine Tests
    def test_aqwa_heave_oscillation(self):
        res = aqwa_tools.aqwa_solve_heave_oscillation(length_m=20.0, beam_m=10.0, draft_m=2.0)
        self.assertTrue(res.get("ok"))
        self.assertGreater(res.get("natural_period_numerical_s", 0), 0.0)
        self.assertLess(res.get("period_relative_error_pct", 100.0), 0.5)

    # 9. Chemkin Kinetics Tests
    def test_chemkin_0d_reactor(self):
        res = chemkin_tools.chemkin_solve_0d_reactor(temperature_k=500.0, initial_ca_mol_m3=1.0, t_end_s=5.0)
        self.assertTrue(res.get("ok"))
        self.assertTrue(res.get("mass_conserved"))
        self.assertLess(res.get("relative_error_half_life_pct", 100.0), 0.05)


if __name__ == "__main__":
    unittest.main()
