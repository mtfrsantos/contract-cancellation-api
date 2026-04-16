from app.domain.contract_status import ContractStatus
from app.infra.query import Query


class UpdateContractStatusQueryFactory:
    def execute(
        self,
        contract_id: str,
        new_status: ContractStatus,
        expected_status: ContractStatus,
    ) -> Query:
        statement = """
        UPDATE contracts
        SET
            status = %(new_status)s,
            updated_at = CURRENT_TIMESTAMP
        WHERE
            id = %(contract_id)s AND
            status = %(expected_status)s
        """
        parameters = {
            "new_status": new_status,
            "contract_id": contract_id,
            "expected_status": expected_status,
        }
        return Query(statement=statement, parameters=parameters)
