import pytest

from preferenceqa.stats import binomial_two_sided_p, cohen_kappa


def test_binomial_balanced_is_not_significant():
    assert binomial_two_sided_p(10, 20) == pytest.approx(1.0)


def test_binomial_extreme_is_significant():
    assert binomial_two_sided_p(20, 20) < 1e-5
    assert binomial_two_sided_p(0, 0) == 1.0


def test_binomial_known_value():
    # 9 of 10: two-sided p = 2 * (C(10,9) + C(10,10)) / 1024 = 22/1024
    assert binomial_two_sided_p(9, 10) == pytest.approx(22 / 1024)


def test_kappa_perfect_agreement():
    assert cohen_kappa(["A", "B", "A", "B"], ["A", "B", "A", "B"]) == pytest.approx(1.0)


def test_kappa_known_example():
    # 2x2 table: both A=20, both B=15, 1:A 5, 1:B 10 -> po=0.7, pe=0.5 -> kappa=0.4
    l1 = ["A"] * 20 + ["B"] * 15 + ["A"] * 5 + ["B"] * 10
    l2 = ["A"] * 20 + ["B"] * 15 + ["B"] * 5 + ["A"] * 10
    assert cohen_kappa(l1, l2) == pytest.approx(0.4)


def test_kappa_rejects_bad_input():
    with pytest.raises(ValueError):
        cohen_kappa([], [])
    with pytest.raises(ValueError):
        cohen_kappa(["A"], ["A", "B"])
