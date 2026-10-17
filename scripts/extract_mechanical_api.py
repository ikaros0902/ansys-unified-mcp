"""
ANSYS Mechanical API 萃取腳本 (Python AST 解析)
掃描 ansys-mechanical-stubs/v251 內所有模組，完整抽取 ACT DataModel Class、Method、Property 與 Type Hints。
"""
import ast
import importlib.util
import os
import site
import sys
import json
from pathlib import Path

def get_annotation_str(node):
    """將 AST 註解節點轉換為字串表達式"""
    if node is None:
        return "None"
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return f"{get_annotation_str(node.value)}.{node.attr}"
    elif isinstance(node, ast.Subscript):
        return f"{get_annotation_str(node.value)}[{get_annotation_str(node.slice)}]"
    elif isinstance(node, ast.Constant):
        return str(node.value)
    elif isinstance(node, ast.Tuple):
        return ", ".join(get_annotation_str(e) for e in node.elts)
    elif isinstance(node, ast.List):
        return f"[{', '.join(get_annotation_str(e) for e in node.elts)}]"
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return f"{get_annotation_str(node.left)} | {get_annotation_str(node.right)}"
    return ast.unparse(node) if hasattr(ast, "unparse") else "Any"


def resolve_stubs_root() -> Path:
    """
    動態解析 ansys-mechanical-stubs 安裝路徑，依序嘗試：
    1. 環境變數 ANSYS_MECHANICAL_STUBS_ROOT 顯式覆寫
    2. importlib 直接定位已安裝套件 ansys.mechanical.stubs
    3. site-packages / user site-packages 底下搜尋 ansys/mechanical/stubs/v<version>
    找不到則拋出清晰錯誤，不預設 fallback 到任何特定個人路徑。
    """
    env_override = os.environ.get("ANSYS_MECHANICAL_STUBS_ROOT")
    if env_override:
        override_path = Path(env_override)
        if override_path.exists():
            return override_path
        raise FileNotFoundError(
            f"環境變數 ANSYS_MECHANICAL_STUBS_ROOT 指定的路徑不存在: {override_path}"
        )

    spec = importlib.util.find_spec("ansys.mechanical.stubs")
    if spec is not None and spec.submodule_search_locations:
        for location in spec.submodule_search_locations:
            candidate = Path(location)
            if candidate.exists():
                version_dirs = sorted(
                    (d for d in candidate.iterdir() if d.is_dir() and d.name.startswith("v")),
                    reverse=True,
                )
                if version_dirs:
                    return version_dirs[0]

    site_dirs = []
    try:
        site_dirs.extend(site.getsitepackages())
    except AttributeError:
        pass
    try:
        site_dirs.append(site.getusersitepackages())
    except AttributeError:
        pass

    for site_dir in site_dirs:
        stubs_parent = Path(site_dir) / "ansys" / "mechanical" / "stubs"
        if stubs_parent.exists():
            version_dirs = sorted(
                (d for d in stubs_parent.iterdir() if d.is_dir() and d.name.startswith("v")),
                reverse=True,
            )
            if version_dirs:
                return version_dirs[0]

    raise FileNotFoundError(
        "找不到 ansys-mechanical-stubs 安裝路徑。請確認已執行 "
        "`pip install ansys-mechanical-stubs`，或透過環境變數 "
        "ANSYS_MECHANICAL_STUBS_ROOT 手動指定 stubs 根目錄。"
    )

def extract_mechanical():
    try:
        stubs_root = resolve_stubs_root()
    except FileNotFoundError as e:
        print(f"錯誤: {e}")
        return None

    api_data = {
        "module": "Ansys.Mechanical",
        "version": stubs_root.name,
        "source": "ansys-mechanical-stubs",
        "modules": {},
        "statistics": {
            "total_modules": 0,
            "total_classes": 0,
            "total_methods": 0,
            "total_properties": 0,
            "total_functions": 0
        }
    }

    py_files = list(stubs_root.rglob("*.py"))
    print(f"找到 {len(py_files)} 個 Python stub 檔案，開始解析...")

    for py_file in py_files:
        rel_path = py_file.relative_to(stubs_root)
        # 轉換為模組名稱
        parts = list(rel_path.parts)
        if parts[-1] == "__init__.py":
            parts.pop()
        else:
            parts[-1] = parts[-1].replace(".py", "")

        module_name = ".".join(parts)
        if not module_name:
            module_name = "Ansys.Mechanical"

        try:
            with open(py_file, "r", encoding="utf-8", errors="replace") as f:
                source = f.read()
            tree = ast.parse(source, filename=str(py_file))
        except Exception as e:
            print(f"解析 {py_file} 失敗: {e}")
            continue

        api_data["statistics"]["total_modules"] += 1
        module_doc = ast.get_docstring(tree) or ""
        module_classes = {}
        module_functions = []

        for item in tree.body:
            if isinstance(item, ast.ClassDef):
                api_data["statistics"]["total_classes"] += 1
                class_doc = ast.get_docstring(item) or ""
                cls_info = {
                    "name": item.name,
                    "doc": class_doc.strip(),
                    "methods": [],
                    "properties": []
                }

                # 遍歷 class 內部定義
                for member in item.body:
                    if isinstance(member, ast.FunctionDef):
                        member_doc = ast.get_docstring(member) or ""
                        # 檢查裝飾器是否為 property
                        is_prop = any(
                            (isinstance(dec, ast.Name) and dec.id == "property") or
                            (isinstance(dec, ast.Attribute) and dec.attr == "property")
                            for dec in member.decorator_list
                        )
                        is_prop_setter = any(
                            isinstance(dec, ast.Attribute) and dec.attr == "setter"
                            for dec in member.decorator_list
                        )

                        if is_prop_setter:
                            # 略過 setter，已在 getter 記錄
                            continue

                        if is_prop:
                            ret_type = get_annotation_str(member.returns)
                            cls_info["properties"].append({
                                "name": member.name,
                                "type": ret_type,
                                "doc": member_doc.strip()
                            })
                            api_data["statistics"]["total_properties"] += 1
                        else:
                            # 一般方法
                            is_static = any(
                                isinstance(dec, ast.Name) and dec.id == "staticmethod"
                                for dec in member.decorator_list
                            )
                            is_classmeth = any(
                                isinstance(dec, ast.Name) and dec.id == "classmethod"
                                for dec in member.decorator_list
                            )
                            params = []
                            for arg in member.args.args:
                                if arg.arg in ("self", "cls"):
                                    continue
                                arg_type = get_annotation_str(arg.annotation)
                                params.append({
                                    "name": arg.arg,
                                    "type": arg_type
                                })

                            ret_type = get_annotation_str(member.returns)
                            cls_info["methods"].append({
                                "name": member.name,
                                "is_static": is_static or is_classmeth,
                                "parameters": params,
                                "return_type": ret_type,
                                "doc": member_doc.strip()
                            })
                            api_data["statistics"]["total_methods"] += 1

                module_classes[item.name] = cls_info

            elif isinstance(item, ast.FunctionDef):
                func_doc = ast.get_docstring(item) or ""
                params = []
                for arg in item.args.args:
                    arg_type = get_annotation_str(arg.annotation)
                    params.append({
                        "name": arg.arg,
                        "type": arg_type
                    })
                ret_type = get_annotation_str(item.returns)
                module_functions.append({
                    "name": item.name,
                    "parameters": params,
                    "return_type": ret_type,
                    "doc": func_doc.strip()
                })
                api_data["statistics"]["total_functions"] += 1

        if module_classes or module_functions:
            api_data["modules"][module_name] = {
                "doc": module_doc.strip(),
                "classes": module_classes,
                "functions": module_functions
            }

    out_path = Path(__file__).resolve().parent.parent / "docs" / "api_inventory" / "mechanical_api.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(api_data, f, ensure_ascii=False, indent=2)

    print(f"Mechanical API 抽取完成！存入: {out_path}")
    print(f"統計: Modules={api_data['statistics']['total_modules']}, Classes={api_data['statistics']['total_classes']}, Methods={api_data['statistics']['total_methods']}, Properties={api_data['statistics']['total_properties']}, Functions={api_data['statistics']['total_functions']}")
    return api_data

if __name__ == "__main__":
    extract_mechanical()
