# 葉輪機械網格與邊界設定最佳實踐

1. 優先使用 TurboGrid 生成高質量結構化六面體網格 (Hexahedral Mesh)。
2. 轉子-定子交界面在穩態分析中使用 Stage 或 Frozen Rotor，瞬態使用 Transient Rotor-Stator。
3. 壁面邊界層 y+ 控制在 1 左右以精確捕捉分離流。
