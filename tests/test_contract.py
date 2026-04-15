from decimal import Decimal

import pytest

from app.contract import Contract, ContractError
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


def test_contract_finish_process() -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    assert contract.status == ContractStatus.PROCESSING
    contract.finish_process()
    assert contract.status == ContractStatus.CREATED


def test_contract_finish_process_not_processing_error() -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
        status=ContractStatus.CREATED,
    )
    with pytest.raises(
        ContractError,
        match="Can not finish process if status is not PROCESSING.",
    ):
        contract.finish_process()
