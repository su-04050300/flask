---
title: Flask
description: A popular minimal server framework for Python
tags:
  - python
  - flask
---

# Python Flask Example

This is a [Flask](https://flask.palletsprojects.com/en/1.1.x/) app that serves a simple JSON response.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/zUcpux)

## ✨ Features

- Python
- Flask

## 💁‍♀️ How to use

- Install Python requirements `pip install -r requirements.txt`
- Start the server for development `python3 main.py`

# 📌 Lyrics LINE Bot

一個可以搜尋歌詞的 LINE 機器人，使用者輸入關鍵字，即可回傳包含該字詞的歌曲片段（來自 Google Sheets 歌詞資料庫）。也支援「-全部歌曲」顯示歌單清單。

---

## 🧱 專案架構與技術

- **Python 3.7**
- **Flask**：建立 Webhook 伺服器
- **LINE Messaging API**：接收使用者訊息與回覆
- **Google Sheets**：儲存與讀取歌詞資料
- **gspread / google-auth**：串接 Google Sheets API
- **Railway**：部署與執行機器人後端

---

## ⚙️ 功能列表

### 🔍 搜尋歌詞

使用者傳入任一關鍵字，機器人會搜尋歌詞資料庫，回傳最多三筆符合歌詞內容的結果（每一筆為一則訊息）。

### 📃 顯示目前曲目清單

當使用者輸入 `-全部歌曲` 時，會回傳目前 Google Sheets 第二個工作表中列出的曲目清單，每行包含 🎵 emoji 標記。

### 📤 自動上傳歌詞（lyrics.txt）

透過 `upload_lyrics_to_gsheet.py` 腳本，自動將 `lyrics.txt` 中的歌詞解析並寫入 Google Sheet。

---

## 🗂️ 資料結構說明

### Google Sheets 表單結構

#### 工作表1（Lyrics）

| 歌名 | 演唱者 | 歌詞 |
|------|--------|------|
| Super Star | S.H.E | 你是電 你是光 你是唯一的神話 |

#### 工作表2（曲目清單）

| 曲目清單 |
|----------|
| Super Star - S.H.E |
| 擁抱 - 五月天 |

---

## 🚀 部署與執行

### 🔐 Railway 環境變數設定

| Key | Value |
|-----|-------|
| `LINE_CHANNEL_ACCESS_TOKEN` | 從 LINE Developers 後台取得 |
| `LINE_CHANNEL_SECRET` | 從 LINE Developers 後台取得 |
| `GOOGLE_CREDENTIALS_JSON` | 將 service account 金鑰 JSON 轉為一行字串貼上（可用 `json.dumps()` 轉換） |
| `SPREADSHEET_ID` | Google Sheet 的 ID（網址中的 `.../d/{這段}/edit`） |

---

## 🧪 執行方式（本機開發）

1. 安裝套件：

```bash
pip install -r requirements.txt
```

2. 建立 `.env` 並填入正確資訊（若要本機測試）：

```
LINE_CHANNEL_ACCESS_TOKEN=xxx
LINE_CHANNEL_SECRET=xxx
SPREADSHEET_ID=xxx
GOOGLE_CREDENTIALS_JSON={"type": "...", ...}
```

3. 執行主程式：

```bash
python main.py
```

---

## ✏️ 如何新增歌詞

### 1. 在 `lyrics.txt` 中新增歌詞資料

格式如下（多首歌用 `**` 分隔）：

```
Super Star - S.H.E
你是電 你是光 你是唯一的神話
笑就歌頌 一皺眉頭就心痛
**

擁抱 - 五月天
脫下長日的假面
奔向夢幻的疆界
```

### 2. 執行上傳腳本

```bash
python upload_lyrics_to_gsheet.py
```

✅ 腳本會解析每一首歌詞並自動去除重複，再批次寫入 Google Sheet。

---

## 🧾 額外腳本功能

### 顯示所有曲目並寫入工作表2

```bash
python list_the_songs.py
```

此腳本會從工作表1 抓出所有不重複的曲目（歌名 + 演唱者），寫入工作表2。

---

## 📦 檔案結構

```
.
├── main.py                      # ✅ 主程式，Flask webhook 處理 LINE 訊息
├── upload_lyrics_to_gsheet.py  # 將 lyrics.txt 上傳至 Google Sheet
├── list_the_songs.py           # 產出目前所有曲目並儲存至工作表2
├── lyrics.txt                  # 原始歌詞資料（可人工編輯）
├── requirements.txt            # Python 套件需求
```

---

## 🔐 Google Sheets 權限設定

- 使用 Google Cloud Console 建立 **Service Account** 並產生金鑰 JSON。
- 將 Google Sheet 共用給該 service account 的 email（例如：`lyrics-bot-account@xxx.iam.gserviceaccount.com`）。

---

## 🎵 emoji 標記

目前列出歌單時會自動加入以下 emoji：
- 🎵：每首歌的前綴
- 可自訂更多如 🎶、🎤、🎧、🎼 等音樂相關 emoji

---

# 📜 常用指令整理

以下為此專案中曾使用過的終端機（Terminal / CMD）指令，依照用途分類整理，便於日後維護與部署。

---

## 🚀 專案執行

```bash
python3 main.py
```
> 執行 LINE Bot 主程式。

```bash
python3 lyrics_to_excel.py
```
> 將 `lyrics.txt` 中的歌詞資料轉換為 Excel（已被新版流程取代）。

```bash
python3 upload_lyrics_to_sheet.py
```
> 將 `lyrics.txt` 內容直接上傳到 Google Sheets。

```bash
python3 list_the_songs.py
```
> 整理目前 Google Sheets 的所有歌曲，儲存在第二工作表。

---

## 🧩 Python 套件安裝

```bash
python3 -m pip install gspread google-auth openpyxl
```
> 安裝專案所需的所有 Python 套件。

⚠️ 注意：使用 `python3 -m pip` 是為了避免 `pip` 被系統環境覆蓋錯誤。

---

## ☁️ Railway 平台設定流程

### 建立與部署專案

1. 前往 [https://railway.app](https://railway.app)
2. 註冊或登入 Railway 帳號
3. 點選「New Project」→ 選擇「Deploy from GitHub repo」
4. 授權連結你的 GitHub 帳號並選取此專案 repo
5. Railway 會自動部署 main.py 並提供一組公開網址（例如 `https://your-app-name.up.railway.app`）
6. 記下 `/callback` 完整網址供 LINE Webhook 使用

---

## 🔐 環境與權限設定（操作說明）

### 1. Railway 環境變數設定
在 Railway 專案的 Settings → Variables 中新增以下三項變數：

| 變數名稱 | 說明 |
|----------|------|
| `GOOGLE_CREDENTIALS_JSON` | **Google Service Account 的 JSON 金鑰內容（整段 JSON）需整理成一整行，並取代\n為\\n。** |
| `LINE_CHANNEL_SECRET` | 從 LINE Developers Console 取得的 Channel Secret |
| `LINE_CHANNEL_ACCESS_TOKEN` | 從 LINE Developers Console 取得的 Channel Access Token |


### 2. Google Sheets 權限
- 將你的 Google Sheets 分享給 Service Account Email，例如：
  - `lyrics-bot-account@xxxx.iam.gserviceaccount.com`

### 3. Google Cloud 設定

- 建立一個專案（lyrics-bot-project）
- 開啟 Google Sheets API
- 建立 Service Account 並產出金鑰（Key）
- 下載 JSON 格式的金鑰，並將其內容存入 Railway 的 GOOGLE_CREDENTIALS_JSON (lyrics-bot-project-57f7d330feba.json)

### 4. LINE Messaging API 設定
- 將 Webhook URL 設定為 Railway 給的網址 `/callback` 路徑，例如：
  - `https://your-app-name.up.railway.app/callback`
- 開啟 Webhook 功能
- 將 Channel Access Token 放入程式環境變數（或程式碼）

---

## 🍴 Fork Flask 專案

專案基礎為 Flask 並希望直接部署 LINE Bot 至 Railway，可參考以下方式：

1. 至 GitHub 搜尋並 fork 你需要的 Flask 專案 https://github.com/railwayapp-templates/flask
2. 將本專案程式碼放入對應目錄
3. Railway 連接 GitHub Repo 後部署
4. 記得加入環境變數與 Webhook 設定