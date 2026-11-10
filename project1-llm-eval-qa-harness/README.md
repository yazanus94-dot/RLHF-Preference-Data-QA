# LLM Response Evaluation Harness

A small, dependency-free Python framework for **QA of AI model outputs**: rule-based checks, weighted rubric
scoring, repeated runs to expose flaky (non-deterministic) behaviour, and a pass/fail **release gate**.

> **Portfolio project by Yazan Aljabari.** Built to demonstrate QA methodology for model evaluation.
> All prompts, answers and data are synthetic, and the "model" is a seeded mock so results are reproducible offline.
> No client or employer data is used.

## Why this exists
Model outputs are not always identical, so exact-match assertions don't work. This harness asserts on
**properties** (correct number, valid structure, no PII leak, correct refusal behaviour, length limits),
scores them with a rubric, and repeats each case several times to measure stability.

## What it checks
| Check | What it verifies |
|---|---|
| `numeric_answer` | final number matches the expected value (with tolerance) |
| `required_terms` / `forbidden_terms` | key facts present, wrong facts absent |
| `valid_json` | output parses and has the required keys |
| `no_pii` | no email addresses or phone-like numbers leaked |
| `max_words` | respects length instructions |
| `refusal` | refuses unsafe requests **and** does not over-refuse benign ones |

Each check has a **weight**, and can be marked **critical** (a hard gate: one critical failure fails the case).

## Design decisions
- **Property assertions over exact text**, because valid answers vary in wording.
- **Repeated runs** per case; a case with a pass rate strictly between 0% and 100% is reported as *flaky*.
- **Critical vs weighted checks**, so safety/privacy failures cannot be averaged away by other passing checks.
- **Seeded mock model**, so every result can be reproduced and the harness itself is testable.
- **Release gate** with an exit code (0/1), so it can run in CI.

## Run it
```bash
pip install -r requirements.txt
python -m pytest -q                                   # 17 tests
python -m evalharness.runner --runs 5                 # normal (slightly flaky) model -> gate PASS
python -m evalharness.runner --runs 5 --bad-rate 0.9  # degraded model -> gate FAIL (exit code 1)
```
Outputs `report/report.md` and `report/results.json`.

## Limitations (honest notes)
- The checks are rule-based; they can't judge nuance, tone or deep reasoning. For those, human review or a
  calibrated model-based grader is needed.
- The numeric check treats the last number in the text as the answer; a real project would parse structured output.
- The mock model stands in for a real API; swapping in a real model only requires a function `(case_id, prompt) -> str`.

## Project layout
```
evalharness/   checks.py, rubric.py, runner.py, mock_model.py
data/          eval_cases.jsonl  (10 synthetic cases)
tests/         pytest suite
.github/       CI workflow
```
