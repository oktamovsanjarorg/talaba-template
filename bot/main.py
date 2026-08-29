import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from core.config import settings
from core.database import engine, Base
from services.storage_cleaner import start_storage_cleaner_task
from bot.handlers.start import router as start_router
from bot.handlers.academic import router as academic_router
from bot.handlers.hemis import router as hemis_router

logging.basicConfig(level=logging.INFO)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Ma'lumotlar bazasi jadvallari tayyor.")


async def main():
    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("DIQQAT: .env faylida BOT_TOKEN ko'rsatilmagan!")
        return

    await init_db()

    # Diskni avtomatik tozalovchi fon jarayonini boshlash
    asyncio.create_task(start_storage_cleaner_task())

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(academic_router)
    dp.include_router(hemis_router)

    print("🚀 Talaba AI & HEMIS Monolith MVP muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
