import asyncio
from src.bot import bot
from src.tasks import background_receive_messages


async def run_bot():
    await bot.polling()


async def run_tasks():
    await asyncio.create_task(background_receive_messages())


async def main():
    await asyncio.gather(
        run_tasks(),  # Запускаем фоновые задачи
        run_bot()  # Запускаем бота
    )


if __name__ == '__main__':
    asyncio.run(main())
