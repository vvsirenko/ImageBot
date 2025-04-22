from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
    payment_info = await user.fetch_payment_info(repo=repository)

    if not payment_info:
        keyboard = [
            [InlineKeyboardButton("Оплатить", callback_data="do_payment")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=texts["no_payment"], reply_markup=reply_markup)
        return BotStates.CREATE_PAYMENT

    await query.edit_message_text(text=texts["send_photos"])
    return BotStates.SAVE_PHOTO