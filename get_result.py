import json
from typing import Dict, IO
from semantic_scholar.type import PaperDetail
import os
import networkx as nx
import matplotlib.pyplot as plt
import graphviz

cite_count = {}

if __name__ == '__main__':
    run_id = 1
    os.makedirs(os.path.join('result', str(run_id)), exist_ok=True)

    with open(os.path.join('intermediates', str(run_id), 'db.json'), 'r') as f:
        graph: Dict[str, PaperDetail] = {k: PaperDetail.from_dict(v) for k, v in json.load(f).items()}
        print(f"grab paper total count: {len(graph)}")
        for index, paper in enumerate(graph.values()):
            setattr(paper, 'index', index)

        # G = nx.DiGraph()
        # dot = graphviz.Digraph('citation-graph')
        for paper in graph.values():
            # G.add_node(paper.index, title=paper.title, year=paper.year)
            # dot.node(str(paper.index), f"{paper.title}({paper.year})")
            if paper.references is not None:
                for ref in paper.references:
                    if ref.paperId in graph:
                        # G.add_edge(paper.index, graph[ref.paperId].index)
                        # dot.edge(str(paper.index), str(graph[ref.paperId].index))
                        cite_count[graph[ref.paperId].paperId] = cite_count.get(graph[ref.paperId].paperId, 0) + 1


        # nx.draw(G)
        # plt.show()
        # dot.render(directory='doctest-output', view=True)

        def write_paper(detail: PaperDetail, idx: int, fff: IO):
            fff.write(f"Top {idx + 1}:\n")
            fff.write(f"title: {detail.title}\n")
            fff.write(f"abstract: {detail.abstract}\n")
            fff.write(f"url: https://www.semanticscholar.org/paper/{detail.paperId}\n")
            fff.write(f"year: {detail.year}\n")
            fff.write(f"fields of study: {','.join(detail.fieldsOfStudy if detail.fieldsOfStudy is not None else [])}\n")
            fff.write(f"real citations: {detail.citationCount}\n")


        with open(os.path.join('result', str(run_id), 'top_result'), 'w') as ff:
            for index, top in enumerate(sorted(cite_count.items(), key=lambda x: x[1], reverse=True)[:100]):
                write_paper(graph[top[0]], index, ff)
                ff.write(f"cite times in graph: {top[1]}\n")
                ff.write("\n")
        with open(os.path.join('result', str(run_id), 'most_recent_result'), 'w') as ff:
            for index, top in enumerate(sorted(graph.values(), key=lambda x: x.year, reverse=True)[:100]):
                write_paper(top, index, ff)
                ff.write("\n")
