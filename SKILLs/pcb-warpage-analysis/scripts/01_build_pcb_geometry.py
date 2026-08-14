# -*- coding: utf-8 -*-
"""
SpaceClaim script: Build PCB Multi-Layer Geometry with Share Topology & UI Delay.
"""
import time

def build_pcb_geometry(num_layers=79, length=100.0, width=80.0, total_thickness=1.6):
    """
    建立 PCB 多層板幾何結構並設定 Share Topology。
    ponytail: 加入 50ms 延遲以避免 GUI Property Pane 刷新異常。
    """
    print("開始建立 {} 層 PCB 幾何模型...".format(num_layers))
    layer_thickness = total_thickness / num_layers
    
    # SpaceClaim API 環境呼叫樣板
    try:
        import SpaceClaim.Api.V22 as Api
        from SpaceClaim.Api.V22.Geometry import Point, DesignVector, SharedTopologyType
        
        doc = Api.Scripting.GetActiveDocument()
        comp = doc.MainPart.CreateComponent("PCB_Stackup")
        
        for i in range(num_layers):
            z_offset = i * layer_thickness
            # 建立多層 Body 方塊
            origin = Point.Create(0, 0, z_offset)
            box = Api.Geometry.Body.CreateBlock(origin, DesignVector.Create(length, width, layer_thickness))
            box.Name = "Layer_{:02d}".format(i + 1)
            comp.Part.AddBody(box)
            
            # UI 刷新緩衝延遲 (50ms)
            time.sleep(0.05)
            
        # 設定 Component Share Topology (關鍵：不得直接在 Root Design 設定)
        comp.SetSharedTopology(SharedTopologyType.Share)
        print("成功建立 PCB 79 層結構並啟動 Share Topology。")
        return True
    except Exception as e:
        print("SpaceClaim API 執行提示: {}".format(e))
        return False

if __name__ == "__main__":
    build_pcb_geometry()
