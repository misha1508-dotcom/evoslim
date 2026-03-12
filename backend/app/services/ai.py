import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
# Using a cost-effective but smart model as default
MODEL = "anthropic/claude-3-haiku"

async def get_ai_response(user_text: str, genetic_context: str | None, allergies_and_risks: str | None) -> str:
    if not settings.openrouter_api_key:
        logger.error("OpenRouter API key is missing")
        return "Извини, ИИ временно недоступен (не настроен API ключ)."
        
    system_prompt = (
        "Ты — профессиональный фитнес-тренер и нутрициолог Evoslim.\n"
        "Твоя цель — помогать пользователю с режимом тренировок, питания и сна. Общайся дружелюбно, профессионально и по делу.\n"
    )
    
    if genetic_context:
        system_prompt += f"\nГенетический контекст пользователя:\n{genetic_context}\n"
        
    if allergies_and_risks:
        system_prompt += (
            f"\nВАЖНО! Медицинские противопоказания и аллергии (Hard Guardrails):\n{allergies_and_risks}\n"
            "АКСИОМА: Тебе КАТЕГОРИЧЕСКИ ЗАПРЕЩАЕТСЯ рекомендовать что-либо, что нарушает эти медицинские ограничения. "
            "Если запрос пользователя противоречит его противопоказаниям, ты должен вежливо отказать и напомнить о рисках для здоровья."
        )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text}
    ]

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://krechet.space", 
        "X-Title": "Evoslim Telegram Bot"
    }
    
    payload = {
        "model": MODEL,
        "messages": messages
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(OPENROUTER_API_URL, json=payload, headers=headers, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling OpenRouter: {e}")
            return "Произошла ошибка при обращении к ИИ. Попробуй позже."

import json

async def parse_workout_from_text(user_text: str) -> dict | None:
    if not settings.openrouter_api_key:
        return None
        
    system_prompt = (
        "Ты — анализатор запросов на тренировки. Твоя единственная цель — составить план тренировки по запросу пользователя и вернуть его СТРОГО в формате JSON без какого-либо дополнительного текста.\n"
        "Если пользователь просит составить тренировку или день из сплита, верни JSON по следующей структуре:\n"
        "{\n"
        "  \"is_workout_proposal\": true,\n"
        "  \"exercises\": [\n"
        "    {\n"
        "      \"name\": \"Название упражнения\",\n"
        "      \"sets\": [\n"
        "        {\"weight_kg\": 0, \"reps\": 10, \"is_warmup\": false}\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "Указывай weight_kg=0 для всех подходов (пользователь сам впишет рабочий вес позже). Если пользователь ничего не просит по тренировке, верни {\"is_workout_proposal\": false}."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text}
    ]

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://krechet.space", 
        "X-Title": "Evoslim Telegram Bot"
    }
    
    payload = {
        "model": "anthropic/claude-3-haiku",
        "messages": messages,
        "response_format": {"type": "json_object"}
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(OPENROUTER_API_URL, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error parsing workout json: {e}")
            return None

async def parse_inbody_scan(base64_image: str) -> dict | None:
    if not settings.openrouter_api_key:
        return None
        
    system_prompt = (
        "Ты — специализированный анализатор медицинских и фитнес-бланков. "
        "Пользователь загружает фотографию распечатки InBody (биоимпедансный анализ тела). "
        "Тебе нужно найти на фото следующие параметры и вернуть их СТРОГО в формате JSON без какого-либо дополнительного текста.\n\n"
        "Структура JSON:\n"
        "{\n"
        "  \"weight_kg\": float,\n"
        "  \"skeletal_muscle_mass_kg\": float,\n"
        "  \"body_fat_mass_kg\": float,\n"
        "  \"total_body_water_l\": float,\n"
        "  \"protein_kg\": float,\n"
        "  \"minerals_kg\": float,\n"
        "  \"bmi\": float,\n"
        "  \"body_fat_percent\": float,\n"
        "  \"inbody_score\": int (общая оценка InBody, обычно от 70 до 100+),\n"
        "  \"visceral_fat_level\": int (уровень висцерального жира)\n"
        "}\n\n"
        "Если каких-то параметров не видно, ставь null. НЕ пиши никаких комментариев или объяснений, только чистый JSON."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user", 
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://krechet.space", 
        "X-Title": "Evoslim Telegram Bot"
    }
    
    payload = {
        "model": "anthropic/claude-3-opus-20240229",
        "messages": messages,
        "response_format": {"type": "json_object"}
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Opus could take slightly longer
            response = await client.post(OPENROUTER_API_URL, json=payload, headers=headers, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error parsing InBody image: {e}")
            return None
