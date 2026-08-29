from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
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
    kb.button(text="📝 Referat tayyorlash (Word)", callback_data="btn_referat")
    kb.button(text="📊 Slayd tayyorlash (PPTX)", callback_data="btn_slide")
    kb.button(text="📑 Mustaqil Ta'lim Ishi", callback_data="btn_mustaqil")
    kb.button(text="🎯 Testlar va Quiz", callback_data="btn_quiz")
    kb.button(text="💡 Aqlli Konspekt", callback_data="btn_summary")
    kb.button(text="🎓 HEMIS Kabineti", callback_data="btn_hemis")
    kb.button(text="👤 Shaxsiy Profil", callback_data="btn_profile")
    kb.button(text="❓ Qo'llanma / Yordam", callback_data="btn_help")
    kb.adjust(2, 2, 2, 1, 1)
    return kb.as_markup()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await user_service.get_or_create(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )

    text = (
        f"Assalomu alaykum, {message.from_user.first_name}! 🎓\n\n"
        "**Talaba AI & HEMIS Assistant** ekotizimiga xush kelibsiz.\n\n"
        "🏛 Bu bot sizning o'qish jarayoningizdagi barcha topshiriqlarni yuqori akademik standartda bajarishga yordam beradi:\n\n"
        "• **Referat & Mustaqil ish:** Times New Roman 14, 1.5 interval, rasmiy titul va mundarija bilan tayyor Word (.docx);\n"
        "• **Taqdimotlar:** 16:9 formatdagi zamonaviy rangli slaydlar (.pptx);\n"
        "• **Testlar:** 4 variantli savollar to'plami va javoblar kaliti;\n"
        "• **HEMIS:** Dars jadvali va topshiriqlar muddati (deadline).\n\n"
        "Kerakli bo'limni tanlang:"
    )
    await message.answer(text, reply_markup=get_persistent_reply_keyboard())
    await message.answer("Xizmatlar ro'yxati:", reply_markup=get_main_menu_inline_keyboard(), parse_mode="Markdown")


# REPLY TUGMALARNI MOS HANDLERLARGA YO'NALTIRISH
@router.message(F.text == "📝 Referat")
async def reply_referat(message: types.Message):
    await message.answer("📝 Referat bo'limi ochilmoqda...", reply_markup=InlineKeyboardBuilder().button(text="✍️ Mavzu kiritish", callback_data="btn_referat").as_markup())

@router.message(F.text == "📊 Slayd")
async def reply_slide(message: types.Message):
    await message.answer("📊 Slayd bo'limi ochilmoqda...", reply_markup=InlineKeyboardBuilder().button(text="📊 Slayd tayyorlash", callback_data="btn_slide").as_markup())

@router.message(F.text == "📑 Mustaqil ish")
async def reply_mustaqil(message: types.Message):
    await message.answer("📑 Mustaqil ish bo'limi ochilmoqda...", reply_markup=InlineKeyboardBuilder().button(text="📑 Mustaqil ish yozish", callback_data="btn_mustaqil").as_markup())

@router.message(F.text == "🎯 Testlar (Quiz)")
async def reply_quiz(message: types.Message):
    await message.answer("🎯 Testlar bo'limi ochilmoqda...", reply_markup=InlineKeyboardBuilder().button(text="🎯 Test tuzish", callback_data="btn_quiz").as_markup())

@router.message(F.text == "💡 Konspekt")
async def reply_summary(message: types.Message):
    await message.answer("💡 Konspekt bo'limi ochilmoqda...", reply_markup=InlineKeyboardBuilder().button(text="💡 Konspekt qilish", callback_data="btn_summary").as_markup())

@router.message(F.text == "🎓 HEMIS")
async def reply_hemis(message: types.Message):
    await message.answer("🎓 HEMIS bo'limi:", reply_markup=InlineKeyboardBuilder().button(text="🎓 HEMISga o'tish", callback_data="btn_hemis").as_markup())

@router.message(F.text.in_(["👤 Profilim", "/profile"]))
@router.callback_query(F.data == "btn_profile")
async def show_profile(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    user = await user_service.get_or_create(user_id, event.from_user.full_name, event.from_user.username)
    creds = await user_service.get_hemis_credentials(user_id)

    hemis_status = f"✅ Ulangan (`{creds['domain']}`)\n👤 Talaba: **{creds.get('name') or 'Aniqlanmagan'}**\n🏫 OTM: `{creds.get('university') or creds['domain']}`" if creds else "❌ Ulanmagan"

    text = (
        f"👤 **Foydalanuvchi Shaxsiy Profili**\n\n"
        f"🆔 Telegram ID: `{user.id}`\n"
        f"👤 Ism: **{user.full_name}**\n\n"
        f"🎓 **HEMIS holati:**\n{hemis_status}\n\n"
        f"📊 **Yaratilgan akademik ishlar:**\n"
        f"• 📝 Referatlar: **{user.referats_count} ta**\n"
        f"• 📊 Slaydlar: **{user.slides_count} ta**\n"
        f"• 📑 Mustaqil ishlar: **{user.mustaqil_count} ta**\n"
        f"• 🎯 Test to'plamlari: **{user.quizzes_count} ta**\n"
    )

    kb = InlineKeyboardBuilder()
    if not creds:
        kb.button(text="🔑 HEMIS hisobini ulash", callback_data="hemis_select_univ")
    kb.button(text="◀️ Asosiy menyu", callback_data="btn_main_menu")
    kb.adjust(1)

    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb.as_markup(), parse_mode="Markdown")


@router.message(F.text.in_(["🏠 Bosh menyu", "/menu"]))
@router.callback_query(F.data == "btn_main_menu")
async def back_to_main_menu(event: types.Message | types.CallbackQuery):
    text = "🏛 **Asosiy menyu.** Kerakli xizmatni tanlang:"
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=get_main_menu_inline_keyboard(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=get_main_menu_inline_keyboard(), parse_mode="Markdown")


@router.callback_query(F.data == "btn_help")
async def show_help(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Asosiy menyu", callback_data="btn_main_menu")
    text = (
        "ℹ️ **Talaba AI & HEMIS Assistant haqida**\n\n"
        "Ushbu bot O'zbekiston oliy ta'lim tizimi talabalari uchun yaratilgan professional akademik yordamchidir.\n\n"
        "📌 **Imkoniyatlar:**\n"
        "• OTM standartlaridagi rasmiy Word va PowerPoint hujjatlarini avtomatik yasash;\n"
        "• Dars jadvali va topshiriqlarni Telegramda eslatib turish;\n"
        "• 4 variantli testlar va javoblar kalitini tayyorlash.\n\n"
        "🔐 **Xavfsizlik:** Barcha ma'lumotlar AES-256 shifrlangan."
    )
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")
    await callback.answer()
