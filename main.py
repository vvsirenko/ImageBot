import asyncio
import os
import threading

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from telegram_bot import ChatTelegramBot
from routes import router as telegram_router

from telegram.ext import Application, ApplicationBuilder


def create_bot():
    load_dotenv()

    # Setup configuration
    telegram_config = {
        'token': os.environ.get('TELEGRAM_BOT_TOKEN', "")
    }

    telegram_bot = ChatTelegramBot(config=telegram_config)
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

