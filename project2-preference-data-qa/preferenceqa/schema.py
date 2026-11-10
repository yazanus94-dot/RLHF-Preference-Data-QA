"""Schema validation for pairwise preference records (one annotator judgement per record)."""
import json
from pathlib import Path

VALID_LABELS = {"A", "B", "tie"}
REQUIRED_FIELDS = ("id", "prompt", "response_a", "response_b", "label", "annotator_id")


def load_jsonl(path):
    records = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def validate_record(rec: dict) -> list:
    """Return a list of human-readable problems (empty list means the record is valid)."""
    problems = []
    for field in REQUIRED_FIELDS:
        if field not in rec or rec[field] in (None, ""):
            problems.append(f"missing field '{field}'")
    if rec.get("label") not in VALID_LABELS and "label" in rec and rec["label"] not in (None, ""):
        problems.append(f"invalid label '{rec['label']}' (expected one of {sorted(VALID_LABELS)})")
    for side in ("response_a", "response_b"):
        if side in rec and isinstance(rec[side], str) and not rec[side].strip():
            problems.append(f"{side} is empty")
    return problems


def validate_all(records) -> dict:
    """Map record id -> list of problems, only for records that have problems."""
    out = {}
    for i, rec in enumerate(records):
        problems = validate_record(rec)
        if problems:
            out[rec.get("id", f"index-{i}")] = problems
    return out
