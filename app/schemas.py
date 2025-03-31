from pydantic import BaseModel

class AudioFileResponse(BaseModel):
    file_name: str
    message: str
