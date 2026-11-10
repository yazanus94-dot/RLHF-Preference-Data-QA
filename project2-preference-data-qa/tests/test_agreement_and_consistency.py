from preferenceqa import agreement, consistency


def rec(i, prompt, label, ann, ra="A text", rb="B text", ida=None, idb=None):
    r = {"id": i, "prompt": prompt, "response_a": ra, "response_b": rb, "label": label, "annotator_id": ann}
    if ida:
        r["response_a_id"], r["response_b_id"] = ida, idb
    return r


def test_pairwise_kappa_perfect_and_disagreeing():
    records = []
    for i in range(12):
        records.append(rec(f"a{i}", f"p{i}", "A" if i % 2 else "B", "x"))
        records.append(rec(f"b{i}", f"p{i}", "A" if i % 2 else "B", "y"))
    rows = agreement.pairwise_kappa(records)
    assert rows[0]["kappa"] == 1.0 and rows[0]["overlap"] == 12


def test_pairwise_kappa_skips_small_overlap():
    records = [rec("1", "p", "A", "x"), rec("2", "p", "A", "y")]
    assert agreement.pairwise_kappa(records) == []


def test_majority_and_no_consensus():
    records = [rec("1", "p", "A", "x"), rec("2", "p", "A", "y"), rec("3", "p", "B", "z"),
               rec("4", "q", "A", "x"), rec("5", "q", "B", "y")]
    labels = agreement.majority_labels(records)
    assert labels[("p", "A text", "B text")] == "A"
    assert labels[("q", "A text", "B text")] == "no_consensus"


def test_disagreements_listed():
    records = [rec("1", "q", "A", "x"), rec("2", "q", "B", "y"), rec("3", "p", "A", "x"), rec("4", "p", "A", "y")]
    assert len(agreement.disagreements(records)) == 1


def test_transitivity_cycle_detected():
    # r1 > r2, r2 > r3, r3 > r1  -> cycle
    records = [rec("1", "p1", "A", "x", "R1", "R2", "r1", "r2"),
               rec("2", "p2", "A", "x", "R2", "R3", "r2", "r3"),
               rec("3", "p3", "A", "x", "R3", "R1", "r3", "r1")]
    cycles = consistency.transitivity_violations(records)
    assert len(cycles) == 1 and set(cycles[0]["cycle"]) == {"r1", "r2", "r3"}


def test_transitive_preferences_have_no_cycle():
    records = [rec("1", "p1", "A", "x", "R1", "R2", "r1", "r2"),
               rec("2", "p2", "A", "x", "R2", "R3", "r2", "r3"),
               rec("3", "p3", "A", "x", "R1", "R3", "r1", "r3")]
    assert consistency.transitivity_violations(records) == []
