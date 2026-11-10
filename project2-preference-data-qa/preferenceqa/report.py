"""Combine all checks into one report (dict + markdown)."""
from . import agreement, checks, consistency, schema


def build_report(records):
    valid_records = [r for r in records if not schema.validate_record(r)]
    report = {
        "total_records": len(records),
        "schema_problems": schema.validate_all(records),
        "duplicates": checks.find_duplicates(valid_records),
        "degenerate_pairs": checks.find_degenerate(valid_records),
        "position_bias": checks.position_bias(valid_records),
        "length_bias": checks.length_bias(valid_records),
        "weak_rationales": checks.weak_rationales(valid_records),
        "agreement": agreement.pairwise_kappa(valid_records),
        "disagreements": len(agreement.disagreements(valid_records)),
        "transitivity_violations": consistency.transitivity_violations(valid_records),
    }
    report["flags"] = _flags(report)
    return report


def _flags(r):
    flags = []
    if r["schema_problems"]:
        flags.append(f"{len(r['schema_problems'])} records fail schema validation")
    if r["duplicates"]:
        flags.append(f"{len(r['duplicates'])} duplicate judgements")
    if r["degenerate_pairs"]:
        flags.append(f"{len(r['degenerate_pairs'])} identical-response pairs with a winner")
    for f in r["position_bias"]:
        if f["flagged"]:
            flags.append(f"annotator {f['annotator_id']} shows position bias (A share {f['share_A']:.0%}, p={_fmt_p(f['p_value'])})")
    if r["length_bias"]["flagged"]:
        flags.append(f"possible length bias (longer response wins {r['length_bias']['longer_wins_share']:.0%})")
    low = [a for a in r["agreement"] if a["kappa"] < 0.4]
    if low:
        flags.append(f"{len(low)} annotator pair(s) with kappa below 0.4")
    if r["transitivity_violations"]:
        flags.append(f"{len(r['transitivity_violations'])} transitivity violation(s)")
    if r["weak_rationales"]:
        flags.append(f"{len(r['weak_rationales'])} decisive labels with weak rationale")
    return flags


def _fmt_p(p):
    return "<0.0001" if p < 0.0001 else str(p)


def to_markdown(report):
    lines = ["# Preference data QA report", "", f"Records analysed: **{report['total_records']}**", "",
             "## Flags", ""]
    lines += [f"- {f}" for f in report["flags"]] or ["- none"]
    lines += ["", "## Annotator agreement", "", "| Annotators | Overlap | Raw agreement | Cohen's kappa |", "|---|---|---|---|"]
    for a in report["agreement"]:
        lines.append(f"| {' / '.join(a['annotators'])} | {a['overlap']} | {a['raw_agreement']:.0%} | {a['kappa']} |")
    lines += ["", "## Position bias by annotator", "", "| Annotator | n | Share A | p-value | Flagged |", "|---|---|---|---|---|"]
    for f in report["position_bias"]:
        lines.append(f"| {f['annotator_id']} | {f['n']} | {f['share_A']:.0%} | {_fmt_p(f['p_value'])} | {'yes' if f['flagged'] else 'no'} |")
    return "\n".join(lines) + "\n"
