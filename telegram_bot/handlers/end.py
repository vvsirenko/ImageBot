from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="До встречи!")
    return ConversationHandler.END