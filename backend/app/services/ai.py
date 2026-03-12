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
