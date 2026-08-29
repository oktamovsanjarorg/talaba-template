import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import text

from core.config import settings
from core.database import engine, Base
from services.storage_cleaner import start_storage_cleaner_task
from bot.commands import setup_bot_commands
from bot.handlers.start import router as start_router
from bot.handlers.academic import router as academic_router
from bot.handlers.hemis import router as hemis_router

logging.basicConfig(level=logging.INFO)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Avtomatik schema evolyutsiyasi (Migrations)
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_active TIMESTAMP DEFAULT NOW();"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS mustaqil_count INTEGER DEFAULT 0;"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS quizzes_count INTEGER DEFAULT 0;"))
    print("✅ Ma'lumotlar bazasi jadvallari va migratsiyalar tayyor.")


async def main():
    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("DIQQAT: .env faylida BOT_TOKEN ko'rsatilmagan!")
        return

    await init_db()

    # Diskni avtomatik tozalovchi fon jarayonini boshlash
    asyncio.create_task(start_storage_cleaner_task())

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Rasmiy buyruqlar menyusini Telegramga o'rnatish
    await setup_bot_commands(bot)

    dp.include_router(start_router)
    dp.include_router(academic_router)
    dp.include_router(hemis_router)

    print("🚀 Talaba AI & HEMIS Monolith MVP to'liq buyruqlar bilan ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
