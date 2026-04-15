from dataclasses import dataclass
from decimal import Decimal

from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel

from app.contract import Contract
from app.contract_repository import ContractRepository


class CreateContractInput(BaseModel):
    amount: Decimal
    refundable_amount: Decimal


@dataclass
class CreateContractOutput:
    contract_id: str
    amount: str
    refundable_amount: str
    status: str
    created_at: str
    updated_at: str


class CreateContract:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._contract_repository: ContractRepository = ContractRepository(
            pool
        )

    async def execute(
        self, input_data: CreateContractInput
    ) -> CreateContractOutput:
        contract = Contract(
            amount=input_data.amount,
            refundable_amount=input_data.refundable_amount,
        )
        old_status = contract.status
        contract_id = await self._contract_repository.save(contract)
        assert contract_id, "Should always return contract_id."
        contract.finish_process()
        await self._contract_repository.update_status(
            contract_id=contract_id,
            new_status=contract.status,
            expected_status=old_status,
        )
        return CreateContractOutput(
            contract_id=contract_id,
            amount=str(contract.amount),
            refundable_amount=str(contract.refundable_amount),
            status=contract.status,
            created_at=contract.created_at.isoformat(),
            updated_at=contract.updated_at.isoformat(),
        )
