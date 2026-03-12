from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user_required

router = APIRouter()

class UserOut(BaseModel):
    id: int
    telegram_id: int | None
    username: str | None
    genetic_context: str | None
    allergies_and_risks: str | None

class UserUpdate(BaseModel):
    genetic_context: str | None = None
    allergies_and_risks: str | None = None

@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user_required)):
    return user

@router.patch("/me", response_model=UserOut)
async def update_me(
    data: UserUpdate,
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    if data.genetic_context is not None:
        user.genetic_context = data.genetic_context
    if data.allergies_and_risks is not None:
        user.allergies_and_risks = data.allergies_and_risks
    
    await db.commit()
    await db.refresh(user)
    return user
