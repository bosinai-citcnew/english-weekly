# 每週英文教室（免費版）

給 A2–B1 程度學習者的英文 App。手機、電腦都能用，不需要任何帳號或訂閱。每週一自動換一批新文章。

- 網站：GitHub Pages（免費）
- 每週更新：GitHub Actions（免費）＋ GitHub Models（免費 AI，不用 API 金鑰、不用信用卡）
- 文章來源：BBC 新聞的公開 RSS 標題與摘要，由 AI 改寫成簡單的學習文章並附原文連結；TED 主題從內建清單輪流選

## 第一次設定（約 10 分鐘）

1. **註冊 GitHub**：到 github.com 註冊免費帳號。
2. **建立儲存庫**：右上角「+」→ New repository。名稱例如 `english-weekly`，選 **Public**，按 Create repository。
3. **上傳檔案**：在新儲存庫頁面按「uploading an existing file」，把這個資料夾裡的所有檔案和資料夾拖進去，按 Commit changes。
   - 包含 `.github` 這個資料夾。它在電腦上可能是隱藏的；Mac 在 Finder 按 ⌘ + Shift + . 可以顯示。
   - 如果拖曳時 `.github` 沒上傳到，在儲存庫按 Add file → Create new file，檔名輸入 `.github/workflows/weekly.yml`，把同名檔案的內容貼進去後存檔。
4. **開啟網站**：Settings → Pages → Build and deployment 的 Source 選 **GitHub Actions**。
5. **第一次執行**：上方 Actions 分頁 → 左邊「每週更新與發布網站」→ 右邊 Run workflow → Run workflow。等約 2 到 5 分鐘，綠色勾勾代表完成。
6. **打開網站**：Settings → Pages 最上面會顯示網址，通常是 `https://你的帳號.github.io/english-weekly/`。把這個網址分享給朋友即可。

之後每週一早上 6:10（台北時間）會自動更新，不需要做任何事。

## 常見問題

- **Actions 失敗了？** 點進失敗的那一次看紅色步驟的訊息。最常見的是 GitHub Models 暫時忙碌，隔天到 Actions 手動 Run workflow 重跑一次即可。失敗時網站會保留上週的文章，不會壞掉。
- **想改更新時間？** 修改 `.github/workflows/weekly.yml` 裡的 `cron`。時間是 UTC，台北時間減 8 小時。
- **想換 TED 演講清單？** 編輯 `scripts/update_week.py` 裡的 `TED` 清單，網址請用 `https://www.ted.com/talks/...` 的演講頁。
- **進度存在哪裡？** 每個人的單字本、成績存在自己的瀏覽器裡，換手機或清除瀏覽資料就會不見。
- **免費額度夠用嗎？** GitHub Models 的免費額度有每日次數限制，每週更新一次大約只會呼叫 5 到 10 次。

## 這個版本沒有的功能

免費版沒有 Claude 的功能：查本週單字表以外的字會改成開啟劍橋詞典；沒有 AI 自由對話、寫作批改、TED 原文的簡化與中文對照。朗讀和語音辨識使用瀏覽器內建功能，語音辨識在 Chrome 效果最好。模擬對話、跟讀、字卡、配對遊戲、週測驗都可以正常使用。
