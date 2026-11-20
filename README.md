# 每週英文教室（免費版）

給 A2–B1 程度學習者的英文 App。手機、電腦都能用，不需要任何帳號或訂閱。每週一自動換一批新文章。

- 網站：GitHub Pages（免費）
- 每週更新：GitHub Actions（免費），從內建的 12 週文章題庫（`bank.json`）依序輪換，**不需要 AI、不需要金鑰**，所以一定會更新
- 每週 4 篇：3 篇生活與科學短文（附參考來源）、1 篇 TED 熱門演講主題（附原演講連結）

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

- **Actions 失敗了？** 點進失敗的那一次看紅色步驟的訊息。失敗時網站會保留上週的文章，不會壞掉。
- **想改更新時間？** 修改 `.github/workflows/weekly.yml` 裡的 `cron`。時間是 UTC，台北時間減 8 小時。
- **進度存在哪裡？** 每個人的單字本、成績存在自己的瀏覽器裡，換手機或清除瀏覽資料就會不見。
- **題庫用完怎麼辦？** 12 週後會從第 1 週重新開始。想加新文章：在 `bank/` 新增 `srcN.py`（格式照 `src1.py`），執行 `python bank/build.py` 後上傳。

## AI 功能（每個人自己的免費額度）

網站本身不放任何金鑰。每位使用者可以在 App 的「會話」頁，用自己的 Google 帳號建立免費金鑰並貼上，就能開啟 AI 自由對話、查任何單字、寫作批改和 TED 原文對照。金鑰只存在使用者自己的瀏覽器。

不連接 AI 也能用：模擬對話（分初級、中級、高級）、跟讀、字卡、配對遊戲、週測驗。朗讀和語音辨識使用瀏覽器內建功能，語音辨識在 Chrome 效果最好。
