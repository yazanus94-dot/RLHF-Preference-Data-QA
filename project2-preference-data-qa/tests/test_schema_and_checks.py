from preferenceqa import checks, schema


def rec(i="r1", label="A", ann="a1", ra="Resp A text", rb="Resp B text", prompt="p", rationale=""):
    return {"id": i, "prompt": prompt, "response_a": ra, "response_b": rb, "label": label,
            "annotator_id": ann, "rationale": rationale}


def test_valid_record_has_no_problems():
    assert schema.validate_record(rec()) == []


def test_missing_and_invalid_fields_reported():
    bad = rec(label="maybe")
    assert any("invalid label" in p for p in schema.validate_record(bad))
    no_ann = rec()
    del no_ann["annotator_id"]
    assert any("annotator_id" in p for p in schema.validate_record(no_ann))
    assert any("empty" in p for p in schema.validate_record(rec(ra="  ")))


def test_validate_all_maps_ids():
    out = schema.validate_all([rec("ok"), rec("bad", label="x")])
    assert list(out) == ["bad"]


def test_duplicates_detected():
    dups = checks.find_duplicates([rec("r1"), rec("r2"), rec("r1")])
    reasons = {d["reason"] for d in dups}
    assert "same annotator, same pair" in reasons
    assert any("appears 2 times" in r for r in reasons)


def test_degenerate_pairs():
    flagged = checks.find_degenerate([rec(ra="same", rb="same", label="A"), rec("t", ra="same", rb="same", label="tie")])
    assert [f["id"] for f in flagged] == ["r1"]


def test_position_bias_flags_always_a_annotator():
    records = [rec(f"x{i}", label="A", ann="biased") for i in range(30)]
    records += [rec(f"y{i}", label="A" if i % 2 else "B", ann="fair") for i in range(30)]
    by = {f["annotator_id"]: f for f in checks.position_bias(records)}
    assert by["biased"]["flagged"] and not by["fair"]["flagged"]


def test_position_bias_needs_minimum_sample():
    records = [rec(f"x{i}", label="A") for i in range(5)]
    assert not checks.position_bias(records)[0]["flagged"]


def test_length_bias():
    long_, short_ = "word " * 20, "word " * 5
    records = [rec(f"i{i}", label="A", ra=long_, rb=short_) for i in range(40)]
    assert checks.length_bias(records)["flagged"]
    balanced = [rec(f"j{i}", label="A" if i % 2 else "B", ra=long_, rb=short_) for i in range(40)]
    assert not checks.length_bias(balanced)["flagged"]


def test_weak_rationales_only_for_decisive_labels():
    records = [rec("a", label="A", rationale="short"), rec("b", label="tie", rationale=""),
               rec("c", label="B", rationale="This answer explains the trade-offs much more clearly.")]
    assert [i["id"] for i in checks.weak_rationales(records)] == ["a"]
