from app.contract import Contract
from app.query import Query


class InsertContractQueryFactory:
    def execute(self, contract: Contract) -> Query:
        statement = """
        INSERT INTO contracts (
            id,
            amount,
            refundable_amount,
            status,
            created_at,
            updated_at
        )
        VALUES (
            %(contract_id)s,
            %(amount)s,
            %(refundable_amount)s,
            %(status)s,
            %(created_at)s,
            %(updated_at)s
        )
        RETURNING id AS contract_id;
        """
        parameters = {
            "contract_id": contract.contract_id,
            "amount": contract.amount,
            "refundable_amount": contract.refundable_amount,
            "status": contract.status,
            "created_at": contract.created_at,
            "updated_at": contract.updated_at,
        }
        return Query(statement=statement, parameters=parameters)
