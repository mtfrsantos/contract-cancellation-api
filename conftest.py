from collections.abc import AsyncGenerator
from typing import Any

import pytest_asyncio
from psycopg_pool import AsyncConnectionPool

from app.infra.environment_variables import environment_variables


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def database_pool() -> AsyncGenerator[AsyncConnectionPool[Any], None]:
    async with AsyncConnectionPool(
        conninfo=environment_variables.DATABASE_URL,
        min_size=environment_variables.MINIMUM_POOL_SIZE,
        max_size=environment_variables.MAXIMUM_POOL_SIZE,
    ) as pool:
        yield pool
