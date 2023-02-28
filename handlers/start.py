from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from database import AsyncSubscribitions
from config import ADMIN_IDS
from handlers.subscribed import check_subscriptions, unsubscribed


db = AsyncSubscribitions()


async def send_welcome(message: types.Message) -> None:
    user_id = message.from_id
    if not (user_id in ADMIN_IDS):
        subscribed = True
        if not all(
            (
                await db.is_subscribed_to_all(user_id),
                await check_subscriptions(message),
            )
        ):
            subscribed = False

        if not subscribed:
            await unsubscribed(message)
            return

        await message.answer(
            "Hi there! Send me a film code and I'll look up its details."
        )
        return

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("➕ New Film"))
    await message.answer("Welcome! Choose an option:", reply_markup=keyboard)
