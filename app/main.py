from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from psycopg_pool import AsyncConnectionPool

from app.contracts_controller import contracts_controller
from app.environment_variables import environment_variables
from app.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Application startup: Initializing resources...")
    app.state.database_pool = AsyncConnectionPool(
        conninfo=environment_variables.DATABASE_URL,
        min_size=environment_variables.MINIMUM_POOL_SIZE,
        max_size=environment_variables.MAXIMUM_POOL_SIZE,
    )
    yield
    await app.state.database_pool.close()
    logger.info("Application shutdown: Cleaning up resources...")
    logger.info("Database pool closed.")


app = FastAPI(lifespan=lifespan)
app.include_router(contracts_controller)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
