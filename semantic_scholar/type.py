from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from fastclasses_json import JSONMixin, dataclass_json


@dataclass_json
@dataclass
class S2FieldOfStudy(JSONMixin):
    category: str
    source: str


@dataclass_json
@dataclass
class Embedding(JSONMixin):
    model: str
    vector: List[Any]


@dataclass_json
@dataclass
class TLDR(JSONMixin):
    model: str
    text: str


@dataclass_json
@dataclass
class AuthorDetail(JSONMixin):
    authorId: Optional[str] = None
    externalIds: Optional[Dict[str, str]] = None
    url: Optional[str] = None
    name: Optional[str] = None
    aliases: Optional[List[str]] = None
    affiliations: Optional[List[str]] = None
    homepage: Optional[str] = None
    paperCount: Optional[int] = None
    citationCount: Optional[int] = None
    hIndex: Optional[int] = None
    papers: Optional[List[PaperDetail]] = None


@dataclass_json
@dataclass
class PaperDetail(JSONMixin):
    paperId: Optional[str] = None
    externalIds: Optional[Dict[str, str]] = None
    url: Optional[str] = None
    title: Optional[str] = None
    abstract: Optional[str] = None
    venue: Optional[str] = None
    year: Optional[int] = None
    referenceCount: Optional[int] = None
    citationCount: Optional[int] = None
    influentialCitationCount: Optional[int] = None
    isOpenAccess: Optional[bool] = None
    fieldsOfStudy: Optional[List[str]] = None
    s2FieldsOfStudy: Optional[List[S2FieldOfStudy]] = None
    authors: Optional[List[AuthorDetail]] = None
    citations: Optional[List[PaperDetail]] = None
    references: Optional[List[PaperDetail]] = None
    embedding: Optional[Embedding] = None
    tldr: Optional[TLDR] = None


@dataclass_json
@dataclass
class CitationDetail(JSONMixin):
    contexts: Optional[List[str]] = None
    intents: Optional[List[str]] = None
    isInfluential: Optional[bool] = None
    citedPaper: Optional[PaperDetail] = None
