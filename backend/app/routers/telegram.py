import logging
from fastapi import APIRouter, Request, BackgroundTasks
import httpx

from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

async def process_telegram_update(update: dict):
    if "message" in update:
        message = update["message"]
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        
        if chat_id and text:
            # Simple echo for now, later we integrate AI logic here
            await send_telegram_message(chat_id, f"Evoslim received: {text}")

async def send_telegram_message(chat_id: int, text: str):
    if not settings.telegram_bot_token:
        logger.error("Telegram bot token not configured")
        return
        
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to send telegram message: {e}")

@router.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        update = await request.json()
        background_tasks.add_task(process_telegram_update, update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error parsing telegram update: {e}")
        return {"status": "error"}
