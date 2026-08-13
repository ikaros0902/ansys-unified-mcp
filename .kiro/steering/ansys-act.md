---
inclusion: fileMatch
fileMatchPattern: '**/*.py'
---

# ANSYS / ACT 專案規則

## ACT 開發前置

- 收到撰寫或修改 ANSYS ACT 程式碼的要求時,先參考 Obsidian Note(`D:\Ikaros\Obisidian\Second Brain\2-project\ACT_Project` 及其子目錄)內的專案規範與 API 知識,再動手。
- 開發與除錯採 Sub-agent 協作:一個負責找問題與根因、一個負責編寫、一個負責編譯與 API 正確性驗證,直到完全無誤。

## ANSYS CAE 上下文

新對話時,若存在則依序閱讀:`contexts/context.md`(專案核心上下文)、`README.md`、`specs/*.md`。若無,先詢問專案狀況並建議建立 `contexts/context.md`。

## 工作模式

- 複雜任務:先讀相關規範與 Obsidian note,制定計劃再執行,完成後更新相關文件。
- 簡單任務:直接執行,保持風格一致。
- 不確定時:主動詢問,提供選項讓使用者決策。
