from typing import Any
from aiogram.dispatcher.storage import BaseStorage


class MemoryStorage(BaseStorage):
    def __init__(self) -> None:
        self.memory = {}

    async def get_data(self, chat, user) -> Any | dict:
        chat = str(chat)
        user = str(user)
        return self.memory.get(chat, {}).get(user, {})

    async def set_data(self, chat, user, data) -> None:
        chat = str(chat)
        user = str(user)
        if chat not in self.memory:
            self.memory[chat] = {}
        self.memory[chat][user] = data
