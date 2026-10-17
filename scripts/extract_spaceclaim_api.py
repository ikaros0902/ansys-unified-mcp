"""
SpaceClaim API 萃取腳本 (Python 3.14 + pythonnet)
透過 .NET 反射 SpaceClaim.Api.V251.Scripting.dll，提取所有 Class、Method、Property 與 Enum。
"""
import os
import sys
import json
import inspect
from pathlib import Path

def extract_spaceclaim():
    scdm_dir = r"C:\Program Files\ANSYS Inc\v251\scdm"
    if scdm_dir not in sys.path:
        sys.path.append(scdm_dir)

    try:
        import clr
    except ImportError:
        print("pythonnet (clr) 未安裝，請先安裝 pythonnet")
        return None

    dll_name = "SpaceClaim.Api.V251.Scripting"
    try:
        clr.AddReference(dll_name)
    except Exception as e:
        print(f"載入 {dll_name} 失敗: {e}")
        return None

    import System
    import System.Reflection

    # 取得已載入的組件
    target_assembly = None
    for asm in System.AppDomain.CurrentDomain.GetAssemblies():
        if "SpaceClaim.Api" in asm.FullName and "Scripting" in asm.FullName:
            target_assembly = asm
            break

    if not target_assembly:
        print("找不到目標組件 SpaceClaim.Api.V251.Scripting")
        return None

    print(f"成功定位組件: {target_assembly.FullName}")

    api_data = {
        "module": "SpaceClaim",
        "assembly": target_assembly.FullName,
        "version": "2025 R1 (v251)",
        "classes": {},
        "enums": {},
        "interfaces": {},
        "statistics": {
            "total_types": 0,
            "total_methods": 0,
            "total_properties": 0,
            "total_enums": 0,
        }
    }

    try:
        types = target_assembly.GetExportedTypes()
    except Exception as e:
        print(f"獲取 ExportedTypes 發生錯誤: {e}")
        types = target_assembly.GetTypes()

    for t in types:
        api_data["statistics"]["total_types"] += 1
        type_name = t.FullName or t.Name

        if t.IsEnum:
            api_data["statistics"]["total_enums"] += 1
            enum_names = list(System.Enum.GetNames(t))
            api_data["enums"][type_name] = {
                "name": t.Name,
                "values": enum_names
            }
            continue

        type_dict = {
            "name": t.Name,
            "is_abstract": t.IsAbstract,
            "is_interface": t.IsInterface,
            "is_class": t.IsClass,
            "methods": [],
            "properties": []
        }

        # 提取 Methods (BindingFlags: Public, Instance, Static, DeclaredOnly)
        binding_flags = (
            System.Reflection.BindingFlags.Public |
            System.Reflection.BindingFlags.Instance |
            System.Reflection.BindingFlags.Static |
            System.Reflection.BindingFlags.DeclaredOnly
        )

        try:
            methods = t.GetMethods(binding_flags)
            for m in methods:
                if m.IsSpecialName:  # 略過 property getter/setter 等特殊方法
                    continue
                params = []
                for p in m.GetParameters():
                    params.append({
                        "name": p.Name,
                        "type": str(p.ParameterType.Name)
                    })
                type_dict["methods"].append({
                    "name": m.Name,
                    "is_static": m.IsStatic,
                    "return_type": str(m.ReturnType.Name),
                    "parameters": params
                })
                api_data["statistics"]["total_methods"] += 1
        except Exception:
            pass

        # 提取 Properties
        try:
            props = t.GetProperties(binding_flags)
            for p in props:
                type_dict["properties"].append({
                    "name": p.Name,
                    "property_type": str(p.PropertyType.Name),
                    "can_read": p.CanRead,
                    "can_write": p.CanWrite
                })
                api_data["statistics"]["total_properties"] += 1
        except Exception:
            pass

        if t.IsInterface:
            api_data["interfaces"][type_name] = type_dict
        else:
            api_data["classes"][type_name] = type_dict

    out_path = Path(__file__).resolve().parent.parent / "docs" / "api_inventory" / "spaceclaim_api.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(api_data, f, ensure_ascii=False, indent=2)

    print(f"SpaceClaim API 抽取完成！存入: {out_path}")
    print(f"統計: Types={api_data['statistics']['total_types']}, Methods={api_data['statistics']['total_methods']}, Properties={api_data['statistics']['total_properties']}, Enums={api_data['statistics']['total_enums']}")
    return api_data

if __name__ == "__main__":
    extract_spaceclaim()
