#!/usr/bin/env bash
set -euo pipefail
: "${AZURE_TEST_SUBSCRIPTION_ID:?Set AZURE_TEST_SUBSCRIPTION_ID}"
: "${AZURE_TEST_RESOURCE_GROUP:?Set AZURE_TEST_RESOURCE_GROUP}"
[[ "${CONFIRM_DELETE_LAB_POLICIES:-}" == "YES" ]] || { echo "Set CONFIRM_DELETE_LAB_POLICIES=YES to delete ONLY portfolio- policies."; exit 1; }
ACCOUNT="$(az account show --query id -o tsv)"
[[ "$ACCOUNT" == "$AZURE_TEST_SUBSCRIPTION_ID" ]] || { echo "Wrong selected subscription"; exit 1; }
RG_ID="$(az group show --name "$AZURE_TEST_RESOURCE_GROUP" --query id -o tsv)"
for NAME in require-https disable-public-blob disable-shared-key; do
  az policy assignment delete --name "portfolio-$NAME" --scope "$RG_ID" --output none
done
for NAME in require-https disable-public-blob disable-shared-key; do
  az policy definition delete --name "portfolio-$NAME" --output none
done
echo "Removed lab assignments and definitions. No resource group or storage account was deleted."
