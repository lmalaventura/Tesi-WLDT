from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ApiEndpoint:
    method: str
    endpoint: str
    description: str
    keywords: list[str]
    request_hint: str = ""


@dataclass
class ApiCall:
    method: str
    endpoint: str
    path_parameters: dict[str, Any] = field(default_factory=dict)
    query_parameters: dict[str, Any] = field(default_factory=dict)
    body: Any = None
    missing_information: list[str] = field(default_factory=list)