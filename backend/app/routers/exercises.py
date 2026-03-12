from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.exercise import Exercise, MuscleGroup, ExerciseType, Equipment
from app.models.workout import Workout, WorkoutExercise, WorkoutSet
from app.seed.exercises import EXERCISES as SEED_EXERCISES

router = APIRouter()


class ExerciseOut(BaseModel):
    id: int
    name: str
    name_en: str | None
    muscle_group: str
    secondary_muscles: list[str]
    exercise_type: str
    effectiveness_coefficient: float
    equipment: str
    is_custom: bool

    model_config = {"from_attributes": True}


class ExerciseCreate(BaseModel):
    name: str
    name_en: str | None = None
    muscle_group: MuscleGroup
    secondary_muscles: list[str] = []
    exercise_type: ExerciseType
    effectiveness_coefficient: float = 0.5
    equipment: Equipment = Equipment.barbell


@router.get("", response_model=list[ExerciseOut])
async def list_exercises(
    muscle_group: MuscleGroup | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Exercise).order_by(Exercise.muscle_group, Exercise.name)
    if muscle_group:
        stmt = stmt.where(Exercise.muscle_group == muscle_group)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/search", response_model=list[ExerciseOut])
async def search_exercises(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Exercise).where(
        Exercise.name.ilike(f"%{q}%") | Exercise.name_en.ilike(f"%{q}%")
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=ExerciseOut, status_code=201)
async def create_exercise(data: ExerciseCreate, db: AsyncSession = Depends(get_db)):
    exercise = Exercise(**data.model_dump(), is_custom=True)
    db.add(exercise)
    await db.commit()
    await db.refresh(exercise)
    return exercise


@router.get("/{exercise_id}/last-sets")
async def get_exercise_last_sets(
    exercise_id: int,
    exclude_workout: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Get the sets from the most recent workout containing this exercise."""
    stmt = (
        select(WorkoutExercise)
        .join(Workout)
        .where(WorkoutExercise.exercise_id == exercise_id)
        .options(selectinload(WorkoutExercise.sets))
        .order_by(Workout.date.desc())
        .limit(1)
    )
    if exclude_workout:
        stmt = stmt.where(Workout.id != exclude_workout)
    result = await db.execute(stmt)
    we = result.scalar_one_or_none()
    if not we:
        return []
    return [
        {"set_number": s.set_number, "weight_kg": s.weight_kg, "reps": s.reps, "is_warmup": s.is_warmup}
        for s in we.sets
    ]


@router.post("/seed", response_model=dict)
async def seed_exercises(db: AsyncSession = Depends(get_db)):
    """Seed the database with default exercises. Skips existing ones."""
    result = await db.execute(select(Exercise).where(Exercise.is_custom == False))
    existing = {e.name for e in result.scalars().all()}

    added = 0
    for ex_data in SEED_EXERCISES:
        if ex_data["name"] not in existing:
            exercise = Exercise(
                name=ex_data["name"],
                name_en=ex_data.get("name_en"),
                muscle_group=MuscleGroup(ex_data["muscle_group"]),
                secondary_muscles=ex_data.get("secondary_muscles", []),
                exercise_type=ExerciseType(ex_data["exercise_type"]),
                effectiveness_coefficient=ex_data.get("effectiveness_coefficient", 0.5),
                equipment=Equipment(ex_data.get("equipment", "barbell")),
                is_custom=False,
            )
            db.add(exercise)
            added += 1

    await db.commit()
    return {"added": added, "total_seed": len(SEED_EXERCISES)}
