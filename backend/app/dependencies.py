import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def validate_telegram_data(init_data: str, bot_token: str) -> dict:
    try:
        parsed_data = dict(parse_qsl(init_data))
        if "hash" not in parsed_data:
            return None

        received_hash = parsed_data.pop("hash")
        
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed_data.items())
        )
        
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()
        
        if calculated_hash != received_hash:
            return None
            
        if "user" in parsed_data:
            return json.loads(parsed_data["user"])
        return None
    except Exception:
        return None

async def get_current_user(
    auth_header: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
) -> User | None:
    # We won't block unauthenticated yet to not break everything locally,
    # but we will extract the User if authorized
    if not auth_header or not auth_header.startswith("tma "):
        return None
        
    init_data = auth_header[4:] # strip "tma "
    bot_token = settings.telegram_bot_token
    
    if not bot_token:
        # If no bot token, we can't validate. Just accept for dev/test?
        return None
        
    user_data = validate_telegram_data(init_data, bot_token)
    if not user_data or "id" not in user_data:
        # Invalid signature
        return None
        
    telegram_id = int(user_data["id"])
    username = user_data.get("username", "")
    
    # Get or create
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(telegram_id=telegram_id, username=username)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    return user

async def get_current_user_required(user: User | None = Depends(get_current_user)) -> User:
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user
