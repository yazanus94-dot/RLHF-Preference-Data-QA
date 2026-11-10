import pytest

from evalharness.rubric import Case, score_response


def make_case(**kw):
    base = {"id": "c1", "prompt": "p", "checks": [
        {"type": "required_terms", "params": {"terms": ["Paris"]}, "critical": True},
        {"type": "max_words", "params": {"max_words": 5}, "weight": 1}]}
    base.update(kw)
    return Case.from_dict(base)


def test_full_score_passes():
    r = score_response("It is Paris", make_case())
    assert r.score == 1.0 and r.passed and not r.critical_failed


def test_critical_failure_overrides_high_score():
    r = score_response("It is Lyon", make_case())
    assert r.critical_failed and not r.passed


def test_partial_score_with_weights():
    r = score_response("Paris is the capital city of France indeed", make_case(pass_score=0.9))
    assert r.score == 0.5 and not r.passed


def test_unknown_check_type_rejected():
    with pytest.raises(ValueError):
        Case.from_dict({"id": "x", "prompt": "p", "checks": [{"type": "nope"}]})
