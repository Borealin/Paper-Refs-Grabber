import signal
import sys
from queue import Queue
from typing import Dict, Any, List, Iterable
from semantic_scholar.paper import search_paper, get_paper_references, CitationFields, SearchFields
from semantic_scholar.type import PaperDetail
from threading import Thread, RLock
import json
import os
import shutil

intermediates_folder = "./intermediates/"


def get_run_id() -> int:
    run_list = [int(f) for f in os.listdir(intermediates_folder) if
                os.path.isdir(os.path.join(intermediates_folder, f)) and f.isdigit()]
    if len(run_list) == 0:
        return 1
    else:
        return max(run_list) + 1


run_id = get_run_id()
db_json = os.path.join(intermediates_folder, str(run_id), 'db.json')
remaining_json = os.path.join(intermediates_folder, str(run_id), 'remaining.json')
os.makedirs(os.path.join(intermediates_folder, str(run_id)), exist_ok=True)
start_points_json = os.path.join(intermediates_folder, 'start_points.json')


def get_start_points(reload: bool, paper_titles: Iterable[str] = ()) -> List[PaperDetail]:
    fields = [SearchFields.PAPER_ID, SearchFields.TITLE,
              SearchFields.YEAR, SearchFields.ABSTRACT,
              SearchFields.REFERENCE_COUNT,
              SearchFields.CITATION_COUNT,
              SearchFields.FIELDS_OF_STUDY]
    if reload:
        start_points = [
            search_paper(title, fields=fields)[0]
            for title in paper_titles
        ]
        json.dump([paper.to_dict() for paper in start_points], open(start_points_json, 'w'))
    else:
        start_points = [PaperDetail.from_dict(paper) for paper in json.load(open(start_points_json, 'r'))]
    shutil.copyfile(start_points_json, os.path.join(intermediates_folder, str(run_id), 'start_points.json'))
    return start_points


def count_and_save(func):
    def wrapper(self, *args, **kwargs):
        with self.lock:
            with wrapper.lock:
                wrapper.count += 1
                if wrapper.count % 50 == 0:
                    print(f"check_and_add {wrapper.count} times")
                    json.dump({k: v.to_dict() for k, v in self.db.items()}, open(db_json, 'w'))
                return func(self, *args, **kwargs)

    wrapper.lock = RLock()
    wrapper.count = 0
    return wrapper


class PaperDB:
    lock: RLock
    db: Dict[str, PaperDetail]

    def __init__(self):
        self.lock = RLock()
        self.db = {}

    @count_and_save
    def check_and_add(self, paper_id: str, paper_detail: PaperDetail) -> bool:
        with self.lock:
            res = paper_id in self.db
            if not res:
                self.db[paper_id] = paper_detail
            return res

    def update(self, paper_id: str, attrs: Dict[str, Any]):
        with self.lock:
            if paper_id in self.db:
                item = self.db[paper_id]
                for k, v in attrs.items():
                    setattr(item, k, v)


def traverse_multithreading(papers: List[PaperDetail], process_number=8) -> PaperDB:
    paper_db = PaperDB()
    queue = Queue()
    for paper in papers:
        paper_db.check_and_add(paper.paperId, paper)
        queue.put(paper.paperId)
    for _ in range(process_number):
        worker = GetPaperDetailThread(queue, paper_db)
        worker.daemon = True
        worker.start()

    def signal_handler(signal: int, frame) -> None:
        print('You pressed Ctrl+C!')
        result_list = []
        while not queue.empty():
            result_list.append(queue.get())
        print(f"{len(result_list)} papers are left")
        json.dump({k: v.to_dict() for k, v in paper_db.db.items()}, open(db_json, 'w'))
        json.dump(result_list, open(remaining_json, 'w'))
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    queue.join()
    return paper_db


class GetPaperDetailThread(Thread):
    def __init__(self, queue: Queue, paper_db: PaperDB):
        super().__init__()
        self.queue = queue
        self.paper_db = paper_db
        self.fields = [CitationFields.PAPER_ID, CitationFields.TITLE,
                       CitationFields.YEAR, CitationFields.ABSTRACT,
                       CitationFields.REFERENCE_COUNT, CitationFields.CITATION_COUNT,
                       CitationFields.FIELDS_OF_STUDY]

    def check_paper_fields(self, paper: PaperDetail) -> bool:
        for field in self.fields:
            if getattr(paper, field.value) is None:
                return False
        return paper.year >= 2000

    def run(self) -> None:
        while True:
            paper = self.queue.get()
            try:
                refs = get_paper_references(paper, fields=self.fields)
                self.paper_db.update(paper,
                                     {"references": [PaperDetail(paperId=ref.citedPaper.paperId) for ref in refs]})
                for ref in refs:
                    cited_paper = ref.citedPaper
                    if self.check_paper_fields(cited_paper):
                        already_in = self.paper_db.check_and_add(cited_paper.paperId, cited_paper)
                        if not already_in:
                            self.queue.put(cited_paper.paperId)
            except Exception as e:
                print(e)
                self.queue.put(paper)
            self.queue.task_done()


if __name__ == "__main__":
    start_papers = get_start_points(True, [
        "Learning to Denoise Raw Mobile UI",
        "VUT: Versatile UI Transformer for Multi-Modal",
        "Understanding Mobile GUI: from Pixel-Words",
        "Multimodal Icon Annotation For Mobile Applications",
        "Nighthawk: Fully Automated Localizing UI Display Issues"
    ])
    print(f"{len(start_papers)} papers are loaded")
    traverse_multithreading(start_papers, 8)
