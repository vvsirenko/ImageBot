from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from telegram_bot.states import BotStates
from telegram_bot.texts import texts


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data: dict = parse_user(update)
    user = TelegramUser(**data)
    await user.fetch_profile(user, repository=None)

    keyboard = [
        [InlineKeyboardButton("Как это работает?", callback_data="how_it_works")],
        [
            InlineKeyboardButton("Начать", callback_data="begin"),
            InlineKeyboardButton("Связаться с поддержкой", url=context.bot_data["support_url"]),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=texts["start_message"],
        reply_markup=reply_markup,
    )
    return BotStates.START
