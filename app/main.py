from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import Base, engine, create_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/main")
async def root():
    return {"message": "Hello, World!"}