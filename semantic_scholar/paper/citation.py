from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List

from fastclasses_json import dataclass_json
from ..type import CitationDetail
from ..base import BaseFields, BaseRequest, BaseResponse
from .base import paper_base_url
import requests

paper_citation_url = paper_base_url + '{paper_id}/citations'
paper_references_url = paper_base_url + '{paper_id}/references'


class CitationFields(BaseFields):
    CONTEXTS = "contexts"
    INTENTS = "intents"
    IS_INFLUENTIAL = "isInfluential"
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


@dataclass_json
@dataclass
class CitationResponse(BaseResponse):
    data: List[CitationDetail]

    @classmethod
    def from_dict(cls, o: dict, *, infer_missing=True) -> CitationResponse:
        pass


def get_paper_citations(paper_id: str, offset: int = 0, limit: int = 100,
                        fields: Iterable[CitationFields] = CitationFields.values()) -> List[CitationDetail]:
    r = requests.get(paper_citation_url.format(paper_id=paper_id), params=BaseRequest[CitationFields](
        offset, limit, fields).to_params())
    if r.status_code != 200:
        raise Exception(f"Failed to get paper citations: {r.text}")
    return CitationResponse.from_dict(r.json()).data


def get_paper_references(paper_id: str, offset: int = 0, limit: int = 100,
                         fields: Iterable[CitationFields] = CitationFields.values()) -> List[CitationDetail]:
    r = requests.get(paper_references_url.format(paper_id=paper_id), params=BaseRequest[CitationFields](
        offset, limit, fields).to_params())
    if r.status_code != 200:
        raise Exception(f"Failed to get paper references: {r.text}")
    return CitationResponse.from_dict(r.json()).data


__all__ = ["get_paper_citations", "get_paper_references", "CitationFields"]
