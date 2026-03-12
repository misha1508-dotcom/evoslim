from datetime import date, datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.workout import Workout, WorkoutExercise, WorkoutSet
from app.models.exercise import Exercise
from app.models.checkin import CheckIn


def calc_estimated_1rm(weight: float, reps: int) -> float:
    """Epley formula for estimated 1RM."""
    if reps <= 0:
        return 0.0
    if reps == 1:
        return weight
    return round(weight * (1 + reps / 30), 1)


async def get_tonnage_by_day(db: AsyncSession, date_from: date, date_to: date) -> list[dict]:
    stmt = (
        select(Workout)
        .where(func.date(Workout.date) >= date_from, func.date(Workout.date) <= date_to)
        .options(
            selectinload(Workout.exercises)
            .selectinload(WorkoutExercise.sets),
            selectinload(Workout.exercises)
            .selectinload(WorkoutExercise.exercise),
        )
        .order_by(Workout.date)
    )
    result = await db.execute(stmt)
    workouts = result.scalars().all()

    days = []
    for w in workouts:
        tonnage = 0.0
        effective_tonnage = 0.0
        for we in w.exercises:
            coeff = we.exercise.effectiveness_coefficient if we.exercise else 0.5
            for s in we.sets:
                if not s.is_warmup:
                    t = s.weight_kg * s.reps
                    tonnage += t
                    effective_tonnage += t * coeff
        days.append({
            "date": w.date.isoformat() if w.date else None,
            "workout_id": w.id,
            "tonnage": round(tonnage, 1),
            "effective_tonnage": round(effective_tonnage, 1),
        })
    return days


async def get_exercise_progress(db: AsyncSession, exercise_id: int) -> list[dict]:
    stmt = (
        select(WorkoutExercise)
        .where(WorkoutExercise.exercise_id == exercise_id)
        .options(
            selectinload(WorkoutExercise.sets),
            selectinload(WorkoutExercise.workout),
        )
        .join(Workout)
        .order_by(Workout.date)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()

    progress = []
    for we in items:
        working_sets = [s for s in we.sets if not s.is_warmup]
        if not working_sets:
            continue
        best_set = max(working_sets, key=lambda s: calc_estimated_1rm(s.weight_kg, s.reps))
        e1rm = calc_estimated_1rm(best_set.weight_kg, best_set.reps)
        total_volume = sum(s.weight_kg * s.reps for s in working_sets)
        progress.append({
            "date": we.workout.date.isoformat() if we.workout.date else None,
            "workout_id": we.workout_id,
            "best_weight": best_set.weight_kg,
            "best_reps": best_set.reps,
            "estimated_1rm": e1rm,
            "total_volume": round(total_volume, 1),
            "sets_count": len(working_sets),
        })
    return progress


async def get_muscle_group_volume(db: AsyncSession, date_from: date, date_to: date) -> list[dict]:
    stmt = (
        select(Workout)
        .where(func.date(Workout.date) >= date_from, func.date(Workout.date) <= date_to)
        .options(
            selectinload(Workout.exercises)
            .selectinload(WorkoutExercise.sets),
            selectinload(Workout.exercises)
            .selectinload(WorkoutExercise.exercise),
        )
    )
    result = await db.execute(stmt)
    workouts = result.scalars().all()

    volumes: dict[str, float] = {}
    for w in workouts:
        for we in w.exercises:
            if not we.exercise:
                continue
            mg = we.exercise.muscle_group.value if we.exercise.muscle_group else "other"
            vol = sum(s.weight_kg * s.reps for s in we.sets if not s.is_warmup)
            volumes[mg] = volumes.get(mg, 0) + vol

    return [{"muscle_group": k, "volume": round(v, 1)} for k, v in sorted(volumes.items(), key=lambda x: -x[1])]


async def get_checkin_correlation(db: AsyncSession) -> list[dict]:
    stmt = (
        select(Workout)
        .options(
            selectinload(Workout.checkin),
            selectinload(Workout.exercises)
            .selectinload(WorkoutExercise.sets),
            selectinload(Workout.exercises)
            .selectinload(WorkoutExercise.exercise),
        )
        .order_by(Workout.date)
    )
    result = await db.execute(stmt)
    workouts = result.scalars().all()

    data = []
    for w in workouts:
        if not w.checkin:
            continue
        tonnage = 0.0
        effective_tonnage = 0.0
        for we in w.exercises:
            coeff = we.exercise.effectiveness_coefficient if we.exercise else 0.5
            for s in we.sets:
                if not s.is_warmup:
                    t = s.weight_kg * s.reps
                    tonnage += t
                    effective_tonnage += t * coeff
        data.append({
            "date": w.date.isoformat() if w.date else None,
            "workout_id": w.id,
            "sleep_quality": w.checkin.sleep_quality,
            "emotional_state": w.checkin.emotional_state,
            "had_breakfast": w.checkin.had_breakfast,
            "had_coffee": w.checkin.had_coffee,
            "tonnage": round(tonnage, 1),
            "effective_tonnage": round(effective_tonnage, 1),
        })
    return data
