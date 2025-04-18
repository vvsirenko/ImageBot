import asyncio
import os
import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI

from api_client.client import FastAPIClient
from telegram_bot import ChatTelegramBot
from rest_api.routes import router as telegram_router


def create_bot():
    load_dotenv()

    FASTAPI_URL = "http://localhost:8000"
    api_client = FastAPIClient(FASTAPI_URL)

    # Setup configuration
    telegram_config = {
        'token': os.environ.get('TELEGRAM_BOT_TOKEN', ""),
        'timeweb_cloud_token': os.environ.get('TIMEWEB_CLOUD_TOKEN', ""),
        'timeweb_cloud_url': os.environ.get('TIMEWEB_CLOUD_URL', ""),
        'support_username': os.environ.get('SUPPORT_USERNAME', "")
    }

    telegram_bot = ChatTelegramBot(config=telegram_config,
                                   api_client=api_client)
    return telegram_bot


app = FastAPI()
app.include_router(telegram_router)

bot: ChatTelegramBot = create_bot()
application = bot._application()


async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)

    async with application:
        await application.start()
        await application.updater.start_polling()

        await server.serve()

        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    asyncio.run(main())







