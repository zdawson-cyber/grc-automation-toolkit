import copy
import json
import unittest
from pathlib import Path
from src.assess import ValidationError, evaluate

ROOT = Path(__file__).resolve().parents[1]


class AssessmentTests(unittest.TestCase):
    def setUp(self):
        self.controls = json.loads((ROOT / "data/controls.json").read_text())
        self.evidence = json.loads((ROOT / "data/evidence.json").read_text())

    def test_expected_finding_counts_and_traceability(self):
        report, poam = evaluate(self.controls, self.evidence)
        self.assertEqual(report["summary"], {"passed": 3, "failed": 2, "total": 5})
        self.assertEqual({p["control_id"] for p in poam}, {"CM-6", "RA-5"})
        self.assertEqual(poam[0]["evidence_id"], "SYN-CFG-003")

    def test_missing_evidence_fails_closed(self):
        self.evidence["records"] = [r for r in self.evidence["records"] if r["control_id"] != "IA-2"]
        report, poam = evaluate(self.controls, self.evidence)
        self.assertEqual(report["summary"]["failed"], 3)
        self.assertIn("IA-2", {r["control_id"] for r in poam})

    def test_future_scan_date_fails(self):
        record = next(r for r in self.evidence["records"] if r["control_id"] == "RA-5")
        record["last_vulnerability_scan"] = "2026-10-14"
        report, _ = evaluate(self.controls, self.evidence)
        result = next(r for r in report["results"] if r["control_id"] == "RA-5")
        self.assertEqual(result["reason"], "Evidence is future-dated")

    def test_bool_does_not_pass_numeric_threshold(self):
        record = next(r for r in self.evidence["records"] if r["control_id"] == "CM-6")
        record["baseline_deviations"] = False
        report, _ = evaluate(self.controls, self.evidence)
        result = next(r for r in report["results"] if r["control_id"] == "CM-6")
        self.assertEqual(result["status"], "FAIL")

    def test_duplicate_evidence_rejected(self):
        self.evidence["records"].append(copy.deepcopy(self.evidence["records"][0]))
        with self.assertRaises(ValidationError):
            evaluate(self.controls, self.evidence)

    def test_unsupported_operator_rejected(self):
        self.controls["controls"][0]["operator"] = "eval"
        with self.assertRaises(ValidationError):
            evaluate(self.controls, self.evidence)

    def test_invalid_date_fails(self):
        self.evidence["as_of"] = "yesterday"
        with self.assertRaises(ValidationError):
            evaluate(self.controls, self.evidence)


if __name__ == "__main__":
    unittest.main()
