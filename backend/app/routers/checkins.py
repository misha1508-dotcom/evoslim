from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.checkin import CheckIn

router = APIRouter()


class CheckInCreate(BaseModel):
    workout_id: int
    sleep_quality: int = Field(..., ge=1, le=10)
    emotional_state: int = Field(..., ge=1, le=10)
    had_breakfast: bool = False
    had_coffee: bool = False
    notes: str | None = None


class CheckInOut(BaseModel):
    id: int
    workout_id: int
    sleep_quality: int
    emotional_state: int
    had_breakfast: bool
    had_coffee: bool
    notes: str | None
    model_config = {"from_attributes": True}


@router.post("", response_model=CheckInOut, status_code=201)
async def create_checkin(data: CheckInCreate, db: AsyncSession = Depends(get_db)):
    checkin = CheckIn(**data.model_dump())
    db.add(checkin)
    await db.commit()
    await db.refresh(checkin)
    return checkin


@router.get("/{workout_id}", response_model=CheckInOut)
async def get_checkin(workout_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(CheckIn).where(CheckIn.workout_id == workout_id)
    result = await db.execute(stmt)
    checkin = result.scalar_one_or_none()
    if not checkin:
        raise HTTPException(404, "Check-in not found for this workout")
    return checkin
