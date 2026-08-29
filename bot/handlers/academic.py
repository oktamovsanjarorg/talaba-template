import os
import asyncio
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.ai_service import ai_service
from services.docx_generator import create_referat_docx
from services.pptx_generator import create_presentation_pptx

router = Router()


class AcademicStates(StatesGroup):
    waiting_for_referat_topic = State()
    waiting_for_slide_topic = State()
    waiting_for_slide_count = State()


def get_cancel_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Bekor qilish", callback_data="btn_main_menu")
    return kb.as_markup()


# ================= REFERAT TAYYORLASH =================
@router.callback_query(F.data == "btn_referat")
async def start_referat_flow(callback: types.CallbackQuery, state: FSMContext):
    text = (
        "📝 **Akademik Referat tayyorlash**\n\n"
        "Iltimos, referat mavzusini kiriting.\n"
        "💡 *Maslahat: Mavzuni qanchalik aniq yozsangiz, referat shunchalik mukammal chiqadi.*\n\n"
        "📌 *Misol:* `Bulutli hisoblash texnologiyalari va DevOps asoslari`"
    )
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
    await state.set_state(AcademicStates.waiting_for_referat_topic)
    await callback.answer()


@router.message(AcademicStates.waiting_for_referat_topic)
async def process_referat_topic(message: types.Message, state: FSMContext):
    topic = message.text.strip()
    
    if len(topic) < 3:
        await message.answer("⚠️ Mavzu juda qisqa. Iltimos, to'liqroq mavzu kiriting:", reply_markup=get_cancel_keyboard())
        return

    # 1-bosqich: Boshlash
    status_msg = await message.answer("⏳ **[1/3]** Mavzu tahlil qilinmoqda va akademik reja tuzilmoqda...")
    
    try:
        # 2-bosqich: Matn yaratish
        await asyncio.sleep(1)
        await status_msg.edit_text("⏳ **[2/3]** Qwen AI orqali boblar va ilmiy xulosalar yozilmoqda...")
        data = await ai_service.generate_referat_structure(topic=topic)
        
        # 3-bosqich: Fayl shakllantirish
        await status_msg.edit_text("⏳ **[3/3]** Titul varag'i va rasmiy Word (.docx) standarti shakllantirilmoqda...")
        output_dir = "/app/storage/referats"
        os.makedirs(output_dir, exist_ok=True)
        file_path = f"{output_dir}/referat_{message.from_user.id}.docx"
        
        create_referat_docx(
            data=data,
            output_path=file_path,
            student_name=message.from_user.full_name
        )
        
        # Tugmalar
        kb = InlineKeyboardBuilder()
        kb.button(text="📊 Shu mavzuda Slayd yasash", callback_data=f"fast_slide_{topic[:25]}")
        kb.button(text="📝 Yangi referat", callback_data="btn_referat")
        kb.button(text="🏠 Asosiy menyu", callback_data="btn_main_menu")
        kb.adjust(1)

        doc_file = FSInputFile(file_path, filename=f"{topic[:30]}_referat.docx")
        await message.answer_document(
            doc_file,
            caption=(
                f"🎉 **Referat muvaffaqiyatli tayyorlandi!**\n\n"
                f"📌 **Mavzu:** *{topic}*\n"
                f"📄 **Format:** Word (.docx)\n"
                f"📐 **Standart:** Times New Roman 14, 1.5 interval, Titul varag'i, Mundarija, Boblar, Xulosa va Adabiyotlar."
            ),
            reply_markup=kb.as_markup(),
            parse_mode="Markdown"
        )
        
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}\nIltimos, qaytadan urinib ko'ring.", reply_markup=get_cancel_keyboard())
    finally:
        try:
            await status_msg.delete()
        except Exception:
            pass
        await state.clear()


# ================= SLAYD TAYYORLASH =================
@router.callback_query(F.data == "btn_slide")
async def start_slide_flow(callback: types.CallbackQuery, state: FSMContext):
    text = (
        "📊 **Taqdimot (PowerPoint Slayd) tayyorlash**\n\n"
        "Iltimos, taqdimot mavzusini kiriting:\n\n"
        "📌 *Misol:* `Sun'iy intellekt va uning zamonaviy kasblarga ta'siri`"
    )
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
    await state.set_state(AcademicStates.waiting_for_slide_topic)
    await callback.answer()


@router.message(AcademicStates.waiting_for_slide_topic)
async def process_slide_topic(message: types.Message, state: FSMContext):
    topic = message.text.strip()
    await state.update_data(slide_topic=topic)
    
    kb = InlineKeyboardBuilder()
    kb.button(text="5 ta slayd (Qisqa)", callback_data="slide_count_5")
    kb.button(text="8 ta slayd (O'rtacha)", callback_data="slide_count_8")
    kb.button(text="10 ta slayd (Katta)", callback_data="slide_count_10")
    kb.button(text="❌ Bekor qilish", callback_data="btn_main_menu")
    kb.adjust(1)

    await message.answer(
        f"📊 Mavzu: *{topic}*\n\nNechta slayddan iborat taqdimot tayyorlansin?",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )
    await state.set_state(AcademicStates.waiting_for_slide_count)


@router.callback_query(F.data.startswith("slide_count_"))
async def process_slide_count_and_generate(callback: types.CallbackQuery, state: FSMContext):
    count = int(callback.data.split("_")[-1])
    data = await state.get_data()
    topic = data.get("slide_topic", "Taqdimot")

    status_msg = await callback.message.answer(f"⏳ **[1/2]** {count} ta slayd uchun professional tezislar tuzilmoqda...")
    await callback.answer()

    try:
        slides_data = await ai_service.generate_slides_data(topic=topic, slide_count=count)
        
        await status_msg.edit_text("⏳ **[2/2]** 16:9 zamonaviy PowerPoint (.pptx) fayli chizilmoqda...")
        output_dir = "/app/storage/slides"
        os.makedirs(output_dir, exist_ok=True)
        file_path = f"{output_dir}/slide_{callback.from_user.id}.pptx"
        
        create_presentation_pptx(
            slides_data=slides_data,
            topic=topic,
            output_path=file_path
        )
        
        kb = InlineKeyboardBuilder()
        kb.button(text="📝 Shu mavzuda Referat yozish", callback_data="btn_referat")
        kb.button(text="📊 Yangi slayd", callback_data="btn_slide")
        kb.button(text="🏠 Asosiy menyu", callback_data="btn_main_menu")
        kb.adjust(1)

        doc_file = FSInputFile(file_path, filename=f"{topic[:30]}_taqdimot.pptx")
        await callback.message.answer_document(
            doc_file,
            caption=(
                f"🎉 **Taqdimot tayyor!**\n\n"
                f"📌 **Mavzu:** *{topic}*\n"
                f"📊 **Slaydlar:** {len(slides_data)} ta\n"
                f"🖥 **Format:** 16:9 Widescreen (.pptx)"
            ),
            reply_markup=kb.as_markup(),
            parse_mode="Markdown"
        )
        
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await callback.message.answer(f"❌ Slayd tayyorlashda xatolik: {str(e)}", reply_markup=get_cancel_keyboard())
    finally:
        try:
            await status_msg.delete()
        except Exception:
            pass
        await state.clear()
