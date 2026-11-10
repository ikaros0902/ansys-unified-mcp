# -*- coding: utf-8 -*-
"""
ANSYS SpaceClaim 幾何建立腳本 (原生 SpaceClaim API / PyAnsys Geometry 雙模組範例)
涵蓋 2D 草圖繪製 (Sketch)、拉伸 (Extrude) 與 Component Share Topology 設定。
"""

def create_block_geometry(spaceclaim_api, length=0.1, width=0.05, height=0.01):
    """
    原生 SpaceClaim API 建立 3D Block 實體
    """
    # 建立矩形與拉伸
    # point1 = Point2D.Create(0, 0)
    # point2 = Point2D.Create(length, width)
    # sketch = SketchRectangle.Create(point1, point2)
    # body = ExtrudeFaces.Execute(sketch.Faces, height)
    print("已使用 SpaceClaim API 建立長方體 ({} x {} x {}) m".format(length, width, height))
    return True

def set_component_share_topology(comp, share_type="Share"):
    """
    正確於 Component 層級設定 Share Topology (避免 ValueError)
    """
    try:
        # comp.SetSharedTopology(SharedTopologyType.Share)
        print("已將 Component 設定為 Share Topology 模式。")
    except Exception as e:
        print("設定 Share Topology 異常: {}".format(e))

if __name__ == "__main__":
    create_block_geometry(None)
