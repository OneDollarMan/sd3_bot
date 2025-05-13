from typing import Optional
from pydantic import BaseModel, ConfigDict


class TelegramUserSchemaCreate(BaseModel):
    chat_id: int
    username: Optional[str]


class ImageRequestSchemaCreate(BaseModel):
    prompt: str


class ImageRequestSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    prompt: str


class ImageReceiveSchema(BaseModel):
    id: int
    img: str
