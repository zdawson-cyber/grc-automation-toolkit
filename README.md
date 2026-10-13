# GRC Automation Toolkit | RMF Control Evidence & POA&M Engineering

A **working, synthetic-data portfolio project** showing how compliance requirements can become testable engineering checks, findings, and traceable remediation records. Built for GRC Engineering, Security Compliance Engineering, RMF, ISSO, and Cloud Security roles.

> **Portfolio demonstration only.** All organizations, systems, evidence, and observations are fictional. Control statements below are illustrative interpretations, not authoritative NIST text. This is not a FedRAMP assessment, CMMC certification, authorization decision, or substitute for assessor judgment. No CUI, classified information, client artifacts, credentials, or proprietary employer material is included.

## What it demonstrates
- **RMF / NIST SP 800-53:** machine-readable control-to-evidence traceability, requirement evaluation, and assessor-ready output
- **Compliance engineering:** deterministic Python rules, structured validation, unit tests, and GitHub Actions
- **POA&M workflows:** failed checks produce remediation records with evidence references and ownership
- **Auditability:** explainable pass/fail results without using AI to invent compliance decisions

## Architecture
```text
synthetic system inventory + control catalog + evidence.json
                         |
                         v
                Python evaluation engine
                         |
              +----------+----------+
              |                     |
      assessment report        POA&M JSON
              |
        GitHub Actions CI
```

## Quick start
Requires Python 3.10+; only Python standard library.

```bash
python -m unittest discover -s tests -v
python -m src.assess --controls data/controls.json --evidence data/evidence.json --output output
```

Outputs: `output/assessment_report.json` and `output/poam.json`. The `output/` directory is intentionally gitignored. Exit status is **2** if one or more checks fail, making policy failure detectable in CI; status 1 means malformed inputs or runtime errors. Sample fixtures intentionally include failures, so the assessment command exits 2.

## Included example checks
| Control | Illustrative engineering expectation | Synthetic outcome |
|---|---|---|
| AC-2 | Quarterly access review evidence exists and is current | Pass |
| IA-2 | MFA enabled for privileged accounts | Pass |
| CM-6 | Secure baseline deviation count is zero | Fail |
| RA-5 | Vulnerability scan is no more than 30 days old | Fail |
| AU-6 | Log review completed within the last 7 days | Pass |

The evaluator supports `equals`, `max`, `min`, and `age_days_max`. Missing/malformed evidence is a finding, not an automatic pass. Dates are evaluated relative to an explicit `as_of` date in fixture data for reproducible tests.

## Engineering choices
1. **Deterministic policy checks** produce reproducible results and traceable evidence IDs.
2. **Evidence is not blindly trusted:** missing fields, type errors, duplicate IDs, unsupported operators, and future-dated records are rejected.
3. **Failure does not equal authorization denial:** machine results identify observations requiring qualified human review.
4. **Sample data is synthetic:** the project intentionally makes no claim of production authorization or organizational past performance.

## Portfolio case study
**Problem:** Manually reconciling control narratives, technical evidence, and findings can introduce inconsistent determinations and delay remediation tracking.

**Approach:** Defined structured requirements and evidence records, implemented a Python evaluator, converted failed checks into draft POA&M entries, and built tests for normal, negative, and malformed cases.

**Demonstrable result:** One local command turns five synthetic control evidence records into repeatable assessments and traceable remediation candidates; a CI workflow prevents broken code from being merged. This is a **lab result**, not a claim of time savings in production.

## Next expansions
- Azure Policy and OPA/Rego policy-as-code checks
- OSCAL-compatible control and assessment exports
- STIG CKL/JSON parsing, vulnerability prioritization, and evidence freshness dashboards
- Human approval workflow for risk acceptance and closure verification

## Resume-ready wording (after running and understanding it)
> Built a Python-based RMF/GRC assessment prototype that maps synthetic NIST SP 800-53 control expectations to technical evidence, detects exceptions, generates draft POA&M records, and validates logic through automated CI tests.

**License:** MIT. See [LICENSE](LICENSE).
