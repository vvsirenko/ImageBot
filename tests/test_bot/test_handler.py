from unittest.mock import MagicMock, AsyncMock

import pytest
from telegram.ext import ContextTypes
from telegram import User, InlineKeyboardMarkup, CallbackQuery

from telegram_bot.containers import Container
from telegram_bot.handlers.start import handler as start_handler
from telegram_bot.handlers.how_it_works import handler as how_it_works_handler
from telegram_bot.states import BotStates
from telegram_bot.user_repository import UserRepository
from telegram_bot.user_service import UserService


@pytest.fixture
def update():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.text = "/start"
    update.effective_user = User(
        first_name='Иван',
        id=789456562,
        is_bot=False,
        is_premium=True,
        language_code='ru',
        last_name='Иванов',
        username='ivanovii'
    )
    update.callback_query = AsyncMock()
    return update


@pytest.fixture
def context():
    user_repository = UserRepository("http://")
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot_data = {
        "user_repository": user_repository,
        "support_url": "https://t.me/support"
    }
    return context


async def test_start_handler(context, update):
    result = await start_handler(update, context)

    args, kwargs = update.message.reply_text.call_args
    assert "text" in kwargs
    assert "reply_markup" in kwargs
    assert isinstance(kwargs["reply_markup"], InlineKeyboardMarkup)

    buttons = kwargs["reply_markup"].inline_keyboard
    assert buttons[0][0].text == "Как это работает?"
    assert buttons[1][0].text == "Начать"
    assert buttons[1][1].url == "https://t.me/support"

    assert result == BotStates.START
    assert context.user_data["profile"] is not None

async def test_how_it_work_handler(context, update):
    result = await how_it_works_handler(update, context)

    args, kwargs = update.callback_query.edit_message_text.call_args
    assert "text" in kwargs

    text = kwargs["text"]
    assert text is not None and  isinstance(text, str)
    assert result == BotStates.PHOTO_PROCESSING
