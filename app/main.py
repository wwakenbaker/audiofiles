from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, File
from sqlalchemy.orm import Session
from starlette.datastructures import UploadFile
from starlette.responses import RedirectResponse

from app.config import AUTHORIZATION_URL, CLIENT_ID, REDIRECT_URI
from app.crud import authorization_service, refresh_token_service, get_user_service, update_user_service, \
    delete_user_service, upload_audio_service
from app.database import create_db, get_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/login")
def login():
    return RedirectResponse(f"{AUTHORIZATION_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}")

@app.get("/auth")
async def authorization(code: str, db: Session = Depends(get_session)):
    return await authorization_service(code, db)

@app.get("/refresh_token")
async def refresh_token(code: str, db: Session = Depends(get_session)):
    return await refresh_token_service(code, db)

@app.get('/user_info')
async def get_user(code: str, db: Session = Depends(get_session)):
    return await get_user_service(code, db)

@app.put('/user_info')
async def update_user(code: str, login: str, db: Session = Depends(get_session)):
    return await update_user_service(code, login, db)

@app.delete('/user_info')
async def delete_user(code: str, login: str, db: Session = Depends(get_session)):
    return await delete_user_service(code, login, db)


@app.post('/audio')
async def upload_audio(code: str, audio_file: UploadFile = File(...), file_name: str = None, db: Session = Depends(get_session)):
    result = await upload_audio_service(code, audio_file, file_name, db)
    return result

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)