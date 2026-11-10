"""Generate a synthetic preference dataset with deliberately injected defects, so the checks can be demonstrated.

All data is fabricated: prompts and responses are templated text. Seeded for reproducibility.
"""
import json
import random
import sys

TOPICS = ["unit testing", "API versioning", "database indexes", "code review", "CI pipelines",
          "regression testing", "flaky tests", "test data management"]


def make_response(topic, quality, rng):
    base = f"{topic.capitalize()} helps teams catch problems early."
    if quality >= 2:
        base += " Start small, automate the repeatable parts, and review failures together."
    if quality >= 3:
        base += " Track results over time so regressions are visible before release."
    if quality == 0:
        base = f"{topic.capitalize()} is good."
    return base


def generate(n_prompts=40, seed=7, inject_defects=True):
    rng = random.Random(seed)
    annotators = ["ann_01", "ann_02", "ann_03"]
    records, rid = [], 0
    for p in range(n_prompts):
        topic = TOPICS[p % len(TOPICS)]
        prompt = f"Explain the role of {topic} in software quality. (item {p})"
        qa, qb = rng.randint(0, 3), rng.randint(0, 3)
        if qa == qb:
            qb = (qb + 1) % 4
        ra, rb = make_response(topic, qa, rng), make_response(topic, qb, rng)
        for ann in annotators:
            truth = "A" if qa > qb else "B"
            label = truth if rng.random() < 0.85 else ("B" if truth == "A" else "A")
            if inject_defects and ann == "ann_03" and rng.random() < 0.8:
                label = "A"  # injected defect: position-biased annotator
            rid += 1
            better = "first" if label == "A" else "second"
            rationale = (f"The {better} response is clearer and more complete on {topic}."
                         if not (inject_defects and rng.random() < 0.12) else "better")
            records.append({"id": f"r{rid:04d}", "prompt": prompt, "response_a": ra, "response_b": rb,
                            "response_a_id": f"p{p}a", "response_b_id": f"p{p}b",
                            "label": label, "annotator_id": ann, "rationale": rationale})
    if inject_defects:
        records.append(dict(records[0]))                                   # exact duplicate record
        records.append({"id": "r9001", "prompt": "Identical pair", "response_a": "Same answer.",
                        "response_b": "Same answer.", "label": "A", "annotator_id": "ann_01",
                        "rationale": "I picked the first one arbitrarily here."})  # degenerate pair
        records.append({"id": "r9002", "prompt": "Bad label", "response_a": "x", "response_b": "y",
                        "label": "maybe", "annotator_id": "ann_02"})       # schema violation
    return records


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "data/sample_preferences.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for rec in generate():
            f.write(json.dumps(rec) + "\n")
    print(f"wrote {out}")
