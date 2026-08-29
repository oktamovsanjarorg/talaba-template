import os
import time
import asyncio
import logging

logger = logging.getLogger(__name__)

STORAGE_DIRS = [
    "/app/storage/referats",
    "/app/storage/slides",
    "/app/storage/mustaqil",
    "/app/storage/quizzes"
]


async def start_storage_cleaner_task(max_age_seconds: int = 1800, check_interval_seconds: int = 600):
    """
    30 daqiqadan eski barcha vaqtinchalik DOCX/PPTX fayllarni avtomatik tozalab turuvchi fon jarayoni.
    """
    while True:
        try:
            now = time.time()
            deleted_count = 0
            for d in STORAGE_DIRS:
                if os.path.exists(d):
                    for fname in os.listdir(d):
                        fpath = os.path.join(d, fname)
                        if os.path.isfile(fpath):
                            if now - os.path.getmtime(fpath) > max_age_seconds:
                                try:
                                    os.remove(fpath)
                                    deleted_count += 1
                                except Exception as err:
                                    logger.warning(f"Faylni o'chirishda xatolik: {fpath} - {err}")
            if deleted_count > 0:
                logger.info(f"🧹 Disk tozalash: {deleted_count} ta eski vaqtinchalik fayl o'chirildi.")
        except Exception as e:
            logger.error(f"Storage cleaner xatosi: {e}")
        
        await asyncio.sleep(check_interval_seconds)
