from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from services.user_service import user_service

router = Router()


def get_persistent_reply_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.button(text="📝 Referat")
    kb.button(text="📊 Slayd")
    kb.button(text="📑 Mustaqil ish")
    kb.button(text="🎯 Testlar (Quiz)")
    kb.button(text="💡 Konspekt")
    kb.button(text="🎓 HEMIS")
    kb.button(text="👤 Profilim")
    kb.button(text="🏠 Bosh menyu")
    kb.adjust(3, 3, 2)
    return kb.as_markup(resize_keyboard=True)


def get_main_menu_inline_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Referat yozish", callback_data="btn_referat")
    kb.button(text="📊 Slayd yasash", callback_data="btn_slide")
    kb.button(text="📑 Mustaqil ish", callback_data="btn_mustaqil")
    kb.button(text="🎯 Testlar (Quiz)", callback_data="btn_quiz")
    kb.button(text="💡 Konspekt qilish", callback_data="btn_summary")
    kb.button(text="🎓 HEMIS Kabineti", callback_data="btn_hemis")
    kb.button(text="👤 Shaxsiy Profil", callback_data="btn_profile")
    kb.button(text="❓ Qo'llanma", callback_data="btn_help")
    kb.adjust(2, 2, 2, 1, 1)
    return kb.as_markup()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await user_service.get_or_create(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )

    text = (
        f"🎓 **Assalomu alaykum, {message.from_user.first_name}!**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "**Talaba AI & HEMIS Assistant** akademik ekotizimiga xush kelibsiz.\n\n"
        "🏛 **Bizning asosiy imkoniyatlarimiz:**\n"
        "┌ 📝 **Referat & Mustaqil ish:** Times New Roman 14, 1.5 interval, rasmiy titul va mundarija bilan Word (.docx)\n"
        "├ 📊 **Taqdimotlar:** 16:9 formatdagi zamonaviy dizayndagi slaydlar (.pptx)\n"
        "├ 🎯 **Testlar & Quiz:** 4 variantli savollar to'plami va javoblar kaliti\n"
        "├ 💡 **Aqlli Konspekt:** Katta matn va leksiyalardan asosiy xulosalar\n"
        "└ 🎓 **HEMIS:** 120+ OTM dars jadvali, topshiriqlar va deadline\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Quyidagi xizmatlardan birini tanlang:"
    )
    await message.answer(text, reply_markup=get_persistent_reply_keyboard(), parse_mode="Markdown")
    await message.answer("👇 **Xizmatlar katalogi:**", reply_markup=get_main_menu_inline_keyboard(), parse_mode="Markdown")


# BEKOR QILISH BUYRUG'I
@router.message(Command("cancel"))
@router.callback_query(F.data == "btn_cancel")
async def cmd_cancel(event: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    text = "❌ **Joriy amal bekor qilindi.** Asosiy menyudasiz."
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=get_main_menu_inline_keyboard(), parse_mode="Markdown")
        await event.answer("Amal bekor qilindi")
    else:
        await event.answer(text, reply_markup=get_main_menu_inline_keyboard(), parse_mode="Markdown")


# BOSH MENYU
@router.message(F.text.in_(["🏠 Bosh menyu", "/menu"]))
@router.callback_query(F.data == "btn_main_menu")
async def back_to_main_menu(event: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    text = "🏛 **Asosiy menyu.** Kerakli xizmatni tanlang:"
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=get_main_menu_inline_keyboard(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=get_main_menu_inline_keyboard(), parse_mode="Markdown")


# PROFIL
@router.message(F.text.in_(["👤 Profilim", "/profile"]))
@router.callback_query(F.data == "btn_profile")
async def show_profile(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    user = await user_service.get_or_create(user_id, event.from_user.full_name, event.from_user.username)
    creds = await user_service.get_hemis_credentials(user_id)

    hemis_info = (
        f"✅ **Ulangan**\n"
        f"├ 👤 Talaba: `{creds.get('name') or 'Noma\'lum'}`\n"
        f"├ 🏫 OTM: `{creds.get('university') or creds['domain']}`\n"
        f"└ 👥 Guruh: `{creds.get('group') or 'Noma\'lum'}`"
    ) if creds else "❌ **Ulanmagan** *(Ulanganidan so'ng dars jadvali va topshiriqlar avtomatik ko'rinadi)*"

    text = (
        "👤 **Foydalanuvchi Shaxsiy Profili**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 **Telegram ID:** `{user.id}`\n"
        f"👤 **Ism:** {user.full_name}\n"
        f"📅 **Ro'yxatdan o'tgan:** `{user.created_at.strftime('%d.%m.%Y %H:%M') if user.created_at else 'Yangi'}`\n\n"
        "🎓 **HEMIS Integratsiyasi:**\n"
        f"{hemis_info}\n\n"
        "📊 **Yaratilgan akademik hujjatlar:**\n"
        f"┌ 📝 Referatlar: **{user.referats_count} ta**\n"
        f"├ 📊 Slaydlar: **{user.slides_count} ta**\n"
        f"├ 📑 Mustaqil ishlar: **{user.mustaqil_count} ta**\n"
        f"└ 🎯 Test to'plamlari: **{user.quizzes_count} ta**\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    kb = InlineKeyboardBuilder()
    if not creds:
        kb.button(text="🔑 HEMISni ulash", callback_data="hemis_select_univ")
    kb.button(text="◀️ Asosiy menyu", callback_data="btn_main_menu")
    kb.adjust(1)

    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb.as_markup(), parse_mode="Markdown")


# YORDAM
@router.message(Command("help"))
@router.callback_query(F.data == "btn_help")
async def show_help(event: types.Message | types.CallbackQuery):
    text = (
        "📖 **Botdan foydalanish qo'llanmasi**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "1. **Referat va Mustaqil ish tayyorlash:**\n"
        "• Menyudan 'Referat' yoki 'Mustaqil ish' tugmasini bosing;\n"
        "• Mavzuni kiriting (masalan: *'Kiberxavfsizlik asoslari'*);\n"
        "• Bot bir necha soniyada OTM talablaridagi to'liq Word (.docx) faylni beradi.\n\n"
        "2. **Taqdimot (PowerPoint) yasash:**\n"
        "• Slayd mavzusi va slaydlar sonini (5, 8, 10 ta) tanlang;\n"
        "• Zamonaviy 16:9 dizayndagi .pptx taqdimot yuklanadi.\n\n"
        "3. **HEMIS kabinetiga ulanish:**\n"
        "• OTMni ro'yxatdan tanlang va Talaba ID hamda parolingizni kiriting;\n"
        "• Bot dars jadvali va deadlinelarni sizga ko'rsatib beradi.\n\n"
        "📌 **Barcha buyruqlar:**\n"
        "/start - Botni qayta ishga tushirish\n"
        "/referat - Referat tayyorlash\n"
        "/slide - Slayd tayyorlash\n"
        "/mustaqil - Mustaqil ish tayyorlash\n"
        "/quiz - Testlar tuzish\n"
        "/summary - Konspekt qilish\n"
        "/hemis - HEMIS kabineti\n"
        "/profile - Shaxsiy statistika\n"
        "/cancel - Joriy jarayonni bekor qilish\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Asosiy menyu", callback_data="btn_main_menu")

    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb.as_markup(), parse_mode="Markdown")
