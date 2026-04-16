from psycopg_pool import AsyncConnectionPool

from app.infra.database import Database
from app.infra.query import Query


class TablesTruncater:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._database: Database = Database(pool)

    async def execute(self) -> None:
        statement = "TRUNCATE TABLE contracts, cancel_requests"
        query = Query(statement=statement)
        _ = await self._database.execute_query(query)
