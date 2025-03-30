import httpx
from fastapi import HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer

from app.config import TOKEN_URL, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, USER_INFO_URL, AUTHORIZATION_URL

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=AUTHORIZATION_URL,
    tokenUrl=TOKEN_URL
)

async def authorization_service(code: str):
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            TOKEN_URL,
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': REDIRECT_URI
            }
        )
        token_data = token_response.json()

        if 'error' in token_data:
            raise HTTPException(status_code=400, detail=token_data['error'])

        # Получение информации о пользователе
        access_token = token_data['access_token']
        user_response = await client.get(USER_INFO_URL, headers={"Authorization": f"Bearer {access_token}"})
        user_info = user_response.json()

        return user_info
