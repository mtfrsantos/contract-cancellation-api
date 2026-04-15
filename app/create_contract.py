from dataclasses import dataclass
from decimal import Decimal

from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel

from app.contract import Contract
from app.contract_repository import ContractRepository
from app.contract_status import ContractStatus


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
        contract.status = ContractStatus.CREATED
        contract_id = await self._contract_repository.save(contract)
        assert contract_id, "Should always return contract_id."
        return CreateContractOutput(
            contract_id=contract_id,
            amount=str(contract.amount),
            refundable_amount=str(contract.refundable_amount),
            status=contract.status,
            created_at=contract.created_at.isoformat(),
            updated_at=contract.updated_at.isoformat(),
        )
