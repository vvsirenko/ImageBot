from io import BytesIO
from telegram import Update
from telegram.ext import ContextTypes
from domain.dto import UserTgModel
from telegram_bot.states import BotStates
from telegram_bot.texts import texts
from telegram_bot.user_stage import UserStateAggregate


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.photo:
        return BotStates.SAVE_PHOTO

    file = await update.message.photo[-1].get_file()


    # Загружаем или создаём агрегат состояния
    # state_data = container.user_data_repository.get_user_state(update.effective_user.id)
    # user_state = UserStateAggregate(user_id=update.effective_user.id)
    # user_state.state = state_data["state"]
    # user_state.photos = state_data["photos"] # todo как управлять стейтами?
    # user_state.add_photo(file.file_id) # ????

    photos = context.user_data.get("photos", []) #todo fix it как долго тут будут храниться данные и не лучше ли юзать Redis?
    photos.append(file)
    context.user_data["photos"] = photos

    photo_count = len(photos)
    max_photos = context.bot_data.get("max_photos", 10)
    remaining = max_photos - photo_count
    text = texts["photo_saved"].format(count=photo_count, remaining=remaining)

    if "status_message" in context.user_data:
        await context.user_data["status_message"].edit_text(text)
    else:
        context.user_data["status_message"] = await update.message.reply_text(text)

    if photo_count >= max_photos:
        return await next_step(update, context)
    return BotStates.SAVE_PHOTO


async def next_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photos = context.user_data.get("photos", [])
    if not photos:
        return BotStates.SAVE_PHOTO

    try:
        files_of_bytes = [BytesIO(await f.download_as_bytearray()) for f in photos]
        await update.message.reply_text(texts["processing"])

        caption_service = context.bot_data["caption_service"]
        zip_service = context.bot_data["zip_service"]
        api_client = context.bot_data["api_client"]

        captions = [await caption_service.generate_caption(file) for file in files_of_bytes]
        user = UserTgModel.from_update(update).to_dict()

        zip_archive = await zip_service.create_zip(
            files_of_bytes=files_of_bytes,
            captions=captions,
            user=user
        )
        response = await api_client.upload_zip(
            zip_archive=zip_archive,
            user=user
        )

        if response:
            await update.message.reply_text(texts["success"].format(count=len(photos)))
        else:
            await update.message.reply_text(texts["failure"])

    except Exception as e:
        await update.message.reply_text(texts["exception"])

    return BotStates.START


async def handlerE(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    container = context.bot_data["container"]
    file = await update.message.photo[-1].get_file()
    file_id = file.file_id

    # Загружаем или создаём агрегат состояния
    state_data = container.user_data_repository.get_user_state(update.effective_user.id)
    user_state = UserStateAggregate(user_id=update.effective_user.id)
    user_state.state = state_data["state"]
    user_state.photos = state_data["photos"]

    user_state.add_photo(file_id)

    # Сохраняем
    container.user_data_repository.save_state(user_state)
    container.user_data_repository.save_events(user_state.user_id, user_state.events)

    await update.message.reply_text("Фото сохранено. Отправьте ещё.")
    return BotStates.SAVE_PHOTO