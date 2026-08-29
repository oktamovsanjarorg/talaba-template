from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.user_service import user_service

router = Router()


def get_main_menu_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Referat tayyorlash (Word)", callback_data="btn_referat")
    kb.button(text="📊 Slayd tayyorlash (PPTX)", callback_data="btn_slide")
    kb.button(text="🎓 HEMIS Integratsiyasi", callback_data="btn_hemis")
    kb.button(text="❓ Bot haqida / Yordam", callback_data="btn_help")
    kb.adjust(1)
    return kb.as_markup()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    # Bazada foydalanuvchini yaratish yoki yangilash
    await user_service.get_or_create(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )

    text = (
        f"Assalomu alaykum, {message.from_user.first_name}!\n\n"
        "🎓 **Talaba AI & HEMIS Assistant** ekotizimiga xush kelibsiz.\n\n"
        "Bu bot sizga nimalarda yordam beradi:\n"
        "• OTM standartlariga mos **Referat (DOCX)** tayyorlash;\n"
        "• Zamonaviy dizayndagi **Slayd (PPTX)** yasash;\n"
        "• **HEMIS** dars jadvali va topshiriq muddatlarini eslatish.\n\n"
        "Quyidagi bo'limlardan birini tanlang:"
    )
    await message.answer(text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")


@router.callback_query(F.data == "btn_main_menu")
async def back_to_main_menu(callback: types.CallbackQuery):
    text = "Asosiy menyu. Kerakli xizmatni tanlang:"
    await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "btn_help")
async def show_help(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Asosiy menyu", callback_data="btn_main_menu")
    text = (
        "ℹ️ **Bot haqida ma'lumot**\n\n"
        "Ushbu bot O'zbekiston oliy ta'lim muassasalari talabalarining o'quv jarayonini "
        "yengillashtirish uchun yaratilgan.\n\n"
        "🤖 **AI Model:** Alibaba Cloud Qwen (High Performance)\n"
        "🏛 **Standart:** OTM akademik talablari (Times New Roman 14, 1.5 interval)\n"
        "🔐 **Xavfsizlik:** AES-256 shifrlash tizimi\n"
        "🚀 **Infratuzilma:** Docker, Redis, PostgreSQL (Production-Grade)"
    )
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")
    await callback.answer()
