# RLHF Preference Data QA Toolkit

A dependency-free Python toolkit that audits **pairwise preference data** (the kind used for RLHF / reward
modelling) for the problems that quietly damage training quality.

> **Portfolio project by Yazan Aljabari.** Built to demonstrate annotation-QA methodology.
> The dataset is **entirely synthetic** and generated with deliberately injected defects so the checks can be demonstrated.
> No client or employer data is used.

## What it detects
| Problem | How it is detected |
|---|---|
| Malformed records | schema validation (required fields, valid labels, empty responses) |
| Duplicate work | same annotator judging the same pair twice, repeated record ids |
| Unjudgeable pairs | identical responses where a winner was chosen |
| **Position bias** | exact two-sided binomial test on the share of "A" choices, per annotator |
| **Length (verbosity) bias** | how often the longer response wins, with minimum-sample guard |
| **Annotator disagreement** | pairwise **Cohen's kappa** and raw agreement on overlapping items |
| **Inconsistent preferences** | transitivity check: A>B, B>C, C>A cycles in majority-vote preferences |
| Weak justifications | decisive labels with a missing or very short rationale |

## Design decisions
- **Statistics, not guesses**: bias flags use an exact binomial test and a minimum sample size to avoid false alarms.
- **Per-annotator analysis**, because one biased annotator can be hidden by the average.
- **Kappa over raw agreement**, since raw agreement is inflated by chance when labels are imbalanced.
- **Valid records only** go into statistics; schema failures are reported separately.
- **Exit code** is non-zero when flags exist, so it can gate a data pipeline in CI.

## Run it
```bash
pip install -r requirements.txt
python -m pytest -q                                              # 26 tests
python -m preferenceqa.synthetic data/sample_preferences.jsonl   # regenerate synthetic data
python -m preferenceqa.cli data/sample_preferences.jsonl         # writes report/report.md + report.json
```

## Example finding (from the included synthetic data)
The report flags annotator `ann_03` for position bias (about 92% "A" choices, p < 0.0001) and shows
kappa of roughly 0.1 to 0.2 against the other annotators, while `ann_01` and `ann_02` agree much more (kappa about 0.65).

## Limitations (honest notes)
- Length bias is a heuristic (word count); a confound between length and true quality cannot be separated by this data alone.
- Transitivity needs repeated use of the same response across pairs; with one pair per prompt there is nothing to compare.
- Real pipelines would add rubric-specific checks and adjudication workflows.

## Project layout
```
preferenceqa/  schema.py, checks.py, agreement.py, consistency.py, stats.py, report.py, synthetic.py, cli.py
data/          sample_preferences.jsonl (synthetic)
tests/         pytest suite
.github/       CI workflow
```
