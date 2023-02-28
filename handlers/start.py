from aiogram import types

from database import AsyncSubscribitions
from config import ADMIN_IDS
from handlers.subscribed import check_subscriptions, unsubscribed


spons_db = AsyncSubscribitions()


async def send_welcome(message: types.Message) -> None:
    user_id = message.from_id
    if not (user_id in ADMIN_IDS):
        subscribed = (
            True
            if all(
                (
                    await spons_db.is_subscribed_to_all(user_id),
                    await check_subscriptions(user_id),
                )
            )
            else False
        )

        if not subscribed:
            await unsubscribed(message)
            return

        await message.answer(
            "Hi there! Send me a film code and I'll look up its details."
        )
        return

    await message.answer(
        "Welcome! Here are admin commands:\n\n"
        "*/add_film* - _add new film to bot's database_\n"
        "*/add_sponsor* - _add new sponsor to bot's database_\n"
        "*/get_sponsors* - _get list of all sponsors_\n"
        "*/remove_sponsor* - _remove a certain sponsor from bot's database_",
        parse_mode="Markdown",
    )
