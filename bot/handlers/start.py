from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.user_service import user_service

router = Router()


def get_main_menu_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Referat tayyorlash (Word)", callback_data="btn_referat")
    kb.button(text="📊 Slayd tayyorlash (PPTX)", callback_data="btn_slide")
    kb.button(text="📑 Mustaqil Ta'lim Ishi", callback_data="btn_mustaqil")
    kb.button(text="🎯 Testlar va Nazorat (Quiz)", callback_data="btn_quiz")
    kb.button(text="💡 Aqlli Konspekt", callback_data="btn_summary")
    kb.button(text="🎓 HEMIS Integratsiyasi", callback_data="btn_hemis")
    kb.button(text="👤 Shaxsiy Profil", callback_data="btn_profile")
    kb.button(text="❓ Bot haqida / Yordam", callback_data="btn_help")
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
        "Bot orqali quyidagi akademik va ta'lim xizmatlaridan foydalanishingiz mumkin:\n"
        "• OTM standartlaridagi **Referat** va **Mustaqil ishlar** (Word)\n"
        "• 16:9 formatdagi zamonaviy **Taqdimotlar** (PowerPoint)\n"
        "• 4 variantli **Testlar (Quiz)** va javoblar kaliti\n"
        "• **HEMIS** dars jadvali va deadline eslatmalari\n\n"
        "Kerakli bo'limni tanlang:"
    )
    await message.answer(text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")


@router.message(Command("menu"))
@router.callback_query(F.data == "btn_main_menu")
async def back_to_main_menu(event: types.Message | types.CallbackQuery):
    text = "🏛 **Asosiy menyu.** Kerakli xizmatni tanlang:"
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")


# SHAXSIY PROFIL
@router.message(Command("profile"))
@router.callback_query(F.data == "btn_profile")
async def show_profile(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    user = await user_service.get_or_create(user_id, event.from_user.full_name, event.from_user.username)
    creds = await user_service.get_hemis_credentials(user_id)

    hemis_status = f"✅ Ulangan (`{creds['domain']}`)" if creds else "❌ Ulanmagan"

    text = (
        f"👤 **Foydalanuvchi Profili**\n\n"
        f"🆔 Telegram ID: `{user.id}`\n"
        f"👤 Ism: **{user.full_name}**\n"
        f"🎓 HEMIS holati: {hemis_status}\n"
        f"📅 A'zo bo'lgan vaqti: `{user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else 'Yangi'}`\n\n"
        f"📊 **Foydalanish statistikasi:**\n"
        f"• Yaratilgan referatlar: **{user.referats_count} ta**\n"
        f"• Yaratilgan slaydlar: **{user.slides_count} ta**\n"
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


@router.callback_query(F.data == "btn_help")
async def show_help(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Asosiy menyu", callback_data="btn_main_menu")
    text = (
        "ℹ️ **Talaba AI haqida ma'lumot**\n\n"
        "Ushbu bot O'zbekiston oliy ta'lim muassasalari talabalarining o'quv jarayonini "
        "yengillashtirish uchun yaratilgan to'liq mustaqil ekotizimdir.\n\n"
        "🤖 **AI Model:** Alibaba Cloud Qwen (High Performance)\n"
        "🏛 **Akademik Standart:** Times New Roman 14, 1.5 interval, Rasmiy Titul varag'i\n"
        "🔐 **Xavfsizlik:** AES-256 shifrlangan ma'lumotlar ombori\n"
        "⚡ **Baza va Kesh:** PostgreSQL 16 + Redis 7"
    )
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")
    await callback.answer()
