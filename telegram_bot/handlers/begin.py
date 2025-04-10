from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.states import BotStates
from telegram_bot.texts import texts
from domain.dto import UserTgModel


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user = UserTgModel.from_update(update)
    paid = await context.bot_data["api_client"].user_payment_info(user.to_dict())

    if not paid.get("paid", False):
        await query.edit_message_text(text=texts["no_payment"])
        return BotStates.CREATE_PAYMENT

    await query.edit_message_text(text=texts["send_photos"])
    return BotStates.SAVE_PHOTO