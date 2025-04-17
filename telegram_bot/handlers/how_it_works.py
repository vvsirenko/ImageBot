from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.states import BotStates
from telegram_bot.texts import texts


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=texts["how_it_works"])
    return BotStates.PHOTO_PROCESSING