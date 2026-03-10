import os
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

load_dotenv()

CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
    raise RuntimeError("請設定環境變數.env")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(CHANNEL_SECRET)

app = FastAPI()

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.post("/callback")
async def callback(request: Request, x_line_signature: str = Header(None)):
    if x_line_signature is None:
        raise HTTPException(status_code=400, detail="Missing X-Line-Signature")
    
    body_text = (await request.body()).decode("utf-8")

    try:
        events = parser.parse(body_text, x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalis signature")
    
    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            try:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=event.message.text + " 汪！")
                )
            except Exception as e:
                print(f"[ERROR] reply_message failed: {e}")

    return "ok"
