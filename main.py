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

        if not creds_json:
            print("❌ GOOGLE_CREDENTIALS_JSON 環境變數未設定", file=sys.stderr)
            raise Exception("❌ GOOGLE_CREDENTIALS_JSON 環境變數未設定")

        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open("LyricsDB").sheet1
        return sheet.get_all_records()

    except Exception as e:
        print(f"❌ Google Sheets 錯誤: {e}", file=sys.stderr)
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

        '''for row in records:
            if keyword in column.get("歌詞", ""):
                reply = f'{row["歌名"]} - {row["演唱者"]}\n{row["歌詞"]}'
                break'''
        print(records)
        for keyword in records:
            if keyword in column.get("歌詞", ""):
                reply = f'{row["歌名"]} - {row["演唱者"]}\n{row["歌詞"]}'
                break       
        
                
        else:
            reply = "找不到包含這個關鍵字的歌詞喔！!!"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
    except Exception as e:
        print(f"❌ 訊息處理錯誤: {e}", file=sys.stderr)

if __name__ == "__main__":
    print("✅ Flask 應用正在啟動...")
    app.run(host="0.0.0.0", port=8080)
