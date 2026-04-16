from app.cancel_request import CancelRequest
from app.query import Query


class InsertCancelRequestQueryFactory:
    def execute(self, cancel_request: CancelRequest) -> Query:
        statement = """
        INSERT INTO cancel_requests (
            id,
            contract_id,
            idempotency_key,
            status,
            created_at
        )
        VALUES (
            %(cancel_request_id)s,
            %(contract_id)s,
            %(idempotency_key)s,
            %(status)s,
            %(created_at)s
        )
        ON CONFLICT (idempotency_key) DO NOTHING
        RETURNING id AS cancel_request_id;
        """
        parameters = {
            "cancel_request_id": cancel_request.cancel_request_id,
            "contract_id": cancel_request.contract_id,
            "idempotency_key": cancel_request.idempotency_key,
            "status": cancel_request.status,
            "created_at": cancel_request.created_at,
        }
        return Query(statement=statement, parameters=parameters)
