from __future__ import annotations
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Dict, Generic, List, TypeVar, Union, Tuple, Iterable
from fastclasses_json import dataclass_json, JSONMixin
base_url = "https://api.semanticscholar.org/graph/v1/"


class BaseFields(Enum):
    @classmethod
    def values(cls) -> Tuple[BaseFields]:
        return tuple([field for field in cls])


T = TypeVar("T", bound=BaseFields)


@dataclass
class BaseRequest(Generic[T]):
    offset: int
    limit: int
    fields: Iterable[T]

    def to_params(self) -> Dict[str, Union[str, int]]:
        res = asdict(self)
        res["fields"] = ",".join([f.value for f in self.fields])
        return res


@dataclass_json
@dataclass
class BaseResponse(JSONMixin):
    total: int
    offset: int
    next: int

    @classmethod
    def from_dict(cls, o: dict, *, infer_missing=True) -> BaseResponse:
        pass
