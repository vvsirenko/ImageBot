from telegram import Update
from telegram.ext import ContextTypes

from domain.user import TelegramUser
from telegram_bot.states import BotStates
from telegram_bot.texts import texts
from infrastructure.user_repository import AbcUserRepository
from telegram_bot.utils import parse_user


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    data: dict = parse_user(update)
    user: TelegramUser = TelegramUser(**data)
    repository: AbcUserRepository = context.bot_data["user_repository"]
    # UseCase payment
    await query.edit_message_text(
        text=texts["do_payment"]
    )
    return BotStates.SAVE_PHOTO