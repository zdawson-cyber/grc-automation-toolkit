"""Deterministic, synthetic RMF control evidence evaluator (not an ATO decision)."""
import argparse
import datetime as dt
import json
from pathlib import Path


class ValidationError(ValueError):
    """Input violates the documented evidence or control schema."""


def _read_date(value):
    if not isinstance(value, str):
        raise ValidationError("Date must be YYYY-MM-DD")
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError(f"Invalid date: {value!r}") from exc


def _number(value):
    return type(value) in (int, float) and not isinstance(value, bool)


def evaluate(controls_doc, evidence_doc):
    """Return (assessment, POA&M); fail closed on missing records."""
    as_of = _read_date(evidence_doc["as_of"])
    controls = controls_doc["controls"]
    records = evidence_doc["records"]
    if not isinstance(controls, list) or not isinstance(records, list):
        raise ValidationError("controls and records must be lists")
    if not isinstance(evidence_doc.get("system"), str) or not evidence_doc["system"]:
        raise ValidationError("system must be a nonempty string")
    lookup = {}
    for record in records:
        if not isinstance(record, dict):
            raise ValidationError("Evidence record must be an object")
        cid = record.get("control_id")
        if not isinstance(cid, str) or not cid or cid in lookup:
            raise ValidationError(f"Missing or duplicate evidence control ID: {cid!r}")
        lookup[cid] = record
    seen = set()
    results, poam = [], []
    for control in controls:
        if not isinstance(control, dict):
            raise ValidationError("Control must be an object")
        cid = control["id"]
        if not isinstance(cid, str) or cid in seen:
            raise ValidationError(f"Duplicate/invalid control ID: {cid!r}")
        seen.add(cid)
        op = control["operator"]
        if op not in {"equals", "max", "min", "age_days_max"}:
            raise ValidationError(f"Unsupported operator: {op}")
        record = lookup.get(cid)
        key = control["evidence_key"]
        actual = record.get(key) if record else None
        evidence_id = record.get("evidence_id") if record else None
        if record and (not isinstance(evidence_id, str) or not evidence_id):
            raise ValidationError(f"Invalid evidence ID for {cid}")
        reason = "Meets illustrative requirement"
        passed = False
        if actual is None:
            reason = "Required evidence missing"
        elif op == "equals":
            passed = type(actual) is type(control["expected"]) and actual == control["expected"]
        elif op in {"max", "min"}:
            if not _number(actual) or not _number(control["expected"]):
                reason = "Numeric evidence or threshold invalid"
            else:
                passed = actual <= control["expected"] if op == "max" else actual >= control["expected"]
        else:
            if not _number(control["expected"]) or control["expected"] < 0:
                raise ValidationError("age_days_max threshold must be nonnegative numeric")
            try:
                age = (as_of - _read_date(actual)).days
                if age < 0:
                    reason = "Evidence is future-dated"
                else:
                    passed = age <= control["expected"]
            except ValidationError:
                reason = "Date evidence invalid"
        if not passed and reason == "Meets illustrative requirement":
            reason = "Evidence outside expected threshold"
        result = {"control_id": cid, "title": control["title"], "status": "PASS" if passed else "FAIL",
                  "evidence_id": evidence_id, "observed": actual, "expected": control["expected"],
                  "operator": op, "reason": reason}
        results.append(result)
        if not passed:
            poam.append({"finding_id": f"DEMO-{cid.replace('-', '')}",
                         "system": evidence_doc["system"], "control_id": cid,
                         "severity": control["severity"], "status": "Open - draft",
                         "evidence_id": evidence_id, "observation": reason,
                         "remediation": control["remediation"], "owner": control["owner"],
                         "closure_criteria": "Independent reviewer verifies new dated evidence"})
    summary = {"passed": sum(r["status"] == "PASS" for r in results),
               "failed": sum(r["status"] == "FAIL" for r in results), "total": len(results)}
    report = {"system": evidence_doc["system"], "as_of": str(as_of), "summary": summary, "results": results,
              "disclaimer": "Synthetic portfolio lab; human assessor review required"}
    return report, poam


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controls", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--output", default=Path("output"), type=Path)
    args = parser.parse_args()
    try:
        controls = json.loads(args.controls.read_text(encoding="utf-8"))
        evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
        report, poam = evaluate(controls, evidence)
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "assessment_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (args.output / "poam.json").write_text(json.dumps(poam, indent=2) + "\n", encoding="utf-8")
        print(f"{report['summary']['passed']} passed; {report['summary']['failed']} failed; {len(poam)} draft POA&M findings")
        return 2 if poam else 0
    except (KeyError, ValidationError, json.JSONDecodeError, OSError, TypeError) as exc:
        parser.exit(status=1, message=f"Invalid input: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
