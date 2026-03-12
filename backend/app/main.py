import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base
from app.routers import exercises, workouts, checkins, measurements, inbody, analytics, telegram


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    os.makedirs(settings.upload_dir, exist_ok=True)
    yield


app = FastAPI(title="Training Diary", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

app.include_router(exercises.router, prefix="/api/exercises", tags=["exercises"])
app.include_router(workouts.router, prefix="/api/workouts", tags=["workouts"])
app.include_router(checkins.router, prefix="/api/checkins", tags=["checkins"])
app.include_router(measurements.router, prefix="/api/measurements", tags=["measurements"])
app.include_router(inbody.router, prefix="/api/inbody", tags=["inbody"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(telegram.router, prefix="/api/telegram", tags=["telegram"])
app.include_router(users.router, prefix="/api/users", tags=["users"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
