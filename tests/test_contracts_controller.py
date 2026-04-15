from collections.abc import AsyncGenerator
from http import HTTPStatus

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from psycopg_pool import AsyncConnectionPool

from app.contract_status import ContractStatus
from app.contracts_controller import contracts_controller

BASE_URL = "http://test.com"


@pytest_asyncio.fixture
async def client(
    database_pool: AsyncConnectionPool,
) -> AsyncGenerator[AsyncClient, None]:
    test_app = FastAPI()
    test_app.state.database_pool = database_pool
    test_app.include_router(contracts_controller)
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url=BASE_URL
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_contracts_controller(client: AsyncClient) -> None:
    payload = {
        "amount": 1000,
        "refundable_amount": 1000,
    }
    response = await client.post(url=f"{BASE_URL}/contracts", json=payload)
    assert response.status_code == HTTPStatus.ACCEPTED
    response_json = response.json()
    assert response_json.get("contract_id")
    assert response_json.get("amount") == "1000"
    assert response_json.get("refundable_amount") == "1000"
    assert response_json.get("status") == ContractStatus.CREATED
    assert response_json.get("created_at")
    assert response_json.get("updated_at")
