from services.caption_service.caption_service import CaptionService
from services.zip_service.zip_service import ZipService
from telegram_bot.user_service import UserService


class Container:
    def __init__(
            self,
            config: dict,
            user_service: UserService,
            zip_service: ZipService,
            caption_service: CaptionService
    ):
        self.config = config
        self.user_service = user_service
        self.zip_service = zip_service
        self.caption_service = caption_service
