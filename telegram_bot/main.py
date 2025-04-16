import logging

from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from api_client.client import FastAPIClient

from services.caption_service.caption_service import CaptionService
from services.zip_service.zip_service import ZipService
from telegram_bot.handlers import start, how_it_works, begin, end, photos
from telegram_bot.states import BotStates

from telegram_bot.containers import Container
from telegram_bot.user_repository import AbcUserRepository
from telegram_bot.user_service import UserService

logging.basicConfig(level=logging.INFO)


class ChatTelegramBot:
    def __init__(
            self,
            config: dict,
            zip_service: ZipService,
            caption_service: CaptionService,
            max_photos: int,
            user_repository: AbcUserRepository
    ):
        self.config = config
        self.max_photos = max_photos
        self.user_service = UserService
        self._zip_service = zip_service
        self._caption_service = caption_service
        self.user_repository = user_repository

    def build(self):
        app = ApplicationBuilder().token(self.config["token"]).build()

        # зависимости
        app.bot_data["support_url"] = f"https://t.me/{self.config['support_username']}"
        app.bot_data["max_photos"] = self.max_photos
        app.bot_data["user_repository"] = self.user_repository
        # app.bot_data["api_client"] = self.api_client
        # app.bot_data["zip_service"] = self._zip_service
        # app.bot_data["caption_service"] = self._caption_service

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start.handler)],
            states={
                BotStates.START: [
                    CallbackQueryHandler(how_it_works.handler, pattern="^" + "how_it_works" + "$"),
                    CallbackQueryHandler(begin.handler, pattern="^" + "begin" + "$"),
                ],
                BotStates.SAVE_PHOTO: [
                    MessageHandler(filters.PHOTO, photos.save),
                ]
            },
            fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, end.handler)],
            per_message=False,
        )
        app.add_handler(conv_handler)
        # application.run_polling()
        return app