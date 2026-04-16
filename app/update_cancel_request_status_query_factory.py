from app.cancel_request_status import CancelRequestStatus
from app.query import Query


class UpdateCancelRequestStatusQueryFactory:
    def execute(
        self,
        cancel_request_id: str,
        new_status: CancelRequestStatus,
        expected_status: CancelRequestStatus,
    ) -> Query:
        statement = """
        UPDATE cancel_requests
        SET
            status = %(new_status)s
        WHERE
            id = %(cancel_request_id)s AND
            status = %(expected_status)s
        """
        parameters = {
            "new_status": new_status,
            "cancel_request_id": cancel_request_id,
            "expected_status": expected_status,
        }
        return Query(statement=statement, parameters=parameters)
