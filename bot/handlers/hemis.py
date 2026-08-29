from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.hemis_service import hemis_service
from services.user_service import user_service
from services.hemis.universities import UNIVERSITIES, search_university

router = Router()


class HemisAuthStates(StatesGroup):
    waiting_for_domain_search = State()
    waiting_for_login = State()
    waiting_for_password = State()


def get_cancel_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Bekor qilish", callback_data="btn_hemis")
    return kb.as_markup()


@router.callback_query(F.data == "btn_hemis")
async def handle_hemis_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    creds = await user_service.get_hemis_credentials(callback.from_user.id)
    kb = InlineKeyboardBuilder()

    if creds:
        kb.button(text="📅 Dars jadvali (Haftalik)", callback_data="hemis_schedule")
        kb.button(text="⏳ Topshiriqlar & Deadlinelar", callback_data="hemis_tasks")
        kb.button(text="🚪 Hisobdan chiqish", callback_data="hemis_logout")
        kb.button(text="◀️ Asosiy menyu", callback_data="btn_main_menu")
        kb.adjust(1)

        text = (
            f"🎓 **HEMIS Shaxsiy Kabineti**\n\n"
            f"👤 Talaba: **{creds.get('name') or 'Noma\'lum'}**\n"
            f"🏫 OTM: `{creds.get('domain')}`\n"
            f"👥 Guruh: `{creds.get('group') or 'Aniqlanmagan'}`\n\n"
            f"Kerakli bo'limni tanlang:"
        )
    else:
        kb.button(text="🔑 HEMIS hisobini ulash", callback_data="hemis_select_univ")
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


# 1. OTMNI TANLASH VA AVTORIZATSIYA
@router.callback_query(F.data == "hemis_select_univ")
async def show_universities_selection(callback: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder()
    for u in UNIVERSITIES[:6]:
        kb.button(text=f"🏛 {u['short'].upper()}", callback_data=f"set_univ_{u['domain']}")
    
    kb.button(text="🔍 Boshqa OTMni qidirish / Yozish", callback_data="hemis_search_univ")
    kb.button(text="◀️ Orqaga", callback_data="btn_hemis")
    kb.adjust(2, 2, 2, 1, 1)

    text = "🏫 **Oliygohingizni (OTM) tanlang:**\n\nRo'yxatdan o'z universitetingizni tanlang yoki qidiruvdan foydalaning:"
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("set_univ_"))
async def select_university_direct(callback: types.CallbackQuery, state: FSMContext):
    domain = callback.data.replace("set_univ_", "")
    await state.update_data(domain=domain)
    
    await callback.message.answer(
        f"🏛 Tanlangan OTM: `{domain}`\n\n"
        f"👤 HEMIS **Talaba ID (Login)**ingizni kiriting:",
        reply_markup=get_cancel_kb()
    )
    await state.set_state(HemisAuthStates.waiting_for_login)
    await callback.answer()


@router.callback_query(F.data == "hemis_search_univ")
async def ask_university_search(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🔍 Universitetingiz nomini yoki domenini yozing:\n*(Masalan: `Samarqand`, `tuit`, yoki `student.nuu.uz`)*",
        reply_markup=get_cancel_kb()
    )
    await state.set_state(HemisAuthStates.waiting_for_domain_search)
    await callback.answer()


@router.message(HemisAuthStates.waiting_for_domain_search)
async def process_domain_search(message: types.Message, state: FSMContext):
    query = message.text.strip()
    found = search_university(query)
    
    if found:
        kb = InlineKeyboardBuilder()
        for u in found:
            kb.button(text=u['name'][:30], callback_data=f"set_univ_{u['domain']}")
        kb.button(text="❌ Bekor qilish", callback_data="btn_hemis")
        kb.adjust(1)
        await message.answer("Topilgan OTMlar ro'yxati:", reply_markup=kb.as_markup())
    else:
        # To'g'ridan-to'g'ri domen deb qabul qilish
        await state.update_data(domain=query)
        await message.answer(f"Domen: `{query}`\n\n👤 HEMIS **Talaba ID** (Login)ingizni kiriting:", reply_markup=get_cancel_kb())
        await state.set_state(HemisAuthStates.waiting_for_login)


@router.message(HemisAuthStates.waiting_for_login)
async def process_login(message: types.Message, state: FSMContext):
    login_id = message.text.strip()
    await state.update_data(login_id=login_id)
    await message.answer("🔒 HEMIS **parolingizni** kiriting:\n*(Xabaringiz xavfsizlik uchun darhol o'chiriladi)*", reply_markup=get_cancel_kb())
    await state.set_state(HemisAuthStates.waiting_for_password)


@router.message(HemisAuthStates.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()
    domain = data.get("domain", "student.tuit.uz")
    login_id = data.get("login_id")

    try:
        await message.delete()
    except Exception:
        pass

    wait_msg = await message.answer("⏳ HEMIS tizimi orqali ma'lumotlar tekshirilmoqda...")
    token = await hemis_service.login(domain, login_id, password)

    if token:
        info = await hemis_service.get_account_info(domain, token)
        await user_service.link_hemis(message.from_user.id, domain, token, info)
        kb = InlineKeyboardBuilder()
        kb.button(text="🎓 HEMIS Kabinetiga o'tish", callback_data="btn_hemis")
        await wait_msg.edit_text("✅ **HEMIS hisobingiz muvaffaqiyatli ulandi!**", reply_markup=kb.as_markup())
    else:
        kb = InlineKeyboardBuilder()
        kb.button(text="🔄 Qayta urinish", callback_data="hemis_select_univ")
        kb.button(text="🏠 Asosiy menyu", callback_data="btn_main_menu")
        kb.adjust(1)
        await wait_msg.edit_text("❌ **Kirish muvaffaqiyatsiz bo'ldi.**\nLogin, parol yoki OTM domeni noto'g'ri kiritildi.", reply_markup=kb.as_markup())

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
        lines = ["📅 **Dars Jadvali:**\n"]
        for item in schedule[:8]:
            subject = item.get("subject", {}).get("name") if isinstance(item.get("subject"), dict) else str(item.get("subject", "Fan"))
            lesson_pair = item.get("lessonPair", {}).get("name") if isinstance(item.get("lessonPair"), dict) else str(item.get("lessonPair", "Vaqt"))
            auditorium = item.get("auditorium", {}).get("name") if isinstance(item.get("auditorium"), dict) else str(item.get("auditorium", "Xona"))
            lines.append(f"⏱ *{lesson_pair}* | **{subject}** ({auditorium})")
        text = "\n".join(lines)
    else:
        text = "📅 Hozirgi kunda jadval bo'sh yoki yuklab bo'lmadi."

    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Orqaga", callback_data="btn_hemis")
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")
    await callback.answer()


# 3. TOPSHIRIQLAR & DEADLINE
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
        lines = ["⏳ **Topshiriqlar va Deadline muddatlari:**\n"]
        for t in tasks[:6]:
            name = t.get("name") or t.get("task", {}).get("name") or "Topshiriq"
            deadline = t.get("deadline") or "Belgilanmagan"
            lines.append(f"📌 **{name}**\n🗓 Deadline: `{deadline}`\n")
        text = "\n".join(lines)
    else:
        text = "✅ Faol topshiriqlar yoki deadlinelar mavjud emas!"

    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Orqaga", callback_data="btn_hemis")
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")
    await callback.answer()


# 4. HISOBDAN CHIQISH (LOGOUT)
@router.callback_query(F.data == "hemis_logout")
async def process_logout(callback: types.CallbackQuery):
    await user_service.link_hemis(callback.from_user.id, "", "", None)
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 Asosiy menyu", callback_data="btn_main_menu")
    await callback.message.edit_text("🚪 **HEMIS hisobingizdan muvaffaqiyatli chiqdingiz.**", reply_markup=kb.as_markup())
    await callback.answer()
