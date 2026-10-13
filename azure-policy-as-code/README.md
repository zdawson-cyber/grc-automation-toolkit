# Azure Policy as Code | Cloud Security Guardrails

**Resume-ready lab:** Three custom Azure Policy definitions implementing auditable storage security guardrails, with synthetic positive/negative test fixtures and automated CI validation. **No Azure deployment has been performed.** Compatible with Azure public cloud in principle; Azure Government applicability and available aliases must be independently verified in the target environment.

## Controls
| Policy definition | Resource property | Audit intent | Illustrative NIST alignment |
|---|---|---|---|
| require-https | supportsHttpsTrafficOnly | TLS/HTTPS requirement | SC-8 |
| disable-public-blob | allowBlobPublicAccess | Prevent anonymous blob access | AC-3 |
| disable-shared-key | allowSharedKeyAccess | Prefer identity-based authorization | IA-2, AC-3 |

Mappings are illustrative, not formal control satisfaction or compliance accreditation. Policies are configured to **Audit** by default; alternatives are Deny or Disabled. Audit only reports—not remediates—noncompliance. A denied configuration might disrupt a workload; evaluate exceptions and dependencies before changing the effect.

## Repository structure
- `policies/`: Azure custom policy definition JSON documents
- `fixtures/`: fictional storage accounts (secure/legacy) and an out-of-scope VM
- `scripts/validate.py`: checks definition shape and locally evaluates this narrow set of known properties
- `tests/`: unit tests including negative cases

## Run without Azure
From the repository root:

```bash
python -m unittest discover -s azure-policy-as-code/tests -v
python azure-policy-as-code/scripts/validate.py --output /tmp/azure-policy-report.json
```

Expected lab observations: 3 compliant, 3 noncompliant, 3 not applicable. This **local simulator is not the Azure Policy evaluation service**. The repo's GitHub Actions test workflow also runs these tests.

## Optional Azure deployment — manual and audit-only
Requires Azure CLI, an authorized **test** subscription, and permission to create policy definitions/assignments. Never deploy to a production or government subscription before change approval. Azure Cloud Shell can provide the CLI.

```bash
az login
az account set --subscription "<TEST_SUBSCRIPTION_ID>"
az account show --query "{name:name,id:id}" -o table

az policy definition create \
  --name "portfolio-require-https" \
  --display-name "Portfolio: Require secure storage transfer" \
  --description "Synthetic portfolio lab - storage secure transfer" \
  --mode All \
  --rules azure-policy-as-code/deploy/require-https-rule.json \
  --params azure-policy-as-code/deploy/effect-parameters.json

az policy assignment create \
  --name "portfolio-https-audit" \
  --display-name "Portfolio HTTPS audit (test only)" \
  --policy "portfolio-require-https" \
  --scope "/subscriptions/<TEST_SUBSCRIPTION_ID>/resourceGroups/<TEST_RESOURCE_GROUP>" \
  --params '{"effect":{"value":"Audit"}}'
```

The `deploy` artifacts isolate the `policyRule` and `parameters` for CLI usage. **These commands are instructions only and are not executed in CI.** Validate the CLI syntax against the installed Azure CLI release and check resource provider aliases before deploying.

## Case study
**Challenge:** Security baseline checks are often manually reviewed with inconsistent evidence and limited repeatability.

**Solution:** Define declarative Azure Policy rules, test expected behavior on synthetic compliant and noncompliant resources, and use CI to detect regression. Default to audit for a safer assessment-first approach.

**Demonstration:** Three storage configuration rules; three fixture states per rule; automated validation with reproducible pass/fail results. This does not establish tenant-level compliance or production impact.

## Interview talking points
1. Why **Audit** precedes **Deny** during rollout.
2. Difference between preventive governance and detective evidence checks.
3. How to scope assignments by resource group, document exemptions, and handle legacy apps before enabling Deny.
4. Why NIST control mappings require a full implementation narrative and assessor review beyond a policy result.

## Resume bullet
> Developed Azure Policy-as-Code security guardrails for storage transport encryption, anonymous blob exposure, and shared-key authorization; built Python-based synthetic compliance validation and automated CI regression tests.

## References
- https://learn.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure
- https://learn.microsoft.com/en-us/azure/storage/common/policy-reference
- https://learn.microsoft.com/en-us/cli/azure/policy/definition
