import sqlite3
from typing import Dict, List

import aiosqlite

from .base import Database


class AsyncFilmDatabase(Database):
    """Class for working with films database

    :param Database: parent class
    :type Database: Database
    """

    def __init__(self, db_file: str = "films.db", name: str = "films") -> None:
        """Create films database object

        :param db_file: path to database, defaults to "films.db"
        :type db_file: str, optional
        :param name: table's name, defaults to "films"
        :type name: str, optional
        """
        super().__init__(db_file)
        self.name = name
        self.columns = {
            "code": "INT PRIMARY KEY UNIQUE NOT NULL",
            "title": "VARCHAR(50) NOT NULL",
            "director": "VARCHAR(50) NOT NULL",
            "year": "INT NOT NULL",
            "description": "TEXT NOT NULL",
        }
        self.init_database(self.name, self.columns)

    async def get_film(self, code: int) -> Dict[int, str | int]:
        return await self.get_item(self.name, "code=?", (code,))

    async def add_film(
        self, code: int, title: str, director: str, year: int, description: str
    ) -> None:
        await self.add_values(
            self.name,
            {
                "code": code,
                "title": title,
                "director": director,
                "year": year,
                "description": description,
            },
        )

    async def remove_film(self, code: int) -> None:
        await self.remove_values(self.name, f"code={code}")

    async def list_films(self) -> List[int | str]:
        async with aiosqlite.connect(self._db_file) as db:
            async with db.execute("SELECT code FROM films") as cursor:
                return [row[0] for row in await cursor.fetchall()]


class AsyncSubscribitions(Database):
    def __init__(
        self, db_file: str = "subscriptions.db", name: str = "subscriptions"
    ) -> None:
        """Class for working with sponsors' channels

        :param db_file: path to database file, defaults to "subscriptions.db"
        :type db_file: str, optional
        :param name: main table's name, defaults to "subscriptions"
        :type name: str, optional
        """
        super().__init__(db_file)
        self.name = name
        self.columns = {
            "user_id": "INTEGER NOT NULL PRIMARY KEY",
            "subscribed": "BOOLEAN DEFAULT 0",
        }
        self.channel_table = "channels"
        self.channel_columns = {
            "channel_name": "TEXT NOT NULL",
        }
        self.init_database(self.name, self.columns)
        self.init_database(self.channel_table, self.channel_columns)
        self._create_subscription_triggers()

    def _create_subscription_triggers(self) -> None:
        with sqlite3.connect(self._db_file) as db:
            for action in ("INSERT", "UPDATE"):
                db.execute(
                    f"CREATE TRIGGER IF NOT EXISTS insert_subscription_trigger \
                    AFTER {action} ON channels \
                    BEGIN \
                        UPDATE subscriptions SET subscribed = 0; \
                    END"
                )
            db.commit()

    async def _update_subscription_status(self, user_id: int, subscribed: bool) -> None:
        async with aiosqlite.connect(self._db_file) as db:
            await db.execute(
                "INSERT OR REPLACE INTO subscriptions (user_id, subscribed) VALUES (?, ?)",
                (user_id, subscribed),
            )
            await db.commit()

    async def is_subscribed_to_all(self, user_id: int) -> bool:
        """Checks if user is subscribed to all sponsors' channels in database

        :param user_id: telegram user id
        :type user_id: int
        :return: True if subscribed otherwise False
        :rtype: bool
        """
        result = await self.get_item(self.name, "user_id=?", (user_id,), "subscribed")
        if not result:
            await self._update_subscription_status(user_id, False)
            return False
        return not not result.get("subscribed")

    async def get_sponsors(self) -> List[str]:
        """Get sponsor list from database

        :return: list of sponsors
        :rtype: List[str]
        """
        db_result = await self.get_items(self.channel_table)
        if not db_result:
            return ["There is no sponsors"]
        return [sponsor["channel_name"] for sponsor in db_result]

    async def add_sponsor(self, channel_name: str) -> None:
        await self.add_values(self.channel_table, {"channel_name": channel_name})

    async def remove_sponsor(self, channel_name: str) -> None:
        await self.remove_values(self.channel_table, "channel_name=?", (channel_name,))

    async def is_in(self, channel_name: str) -> bool:
        """Check if sponsor is in database

        :param channel_name: sponsor's channel name
        :type channel_name: str
        :return: True if channel is in database otherwise False
        :rtype: bool
        """
        return not not await self.get_item(
            self.channel_table, "channel_name=?", (channel_name,)
        )
