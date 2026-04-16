import datetime
from decimal import Decimal
from typing import Self, override
from uuid import UUID, uuid4

from app.domain.contract_status import ContractStatus


class Contract:
    def __init__(
        self,
        amount: Decimal,
        refundable_amount: Decimal,
        status: ContractStatus = ContractStatus.PROCESSING,
        contract_id: str = "",
        created_at: datetime.datetime | None = None,
        updated_at: datetime.datetime | None = None,
    ) -> None:
        self.contract_id: str = contract_id or str(uuid4())
        self.amount: Decimal = amount
        self.refundable_amount: Decimal = refundable_amount
        self.status: ContractStatus = status
        current_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        self.created_at: datetime.datetime = created_at or current_datetime
        self.updated_at: datetime.datetime = updated_at or current_datetime

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Contract):
            return NotImplemented
        return (
            self.amount == other.amount
            and self.refundable_amount == other.refundable_amount
            and self.status == other.status
            and self.contract_id == other.contract_id
            and self.created_at == other.created_at
            and self.updated_at == other.updated_at
        )

    @classmethod
    def restore(
        cls,
        amount: Decimal,
        refundable_amount: Decimal,
        status: str,
        contract_id: UUID | str,
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
    ) -> Self:
        assert isinstance(amount, Decimal)
        assert isinstance(refundable_amount, Decimal)
        assert isinstance(status, str)
        assert isinstance(contract_id, UUID) or isinstance(contract_id, str)
        assert isinstance(created_at, datetime.datetime)
        assert isinstance(updated_at, datetime.datetime)
        instance = cls.__new__(cls)
        instance.amount = amount
        instance.refundable_amount = refundable_amount
        instance.status = ContractStatus(status)
        instance.contract_id = str(contract_id)
        instance.created_at = created_at
        instance.updated_at = updated_at
        return instance

    def finish_process(self) -> None:
        if self.status == ContractStatus.CREATED:
            return
        if self.status != ContractStatus.PROCESSING:
            raise ContractError(
                "Can not finish process if status is not PROCESSING."
            )
        self.status = ContractStatus.CREATED

    def cancel(self) -> None:
        if self.status == ContractStatus.CANCELLED:
            return
        if self.status != ContractStatus.CREATED:
            raise ContractError(
                "Can not cancel contract if status is not CREATED."
            )
        today = datetime.datetime.now(tz=datetime.timezone.utc)
        one_week_after_created_at = self.created_at + datetime.timedelta(
            days=7
        )
        if today > one_week_after_created_at:
            raise ContractError(
                "Can not cancel contract, 7 days window has passed."
            )
        if self.refundable_amount <= Decimal("0"):
            raise ContractError(
                "Can not cancel contract, no refundable amount available."
            )
        self.status = ContractStatus.CANCELLED


class ContractError(Exception):
    pass
