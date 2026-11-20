# 每週英文教室（免費版）

給 A2–B1 程度學習者的英文 App。手機、電腦都能用，不需要任何帳號或訂閱。每週一自動換一批新文章。

- 網站：GitHub Pages（免費）
- 每週更新：GitHub Actions（免費）＋ Google Gemini 的免費額度（用 Google 帳號建立金鑰，不用信用卡）
- 文章來源：BBC 新聞的公開 RSS 標題與摘要，由 AI 改寫成簡單的學習文章並附原文連結；TED 主題從內建清單輪流選

## 第一次設定（約 10 分鐘）

1. **註冊 GitHub**：到 github.com 註冊免費帳號。
2. **建立儲存庫**：右上角「+」→ New repository。名稱例如 `english-weekly`，選 **Public**，按 Create repository。
3. **上傳檔案**：在新儲存庫頁面按「uploading an existing file」，把這個資料夾裡的所有檔案和資料夾拖進去，按 Commit changes。
   - 包含 `.github` 這個資料夾。它在電腦上可能是隱藏的；Mac 在 Finder 按 ⌘ + Shift + . 可以顯示。
   - 如果拖曳時 `.github` 沒上傳到，在儲存庫按 Add file → Create new file，檔名輸入 `.github/workflows/weekly.yml`，把同名檔案的內容貼進去後存檔。
4. **開啟網站**：Settings → Pages → Build and deployment 的 Source 選 **GitHub Actions**。
5. **建立免費 AI 金鑰**：到 https://aistudio.google.com/apikey 用 Google 帳號登入，按 Create API key，複製金鑰。
6. **把金鑰交給 GitHub**：儲存庫 Settings → Secrets and variables → Actions → New repository secret。Name 填 `GEMINI_API_KEY`，Secret 貼上金鑰，按 Add secret。
7. **第一次執行**：上方 Actions 分頁 → 左邊「每週更新與發布網站」→ 右邊 Run workflow → Run workflow。等約 2 到 5 分鐘，綠色勾勾代表完成。
8. **打開網站**：Settings → Pages 最上面會顯示網址，通常是 `https://你的帳號.github.io/english-weekly/`。把這個網址分享給朋友即可。

之後每週一早上 6:10（台北時間）會自動更新，不需要做任何事。

## 常見問題

- **Actions 失敗了？** 點進失敗的那一次看紅色步驟的訊息。最常見的是 Google 免費額度暫時用完或金鑰沒設定好，隔天到 Actions 手動 Run workflow 重跑一次即可。失敗時網站會保留上週的文章，不會壞掉。
- **想改更新時間？** 修改 `.github/workflows/weekly.yml` 裡的 `cron`。時間是 UTC，台北時間減 8 小時。
- **想換 TED 演講清單？** 編輯 `scripts/update_week.py` 裡的 `TED` 清單，網址請用 `https://www.ted.com/talks/...` 的演講頁。
- **進度存在哪裡？** 每個人的單字本、成績存在自己的瀏覽器裡，換手機或清除瀏覽資料就會不見。
- **免費額度夠用嗎？** Google 的免費額度每分鐘、每天都有上限，每週更新一次大約只會呼叫 5 到 10 次。

## AI 功能（每個人自己的免費額度）

網站本身不放任何金鑰。每位使用者可以在 App 的「會話」頁，用自己的 Google 帳號建立免費金鑰並貼上，就能開啟 AI 自由對話、查任何單字、寫作批改和 TED 原文對照。金鑰只存在使用者自己的瀏覽器。

不連接 AI 也能用：模擬對話（分初級、中級、高級）、跟讀、字卡、配對遊戲、週測驗。朗讀和語音辨識使用瀏覽器內建功能，語音辨識在 Chrome 效果最好。
