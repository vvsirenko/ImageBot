from telegram_bot.events import UserEvent


class UserStateAggregate:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.state = "START"
        self.photos = []
        self.events = []

    def add_photo(self, file_id: str):
        self.photos.append(file_id)
        self.events.append(UserEvent("PHOTO_ADDED", {"file_id": file_id}))

    def change_state(self, new_state: str):
        self.state = new_state #Enum ?
        self.events.append(UserEvent("STATE_CHANGED", {"state": new_state}))