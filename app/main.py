from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app.config import AUTHORIZATION_URL, CLIENT_ID, REDIRECT_URI
from app.crud import authorization_service
from app.database import create_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/login")
def login():
    return RedirectResponse(f"{AUTHORIZATION_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}")

@app.get("/auth")
async def authorization(code: str):
    return await authorization_service(code)


# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)