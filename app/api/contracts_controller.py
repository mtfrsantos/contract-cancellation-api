from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from app.services.create_cancel_request import (
    CreateCancelRequest,
    CreateCancelRequestInput,
)
from app.services.create_contract import CreateContract, CreateContractInput
from app.services.reprocess_contract import (
    ReprocessContract,
    ReprocessContractInput,
)

contracts_controller = APIRouter(prefix="/contracts", tags=["contracts"])


@contracts_controller.post("")
async def create_contract(
    input_data: CreateContractInput, request: Request
) -> JSONResponse:
    pool = request.app.state.database_pool
    output_data = await CreateContract(pool).execute(input_data)
    return JSONResponse(
        status_code=HTTPStatus.ACCEPTED,
        content={
            "contract_id": output_data.contract_id,
            "amount": output_data.amount,
            "refundable_amount": output_data.refundable_amount,
            "status": output_data.status,
            "created_at": output_data.created_at,
            "updated_at": output_data.updated_at,
        },
    )


@contracts_controller.post("/{contract_id}/cancel")
async def cancel_contract(
    request: Request,
    contract_id: str,
    x_idempotency_key: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    if not x_idempotency_key:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Missing x-idempotency-key header",
        )
    pool = request.app.state.database_pool
    input_data = CreateCancelRequestInput(
        contract_id=contract_id, idempotency_key=x_idempotency_key
    )
    output_data = await CreateCancelRequest(pool).execute(input_data)
    return JSONResponse(
        status_code=HTTPStatus.ACCEPTED,
        content={"status": output_data.status},
    )


@contracts_controller.post("/{contract_id}/reprocess")
async def reprocess_contract(
    request: Request,
    contract_id: str,
) -> JSONResponse:
    pool = request.app.state.database_pool
    input_data = ReprocessContractInput(contract_id=contract_id)
    output_data = await ReprocessContract(pool).execute(input_data)
    return JSONResponse(
        status_code=HTTPStatus.ACCEPTED,
        content={"status": output_data.status},
    )
