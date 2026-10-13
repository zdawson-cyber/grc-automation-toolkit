#!/usr/bin/env bash
set -euo pipefail

# Explicitly scoped, audit-only lab deployment. Does not create Azure resources.
: "${AZURE_TEST_SUBSCRIPTION_ID:?Set AZURE_TEST_SUBSCRIPTION_ID}"
: "${AZURE_TEST_RESOURCE_GROUP:?Set AZURE_TEST_RESOURCE_GROUP}"
[[ "${CONFIRM_TEST_SCOPE:-}" == "YES" ]] || { echo "Set CONFIRM_TEST_SCOPE=YES after checking the subscription/resource group are nonproduction."; exit 1; }
for cmd in az python3; do command -v "$cmd" >/dev/null || { echo "Missing $cmd"; exit 1; }; done
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ACCOUNT="$(az account show --query id -o tsv)"
[[ "$ACCOUNT" == "$AZURE_TEST_SUBSCRIPTION_ID" ]] || { echo "Selected subscription differs from AZURE_TEST_SUBSCRIPTION_ID"; exit 1; }
RG_ID="$(az group show --name "$AZURE_TEST_RESOURCE_GROUP" --query id -o tsv)"
EXPECTED_RG="/subscriptions/$AZURE_TEST_SUBSCRIPTION_ID/resourceGroups/$AZURE_TEST_RESOURCE_GROUP"
[[ "${RG_ID,,}" == "${EXPECTED_RG,,}" ]] || { echo "Scope does not match test resource group"; exit 1; }

TEMP="$(mktemp -d)"
trap 'rm -rf "$TEMP"' EXIT
echo "Selected subscription: $ACCOUNT"
echo "Approved lab scope: $RG_ID"
echo "Deploying Audit definitions and resource-group assignments ONLY."
for NAME in require-https disable-public-blob disable-shared-key; do
  python3 - "$ROOT/policies/$NAME.json" "$TEMP" "$NAME" <<'PY'
import json,sys,pathlib
doc=json.loads(pathlib.Path(sys.argv[1]).read_text())["properties"]
out=pathlib.Path(sys.argv[2]); name=sys.argv[3]
(out/f"{name}-rule.json").write_text(json.dumps(doc["policyRule"]))
(out/f"{name}-params.json").write_text(json.dumps(doc["parameters"]))
PY
  DEF_NAME="portfolio-$NAME"
  ASSIGN_NAME="portfolio-$NAME"
  if az policy definition show --name "$DEF_NAME" >/dev/null 2>&1; then
    echo "Definition $DEF_NAME already exists; refusing to overwrite."
    exit 1
  fi
  az policy definition create --subscription "$AZURE_TEST_SUBSCRIPTION_ID" \
    --name "$DEF_NAME" --display-name "Portfolio lab: $NAME" --mode All \
    --description "Test-only audit guardrail; synthetic portfolio project" \
    --rules "$TEMP/$NAME-rule.json" --params "$TEMP/$NAME-params.json" --output none
  DEF_ID="$(az policy definition show --name "$DEF_NAME" --query id -o tsv)"
  if az policy assignment show --name "$ASSIGN_NAME" --scope "$RG_ID" >/dev/null 2>&1; then
    echo "Assignment $ASSIGN_NAME already exists; refusing to overwrite."
    exit 1
  fi
  az policy assignment create --name "$ASSIGN_NAME" \
    --display-name "Portfolio lab audit: $NAME" --scope "$RG_ID" \
    --policy "$DEF_ID" --params '{"effect":{"value":"Audit"}}' --output none
  echo "Created $DEF_NAME and assigned Audit effect to $RG_ID"
done
echo "Azure Policy evaluation is asynchronous. Run collect-evidence.sh after Azure has evaluated resources."
