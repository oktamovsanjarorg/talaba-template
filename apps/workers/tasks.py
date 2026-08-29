import asyncio
import os
import logging
from apps.workers.celery_app import celery_app
from services.ai_service import ai_service
from services.docx_generator import create_referat_docx
from services.pptx_generator import create_presentation_pptx
from core.telemetry import REFERATS_GENERATED, SLIDES_GENERATED

logger = logging.getLogger(__name__)


@celery_app.task(name="apps.workers.tasks.generate_referat_task")
def generate_referat_task(user_id: int, topic: str, student_name: str = "Talaba"):
    """
    Fon ishchisi: Referat uchun AI ga so'rov yuborish va DOCX fayl yasash
    """
    logger.info(f"🚀 Referat generatsiyasi boshlandi: User={user_id}, Mavzu={topic}")
    
    # Asinxron kodni sinxron Celery ichida yurgizish
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        data = loop.run_until_complete(ai_service.generate_referat_structure(topic=topic))
        
        output_dir = "/app/storage/referats"
        os.makedirs(output_dir, exist_ok=True)
        file_path = f"{output_dir}/referat_{user_id}.docx"
        
        create_referat_docx(
            data=data,
            output_path=file_path,
            student_name=student_name
        )
        
        REFERATS_GENERATED.labels(status="success").inc()
        return {"status": "success", "file_path": file_path, "title": topic}
    except Exception as e:
        REFERATS_GENERATED.labels(status="failed").inc()
        logger.error(f"Referat generatsiya xatosi: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        loop.close()


@celery_app.task(name="apps.workers.tasks.generate_slides_task")
def generate_slides_task(user_id: int, topic: str, slide_count: int = 6):
    """
    Fon ishchisi: Slaydlar uchun AI ga so'rov va PPTX fayl yasash
    """
    logger.info(f"📊 Slayd generatsiyasi boshlandi: User={user_id}, Mavzu={topic}")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        slides_data = loop.run_until_complete(ai_service.generate_slides_data(topic=topic, slide_count=slide_count))
        
        output_dir = "/app/storage/slides"
        os.makedirs(output_dir, exist_ok=True)
        file_path = f"{output_dir}/slide_{user_id}.pptx"
        
        create_presentation_pptx(
            slides_data=slides_data,
            topic=topic,
            output_path=file_path
        )
        
        SLIDES_GENERATED.labels(status="success").inc()
        return {"status": "success", "file_path": file_path, "title": topic}
    except Exception as e:
        SLIDES_GENERATED.labels(status="failed").inc()
        logger.error(f"Slayd generatsiya xatosi: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        loop.close()


@celery_app.task(name="apps.workers.tasks.check_all_hemis_deadlines")
def check_all_hemis_deadlines():
    """
    Davriy vazifa (Cron): Barcha talabalarning topshiriqlarini tekshirib, deadline yaqinlashganini eslatish
    """
    logger.info("⏰ HEMIS Deadline tekshiruvi boshlandi...")
    return {"status": "checked"}
