import datetime
from decimal import Decimal
from uuid import uuid4

from app.contract_status import ContractStatus


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

    def finish_process(self) -> None:
        if self.status == ContractStatus.CREATED:
            return
        if self.status != ContractStatus.PROCESSING:
            raise ContractError(
                "Can not finish process if status is not PROCESSING."
            )
        self.status = ContractStatus.CREATED


class ContractError(Exception):
    pass
