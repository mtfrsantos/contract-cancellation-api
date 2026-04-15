from psycopg_pool import AsyncConnectionPool

from app.database import Database
from app.query import Query


class TablesTruncater:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._database: Database = Database(pool)

    async def execute(self) -> None:
        statement = "TRUNCATE TABLE contracts"
        query = Query(statement=statement)
        _ = await self._database.execute_query(query)
