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
                
                # Ask AI if this is a workout log
                from app.services.ai import parse_workout_from_text
                workout_data = await parse_workout_from_text(text)
                added_workout_text = ""
                
                if workout_data and workout_data.get("is_workout_proposal"):
                    try:
                        from app.models.workout import Workout, WorkoutExercise, WorkoutSet
                        from app.models.exercise import Exercise, MuscleGroup, ExerciseType, Equipment
                        
                        # Create planned Workout
                        workout = Workout(user_id=user.id, started_at=None)
                        session.add(workout)
                        await session.flush()
                        
                        ex_index = 0
                        for ex_data in workout_data.get("exercises", []):
                            ex_name = ex_data.get("name", "Неизвестное упражнение")
                            
                            stmt_ex = select(Exercise).where(Exercise.name.ilike(f"%{ex_name}%"))
                            ex_result = await session.execute(stmt_ex)
                            db_exercise = ex_result.scalar_one_or_none()
                            
                            if not db_exercise:
                                db_exercise = Exercise(
                                    name=ex_name,
                                    muscle_group=MuscleGroup.other,
                                    exercise_type=ExerciseType.compound,
                                    equipment=Equipment.other,
                                    is_custom=True
                                )
                                session.add(db_exercise)
                                await session.flush()
                                
                            we = WorkoutExercise(workout_id=workout.id, exercise_id=db_exercise.id, order_index=ex_index)
                            session.add(we)
                            await session.flush()
                            
                            set_num = 1
                            for s_data in ex_data.get("sets", []):
                                w_set = WorkoutSet(
                                    workout_exercise_id=we.id,
                                    set_number=set_num,
                                    weight_kg=0.0,
                                    reps=int(s_data.get("reps", 0)),
                                    is_warmup=bool(s_data.get("is_warmup", False))
                                )
                                session.add(w_set)
                                set_num += 1
                                
                            ex_index += 1
                            
                        await session.commit()
                        added_workout_text = "\n\n✅ Тренировка составлена и сохранена! Открой Evoslim, чтобы начать ее."
                    except Exception as parse_e:
                        logger.error(f"Failed to save planned workout: {parse_e}")
                        await session.rollback()

                # Get AI response
                ai_reply = await get_ai_response(
                    user_text=text, 
                    genetic_context=user.genetic_context, 
                    allergies_and_risks=user.allergies_and_risks
                )
                
            await send_telegram_message(
                chat_id=chat_id, 
                text=ai_reply + added_workout_text,
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
