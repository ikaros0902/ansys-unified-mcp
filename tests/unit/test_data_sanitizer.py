"""Unit test suite for Stage 0 Data Sanitizer and Secret Redaction Gate."""

from __future__ import annotations

import copy
import json
import pytest

from ansys_unified_mcp.core.data_sanitizer import (
    DataSanitizer,
    REDACTED_PROPRIETARY_ALLOY,
    REDACTED_ASPHERIC_COEFF,
    REDACTED_LICENSE_SERVER,
    REDACTED_USER,
    REDACTED_API_KEY,
    REDACTED_SECRET,
    REDACTED_TOKEN,
    sanitize_material_properties,
    sanitize_optical_parameters,
    sanitize_bom_and_metadata,
    sanitize_text,
    sanitize_evidence_payload,
)


class TestMaterialSanitization:
    """Test suite for CAE material property sanitization."""

    def test_material_dict_linear_preservation_and_plastic_redaction(self) -> None:
        raw_mat = {
            "name": "Proprietary Titanium Alloy",
            "youngs_modulus": 113.8e9,
            "poissons_ratio": 0.34,
            "density": 4430.0,
            "secant_cte": 8.6e-6,
            "thermal_conductivity": 6.7,
            "johnson_cook": {
                "A": 862e6,
                "B": 331e6,
                "n": 0.34,
                "C": 0.012,
                "m": 0.8,
                "t_melt": 1878.0,
            },
            "cowper_symonds": {
                "c": 40.0,
                "p": 5.0,
            },
            "stress_strain_curve": [
                [0.0, 862e6],
                [0.02, 910e6],
                [0.05, 960e6],
            ],
            "granta_record_id": "GRANTA-MIL-HDBK-5J-TI64",
        }

        sanitized = sanitize_material_properties(raw_mat)
        assert isinstance(sanitized, dict)

        # Standard linear elastic properties must be retained
        assert sanitized["youngs_modulus"] == 113.8e9
        assert sanitized["poissons_ratio"] == 0.34
        assert sanitized["density"] == 4430.0
        assert sanitized["secant_cte"] == 8.6e-6
        assert sanitized["thermal_conductivity"] == 6.7

        # Proprietary non-linear constants and tables must be redacted
        assert sanitized["johnson_cook"] == REDACTED_PROPRIETARY_ALLOY
        assert sanitized["cowper_symonds"] == REDACTED_PROPRIETARY_ALLOY
        assert sanitized["stress_strain_curve"] == REDACTED_PROPRIETARY_ALLOY
        assert sanitized["granta_record_id"] == REDACTED_PROPRIETARY_ALLOY

    def test_material_dict_flat_keys(self) -> None:
        flat_mat = {
            "elastic_modulus": 200e9,
            "poissons_ratio": 0.3,
            "jc_a": 792e6,
            "jc_b": 510e6,
            "jc_n": 0.26,
            "cs_c": 40.0,
            "cs_p": 5.0,
            "miso_table": [[0.0, 400e6], [0.1, 450e6]],
        }

        sanitized = sanitize_material_properties(flat_mat)
        assert isinstance(sanitized, dict)
        assert sanitized["elastic_modulus"] == 200e9
        assert sanitized["poissons_ratio"] == 0.3
        assert sanitized["jc_a"] == REDACTED_PROPRIETARY_ALLOY
        assert sanitized["jc_b"] == REDACTED_PROPRIETARY_ALLOY
        assert sanitized["jc_n"] == REDACTED_PROPRIETARY_ALLOY
        assert sanitized["cs_c"] == REDACTED_PROPRIETARY_ALLOY
        assert sanitized["cs_p"] == REDACTED_PROPRIETARY_ALLOY
        assert sanitized["miso_table"] == REDACTED_PROPRIETARY_ALLOY

    def test_material_string_dyna_and_apdl(self) -> None:
        dyna_card = (
            "*KEYWORD\n"
            "*MAT_JOHNSON_COOK\n"
            "$#     mid        ro         g         a         b         n         c         m\n"
            "         1     7.8e-9    77.0e3     862.0     331.0      0.34     0.012       0.8\n"
            "*MAT_ELASTIC\n"
            "         2     7.8e-9    210.0e3       0.3\n"
            "*END"
        )
        sanitized = sanitize_material_properties(dyna_card)
        assert isinstance(sanitized, str)
        assert "*MAT_JOHNSON_COOK" in sanitized
        assert REDACTED_PROPRIETARY_ALLOY in sanitized
        assert "862.0" not in sanitized
        assert "*MAT_ELASTIC" in sanitized

        apdl_card = (
            "/PREP7\n"
            "MP,EX,1,200E9\n"
            "MP,NUXY,1,0.3\n"
            "TB,MISO,1,1,3\n"
            "TBTEMP,0\n"
            "TBPT,,0.0,250E6\n"
            "TBPT,,0.05,320E6\n"
            "TBPT,,0.1,380E6\n"
        )
        sanitized_apdl = sanitize_material_properties(apdl_card)
        assert "MP,EX,1,200E9" in sanitized_apdl
        assert REDACTED_PROPRIETARY_ALLOY in sanitized_apdl
        assert "380E6" not in sanitized_apdl


class TestOpticalSanitization:
    """Test suite for Zemax optical parameter sanitization."""

    def test_optical_dict_aspheric_redaction(self) -> None:
        opt = {
            "surface_name": "Aspheric Objective Lens",
            "radius": 42.5,
            "conic": -0.85,
            "semi_diameter": 12.0,
            "thickness": 3.5,
            "a4": 2.15e-6,
            "a6": -4.82e-9,
            "a8": 1.05e-12,
            "a10": -3.2e-16,
        }

        sanitized = sanitize_optical_parameters(opt)
        assert isinstance(sanitized, dict)
        assert sanitized["radius"] == 42.5
        assert sanitized["conic"] == -0.85
        assert sanitized["semi_diameter"] == 12.0
        assert sanitized["thickness"] == 3.5
        assert sanitized["a4"] == REDACTED_ASPHERIC_COEFF
        assert sanitized["a6"] == REDACTED_ASPHERIC_COEFF
        assert sanitized["a8"] == REDACTED_ASPHERIC_COEFF
        assert sanitized["a10"] == REDACTED_ASPHERIC_COEFF

    def test_optical_aspheric_coefficient_list(self) -> None:
        opt = {
            "surface_type": "EVENASPH",
            "curvature": 0.04,
            "aspheric_coefficients": [0.0, 1.25e-5, -3.1e-8, 4.5e-11],
        }
        sanitized = sanitize_optical_parameters(opt)
        assert isinstance(sanitized, dict)
        coeffs = sanitized["aspheric_coefficients"]
        assert coeffs[0] == 0.0  # 2nd order preserved
        assert coeffs[1] == REDACTED_ASPHERIC_COEFF  # 4th order redacted
        assert coeffs[2] == REDACTED_ASPHERIC_COEFF  # 6th order redacted
        assert coeffs[3] == REDACTED_ASPHERIC_COEFF  # 8th order redacted

    def test_optical_string_zemax_parm(self) -> None:
        zmx_text = (
            "SURF 3\n"
            "  TYPE EVENASPH\n"
            "  CURV 0.025\n"
            "  CONI -1.0\n"
            "  PARM 1 0.0\n"
            "  PARM 2 3.456e-06\n"
            "  PARM 3 -1.234e-09\n"
            "  PARM 4 5.678e-12\n"
        )
        sanitized = sanitize_optical_parameters(zmx_text)
        assert isinstance(sanitized, str)
        assert "PARM 1 0.0" in sanitized
        assert f"PARM 2 {REDACTED_ASPHERIC_COEFF}" in sanitized
        assert f"PARM 3 {REDACTED_ASPHERIC_COEFF}" in sanitized
        assert f"PARM 4 {REDACTED_ASPHERIC_COEFF}" in sanitized
        assert "3.456e-06" not in sanitized


class TestBOMAndMetadataSanitization:
    """Test suite for BOM, part numbers, defense codenames, and GPS sanitization."""

    def test_bom_list_deterministic_anonymization(self) -> None:
        sanitizer = DataSanitizer()
        bom = [
            {"part_number": "820-00123-A", "vendor": "Foxconn", "qty": 10},
            {"part_number": "TPS54331DDAR", "vendor": "TI", "qty": 5},
            {"part_number": "820-00123-A", "vendor": "Foxconn", "qty": 20},  # Duplicate
        ]

        sanitized = sanitizer.sanitize_bom_and_metadata(bom)
        assert isinstance(sanitized, list)
        assert sanitized[0]["part_number"] == "COMP_001"
        assert sanitized[1]["part_number"] == "COMP_002"
        # Deterministic check: identical input PN gets identical generic ID
        assert sanitized[2]["part_number"] == "COMP_001"

    def test_defense_codenames_and_gps(self) -> None:
        sanitizer = DataSanitizer()
        data = {
            "project_name": "Project Aegis",
            "subproject": "Project Skunkworks",
            "facility_location": {
                "coordinates": "37.774929, -122.419416",
                "alt_coordinates": "37.774929, -122.419416",
            },
        }

        sanitized = sanitizer.sanitize_bom_and_metadata(data)
        assert isinstance(sanitized, dict)
        assert sanitized["project_name"] == "PROJ_GENERIC_001"
        assert sanitized["subproject"] == "PROJ_GENERIC_002"
        assert "ZONE_" in sanitized["facility_location"]["coordinates"]
        # Consistent mapping for identical coordinates
        assert sanitized["facility_location"]["coordinates"] == sanitized["facility_location"]["alt_coordinates"]


class TestTextAndSecretSanitization:
    """Test suite for regex filters on credentials, licenses, and paths."""

    def test_license_server_ip_and_port(self) -> None:
        raw = "Using license from 1055@10.200.1.50 or backup 27000@lic.internal.corp:27000."
        sanitized = sanitize_text(raw)
        assert REDACTED_LICENSE_SERVER in sanitized
        assert "1055@10.200.1.50" not in sanitized
        assert "27000@lic.internal.corp" not in sanitized

    def test_windows_user_path_redaction(self) -> None:
        raw = r"Output saved to C:\Users\SecretAgent47\AppData\Local\Ansys\job.log and D:/Users/Admin/results.rst."
        sanitized = sanitize_text(raw)
        assert f"C:\\Users\\{REDACTED_USER}\\AppData" in sanitized
        assert f"D:/Users/{REDACTED_USER}/results.rst" in sanitized
        assert "SecretAgent47" not in sanitized
        assert "Admin" not in sanitized

    def test_api_tokens_and_passwords(self) -> None:
        raw = (
            "OpenAI sk-proj-1234567890abcdef1234567890\n"
            "Anthropic sk-ant-api03-abcdef1234567890-xyz\n"
            "Google AIzaSyD-1234567890abcdef1234567890abc\n"
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xyz\n"
            "db_pass: password=SuperSecretPassword99!"
        )
        sanitized = sanitize_text(raw)
        assert REDACTED_API_KEY in sanitized
        assert "sk-proj-" not in sanitized
        assert "sk-ant-" not in sanitized
        assert "AIzaSyD" not in sanitized
        assert f"Bearer {REDACTED_TOKEN}" in sanitized
        assert f"password={REDACTED_SECRET}" in sanitized


class TestEvidencePayloadDeepSanitization:
    """Test suite for recursive evidence scanning and immutability."""

    def test_evidence_payload_comprehensive(self) -> None:
        raw_payload = {
            "simulation_id": "SIM_AUTO_42",
            "license_env": "ANSYSLMD_LICENSE_FILE=1055@lic-cluster.corp",
            "working_directory": r"C:\Users\JohnDoe\Simulations\DropTest",
            "material_models": {
                "titanium": {
                    "name": "Ti-6Al-4V Grade 5",
                    "youngs_modulus": 114e9,
                    "poissons_ratio": 0.33,
                    "jc_a": 862e6,
                    "jc_b": 331e6,
                    "jc_n": 0.34,
                }
            },
            "optical_prescription": {
                "surface_type": "EVENASPH",
                "radius": 22.0,
                "a4": 1.2e-5,
                "a6": -3.4e-8,
            },
            "bill_of_materials": [
                {"part_number": "820-00999-B", "qty": 2},
                {"part_number": "STM32F407VGT6", "qty": 1},
            ],
            "credentials": {
                "api_key": "AIzaSyD-9876543210zyxwvutsrqponmlkjihg",
                "auth_header": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.token",
            },
        }

        # Keep original copy for immutability check
        original_copy = copy.deepcopy(raw_payload)

        sanitized = sanitize_evidence_payload(raw_payload)

        # Immutability check: raw_payload must not be altered
        assert raw_payload == original_copy

        # Content checks
        assert REDACTED_LICENSE_SERVER in sanitized["license_env"]
        assert "JohnDoe" not in sanitized["working_directory"]
        assert sanitized["material_models"]["titanium"]["youngs_modulus"] == 114e9
        assert sanitized["material_models"]["titanium"]["jc_a"] == REDACTED_PROPRIETARY_ALLOY
        assert sanitized["optical_prescription"]["radius"] == 22.0
        assert sanitized["optical_prescription"]["a4"] == REDACTED_ASPHERIC_COEFF
        assert "COMP_" in sanitized["bill_of_materials"][0]["part_number"]
        assert sanitized["credentials"]["api_key"] == REDACTED_API_KEY
        assert sanitized["credentials"]["auth_header"] == f"Bearer {REDACTED_TOKEN}"
