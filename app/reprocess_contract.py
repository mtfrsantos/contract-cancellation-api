import datetime
from dataclasses import dataclass

from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel

from app.contract_repository import ContractRepository
from app.contract_status import ContractStatus


class ReprocessContractInput(BaseModel):
    contract_id: str


@dataclass
class ReprocessContractOutput:
    status: str


class ReprocessContract:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._contract_repository: ContractRepository = ContractRepository(
            pool
        )

    async def execute(
        self, input_data: ReprocessContractInput
    ) -> ReprocessContractOutput:
        contract = await self._contract_repository.get_by_id(
            input_data.contract_id
        )
        if contract.status != ContractStatus.PROCESSING:
            raise ReprocessContractError("Contract should be PROCESSING.")
        current_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        five_minutes_window = current_datetime - datetime.timedelta(minutes=5)
        if contract.updated_at > five_minutes_window:
            raise ReprocessContractError("Contract recently updated.")
        initial_status = contract.status
        if not contract:
            raise ReprocessContractError("Contract could not be found.")
        contract.finish_process()
        await self._contract_repository.update_status(
            contract_id=input_data.contract_id,
            new_status=contract.status,
            expected_status=initial_status,
        )
        return ReprocessContractOutput(status=contract.status)


class ReprocessContractError(Exception):
    pass
