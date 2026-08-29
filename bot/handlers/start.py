from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Referat tayyorlash (Word)", callback_data="btn_referat")
    kb.button(text="📊 Slayd tayyorlash (PPTX)", callback_data="btn_slide")
    kb.button(text="🎓 HEMIS Integratsiyasi", callback_data="btn_hemis")
    kb.button(text="⚙️ Yordam / Ma'lumot", callback_data="btn_help")
    kb.adjust(1)

    text = (
        f"Assalomu alaykum, {message.from_user.first_name}!\n\n"
        "🎓 **Talaba AI & HEMIS Assistant** ekotizimiga xush kelibsiz.\n\n"
        "Bu bot sizga nimalarda yordam beradi:\n"
        "• OTM standartlariga mos **Referat (DOCX)** tayyorlash;\n"
        "• Zamonaviy dizayndagi **Slayd (PPTX)** yasash;\n"
        "• **HEMIS** dars jadvali va topshiriq muddatlarini eslatish.\n\n"
        "Quyidagi bo'limlardan birini tanlang:"
    )
    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="Markdown")
