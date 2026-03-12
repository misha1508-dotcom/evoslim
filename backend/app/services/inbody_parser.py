import base64
import json

import anthropic

from app.config import settings

INBODY_PROMPT = """Проанализируй фото результата InBody. Извлеки ВСЕ числовые показатели и верни строго в JSON формате (без markdown, без ```json).

Обязательные поля:
{
  "weight_kg": число,
  "skeletal_muscle_mass_kg": число,
  "body_fat_mass_kg": число,
  "total_body_water_l": число,
  "protein_kg": число,
  "minerals_kg": число,
  "bmi": число,
  "body_fat_percent": число,
  "basal_metabolic_rate_kcal": число,
  "visceral_fat_level": число,
  "waist_hip_ratio": число или null,
  "fat_free_mass_kg": число,
  "obesity_degree_percent": число или null,
  "inbody_score": число,
  "ideal_weight_kg": число,
  "segmental_lean": {
    "left_arm_kg": число,
    "right_arm_kg": число,
    "trunk_kg": число,
    "left_leg_kg": число,
    "right_leg_kg": число
  },
  "segmental_fat": {
    "left_arm_kg": число,
    "right_arm_kg": число,
    "trunk_kg": число,
    "left_leg_kg": число,
    "right_leg_kg": число
  }
}

Если какой-то показатель не виден на фото, поставь null. Верни ТОЛЬКО валидный JSON, без комментариев."""


async def parse_inbody_image(image_bytes: bytes, media_type: str = "image/jpeg") -> dict:
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    b64 = base64.b64encode(image_bytes).decode("utf-8")

    message = await client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": INBODY_PROMPT,
                    },
                ],
            }
        ],
    )

    raw_text = message.content[0].text.strip()
    # Strip markdown fences if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

    return json.loads(raw_text)
