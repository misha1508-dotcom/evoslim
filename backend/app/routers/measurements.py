from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.measurement import BodyMeasurement

router = APIRouter()


class MeasurementCreate(BaseModel):
    weight_kg: float | None = None
    chest_cm: float | None = None
    waist_cm: float | None = None
    hips_cm: float | None = None
    left_arm_cm: float | None = None
    right_arm_cm: float | None = None
    left_thigh_cm: float | None = None
    right_thigh_cm: float | None = None
    left_calf_cm: float | None = None
    right_calf_cm: float | None = None
    neck_cm: float | None = None
    shoulders_cm: float | None = None
    notes: str | None = None


class MeasurementOut(BaseModel):
    id: int
    date: datetime | None
    weight_kg: float | None
    chest_cm: float | None
    waist_cm: float | None
    hips_cm: float | None
    left_arm_cm: float | None
    right_arm_cm: float | None
    left_thigh_cm: float | None
    right_thigh_cm: float | None
    left_calf_cm: float | None
    right_calf_cm: float | None
    neck_cm: float | None
    shoulders_cm: float | None
    notes: str | None
    model_config = {"from_attributes": True}


MEASUREMENT_FIELDS = [
    "weight_kg", "chest_cm", "waist_cm", "hips_cm",
    "left_arm_cm", "right_arm_cm", "left_thigh_cm", "right_thigh_cm",
    "left_calf_cm", "right_calf_cm", "neck_cm", "shoulders_cm",
]

# Fields where decrease is positive progress
DECREASE_IS_GOOD = {"waist_cm"}


def compute_deltas(current: BodyMeasurement, previous: BodyMeasurement | None) -> dict:
    deltas = {}
    for field in MEASUREMENT_FIELDS:
        cur = getattr(current, field, None)
        prev = getattr(previous, field, None) if previous else None
        if cur is not None and prev is not None:
            diff = round(cur - prev, 1)
            if abs(diff) < 0.3:
                direction = "neutral"
            elif field in DECREASE_IS_GOOD:
                direction = "positive" if diff < 0 else "negative"
            else:
                direction = "positive" if diff > 0 else "negative"
            deltas[field] = {"diff": diff, "direction": direction}
        else:
            deltas[field] = None
    return deltas


@router.post("", response_model=MeasurementOut, status_code=201)
async def create_measurement(data: MeasurementCreate, db: AsyncSession = Depends(get_db)):
    m = BodyMeasurement(**data.model_dump())
    db.add(m)
    await db.commit()
    await db.refresh(m)
    return m


@router.get("")
async def list_measurements(db: AsyncSession = Depends(get_db)):
    stmt = select(BodyMeasurement).order_by(BodyMeasurement.date.desc())
    result = await db.execute(stmt)
    items = result.scalars().all()

    out = []
    for i, m in enumerate(items):
        prev = items[i + 1] if i + 1 < len(items) else None
        out.append({
            **MeasurementOut.model_validate(m).model_dump(),
            "deltas": compute_deltas(m, prev),
        })
    return out


@router.get("/latest")
async def get_latest_measurement(db: AsyncSession = Depends(get_db)):
    stmt = select(BodyMeasurement).order_by(BodyMeasurement.date.desc()).limit(2)
    result = await db.execute(stmt)
    items = result.scalars().all()
    if not items:
        raise HTTPException(404, "No measurements found")
    current = items[0]
    prev = items[1] if len(items) > 1 else None
    return {
        **MeasurementOut.model_validate(current).model_dump(),
        "deltas": compute_deltas(current, prev),
    }
