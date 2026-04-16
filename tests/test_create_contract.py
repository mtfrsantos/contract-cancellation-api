from collections.abc import AsyncGenerator
from decimal import Decimal

import pytest
import pytest_asyncio
from psycopg_pool import AsyncConnectionPool

from app.domain.contract_status import ContractStatus
from app.infra.tables_truncater import TablesTruncater
from app.services.create_contract import CreateContract, CreateContractInput


@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def before_each(
    database_pool: AsyncConnectionPool,
) -> AsyncGenerator[None, None]:
    await TablesTruncater(pool=database_pool).execute()
    yield


@pytest.mark.asyncio(loop_scope="session")
async def test_create_contract(
    database_pool: AsyncConnectionPool,
) -> None:
    input_data = CreateContractInput(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    output_data = await CreateContract(pool=database_pool).execute(input_data)
    assert output_data.contract_id
    assert output_data.amount == "1000"
    assert output_data.refundable_amount == "1000"
    assert output_data.status == ContractStatus.CREATED
    assert output_data.created_at
    assert output_data.updated_at
