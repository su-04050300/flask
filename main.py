from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import os
import json
import sys
import gspread
from google.oauth2.service_account import Credentials
import random

import tempfile 

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
        

        #print("🔍 型別:", type(creds_json))
        #print("✅ GOOGLE_CREDENTIALS_JSON 已載入全部:",str(creds_json))

        if not creds_json:
            print("❌ GOOGLE_CREDENTIALS_JSON 環境變數未設定")
            raise Exception("❌ GOOGLE_CREDENTIALS_JSON 環境變數未設定")


        # 修復結尾多餘分號
        #if creds_json.strip().endswith(";}"):
         #   print("⚠️ 偵測到 GOOGLE_CREDENTIALS_JSON 結尾有多餘分號，已自動修復")
          #  creds_json = creds_json.strip()[:-1]
        
        #print("🔍 嘗試解析 GOOGLE_CREDENTIALS_JSON...")
        #print(f"🔹 第一個字元: {repr(creds_json[:1])}")
        #print(f"🔹 最後 10 個字元: {repr(creds_json[-10:])}")
        #print(f"🔹 JSON 長度: {len(creds_json)}")

        


        try:
            print("🔍 嘗試解析 GOOGLE_CREDENTIALS_JSON...")
            creds_dict = json.loads(creds_json)
            
            
            # 確保 private_key 存在且正確
            if "private_key" not in creds_dict:
                print("❌ 錯誤：GOOGLE_CREDENTIALS_JSON 沒有 'private_key'")
            elif not creds_dict["private_key"].startswith("-----BEGIN PRIVATE KEY-----"):
                print(f"⚠️ 'private_key' 開頭異常: {repr(creds_dict['private_key'][:30])}")
            else:
                print("✅ 'private_key' 解析正常")
                
        except json.JSONDecodeError as json_err:
            print("❌ JSON 格式錯誤！")
            print(creds_json[:500])  # 印前 500 字供檢查
            print(f"錯誤內容: {json_err}")
            raise

        # 檢查格式並轉換
        creds_dict = json.loads(creds_json)
        print("🧪 已解析 Key 清單：", creds_dict.keys())

        try:
            #print(f"🔍 'private_key' 第一行: {creds_dict['private_key'].splitlines()[0]}")
            #creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            #print("🧪 已建立 Credentials 物件")
            #client = gspread.authorize(creds)
            #print("✅ 成功轉換 creds_dict 並建立 gspread client")
            
            # ✅ **將 JSON 存入臨時檔案**
            #with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
             #   temp_file.write(json.dumps(creds_dict))
              #  temp_filename = temp_file.name
    
            # ✅ **使用 from_service_account_file**
            #creds = Credentials.from_service_account_file(temp_filename, scopes=scopes)
            #client = gspread.authorize(creds)
    
            # 修正 private_key 格式
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

            # 嘗試授權
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            client = gspread.authorize(creds)
            print("✅ gspread 授權成功！")

            
        except Exception as e:
            print(f"❌ gspread 授權失敗: {e}")
            raise  # 再丟出錯誤讓外層 catch

        # 開啟指定試算表
        sheet_id = "12iaGClpEjnAw8K9mj6XlXivJdQAvvCykuk7ahcsZyyU"
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1
        
        print("✅ 成功連線 Google Sheets，開始讀取資料...")
        
        records = worksheet.get_all_records()
        
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
        
def get_song_list_from_sheet2():
    #讀取工作表2的所有曲目（不重複）
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        #print("🔍 型別:", type(creds_json))
        #print("✅ GOOGLE_CREDENTIALS_JSON 已載入全部:",str(creds_json))

        if not creds_json:
            print("❌ GOOGLE_CREDENTIALS_JSON 環境變數未設定")
            raise Exception("❌ GOOGLE_CREDENTIALS_JSON 環境變數未設定")
        print("🔍 嘗試解析 GOOGLE_CREDENTIALS_JSON...")
        creds_dict = json.loads(creds_json)
            
            
        # 確保 private_key 存在且正確
        if "private_key" not in creds_dict:
            print("❌ 錯誤：GOOGLE_CREDENTIALS_JSON 沒有 'private_key'")
        elif not creds_dict["private_key"].startswith("-----BEGIN PRIVATE KEY-----"):
            print(f"⚠️ 'private_key' 開頭異常: {repr(creds_dict['private_key'][:30])}")
        else:
            print("✅ 'private_key' 解析正常")


        # 修正 private_key 格式
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

        # 嘗試授權
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        print("✅ gspread 授權成功！")
        
        sheet_id = "12iaGClpEjnAw8K9mj6XlXivJdQAvvCykuk7ahcsZyyU"    
        sheet = client.open_by_key(sheet_id).worksheet("sheet2")
        values = sheet.col_values(1)  # 假設歌曲都放在第1欄
        values = values[1:]
        # 去除重複與空值
        unique_songs = sorted(set([v.strip() for v in values if v.strip()]))
        # 加入 Emoji 標記
        decorated = [f"🎵 {i+1}. {title}" for i, title in enumerate(unique_songs)]
        
        print("🔍 所有歌曲:")
        print(unique_songs)
        return decorated
    except Exception as e:
        print(f"❌ 無法讀取工作表2: {e}")
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
        
        
        
        if keyword == "-全部歌曲":
            song_list = get_song_list_from_sheet2()
            if song_list:
                chunks = [song_list[i:i+10] for i in range(0, len(song_list), 10)]  # 避免超過 LINE 訊息長度
                messages = [TextSendMessage(text="\n".join(chunk)) for chunk in chunks]
                line_bot_api.reply_message(event.reply_token, messages)
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="目前找不到任何歌曲資料。")
                )
            return
        
        records = get_sheet_data()
        print("🔹🔹🔹🔹")
        #print("get record from google sheet")
        #print(records)

        matched = []
        
        # 找出包含關鍵字的歌詞
        for row in records:
            if keyword in row.get("歌詞", ""):
                #matched.append(TextSendMessage(text=f'{row["歌名"]} - {row["演唱者"]}\n{row["歌詞"]}'))
                lyric = row.get("歌詞", "")
                if lyric.startswith(keyword):
                    matched.append(TextSendMessage(text=f'{row["歌詞"]}'))

        # 如果有符合的歌詞，回覆最多 5 則（LINE API 單次最多 5 則訊息）
        if matched:
            max_reply = 5
            count = min(max_reply, len(matched))
            random_indices = [random.randint(0, len(matched) - 1) for _ in range(count)]
            
            print(f"🔹 隨機索引: {random_indices}")
            
            selected = [matched[i] for i in random_indices]
            print(f"🔹 隨機選取歌詞: {selected}")
            messages = [TextSendMessage(text=s.text[:4900]) for s in selected]  # 加上長度保護
            line_bot_api.reply_message(event.reply_token, messages)
            #line_bot_api.reply_message(event.reply_token, matched[:max_reply])
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到包含這個關鍵字的歌詞喔！"))

    except Exception as e:
        print(f"❌ 訊息處理錯誤: {e}", file=sys.stderr)

# === 處理貼圖訊息 ===
from linebot.models import StickerMessage, StickerSendMessage

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event):
    sticker = event.message
    #sticker.package_id
    #sticker.sticker_id
    stickerID=[2734, 2735, 2736, 2737, 2738, 2741, 2742, 2743, 2745, 2747, 2748, 2752, 2759, 2763, 2768, 2771]
    random_id = random.choice(stickerID)
    print(f"🎉 收到貼圖: packageId={sticker.package_id}, stickerId={sticker.sticker_id}")
    print(f"✅ 回覆貼圖: stickerId={random_id}")
    # 傳回同樣的貼圖（或固定一張你想要的貼圖）
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=11537,
            sticker_id=random_id
            
        )
    )


if __name__ == "__main__":
    print("✅ Flask 應用正在啟動...")
    app.run(host="0.0.0.0", port=8080)
