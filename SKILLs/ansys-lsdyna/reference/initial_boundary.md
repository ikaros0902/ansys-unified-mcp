# LS-DYNA 初始速度與邊界條件設置指南 (`initial_boundary.md`)

落摔試驗若依真實物理從空中自由釋放，將消耗大量無謂運算時間在物體於空中平移的階段。標準工程做法是：**將物體平移至貼近地坪處，並直接賦予撞擊初速度**。

---

## 一、初速度計算與擺放原則

### 1. 撞擊初速度公式
設落摔測試之規範高度為 $h$（例如 $1.0\text{ m} = 1000\text{ mm}$），重力加速度 $g = 9806.65\text{ mm/s}^2$：
$$v_0 = -\sqrt{2 \cdot g \cdot h}$$
- 例：$h = 1000\text{ mm} \implies v_0 = -\sqrt{2 \times 9806.65 \times 1000} \approx -4428.69\text{ mm/s}$。
- 例：$h = 1500\text{ mm} \implies v_0 = -\sqrt{2 \times 9806.65 \times 1500} \approx -5424.02\text{ mm/s}$。

### 2. 空間幾何擺放準則
- 將落摔主體平移至物體最下端距離剛性地面 **$1.0 \sim 2.0\text{ mm}$** 之安全間隙處。
- **禁忌**：嚴禁初始間距小於接觸容差（防止 $t=0$ 發生初始穿透）；亦不建議大於 $5\text{ mm}$（白白浪費計算時間步）。

---

## 二、初始速度卡片：*INITIAL_VELOCITY_GENERATION

將初速度向量均勻賦予指定部件（Part）或節點集（Node Set）：

```text
*INITIAL_VELOCITY_GENERATION
$#      id      styp     omega        vx        vy        vz      ivat     icid
         1         2       0.0       0.0       0.0  -4428.69         0        0
$#      xc        yc        zc        nx        ny        nz     phase    irigid
       0.0       0.0       0.0       0.0       0.0       0.0         0         0
```

### 欄位解析：
- **`id`**：實體目標編號（如部件號 1）。
- **`styp`**：目標類型（`1`=Part Set, `2`=Part ID, `3`=Node Set）。
- **`vz`**：Z 方向初速度（負號表示朝向 -Z 方向衝擊地坪）。

---

## 三、剛性地面定義：*RIGIDWALL_PLANAR

使用平面剛性牆代替網格化的實體地坪，具備無限大剛度且完全不消耗有限元求解自由度：

```text
*RIGIDWALL_PLANAR
$#    nsid      nsid       box       box      dseq      dseq
         0         0         0         0       0.0       0.0
$#      xt        yt        zt        xh        yh        zh      fric       wvel
       0.0       0.0       0.0       0.0       0.0       1.0      0.30        0.0
```

### 欄位解析：
- **`xt, yt, zt`**：剛性平面上任意一點坐標（例如地面位於 $Z = 0$ 處，填 `0.0, 0.0, 0.0`）。
- **`xh, yh, zh`**：地面的向外法向量向量（朝向物體方向，衝擊面向上則填 `0.0, 0.0, 1.0`）。
- **`fric`**：剛性地坪與落摔體之間的庫侖摩擦係數（如 `0.30`）。
