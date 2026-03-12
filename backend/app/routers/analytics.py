from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.analytics import (
    get_tonnage_by_day,
    get_exercise_progress,
    get_muscle_group_volume,
    get_checkin_correlation,
)

router = APIRouter()


@router.get("/tonnage")
async def tonnage(
    date_from: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    date_to: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db),
):
    return await get_tonnage_by_day(db, date_from, date_to)


@router.get("/effective-tonnage")
async def effective_tonnage(
    date_from: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    date_to: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db),
):
    data = await get_tonnage_by_day(db, date_from, date_to)
    return [{"date": d["date"], "workout_id": d["workout_id"], "effective_tonnage": d["effective_tonnage"]} for d in data]


@router.get("/exercise-progress/{exercise_id}")
async def exercise_progress(exercise_id: int, db: AsyncSession = Depends(get_db)):
    return await get_exercise_progress(db, exercise_id)


@router.get("/muscle-group-volume")
async def muscle_group_volume(
    date_from: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    date_to: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db),
):
    return await get_muscle_group_volume(db, date_from, date_to)


@router.get("/checkin-correlation")
async def checkin_correlation(db: AsyncSession = Depends(get_db)):
    return await get_checkin_correlation(db)
