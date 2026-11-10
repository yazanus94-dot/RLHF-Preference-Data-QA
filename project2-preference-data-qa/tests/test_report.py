from preferenceqa.cli import main
from preferenceqa.report import build_report, to_markdown
from preferenceqa.schema import load_jsonl
from preferenceqa.synthetic import generate

DATA = "data/sample_preferences.jsonl"


def test_report_finds_every_injected_defect():
    report = build_report(generate(seed=7, inject_defects=True))
    flags = " ".join(report["flags"])
    assert "schema validation" in flags
    assert "duplicate" in flags
    assert "identical-response" in flags
    assert "ann_03 shows position bias" in flags


def test_clean_synthetic_data_has_no_defect_flags():
    report = build_report(generate(seed=7, inject_defects=False))
    assert report["schema_problems"] == {}
    assert report["duplicates"] == []
    assert report["degenerate_pairs"] == []
    assert not any(f["flagged"] for f in report["position_bias"])


def test_synthetic_generation_is_reproducible():
    assert generate(seed=3) == generate(seed=3)


def test_markdown_contains_sections():
    md = to_markdown(build_report(load_jsonl(DATA)))
    assert "## Flags" in md and "Cohen's kappa" in md


def test_cli_returns_nonzero_when_flags_exist(tmp_path):
    assert main([DATA, "--out", str(tmp_path)]) == 1
    assert (tmp_path / "report.json").exists() and (tmp_path / "report.md").exists()
