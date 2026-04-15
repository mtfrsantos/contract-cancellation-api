from decimal import Decimal

from app.contract import Contract
from app.contract_status import ContractStatus


def test_contract() -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    assert contract.contract_id
    assert contract.amount == Decimal("1000")
    assert contract.refundable_amount == Decimal("1000")
    assert contract.status == ContractStatus.PROCESSING
    assert contract.created_at
    assert contract.updated_at
