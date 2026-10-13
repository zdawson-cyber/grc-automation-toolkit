"""Local Azure Policy guardrail validation for synthetic storage resources.

This intentionally tests a narrow subset of Azure Policy and is not the Azure
Policy compliance engine. The Azure service must validate deployed definitions.
"""
import argparse
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
EXPECTED = {
    "require-https": ("Microsoft.Storage/storageAccounts/supportsHttpsTrafficOnly", True),
    "disable-public-blob": ("Microsoft.Storage/storageAccounts/allowBlobPublicAccess", False),
    "disable-shared-key": ("Microsoft.Storage/storageAccounts/allowSharedKeyAccess", False),
}

def validate_definition(name, policy):
    properties = policy["properties"]
    assert properties["mode"] == "All"
    param = properties["parameters"]["effect"]
    assert param["defaultValue"] == "Audit"
    assert set(param["allowedValues"]) == {"Audit", "Deny", "Disabled"}
    rule = properties["policyRule"]
    assert rule["then"]["effect"] == "[parameters('effect')]"
    conditions = rule["if"]["allOf"]
    assert conditions[0] == {"field": "type", "equals": "Microsoft.Storage/storageAccounts"}
    alias, expected = EXPECTED[name]
    assert conditions[1] == {"field": alias, "notEquals": expected}

def check_resource(name, resource):
    """Simple fixture evaluation, not a general Azure Policy interpreter."""
    alias, expected = EXPECTED[name]
    if resource["type"] != "Microsoft.Storage/storageAccounts":
        return "NOT_APPLICABLE"
    key = alias.rsplit("/", 1)[-1]
    actual = resource.get("properties", {}).get(key)
    return "COMPLIANT" if actual is expected else "NONCOMPLIANT"

def run():
    resources = json.loads((BASE / "fixtures/resources.json").read_text())["resources"]
    report = []
    for name in EXPECTED:
        doc = json.loads((BASE / "policies" / f"{name}.json").read_text())
        validate_definition(name, doc)
        for resource in resources:
            report.append({"policy": name, "resource_id": resource["id"], "status": check_resource(name, resource)})
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=BASE / "sample-report.json")
    args = parser.parse_args()
    report = run()
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    counts = {key: sum(x["status"] == key for x in report) for key in ("COMPLIANT", "NONCOMPLIANT", "NOT_APPLICABLE")}
    print("Synthetic fixture results:", counts)

if __name__ == "__main__":
    main()
