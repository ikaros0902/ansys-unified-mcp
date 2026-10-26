# CFX Command Language (CCL) 指南

CFX 透過層次化 CCL 定義物理域、邊界與數值設定。

## CCL 核心語法
```ccl
FLOW: Flow Analysis 1
  DOMAIN: Rotor
    Coord Frame = Coord 1
    Domain Type = Fluid
    Location = B1
  END
END
```
