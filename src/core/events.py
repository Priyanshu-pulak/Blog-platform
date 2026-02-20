from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.database import Base, engine

@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    await engine.dispose()