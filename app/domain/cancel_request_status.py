from enum import StrEnum


class CancelRequestStatus(StrEnum):
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
