from enum import StrEnum


class ContractStatus(StrEnum):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
