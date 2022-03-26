import json
from typing import Dict, IO
from semantic_scholar.type import PaperDetail
import os
import networkx as nx
import matplotlib.pyplot as plt
import graphviz


def get_paper_db(path: str) -> Dict[str, PaperDetail]:
    with open(path, 'r') as f:
        return {k: PaperDetail.from_dict(v) for k, v in json.load(f).items()}


def get_cite_count(_paper_db: Dict[str, PaperDetail]) -> Dict[str, int]:
    _cite_count = {}
    for _paper in _paper_db.values():
        if _paper.references is not None:
            for _ref in _paper.references:
                if _ref.paperId in _paper_db:
                    _cite_count[_ref.paperId] = _cite_count.get(_ref.paperId, 0) + 1
    return _cite_count


def visualize(paper_db: Dict[str, PaperDetail], path: str,
              graph_threshold=50, nx_graph=True, dot_graph=True):
    top_citations = sorted(get_cite_count(paper_db).items(), key=lambda x: x[1], reverse=True)[:graph_threshold]
    top_citations_db = {k: paper_db[k] for k, v in top_citations}
    for index, paper in enumerate(top_citations_db.values()):
        setattr(paper, 'index', index)

    def nx_visualize(_top_citations_db: Dict[str, PaperDetail]):
        G = nx.DiGraph()
        for paper in _top_citations_db.values():
            G.add_node(paper.index, title=paper.title, year=paper.year)
            if paper.references is not None:
                for ref in paper.references:
                    if ref.paperId in _top_citations_db:
                        G.add_edge(paper.index, _top_citations_db[ref.paperId].index)
        idx_to_node_dict = {}
        for idx, node in enumerate(G.nodes):
            idx_to_node_dict[idx] = node
        fig, ax = plt.subplots()
        pos = nx.spring_layout(G)
        nodes = nx.draw_networkx_nodes(G, pos=pos, ax=ax)
        nx.draw_networkx_edges(G, pos=pos, ax=ax)
        annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        def update_annot(ind):
            node_idx = ind["ind"][0]
            node = idx_to_node_dict[node_idx]
            xy = pos[node]
            annot.xy = xy
            node_attr = {'node': node}
            node_attr.update(G.nodes[node])
            text = '\n'.join(f'{k}: {v}' for k, v in node_attr.items())
            annot.set_text(text)

        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                cont, ind = nodes.contains(event)
                if cont:
                    update_annot(ind)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", hover)
        plt.show()

    def graphviz_visualize(_top_citations_db: Dict[str, PaperDetail]):
        dot = graphviz.Digraph('citation-graph')
        for paper in _top_citations_db.values():
            dot.node(str(paper.index), f"{paper.title[:25]}({paper.year})({paper.citationCount})")
            if paper.references is not None:
                for ref in paper.references:
                    if ref.paperId in _top_citations_db:
                        dot.edge(str(paper.index), str(_top_citations_db[ref.paperId].index))
        dot.render(os.path.join(path, 'citation-graph.gv'), view=True)

    if nx_graph:
        nx_visualize(top_citations_db)
    if dot_graph:
        graphviz_visualize(top_citations_db)


def write_res(paper_db: Dict[str, PaperDetail],
              path: str,
              top_threshold=100):
    def write_paper(detail: PaperDetail, idx: int, fff: IO):
        fff.write(f"Top {idx + 1}:\n")
        fff.write(f"title: {detail.title}\n")
        fff.write(f"abstract: {detail.abstract}\n")
        fff.write(f"url: https://www.semanticscholar.org/paper/{detail.paperId}\n")
        fff.write(f"year: {detail.year}\n")
        fff.write(
            f"fields of study: {','.join(detail.fieldsOfStudy if detail.fieldsOfStudy is not None else [])}\n")
        fff.write(f"real citations: {detail.citationCount}\n")

    with open(os.path.join(path, 'top_citation'), 'w') as ff:
        for index, top in enumerate(
                sorted(get_cite_count(paper_db).items(), key=lambda x: x[1], reverse=True)[:top_threshold]):
            write_paper(paper_db[top[0]], index, ff)
            ff.write(f"cite times in graph: {top[1]}\n")
            ff.write("\n")

    with open(os.path.join(path, 'most_recent'), 'w') as ff:
        for index, top in enumerate(sorted(paper_db.values(), key=lambda x: x.year, reverse=True)[:top_threshold]):
            write_paper(top, index, ff)
            ff.write("\n")


if __name__ == '__main__':
    run_id = 1
    intermediates_path = os.path.join('intermediates', str(run_id))
    result_path = os.path.join('result', str(run_id))
    os.makedirs(result_path, exist_ok=True)

    db = get_paper_db(os.path.join(intermediates_path, 'db.json'))
    print(f"grab paper total count: {len(db)}")
    write_res(db, result_path, 100)
    visualize(db, result_path, 1000, True, False)
