"""Transitivity check: if A beats B and B beats C, C must not beat A.

Uses response ids when records carry them (response_a_id / response_b_id), otherwise the response text.
Cycles in majority-vote preferences indicate inconsistent labelling or an ambiguous rubric.
"""
from collections import defaultdict

from .agreement import group_by_item, majority_labels


def _node(rec, side):
    return rec.get(f"response_{side}_id") or rec[f"response_{side}"]


def build_graph(records):
    ids = {}
    for rec in records:
        ids[(rec["prompt"], rec["response_a"], rec["response_b"])] = (_node(rec, "a"), _node(rec, "b"))
    graph = defaultdict(set)
    for key, label in majority_labels(records).items():
        a, b = ids[key]
        if a == b:
            continue  # identical responses cannot form a meaningful preference edge
        if label == "A":
            graph[a].add(b)
        elif label == "B":
            graph[b].add(a)
    return graph


def transitivity_violations(records):
    graph = build_graph(records)
    cycles = set()
    for a in list(graph):
        for b in graph[a]:
            for c in graph.get(b, ()):
                if a in graph.get(c, ()):
                    cycle = (a, b, c)
                    start = cycle.index(min(cycle))
                    cycles.add(cycle[start:] + cycle[:start])
    return [{"cycle": list(c), "meaning": f"{c[0]} > {c[1]} > {c[2]} > {c[0]}"} for c in sorted(cycles)]
