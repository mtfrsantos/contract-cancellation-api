from enum import IntEnum


class ContractStatus(IntEnum):
    CREATED = 1
    PROCESSING = 2
    CANCELLED = 3
    FAILED = 4
