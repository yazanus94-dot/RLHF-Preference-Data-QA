"""Small statistics helpers (standard library only)."""
from math import comb


def binomial_two_sided_p(successes: int, n: int, p: float = 0.5) -> float:
    """Exact two-sided binomial test p-value."""
    if n == 0:
        return 1.0
    pmf = [comb(n, k) * (p ** k) * ((1 - p) ** (n - k)) for k in range(n + 1)]
    observed = pmf[successes]
    return min(1.0, sum(x for x in pmf if x <= observed + 1e-12))


def cohen_kappa(labels_1, labels_2) -> float:
    """Cohen's kappa for two raters over the same items."""
    if len(labels_1) != len(labels_2) or not labels_1:
        raise ValueError("label lists must be non-empty and of equal length")
    n = len(labels_1)
    categories = set(labels_1) | set(labels_2)
    observed = sum(a == b for a, b in zip(labels_1, labels_2)) / n
    expected = sum((labels_1.count(c) / n) * (labels_2.count(c) / n) for c in categories)
    if expected == 1:
        return 1.0
    return (observed - expected) / (1 - expected)
