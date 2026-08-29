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
from services.mustaqil_ish_generator import create_mustaqil_ish_docx
from services.quiz_generator import create_quiz_docx
from services.user_service import user_service

router = Router()


class AcademicStates(StatesGroup):
    waiting_for_referat_topic = State()
    waiting_for_slide_topic = State()
    waiting_for_slide_count = State()
    waiting_for_mustaqil_topic = State()
    waiting_for_quiz_topic = State()
    waiting_for_summary_text = State()


def get_cancel_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Bekor qilish", callback_data="btn_main_menu")
    return kb.as_markup()


# ================= 1. REFERAT TAYYORLASH =================
@router.callback_query(F.data == "btn_referat")
async def start_referat_flow(callback: types.CallbackQuery, state: FSMContext):
    text = (
        "📝 **Akademik Referat tayyorlash**\n\n"
        "Iltimos, referat mavzusini kiriting.\n"
        "💡 *Maslahat: Mavzuni qanchalik aniq yozsangiz, referat shunchalik mukammal chiqadi.*\n\n"
        "📌 *Misol:* `O'zbekistonda raqamli iqtisodiyotni rivojlantirish istiqbollari`"
    )
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
    await state.set_state(AcademicStates.waiting_for_referat_topic)
    await callback.answer()


@router.message(AcademicStates.waiting_for_referat_topic)
async def process_referat_topic(message: types.Message, state: FSMContext):
    topic = message.text.strip()
    if len(topic) < 3:
        await message.answer("⚠️ Mavzu juda qisqa. To'liqroq mavzu kiriting:", reply_markup=get_cancel_keyboard())
        return

    status_msg = await message.answer("⏳ **[1/3]** Mavzu tahlil qilinmoqda va akademik reja tuzilmoqda...")
    try:
        await asyncio.sleep(1)
        await status_msg.edit_text("⏳ **[2/3]** Akademik boblar va ilmiy matn yozilmoqda...")
        data = await ai_service.generate_referat_structure(topic=topic)
        
        await status_msg.edit_text("⏳ **[3/3]** Titul varag'i va rasmiy Word (.docx) shakllantirilmoqda...")
        output_dir = "/app/storage/referats"
        os.makedirs(output_dir, exist_ok=True)
        file_path = f"{output_dir}/referat_{message.from_user.id}.docx"
        
        create_referat_docx(
            data=data,
            output_path=file_path,
            student_name=message.from_user.full_name
        )
        
        await user_service.record_generation(message.from_user.id, "referat", topic, "success")

        kb = InlineKeyboardBuilder()
        kb.button(text="📊 Shu mavzuda Slayd yasash", callback_data="btn_slide")
        kb.button(text="🎯 Testlar tuzish", callback_data="btn_quiz")
        kb.button(text="🏠 Asosiy menyu", callback_data="btn_main_menu")
        kb.adjust(1)

        doc_file = FSInputFile(file_path, filename=f"{topic[:30]}_referat.docx")
        await message.answer_document(
            doc_file,
            caption=(
                f"🎉 **Referat muvaffaqiyatli tayyorlandi!**\n\n"
                f"📌 **Mavzu:** *{topic}*\n"
                f"📄 **Format:** Word (.docx)\n"
                f"📐 **Standart:** Times New Roman 14, 1.5 interval, Titul, Mundarija, Boblar, Xulosa va Adabiyotlar."
            ),
            reply_markup=kb.as_markup(),
            parse_mode="Markdown"
        )
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        await user_service.record_generation(message.from_user.id, "referat", topic, "failed")
        await message.answer(f"❌ Xatolik: {str(e)}", reply_markup=get_cancel_keyboard())
    finally:
        try:
            await status_msg.delete()
        except Exception:
            pass
        await state.clear()


# ================= 2. SLAYD (PPTX) TAYYORLASH =================
@router.callback_query(F.data == "btn_slide")
async def start_slide_flow(callback: types.CallbackQuery, state: FSMContext):
    text = (
        "📊 **Taqdimot (PowerPoint Slayd) tayyorlash**\n\n"
        "Iltimos, taqdimot mavzusini kiriting:\n\n"
        "📌 *Misol:* `Sun'iy intellekt va axborot xavfsizligi`"
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
async def process_slide_count(callback: types.CallbackQuery, state: FSMContext):
    count = int(callback.data.split("_")[-1])
    data = await state.get_data()
    topic = data.get("slide_topic", "Taqdimot")

    status_msg = await callback.message.answer(f"⏳ **[1/2]** {count} ta slayd uchun professional tezislar tuzilmoqda...")
    await callback.answer()

    try:
        slides_data = await ai_service.generate_slides_data(topic=topic, slide_count=count)
        await status_msg.edit_text("⏳ **[2/2]** 16:9 zamonaviy PowerPoint (.pptx) fayli shakllantirilmoqda...")
        
        output_dir = "/app/storage/slides"
        os.makedirs(output_dir, exist_ok=True)
        file_path = f"{output_dir}/slide_{callback.from_user.id}.pptx"
        
        create_presentation_pptx(slides_data=slides_data, topic=topic, output_path=file_path, student_name=callback.from_user.full_name)
        await user_service.record_generation(callback.from_user.id, "slide", topic, "success")
        
        kb = InlineKeyboardBuilder()
        kb.button(text="📝 Shu mavzuda Referat yozish", callback_data="btn_referat")
        kb.button(text="🏠 Asosiy menyu", callback_data="btn_main_menu")
        kb.adjust(1)

        doc_file = FSInputFile(file_path, filename=f"{topic[:30]}_taqdimot.pptx")
        await callback.message.answer_document(
            doc_file,
            caption=f"🎉 **Taqdimot tayyor!**\n\n📌 **Mavzu:** *{topic}*\n📊 **Slaydlar:** {len(slides_data)} ta\n🖥 **Format:** 16:9 Widescreen (.pptx)",
            reply_markup=kb.as_markup(),
            parse_mode="Markdown"
        )
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        await user_service.record_generation(callback.from_user.id, "slide", topic, "failed")
        await callback.message.answer(f"❌ Xatolik: {str(e)}", reply_markup=get_cancel_keyboard())
    finally:
        try:
            await status_msg.delete()
        except Exception:
            pass
        await state.clear()


# ================= 3. MUSTAQIL ISH TAYYORLASH =================
@router.callback_query(F.data == "btn_mustaqil")
async def start_mustaqil_flow(callback: types.CallbackQuery, state: FSMContext):
    text = (
        "📑 **Mustaqil Ta'lim Ishi tayyorlash**\n\n"
        "Mustaqil ish mavzusini kiriting:\n\n"
        "📌 *Misol:* `Mikroiqtisodiyotda talab va taklif qonunlari tahlili`"
    )
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
    await state.set_state(AcademicStates.waiting_for_mustaqil_topic)
    await callback.answer()


@router.message(AcademicStates.waiting_for_mustaqil_topic)
async def process_mustaqil_topic(message: types.Message, state: FSMContext):
    topic = message.text.strip()
    status_msg = await message.answer("⏳ Mustaqil ta'lim ishi OTM talablari asosida tuzilmoqda...")

    try:
        data = await ai_service.generate_mustaqil_ish_structure(topic=topic)
        output_dir = "/app/storage/mustaqil"
        os.makedirs(output_dir, exist_ok=True)
        file_path = f"{output_dir}/mustaqil_{message.from_user.id}.docx"

        create_mustaqil_ish_docx(data=data, output_path=file_path, student_name=message.from_user.full_name)
        await user_service.record_generation(message.from_user.id, "mustaqil", topic, "success")

        kb = InlineKeyboardBuilder()
        kb.button(text="🏠 Asosiy menyu", callback_data="btn_main_menu")

        doc_file = FSInputFile(file_path, filename=f"{topic[:30]}_mustaqil_ish.docx")
        await message.answer_document(
            doc_file,
            caption=f"🎉 **Mustaqil ish tayyor!**\n\n📌 **Mavzu:** *{topic}*\n📄 **Format:** Word (.docx)\nStandart: Maqsad, Nazariy qism, Amaliy tahlil va Xulosa.",
            reply_markup=kb.as_markup(),
            parse_mode="Markdown"
        )
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        await user_service.record_generation(message.from_user.id, "mustaqil", topic, "failed")
        await message.answer(f"❌ Xatolik: {str(e)}", reply_markup=get_cancel_keyboard())
    finally:
        try:
            await status_msg.delete()
        except Exception:
            pass
        await state.clear()


# ================= 4. TEST (QUIZ) TUZISH =================
@router.callback_query(F.data == "btn_quiz")
async def start_quiz_flow(callback: types.CallbackQuery, state: FSMContext):
    text = (
        "🎯 **Test va Nazorat Savollari tuzish**\n\n"
        "Qaysi mavzu yoki fan bo'yicha test savollari tuzilsin?\n\n"
        "📌 *Misol:* `O'zbekiston tarixi` yoki `Python dasturlash asoslari`"
    )
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
    await state.set_state(AcademicStates.waiting_for_quiz_topic)
    await callback.answer()


@router.message(AcademicStates.waiting_for_quiz_topic)
async def process_quiz_topic(message: types.Message, state: FSMContext):
    topic = message.text.strip()
    status_msg = await message.answer("⏳ 4 variantli test savollari va javoblar kaliti shakllantirilmoqda...")

    try:
        quiz_data = await ai_service.generate_quiz_data(topic=topic, count=6)
        output_dir = "/app/storage/quizzes"
        os.makedirs(output_dir, exist_ok=True)
        file_path = f"{output_dir}/quiz_{message.from_user.id}.docx"

        create_quiz_docx(quiz_data=quiz_data, topic=topic, output_path=file_path)
        await user_service.record_generation(message.from_user.id, "quiz", topic, "success")

        kb = InlineKeyboardBuilder()
        kb.button(text="🎯 Yangi test", callback_data="btn_quiz")
        kb.button(text="🏠 Asosiy menyu", callback_data="btn_main_menu")
        kb.adjust(1)

        doc_file = FSInputFile(file_path, filename=f"{topic[:30]}_testlar.docx")
        await message.answer_document(
            doc_file,
            caption=f"🎉 **Testlar to'plami tayyor!**\n\n📌 **Mavzu:** *{topic}*\n🎯 **Savollar:** {len(quiz_data)} ta (Javoblar kaliti bilan birga).",
            reply_markup=kb.as_markup(),
            parse_mode="Markdown"
        )

        if quiz_data:
            first_q = quiz_data[0]
            await message.answer_poll(
                question=f"1-namuna savol: {first_q.get('question')[:250]}",
                options=first_q.get("options")[:4],
                type="quiz",
                correct_option_id=first_q.get("correct_index", 0),
                explanation=first_q.get("explanation", "")[:200],
                is_anonymous=False
            )

        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        await user_service.record_generation(message.from_user.id, "quiz", topic, "failed")
        await message.answer(f"❌ Xatolik: {str(e)}", reply_markup=get_cancel_keyboard())
    finally:
        try:
            await status_msg.delete()
        except Exception:
            pass
        await state.clear()


# ================= 5. KONSPEKT & XULOSA =================
@router.callback_query(F.data == "btn_summary")
async def start_summary_flow(callback: types.CallbackQuery, state: FSMContext):
    text = (
        "💡 **Aqlli Konspekt va Matnni qisqartirish**\n\n"
        "Konspekt qilmoqchi bo'lgan uzun matn, leksiya yoki maqolani botga yuboring:"
    )
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
    await state.set_state(AcademicStates.waiting_for_summary_text)
    await callback.answer()


@router.message(AcademicStates.waiting_for_summary_text)
async def process_summary_text(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if len(text) < 30:
        await message.answer("⚠️ Matn juda qisqa. Kamida 2-3 jumlali matn kiriting:", reply_markup=get_cancel_keyboard())
        return

    status_msg = await message.answer("⏳ Matn tahlil qilinib, asosiy xulosalar konspekt qilinmoqda...")
    try:
        summary = await ai_service.summarize_text(text)
        await user_service.record_generation(message.from_user.id, "summary", text[:50], "success")

        kb = InlineKeyboardBuilder()
        kb.button(text="🏠 Asosiy menyu", callback_data="btn_main_menu")

        await message.answer(
            f"📑 **Mavzu bo'yicha Konspekt va Asosiy Xulosalar:**\n\n{summary}",
            reply_markup=kb.as_markup(),
            parse_mode="Markdown"
        )
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}", reply_markup=get_cancel_keyboard())
    finally:
        try:
            await status_msg.delete()
        except Exception:
            pass
        await state.clear()
