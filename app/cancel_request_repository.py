from typing import Any

from psycopg_pool import AsyncConnectionPool

from app.cancel_request import CancelRequest
from app.cancel_request_status import CancelRequestStatus
from app.database import Database
from app.insert_cancel_request_query_factory import (
    InsertCancelRequestQueryFactory,
)
from app.select_cancel_request_by_idempotency_key_query_factory import (
    SelectCancelRequestByIdempotencyKeyQueryFactory,
)
from app.update_cancel_request_status_query_factory import (
    UpdateCancelRequestStatusQueryFactory,
)


class CancelRequestRepository:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._database: Database = Database(pool)

    async def save(self, cancel_request: CancelRequest) -> str:
        query = InsertCancelRequestQueryFactory().execute(cancel_request)
        result = await self._database.execute_query(query)
        if not result:
            return ""
        single_result = self._get_single_result(result)
        cancel_request_uuid = single_result.get("cancel_request_id") or ""
        return str(cancel_request_uuid)

    async def get_by_idempotency_key(
        self, idempotency_key: str
    ) -> CancelRequest:
        query = SelectCancelRequestByIdempotencyKeyQueryFactory().execute(
            idempotency_key
        )
        result = await self._database.execute_query(query)
        if not result:
            raise ValueError("Cancel request not found.")
        single_result = self._get_single_result(result)
        return CancelRequest.restore(**single_result)

    async def update_status(
        self,
        cancel_request_id: str,
        new_status: CancelRequestStatus,
        expected_status: CancelRequestStatus,
    ) -> None:
        if new_status == expected_status:
            return
        query = UpdateCancelRequestStatusQueryFactory().execute(
            cancel_request_id=cancel_request_id,
            new_status=new_status,
            expected_status=expected_status,
        )
        _ = await self._database.execute_query(query)

    def _get_single_result(
        self, result: list[dict[str, Any]]
    ) -> dict[str, Any]:
        assert len(result) == 1, "Should contain only single result."
        return result[0]
