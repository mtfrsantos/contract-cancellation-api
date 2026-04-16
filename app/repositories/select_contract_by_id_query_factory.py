from app.infra.query import Query


class SelectContractByIdQueryFactory:
    def execute(self, contract_id: str) -> Query:
        statement = """
        SELECT 
            id AS contract_id,
            amount,
            refundable_amount,
            status,
            created_at,
            updated_at
        FROM contracts
        WHERE id = %(contract_id)s;
        """
        parameters = {"contract_id": contract_id}
        return Query(statement=statement, parameters=parameters)
