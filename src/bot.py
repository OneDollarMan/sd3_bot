from telebot.async_telebot import AsyncTeleBot
from config import TELEGRAM_BOT_TOKEN
from db import get_async_session
from src.rpc import create_image_request_task
from src.service import register_user, request_image, get_user_by_chat_id, set_request_status_in_progress
from src.schemas import TelegramUserSchemaCreate, ImageRequestSchemaCreate, ImageRequestSchema

bot = AsyncTeleBot(TELEGRAM_BOT_TOKEN, parse_mode=None)


@bot.message_handler(commands=['start'])
async def send_welcome(message):
    async with get_async_session() as session:
        user = TelegramUserSchemaCreate(chat_id=message.chat.id, username=message.from_user.username)
        await register_user(session, user)
        await session.commit()
    await bot.send_message(message.chat.id, "Welcome! Write prompt to generate image")


@bot.message_handler(func=lambda m: True)
async def start_generating(message):
    async with get_async_session() as session:
        user = await get_user_by_chat_id(session, message.chat.id)
        if not user:
            await bot.reply_to(message, "Type /start to start using bot")
            return

        request_schema = ImageRequestSchemaCreate(prompt=message.text)
        request = await request_image(session, user, request_schema)
        await session.commit()

    if not request:
        await bot.reply_to(message, "You already have image in queue")
        return

    request = ImageRequestSchema.model_validate(request)
    await create_image_request_task(request)

    async with get_async_session() as session:
        await set_request_status_in_progress(session, request.id)
        await session.commit()

    await bot.reply_to(message, "Started generating, please wait")
