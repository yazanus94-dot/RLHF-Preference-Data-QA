"""Quality checks for preference datasets. Each returns plain, JSON-friendly findings."""
from collections import Counter, defaultdict

from .stats import binomial_two_sided_p


def words(text: str) -> int:
    return len(text.split())


def find_duplicates(records):
    """Same annotator judging the same pair twice, or a repeated record id."""
    seen_ids, seen_pairs, dups = Counter(), {}, []
    for rec in records:
        seen_ids[rec["id"]] += 1
        key = (rec["annotator_id"], rec["prompt"], rec["response_a"], rec["response_b"])
        if key in seen_pairs:
            dups.append({"id": rec["id"], "duplicate_of": seen_pairs[key], "reason": "same annotator, same pair"})
        else:
            seen_pairs[key] = rec["id"]
    for rid, count in seen_ids.items():
        if count > 1:
            dups.append({"id": rid, "duplicate_of": rid, "reason": f"record id appears {count} times"})
    return dups


def find_degenerate(records):
    """Pairs that cannot be meaningfully judged: identical responses given a winner."""
    issues = []
    for rec in records:
        a, b = rec["response_a"].strip(), rec["response_b"].strip()
        if a == b and rec["label"] != "tie":
            issues.append({"id": rec["id"], "reason": "identical responses but a winner was chosen"})
    return issues


def position_bias(records, alpha=0.01, min_n=20):
    """Does the annotator (or dataset) prefer slot A (or B) more than chance allows?"""
    by_annotator = defaultdict(list)
    for rec in records:
        if rec["label"] in ("A", "B"):
            by_annotator[rec["annotator_id"]].append(rec["label"])
    findings = []
    for annotator, labels in sorted(by_annotator.items()):
        n, a_count = len(labels), labels.count("A")
        p = binomial_two_sided_p(a_count, n)
        findings.append({"annotator_id": annotator, "n": n, "share_A": round(a_count / n, 3),
                         "p_value": round(p, 5), "flagged": n >= min_n and p < alpha})
    return findings


def length_bias(records, threshold=0.75, min_n=30):
    """Share of decisive labels where the longer response won (verbosity bias)."""
    longer_wins, n = 0, 0
    for rec in records:
        if rec["label"] not in ("A", "B"):
            continue
        wa, wb = words(rec["response_a"]), words(rec["response_b"])
        if wa == wb:
            continue
        n += 1
        winner_longer = (rec["label"] == "A") == (wa > wb)
        longer_wins += winner_longer
    share = longer_wins / n if n else 0.0
    return {"n": n, "longer_wins_share": round(share, 3), "flagged": n >= min_n and share >= threshold}


def weak_rationales(records, min_words=6):
    """Decisive labels with a missing or too-short justification."""
    issues = []
    for rec in records:
        if rec["label"] in ("A", "B"):
            rationale = (rec.get("rationale") or "").strip()
            if words(rationale) < min_words:
                issues.append({"id": rec["id"], "reason": "missing or very short rationale"})
    return issues
