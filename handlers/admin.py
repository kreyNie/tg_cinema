from aiogram import types
from aiogram.dispatcher import FSMContext


from database import AsyncFilmDatabase, AsyncSubscribitions
from .states import FilmState, AddingState


films_db = AsyncFilmDatabase("films.db")
sponsor_db = AsyncSubscribitions("subscriptions.db")


async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    if await state.get_state():
        await state.reset_state()
    await message.answer("Operation canceled. Please start again.")


class FilmProcess:
    @staticmethod
    async def add_new_film(message: types.Message) -> None:
        await FilmState.code.set()
        await message.answer(
            "OK! Adding new film. To cancel, you can send 'q' on any step of adding info\n"
            "Enter film code:"
        )

    @staticmethod
    async def process_film_code(message: types.Message, state: FSMContext) -> None:
        exists = await films_db.get_film(message.text)
        if exists:
            await message.reply(
                "Film with this code is already exists! Choose another one code"
            )
            return

        await state.set_data({"code": message.text})

        await FilmState.title.set()
        await message.answer("Enter film title:")

    @staticmethod
    async def process_film_title(message: types.Message, state: FSMContext) -> None:
        film_state = await state.get_data()
        film_state["title"] = message.text
        await state.set_data(film_state)

        await FilmState.director.set()
        await message.answer("Enter film director:")

    @staticmethod
    async def process_film_director(message: types.Message, state: FSMContext) -> None:
        film_state = await state.get_data()
        film_state["director"] = message.text
        await state.set_data(film_state)
        await FilmState.year.set()
        await message.answer("Enter film year:")

    @staticmethod
    async def process_film_year(message: types.Message, state: FSMContext) -> None:
        film_state = await state.get_data()
        film_state["year"] = message.text
        await state.set_data(film_state)
        await FilmState.description.set()
        await message.answer("Enter film description:")

    @staticmethod
    async def process_film_description(
        message: types.Message, state: FSMContext
    ) -> None:
        film_state = await state.get_data()
        film_state["description"] = message.text
        await state.set_data(film_state)

        film_state = await state.get_data()
        await state.reset_state()
        await films_db.add_film(*film_state.values())
        await message.answer("✅ Film added")


class AsyncSponsor:
    @staticmethod
    async def add_state(message: types.Message) -> None:
        await message.answer('Type "q" for quit adding')
        await message.answer(
            "⚠️ NOTE ⚠️\n"
            "After updating (adding or removing) sponsors all users "
            "will be automatically set to unsubscribed state\n\n"
            'You should write sponsors like "@your_sponsor_channel" (without quotes)\n\n'
            "⚠️ NOTE ⚠️\n"
            "Bot should be an admin in your sponsor's channel to check if user is in the channel"
        )
        await AddingState.add_sponsor.set()

    @staticmethod
    async def add_sponsor(message: types.Message) -> None:
        sponsor_name = message.text
        if await sponsor_db.is_in(sponsor_name):
            await message.answer(f"{sponsor_name} is already in database!")
            return

        await sponsor_db.add_sponsor(sponsor_name)
        await message.answer(
            f'Channel "{sponsor_name}" has been *added*', parse_mode="Markdown"
        )

    @staticmethod
    async def get_sponsors(message: types.Message) -> None:
        sponsor_list = await sponsor_db.get_sponsors()
        await message.answer("Current sponsor list:\n" + "\n".join(sponsor_list))

    @staticmethod
    async def remove_state(message: types.Message) -> None:
        await message.answer('Type "q" for quit adding')
        await message.answer(
            "⚠️ NOTE ⚠️\n"
            "After updating (adding or removing) sponsors all users "
            "will be automatically set to unsubscribed state\n\n"
            'You should write sponsors like "@your_sponsor_channel" (without quotes)'
        )
        await AddingState.remove_sponsor.set()

    @staticmethod
    async def remove_sponsor(message: types.Message) -> None:
        sponsor_name = message.text
        if not await sponsor_db.is_in(sponsor_name):
            await message.answer(f"There is no {sponsor_name} in sponsor list!")
            return

        await sponsor_db.remove_sponsor(message.text)
        await message.answer(
            f'Channel "{message.text}" has been *removed*', parse_mode="Markdown"
        )
