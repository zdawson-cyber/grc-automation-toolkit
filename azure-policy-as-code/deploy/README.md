# Lab scripts

These scripts are intentionally **manual** and are not invoked by GitHub Actions.

- `deploy-audit.sh`: requires an existing approved test resource group and explicit confirmation, then creates three audit-only custom definitions and scoped assignments.
- `collect-evidence.sh`: retrieves current Azure Policy results for human review; Azure evaluation is asynchronous.
- `cleanup.sh`: removes the three named portfolio assignments and definitions only after explicit confirmation.

See [LIVE-LAB.md](../LIVE-LAB.md). Do not commit credentials or unredacted Azure evidence.
