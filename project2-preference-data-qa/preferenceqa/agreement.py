"""Inter-annotator agreement on items judged by more than one annotator."""
from collections import Counter, defaultdict
from itertools import combinations

from .stats import cohen_kappa


def item_key(rec):
    return (rec["prompt"], rec["response_a"], rec["response_b"])


def group_by_item(records):
    groups = defaultdict(dict)
    for rec in records:
        groups[item_key(rec)][rec["annotator_id"]] = rec["label"]
    return groups


def pairwise_kappa(records, min_overlap=10):
    groups = group_by_item(records)
    annotators = sorted({r["annotator_id"] for r in records})
    rows = []
    for a1, a2 in combinations(annotators, 2):
        shared = [labels for labels in groups.values() if a1 in labels and a2 in labels]
        if len(shared) < min_overlap:
            continue
        l1 = [s[a1] for s in shared]
        l2 = [s[a2] for s in shared]
        rows.append({"annotators": [a1, a2], "overlap": len(shared),
                     "raw_agreement": round(sum(x == y for x, y in zip(l1, l2)) / len(shared), 3),
                     "kappa": round(cohen_kappa(l1, l2), 3)})
    return rows


def majority_labels(records):
    """Majority label per item; items with no clear majority are returned as 'no_consensus'."""
    result = {}
    for key, labels in group_by_item(records).items():
        counts = Counter(labels.values()).most_common()
        if len(counts) > 1 and counts[0][1] == counts[1][1]:
            result[key] = "no_consensus"
        else:
            result[key] = counts[0][0]
    return result


def disagreements(records):
    """Items where annotators did not all give the same label (candidates for adjudication)."""
    return [{"prompt": k[0][:60], "labels": labels}
            for k, labels in group_by_item(records).items() if len(set(labels.values())) > 1]
