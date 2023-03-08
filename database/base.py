import sqlite3
from typing import Any, Dict, List

import aiosqlite


class Database:
    """
    Parent class for all databases

    Call init.database() in class __init__ function initialize databases.
    That function will create new tables with their columns and column
    types if they are not exist.
    """

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
    ) -> Dict[str, Any] | None:
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
