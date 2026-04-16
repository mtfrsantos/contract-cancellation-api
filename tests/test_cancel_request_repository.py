from collections.abc import AsyncGenerator
from decimal import Decimal
from uuid import uuid4

import pytest
import pytest_asyncio
from psycopg_pool import AsyncConnectionPool

from app.domain.cancel_request import CancelRequest
from app.domain.cancel_request_status import CancelRequestStatus
from app.domain.contract import Contract
from app.domain.contract_status import ContractStatus
from app.infra.tables_truncater import TablesTruncater
from app.repositories.cancel_request_repository import CancelRequestRepository
from app.repositories.contract_repository import ContractRepository


@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def before_each(
    database_pool: AsyncConnectionPool,
) -> AsyncGenerator[None, None]:
    await TablesTruncater(pool=database_pool).execute()
    yield


@pytest.mark.asyncio(loop_scope="session")
async def test_cancel_request_repository_save(
    database_pool: AsyncConnectionPool,
) -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    contract_repository = ContractRepository(pool=database_pool)
    contract_id = await contract_repository.save(contract)
    idempotency_key = str(uuid4())
    cancel_request = CancelRequest(
        contract_id=contract_id,
        idempotency_key=idempotency_key,
    )
    cancel_request_repository = CancelRequestRepository(pool=database_pool)
    cancel_request_id = await cancel_request_repository.save(cancel_request)
    assert cancel_request_id == cancel_request.cancel_request_id


@pytest.mark.asyncio(loop_scope="session")
async def test_cancel_request_repository_get_by_idempotency_key(
    database_pool: AsyncConnectionPool,
) -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    contract_repository = ContractRepository(pool=database_pool)
    contract_id = await contract_repository.save(contract)
    idempotency_key = str(uuid4())
    cancel_request = CancelRequest(
        contract_id=contract_id,
        idempotency_key=idempotency_key,
    )
    cancel_request_repository = CancelRequestRepository(pool=database_pool)
    _ = await cancel_request_repository.save(cancel_request)
    recovered_cancel_request = (
        await cancel_request_repository.get_by_idempotency_key(idempotency_key)
    )
    assert cancel_request == recovered_cancel_request


@pytest.mark.asyncio(loop_scope="session")
async def test_cancel_request_repository_update_status(
    database_pool: AsyncConnectionPool,
) -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
        status=ContractStatus.CREATED,
    )
    contract_repository = ContractRepository(pool=database_pool)
    contract_id = await contract_repository.save(contract)
    idempotency_key = str(uuid4())
    cancel_request = CancelRequest(
        contract_id=contract_id,
        idempotency_key=idempotency_key,
    )
    before_status = cancel_request.status
    assert before_status == CancelRequestStatus.PROCESSING
    cancel_request_repository = CancelRequestRepository(pool=database_pool)
    cancel_request.success()
    cancel_request_id = await cancel_request_repository.save(cancel_request)
    await cancel_request_repository.update_status(
        cancel_request_id=cancel_request_id,
        new_status=cancel_request.status,
        expected_status=before_status,
    )
    recovered_cancel_request = (
        await cancel_request_repository.get_by_idempotency_key(idempotency_key)
    )
    assert recovered_cancel_request.status == CancelRequestStatus.SUCCESS
