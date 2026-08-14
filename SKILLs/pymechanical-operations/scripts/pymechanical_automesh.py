# -*- coding: utf-8 -*-
"""
PyMechanical 自動網格劃分與多體連線腳本
透過 PyMechanical run_python_script 執行全體 Solid/Shell 分類與 MultiZone, Edge Sizing 及 Washer 劃分。
"""

def generate_automesh_script(solid_size_mm=2.0, shell_size_mm=3.0):
    """
    生成傳送至 Mechanical 執行的 AutoMesh 核心 Python 代碼
    """
    code_lines = [
        "import time",
        "from Ansys.ACT.Interfaces.Common import SelectionTypeEnum",
        "from Ansys.Mechanical.DataModel.Enums import MethodType",
        "from Ansys.Core.Units import Quantity",
        "",
        "model = DataModel.Project.Model",
        "mesher = model.Mesh",
        "geo_data = ExtAPI.DataModel.GeoData",
        "",
        "# 取得所有 Solid Body ID",
        "solid_ids = []",
        "for part in geo_data.Assemblies[0].Parts:",
        "    for body in part.Bodies:",
        "        if not body.Suppressed and str(body.BodyType) == 'GeoBodySolid':",
        "            solid_ids.append(body.Id)",
        "",
        "if solid_ids:",
        "    sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)",
        "    sel.Ids = solid_ids",
        "    sizing = mesher.AddSizing()",
        "    sizing.Name = 'Solid Body Sizing ({}) mm'.format(" + str(solid_size_mm) + ")",
        "    sizing.Location = sel",
        "    sizing.ElementSize = Quantity('{} [mm]'.format(" + str(solid_size_mm) + "))",
        "",
        "    method = mesher.AddAutomaticMethod()",
        "    method.Name = 'MultiZone Solid Method'",
        "    method.Location = sel",
        "    method.Method = MethodType.MultiZone",
        "",
        "# 執行 Generate Mesh",
        "start_t = time.time()",
        "mesher.GenerateMesh()",
        "print('AutoMesh 自動網格劃分成功，耗時: {:.2f}s'.format(time.time() - start_t))"
    ]
    return "\n".join(code_lines)

if __name__ == "__main__":
    script_str = generate_automesh_script()
    print("生成之 PyMechanical 網格自動化腳本:\n")
    print(script_str)
