from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str

class UserResponse(BaseModel):
    user_id: int
    username: str

    class Config:
        orm_mode = True

class AudioFileResponse(BaseModel):
    file_id: int
    file_path: str