from enum import IntEnum


class BotStates(IntEnum):
    START = 1
    SAVE_PHOTO = 2
    PHOTO_PROCESSING = 3
    CREATE_PAYMENT = 4
