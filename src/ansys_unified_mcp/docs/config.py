"""Documentation retrieval configuration: paths and the curated doc set.

Taxonomy (normalized, see ARCHITECTURE.md / contexts/context.md):

- product  : which ANSYS product the doc belongs to. One of PRODUCTS.
- category : the doc's nature. One of CATEGORIES.
    - api_reference : object/keyword reference (the "API surface")
    - api_scripting : scripting guides (how to drive the product via script)
    - guide         : user / analysis / methods guides (prose, few commands)
    - tutorial      : step-by-step tutorials and example problems
- style    : which cleaning ruleset docs/clean.py applies
    - "ansys" : ANSYS/Synopsys boilerplate (default)
    - "lstc"  : LS-PrePost / LSTC revision-table style

Routing: search defaults to PRIMARY_CATEGORIES (the crisp API docs) so API
lookups stay precise; guide/tutorial docs are kept indexed but only searched
when the scope is widened (see docs/index.py search()).
"""

from __future__ import annotations

from pathlib import Path

# Repo root = parents[3]: docs/ -> ansys_unified_mcp/ -> src/ -> repo
REPO_ROOT = Path(__file__).resolve().parents[3]

SOURCE_DIR = REPO_ROOT / "Documentation_md"
CLEAN_DIR = REPO_ROOT / "Documentation_clean"
INDEX_PATH = CLEAN_DIR / "docs_index.sqlite"

# Chunking (characters). Windows kept small enough to be digestible in a single
# search result, with light overlap so context is not lost at boundaries.
CHUNK_SIZE = 1400
CHUNK_OVERLAP = 180

# Recognized products. `workbench` is registered for completeness but currently
# has no source document in Documentation_md (nothing to index yet).
PRODUCTS = ("mechanical", "lsdyna", "ls-prepost", "optislang", "spaceclaim", "workbench")

# Recognized categories.
CATEGORIES = ("api_reference", "api_scripting", "guide", "tutorial")

# Categories that the default (narrow) search targets: the crisp API docs.
PRIMARY_CATEGORIES = ("api_reference", "api_scripting")

# Curated set. Every real doc in Documentation_md is indexed so it is
# searchable, but `category` lets search route API lookups away from prose.
# Excluded: LS-DYNA_Keyword_and_Theory_Manuals (source is a 4 KB cover-page
# stub, no real keyword content to index).
API_DOCS: list[dict] = [
    # --- Mechanical -------------------------------------------------------
    {"name": "Ansys_Scripting_in_Mechanical_Guide", "title": "Scripting in Mechanical Guide", "category": "api_scripting", "product": "mechanical", "style": "ansys"},
    {"name": "Mechanical_Object_Reference", "title": "Mechanical Object Reference", "category": "api_reference", "product": "mechanical", "style": "ansys"},
    {"name": "Ansys_Mechanical_Users_Guide", "title": "Ansys Mechanical User's Guide", "category": "guide", "product": "mechanical", "style": "ansys"},
    {"name": "ANSYS_Mechanical_Tutorials_2026_R1", "title": "Ansys Mechanical Tutorials 2026 R1", "category": "tutorial", "product": "mechanical", "style": "ansys"},
    {"name": "Ansys_Explicit_Dynamics_Analysis_Guide", "title": "Ansys Explicit Dynamics Analysis Guide", "category": "guide", "product": "mechanical", "style": "ansys"},
    {"name": "Mechanical_Acoustic_Analysis_Guide", "title": "Mechanical Acoustic Analysis Guide", "category": "guide", "product": "mechanical", "style": "ansys"},
    {"name": "Mechanical_Add-ons_Guide", "title": "Mechanical Add-ons Guide", "category": "guide", "product": "mechanical", "style": "ansys"},
    {"name": "Mechanical_Beta_Features", "title": "Mechanical Beta Features", "category": "guide", "product": "mechanical", "style": "ansys"},
    {"name": "Mechanical_Technology_Showcase_Example_Problems", "title": "Mechanical Technology Showcase Example Problems", "category": "tutorial", "product": "mechanical", "style": "ansys"},
    # --- LS-DYNA ----------------------------------------------------------
    {"name": "LS-DYNA_Users_Guide", "title": "LS-DYNA User's Guide", "category": "guide", "product": "lsdyna", "style": "ansys"},
    {"name": "LS-DYNA_Implicit_Analysis_Guide", "title": "LS-DYNA Implicit Analysis Guide", "category": "guide", "product": "lsdyna", "style": "ansys"},
    {"name": "LS-DYNA_Beta_Features", "title": "LS-DYNA Beta Features", "category": "guide", "product": "lsdyna", "style": "ansys"},
    {"name": "LS-Run_Users_Guide", "title": "LS-Run User's Guide", "category": "guide", "product": "lsdyna", "style": "ansys"},
    {"name": "Envyo_Users_Guide", "title": "Envyo User's Guide", "category": "guide", "product": "lsdyna", "style": "ansys"},
    {"name": "Explicit_Dynamics_Autodyn_to_LS-DYNA_Migration_Guide", "title": "Autodyn to LS-DYNA Migration Guide", "category": "guide", "product": "lsdyna", "style": "ansys"},
    # --- LS-PrePost -------------------------------------------------------
    {"name": "lsppscripting", "title": "LS-PrePost Scripting (Command Language & Python)", "category": "api_scripting", "product": "ls-prepost", "style": "lstc"},
    {"name": "Ansys_LS-PrePost_Users_Guide", "title": "Ansys LS-PrePost User's Guide", "category": "guide", "product": "ls-prepost", "style": "ansys"},
    {"name": "LS-DYNA_LS-PrePost_Tutorials", "title": "LS-DYNA LS-PrePost Tutorials", "category": "tutorial", "product": "ls-prepost", "style": "ansys"},
    # --- optiSLang --------------------------------------------------------
    {"name": "optiSLang_Customization_API_and_Remote_Control", "title": "optiSLang Customization, API, and Remote Control", "category": "api_reference", "product": "optislang", "style": "ansys"},
    {"name": "optiSLang_Users_Guide", "title": "optiSLang User's Guide", "category": "guide", "product": "optislang", "style": "ansys"},
    {"name": "optiSLang_Tutorials", "title": "optiSLang Tutorials", "category": "tutorial", "product": "optislang", "style": "ansys"},
    {"name": "optiSLang_3D_Post-Processing_Tutorials", "title": "optiSLang 3D Post-Processing Tutorials", "category": "tutorial", "product": "optislang", "style": "ansys"},
    {"name": "optiSLang_Methods_for_Multi-Disciplinary_Optimization_and_Robustness_Analysis", "title": "optiSLang Methods for Multi-Disciplinary Optimization and Robustness Analysis", "category": "guide", "product": "optislang", "style": "ansys"},
    {"name": "Methods_for_Parametric_Design_Optimization", "title": "Methods for Parametric Design Optimization", "category": "guide", "product": "optislang", "style": "ansys"},
    {"name": "optiSLang_Installation_and_Licensing_Guide", "title": "optiSLang Installation and Licensing Guide", "category": "guide", "product": "optislang", "style": "ansys"},
    {"name": "optiSLang_Whats_New", "title": "optiSLang What's New", "category": "guide", "product": "optislang", "style": "ansys"},
    # --- SpaceClaim -------------------------------------------------------
    {"name": "SpaceClaim_Documentation", "title": "SpaceClaim Documentation", "category": "guide", "product": "spaceclaim", "style": "ansys"},
]


def doc_by_name(name: str) -> dict | None:
    for d in API_DOCS:
        if d["name"] == name:
            return d
    return None


def docs_in_categories(categories: tuple[str, ...]) -> list[str]:
    """Return the names of docs whose category is in `categories`."""
    return [d["name"] for d in API_DOCS if d["category"] in categories]


def primary_doc_names() -> list[str]:
    """Names of the crisp API docs (default search scope)."""
    return docs_in_categories(PRIMARY_CATEGORIES)
