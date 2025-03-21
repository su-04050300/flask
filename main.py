from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import os
import json
import sys
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# === 讀取 LINE 機密資訊 ===
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if not LINE_CHANNEL_SECRET or not LINE_CHANNEL_ACCESS_TOKEN:
    print("❌ LINE 環境變數未設定", file=sys.stderr)
    raise Exception("❌ LINE 環境變數未設定")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# === 讀取 Google Sheets 歌詞 ===
def get_sheet_data():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        

        print("🔍 型別:", type(creds_json))
        print("✅ GOOGLE_CREDENTIALS_JSON 已載入全部:",str(creds_json)[:-3])
        creds_json = str(creds_json)[:-3]+'"}'
        print("✅ 已載入全部creds_json",str(creds_json))
		
        if not creds_json:
            print("❌ GOOGLE_CREDENTIALS_JSON 環境變數未設定")
            raise Exception("❌ GOOGLE_CREDENTIALS_JSON 環境變數未設定")

        # 檢查格式並轉換
        creds_dict = json.loads(creds_json) if isinstance(creds_json, str) else creds_json

        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        print("✅ 成功轉換creds_dict")

        # 開啟指定試算表
        sheet_id = "12iaGClpEjnAw8K9mj6XlXivJdQAvvCykuk7ahcsZyyU"
        sheet = client.open_by_key(sheet_id)

        print("✅ 成功連線 Google Sheets，開始讀取資料...")

        records = sheet.get_all_records()

        # 加入驗證印出
        if records:
            print(f"📄 已讀取 {len(records)} 筆歌詞資料")
            print("📌 第一筆資料：", records[0])
        else:
            print("⚠️ 試算表為空（0 筆資料）")

        return records

    except Exception as e:
        print(f"❌ Google Sheets 錯誤: {e}")
        return []

# === LINE Webhook 路由 ===
@app.route("/callback", methods=["POST"])
def callback():
    try:
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)

        print("🔹 收到 Webhook Body: ", body)  # Debug 用

        handler.handle(body, signature)
    except InvalidSignatureError:
        print("❌ LINE Webhook 簽名驗證失敗", file=sys.stderr)
        abort(400)
    except Exception as e:
        print(f"❌ Webhook 內部錯誤: {e}", file=sys.stderr)
        abort(500)

    return "OK"


# === 處理文字訊息 ===
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        keyword = event.message.text.strip()
        print(f"🔹 收到使用者訊息: {keyword}")

        records = get_sheet_data()
        print("🔹🔹🔹🔹")
        print("get record form google sheet")
        print(records)
        matched = []
        
        for row in records:
            if keyword in row.get("歌詞", ""):
                matched.append(f'{row["歌名"]} - {row["演唱者"]}\n{row["歌詞"]}')
        
        if matched:
            reply = "\n\n".join(matched[:3])  # 最多三筆，避免太長
        else:
            reply = "找不到包含這個關鍵字的歌詞喔！"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
    except Exception as e:
        print(f"❌ 訊息處理錯誤: {e}", file=sys.stderr)

if __name__ == "__main__":
    print("✅ Flask 應用正在啟動...")
    app.run(host="0.0.0.0", port=8080)
