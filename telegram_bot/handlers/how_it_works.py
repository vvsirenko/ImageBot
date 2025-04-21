from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from telegram_bot.states import BotStates
from telegram_bot.texts import texts


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Начать творить", callback_data="begin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=texts["how_it_works"], reply_markup=reply_markup
    )
    return BotStates.PHOTO_PROCESSING