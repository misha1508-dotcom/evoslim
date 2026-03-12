import logging
from fastapi import APIRouter, Request, BackgroundTasks
import httpx

from app.config import settings

from sqlalchemy import select
from app.database import async_session
from app.models.user import User
from app.services.ai import get_ai_response

router = APIRouter()
logger = logging.getLogger(__name__)

async def process_telegram_update(update: dict):
    if "message" in update:
        message = update["message"]
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        username = message.get("from", {}).get("username")
        
        if chat_id and text:
            # Notify user that we are thinking
            await send_telegram_chat_action(chat_id, "typing")
            
            async with async_session() as session:
                # Get or create user
                stmt = select(User).where(User.telegram_id == chat_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if not user:
                    user = User(telegram_id=chat_id, username=username)
                    session.add(user)
                    await session.commit()
                    await session.refresh(user)
                
                # Get AI response
                ai_reply = await get_ai_response(
                    user_text=text, 
                    genetic_context=user.genetic_context, 
                    allergies_and_risks=user.allergies_and_risks
                )
                
            await send_telegram_message(
                chat_id=chat_id, 
                text=ai_reply,
                reply_markup={
                    "inline_keyboard": [[{
                        "text": "📱 Открыть Evoslim",
                        "web_app": {"url": "https://krechet.space/training/"}
                    }]]
                } if text.startswith("/start") else None
            )

async def send_telegram_chat_action(chat_id: int, action: str):
    if not settings.telegram_bot_token:
        return
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendChatAction"
    payload = {"chat_id": chat_id, "action": action}
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload)
        except Exception:
            pass

async def send_telegram_message(chat_id: int, text: str, reply_markup: dict = None):
    if not settings.telegram_bot_token:
        logger.error("Telegram bot token not configured")
        return
        
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
        
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
