from evalharness.mock_model import MockModel
from evalharness.runner import evaluate, load_cases, main, summarize

CASES = "data/eval_cases.jsonl"


def test_cases_load():
    assert len(load_cases(CASES)) == 10


def test_results_are_reproducible_with_same_seed():
    cases = load_cases(CASES)
    a = evaluate(MockModel(seed=1), cases, runs=3)
    b = evaluate(MockModel(seed=1), cases, runs=3)
    assert [r["response"] for r in a] == [r["response"] for r in b]


def test_flaky_cases_are_detected():
    cases = load_cases(CASES)
    summary = summarize(evaluate(MockModel(seed=7), cases, runs=20))
    flaky = {c["case_id"] for c in summary["cases"] if c["flaky"]}
    assert {"math-002", "length-001"} <= flaky


def test_stable_cases_always_pass():
    cases = load_cases(CASES)
    summary = summarize(evaluate(MockModel(seed=7), cases, runs=10))
    rows = {c["case_id"]: c for c in summary["cases"]}
    assert rows["fact-001"]["pass_rate"] == 1.0 and not rows["fact-001"]["flaky"]


def test_degraded_model_fails_release_gate():
    cases = load_cases(CASES)
    summary = summarize(evaluate(MockModel(seed=7, global_bad_rate=0.9), cases, runs=5))
    assert not summary["gate_passed"]


def test_cli_exit_codes(tmp_path):
    assert main(["--cases", CASES, "--runs", "3", "--threshold", "0.5", "--out", str(tmp_path / "ok")]) == 0
    assert main(["--cases", CASES, "--runs", "3", "--bad-rate", "0.95", "--out", str(tmp_path / "bad")]) == 1
    assert (tmp_path / "ok" / "report.md").exists()
