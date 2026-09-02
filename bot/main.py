import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from sqlalchemy import text

from core.config import settings
from core.database import engine, Base
from core.telemetry import start_metrics_server
from services.storage_cleaner import start_storage_cleaner_task
from bot.commands import setup_bot_commands
from bot.handlers.start import router as start_router
from bot.handlers.academic import router as academic_router
from bot.handlers.hemis import router as hemis_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db():
    """Ma'lumotlar bazasi jadvallarini yaratish va schema evolyutsiyasi"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Schema evolyutsiyasi (yangi ustunlar qo'shish)
        migrations = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_active TIMESTAMP DEFAULT NOW();",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS mustaqil_count INTEGER DEFAULT 0;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS quizzes_count INTEGER DEFAULT 0;",
        ]
        for sql in migrations:
            try:
                await conn.execute(text(sql))
            except Exception as e:
                logger.warning(f"Migratsiya ogohlantirishi: {e}")
    logger.info("✅ Ma'lumotlar bazasi jadvallari va migratsiyalar tayyor.")


async def on_startup_background_tasks():
    """Fon jarayonlarini xavfsiz ishga tushirish"""
    try:
        await start_storage_cleaner_task()
    except Exception as e:
        logger.error(f"Storage cleaner xatosi: {e}")


async def main():
    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("DIQQAT: .env faylida BOT_TOKEN ko'rsatilmagan!")
        return

    await init_db()

    # Prometheus metrikalari serverini ishga tushirish
    start_metrics_server(settings.PROMETHEUS_METRICS_PORT)

    # Redis orqali FSM saqlash (bot restart bo'lganda state saqlanadi)
    storage = RedisStorage.from_url(settings.REDIS_URL)
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    # Rasmiy buyruqlar menyusini Telegramga o'rnatish
    await setup_bot_commands(bot)

    dp.include_router(start_router)
    dp.include_router(academic_router)
    dp.include_router(hemis_router)

    # Diskni avtomatik tozalovchi fon jarayonini boshlash
    asyncio.create_task(on_startup_background_tasks())

    logger.info("🚀 Talaba AI & HEMIS bot to'liq ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
