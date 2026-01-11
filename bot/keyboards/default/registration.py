from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_fullname_keyboard(first_name: str, last_name: str = "") -> ReplyKeyboardMarkup:
    """
    Telegram first_name va last_name asosida default tugma yaratadi.
    """
    full_name = f"{first_name} {last_name}".strip()
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=full_name)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """
    Telefon raqamni yuborish uchun contact tugmasi.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard
