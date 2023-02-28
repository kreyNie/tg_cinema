from aiogram import types
from config import ADMIN_IDS
from database import AsyncFilmDatabase, AsyncSubscribitions
from .subscribed import check_subscriptions, unsubscribed


films_db = AsyncFilmDatabase("films.db")
spons_db = AsyncSubscribitions("subscriptions.db")


async def find_film_code(message: types.Message) -> None:
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

    code = message.text
    film = await films_db.get_film(code)
    if film:
        await message.reply(
            f"Here is the information for the film with code {code}:\n\n"
            f"🎞️ Title: {film['title']}\n"
            f"🎬 Director: {film['director']}\n"
            f"📃 Description:\n{film['description']}"
        )
    else:
        await message.reply(
            f"Sorry, I couldn't find any information for the film with code {code}."
        )
