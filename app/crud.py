import os

import httpx
from fastapi import HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy import select

from app.config import (
    TOKEN_URL,
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URI,
    USER_INFO_URL,
    AUTHORIZATION_URL,
)
from app.models import User, AudioFile

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=AUTHORIZATION_URL, tokenUrl=TOKEN_URL
)


async def authorization_service(code: str, db):
    """ Сервис авторизации """
    async with httpx.AsyncClient() as client:
        # Аутентификация пользователя
        token_response = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
            },
        )
        token_data = token_response.json()

        if "error" in token_data:
            raise HTTPException(status_code=400, detail=token_data["error"])

        # Получение информации о пользователе
        access_token = token_data["access_token"]
        user_response = await client.get(
            USER_INFO_URL, headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_response.json()

        # Сохранение токена в базе данных.
        db.add(
            User(
                user_id=user_info["id"],
                username=user_info["login"],
                access_token=access_token,
                refresh_token=token_data["refresh_token"],
            )
        )
        await db.commit()

        print(token_data)
        return user_info


async def refresh_token_service(code: str, db):
    """ Сервис обновления токена """
    user = await db.execute(select(User).where(User.access_token == code))
    user = user.scalars().one()
    ref_token = user.refresh_token

    # Запрос на обновления токена
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": ref_token,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
        )
        token_data = token_response.json()
        user.access_token = token_data["access_token"]
        await db.commit()

        if "error" in token_data:
            raise HTTPException(status_code=400, detail=token_data["error"])

        return token_data


async def get_user_service(code, db):
    """ Получение пользователя по токену """
    user = await db.execute(select(User).where(User.access_token == code))
    user = user.scalars().one()
    return user


async def update_user_service(code, login, db):
    """ Изменение логина """
    user = await db.execute(select(User).where(User.access_token == code))
    user = user.scalars().one()
    user.username = login
    await db.commit()
    return user.username


async def delete_user_service(code, login, db):
    """ Удаление пользователя (только с правами суперпользователя) """
    # Проверка прав суперпользователя
    admin = await db.execute(select(User).where(User.access_token == code))
    admin = admin.scalars().one()
    if admin.grade == "admin":
        user = await db.execute(select(User).where(User.username == login))
        user = user.scalars().one()
        if user:
            db.delete(user)
            await db.commit()
            return "User deleted"
        else:
            return "User not found"
    else:
        return "Insufficient privileges"


async def upload_audio_service(code, audio_file, file_name, db):
    """ Загрузка и сохранение аудиофайла """
    # Получение пользователя из базы данных
    user = await db.execute(select(User).where(User.access_token == code))
    user = user.scalars().one()

    # Создание пути для сохранения файла
    file_path = f"uploads/{user.username}/{file_name}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Сохранение содержимого файла
    with open(file_path, "wb") as f:
        contents = await audio_file.read()
        f.write(contents)

    # Сохранение информации о файле в базе данных
    audio_file_record = AudioFile(
        user_id=user.user_id, file_name=file_name, file_path=file_path
    )
    db.add(audio_file_record)
    await db.commit()


async def get_user_audio_files_service(code, db):
    """ Получение списка аудиофайлов пользователя """
    # Получение пользователя из базы данных
    user = await db.execute(select(User).where(User.access_token == code))
    user = user.scalars().one()

    audio_files = await db.execute(
        select(AudioFile).where(AudioFile.user_id == user.user_id)
    )
    audio_files = audio_files.scalars().all()

    file_info = [
        {"file_name": file.file_name, "file_path": file.file_path}
        for file in audio_files
    ]
    return file_info
