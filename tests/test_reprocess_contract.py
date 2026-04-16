import datetime
from collections.abc import AsyncGenerator
from decimal import Decimal
from uuid import uuid4

import pytest
import pytest_asyncio
from psycopg_pool import AsyncConnectionPool

from app.domain.contract import Contract
from app.domain.contract_status import ContractStatus
from app.infra.tables_truncater import TablesTruncater
from app.repositories.contract_repository import ContractRepository
from app.services.reprocess_contract import (
    ReprocessContract,
    ReprocessContractError,
    ReprocessContractInput,
)


@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def before_each(
    database_pool: AsyncConnectionPool,
) -> AsyncGenerator[None, None]:
    await TablesTruncater(pool=database_pool).execute()
    yield


@pytest.mark.asyncio(loop_scope="session")
async def test_reprocess_contract(
    database_pool: AsyncConnectionPool,
) -> None:
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
    contract_id = await contract_repository.save(contract)
    input_data = ReprocessContractInput(contract_id=contract_id)
    output_data = await ReprocessContract(database_pool).execute(input_data)
    assert output_data.status == ContractStatus.CREATED


@pytest.mark.asyncio(loop_scope="session")
async def test_reprocess_contract_status_failed(
    database_pool: AsyncConnectionPool,
) -> None:
    current_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
    one_day_ago = current_datetime - datetime.timedelta(days=1)
    ten_minutes_ago = current_datetime - datetime.timedelta(minutes=10)
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
        status=ContractStatus.FAILED,
        created_at=one_day_ago,
        updated_at=ten_minutes_ago,
    )
    contract_repository = ContractRepository(pool=database_pool)
    contract_id = await contract_repository.save(contract)
    input_data = ReprocessContractInput(contract_id=contract_id)
    with pytest.raises(
        ReprocessContractError,
        match="Contract should be PROCESSING.",
    ):
        _ = await ReprocessContract(database_pool).execute(input_data)


@pytest.mark.asyncio(loop_scope="session")
async def test_reprocess_contract_updated_at_less_than_5_minutes(
    database_pool: AsyncConnectionPool,
) -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    contract_repository = ContractRepository(pool=database_pool)
    contract_id = await contract_repository.save(contract)
    input_data = ReprocessContractInput(contract_id=contract_id)
    with pytest.raises(
        ReprocessContractError,
        match="Contract recently updated.",
    ):
        _ = await ReprocessContract(database_pool).execute(input_data)


@pytest.mark.asyncio(loop_scope="session")
async def test_reprocess_contract_no_contract(
    database_pool: AsyncConnectionPool,
) -> None:
    input_data = ReprocessContractInput(contract_id=str(uuid4()))
    with pytest.raises(ValueError, match="Contract not found."):
        _ = await ReprocessContract(database_pool).execute(input_data)
