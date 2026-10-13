#!/usr/bin/env bash
set -euo pipefail
: "${AZURE_TEST_SUBSCRIPTION_ID:?Set AZURE_TEST_SUBSCRIPTION_ID}"
: "${AZURE_TEST_RESOURCE_GROUP:?Set AZURE_TEST_RESOURCE_GROUP}"
ACCOUNT="$(az account show --query id -o tsv)"
[[ "$ACCOUNT" == "$AZURE_TEST_SUBSCRIPTION_ID" ]] || { echo "Wrong selected Azure subscription"; exit 1; }
RG_ID="$(az group show --name "$AZURE_TEST_RESOURCE_GROUP" --query id -o tsv)"
OUT="${EVIDENCE_OUTPUT_DIR:-./azure-policy-evidence}"
mkdir -p "$OUT"
az policy state list --resource-group "$AZURE_TEST_RESOURCE_GROUP" \
  --query "[?contains(policyAssignmentName, 'portfolio-')].{resourceId:resourceId,policyAssignmentName:policyAssignmentName,complianceState:complianceState,timestamp:timestamp}" \
  -o json > "$OUT/policy-states.json"
az policy assignment list --scope "$RG_ID" \
  --query "[?starts_with(name, 'portfolio-')].{name:name,id:id,policyDefinitionId:policyDefinitionId}" \
  -o json > "$OUT/assignments.json"
echo "Exported Azure Policy findings to $OUT."
echo "Review these outputs before sharing: resource IDs, subscription IDs, and metadata can be sensitive."
echo "Only publish redacted examples after review. Azure Policy evaluation can take time."
