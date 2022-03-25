from typing import Iterable
from ..type import PaperDetail
from ..base import BaseFields, BaseRequest
from .base import paper_base_url
import requests

paper_detail_url = paper_base_url + '{paper_id}'


class DetailFields(BaseFields):
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
    CITATIONS = "citations"
    REFERENCES = "references"
    EMBEDDING = "embedding"
    TLDR = "tldr"


def get_paper_detail(paper_id: str, offset: int = 0, limit: int = 100,
                     fields: Iterable[DetailFields] = DetailFields.values()) -> PaperDetail:
    r = requests.get(paper_detail_url.format(paper_id=paper_id),
                     params=BaseRequest[DetailFields](offset, limit, fields).to_params())
    if r.status_code != 200:
        raise Exception(f"Failed to get paper detail: {r.text}")
    return PaperDetail.from_dict(r.json())


__all__ = ["get_paper_detail", "DetailFields"]
