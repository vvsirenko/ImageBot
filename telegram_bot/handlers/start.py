from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from domain.dto import UserTgModel
from telegram_bot.states import BotStates
from telegram_bot.texts import texts


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = UserTgModel.from_update(update)
    await context.bot_data['api_client'].add_user(user.to_dict())

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
