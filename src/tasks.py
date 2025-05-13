import base64
import datetime
import json

import aio_pika
import asyncio
from aio_pika.abc import AbstractIncomingMessage
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from config import RABBITMQ_URL, IMAGE_QUEUE_NAME
from db import get_async_session
from src.bot import bot
from src.models import ImageRequest
from src.schemas import ImageReceiveSchema


async def on_message(message: AbstractIncomingMessage) -> None:
    image = ImageReceiveSchema.model_validate(json.loads(message.body.decode()))
    async with get_async_session() as session:
        request = await session.execute(
            select(ImageRequest).filter(
                ImageRequest.id == image.id
            ).options(
                selectinload(ImageRequest.user)
            )
        )
        request = request.scalar()
        if not request:
            return

        request.status = ImageRequest.STATUS_FINISHED
        request.finished_at = datetime.datetime.now()
        await session.commit()

    await bot.send_photo(request.user.chat_id, base64.b64decode(image.img.encode()))
    await message.ack()


async def background_receive_messages():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)

    async with connection:
        channel = await connection.channel()

        queue = await channel.declare_queue(IMAGE_QUEUE_NAME, durable=True)

        await queue.consume(on_message)
        await asyncio.Future()



