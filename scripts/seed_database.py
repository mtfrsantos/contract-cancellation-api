import asyncio
from pathlib import Path

import psycopg
from psycopg_pool import AsyncConnectionPool

from app.environment_variables import environment_variables

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_SQL_PATH = PROJECT_ROOT / "database.sql"


async def execute(
    pool: AsyncConnectionPool | None = None,
) -> None:
    if not DATABASE_SQL_PATH.exists():
        raise FileNotFoundError(
            f"Could not find database.sql at: {DATABASE_SQL_PATH}"
        )
    sql_script = DATABASE_SQL_PATH.read_text()
    if pool is None:
        print("Seeding database using new standalone connection...")
        db_url = environment_variables.DATABASE_URL
        async with await psycopg.AsyncConnection.connect(
            db_url, autocommit=True
        ) as connection:
            async with connection.cursor() as cursor:
                _ = await cursor.execute(sql_script)  # pyright: ignore[reportArgumentType]
        return
    print("Seeding database using existing connection pool...")
    async with pool.connection() as connection:
        await connection.set_autocommit(True)
        async with connection.cursor() as cursor:
            _ = await cursor.execute(sql_script)  # pyright: ignore[reportArgumentType]
    print("Database wipe and seed successful.")


if __name__ == "__main__":
    print("Running seed_database script in standalone mode...")
    asyncio.run(execute())
