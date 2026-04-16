from typing import Any

from psycopg_pool import AsyncConnectionPool

from app.domain.contract import Contract
from app.domain.contract_status import ContractStatus
from app.infra.database import Database
from app.repositories.insert_contract_query_factory import (
    InsertContractQueryFactory,
)
from app.repositories.select_contract_by_id_query_factory import (
    SelectContractByIdQueryFactory,
)
from app.repositories.update_contract_status_query_factory import (
    UpdateContractStatusQueryFactory,
)


class ContractRepository:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._database: Database = Database(pool)

    async def save(self, contract: Contract) -> str:
        query = InsertContractQueryFactory().execute(contract)
        result = await self._database.execute_query(query)
        assert result, "Result should never be empty."
        single_result = self._get_single_result(result)
        contract_id_uuid = single_result.get("contract_id") or ""
        return str(contract_id_uuid)

    async def get_by_id(self, contract_id: str) -> Contract:
        query = SelectContractByIdQueryFactory().execute(contract_id)
        result = await self._database.execute_query(query)
        if not result:
            raise ValueError("Contract not found.")
        single_result = self._get_single_result(result)
        return Contract.restore(**single_result)

    async def update_status(
        self,
        contract_id: str,
        new_status: ContractStatus,
        expected_status: ContractStatus,
    ) -> None:
        if new_status == expected_status:
            return
        query = UpdateContractStatusQueryFactory().execute(
            contract_id=contract_id,
            new_status=new_status,
            expected_status=expected_status,
        )
        _ = await self._database.execute_query(query)

    def _get_single_result(
        self, result: list[dict[str, Any]]
    ) -> dict[str, Any]:
        assert len(result) == 1, "Should contain only single result."
        return result[0]
