from config import bot
from aiogram.utils.exceptions import BadRequest


class TelegramUtils:
    @staticmethod
    async def is_member(channel_name: str, user_id: int) -> bool:
        try:
            result = await bot.get_chat_member(channel_name, user_id)
            if result.status == "left":
                return False
        except BadRequest as e:
            error_message = e.args[0]
            if error_message.lower() == "invalid user_id specified":
                return False
        else:
            return True
