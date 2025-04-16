from telegram import Update


def parse_user(update: Update) -> dict:
    user = update.effective_user

    if not user:
        raise ValueError("User is not found")

    return {
        "id": user.id,
        "username": user.username or "",
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "is_bot": bool(user.is_bot),
        "is_premium": bool(user.is_premium),
        "language_code": user.language_code or ""
    }
