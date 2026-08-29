import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from core.config import settings
from bot.handlers.start import router as start_router
from bot.handlers.academic import router as academic_router

logging.basicConfig(level=logging.INFO)


async def main():
    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("DIQQAT: .env faylida BOT_TOKEN ko'rsatilmagan! Iltimos @BotFather dan olingan tokenni .env ga qo'ying.")
        return

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Routerlarni ro'yxatga olish
    dp.include_router(start_router)
    dp.include_router(academic_router)

    print("🚀 Talaba AI & HEMIS Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
