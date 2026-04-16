import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.cancel_request import CancelRequest, CancelRequestError
from app.cancel_request_status import CancelRequestStatus
from app.contract import Contract


def test_cancel_request() -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    idempotency_key = str(uuid4())
    cancel_request = CancelRequest(
        contract_id=contract.contract_id,
        idempotency_key=idempotency_key,
    )
    assert cancel_request.cancel_request_id
    assert cancel_request.contract_id == contract.contract_id
    assert cancel_request.idempotency_key == idempotency_key
    assert cancel_request.status == CancelRequestStatus.PROCESSING
    assert cancel_request.created_at


def test_cancel_request_status_success_from_processing() -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    idempotency_key = str(uuid4())
    cancel_request = CancelRequest(
        contract_id=contract.contract_id,
        idempotency_key=idempotency_key,
    )
    assert cancel_request.status == CancelRequestStatus.PROCESSING
    cancel_request.success()
    assert cancel_request.status == CancelRequestStatus.SUCCESS


def test_cancel_request_status_success_from_success() -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    idempotency_key = str(uuid4())
    cancel_request = CancelRequest(
        contract_id=contract.contract_id,
        idempotency_key=idempotency_key,
        status=CancelRequestStatus.SUCCESS,
    )
    cancel_request.success()
    assert cancel_request.status == CancelRequestStatus.SUCCESS


def test_cancel_request_status_success_from_failed() -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    idempotency_key = str(uuid4())
    cancel_request = CancelRequest(
        contract_id=contract.contract_id,
        idempotency_key=idempotency_key,
        status=CancelRequestStatus.FAILED,
    )
    with pytest.raises(
        CancelRequestError,
        match="Can not change status from FAILED to SUCCESS.",
    ):
        cancel_request.success()


def test_cancel_request_status_failed_from_processing() -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    idempotency_key = str(uuid4())
    cancel_request = CancelRequest(
        contract_id=contract.contract_id,
        idempotency_key=idempotency_key,
    )
    assert cancel_request.status == CancelRequestStatus.PROCESSING
    cancel_request.fail()
    assert cancel_request.status == CancelRequestStatus.FAILED


def test_cancel_request_status_failed_from_failed() -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    idempotency_key = str(uuid4())
    cancel_request = CancelRequest(
        contract_id=contract.contract_id,
        idempotency_key=idempotency_key,
        status=CancelRequestStatus.FAILED,
    )
    cancel_request.fail()
    assert cancel_request.status == CancelRequestStatus.FAILED


def test_cancel_request_status_failed_from_success() -> None:
    contract = Contract(
        amount=Decimal("1000"),
        refundable_amount=Decimal("1000"),
    )
    idempotency_key = str(uuid4())
    cancel_request = CancelRequest(
        contract_id=contract.contract_id,
        idempotency_key=idempotency_key,
        status=CancelRequestStatus.SUCCESS,
    )
    with pytest.raises(
        CancelRequestError,
        match="Can not change status from SUCCESS to FAILED.",
    ):
        cancel_request.fail()


def test_cancel_request_equality() -> None:
    contract_id = str(uuid4())
    idempotency_key = str(uuid4())
    cancel_request1 = CancelRequest(
        contract_id=contract_id, idempotency_key=idempotency_key
    )
    cancel_request2 = CancelRequest(
        contract_id=contract_id,
        idempotency_key=idempotency_key,
        status=cancel_request1.status,
        cancel_request_id=cancel_request1.cancel_request_id,
        created_at=cancel_request1.created_at,
    )
    assert cancel_request1 == cancel_request2


def test_cancel_request_inequality_different_ids() -> None:
    contract_id = str(uuid4())
    idempotency_key = str(uuid4())
    cancel_request1 = CancelRequest(
        contract_id=contract_id, idempotency_key=idempotency_key
    )
    cancel_request2 = CancelRequest(
        contract_id=contract_id, idempotency_key=idempotency_key
    )
    assert (
        cancel_request1.cancel_request_id != cancel_request2.cancel_request_id
    )
    assert cancel_request1 != cancel_request2


def test_cancel_request_restore() -> None:
    contract_id = str(uuid4())
    idempotency_key = str(uuid4())
    cancel_request_id = str(uuid4())
    created_at = datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc)
    cancel_request = CancelRequest.restore(
        contract_id=contract_id,
        idempotency_key=idempotency_key,
        status="FAILED",
        cancel_request_id=cancel_request_id,
        created_at=created_at,
    )
    assert cancel_request.contract_id == contract_id
    assert cancel_request.idempotency_key == idempotency_key
    assert cancel_request.status == CancelRequestStatus.FAILED
    assert cancel_request.cancel_request_id == cancel_request_id
    assert cancel_request.created_at == created_at


def test_cancel_request_restore_type_assertions() -> None:
    valid_now = datetime.datetime.now(tz=datetime.timezone.utc)
    with pytest.raises(AssertionError):
        _ = CancelRequest.restore(
            contract_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            status=1,  # type: ignore # pyright: ignore[reportArgumentType]
            cancel_request_id=str(uuid4()),
            created_at=valid_now,
        )
