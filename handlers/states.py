from aiogram.dispatcher.filters.state import State, StatesGroup


class FilmState(StatesGroup):
    code = State()
    title = State()
    director = State()
    year = State()
    description = State()


class AddingState(StatesGroup):
    add_sponsor = State()
    remove_sponsor = State()
