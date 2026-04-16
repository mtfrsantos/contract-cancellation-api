from typing import Any

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.query import Query


class Database:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self.pool: AsyncConnectionPool = pool

    async def execute_query(
        self, *query_collection: Query
    ) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        # logger.debug("Connecting to database...")
        async with self.pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                for query in query_collection:
                    # logger.debug(
                    #     f"Query:\n{query.statement}\n{query.parameters}"
                    # )
                    _ = await cursor.execute(
                        query.statement,  # pyright: ignore[reportArgumentType]
                        query.parameters,
                    )
                if cursor.description:
                    result = await cursor.fetchall()
        return result
