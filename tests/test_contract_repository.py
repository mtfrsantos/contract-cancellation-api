from collections.abc import AsyncGenerator
from decimal import Decimal

import pytest
import pytest_asyncio
from psycopg_pool import AsyncConnectionPool

from app.contract import Contract
from app.contract_repository import ContractRepository
from app.contract_status import ContractStatus
from app.tables_truncater import TablesTruncater


@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def before_each(
    database_pool: AsyncConnectionPool,
) -> AsyncGenerator[None, None]:
    await TablesTruncater(pool=database_pool).execute()
    yield


@pytest.mark.asyncio(loop_scope="session")
async def test_contract_repository_save(
    database_pool: AsyncConnectionPool,
) -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    contract_repository = ContractRepository(pool=database_pool)
    contract_id = await contract_repository.save(contract)
    assert contract_id == contract.contract_id


@pytest.mark.asyncio(loop_scope="session")
async def test_contract_repository_get_by_id(
    database_pool: AsyncConnectionPool,
) -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    contract_repository = ContractRepository(pool=database_pool)
    contract_id = await contract_repository.save(contract)
    recovered_contract = await contract_repository.get_by_id(contract_id)
    assert contract == recovered_contract


@pytest.mark.asyncio(loop_scope="session")
async def test_contract_repository_update_status(
    database_pool: AsyncConnectionPool,
) -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    before_status = contract.status
    assert before_status == ContractStatus.PROCESSING
    contract_repository = ContractRepository(pool=database_pool)
    contract_id = await contract_repository.save(contract)
    before_finish_process_recovered_contract = (
        await contract_repository.get_by_id(contract_id)
    )
    assert (
        before_finish_process_recovered_contract.status
        == ContractStatus.PROCESSING
    )
    contract.finish_process()
    after_status = contract.status
    assert after_status == ContractStatus.CREATED
    await contract_repository.update_status(
        contract_id=contract_id,
        new_status=after_status,
        expected_status=before_status,
    )
    after_finish_process_recovered_contract = (
        await contract_repository.get_by_id(contract_id)
    )
    assert (
        after_finish_process_recovered_contract.status
        == ContractStatus.CREATED
    )
