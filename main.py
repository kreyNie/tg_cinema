import logging

from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor

from config import ADMIN_IDS, DEBUG, bot
from handlers import film_code, start, subscribed
from handlers.admin import AsyncSponsor, FilmProcess, cancel_handler
from handlers.states import AddingState, FilmState

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    filename="app.log",
    filemode="a",
    format="%(asctime)s %(levelname)s %(message)s",
)


dp.register_message_handler(
    lambda message: start.send_welcome(message),
    commands=["start"],
)
dp.register_message_handler(
    film_code.find_film_code,
    regexp=r"\d+",
)
dp.register_message_handler(
    lambda message: message.from_id in AsyncSponsor,
    FilmProcess.add_new_film,
    commands=["add_film"],
)
dp.register_message_handler(
    lambda message: message.from_id in ADMIN_IDS,
    AsyncSponsor.add_state,
    commands=["add_sponsor"],
)
dp.register_message_handler(
    lambda message: message.from_id in ADMIN_IDS,
    AsyncSponsor.add_sponsor,
    regexp=r"@(\w+)",
    state=AddingState.add_sponsor,
)
dp.register_message_handler(
    lambda message: message.from_id in ADMIN_IDS,
    AsyncSponsor.get_sponsors,
    commands=["get_sponsors"],
)
dp.register_message_handler(
    lambda message: message.from_id in ADMIN_IDS,
    AsyncSponsor.remove_state,
    commands=["remove_sponsor"],
)
dp.register_message_handler(
    lambda message: message.from_id in ADMIN_IDS,
    AsyncSponsor.remove_sponsor,
    regexp=r"@(\w+)",
    state=AddingState.remove_sponsor,
)
dp.register_message_handler(
    lambda message: cancel_handler(message, dp.current_state()),
    Text("q"),
    state="*",
)
dp.register_message_handler(FilmProcess.process_film_code, state=FilmState.code)
dp.register_message_handler(FilmProcess.process_film_title, state=FilmState.title)
dp.register_message_handler(FilmProcess.process_film_director, state=FilmState.director)
dp.register_message_handler(FilmProcess.process_film_year, state=FilmState.year)
dp.register_message_handler(
    FilmProcess.process_film_description, state=FilmState.description
)

dp.register_callback_query_handler(
    lambda callback_query: subscribed.check_subs_handler(callback_query),
    text="check_subs",
)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
