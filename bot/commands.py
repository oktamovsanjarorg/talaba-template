from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def setup_bot_commands(bot: Bot):
    """
    Telegram menyusidagi rasmiy buyruqlar ro'yxatini o'rnatish.
    """
    commands = [
        BotCommand(command="start", description="🚀 Botni ishga tushirish va menyu"),
        BotCommand(command="referat", description="📝 Akademik referat yozish (Word)"),
        BotCommand(command="slide", description="📊 Taqdimot slaydlari yasash (PPTX)"),
        BotCommand(command="mustaqil", description="📑 Mustaqil ta'lim ishi tayyorlash"),
        BotCommand(command="quiz", description="🎯 Testlar va savollar to'plami"),
        BotCommand(command="summary", description="💡 Aqlli konspekt va xulosachi"),
        BotCommand(command="hemis", description="🎓 HEMIS dars jadvali va deadline"),
        BotCommand(command="profile", description="👤 Shaxsiy profil va statistika"),
        BotCommand(command="help", description="❓ Yordam va qo'llanma"),
        BotCommand(command="cancel", description="❌ Joriy amalni bekor qilish"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
