from aiogram import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import ADMIN_IDS, bot
from handlers import start
from handlers import film_code
from handlers import subscribed
from handlers.admin import FilmProcess, AsyncSponsor, cancel_handler
from handlers.states import FilmState, AddingState

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


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
