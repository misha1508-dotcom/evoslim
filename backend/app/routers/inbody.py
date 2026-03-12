import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.inbody import InBodyScan
from app.services.inbody_parser import parse_inbody_image

router = APIRouter()


class InBodyOut(BaseModel):
    id: int
    date: datetime | None
    weight_kg: float | None
    skeletal_muscle_mass_kg: float | None
    body_fat_mass_kg: float | None
    total_body_water_l: float | None
    protein_kg: float | None
    minerals_kg: float | None
    bmi: float | None
    body_fat_percent: float | None
    basal_metabolic_rate_kcal: int | None
    visceral_fat_level: int | None
    waist_hip_ratio: float | None
    fat_free_mass_kg: float | None
    obesity_degree_percent: float | None
    inbody_score: int | None
    ideal_weight_kg: float | None
    lean_mass_left_arm_kg: float | None
    lean_mass_right_arm_kg: float | None
    lean_mass_trunk_kg: float | None
    lean_mass_left_leg_kg: float | None
    lean_mass_right_leg_kg: float | None
    fat_mass_left_arm_kg: float | None
    fat_mass_right_arm_kg: float | None
    fat_mass_trunk_kg: float | None
    fat_mass_left_leg_kg: float | None
    fat_mass_right_leg_kg: float | None
    image_path: str | None
    notes: str | None
    model_config = {"from_attributes": True}


@router.post("/upload", response_model=InBodyOut, status_code=201)
async def upload_inbody(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    contents = await file.read()
    media_type = file.content_type or "image/jpeg"

    # Save image
    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "jpg"
    filename = f"inbody_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(settings.upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(contents)

    # Parse with Claude Vision
    parsed = await parse_inbody_image(contents, media_type)

    seg_lean = parsed.get("segmental_lean", {})
    seg_fat = parsed.get("segmental_fat", {})

    scan = InBodyScan(
        image_path=filename,
        raw_json=parsed,
        weight_kg=parsed.get("weight_kg"),
        skeletal_muscle_mass_kg=parsed.get("skeletal_muscle_mass_kg"),
        body_fat_mass_kg=parsed.get("body_fat_mass_kg"),
        total_body_water_l=parsed.get("total_body_water_l"),
        protein_kg=parsed.get("protein_kg"),
        minerals_kg=parsed.get("minerals_kg"),
        bmi=parsed.get("bmi"),
        body_fat_percent=parsed.get("body_fat_percent"),
        basal_metabolic_rate_kcal=parsed.get("basal_metabolic_rate_kcal"),
        visceral_fat_level=parsed.get("visceral_fat_level"),
        waist_hip_ratio=parsed.get("waist_hip_ratio"),
        fat_free_mass_kg=parsed.get("fat_free_mass_kg"),
        obesity_degree_percent=parsed.get("obesity_degree_percent"),
        inbody_score=parsed.get("inbody_score"),
        ideal_weight_kg=parsed.get("ideal_weight_kg"),
        lean_mass_left_arm_kg=seg_lean.get("left_arm_kg"),
        lean_mass_right_arm_kg=seg_lean.get("right_arm_kg"),
        lean_mass_trunk_kg=seg_lean.get("trunk_kg"),
        lean_mass_left_leg_kg=seg_lean.get("left_leg_kg"),
        lean_mass_right_leg_kg=seg_lean.get("right_leg_kg"),
        fat_mass_left_arm_kg=seg_fat.get("left_arm_kg"),
        fat_mass_right_arm_kg=seg_fat.get("right_arm_kg"),
        fat_mass_trunk_kg=seg_fat.get("trunk_kg"),
        fat_mass_left_leg_kg=seg_fat.get("left_leg_kg"),
        fat_mass_right_leg_kg=seg_fat.get("right_leg_kg"),
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    return scan


@router.get("", response_model=list[InBodyOut])
async def list_inbody(db: AsyncSession = Depends(get_db)):
    stmt = select(InBodyScan).order_by(InBodyScan.date.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{scan_id}", response_model=InBodyOut)
async def get_inbody(scan_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(InBodyScan).where(InBodyScan.id == scan_id)
    result = await db.execute(stmt)
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(404, "Scan not found")
    return scan


@router.get("/compare/{id1}/{id2}")
async def compare_inbody(id1: int, id2: int, db: AsyncSession = Depends(get_db)):
    stmt1 = select(InBodyScan).where(InBodyScan.id == id1)
    stmt2 = select(InBodyScan).where(InBodyScan.id == id2)
    r1 = await db.execute(stmt1)
    r2 = await db.execute(stmt2)
    s1 = r1.scalar_one_or_none()
    s2 = r2.scalar_one_or_none()
    if not s1 or not s2:
        raise HTTPException(404, "Scan not found")

    compare_fields = [
        "weight_kg", "skeletal_muscle_mass_kg", "body_fat_mass_kg",
        "body_fat_percent", "bmi", "fat_free_mass_kg",
        "basal_metabolic_rate_kcal", "visceral_fat_level", "inbody_score",
    ]
    # Fields where decrease = good
    decrease_good = {"weight_kg", "body_fat_mass_kg", "body_fat_percent", "bmi", "visceral_fat_level"}

    diffs = {}
    for field in compare_fields:
        v1 = getattr(s1, field, None)
        v2 = getattr(s2, field, None)
        if v1 is not None and v2 is not None:
            diff = round(v1 - v2, 2)
            if abs(diff) < 0.01:
                direction = "neutral"
            elif field in decrease_good:
                direction = "positive" if diff < 0 else "negative"
            else:
                direction = "positive" if diff > 0 else "negative"
            diffs[field] = {"scan1": v1, "scan2": v2, "diff": diff, "direction": direction}

    return {
        "scan1": InBodyOut.model_validate(s1),
        "scan2": InBodyOut.model_validate(s2),
        "comparison": diffs,
    }
