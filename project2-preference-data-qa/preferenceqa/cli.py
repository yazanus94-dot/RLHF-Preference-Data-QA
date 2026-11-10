import argparse
import json
import sys
from pathlib import Path

from .report import build_report, to_markdown
from .schema import load_jsonl


def main(argv=None):
    p = argparse.ArgumentParser(description="QA checks for RLHF pairwise preference data.")
    p.add_argument("data", help="JSONL file of preference records")
    p.add_argument("--out", default="report", help="output directory")
    args = p.parse_args(argv)
    report = build_report(load_jsonl(args.data))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (out / "report.md").write_text(to_markdown(report), encoding="utf-8")
    print(to_markdown(report))
    return 1 if report["flags"] else 0


if __name__ == "__main__":
    sys.exit(main())
