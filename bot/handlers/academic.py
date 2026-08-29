import os
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile

from services.ai_service import ai_service
from services.docx_generator import create_referat_docx
from services.pptx_generator import create_presentation_pptx

router = Router()


class AcademicStates(StatesGroup):
    waiting_for_referat_topic = State()
    waiting_for_slide_topic = State()


# REFERAT TUGMASI VA MANTIG'I
@router.callback_query(F.data == "btn_referat")
async def start_referat_flow(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "✍️ **Referat mavzusini kiriting:**\n"
        "(Masalan: *'Bulutli texnologiyalar va DevOps asoslari'* yoki *'O'zbekiston iqtisodiyoti taraqqiyoti'*)"
    )
    await state.set_state(AcademicStates.waiting_for_referat_topic)
    await callback.answer()


@router.message(AcademicStates.waiting_for_referat_topic)
async def process_referat_topic(message: types.Message, state: FSMContext):
    topic = message.text.strip()
    status_msg = await message.answer("⏳ Sun'iy intellekt akademik referatni shakllantirmoqda. Iltimos, kuting (10-15 soniya)...")
    
    try:
        # 1. AI orqali akademik tuzilma va matn yaratish
        data = await ai_service.generate_referat_structure(topic=topic)
        
        # 2. Word (.docx) faylini OTM talablarida shakllantirish
        output_dir = "/home/sanjar/talaba/storage/referats"
        os.makedirs(output_dir, exist_ok=True)
        file_path = f"{output_dir}/referat_{message.from_user.id}.docx"
        
        create_referat_docx(
            data=data,
            output_path=file_path,
            student_name=message.from_user.full_name
        )
        
        # 3. Faylni yuborish
        doc_file = FSInputFile(file_path, filename=f"{topic[:30]}_referat.docx")
        await message.answer_document(
            doc_file,
            caption=f"✅ **Referat tayyor!**\n\nMavzu: *{topic}*\nFormat: Word (.docx)\nStandart: Times New Roman 14, Titul varag'i, Reja, Xulosa va Adabiyotlar."
        )
        
        # Tozalash
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        await message.answer(f"❌ Referat tayyorlashda xatolik yuz berdi: {str(e)}")
    finally:
        await status_msg.delete()
        await state.clear()


# SLAYD TUGMASI VA MANTIG'I
@router.callback_query(F.data == "btn_slide")
async def start_slide_flow(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "📊 **Taqdimot (Slayd) mavzusini kiriting:**\n"
        "(Masalan: *'Kiberxavfsizlik asoslari'* yoki *'Sun'iy intellekt kelajagi'*)"
    )
    await state.set_state(AcademicStates.waiting_for_slide_topic)
    await callback.answer()


@router.message(AcademicStates.waiting_for_slide_topic)
async def process_slide_topic(message: types.Message, state: FSMContext):
    topic = message.text.strip()
    status_msg = await message.answer("⏳ Taqdimot slaydlari tayyorlanmoqda...")

    try:
        # 1. AI orqali slaydlar rejasini yaratish
        slides_data = await ai_service.generate_slides_data(topic=topic, slide_count=6)
        
        # 2. PowerPoint (.pptx) faylini yaratish
        output_dir = "/home/sanjar/talaba/storage/slides"
        os.makedirs(output_dir, exist_ok=True)
        file_path = f"{output_dir}/slide_{message.from_user.id}.pptx"
        
        create_presentation_pptx(
            slides_data=slides_data,
            topic=topic,
            output_path=file_path
        )
        
        # 3. Faylni yuborish
        doc_file = FSInputFile(file_path, filename=f"{topic[:30]}_taqdimot.pptx")
        await message.answer_document(
            doc_file,
            caption=f"✅ **Taqdimot tayyor!**\n\nMavzu: *{topic}*\nFormat: PowerPoint (.pptx)\nSlaydlar soni: {len(slides_data)}"
        )
        
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await message.answer(f"❌ Slayd tayyorlashda xatolik yuz berdi: {str(e)}")
    finally:
        await status_msg.delete()
        await state.clear()
