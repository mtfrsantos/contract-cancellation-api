from dataclasses import dataclass
from typing import Any


@dataclass
class Query:
    statement: str
    parameters: dict[str, Any] | None = None
