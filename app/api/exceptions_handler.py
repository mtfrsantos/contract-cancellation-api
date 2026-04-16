from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse

from app.domain.cancel_request import CancelRequestError
from app.domain.contract import ContractError
from app.infra.logger import logger
from app.main import app
from app.services.create_cancel_request import CreateCancelRequestError
from app.services.reprocess_contract import ReprocessContractError


@app.exception_handler(ContractError)
async def contract_error_handler(
    _request: Request, exc: ContractError
) -> JSONResponse:
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={"message": str(exc)},
    )


@app.exception_handler(CancelRequestError)
async def cancel_request_error_handler(
    _request: Request, exc: CancelRequestError
) -> JSONResponse:
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={"message": str(exc)},
    )


@app.exception_handler(CreateCancelRequestError)
async def create_cancel_request_error_handler(
    _request: Request, exc: CreateCancelRequestError
) -> JSONResponse:
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={"message": str(exc)},
    )


@app.exception_handler(ReprocessContractError)
async def reprocess_contract_error_handler(
    _request: Request, exc: ReprocessContractError
) -> JSONResponse:
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={"message": str(exc)},
    )


@app.exception_handler(Exception)
async def universal_exception_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    logger.error(f"Unhandled error occurred: {exc}")
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={
            "message": "An unexpected internal error occurred.",
        },
    )
