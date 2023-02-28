from aiogram import types

from config import bot
from database import AsyncSubscribitions
from .tg_utils import TelegramUtils

db = AsyncSubscribitions()


async def check_subscriptions(user_id: int) -> bool:
    for channel in await db.get_sponsors():
        if not await TelegramUtils.is_member(channel, user_id):
            return False

    return True


async def check_subs_handler(callback_query: types.CallbackQuery) -> None:
    user_id = callback_query.from_user.id

    subscribed = await check_subscriptions(user_id)

    answer = "You have not subscribed to all channels!"
    if subscribed:
        answer = "Have a great day!"
        await db.update_subscription_status(user_id, True)
    await bot.answer_callback_query(callback_query.id, answer)


async def unsubscribed(message: types.Message) -> None:
    sponsor_list = await db.get_sponsors()
    await message.answer(
        "You have not subscribed to all sponsor channels. Please subscribe:\n"
        + "\n".join(sponsor_list)
    )
    keyboard = types.InlineKeyboardMarkup()
    check_button = types.InlineKeyboardButton(
        text="✅ Check subscriptions", callback_data="check_subs"
    )
    keyboard.add(check_button)
    await message.answer(
        "Press the button to update your subscriptions", reply_markup=keyboard
    )
