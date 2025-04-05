import base64
import logging
from io import BytesIO

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from api_client.client import FastAPIClient
from application.main import image_caption_generator, zip_creator
from models.api_model import User
from services.caption_generator.caption_service import CaptionService
from services.zip_creator.zip_service import ZipService

logging.basicConfig(level=logging.INFO)


class ChatTelegramBot:
    """Class Telegram Bot
    """

    def __init__(self, config: dict, api_client: FastAPIClient):
        self.config = config
        self.max_photos = 3
        self.photo_count = 0
        self.photo_cache = []  # FIXME глобальный кэш для все пользователей, нужно че-то придумать. + инвалидаця
        self.api_client = api_client
        self._zip_service = ZipService(zip_creator)  # TODO to DI
        self._caption_service = CaptionService(image_caption_generator)  # TODO to DI

    START_ROUTES = 1
    SAVE_PHOTO = 2
    PHOTO_ROUTES = 3
    CREATE_PAYMENT = 4

    # Callback data
    ONE, TWO, THREE, FOUR = range(4)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Send message on `/start`."""
        await self.add_user(user=update.message.from_user)

        support_username = self.config["support_username"]
        support_link = f"https://t.me/{support_username}"

        keyboard = [
            [InlineKeyboardButton("Как это работает?", callback_data="how_it_works")],
            [
                InlineKeyboardButton("Начать", callback_data="begin"),
                InlineKeyboardButton("Связаться с поддержкой", url=support_link),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            text="Привет!\n\n"
                 "Я готов помочь тебе с твоими фото.\n"
                 "Постараюсь сделать их еще более потрясающими.\n\n"
                 "Просто загрузи фото, а я сделаю магию\n\n"
                 "Как это работает? Можешь узнать подробнее по кнопке ниже.\n",
            reply_markup=reply_markup,
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
        await query.edit_message_text(text="Выберите 10 фото, чтобы создать аватар.")
        return self.PHOTO_ROUTES

    async def check_payment_status(self, user_id: int, update: Update) -> bool:
        """Check the user's payment status from FastAPI."""
        response = await self.api_client.user_payment_info(
            user=User(
                id=update.effective_user.id,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name,
                username=update.effective_user.username,
                is_premium=update.effective_user.is_premium,
                language_code=update.effective_user.language_code,
            ),
        )

        return response.get("paid", False)

    async def add_user(self, user) -> bool:
        response = await self.api_client.add_user(user=user)
        return response

    async def begin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        if not await self.check_payment_status(user_id, update):
            await query.edit_message_text(
                text="У вас нет активной оплаты. Пожалуйста, совершите платеж.")
            return self.CREATE_PAYMENT

        await query.edit_message_text(text="Пожалуйста, отправьте свои фото, 10 штук")
        return self.SAVE_PHOTO

    async def next_step(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not self.photo_cache:
            return

        try:
            files_of_bytes = [BytesIO(await file.download_as_bytearray()) for file in self.photo_cache]
            await update.message.reply_text(
                "Фотографии успешно отправлены. Ожидайте ответа от сервера...")

            captions = [await self._caption_service.generate_caption(file_bytes) for file_bytes in files_of_bytes]
            user = User(  # TODO добавить ValueObject для юзера.
                id=update.effective_user.id,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name,
                username=update.effective_user.username,
                is_premium=update.effective_user.is_premium,
                language_code=update.effective_user.language_code,
            )
            zip_archive = await self._zip_service.create_zip(
                files_of_bytes=files_of_bytes,
                captions=captions,
                user=user,
            )
            response = await self.api_client.upload_zip(
                zip_archive=zip_archive,
                user=user,
            )
            if response:
                await update.message.reply_text(f"Сохранено {len(self.photo_cache)} фото!")
            else:
                await update.message.reply_text("Что-то пошло не так. Попробуйте еще раз.")
        except Exception:
            await update.message.reply_text("Что пошло не так")

    async def save_user_photos(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not update.message.photo:
            return None

        file = await update.message.photo[-1].get_file()
        self.photo_cache.append(file)

        self.photo_count += 1
        text = f"Фотография {self.photo_count} сохранена. Осталось загрузить {self.max_photos - self.photo_count} фотографий."

        if hasattr(self, "status_message") and self.status_message:
            await self.status_message.edit_text(text)
        else:
            self.status_message = await update.message.reply_text(text)

        if self.photo_count >= self.max_photos:
            return await self.next_step(update, context)

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        photo_file = await update.message.photo[-1].get_file()

        await update.message.reply_text("Вызов FastAPI")
        await photo_file.download_to_drive(f"user_photo_{user.id}.jpg")
        file_bytes = await photo_file.download_as_bytearray()

        data = {
            "name": "photo",
            "data": base64.b64encode(file_bytes).decode("utf-8"),
        }
        await update.message.reply_text("Фото успешно получено и сохранено!")
        return self.PHOTO_ROUTES

    def _application(self) -> None:
        application = ApplicationBuilder().token(self.config["token"]).build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                self.START_ROUTES: [
                    CallbackQueryHandler(self.how_it_works, pattern="^" + "how_it_works" + "$"),
                    CallbackQueryHandler(self.begin, pattern="^" + "begin" + "$"),
                ],
                self.SAVE_PHOTO: [
                    MessageHandler(filters.PHOTO, self.save_user_photos),
                ],
                self.PHOTO_ROUTES: [
                    MessageHandler(filters.PHOTO, self.handle_photo),
                ],
            },
            fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, self.end)],
            per_message=False,
        )
        application.add_handler(conv_handler)
        # application.run_polling()
        return application
