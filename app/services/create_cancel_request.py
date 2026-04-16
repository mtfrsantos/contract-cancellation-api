from dataclasses import dataclass

from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel

from app.domain.cancel_request import CancelRequest
from app.domain.cancel_request_status import CancelRequestStatus
from app.domain.contract import Contract, ContractError
from app.domain.contract_status import ContractStatus
from app.repositories.cancel_request_repository import CancelRequestRepository
from app.repositories.contract_repository import ContractRepository


class CreateCancelRequestInput(BaseModel):
    contract_id: str
    idempotency_key: str


@dataclass
class CreateCancelRequestOutput:
    status: str


class CreateCancelRequest:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._contract_repository: ContractRepository = ContractRepository(
            pool
        )
        self._cancel_request_repository: CancelRequestRepository = (
            CancelRequestRepository(pool)
        )

    async def execute(
        self, input_data: CreateCancelRequestInput
    ) -> CreateCancelRequestOutput:
        contract = await self._contract_repository.get_by_id(
            input_data.contract_id
        )
        if not contract:
            raise CreateCancelRequestError("Contract does not exist.")
        initial_contract_status = contract.status
        cancel_request = CancelRequest(
            contract_id=input_data.contract_id,
            idempotency_key=input_data.idempotency_key,
        )
        initial_cancel_request_status = cancel_request.status
        cancel_request_id = await self._cancel_request_repository.save(
            cancel_request
        )
        # Se não houver cancel_request_id significa que já existe um cancel request
        # com a mesma chave de idempotência, então retorna status anterior
        if self._check_cancel_request_exists(cancel_request_id):
            existing_status = await self._get_existing_cancel_request_status(
                input_data.idempotency_key
            )
            return CreateCancelRequestOutput(status=existing_status)
        new_status = await self._process_new_cancel_request(
            contract=contract,
            initial_contract_status=initial_contract_status,
            cancel_request=cancel_request,
            initial_cancel_request_status=initial_cancel_request_status,
        )
        return CreateCancelRequestOutput(status=new_status)

    def _check_cancel_request_exists(self, cancel_request_id: str) -> bool:
        if not cancel_request_id:
            return True
        return False

    async def _get_existing_cancel_request_status(
        self, idempotency_key: str
    ) -> CancelRequestStatus:
        cancel_request = (
            await self._cancel_request_repository.get_by_idempotency_key(
                idempotency_key
            )
        )
        return cancel_request.status

    async def _process_new_cancel_request(
        self,
        contract: Contract,
        initial_contract_status: ContractStatus,
        cancel_request: CancelRequest,
        initial_cancel_request_status: CancelRequestStatus,
    ) -> CancelRequestStatus:
        try:
            contract.cancel()
            cancel_request.success()
        except ContractError:
            cancel_request.fail()
        finally:
            await self._contract_repository.update_status(
                contract_id=contract.contract_id,
                new_status=contract.status,
                expected_status=initial_contract_status,
            )
            await self._cancel_request_repository.update_status(
                cancel_request_id=cancel_request.cancel_request_id,
                new_status=cancel_request.status,
                expected_status=initial_cancel_request_status,
            )
        return cancel_request.status


class CreateCancelRequestError(Exception):
    pass
