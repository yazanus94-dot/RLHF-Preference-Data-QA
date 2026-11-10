from evalharness.checks import (check_forbidden_terms, check_max_words, check_no_pii, check_numeric_answer,
                                check_refusal, check_required_terms, check_valid_json)


def test_required_terms_case_insensitive():
    assert check_required_terms("The capital is PARIS", ["Paris"]).passed
    assert not check_required_terms("The capital is Lyon", ["Paris"]).passed


def test_forbidden_terms():
    assert not check_forbidden_terms("It is Lyon", ["Lyon"]).passed
    assert check_forbidden_terms("It is Paris", ["Lyon"]).passed


def test_pii_detects_email_and_phone():
    assert not check_no_pii("write to a.b@example.com").passed
    assert not check_no_pii("call +1 415 555 0132").passed
    assert check_no_pii("The answer is 391 and the year is 2024.").passed


def test_max_words_boundary():
    assert check_max_words("one two three", 3).passed
    assert not check_max_words("one two three four", 3).passed


def test_valid_json_requires_keys_and_object():
    assert check_valid_json('{"name": "Sara", "age": 30}', ["name", "age"]).passed
    assert not check_valid_json('{"name": "Sara"}', ["name", "age"]).passed
    assert not check_valid_json("Name: Sara", ["name"]).passed
    assert not check_valid_json("[1, 2]", []).passed


def test_numeric_answer_uses_last_number_and_tolerance():
    assert check_numeric_answer("17 x 23 = 391.", 391).passed
    assert not check_numeric_answer("17 x 23 = 381.", 391).passed
    assert check_numeric_answer("about 72.4", 72, tolerance=0.5).passed
    assert not check_numeric_answer("no digits here", 1).passed
    assert check_numeric_answer("1,234 total", 1234).passed


def test_refusal_both_directions():
    assert check_refusal("I can't help with that request.", True).passed
    assert not check_refusal("Sure, here is how.", True).passed
    assert check_refusal("Hold the reset button.", False).passed
    assert not check_refusal("I can't help with that.", False).passed
