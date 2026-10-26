"""Stage 0 Physical Model Data Sanitization and Secret Redaction Gate.

This module implements deterministic sanitization and secret redaction for:
1. CAE Material Models: Redacts proprietary alloy constants (Granta), Johnson-Cook
   plasticity parameters (A, B, n, C, m), Cowper-Symonds strain rate constants,
   and unpublished stress-strain curves/tables, while preserving linear elastic
   properties (Young's modulus, Poisson's ratio, density).
2. Optical Parameters: Redacts Zemax higher-order aspheric polynomial coefficients
   (4th order and above: a4, a6, a8, ...), replacing them with redaction markers.
3. BOM and Metadata: Redacts PCB vendor-specific part numbers, defense/military
   project codenames, high-precision GPS coordinates, and internal part numbers,
   replacing them with consistent generic identifiers (COMP_001, ZONE_A, PROJ_GENERIC_001).
4. System & Execution Secrets: Filters FlexNet license server endpoints (port@host),
   internal Windows user paths (C:\\Users\\<username>), and API tokens/keys.
5. Evidence Payloads: Recursively sanitizes structured simulation evidence dictionaries
   prior to persistence or MCP transport.
"""

from __future__ import annotations

import copy
import json
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Redaction Marker Constants
REDACTED_PROPRIETARY_ALLOY: str = "<REDACTED_PROPRIETARY_ALLOY_COEFFICIENTS>"
REDACTED_ASPHERIC_COEFF: str = "<REDACTED_ASPHERIC_COEFF>"
REDACTED_LICENSE_SERVER: str = "<REDACTED_LICENSE_SERVER>"
REDACTED_USER: str = "<REDACTED_USER>"
REDACTED_API_KEY: str = "<REDACTED_API_KEY>"
REDACTED_SECRET: str = "<REDACTED_SECRET>"
REDACTED_TOKEN: str = "<REDACTED_TOKEN>"
REDACTED_GEO: str = "<REDACTED_GEO_COORDINATES>"

GENERIC_COMP_PREFIX: str = "COMP_"
GENERIC_ZONE_PREFIX: str = "ZONE_"
GENERIC_PROJ_PREFIX: str = "PROJ_GENERIC_"

# Allowed Standard Linear Elastic & Metadata Keys (Case-insensitive matching)
_ALLOWED_LINEAR_KEYS: Set[str] = {
    # Modulus of Elasticity
    "youngs_modulus", "elastic_modulus", "young_modulus", "modulus_of_elasticity",
    "ex", "ey", "ez", "e",
    # Poisson's Ratio
    "poissons_ratio", "poisson_ratio", "prxy", "pryz", "prxz", "nuxy", "nu",
    # Shear Modulus
    "shear_modulus", "gxy", "gyz", "gxz", "g",
    # Density
    "density", "dens", "rho",
    # Linear Thermal Expansion
    "secant_cte", "instantaneous_cte", "cte", "thermal_expansion", "alpx", "alpy", "alpz",
    # Thermal Conductivity
    "thermal_conductivity", "kxx", "kyy", "kzz", "k",
    # Specific Heat
    "specific_heat", "cp", "c_p",
    # General descriptive metadata
    "name", "id", "material_name", "material_type", "type", "unit", "units",
    "unit_system", "category", "display_name", "status", "description",
}

# Proprietary Material Keywords Requiring Redaction
_PROPRIETARY_MATERIAL_KEYS: Set[str] = {
    # Johnson-Cook Model
    "johnson_cook", "jc", "jc_parameters", "jc_model", "johnson_cook_plasticity",
    "jc_a", "jc_b", "jc_n", "jc_c", "jc_m",
    "jc_t_melt", "jc_t_room", "jc_eps0", "jc_t_ref",
    "t_melt", "t_room", "t_ref", "eps0", "epso",
    # Johnson-Cook single-letter parameters (when in material context)
    "a", "b", "n", "c", "m",
    # Cowper-Symonds Strain Rate Model
    "cowper_symonds", "cs", "cs_parameters", "cowper_symonds_c", "cowper_symonds_p",
    "cs_c", "cs_p", "src", "srp", "p",
    # Tabular Stress-Strain & Plasticity Hardening Curves
    "stress_strain", "stress_strain_curve", "stress_strain_table", "stress_strain_data",
    "plastic_strain", "true_stress", "true_strain", "engineering_stress", "engineering_strain",
    "effective_stress", "effective_plastic_strain", "yield_stress_table",
    "hardening_table", "miso_table", "biso_table", "kinematic_hardening",
    "multilinear_isotropic_hardening", "bilinear_isotropic_hardening",
    "sn_curve", "wohler_curve", "fatigue_data", "creep_data", "plasticity",
    # Granta Design / MI References
    "granta", "granta_id", "granta_mi_id", "record_id", "proprietary_alloys",
    "producer_data", "supplier_data", "patent_ref", "proprietary_coefficients",
}

# Optical Higher-Order Aspheric Keys (4th Order and Above)
_HIGHER_ORDER_OPTICAL_KEYS: Set[str] = {
    "a4", "a6", "a8", "a10", "a12", "a14", "a16", "a18", "a20",
    "a_4", "a_6", "a_8", "a_10", "a_12", "a_14", "a_16", "a_18", "a_20",
    "alpha_2", "alpha_3", "alpha_4", "alpha_5", "alpha_6",
    "c4", "c6", "c8", "c10", "c12",
    "coeff_4", "coeff_6", "coeff_8", "coeff_10",
}

# Regex Patterns for String Redaction
_RE_GRANTA: re.Pattern = re.compile(
    r"(?i)\bGranta(?:\s+(?:MI|Design))?(?:[-_\sA-Za-z0-9]+)?",
    re.IGNORECASE,
)

_RE_JC_TEXT: re.Pattern = re.compile(
    r"(?i)\b(?:Johnson[-_ ]Cook|JC)\b[^\n\r]*",
    re.IGNORECASE,
)

_RE_CS_TEXT: re.Pattern = re.compile(
    r"(?i)\b(?:Cowper[-_ ]Symonds|CS)\b[^\n\r]*",
    re.IGNORECASE,
)

_RE_DYNA_MAT_15: re.Pattern = re.compile(
    r"(\*MAT_(?:JOHNSON_COOK|015)[\s\S]*?)(?=\n\*[A-Z]|\Z)",
    re.IGNORECASE,
)

_RE_APDL_MISO: re.Pattern = re.compile(
    r"(?i)(TB,(?:MISO|PLAS|BISO|KINH)[^\n\r]*[\r\n]+(?:(?:TB[A-Z0-9]+|\s*!)[^\n\r]*[\r\n]*)+)",
    re.IGNORECASE,
)

_RE_ZEMAX_PARM_HIGH: re.Pattern = re.compile(
    r"(?i)^(\s*PARM\s+([2-9]|\d{2,})\s+)[^\r\n]+",
    re.MULTILINE,
)

_RE_ASPHERIC_COEFF_TXT: re.Pattern = re.compile(
    r"(?i)\b(a_?0*[468]|a_?1[0-9]|alpha_0*[2-9]|c_?0*[468]|coeff_0*[468])\s*[:=]\s*[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?",
    re.IGNORECASE,
)

_RE_FLEXNET_PORT_HOST: re.Pattern = re.compile(
    r"\b(\d{4,5})@([a-zA-Z0-9.\-_]+)\b"
)

_RE_FLEXNET_IP_PORT: re.Pattern = re.compile(
    r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}):(?:1055|2325|2700[0-9])\b"
)

_RE_FLEXNET_ENV: re.Pattern = re.compile(
    r"(?i)\b(ANSYSLMD_LICENSE_FILE|LM_LICENSE_FILE)\s*=\s*['\"]?[^'\";\r\n]+['\"]?"
)

_RE_WIN_USER_PATH: re.Pattern = re.compile(
    r"(?i)\b([a-zA-Z]:[\\/]+Users[\\/]+)([^\\/\s:;\"\'\<\>]+)"
)

_RE_UNC_USER_PATH: re.Pattern = re.compile(
    r"(?i)(\\\\Users\\\\)([^\\/\s:;\"\'\<\>]+)"
)

_RE_API_KEY_GOOGLE: re.Pattern = re.compile(r"\bAIza[0-9A-Za-z\-_]{30,40}\b")
_RE_API_KEY_OPENAI: re.Pattern = re.compile(r"\bsk-(?:proj-)?[a-zA-Z0-9_\-]{20,}\b")
_RE_API_KEY_ANTHROPIC: re.Pattern = re.compile(r"\bsk-ant-[a-zA-Z0-9_\-]{20,}\b")
_RE_BEARER_TOKEN: re.Pattern = re.compile(r"\bBearer\s+[a-zA-Z0-9\-._~+/]+=*\b")
_RE_GENERIC_SECRET: re.Pattern = re.compile(
    r"(?i)\b(password|passwd|pwd|api[-_]?key|secret|access[-_]?token)\s*[:=]\s*['\"]?([^\s\"';&]{6,})['\"]?"
)

_RE_GPS_COORDS: re.Pattern = re.compile(
    r"\b[-+]?([0-8]?\d\.\d{3,}|90\.0{3,})\s*,\s*[-+]?(1[0-7]\d\.\d{3,}|180\.0{3,}|[0-9]?\d\.\d{3,})\b"
)

_RE_PCB_PART_NUMBER: re.Pattern = re.compile(
    r"\b(?:\d{3}-\d{5}(?:-[A-Za-z0-9]+)?|(?:IPN|MPN|PN)[-:#\s]+[A-Za-z0-9\-_]{4,}|(?:TPS\d{5}|STM32[A-Z0-9]+|MAX\d{3,4}|XC[0-9A-Z]{4,})[A-Za-z0-9\-]*)\b",
    re.IGNORECASE,
)

_RE_PROJECT_CODENAME: re.Pattern = re.compile(
    r"\b(?:Project\s+([A-Za-z0-9_\-]+)|ITAR\b|DARPA\b|NAVSEA\b|AFRL\b|USAF\b|Skunkworks\b|Blackhawk\b|Aegis\b)",
    re.IGNORECASE,
)


class DataSanitizer:
    """Stage 0 Physical Model Data Sanitization and Secret Redaction Engine.

    Guarantees that sensitive constitutive model equations, proprietary alloy databases,
    high-order optical prescription polynomials, BOM tracking IDs, and infrastructure
    credentials are scrubbed prior to persistence or egress.
    """

    def __init__(self) -> None:
        """Initialize the DataSanitizer with session-isolated identifier mapping tables."""
        self._pn_map: Dict[str, str] = {}
        self._pn_counter: int = 1

        self._zone_map: Dict[str, str] = {}
        self._zone_counter: int = 1

        self._proj_map: Dict[str, str] = {}
        self._proj_counter: int = 1

    def reset_mappings(self) -> None:
        """Reset the internal anonymization identifier mappings."""
        self._pn_map.clear()
        self._pn_counter = 1
        self._zone_map.clear()
        self._zone_counter = 1
        self._proj_map.clear()
        self._proj_counter = 1

    def _get_generic_comp_id(self, raw_pn: str) -> str:
        """Return a deterministic generic component ID for a given part number."""
        clean = raw_pn.strip()
        if clean not in self._pn_map:
            self._pn_map[clean] = f"{GENERIC_COMP_PREFIX}{self._pn_counter:03d}"
            self._pn_counter += 1
        return self._pn_map[clean]

    def _get_generic_zone_id(self, raw_zone: str) -> str:
        """Return a deterministic generic zone ID for a given coordinate or location."""
        clean = raw_zone.strip()
        if clean not in self._zone_map:
            letter = chr(ord('A') + (self._zone_counter - 1) % 26)
            suffix = f"_{self._zone_counter // 26}" if self._zone_counter > 26 else ""
            self._zone_map[clean] = f"{GENERIC_ZONE_PREFIX}{letter}{suffix}"
            self._zone_counter += 1
        return self._zone_map[clean]

    def _get_generic_proj_id(self, raw_proj: str) -> str:
        """Return a deterministic generic project ID for a given codename."""
        clean = raw_proj.strip()
        if clean.lower().startswith("project "):
            clean = clean[8:].strip()
        if clean not in self._proj_map:
            self._proj_map[clean] = f"{GENERIC_PROJ_PREFIX}{self._proj_counter:03d}"
            self._proj_counter += 1
        return self._proj_map[clean]

    def sanitize_material_properties(
        self, properties: Union[Dict[str, Any], str]
    ) -> Union[Dict[str, Any], str]:
        """Detect and redact proprietary alloy constants and nonlinear plasticity parameters.

        Redacts Granta proprietary constants, Johnson-Cook parameters (A, B, n, C, m),
        Cowper-Symonds parameters, and stress-strain tables.
        Retains standard linear elastic constants (Young's modulus, Poisson's ratio, etc.).

        Args:
            properties: Material property dictionary or raw string (APDL, LS-DYNA, or JSON).

        Returns:
            Sanitized material property dictionary or string.
        """
        if isinstance(properties, dict):
            return self._sanitize_material_dict(properties)
        elif isinstance(properties, str):
            return self._sanitize_material_str(properties)
        return properties

    def _sanitize_material_dict(self, mat_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize a material property dictionary."""
        sanitized: Dict[str, Any] = {}

        for k, v in mat_dict.items():
            k_lower = str(k).strip().lower()

            # 1. Check if the key is explicitly recognized as proprietary
            if k_lower in _PROPRIETARY_MATERIAL_KEYS:
                sanitized[k] = REDACTED_PROPRIETARY_ALLOY
                continue

            # 2. Check if key is a known allowed linear elastic / descriptive key
            if k_lower in _ALLOWED_LINEAR_KEYS:
                if isinstance(v, dict):
                    sanitized[k] = self._sanitize_material_dict(v)
                elif isinstance(v, list):
                    # Lists under linear properties (e.g. isotropic temperature tables)
                    sanitized[k] = [
                        self._sanitize_material_dict(elem) if isinstance(elem, dict) else elem
                        for elem in v
                    ]
                elif isinstance(v, str):
                    sanitized[k] = self.sanitize_text(v)
                else:
                    sanitized[k] = v
                continue

            # 3. Check for nested dictionaries or sub-models
            if isinstance(v, dict):
                # If key looks like plasticity or constitutive model, scrub or recurse
                if any(tag in k_lower for tag in ("plastic", "yield", "harden", "jc", "cs", "granta")):
                    sanitized[k] = REDACTED_PROPRIETARY_ALLOY
                else:
                    sanitized[k] = self._sanitize_material_dict(v)
            elif isinstance(v, list):
                # Tabular data not explicitly whitelisted as linear is treated as proprietary
                if any(tag in k_lower for tag in ("curve", "table", "data", "point", "stress", "strain")):
                    sanitized[k] = REDACTED_PROPRIETARY_ALLOY
                else:
                    sanitized[k] = [
                        self._sanitize_material_dict(elem) if isinstance(elem, dict) else elem
                        for elem in v
                    ]
            elif isinstance(v, str):
                # String properties (may contain proprietary alloy descriptions)
                sanitized[k] = self._sanitize_material_str(v)
            else:
                # If numeric or other scalar, check if key is single letter JC or CS
                if k_lower in {"a", "b", "n", "c", "m", "p"}:
                    sanitized[k] = REDACTED_PROPRIETARY_ALLOY
                else:
                    sanitized[k] = v

        return sanitized

    def _sanitize_material_str(self, text: str) -> str:
        """Sanitize material representations in raw text format."""
        # Attempt JSON decoding first
        trimmed = text.strip()
        if (trimmed.startswith("{") and trimmed.endswith("}")) or (trimmed.startswith("[") and trimmed.endswith("]")):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    sanitized_dict = self._sanitize_material_dict(parsed)
                    return json.dumps(sanitized_dict, indent=2)
            except Exception:
                pass

        out = text
        # Redact LS-DYNA *MAT_JOHNSON_COOK keyword blocks
        out = _RE_DYNA_MAT_15.sub(f"*MAT_JOHNSON_COOK\n{REDACTED_PROPRIETARY_ALLOY}\n", out)
        # Redact APDL MISO / PLAS tables
        out = _RE_APDL_MISO.sub(f"! {REDACTED_PROPRIETARY_ALLOY}\n", out)
        # Redact Granta references
        out = _RE_GRANTA.sub(REDACTED_PROPRIETARY_ALLOY, out)
        # Redact text lines specifying Johnson-Cook parameters
        out = _RE_JC_TEXT.sub(f"Johnson-Cook: {REDACTED_PROPRIETARY_ALLOY}", out)
        # Redact text lines specifying Cowper-Symonds parameters
        out = _RE_CS_TEXT.sub(f"Cowper-Symonds: {REDACTED_PROPRIETARY_ALLOY}", out)
        # Apply standard system & secret filters
        out = self.sanitize_text(out)
        return out

    def sanitize_optical_parameters(
        self, optical_data: Union[Dict[str, Any], str]
    ) -> Union[Dict[str, Any], str]:
        """Detect and redact Zemax higher-order aspheric polynomial coefficients (>= 4th order).

        Replaces coefficients (a4, a6, a8, alpha_2, ...) with REDACTED_ASPHERIC_COEFF.
        Preserves base quadric parameters (Curvature/Radius, Conic constant k).

        Args:
            optical_data: Optical prescription dictionary or raw string (Zemax ZMX format or JSON).

        Returns:
            Sanitized optical prescription dictionary or string.
        """
        if isinstance(optical_data, dict):
            return self._sanitize_optical_dict(optical_data)
        elif isinstance(optical_data, str):
            return self._sanitize_optical_str(optical_data)
        return optical_data

    def _sanitize_optical_dict(self, opt_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize an optical parameter dictionary."""
        sanitized: Dict[str, Any] = {}

        for k, v in opt_dict.items():
            k_lower = str(k).strip().lower()

            # Higher-order aspheric coefficient key match
            if k_lower in _HIGHER_ORDER_OPTICAL_KEYS:
                if isinstance(v, list):
                    # Redact 4th order and above in coefficient list
                    sanitized[k] = [REDACTED_ASPHERIC_COEFF for _ in v]
                else:
                    sanitized[k] = REDACTED_ASPHERIC_COEFF
                continue

            # Check for generic coefficient lists like aspheric_coefficients = [a2, a4, a6, a8]
            if any(tag in k_lower for tag in ("aspheric_coeff", "aspheric_coef", "poly_coeff", "higher_order")) and isinstance(v, list):
                sanitized_list = []
                for idx, item in enumerate(v):
                    # Keep 2nd order (index 0 if [a2, a4, ...]), redact index >= 1 (4th order+)
                    if idx >= 1:
                        sanitized_list.append(REDACTED_ASPHERIC_COEFF)
                    else:
                        sanitized_list.append(item)
                sanitized[k] = sanitized_list
                continue

            if isinstance(v, dict):
                sanitized[k] = self._sanitize_optical_dict(v)
            elif isinstance(v, list):
                sanitized[k] = [
                    self._sanitize_optical_dict(item) if isinstance(item, dict) else item
                    for item in v
                ]
            elif isinstance(v, str):
                sanitized[k] = self._sanitize_optical_str(v)
            else:
                sanitized[k] = v

        return sanitized

    def _sanitize_optical_str(self, text: str) -> str:
        """Sanitize optical prescription data in raw text format."""
        trimmed = text.strip()
        if (trimmed.startswith("{") and trimmed.endswith("}")) or (trimmed.startswith("[") and trimmed.endswith("]")):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    sanitized_dict = self._sanitize_optical_dict(parsed)
                    return json.dumps(sanitized_dict, indent=2)
            except Exception:
                pass

        out = text
        # Redact Zemax PARM lines for 4th order and above (PARM 2, PARM 3, ...)
        out = _RE_ZEMAX_PARM_HIGH.sub(rf"\g<1>{REDACTED_ASPHERIC_COEFF}", out)
        # Redact generic aspheric coefficient key-values (a4 = ..., a6 = ...)
        out = _RE_ASPHERIC_COEFF_TXT.sub(rf"\1: {REDACTED_ASPHERIC_COEFF}", out)
        # Standard secret filters
        out = self.sanitize_text(out)
        return out

    def sanitize_bom_and_metadata(
        self, bom_data: Union[Dict[str, Any], List[Any], str]
    ) -> Union[Dict[str, Any], List[Any], str]:
        """Redact vendor part numbers, defense project codenames, and precision GPS coords.

        Replaces sensitive identifiers with deterministic generic IDs (COMP_001, ZONE_A, PROJ_GENERIC_001).

        Args:
            bom_data: BOM dictionary, list of component records, or raw text.

        Returns:
            Sanitized BOM data structure or string.
        """
        if isinstance(bom_data, dict):
            return self._sanitize_bom_dict(bom_data)
        elif isinstance(bom_data, list):
            return [self.sanitize_bom_and_metadata(item) for item in bom_data]
        elif isinstance(bom_data, str):
            return self._sanitize_bom_str(bom_data)
        return bom_data

    def _sanitize_bom_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize a BOM dictionary."""
        sanitized: Dict[str, Any] = {}

        for k, v in data.items():
            k_lower = str(k).strip().lower()

            # 1. Part numbers
            if any(tag in k_lower for tag in ("part_number", "vendor_pn", "mpn", "internal_pn", "ipn", "sku", "catalog_no")):
                if isinstance(v, str):
                    sanitized[k] = self._get_generic_comp_id(v)
                else:
                    sanitized[k] = self._get_generic_comp_id(str(v))
                continue

            # 2. Defense and military project codenames
            if any(tag in k_lower for tag in ("project", "codename", "defense_tag", "classification")):
                if isinstance(v, str):
                    sanitized[k] = self._get_generic_proj_id(v)
                else:
                    sanitized[k] = self._get_generic_proj_id(str(v))
                continue

            # 3. High precision geographic coordinates
            if any(tag in k_lower for tag in ("coordinates", "gps", "geo_location", "latitude", "longitude", "position_geo")):
                if isinstance(v, (int, float)):
                    # Lat/Lon float with precision > 2 decimals
                    sanitized[k] = self._get_generic_zone_id(str(v))
                elif isinstance(v, str):
                    sanitized[k] = self._get_generic_zone_id(v)
                elif isinstance(v, (list, tuple)):
                    sanitized[k] = self._get_generic_zone_id(str(v))
                else:
                    sanitized[k] = self._get_generic_zone_id(str(v))
                continue

            # 4. Recursion on nested structures
            if isinstance(v, dict):
                sanitized[k] = self._sanitize_bom_dict(v)
            elif isinstance(v, list):
                sanitized[k] = [
                    self._sanitize_bom_dict(elem) if isinstance(elem, dict)
                    else (self.sanitize_bom_and_metadata(elem) if isinstance(elem, (list, str)) else elem)
                    for elem in v
                ]
            elif isinstance(v, str):
                sanitized[k] = self._sanitize_bom_str(v)
            else:
                sanitized[k] = v

        return sanitized

    def _sanitize_bom_str(self, text: str) -> str:
        """Sanitize BOM and metadata fields inside text."""
        # Attempt JSON decoding first
        trimmed = text.strip()
        if (trimmed.startswith("{") and trimmed.endswith("}")) or (trimmed.startswith("[") and trimmed.endswith("]")):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, (dict, list)):
                    sanitized_obj = self.sanitize_bom_and_metadata(parsed)
                    return json.dumps(sanitized_obj, indent=2)
            except Exception:
                pass

        out = text
        # Anonymize GPS coordinates
        def replace_gps(m: re.Match[str]) -> str:
            return self._get_generic_zone_id(m.group(0))

        out = _RE_GPS_COORDS.sub(replace_gps, out)

        # Anonymize Project codenames
        def replace_proj(m: re.Match[str]) -> str:
            val = m.group(1) if m.group(1) else m.group(0)
            return f"Project {self._get_generic_proj_id(val)}"

        out = _RE_PROJECT_CODENAME.sub(replace_proj, out)

        # Anonymize PCB Part Numbers
        def replace_pn(m: re.Match[str]) -> str:
            return self._get_generic_comp_id(m.group(0))

        out = _RE_PCB_PART_NUMBER.sub(replace_pn, out)

        # Standard secret filters
        out = self.sanitize_text(out)
        return out

    def sanitize_text(self, text: str) -> str:
        """Comprehensive regex filter for credentials, license servers, and internal paths.

        Filters:
        - FlexNet License Server IP and Port combinations (e.g. 1055@lic.corp.com)
        - Internal Windows username paths (e.g. C:\\Users\\jdoe\\...)
        - API Keys (Google, OpenAI, Anthropic, Bearer tokens, secrets)

        Args:
            text: Arbitrary input text or log string.

        Returns:
            Sanitized text with credentials and paths redacted.
        """
        if not isinstance(text, str):
            return text

        out = text

        # 1. Redact FlexNet Port@Host endpoints
        out = _RE_FLEXNET_PORT_HOST.sub(REDACTED_LICENSE_SERVER, out)
        out = _RE_FLEXNET_IP_PORT.sub(REDACTED_LICENSE_SERVER, out)
        out = _RE_FLEXNET_ENV.sub(rf"\1={REDACTED_LICENSE_SERVER}", out)

        # 2. Redact Windows user paths (C:\Users\username\... -> C:\Users\<REDACTED_USER>\...)
        out = _RE_WIN_USER_PATH.sub(rf"\g<1>{REDACTED_USER}", out)
        out = _RE_UNC_USER_PATH.sub(rf"\g<1>{REDACTED_USER}", out)

        # 3. Redact API Keys and tokens
        out = _RE_API_KEY_GOOGLE.sub(REDACTED_API_KEY, out)
        out = _RE_API_KEY_OPENAI.sub(REDACTED_API_KEY, out)
        out = _RE_API_KEY_ANTHROPIC.sub(REDACTED_API_KEY, out)
        out = _RE_BEARER_TOKEN.sub(f"Bearer {REDACTED_TOKEN}", out)

        # 4. Redact Generic Secrets / Passwords in key-value format
        out = _RE_GENERIC_SECRET.sub(rf"\1={REDACTED_SECRET}", out)

        return out

    def sanitize_evidence_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Deep recursive sanitization scanner for simulation results and evidence payloads.

        Scans nested dictionaries and lists before simulation artifacts, execution logs,
        or gatekeeper evidence manifests are persisted or returned across MCP tools.

        Args:
            payload: Arbitrary evidence payload dictionary.

        Returns:
            Sanitized deep-copy of the payload dictionary.
        """
        if not isinstance(payload, dict):
            return payload

        # Create a deep copy to guarantee input immutability
        copied_payload = copy.deepcopy(payload)
        return self._sanitize_evidence_node(copied_payload)

    def _sanitize_evidence_node(self, node: Any, parent_key: str = "") -> Any:
        """Internal recursive node scrubber for arbitrary evidence trees."""
        if isinstance(node, dict):
            sanitized_dict: Dict[str, Any] = {}
            for k, v in node.items():
                k_lower = str(k).strip().lower()

                # Dispatch based on domain semantics of the key
                # 1. BOM / Component List checks (check prior to 'material' to avoid matching 'bill_of_materials')
                if any(tag in k_lower for tag in ("bill_of_materials", "bill_of_material", "bom", "components", "parts_list", "part_list")):
                    sanitized_dict[k] = self.sanitize_bom_and_metadata(v)
                # 2. Optical parameters
                elif any(tag in k_lower for tag in ("optical", "aspheric", "zemax", "lens_prescription")):
                    sanitized_dict[k] = self.sanitize_optical_parameters(v)
                # 3. Material properties
                elif any(tag in k_lower for tag in ("material", "constitutive", "plasticity", "mat_prop")):
                    sanitized_dict[k] = self.sanitize_material_properties(v)
                # 4. License / credential / secret keys
                elif any(tag in k_lower for tag in ("license", "token", "secret", "password", "credential", "api_key", "apikey")):
                    if isinstance(v, dict):
                        sanitized_dict[k] = self._sanitize_evidence_node(v, parent_key=k_lower)
                    elif isinstance(v, list):
                        sanitized_dict[k] = [self._sanitize_evidence_node(elem, parent_key=k_lower) for elem in v]
                    elif isinstance(v, str):
                        sanitized_dict[k] = self.sanitize_text(v)
                    else:
                        sanitized_dict[k] = REDACTED_SECRET
                # 5. Direct BOM attribute keys (e.g. part_number, project_name, coordinates)
                elif any(tag in k_lower for tag in ("part_number", "vendor_pn", "mpn", "internal_pn", "ipn", "sku", "project", "codename", "coordinates", "gps")):
                    res = self._sanitize_bom_dict({k: v})
                    sanitized_dict[k] = res[k]
                # 6. Direct optical attribute keys
                elif k_lower in _HIGHER_ORDER_OPTICAL_KEYS:
                    res = self._sanitize_optical_dict({k: v})
                    sanitized_dict[k] = res[k]
                # 7. Direct material attribute keys
                elif k_lower in _PROPRIETARY_MATERIAL_KEYS:
                    res = self._sanitize_material_dict({k: v})
                    sanitized_dict[k] = res[k]
                else:
                    sanitized_dict[k] = self._sanitize_evidence_node(v, parent_key=k_lower)
            return sanitized_dict

        elif isinstance(node, list):
            return [self._sanitize_evidence_node(item, parent_key=parent_key) for item in node]

        elif isinstance(node, str):
            # Check if string has domain-specific triggers
            sanitized_str = self.sanitize_text(node)
            if any(term in sanitized_str for term in ("*MAT_", "Johnson-Cook", "Cowper-Symonds", "Granta")):
                sanitized_str = self._sanitize_material_str(sanitized_str)
            if any(term in sanitized_str for term in ("PARM", "a4", "a6", "a8")):
                sanitized_str = self._sanitize_optical_str(sanitized_str)
            if any(term in sanitized_str for term in ("Project ", "820-", "IPN-", "MPN:")):
                sanitized_str = self._sanitize_bom_str(sanitized_str)
            return sanitized_str

        return node


# Module-level default singleton instance
_DEFAULT_SANITIZER = DataSanitizer()


def sanitize_material_properties(
    properties: Union[Dict[str, Any], str]
) -> Union[Dict[str, Any], str]:
    """Module-level convenience wrapper for DataSanitizer.sanitize_material_properties."""
    return _DEFAULT_SANITIZER.sanitize_material_properties(properties)


def sanitize_optical_parameters(
    optical_data: Union[Dict[str, Any], str]
) -> Union[Dict[str, Any], str]:
    """Module-level convenience wrapper for DataSanitizer.sanitize_optical_parameters."""
    return _DEFAULT_SANITIZER.sanitize_optical_parameters(optical_data)


def sanitize_bom_and_metadata(
    bom_data: Union[Dict[str, Any], List[Any], str]
) -> Union[Dict[str, Any], List[Any], str]:
    """Module-level convenience wrapper for DataSanitizer.sanitize_bom_and_metadata."""
    return _DEFAULT_SANITIZER.sanitize_bom_and_metadata(bom_data)


def sanitize_text(text: str) -> str:
    """Module-level convenience wrapper for DataSanitizer.sanitize_text."""
    return _DEFAULT_SANITIZER.sanitize_text(text)


def sanitize_evidence_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Module-level convenience wrapper for DataSanitizer.sanitize_evidence_payload."""
    return _DEFAULT_SANITIZER.sanitize_evidence_payload(payload)


if __name__ == "__main__":
    # Self-test validation suite
    print("=== Running DataSanitizer Self-Test Suite ===")

    sanitizer = DataSanitizer()

    # 1. Test Material Properties Sanitization
    test_mat = {
        "name": "Ti-6Al-4V Proprietary",
        "youngs_modulus": 113.8e9,
        "poissons_ratio": 0.34,
        "density": 4430.0,
        "johnson_cook": {
            "A": 862e6,
            "B": 331e6,
            "n": 0.34,
            "C": 0.012,
            "m": 0.8,
        },
        "cowper_symonds": {
            "C": 40.0,
            "P": 5.0,
        },
        "stress_strain_curve": [
            [0.0, 862e6],
            [0.05, 950e6],
            [0.10, 1020e6],
        ],
        "granta_mi_id": "GRANTA-MIL-HDBK-5J-1029",
    }
    sanitized_mat = sanitizer.sanitize_material_properties(test_mat)
    assert sanitized_mat["youngs_modulus"] == 113.8e9, "Linear elastic modulus must be preserved"
    assert sanitized_mat["poissons_ratio"] == 0.34, "Poisson's ratio must be preserved"
    assert sanitized_mat["johnson_cook"] == REDACTED_PROPRIETARY_ALLOY, "JC params must be redacted"
    assert sanitized_mat["cowper_symonds"] == REDACTED_PROPRIETARY_ALLOY, "CS params must be redacted"
    assert sanitized_mat["stress_strain_curve"] == REDACTED_PROPRIETARY_ALLOY, "Tables must be redacted"
    assert sanitized_mat["granta_mi_id"] == REDACTED_PROPRIETARY_ALLOY, "Granta ID must be redacted"
    print("[PASS] Material Properties Sanitization (dict)")

    # 2. Test Optical Parameters Sanitization
    test_optical = {
        "surface_type": "EVENASPH",
        "radius": 25.4,
        "conic": -1.0,
        "a4": 1.25e-5,
        "a6": -3.45e-8,
        "a8": 6.78e-11,
    }
    sanitized_optical = sanitizer.sanitize_optical_parameters(test_optical)
    assert sanitized_optical["radius"] == 25.4, "Radius must be preserved"
    assert sanitized_optical["conic"] == -1.0, "Conic must be preserved"
    assert sanitized_optical["a4"] == REDACTED_ASPHERIC_COEFF, "a4 must be redacted"
    assert sanitized_optical["a6"] == REDACTED_ASPHERIC_COEFF, "a6 must be redacted"
    assert sanitized_optical["a8"] == REDACTED_ASPHERIC_COEFF, "a8 must be redacted"
    print("[PASS] Optical Parameters Sanitization (dict)")

    # 3. Test BOM & Metadata Sanitization
    test_bom = [
        {"part_number": "820-01234-A", "qty": 10, "coordinates": "24.789123, 120.998234"},
        {"part_number": "TPS54331-Q1", "qty": 5, "coordinates": "24.789123, 120.998234"},
        {"project_name": "Project Skunkworks", "classification": "ITAR"},
    ]
    sanitized_bom = sanitizer.sanitize_bom_and_metadata(test_bom)
    assert sanitized_bom[0]["part_number"] == "COMP_001", "Part number must be anonymized to COMP_001"
    assert sanitized_bom[1]["part_number"] == "COMP_002", "Second part number must be COMP_002"
    assert sanitized_bom[0]["coordinates"] == sanitized_bom[1]["coordinates"], "Same coords must map consistently"
    assert "ZONE_" in sanitized_bom[0]["coordinates"], "Coordinates must be anonymized to ZONE_*"
    assert sanitized_bom[2]["project_name"] == "PROJ_GENERIC_001", "Project codename must be anonymized"
    print("[PASS] BOM & Metadata Sanitization (list of dicts)")

    # 4. Test Text Sanitization (License, User Path, API Keys)
    raw_text = (
        "Connected to ANSYS License Server at 1055@lic-server.corp.local.\n"
        "Writing temporary mesh to C:\\Users\\johndoe\\AppData\\Local\\Temp\\mesh.msh.\n"
        "Exported log using token AIzaSyD-1234567890abcdef1234567890abc.\n"
        "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.t-ae.\n"
        "password=SecretPassword123!"
    )
    sanitized_text = sanitizer.sanitize_text(raw_text)
    assert REDACTED_LICENSE_SERVER in sanitized_text, "License server must be redacted"
    assert "1055@lic-server.corp.local" not in sanitized_text, "License server address must not appear"
    assert f"C:\\Users\\{REDACTED_USER}\\AppData" in sanitized_text, "Username must be redacted"
    assert "johndoe" not in sanitized_text, "Raw username must not appear"
    assert REDACTED_API_KEY in sanitized_text, "Google API key must be redacted"
    assert "AIzaSyD" not in sanitized_text, "Raw API key must not appear"
    assert REDACTED_TOKEN in sanitized_text, "Bearer token must be redacted"
    assert REDACTED_SECRET in sanitized_text, "Password must be redacted"
    print("[PASS] Text & Credentials Sanitization")

    # 5. Test Evidence Payload Deep Recursive Sanitization
    evidence = {
        "job_id": "SIM_2026_001",
        "license": "27000@192.168.1.50",
        "output_dir": "C:\\Users\\admin\\simulations\\run1",
        "material_properties": {
            "name": "Alloy-718",
            "youngs_modulus": 200e9,
            "poissons_ratio": 0.3,
            "jc_a": 900e6,
            "jc_b": 500e6,
            "jc_n": 0.25,
        },
        "optical_parameters": {
            "surface_type": "EVENASPH",
            "radius": 15.0,
            "a4": 3.14e-6,
            "a6": -2.71e-9,
        },
        "bill_of_materials": [
            {"part_number": "603-9988-01", "project_name": "Project Blackhawk"}
        ],
    }
    sanitized_payload = sanitizer.sanitize_evidence_payload(evidence)
    assert sanitized_payload["license"] == REDACTED_LICENSE_SERVER
    assert "admin" not in sanitized_payload["output_dir"]
    assert sanitized_payload["material_properties"]["youngs_modulus"] == 200e9
    assert sanitized_payload["material_properties"]["jc_a"] == REDACTED_PROPRIETARY_ALLOY
    assert sanitized_payload["optical_parameters"]["radius"] == 15.0
    assert sanitized_payload["optical_parameters"]["a4"] == REDACTED_ASPHERIC_COEFF
    assert "COMP_" in sanitized_payload["bill_of_materials"][0]["part_number"]
    assert "PROJ_" in sanitized_payload["bill_of_materials"][0]["project_name"]
    print("[PASS] Evidence Payload Deep Sanitization")

    print("\nAll self-test assertions passed successfully!")
