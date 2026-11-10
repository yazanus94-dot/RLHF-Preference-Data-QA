# QA for AI / RLHF: Two Portfolio Projects

[![Tests](https://github.com/yazanus94-dot/RLHF-Preference-Data-QA/actions/workflows/ci.yml/badge.svg)](https://github.com/yazanus94-dot/RLHF-Preference-Data-QA/actions/workflows/ci.yml)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Author: **Yazan Aljabari** | QA Automation Engineer | GitHub: https://github.com/yazanus94-dot

Two small, fully tested, dependency-free Python projects that show how I approach quality assurance for AI systems:

| # | Project | Question it answers | Highlights |
|---|---------|--------------------|------------|
| 1 | [project1-llm-eval-qa-harness](project1-llm-eval-qa-harness/) | How do we QA model *responses*? | Property-based checks (numeric tolerance, JSON validity, PII leak, refusal correctness), weighted rubric scoring, **critical vs weighted checks**, repeated runs expose **non-deterministic (flaky)** outputs, pass/fail release gate |
| 2 | [project2-preference-data-qa](project2-preference-data-qa/) | How do we audit RLHF *preference data*? | Exact binomial tests for **position bias**, likelihood weighting for **verbosity bias**, per-annotator **Cohen's kappa**, transitivity-cycle detection for inconsistent preferences, duplicate-work and malformed-record detection |

## Method, not demo data

Both projects run entirely on synthetic data with **deliberately injected defects** — biased annotators, duplicate judgments, flaky answers — so every detector and statistic is demonstrated against a *known* problem, not a best case. A seeded mock model keeps results reproducible offline; pointing the harness at a real inference backend requires no code change beyond the backend interface.

Key statistical choices: bias flags use exact binomial tests with minimum-sample guards (no false alarms from small samples), and inter-annotator agreement is reported as Cohen's kappa rather than raw agreement, which is inflated by chance on imbalanced labels.

## Quick start

```bash
# 1. LLM response evaluation harness
cd project1-llm-eval-qa-harness
pip install -r requirements.txt
python -m pytest -q
python -m evalharness.runner --runs 5 --threshold 0.85

# 2. Preference-data QA toolkit
cd ../project2-preference-data-qa
pip install -r requirements.txt
python -m pytest -q
```

CI runs the same suites on Python 3.11 / 3.12 / 3.13 on every push, including the end-to-end harness run against its release gate.

## Scope and honesty

Personal portfolio projects, not client or employer work. All data is synthetic; nothing here is a statement about any real model, annotator pool, or company dataset.

## License

MIT, see [LICENSE](LICENSE).
