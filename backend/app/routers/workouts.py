from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.workout import Workout, WorkoutExercise, WorkoutSet
from app.models.user import User
from app.dependencies import get_current_user, get_current_user_required

router = APIRouter()


# --- Schemas ---

class SetOut(BaseModel):
    id: int
    set_number: int
    weight_kg: float
    reps: int
    is_warmup: bool
    model_config = {"from_attributes": True}


class SetCreate(BaseModel):
    weight_kg: float
    reps: int
    is_warmup: bool = False


class WorkoutExerciseOut(BaseModel):
    id: int
    exercise_id: int
    order_index: int
    exercise_name: str | None = None
    sets: list[SetOut]
    model_config = {"from_attributes": True}


class WorkoutExerciseCreate(BaseModel):
    exercise_id: int
    order_index: int = 0


class WorkoutOut(BaseModel):
    id: int
    date: datetime | None
    started_at: datetime | None
    finished_at: datetime | None
    notes: str | None
    exercises: list[WorkoutExerciseOut]
    model_config = {"from_attributes": True}


class WorkoutCreate(BaseModel):
    notes: str | None = None


class WorkoutUpdate(BaseModel):
    finished_at: datetime | None = None
    notes: str | None = None


# --- Helpers ---

def _to_workout_out(w: Workout) -> dict:
    exercises = []
    for we in w.exercises:
        exercises.append({
            "id": we.id,
            "exercise_id": we.exercise_id,
            "order_index": we.order_index,
            "exercise_name": we.exercise.name if we.exercise else None,
            "sets": [SetOut.model_validate(s) for s in we.sets],
        })
    return {
        "id": w.id,
        "date": w.date,
        "started_at": w.started_at,
        "finished_at": w.finished_at,
        "notes": w.notes,
        "exercises": exercises,
    }


def _load_options():
    return [
        selectinload(Workout.exercises).selectinload(WorkoutExercise.sets),
        selectinload(Workout.exercises).selectinload(WorkoutExercise.exercise),
    ]


# --- Routes ---

@router.post("", status_code=201)
async def start_workout(
    data: WorkoutCreate, 
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user)
):
    workout = Workout(notes=data.notes, user_id=user.id if user else None)
    db.add(workout)
    await db.commit()
    await db.refresh(workout)
    return {"id": workout.id, "date": workout.date, "started_at": workout.started_at}


@router.get("")
async def list_workouts(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user)
):
    stmt = (
        select(Workout)
        .options(*_load_options())
        .order_by(Workout.date.desc())
        .limit(limit)
        .offset(offset)
    )
    if user:
        stmt = stmt.where(Workout.user_id == user.id)
    else:
        # Before returning all for unauthenticated, we could return empty or all. 
        # Leaving all for now so existing local UI keeps working if missing TMA auth.
        pass
    result = await db.execute(stmt)
    workouts = result.scalars().all()
    return [_to_workout_out(w) for w in workouts]


@router.get("/{workout_id}")
async def get_workout(workout_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Workout).where(Workout.id == workout_id).options(*_load_options())
    result = await db.execute(stmt)
    w = result.scalar_one_or_none()
    if not w:
        raise HTTPException(404, "Workout not found")
    return _to_workout_out(w)


@router.patch("/{workout_id}")
async def update_workout(workout_id: int, data: WorkoutUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Workout).where(Workout.id == workout_id)
    result = await db.execute(stmt)
    w = result.scalar_one_or_none()
    if not w:
        raise HTTPException(404, "Workout not found")
    if data.finished_at is not None:
        w.finished_at = data.finished_at
    if data.notes is not None:
        w.notes = data.notes
    await db.commit()
    return {"ok": True}

@router.post("/{workout_id}/start")
async def start_planned_workout(workout_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Workout).where(Workout.id == workout_id)
    result = await db.execute(stmt)
    w = result.scalar_one_or_none()
    if not w:
        raise HTTPException(404, "Workout not found")
    if w.started_at is None:
        from datetime import datetime, timezone
        w.started_at = datetime.now(timezone.utc)
        await db.commit()
    return {"ok": True}


@router.delete("/{workout_id}", status_code=204)
async def delete_workout(workout_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Workout).where(Workout.id == workout_id)
    result = await db.execute(stmt)
    w = result.scalar_one_or_none()
    if not w:
        raise HTTPException(404, "Workout not found")
    await db.delete(w)
    await db.commit()


# --- Workout exercises ---

@router.post("/{workout_id}/exercises", status_code=201)
async def add_exercise_to_workout(
    workout_id: int,
    data: WorkoutExerciseCreate,
    db: AsyncSession = Depends(get_db),
):
    we = WorkoutExercise(
        workout_id=workout_id,
        exercise_id=data.exercise_id,
        order_index=data.order_index,
    )
    db.add(we)
    await db.commit()
    await db.refresh(we)
    return {"id": we.id, "exercise_id": we.exercise_id, "order_index": we.order_index}


@router.delete("/{workout_id}/exercises/{we_id}", status_code=204)
async def remove_exercise_from_workout(
    workout_id: int, we_id: int, db: AsyncSession = Depends(get_db)
):
    stmt = select(WorkoutExercise).where(
        WorkoutExercise.id == we_id, WorkoutExercise.workout_id == workout_id
    )
    result = await db.execute(stmt)
    we = result.scalar_one_or_none()
    if not we:
        raise HTTPException(404, "Exercise not found in workout")
    await db.delete(we)
    await db.commit()


# --- Sets ---

@router.post("/{workout_id}/exercises/{we_id}/sets", status_code=201)
async def add_set(
    workout_id: int, we_id: int, data: SetCreate, db: AsyncSession = Depends(get_db)
):
    # Get current max set_number
    stmt = select(WorkoutSet).where(WorkoutSet.workout_exercise_id == we_id).order_by(WorkoutSet.set_number.desc())
    result = await db.execute(stmt)
    last = result.scalars().first()
    next_num = (last.set_number + 1) if last else 1

    s = WorkoutSet(
        workout_exercise_id=we_id,
        set_number=next_num,
        weight_kg=data.weight_kg,
        reps=data.reps,
        is_warmup=data.is_warmup,
    )
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return SetOut.model_validate(s)


@router.delete("/{workout_id}/exercises/{we_id}/sets/{set_id}", status_code=204)
async def delete_set(
    workout_id: int, we_id: int, set_id: int, db: AsyncSession = Depends(get_db)
):
    stmt = select(WorkoutSet).where(
        WorkoutSet.id == set_id, WorkoutSet.workout_exercise_id == we_id
    )
    result = await db.execute(stmt)
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(404, "Set not found")
    await db.delete(s)
    await db.commit()
