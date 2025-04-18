from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from telegram_bot.domain.user import TelegramUser
from telegram_bot.states import BotStates
from telegram_bot.texts import texts
from telegram_bot.user_repository import AbcUserRepository
from telegram_bot.utils import parse_user


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data: dict = parse_user(update)
    user: TelegramUser = TelegramUser(**data)
    repository: AbcUserRepository = context.bot_data["user_repository"]
    await user.fetch_profile(repo=repository)

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
        reply_markup=reply_markup
    )
    return BotStates.START
