import base64

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, \
    ConversationHandler, MessageHandler, filters, CallbackQueryHandler


import logging

from client import FastAPIClient

logging.basicConfig(level=logging.INFO)

class ChatTelegramBot:
    """
    Class Telegram Bot
    """
    def __init__(self, config: dict):
        self.config = config

    START_ROUTES, PHOTO_ROUTES, END_ROUTES = range(3)
    FASTAPI_URL = "http://localhost:8000"

    # Callback data
    ONE, TWO, THREE, FOUR = range(4)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Send message on `/start`."""
        keyboard = [
            [InlineKeyboardButton("Как это работает?", callback_data='how_it_works')],
            # [InlineKeyboardButton("Оплатить", callback_data='pay')],
            # [InlineKeyboardButton("Пригласить друга", callback_data='invite')],
            # [InlineKeyboardButton("Язык", callback_data='language'), InlineKeyboardButton("Поддержка", callback_data='support')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text="Привет! Я бот Shotix\n\n"
                 "Нейросеть, для создания любых фото и видео с твоим лицом\n\n"
                 "Как это работает? Можешь узнать подробнее по кнопке ниже\n\n"
                 "А если сервис уже знаком, то можешь сразу оплатить и перейти к созданию фото.",
            reply_markup=reply_markup
        )
        return self.START_ROUTES

    async def start_over(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        keyboard = [
            [
                InlineKeyboardButton("1", callback_data=str(self.ONE)),
                InlineKeyboardButton("2", callback_data=str(self.TWO)),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Start handler, Choose a route", reply_markup=reply_markup)
        return self.START_ROUTES

    async def two(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Show new choice of buttons"""
        query = update.callback_query
        await query.answer()
        keyboard = [
            [
                InlineKeyboardButton("1", callback_data=str(self.ONE)),
                InlineKeyboardButton("3", callback_data=str(self.THREE)),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Second CallbackQueryHandler, Choose a route", reply_markup=reply_markup)
        return self.START_ROUTES

    async def three(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        keyboard = [
            [
                InlineKeyboardButton("Yes, let's do it again!", callback_data=str(self.ONE)),
                InlineKeyboardButton("Nah, I've had enough ...", callback_data=str(self.TWO)),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Third CallbackQueryHandler. Do want to start over?", reply_markup=reply_markup)
        return self.END_ROUTES

    async def four(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        keyboard = [
            [
                InlineKeyboardButton("2", callback_data=str(self.TWO)),
                InlineKeyboardButton("3", callback_data=str(self.THREE)),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Fourth CallbackQueryHandler, Choose a route", reply_markup=reply_markup)
        return self.START_ROUTES

    async def end(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text="See you next time!")
        return ConversationHandler.END

    async def request_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Ask the user to send a photo."""
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text="Пожалуйста, загрузите фото.")
        return self.PHOTO_ROUTES

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        photo_file = await update.message.photo[-1].get_file()
        await update.message.reply_text("Вызов FastAPI")
        await photo_file.download_to_drive(f"user_photo_{user.id}.jpg")

        file_bytes = await photo_file.download_as_bytearray()

        # Отправка изображения на FastAPI
        data = {
            'name': 'photo',
            'data': base64.b64encode(file_bytes).decode('utf-8')
        }
        client = FastAPIClient(self.FASTAPI_URL)
        response = await client.process_image(data=data)

        if response.get("status") == 200:
            await context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=response.get("content"))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Ошибка обработки изображения")

        await update.message.reply_text("Фото успешно получено и сохранено!")
        return self.PHOTO_ROUTES

    def _application(self) -> None:
        application = ApplicationBuilder().token(self.config['token']).build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                self.START_ROUTES: [
                    CallbackQueryHandler(self.request_photo, pattern="^" + "how_it_works" + "$"),
                ],
                self.PHOTO_ROUTES: [
                    MessageHandler(filters.PHOTO, self.handle_photo),
                ],
                self.END_ROUTES: [
                    CallbackQueryHandler(self.start_over, pattern="^" + str(self.ONE) + "$"),
                ],
            },
            fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, self.end)],
            per_message=False
        )
        application.add_handler(conv_handler)
        # application.run_polling()
        return application
