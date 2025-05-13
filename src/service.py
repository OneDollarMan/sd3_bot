from typing import Optional

from sqlalchemy import select, Update
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import TelegramUser, ImageRequest
from src.schemas import TelegramUserSchemaCreate, ImageRequestSchemaCreate


async def get_user_by_chat_id(session: AsyncSession, chat_id: int) -> Optional[TelegramUser]:
    user = await session.execute(
        select(TelegramUser).filter(TelegramUser.chat_id == chat_id)
    )
    if user:
        return user.scalar()


async def is_user_has_image_in_queue(session: AsyncSession, user_id) -> bool:
    request = await session.execute(
        select(ImageRequest).filter(ImageRequest.user_id == user_id, ImageRequest.status != ImageRequest.STATUS_FINISHED)
    )
    return request.scalar()


async def register_user(session: AsyncSession, user_schema: TelegramUserSchemaCreate):
    if await get_user_by_chat_id(session, user_schema.chat_id):
        return

    user = TelegramUser(
        chat_id=user_schema.chat_id, username=user_schema.username
    )
    session.add(user)


async def request_image(
        session: AsyncSession,
        user: TelegramUser,
        request_schema: ImageRequestSchemaCreate
) -> Optional[ImageRequest]:
    if await is_user_has_image_in_queue(session, user.id):
        return

    request = ImageRequest(user=user, prompt=request_schema.prompt)
    session.add(request)
    await session.flush([request])
    await session.refresh(request)
    return request


async def set_request_status_in_progress(session: AsyncSession, request_id: int):
    await session.execute(
        Update(ImageRequest).filter(ImageRequest.id == request_id).values(status=ImageRequest.STATUS_IN_PROGRESS)
    )
