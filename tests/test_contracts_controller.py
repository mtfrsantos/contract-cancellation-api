import datetime
from collections.abc import AsyncGenerator
from decimal import Decimal
from http import HTTPStatus
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from psycopg_pool import AsyncConnectionPool

from app.api.contracts_controller import contracts_controller
from app.domain.contract import Contract
from app.domain.contract_status import ContractStatus
from app.repositories.contract_repository import ContractRepository

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


@pytest_asyncio.fixture
async def reprocess_contract_id(
    database_pool: AsyncConnectionPool,
) -> str:
    current_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
    one_day_ago = current_datetime - datetime.timedelta(days=1)
    ten_minutes_ago = current_datetime - datetime.timedelta(minutes=10)
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
        created_at=one_day_ago,
        updated_at=ten_minutes_ago,
    )
    contract_repository = ContractRepository(pool=database_pool)
    return await contract_repository.save(contract)


@pytest.mark.asyncio
async def test_create_contracts(client: AsyncClient) -> None:
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


@pytest.mark.asyncio
async def test_cancel_requests(client: AsyncClient) -> None:
    create_contract_payload = {
        "amount": 1000,
        "refundable_amount": 1000,
    }
    create_contract_response = await client.post(
        url=f"{BASE_URL}/contracts", json=create_contract_payload
    )
    assert create_contract_response.status_code == HTTPStatus.ACCEPTED
    create_contract_response_json = create_contract_response.json()
    assert (
        create_contract_response_json.get("status") == ContractStatus.CREATED
    )
    assert create_contract_response_json.get("contract_id")
    contract_id = create_contract_response_json.get("contract_id")
    idempotency_key = str(uuid4())
    headers = {"x-idempotency-key": idempotency_key}
    cancel_request_response = await client.post(
        url=f"{BASE_URL}/contracts/{contract_id}/cancel",
        headers=headers,
    )
    assert cancel_request_response.status_code == HTTPStatus.ACCEPTED
    cancel_request_response_json = cancel_request_response.json()
    assert cancel_request_response_json == {"status": "SUCCESS"}


@pytest.mark.asyncio
async def test_reprocess_contracts(
    client: AsyncClient, reprocess_contract_id: str
) -> None:
    reprocess_contract_response = await client.post(
        url=f"{BASE_URL}/contracts/{reprocess_contract_id}/reprocess"
    )
    assert reprocess_contract_response.status_code == HTTPStatus.ACCEPTED
    reprocess_contract_response_json = reprocess_contract_response.json()
    assert reprocess_contract_response_json == {"status": "CREATED"}
