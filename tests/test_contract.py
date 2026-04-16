import datetime
from decimal import Decimal
from uuid import uuid4

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


def test_contract_finish_process_status_created() -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
        status=ContractStatus.CREATED,
    )
    contract.finish_process()
    assert contract.status == ContractStatus.CREATED


def test_contract_finish_process_not_processing_error() -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
        status=ContractStatus.CANCELLED,
    )
    with pytest.raises(
        ContractError,
        match="Can not finish process if status is not PROCESSING.",
    ):
        contract.finish_process()


def test_contract_cancel() -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    assert contract.status == ContractStatus.PROCESSING
    contract.finish_process()
    assert contract.status == ContractStatus.CREATED
    contract.cancel()
    assert contract.status == ContractStatus.CANCELLED


def test_contract_cancel_status_cancelled() -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
        status=ContractStatus.CANCELLED,
    )
    contract.cancel()
    assert contract.status == ContractStatus.CANCELLED


def test_contract_cancel_after_one_week() -> None:
    current_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
    created_at = current_datetime - datetime.timedelta(days=10)
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
        created_at=created_at,
        updated_at=created_at,
    )
    contract.finish_process()
    assert contract.status == ContractStatus.CREATED
    with pytest.raises(
        ContractError,
        match="Can not cancel contract, 7 days window has passed.",
    ):
        contract.cancel()


def test_contract_cancel_no_refundable_amount() -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("0"),
    )
    contract.finish_process()
    assert contract.status == ContractStatus.CREATED
    with pytest.raises(
        ContractError,
        match="Can not cancel contract, no refundable amount available.",
    ):
        contract.cancel()


def test_contract_equality() -> None:
    contract1 = Contract(
        amount=Decimal("1000"), refundable_amount=Decimal("1000")
    )
    contract2 = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
        status=contract1.status,
        contract_id=contract1.contract_id,
        created_at=contract1.created_at,
        updated_at=contract1.updated_at,
    )
    assert contract1 == contract2


def test_contract_inequality_different_ids() -> None:
    contract1 = Contract(
        amount=Decimal("1000"), refundable_amount=Decimal("1000")
    )
    contract2 = Contract(
        amount=Decimal("1000"), refundable_amount=Decimal("1000")
    )
    assert contract1.contract_id != contract2.contract_id
    assert contract1 != contract2


def test_contract_restore() -> None:
    contract_id = str(uuid4())
    created_at = datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc)
    contract = Contract.restore(
        amount=Decimal("5000"),
        refundable_amount=Decimal("2500"),
        status="CANCELLED",
        contract_id=contract_id,
        created_at=created_at,
        updated_at=created_at,
    )
    assert contract.amount == Decimal("5000")
    assert contract.refundable_amount == Decimal("2500")
    assert contract.status == ContractStatus.CANCELLED
    assert contract.contract_id == contract_id
    assert contract.created_at == created_at
    assert contract.updated_at == created_at


def test_contract_restore_type_assertions() -> None:
    valid_now = datetime.datetime.now(tz=datetime.timezone.utc)
    with pytest.raises(AssertionError):
        _ = Contract.restore(
            amount="1000",  # type: ignore  # pyright: ignore[reportArgumentType]
            refundable_amount=Decimal("1000"),
            status="CREATED",
            contract_id=str(uuid4()),
            created_at=valid_now,
            updated_at=valid_now,
        )
