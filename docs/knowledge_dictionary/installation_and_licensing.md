# Ansys 安裝與授權字典

本文整理 Ansys 2026 R1 Quick Start PDF 與官方 Installation／Licensing Guide 的可核實段落。Quick Start 僅供流程導覽，不取代平台安裝手冊、授權管理手冊或組織內的 license server 設定程序。兩份本機 PDF 封面均標示 Release 2026 R1，各 8 頁，已保留原件及逐頁 Markdown。

## 產品安裝與用戶端設定

### 多版本安裝順序

2026 R1 Installation Quick Start 的重要事項指出：若需安裝多個 Ansys release，應依時間順序由舊到新安裝。若已安裝 2026 R1 後再安裝較早版本，可能造成 licensing issues；文件給出的恢復流程是先移除 2026 R1，再按順序重裝。若要保留舊版並新增 2026 R1，文件說明可使用相同 root installation directory（預設 `C:\Program Files\ANSYS Inc`）建立 side-by-side 安裝；若要移除舊版，建議先完成並確認 2026 R1 可正常使用再移除舊版。這些是 2026 R1 文件規則；執行卸載或升級前仍須核對完整平台手冊及 release notes。[Quick Start Installation Guide，PDF Page 5](../ANSYS_Document/Installation_and_Licensing/v261/manuals/quickstartinstall.pdf#page=5) · [v261 Windows Installation Guide](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/installation/win_install.html)

2026 R1 產品需搭配 2026 R1 License Manager；該版 License Manager 文件稱可支援先前 Ansys releases。這不代表不同產品版本的功能、license entitlement 或客戶端設定都相同。[Quick Start Installation Guide，PDF Page 5](../ANSYS_Document/Installation_and_Licensing/v261/manuals/quickstartinstall.pdf#page=5) · [Quick Start Licensing Guide，PDF Page 5](../ANSYS_Document/Installation_and_Licensing/v261/manuals/quickstartlic.pdf#page=5)

### 取得與啟動安裝程式

Quick Start 指出下載安裝包需要有效的 technical support agreement；依產品及平台可能需要多個套件。文件列出 Windows x64／Linux x64、Primary Packages／ISO Images，並建議解壓到新的暫存資料夾。Windows 從 `setup.exe` 以 Run as Administrator 啟動；Linux 從掛載目錄執行 `INSTALL`。個別產品可能另有 post-installation 步驟，應依 Windows／Linux Installation Guide 完成。[Quick Start Installation Guide，PDF Page 5–6](../ANSYS_Document/Installation_and_Licensing/v261/manuals/quickstartinstall.pdf#page=5) · [v261 Installation Guides](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/pdf/ANSYS_Inc._Installation_Guides.pdf)

Installation Guide 將產品安裝與 license server 角色分開說明：執行產品的 client 需要連到有效的 License Manager；License Manager 必須安裝在至少一台 server machine 上，client 本機不一定需要安裝 License Manager。Linux 的 server 安裝章節明示，License Manager 安裝包需從 Customer Portal 的 Tools 下載，並以 `./INSTALL -LM` 啟動；該章節亦說明可安裝在獨立於產品 client 的機器。[v261 Windows client licensing](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/installation/win_install.html) · [v261 Linux License Manager installation](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/installation/lin_install_server.html)

### Client licensing 情境

| 情境 | Quick Start 說明的動作 | 核對界線 |
| --- | --- | --- |
| 已有有效 license key，且已有 server 設定 | 安裝產品後，在 client licensing 設定頁確認已有有效 server 規格，再結束安裝。 | 若 server 規格缺失，安裝程式會要求輸入 server 資訊。 |
| 有新的 license key | 先交由 license administrator 安裝到指定 server，再完成 client 產品安裝與 server 指定。 | license key 未在 server 生效前不能執行產品。 |
| 尚無 license key | License administrator 使用 `ANSLIC_ADMIN` 的 Register License Server Information 產生 `licserver.info`，交由 Ansys 業務代表建立 license key；取得 key 後安裝到 server。 | 操作順序依 PDF Page 7–8；不要把 `licserver.info` 當成 license file。 |

上述步驟整理自 [Quick Start Installation Guide，PDF Page 6–8](../ANSYS_Document/Installation_and_Licensing/v261/manuals/quickstartinstall.pdf#page=6)。完整產品選項、silent installation、CAD 設定及平台差異請查 [v261 Installation Guides](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/pdf/ANSYS_Inc._Installation_Guides.pdf)。

## License Manager 與 license file

### 角色與版本邊界

自 Ansys 2024 R2 起，License Manager 安裝包已從產品安裝包分離。2026 R1 Quick Start 指示從 Customer Portal 的 `Downloads > Current Release > Tools > Ansys License Manager` 取得安裝包。2026 R1 License Manager 與其管理流程有更新；若使用 Ansys License Management Center 管理，依該工具的程序操作。使用自有管理程序的組織，Quick Start 明確提醒其簡易步驟可能不適用，應先閱讀完整 Licensing Guide。[Quick Start Licensing Guide，PDF Page 5–6](../ANSYS_Document/Installation_and_Licensing/v261/manuals/quickstartlic.pdf#page=5) · [Ansys Licensing Guide v261](https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/licensing/licensing.html)

### 首次安裝及加入 license

Quick Start 中 License Manager server 的常見操作順序如下：

1. 在 server 安裝與 Ansys 2026 R1 相符的 License Manager。Windows 執行 `setup.exe` 並選擇 `Install Ansys License Manager`；Linux 執行 `./INSTALL -LM`。對三台 server 的 redundant triad，依文件在三台都執行相關程序。
2. 從 Ansys License Management Center 取得 host ID 資訊；若尚無 license file，將選定的 host ID 資訊提供給 Ansys 業務代表建立 license file。
3. 將收到的 `.lic` 檔暫存，再從 License Management Center 選擇 `Add A License File`，指定檔案並執行 `Install License File`。
4. 查看 Status pane 確認 License Manager 啟動結果。管理中心也可查看 FlexNet license／status、啟停 License Manager 與重新讀取設定。

這是經簡化的 2026 R1 Quick Start 路徑；三台 server 環境須使用同一 license file。License Management Guide 指出 redundant triad 至少有兩台 server 運行後，產品才可取得 license。詳見 [Quick Start Licensing Guide，PDF Page 5–8](../ANSYS_Document/Installation_and_Licensing/v261/manuals/quickstartlic.pdf#page=5) 與 [Ansys License Management Guide v261，License Server Administration](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/pdf/ansys_license_management_guide.pdf)。

### 用戶端指定 FlexNet server

`Ansys License Management Center` 是 server 管理介面；`Ansys Licensing Settings` 是 client 設定工具，兩者用途不同。v261 Licensing Settings Utility 可在 FlexNet Publisher > License Servers 設定 hostname、port 與查詢順序，使用 `Test` 檢查 server 可達性後儲存。server 順序會影響 checkout 的查詢順序；無回應的 server 可能拖慢 checkout。[Using the Ansys Licensing Settings Utility v261](https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/licensing/lmg_using_cls.html)

在 Installation 模式下，工具使用安裝層級設定；User 模式將使用者設定存於 Windows `%AppData%\.ansys_licensing\ansyslmd.ini` 或 Linux `${HOME}/.ansys_licensing/ansyslmd.ini`。一般設定的讀取優先序是環境變數、user `ansyslmd.ini`、installation `ansyslmd.ini`。`SERVER` 設定有特例：先讀 `ANSYSLMD_LICENSE_FILE`，再依 `ANS_FLEXLM_DISABLE_DEFLICPATH` 是否設定決定是否繼續讀取 user／installation 檔案。[Using the Ansys Licensing Settings Utility v261](https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/licensing/lmg_using_cls.html)

### 防火牆核對

License Management Guide v261 列出的預設連線埠為 Licensing Interconnect `2325`、FlexNet `1055`，並要求另核對 license file `VENDOR` 行指定的 `PORT`。這些是 v261 文件所列預設值，不保證組織設定未變；防火牆規則應以實際 server／license file 設定核實。[Ansys License Management Guide v261，Firewall Settings](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/pdf/ansys_license_management_guide.pdf)

## 來源狀態與待補

本機兩份 Quick Start PDF 均保留原件，逐頁 Markdown 有 8/8 頁標記。完整版 Installation Guide、Licensing Guide、License Management Guide 及 Windows／Linux 線上章節以 v261 官方網址列入來源清冊；先前以瀏覽器讀取並整理摘要。這些頁面未下載或鏡像正文，因此未收入本機官方全文索引。官方 quick start PDF 標示 proprietary／confidential；團隊分享原文或衍生內容前仍須確認使用條款。

本頁只完成 2026 R1 快速安裝、client licensing、License Manager 安裝入口及常見網路／設定邊界；完整平台安裝、silent deployment、CAD integration、Elastic／Web licensing、複雜 triad 網路、custom licensing 流程與完整 troubleshooting 尚未整理或實際操作。產品安裝、License Manager 及 port 設定均未在本機執行驗證。


## 來源定位與檢索界線

本地正文只有兩份 v261 Quick Start，來源 ID 為 `ansys_e1557ebb521315b404ff8247`（Installation）及 `ansys_870432d779ea86181799d9f0`（Licensing）；均為 Release 2026 R1。逐頁引文使用 PDF 頁碼，可回到原件。PDF 以外的官方平台／授權指南曾在先前核讀並摘要於本字典，但沒有本機正文；網址包含 `Views/Secured` 的頁面可能要求客戶登入。它們是瀏覽摘要來源，不可視為本機全文可搜尋，也未在本輪重新驗證網站存取或授權條件。官方來源及目前狀態：

| 來源 | 用途 | 本機狀態 |
| --- | --- | --- |
| [Installation Guides v261 (PDF)](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/pdf/ANSYS_Inc._Installation_Guides.pdf) | 完整 Windows／Linux 平台安裝入口 | 網頁摘要；未鏡像 |
| [Windows Installation Guide v261](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/installation/win_install.html) | Windows client licensing 與安裝 | 網頁摘要；未鏡像 |
| [Linux License Manager installation v261](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/installation/lin_install_server.html) | Linux server 端 License Manager 安裝 | 網頁摘要；未鏡像 |
| [Licensing Guide v261](https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/licensing/licensing.html) | 授權架構與管理完整手冊 | 網頁摘要；未鏡像 |
| [Licensing Settings Utility v261](https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/licensing/lmg_using_cls.html) | Client FlexNet server 設定工具 | 網頁摘要；未鏡像 |
| [License Management Guide v261 (PDF)](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/pdf/ansys_license_management_guide.pdf) | License server 管理、port 與 triad | 網頁摘要；未鏡像 |

共享來源清冊已恢復這六筆官方 URL、標題與 `release=v261`。六列均標為 `online_summary_only`，`local_path` 空白，`indexed_chars=0`。版本依據是 URL 內的 v261。網站存取及授權條件未重新核實。

本機 PDF 轉 Markdown 維持原件，兩份 PDF 均有 8/8 個 `## PDF Page N` 標記；轉換文本與同名 `.md` 完全一致。封面、版權與目錄頁的文字較少，沒有因此視為缺頁。Installation 與 Licensing 的轉換稿分別有 3 與 5 個 U+0002 控制字元。部分字詞在抽取中被截斷，例如 `in` + U+0002 + `stalling`，英文關鍵字檢索可能受影響。表格、圖像及頁內讀序待視覺核對。引用操作步驟時以 PDF 原頁覆核，不把 Markdown 抽取品質當作完美轉換。


## 2026-11-04：Wave 7 本機來源盤點與限制說明

來源清冊含 2 份本機 v261 Quick Start PDF 和 6 筆官方線上摘要。原件與 canonical Markdown 雜湊均吻合，兩份鄰接 Markdown 與 canonical 逐份位元組相同。線上摘要無本機正文或雜湊，11 月 4 日批次未擷取清冊內 6 個網址。完整手冊與授權條件仍是來源缺口。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/installation_and_licensing_module_conversion_report_20261104.md)。
