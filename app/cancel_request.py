import datetime
from typing import Self, override
from uuid import UUID, uuid4

from app.cancel_request_status import CancelRequestStatus


class CancelRequest:
    def __init__(
        self,
        contract_id: str,
        idempotency_key: str,
        status: CancelRequestStatus = CancelRequestStatus.PROCESSING,
        cancel_request_id: str = "",
        created_at: datetime.datetime | None = None,
    ) -> None:
        self.cancel_request_id: str = cancel_request_id or str(uuid4())
        self.contract_id: str = contract_id
        self.idempotency_key: str = idempotency_key
        self.status: CancelRequestStatus = status
        current_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        self.created_at: datetime.datetime = created_at or current_datetime

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CancelRequest):
            return NotImplemented
        return (
            self.contract_id == other.contract_id
            and self.idempotency_key == other.idempotency_key
            and self.status == other.status
            and self.cancel_request_id == other.cancel_request_id
            and self.created_at == other.created_at
        )

    @classmethod
    def restore(
        cls,
        contract_id: UUID | str,
        idempotency_key: UUID | str,
        status: str,
        cancel_request_id: str,
        created_at: datetime.datetime,
    ) -> Self:
        assert isinstance(contract_id, UUID) or isinstance(contract_id, str)
        assert isinstance(idempotency_key, UUID) or isinstance(
            idempotency_key, str
        )
        assert isinstance(status, str)
        assert isinstance(cancel_request_id, UUID) or isinstance(
            cancel_request_id, str
        )
        assert isinstance(created_at, datetime.datetime)
        instance = cls.__new__(cls)
        instance.contract_id = str(contract_id)
        instance.idempotency_key = str(idempotency_key)
        instance.status = CancelRequestStatus(status)
        instance.cancel_request_id = str(cancel_request_id)
        instance.created_at = created_at
        return instance

    def success(self) -> None:
        if self.status == CancelRequestStatus.SUCCESS:
            return
        if self.status == CancelRequestStatus.FAILED:
            raise CancelRequestError(
                "Can not change status from FAILED to SUCCESS."
            )
        self.status = CancelRequestStatus.SUCCESS

    def fail(self) -> None:
        if self.status == CancelRequestStatus.FAILED:
            return
        if self.status == CancelRequestStatus.SUCCESS:
            raise CancelRequestError(
                "Can not change status from SUCCESS to FAILED."
            )
        self.status = CancelRequestStatus.FAILED


class CancelRequestError(Exception):
    pass
