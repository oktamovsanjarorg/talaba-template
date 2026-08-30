import os
import asyncio
from aiogram import Router, F, types, Bot
from aiogram.filters import Command
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
    kb.button(text="❌ Bekor qilish", callback_data="btn_cancel")
    return kb.as_markup()


# ================= 1. REFERAT =================
@router.message(Command("referat"))
@router.message(F.text == "📝 Referat")
@router.callback_query(F.data == "btn_referat")
async def start_referat_flow(event: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    # Agar buyruq bilan birga mavzu yozilgan bo'lsa (Masalan: /referat Bulutli texnologiyalar)
    if isinstance(event, types.Message) and event.text and event.text.startswith("/referat ") and len(event.text.split(" ", 1)) > 1:
        topic = event.text.split(" ", 1)[1].strip()
        await execute_referat_generation(event, topic, state)
        return

    text = (
        "📝 **Akademik Referat tayyorlash**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Iltimos, referat **mavzusini** kiriting:\n\n"
        "💡 *Maslahat: Mavzuni aniq yozing.*\n"
        "📌 *Misol:* `O'zbekistonda raqamli iqtisodiyotni rivojlantirish`\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
    await state.set_state(AcademicStates.waiting_for_referat_topic)


@router.message(AcademicStates.waiting_for_referat_topic)
async def process_referat_topic(message: types.Message, state: FSMContext):
    topic = message.text.strip()
    if len(topic) < 3:
        await message.answer("⚠️ Mavzu juda qisqa. To'liqroq mavzu kiriting:", reply_markup=get_cancel_keyboard())
        return
    await execute_referat_generation(message, topic, state)


async def execute_referat_generation(message: types.Message, topic: str, state: FSMContext):
    status_msg = await message.answer(
        "⏳ **[1/3]** Mavzu tahlil qilinmoqda va akademik reja tuzilmoqda...\n"
        "*(Iltimos, 10-15 soniya kuting)*",
        parse_mode="Markdown"
    )
    try:
        await asyncio.sleep(1)
        await status_msg.edit_text("⏳ **[2/3]** Qwen AI orqali ilmiy boblar va xulosalar yozilmoqda...", parse_mode="Markdown")
        data = await ai_service.generate_referat_structure(topic=topic)
        
        await status_msg.edit_text("⏳ **[3/3]** Rasmiy Titul varag'i va Word (.docx) standarti shakllantirilmoqda...", parse_mode="Markdown")
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
        kb.button(text="📊 Shu mavzuda Slayd yasash", callback_data=f"auto_slide_{topic[:25]}")
        kb.button(text="🎯 Testlar to'plami tuzish", callback_data=f"auto_quiz_{topic[:25]}")
        kb.button(text="🏠 Asosiy menyu", callback_data="btn_main_menu")
        kb.adjust(1)

        doc_file = FSInputFile(file_path, filename=f"{topic[:25]}_referat.docx")
        await message.answer_document(
            doc_file,
            caption=(
                f"🎉 **Referat muvaffaqiyatli tayyorlandi!**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 **Mavzu:** *{topic}*\n"
                f"📄 **Format:** Microsoft Word (.docx)\n"
                f"📐 **Standart:** Times New Roman 14, 1.5 interval, Titul, Mundarija, Boblar, Xulosa va Adabiyotlar.\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            ),
            reply_markup=kb.as_markup(),
            parse_mode="Markdown"
        )
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        await user_service.record_generation(message.from_user.id, "referat", topic, "failed")
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}\nQaytadan urinib ko'ring:", reply_markup=get_cancel_keyboard())
    finally:
        try:
            await status_msg.delete()
        except Exception:
            pass
        await state.clear()


# ================= 2. SLAYD (PPTX) =================
@router.message(Command("slide"))
@router.message(F.text == "📊 Slayd")
@router.callback_query(F.data == "btn_slide")
@router.callback_query(F.data.startswith("auto_slide_"))
async def start_slide_flow(event: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    # Auto slide trigger
    if isinstance(event, types.CallbackQuery) and event.data.startswith("auto_slide_"):
        topic = event.data.replace("auto_slide_", "").strip()
        await state.update_data(slide_topic=topic)
        await show_slide_count_options(event.message, topic, state)
        await event.answer()
        return

    # Command parameter
    if isinstance(event, types.Message) and event.text and event.text.startswith("/slide ") and len(event.text.split(" ", 1)) > 1:
        topic = event.text.split(" ", 1)[1].strip()
        await state.update_data(slide_topic=topic)
        await show_slide_count_options(event, topic, state)
        return

    text = (
        "📊 **Taqdimot (PowerPoint Slayd) tayyorlash**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Iltimos, taqdimot **mavzusini** kiriting:\n\n"
        "📌 *Misol:* `Sun'iy intellekt va kiberxavfsizlik asoslari`\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
    await state.set_state(AcademicStates.waiting_for_slide_topic)


@router.message(AcademicStates.waiting_for_slide_topic)
async def process_slide_topic(message: types.Message, state: FSMContext):
    topic = message.text.strip()
    await state.update_data(slide_topic=topic)
    await show_slide_count_options(message, topic, state)


async def show_slide_count_options(target: types.Message, topic: str, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text="5 ta slayd (Qisqa)", callback_data="slide_count_5")
    kb.button(text="8 ta slayd (O'rtacha)", callback_data="slide_count_8")
    kb.button(text="10 ta slayd (Katta)", callback_data="slide_count_10")
    kb.button(text="❌ Bekor qilish", callback_data="btn_cancel")
    kb.adjust(1)

    await target.answer(
        f"📊 **Mavzu:** *{topic}*\n\nNechta slayddan iborat taqdimot tayyorlansin?",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )
    await state.set_state(AcademicStates.waiting_for_slide_count)


@router.callback_query(F.data.startswith("slide_count_"))
async def process_slide_count(callback: types.CallbackQuery, state: FSMContext):
    count = int(callback.data.split("_")[-1])
    data = await state.get_data()
    topic = data.get("slide_topic", "Taqdimot")

    status_msg = await callback.message.answer(f"⏳ **[1/2]** {count} ta slayd uchun professional ssenariy va tezislar tuzilmoqda...")
    await callback.answer()

    try:
        slides_data = await ai_service.generate_slides_data(topic=topic, slide_count=count)
        await status_msg.edit_text("⏳ **[2/2]** 16:9 zamonaviy ranglar palitrasidagi PowerPoint (.pptx) chizilmoqda...")
        
        output_dir = "/app/storage/slides"
        os.makedirs(output_dir, exist_ok=True)
        file_path = f"{output_dir}/slide_{callback.from_user.id}.pptx"
        
        create_presentation_pptx(slides_data=slides_data, topic=topic, output_path=file_path, student_name=callback.from_user.full_name)
        await user_service.record_generation(callback.from_user.id, "slide", topic, "success")
        
        kb = InlineKeyboardBuilder()
        kb.button(text="📝 Shu mavzuda Referat yozish", callback_data="btn_referat")
        kb.button(text="🏠 Asosiy menyu", callback_data="btn_main_menu")
        kb.adjust(1)

        doc_file = FSInputFile(file_path, filename=f"{topic[:25]}_taqdimot.pptx")
        await callback.message.answer_document(
            doc_file,
            caption=(
                f"🎉 **Taqdimot tayyor!**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 **Mavzu:** *{topic}*\n"
                f"📊 **Slaydlar soni:** {len(slides_data)} ta\n"
                f"🖥 **Format:** 16:9 Widescreen (.pptx)\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            ),
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


# ================= 3. MUSTAQIL ISH =================
@router.message(Command("mustaqil"))
@router.message(F.text == "📑 Mustaqil ish")
@router.callback_query(F.data == "btn_mustaqil")
async def start_mustaqil_flow(event: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    if isinstance(event, types.Message) and event.text and event.text.startswith("/mustaqil ") and len(event.text.split(" ", 1)) > 1:
        topic = event.text.split(" ", 1)[1].strip()
        await execute_mustaqil_generation(event, topic, state)
        return

    text = (
        "📑 **Mustaqil Ta'lim Ishi tayyorlash**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Mustaqil ish **mavzusini** kiriting:\n\n"
        "📌 *Misol:* `Mikroiqtisodiyotda talab va taklif qonunlari tahlili`\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
    await state.set_state(AcademicStates.waiting_for_mustaqil_topic)


@router.message(AcademicStates.waiting_for_mustaqil_topic)
async def process_mustaqil_topic(message: types.Message, state: FSMContext):
    topic = message.text.strip()
    await execute_mustaqil_generation(message, topic, state)


async def execute_mustaqil_generation(message: types.Message, topic: str, state: FSMContext):
    status_msg = await message.answer("⏳ Mustaqil ta'lim ishi OTM talablari asosida shakllantirilmoqda...")
    try:
        data = await ai_service.generate_mustaqil_ish_structure(topic=topic)
        output_dir = "/app/storage/mustaqil"
        os.makedirs(output_dir, exist_ok=True)
        file_path = f"{output_dir}/mustaqil_{message.from_user.id}.docx"

        create_mustaqil_ish_docx(data=data, output_path=file_path, student_name=message.from_user.full_name)
        await user_service.record_generation(message.from_user.id, "mustaqil", topic, "success")

        kb = InlineKeyboardBuilder()
        kb.button(text="🏠 Asosiy menyu", callback_data="btn_main_menu")

        doc_file = FSInputFile(file_path, filename=f"{topic[:25]}_mustaqil_ish.docx")
        await message.answer_document(
            doc_file,
            caption=(
                f"🎉 **Mustaqil ish tayyor!**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 **Mavzu:** *{topic}*\n"
                f"📄 **Format:** Word (.docx)\n"
                f"📐 **Standart:** Maqsad, Nazariy qism, Amaliy tahlil va Xulosa.\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            ),
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


# ================= 4. TESTLAR (QUIZ) =================
@router.message(Command("quiz"))
@router.message(F.text == "🎯 Testlar (Quiz)")
@router.callback_query(F.data == "btn_quiz")
@router.callback_query(F.data.startswith("auto_quiz_"))
async def start_quiz_flow(event: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    if isinstance(event, types.CallbackQuery) and event.data.startswith("auto_quiz_"):
        topic = event.data.replace("auto_quiz_", "").strip()
        await execute_quiz_generation(event.message, topic, state)
        await event.answer()
        return

    if isinstance(event, types.Message) and event.text and event.text.startswith("/quiz ") and len(event.text.split(" ", 1)) > 1:
        topic = event.text.split(" ", 1)[1].strip()
        await execute_quiz_generation(event, topic, state)
        return

    text = (
        "🎯 **Test va Nazorat Savollari tuzish**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Qaysi mavzu yoki fan bo'yicha testlar tuzilsin?\n\n"
        "📌 *Misol:* `O'zbekiston tarixi` yoki `Python dasturlash asoslari`\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
    await state.set_state(AcademicStates.waiting_for_quiz_topic)


@router.message(AcademicStates.waiting_for_quiz_topic)
async def process_quiz_topic(message: types.Message, state: FSMContext):
    topic = message.text.strip()
    await execute_quiz_generation(message, topic, state)


async def execute_quiz_generation(message: types.Message, topic: str, state: FSMContext):
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

        doc_file = FSInputFile(file_path, filename=f"{topic[:25]}_testlar.docx")
        await message.answer_document(
            doc_file,
            caption=(
                f"🎉 **Testlar to'plami tayyor!**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 **Mavzu:** *{topic}*\n"
                f"🎯 **Savollar soni:** {len(quiz_data)} ta\n"
                f"📄 **Format:** Word (.docx) — Javoblar kaliti bilan.\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            ),
            reply_markup=kb.as_markup(),
            parse_mode="Markdown"
        )

        if quiz_data:
            first_q = quiz_data[0]
            opts = first_q.get("options", ["A", "B", "C", "D"])[:4]
            # Telegram poll options must be unique and 1-100 chars
            clean_opts = [str(o)[:95] for o in opts]
            corr_id = first_q.get("correct_index", 0)
            if corr_id >= len(clean_opts):
                corr_id = 0
            await message.answer_poll(
                question=f"1-savol: {first_q.get('question')[:250]}",
                options=clean_opts,
                type="quiz",
                correct_option_id=corr_id,
                explanation=first_q.get("explanation", "")[:190] if first_q.get("explanation") else None,
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


# ================= 5. KONSPEKT =================
@router.message(Command("summary"))
@router.message(F.text == "💡 Konspekt")
@router.callback_query(F.data == "btn_summary")
async def start_summary_flow(event: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "💡 **Aqlli Konspekt va Matnni qisqartirish**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Konspekt qilmoqchi bo'lgan uzun matn yoki maqolani botga yuboring:\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
    await state.set_state(AcademicStates.waiting_for_summary_text)


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
            f"📑 **Mavzu bo'yicha Konspekt va Asosiy Xulosalar:**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{summary}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━",
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


# ================= 6. SMART GENERAL ROUTER (FOYDALANUVCHI IXTIYORIY MATN YOZGANDA) =================
@router.message(F.text & ~F.text.startswith("/"))
async def handle_general_text_input(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        return # FSM state ichida bo'lsa o'sha handler ishlaydi

    topic = message.text.strip()
    if len(topic) < 2:
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Referat (Word)", callback_data=f"smart_ref_{topic[:25]}")
    kb.button(text="📊 Taqdimot (PPTX)", callback_data=f"auto_slide_{topic[:25]}")
    kb.button(text="📑 Mustaqil ish (Word)", callback_data=f"smart_mst_{topic[:25]}")
    kb.button(text="🎯 Testlar (Quiz)", callback_data=f"auto_quiz_{topic[:25]}")
    kb.adjust(2, 2)

    await message.answer(
        f"💡 **Mavzu aniqlandi:** *{topic}*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Ushbu mavzu bo'yicha qanday akademik hujjat tayyorlab beray?",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("smart_ref_"))
async def process_smart_referat(callback: types.CallbackQuery, state: FSMContext):
    topic = callback.data.replace("smart_ref_", "").strip()
    await execute_referat_generation(callback.message, topic, state)
    await callback.answer()


@router.callback_query(F.data.startswith("smart_mst_"))
async def process_smart_mustaqil(callback: types.CallbackQuery, state: FSMContext):
    topic = callback.data.replace("smart_mst_", "").strip()
    await execute_mustaqil_generation(callback.message, topic, state)
    await callback.answer()
