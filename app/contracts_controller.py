from http import HTTPStatus

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.create_contract import CreateContract, CreateContractInput

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
