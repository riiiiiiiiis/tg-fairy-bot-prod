
import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from app.handlers import router

async def main():
    print("🚀 Запуск Telegram бота...")
    bot = Bot(token=BOT_TOKEN)
    print("✅ Бот создан")
    dp = Dispatcher()
    dp.include_router(router)
    print("✅ Диспетчер настроен")
    print("🔄 Запуск polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("=" * 50)
    print("🎯 ЗАПУСК TYPES OF MAGIC BOT")
    print("=" * 50)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
