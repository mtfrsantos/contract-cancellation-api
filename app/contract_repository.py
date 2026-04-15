from typing import Any

from psycopg_pool import AsyncConnectionPool

from app.contract import Contract
from app.contract_status import ContractStatus
from app.database import Database
from app.insert_contract_query_factory import InsertContractQueryFactory
from app.select_contract_by_id_query_factory import (
    SelectContractByIdQueryFactory,
)


class ContractRepository:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._database: Database = Database(pool)

    async def save(self, contract: Contract) -> str:
        query = InsertContractQueryFactory().execute(contract)
        result = await self._database.execute_query(query)
        assert result, "Result should never be empty."
        single_result = self.get_single_result(result)
        contract_id_uuid = single_result.get("contract_id") or ""
        return str(contract_id_uuid)

    async def get_by_id(self, contract_id: str) -> Contract:
        query = SelectContractByIdQueryFactory().execute(contract_id)
        result = await self._database.execute_query(query)
        assert result, "Result should never be empty."
        single_result = self.get_single_result(result)
        return Contract.restore(**single_result)

    def get_single_result(
        self, result: list[dict[str, Any]]
    ) -> dict[str, Any]:
        assert len(result) == 1, "Should contain only single result."
        return result[0]
