from telegram_bot.events import UserEvent


class UserProfileAggregate:
    def __init__(self, user_id: int, username: str, full_name: str):
        self.user_id = user_id
        self.username = username
        self.full_name = full_name
        self.events = []

    def update_profile(self, new_username: str, new_full_name: str):
        self.username = new_username
        self.full_name = new_full_name
        self.events.append(UserEvent("PROFILE_UPDATED", self.to_dict()))

    def to_dict(self):
        return {
            "id": self.user_id,
            "username": self.username,
            "full_name": self.full_name
        }