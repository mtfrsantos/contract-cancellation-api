from app.query import Query


class SelectCancelRequestByIdempotencyKeyQueryFactory:
    def execute(self, idempotency_key: str) -> Query:
        statement = """
        SELECT 
            id AS cancel_request_id,
            contract_id,
            idempotency_key,
            status,
            created_at
        FROM cancel_requests
        WHERE idempotency_key = %(idempotency_key)s;
        """
        parameters = {"idempotency_key": idempotency_key}
        return Query(statement=statement, parameters=parameters)
