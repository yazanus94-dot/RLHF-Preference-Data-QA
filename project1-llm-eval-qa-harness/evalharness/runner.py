"""Runs a model over evaluation cases several times and reports pass rates, flakiness and a release gate."""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from .mock_model import MockModel
from .rubric import Case, score_response


def load_cases(path):
    cases = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            cases.append(Case.from_dict(json.loads(line)))
    return cases


def evaluate(model_fn, cases, runs=5):
    """Return per-run results. Several runs per case expose non-deterministic (flaky) behaviour."""
    results = []
    for run in range(1, runs + 1):
        for case in cases:
            response = model_fn(case.id, case.prompt)
            scored = score_response(response, case)
            results.append({"run": run, "case_id": case.id, "category": case.category,
                            "response": response, "score": scored.score, "passed": scored.passed,
                            "critical_failed": scored.critical_failed,
                            "failed_checks": [r.name + ": " + r.detail for r in scored.results if not r.passed]})
    return results


def summarize(results, threshold=0.85):
    per_case = defaultdict(list)
    for r in results:
        per_case[r["case_id"]].append(r)
    case_rows = []
    for case_id, rows in per_case.items():
        pass_rate = sum(r["passed"] for r in rows) / len(rows)
        case_rows.append({
            "case_id": case_id,
            "category": rows[0]["category"],
            "pass_rate": round(pass_rate, 3),
            "flaky": 0 < pass_rate < 1,
            "always_failing": pass_rate == 0,
            "critical_failures": sum(r["critical_failed"] for r in rows),
        })
    overall = sum(r["passed"] for r in results) / len(results)
    critical_total = sum(c["critical_failures"] for c in case_rows)
    gate_passed = overall >= threshold and critical_total == 0
    return {"overall_pass_rate": round(overall, 3), "threshold": threshold,
            "critical_failures": critical_total, "gate_passed": gate_passed,
            "cases": sorted(case_rows, key=lambda c: (c["pass_rate"], c["case_id"]))}


def to_markdown(summary):
    lines = ["# Evaluation report", "",
             f"- Overall pass rate: **{summary['overall_pass_rate']:.1%}** (threshold {summary['threshold']:.0%})",
             f"- Critical failures: **{summary['critical_failures']}**",
             f"- Release gate: **{'PASS' if summary['gate_passed'] else 'FAIL'}**", "",
             "| Case | Category | Pass rate | Flaky | Critical failures |", "|---|---|---|---|---|"]
    for c in summary["cases"]:
        lines.append(f"| {c['case_id']} | {c['category']} | {c['pass_rate']:.0%} | "
                     f"{'yes' if c['flaky'] else 'no'} | {c['critical_failures']} |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description="Run the LLM response evaluation harness.")
    p.add_argument("--cases", default="data/eval_cases.jsonl")
    p.add_argument("--runs", type=int, default=5)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--bad-rate", type=float, default=0.0, help="simulate a degraded model (0-1)")
    p.add_argument("--threshold", type=float, default=0.85)
    p.add_argument("--out", default="report")
    args = p.parse_args(argv)

    cases = load_cases(args.cases)
    results = evaluate(MockModel(args.seed, args.bad_rate), cases, args.runs)
    summary = summarize(results, args.threshold)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    (out / "report.md").write_text(to_markdown(summary), encoding="utf-8")
    print(to_markdown(summary))
    return 0 if summary["gate_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
