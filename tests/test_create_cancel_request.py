import datetime
from collections.abc import AsyncGenerator
from decimal import Decimal
from uuid import uuid4

import pytest
import pytest_asyncio
from psycopg_pool import AsyncConnectionPool

from app.domain.cancel_request_status import CancelRequestStatus
from app.domain.contract import Contract
from app.domain.contract_status import ContractStatus
from app.infra.tables_truncater import TablesTruncater
from app.repositories.contract_repository import ContractRepository
from app.services.create_cancel_request import (
    CreateCancelRequest,
    CreateCancelRequestInput,
)


@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def before_each(
    database_pool: AsyncConnectionPool,
) -> AsyncGenerator[None, None]:
    await TablesTruncater(pool=database_pool).execute()
    yield


@pytest.mark.asyncio(loop_scope="session")
async def test_create_cancel_request(
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
    input_data = CreateCancelRequestInput(
        contract_id=contract_id, idempotency_key=idempotency_key
    )
    output_data = await CreateCancelRequest(pool=database_pool).execute(
        input_data
    )
    assert output_data.status == CancelRequestStatus.SUCCESS


@pytest.mark.asyncio(loop_scope="session")
async def test_create_cancel_request_failed_contract(
    database_pool: AsyncConnectionPool,
) -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
        status=ContractStatus.FAILED,
    )
    contract_repository = ContractRepository(pool=database_pool)
    contract_id = await contract_repository.save(contract)
    idempotency_key = str(uuid4())
    input_data = CreateCancelRequestInput(
        contract_id=contract_id, idempotency_key=idempotency_key
    )
    output_data = await CreateCancelRequest(pool=database_pool).execute(
        input_data
    )
    assert output_data.status == CancelRequestStatus.FAILED


@pytest.mark.asyncio(loop_scope="session")
async def test_create_cancel_request_processing_contract(
    database_pool: AsyncConnectionPool,
) -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
        status=ContractStatus.PROCESSING,
    )
    contract_repository = ContractRepository(pool=database_pool)
    contract_id = await contract_repository.save(contract)
    idempotency_key = str(uuid4())
    input_data = CreateCancelRequestInput(
        contract_id=contract_id, idempotency_key=idempotency_key
    )
    output_data = await CreateCancelRequest(pool=database_pool).execute(
        input_data
    )
    assert output_data.status == CancelRequestStatus.FAILED


@pytest.mark.asyncio(loop_scope="session")
async def test_create_cancel_request_duplicated_request(
    database_pool: AsyncConnectionPool,
) -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
        status=ContractStatus.PROCESSING,
    )
    contract_repository = ContractRepository(pool=database_pool)
    contract_id = await contract_repository.save(contract)
    idempotency_key = str(uuid4())
    first_input_data = CreateCancelRequestInput(
        contract_id=contract_id, idempotency_key=idempotency_key
    )
    first_output_data = await CreateCancelRequest(pool=database_pool).execute(
        first_input_data
    )
    assert first_output_data.status == CancelRequestStatus.FAILED
    second_output_data = await CreateCancelRequest(pool=database_pool).execute(
        first_input_data
    )
    assert second_output_data.status == CancelRequestStatus.FAILED


@pytest.mark.asyncio(loop_scope="session")
async def test_create_cancel_request_duplicated_request_with_different_idempotency_key(
    database_pool: AsyncConnectionPool,
) -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
        status=ContractStatus.CREATED,
    )
    contract_repository = ContractRepository(pool=database_pool)
    contract_id = await contract_repository.save(contract)
    first_input_data = CreateCancelRequestInput(
        contract_id=contract_id, idempotency_key=str(uuid4())
    )
    first_output_data = await CreateCancelRequest(pool=database_pool).execute(
        first_input_data
    )
    assert first_output_data.status == CancelRequestStatus.SUCCESS
    second_input_data = CreateCancelRequestInput(
        contract_id=contract_id, idempotency_key=str(uuid4())
    )
    second_output_data = await CreateCancelRequest(pool=database_pool).execute(
        second_input_data
    )
    assert second_output_data.status == CancelRequestStatus.SUCCESS


@pytest.mark.asyncio(loop_scope="session")
async def test_create_cancel_request_after_one_week_contract(
    database_pool: AsyncConnectionPool,
) -> None:
    current_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
    ten_days_before_today = current_datetime - datetime.timedelta(days=10)
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
        status=ContractStatus.CREATED,
        created_at=ten_days_before_today,
        updated_at=ten_days_before_today,
    )
    contract_repository = ContractRepository(pool=database_pool)
    contract_id = await contract_repository.save(contract)
    idempotency_key = str(uuid4())
    input_data = CreateCancelRequestInput(
        contract_id=contract_id, idempotency_key=idempotency_key
    )
    output_data = await CreateCancelRequest(pool=database_pool).execute(
        input_data
    )
    assert output_data.status == CancelRequestStatus.FAILED


@pytest.mark.asyncio(loop_scope="session")
async def test_create_cancel_request_without_refundable_amount(
    database_pool: AsyncConnectionPool,
) -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("0"),
        status=ContractStatus.CREATED,
    )
    contract_repository = ContractRepository(pool=database_pool)
    contract_id = await contract_repository.save(contract)
    idempotency_key = str(uuid4())
    input_data = CreateCancelRequestInput(
        contract_id=contract_id, idempotency_key=idempotency_key
    )
    output_data = await CreateCancelRequest(pool=database_pool).execute(
        input_data
    )
    assert output_data.status == CancelRequestStatus.FAILED
