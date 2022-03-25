from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List
from fastclasses_json import dataclass_json
from ..type import PaperDetail
from ..base import BaseRequest, BaseResponse, BaseFields
from .base import paper_base_url
import requests

paper_search_url = paper_base_url + 'search'


class SearchFields(BaseFields):
    PAPER_ID = "paperId"
    EXTERNAL_IDS = "externalIds"
    URL = "url"
    TITLE = "title"
    ABSTRACT = "abstract"
    VENUE = "venue"
    YEAR = "year"
    REFERENCE_COUNT = "referenceCount"
    CITATION_COUNT = "citationCount"
    INFLUENTIAL_CITATION_COUNT = "influentialCitationCount"
    IS_OPEN_ACCESS = "isOpenAccess"
    FIELDS_OF_STUDY = "fieldsOfStudy"
    S2FIELDS_OF_STUDY = "s2FieldsOfStudy"
    AUTHORS = "authors"


@dataclass
class SearchRequest(BaseRequest[SearchFields]):
    query: str


@dataclass_json
@dataclass
class SearchResponse(BaseResponse):
    data: List[PaperDetail]

    @classmethod
    def from_dict(cls, o: dict, *, infer_missing=True) -> SearchResponse:
        pass


def search_paper(query: str, offset: int = 0, limit: int = 100,
                 fields: Iterable[SearchFields] = SearchFields.values()) -> List[PaperDetail]:
    query_params = SearchRequest(
        query=query,
        offset=offset,
        limit=limit,
        fields=fields
    )
    r = requests.get(paper_search_url, params=query_params.to_params())
    if r.status_code != 200:
        raise Exception(f"Failed to search paper: {r.text}")
    return SearchResponse.from_dict(r.json()).data


__all__ = ["search_paper", "SearchFields"]
