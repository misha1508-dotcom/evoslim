import asyncio
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, and_, or_
from app.database import async_session
from app.models.user import User

logger = logging.getLogger(__name__)

async def check_reminders_loop():
    logger.info("Started reminder background loop")
    while True:
        try:
            await send_due_reminders()
        except Exception as e:
            logger.error(f"Error in reminder loop: {e}")
        # Run once a day
        await asyncio.sleep(86400)

async def send_due_reminders():
    # 14 days ago
    two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14)
    
    async with async_session() as session:
        # Find users who haven't been asked in 14 days, or have never been asked but were created 14+ days ago
        stmt = select(User).where(
            or_(
                and_(
                    User.last_measurements_request != None,
                    User.last_measurements_request < two_weeks_ago
                ),
                and_(
                    User.last_measurements_request == None,
                    User.created_at < two_weeks_ago
                )
            )
        )
        result = await session.execute(stmt)
        users = result.scalars().all()
        
        from app.routers.telegram import send_telegram_message
        
        for user in users:
            try:
                msg = (
                    "👋 Привет! Прошло 2 недели с нашего последнего чекапа.\n\n"
                    "Пожалуйста, пришли мне свежие данные, чтобы я мог скорректировать твой план:\n"
                    "1. Твой текущий вес\n"
                    "2. Обхваты: грудь талия бедра (в см)\n"
                    "3. Фото в зеркале для отслеживания прогресса\n"
                    "4. Скриншот из Apple Health \n\n"
                    "Жду твоих результатов! 💪"
                )
                await send_telegram_message(user.telegram_id, msg)
                
                # Update timestamp
                user.last_measurements_request = datetime.now(timezone.utc)
                await session.flush()
                
            except Exception as e:
                logger.error(f"Failed to send reminder to user {user.id}: {e}")
                
        if users:
            await session.commit()
