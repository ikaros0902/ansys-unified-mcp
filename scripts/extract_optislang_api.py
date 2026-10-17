"""
ANSYS optiSLang API 萃取腳本 (Python 3.14 + inspect + pkgutil)
萃取 ansys.optislang.core 完整 Python API 及 v251 optiSLang scripting 內建演算法與節點定義。
"""
import os
import sys
import json
import inspect
import pkgutil
import importlib
from pathlib import Path

def extract_optislang():
    import ansys.optislang.core as osl_root

    api_data = {
        "module": "ansys.optislang.core",
        "version": getattr(osl_root, "__version__", "1.6.1"),
        "modules": {},
        "built_in_scripting_categories": {},
        "statistics": {
            "total_modules": 0,
            "total_classes": 0,
            "total_methods": 0,
            "total_functions": 0
        }
    }

    # 1. 萃取 ansys.optislang.core 所有模組
    visited_modules = set()

    def walk_and_extract(package):
        prefix = package.__name__ + "."
        for _, modname, ispkg in pkgutil.walk_packages(package.__path__, prefix):
            if modname in visited_modules:
                continue
            visited_modules.add(modname)
            try:
                mod = importlib.import_module(modname)
            except Exception as e:
                # print(f"略過或載入失敗 {modname}: {e}")
                continue

            api_data["statistics"]["total_modules"] += 1
            mod_doc = inspect.getdoc(mod) or ""
            classes_dict = {}
            funcs_list = []

            for attr_name, obj in inspect.getmembers(mod):
                if attr_name.startswith("_"):
                    continue

                if inspect.isclass(obj) and obj.__module__.startswith("ansys.optislang"):
                    api_data["statistics"]["total_classes"] += 1
                    cls_doc = inspect.getdoc(obj) or ""
                    methods_list = []
                    props_list = []

                    for m_name, m_obj in inspect.getmembers(obj):
                        if m_name.startswith("_") and m_name not in ("__init__", "__call__"):
                            continue
                        if inspect.isfunction(m_obj) or inspect.ismethod(m_obj):
                            try:
                                sig = str(inspect.signature(m_obj))
                            except Exception:
                                sig = "()"
                            m_doc = inspect.getdoc(m_obj) or ""
                            methods_list.append({
                                "name": m_name,
                                "signature": sig,
                                "doc": m_doc.strip()
                            })
                            api_data["statistics"]["total_methods"] += 1
                        elif isinstance(m_obj, property):
                            p_doc = inspect.getdoc(m_obj) or ""
                            props_list.append({
                                "name": m_name,
                                "doc": p_doc.strip()
                            })

                    classes_dict[attr_name] = {
                        "name": attr_name,
                        "doc": cls_doc.strip(),
                        "methods": methods_list,
                        "properties": props_list
                    }

                elif inspect.isfunction(obj) and obj.__module__.startswith("ansys.optislang"):
                    try:
                        sig = str(inspect.signature(obj))
                    except Exception:
                        sig = "()"
                    f_doc = inspect.getdoc(obj) or ""
                    funcs_list.append({
                        "name": attr_name,
                        "signature": sig,
                        "doc": f_doc.strip()
                    })
                    api_data["statistics"]["total_functions"] += 1

            if classes_dict or funcs_list:
                api_data["modules"][modname] = {
                    "doc": mod_doc.strip(),
                    "classes": classes_dict,
                    "functions": funcs_list
                }

    walk_and_extract(osl_root)

    # 2. 掃描 v251 optiSLang scripting 目錄
    osl_scripting_dir = Path(r"C:\Program Files\ANSYS Inc\v251\optiSLang\scripting")
    if osl_scripting_dir.exists():
        for category_dir in osl_scripting_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith("."):
                items = []
                for f in category_dir.iterdir():
                    if f.suffix in (".py", ".pye", ".cfg", ".html"):
                        items.append({
                            "name": f.stem,
                            "type": f.suffix,
                            "filename": f.name
                        })
                api_data["built_in_scripting_categories"][category_dir.name] = {
                    "path": str(category_dir),
                    "items_count": len(items),
                    "items": items
                }

    out_path = Path(__file__).resolve().parent.parent / "docs" / "api_inventory" / "optislang_api.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(api_data, f, ensure_ascii=False, indent=2)

    print(f"optiSLang API 抽取完成！存入: {out_path}")
    print(f"統計: Modules={api_data['statistics']['total_modules']}, Classes={api_data['statistics']['total_classes']}, Methods={api_data['statistics']['total_methods']}, Functions={api_data['statistics']['total_functions']}")
    return api_data

if __name__ == "__main__":
    extract_optislang()
