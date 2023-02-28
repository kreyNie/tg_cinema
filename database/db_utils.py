from typing import Any, Dict, List
import sqlite3
import aiosqlite


class Database:
    def __init__(self, db_file: str) -> None:
        self._db_file = db_file

    def init_database(self, table_name: str, columns: dict) -> None:
        """Creates needed table if not exists

        :param table_name: name of table
        :type table_name: str
        :param columns: creates columns with their names and types
        :type columns: dict
        """
        with sqlite3.connect(self._db_file) as db:
            column_defs = ", ".join(
                f"{col_name} {col_type}" for col_name, col_type in columns.items()
            )
            db.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs})")

    async def create_indexes(self, table_name: str, indexes: list) -> None:
        async with aiosqlite.connect(self._db_file) as db:
            for index_def in indexes:
                await db.execute(
                    f"CREATE INDEX IF NOT EXISTS {table_name}_{index_def} ON {table_name} ({index_def})"
                )

            await db.commit()

    async def add_values(self, table_name: str, values: dict) -> None:
        async with aiosqlite.connect(self._db_file) as db:
            placeholders = ", ".join("?" for _ in values.values())
            columns = ", ".join(values.keys())
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            print(query, tuple(values.values()))
            await db.execute(query, tuple(values.values()))
            await db.commit()

    async def remove_values(
        self, table_name: str, condition: str, values: tuple = None
    ) -> None:
        async with aiosqlite.connect(self._db_file) as db:
            query = f"DELETE FROM {table_name} WHERE {condition}"
            await db.execute(query, values)
            await db.commit()

    async def get_item(
        self,
        table_name: str,
        condition: str = None,
        values: tuple = None,
        target: str = "*",
    ) -> Dict[str, Any]:
        async with aiosqlite.connect(self._db_file) as db:
            query = (
                f"SELECT {target} FROM {table_name}" + f" WHERE {condition}"
                if condition
                else ""
            )
            async with db.execute(query, values) as cursor:
                result = await cursor.fetchone()
                if result is not None:
                    columns = [d[0] for d in cursor.description]
                    return dict(zip(columns, result))
                else:
                    return None

    async def get_items(
        self,
        table_name: str,
        condition: str = None,
        values: tuple = None,
        target: str = "*",
    ) -> List[Dict[str, Any]] | None:
        async with aiosqlite.connect(self._db_file) as db:
            query = f"SELECT {target} FROM {table_name}"
            query += f"WHERE {condition}" if condition else ""
            async with db.execute(query, values) as cursor:
                result = await cursor.fetchall()
                if not result:
                    return None
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in result]


class AsyncFilmDatabase(Database):
    def __init__(self, db_file: str = "films.db", name: str = "films") -> None:
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
        super().__init__(db_file)
        self.name = name
        self.columns = {
            "user_id": "INTEGER NOT NULL PRIMARY KEY",
            "subscribed": "BOOLEAN DEFAULT 0",
        }
        self.channel_table = "channels"
        self.channel_columns = {
            "channel_name": "TEXT NOT NULL PRIMARY KEY",
        }
        self.init_database(self.name, self.columns)
        self.init_database(self.channel_table, self.channel_columns)
        self.create_subscription_triggers()

    def create_subscription_triggers(self) -> None:
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

    async def update_subscription_status(self, user_id: int, subscribed: bool) -> None:
        async with aiosqlite.connect(self._db_file) as db:
            await db.execute(
                "INSERT OR REPLACE INTO subscriptions (user_id, subscribed) VALUES (?, ?)",
                (user_id, subscribed),
            )
            await db.commit()

    async def is_subscribed_to_all(self, user_id: int) -> bool:
        result = await self.get_item(self.name, "user_id=?", (user_id,), "subscribed")
        return not not result["subscribed"]

    async def get_sponsors(self) -> List[str]:
        db_result = await self.get_items(self.channel_table)
        if not db_result:
            return ["There is no sponsors"]
        return [sponsor["channel_name"] for sponsor in db_result]

    async def add_sponsor(self, channel_name: str) -> None:
        await self.add_values(self.channel_table, {"channel_name": channel_name})

    async def edit_sponsors(self, channel_name: int, operation: bool) -> None:
        if operation:
            self.set(channel_name)
        else:
            await self.remove_values(
                self.channel_table, "channel_name=?", (channel_name,)
            )
