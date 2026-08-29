from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.hemis_service import hemis_service
from services.user_service import user_service

router = Router()


class HemisAuthStates(StatesGroup):
    waiting_for_domain = State()
    waiting_for_login = State()
    waiting_for_password = State()


@router.callback_query(F.data == "btn_hemis")
async def handle_hemis_menu(callback: types.CallbackQuery, state: FSMContext):
    creds = await user_service.get_hemis_credentials(callback.from_user.id)
    kb = InlineKeyboardBuilder()

    if creds:
        kb.button(text="📅 Bugungi dars jadvali", callback_data="hemis_schedule")
        kb.button(text="⏳ Topshiriqlar & Deadline", callback_data="hemis_tasks")
        kb.button(text="📊 Profil & Davomat", callback_data="hemis_profile")
        kb.button(text="🚪 Hisobdan chiqish", callback_data="hemis_logout")
        kb.adjust(1)

        text = (
            f"🎓 **HEMIS Kabineti**\n\n"
            f"👤 Talaba: **{creds.get('name') or 'Noma\'lum'}**\n"
            f"🏫 OTM: `{creds.get('domain')}`\n"
            f"👥 Guruh: `{creds.get('group') or 'Aniqlanmagan'}`\n\n"
            f"Kerakli bo'limni tanlang:"
        )
    else:
        kb.button(text="🔑 HEMIS hisobini ulash", callback_data="hemis_login_start")
        kb.button(text="◀️ Asosiy menyu", callback_data="btn_main_menu")
        kb.adjust(1)

        text = (
            "🎓 **HEMIS tizimi ulanmagan**\n\n"
            "Dars jadvali, topshiriqlar muddatlari (deadline) va baholaringizni avtomatik "
            "kuzatib borish uchun HEMIS profilingizni botga ulang.\n\n"
            "🔒 *Parol va ma'lumotlaringiz AES-256 algoritmi orqali shifrlanadi.*"
        )

    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")
    await callback.answer()


# 1. AUTENTIFIKATSIYA OQIMI
@router.callback_query(F.data == "hemis_login_start")
async def start_hemis_auth(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🏫 **Universitetingiz HEMIS domenini kiriting:**\n"
        "(Masalan: `student.tuit.uz`, `student.nuu.uz`, yoki shunchaki `tuit`)"
    )
    await state.set_state(HemisAuthStates.waiting_for_domain)
    await callback.answer()


@router.message(HemisAuthStates.waiting_for_domain)
async def process_domain(message: types.Message, state: FSMContext):
    domain = message.text.strip().lower()
    await state.update_data(domain=domain)
    await message.answer("👤 Endi HEMIS **Talaba ID** (Login)ingizni kiriting:")
    await state.set_state(HemisAuthStates.waiting_for_login)


@router.message(HemisAuthStates.waiting_for_login)
async def process_login(message: types.Message, state: FSMContext):
    login_id = message.text.strip()
    await state.update_data(login_id=login_id)
    await message.answer("🔒 HEMIS **parolingizni** kiriting:\n*(Xavfsizlik uchun xabaringiz tizim tomonidan darhol o'chiriladi)*")
    await state.set_state(HemisAuthStates.waiting_for_password)


@router.message(HemisAuthStates.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()
    domain = data.get("domain")
    login_id = data.get("login_id")

    # Xavfsizlik: Parol yozilgan xabarni darhol o'chirish
    try:
        await message.delete()
    except Exception:
        pass

    wait_msg = await message.answer("⏳ HEMIS tizimi bilan tekshirilmoqda...")
    token = await hemis_service.login(domain, login_id, password)

    if token:
        # Profil ma'lumotlarini olish
        info = await hemis_service.get_account_info(domain, token)
        await user_service.link_hemis(message.from_user.id, domain, token, info)
        await wait_msg.edit_text("✅ **HEMIS hisobingiz muvaffaqiyatli ulandi!**\n\nMenyuga qaytish uchun /start bosing.")
    else:
        await wait_msg.edit_text("❌ **Kirish muvaffaqiyatsiz bo'ldi.**\nLogin, parol yoki OTM domeni noto'g'ri kiritildi. Qayta urinib ko'ring.")

    await state.clear()


# 2. DARS JADVALI
@router.callback_query(F.data == "hemis_schedule")
async def show_schedule(callback: types.CallbackQuery):
    creds = await user_service.get_hemis_credentials(callback.from_user.id)
    if not creds:
        await callback.answer("Avval HEMIS hisobini ulang!", show_alert=True)
        return

    wait_msg = await callback.message.answer("⏳ Dars jadvali yuklanmoqda...")
    schedule = await hemis_service.get_schedule(creds["domain"], creds["token"])
    await wait_msg.delete()

    if schedule:
        lines = ["📅 **Bugungi / Haftalik Dars Jadvali:**\n"]
        for item in schedule[:8]:
            subject = item.get("subject", {}).get("name") or "Fan"
            lesson_pair = item.get("lessonPair", {}).get("name") or ""
            auditorium = item.get("auditorium", {}).get("name") or "Xona noma'lum"
            lines.append(f"⏱ *{lesson_pair}* | **{subject}** ({auditorium})")
        text = "\n".join(lines)
    else:
        text = "📅 Hozirgi kunda jadval bo'sh yoki yuklab bo'lmadi."

    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Orqaga", callback_data="btn_hemis")
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")
    await callback.answer()


# 3. TOPSHIRIQLAR VA DEADLINE
@router.callback_query(F.data == "hemis_tasks")
async def show_tasks(callback: types.CallbackQuery):
    creds = await user_service.get_hemis_credentials(callback.from_user.id)
    if not creds:
        await callback.answer("Avval HEMIS hisobini ulang!", show_alert=True)
        return

    wait_msg = await callback.message.answer("⏳ Topshiriqlar yuklanmoqda...")
    tasks = await hemis_service.get_tasks(creds["domain"], creds["token"])
    await wait_msg.delete()

    if tasks:
        lines = ["⏳ **Topshiriqlar va Yakunlanish Muddatlari (Deadline):**\n"]
        for t in tasks[:6]:
            name = t.get("name") or t.get("task", {}).get("name") or "Topshiriq"
            deadline = t.get("deadline") or "Muddati belgilanmagan"
            lines.append(f"📌 **{name}**\n🗓 Muddati: `{deadline}`\n")
        text = "\n".join(lines)
    else:
        text = "✅ Faol topshiriqlar yoki deadlinelar mavjud emas!"

    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Orqaga", callback_data="btn_hemis")
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")
    await callback.answer()
