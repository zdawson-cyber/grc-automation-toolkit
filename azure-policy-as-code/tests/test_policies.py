import importlib.util
import json
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validator", BASE / "scripts/validate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class AzurePolicyTests(unittest.TestCase):
    def test_definitions_and_expected_results(self):
        results = module.run()
        self.assertEqual(len(results), 9)
        self.assertEqual(sum(x["status"] == "COMPLIANT" for x in results), 3)
        self.assertEqual(sum(x["status"] == "NONCOMPLIANT" for x in results), 3)
        self.assertEqual(sum(x["status"] == "NOT_APPLICABLE" for x in results), 3)

    def test_default_effect_audit(self):
        for name in module.EXPECTED:
            p = json.loads((BASE / "policies" / f"{name}.json").read_text())
            self.assertEqual(p["properties"]["parameters"]["effect"]["defaultValue"], "Audit")

    def test_missing_setting_fails_fixture(self):
        self.assertEqual(module.check_resource("require-https", {"type": "Microsoft.Storage/storageAccounts", "properties": {}}), "NONCOMPLIANT")

if __name__ == "__main__":
    unittest.main()
