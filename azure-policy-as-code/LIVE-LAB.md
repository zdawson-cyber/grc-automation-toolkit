# Azure Policy live lab: safe deployment and evidence capture

**Status: deployment scripts authored; Azure deployment NOT performed.**

This walkthrough uses **an existing dedicated NONPRODUCTION Azure resource group**. It creates custom policy definitions at the currently selected subscription and applies them **only to that resource group**. It does **not** create storage accounts, incur storage costs, or change existing resource settings. Azure role permissions to create definitions and assignments are required; never use an organizational subscription without written authorization.

## Before deployment

1. In Azure Cloud Shell (Bash) or a workstation with Azure CLI and Python 3, clone the repository.
2. Select an approved test subscription and existing test resource group. Do not include identifiers in public screenshots.
3. Check policy aliases in the targeted Azure cloud/region and confirm that no conflicting portfolio-named definitions exist.
4. Ensure organizational policies allow adding scoped custom audit assignments.

```bash
git clone https://github.com/zdawson-cyber/grc-automation-toolkit.git
cd grc-automation-toolkit
az login
az account list -o table
az account set --subscription "<TEST_SUBSCRIPTION_ID>"
az account show --query "{id:id,name:name}" -o table
az provider show --namespace Microsoft.Storage --expand "resourceTypes/aliases" --query "resourceTypes[?resourceType=='storageAccounts'].aliases[].name" -o tsv

export AZURE_TEST_SUBSCRIPTION_ID="<TEST_SUBSCRIPTION_ID>"
export AZURE_TEST_RESOURCE_GROUP="<EXISTING_TEST_RESOURCE_GROUP>"
export CONFIRM_TEST_SCOPE=YES
bash azure-policy-as-code/deploy/deploy-audit.sh
```

The deployment script **fails closed** if the selected Azure subscription does not match. All assignments use the **Audit** effect; it does not apply Deny, remediate, or create an Azure resource.

## Demonstrate the control

Use an already approved test storage account inside the lab resource group or create one manually after reviewing Azure cost estimates. A secure account may show Compliant; deliberately weaker configurations require separate explicit permission and should not be deployed in production. Azure Policy evaluation may be delayed.

From the Azure Portal, open **Policy > Compliance**, filter to the test resource group and the three `portfolio-` assignments, then review policy/resource compliance. Do not infer a noncompliant result just because the local fixtures show one.

```bash
export EVIDENCE_OUTPUT_DIR="./azure-policy-evidence"
bash azure-policy-as-code/deploy/collect-evidence.sh
```

Collected artifacts include assignment IDs and Azure's actual policy states. The output directory is gitignored, because exported metadata and resource IDs can be sensitive. Redact before preparing a public portfolio screenshot. Document date, cloud, subscription type (not ID), applicable resource, actual policy result, and any timing caveats.

## Cleanup

```bash
export CONFIRM_DELETE_LAB_POLICIES=YES
bash azure-policy-as-code/deploy/cleanup.sh
```

This deletes only `portfolio-` assignments in the named lab RG and three named policy definitions from the selected subscription. It does not delete resources. Do not run cleanup if you have reused these names for other workloads.

## Portfolio evidence template

| Field | Fill after Azure validation |
|---|---|
| Cloud | Azure commercial / Azure Government |
| Environment | Nonproduction sandbox |
| Policy definition(s) | |
| Scope | Test resource group (sanitized) |
| Date/time of evaluation | |
| Actual compliant/noncompliant count | |
| Review of false positives / exceptions | |
| Screenshots or sanitized artifacts | |
| Cleanup completed | |

**Resume phrasing until deployed:** “Implemented and tested Azure Policy-as-Code definitions using synthetic compliance scenarios.” Only claim **deployed and validated in Azure** after real deployment, assessment, and evidence collection.

References: [Azure CLI policy definition](https://learn.microsoft.com/en-us/cli/azure/policy/definition), [assignments](https://learn.microsoft.com/en-us/cli/azure/policy/assignment), [creating policies](https://learn.microsoft.com/en-us/azure/governance/policy/how-to/programmatically-create).
