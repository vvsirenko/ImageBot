import base64
import time
from io import BytesIO

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, \
    ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from api_client.client import FastAPIClient

import logging

logging.basicConfig(level=logging.INFO)


class ChatTelegramBot:
    """
    Class Telegram Bot
    """
    def __init__(self, config: dict, api_client: FastAPIClient):
        self.config = config
        self.max_photos = 3
        self.photo_count = 0
        self.photo_casche = []
        self.api_client = api_client

    START_ROUTES = 1
    SAVE_PHOTO = 2
    PHOTO_ROUTES = 3

    # Callback data
    ONE, TWO, THREE, FOUR = range(4)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Send message on `/start`."""
        keyboard = [
            [InlineKeyboardButton("Как это работает?", callback_data='how_it_works'), InlineKeyboardButton("Начать", callback_data='begin')],
            [InlineKeyboardButton("Поддержка", callback_data='support')]
            # [InlineKeyboardButton("Пригласить друга", callback_data='invite')],
            # [InlineKeyboardButton("Язык", callback_data='language'), ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text="Привет!\n\n"
                 "Я готов помочь тебе с твоими фото.\n"
                 "Постараюсь сделать их еще более потрясающими.\n\n"
                 "Просто загрузи фото, а я сделаю магию\n\n"
                 "Как это работает? Можешь узнать подробнее по кнопке ниже.\n",
            reply_markup=reply_markup
        )
        return self.START_ROUTES

    async def end(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text="See you next time!")
        return ConversationHandler.END

    async def how_it_works(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text="Пожалуйста, загрузите фото.")
        return self.PHOTO_ROUTES

    async def begin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text="Пожалуйста, отправьте свои фото, 10 штук")
        return self.SAVE_PHOTO

    async def next_step(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not self.photo_casche:
            return

        try:
            files_of_bytes = [BytesIO(await file.download_as_bytearray()) for file in self.photo_casche]
            await update.message.reply_text(
                f"Фотографии успешно отправлены. Ожидайте ответа от сервера...")
            response = await self.api_client.upload_zip(
                files_of_bytes=files_of_bytes,
                user=update.message.from_user
            )
            if response:
                await update.message.reply_text(f"Сохранено {len(self.photo_casche)} фото!")
            else:
                await update.message.reply_text(f"Что-то пошло не так. Попробуйте еще раз.")
        except Exception as e:
            await update.message.reply_text(f"Что пошло не так")

    async def save_user_photos(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not update.message.photo:
            return

        file = await update.message.photo[-1].get_file()
        self.photo_casche.append(file)

        self.photo_count += 1
        if self.photo_count >= self.max_photos:
            return await self.next_step(update, context)
        else:
            await update.message.reply_text(
                f"Фотография {self.photo_count} сохранена. Осталось загрузить {self.max_photos - self.photo_count} фотографий.")

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        photo_file = await update.message.photo[-1].get_file()

        await update.message.reply_text("Вызов FastAPI")
        await photo_file.download_to_drive(f"user_photo_{user.id}.jpg")
        file_bytes = await photo_file.download_as_bytearray()

        data = {
            'name': 'photo',
            'data': base64.b64encode(file_bytes).decode('utf-8')
        }
        await update.message.reply_text("Фото успешно получено и сохранено!")
        return self.PHOTO_ROUTES

    def _application(self) -> None:
        application = ApplicationBuilder().token(self.config['token']).build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                self.START_ROUTES: [
                    CallbackQueryHandler(self.how_it_works, pattern="^" + "how_it_works" + "$"),
                    CallbackQueryHandler(self.begin, pattern="^" + "begin" + "$")
                ],
                self.SAVE_PHOTO: [
                    MessageHandler(filters.PHOTO, self.save_user_photos)
                ],
                self.PHOTO_ROUTES: [
                    MessageHandler(filters.PHOTO, self.handle_photo),
                ]
            },
            fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, self.end)],
            per_message=False
        )
        application.add_handler(conv_handler)
        # application.run_polling()
        return application
