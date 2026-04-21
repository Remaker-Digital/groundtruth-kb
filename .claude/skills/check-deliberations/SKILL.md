---
name: check-deliberations
description: "Run deliberation archive health check. Reports 5 metrics (population, linkage, conflict quarantine, redaction, duplicates) with PASS/WARN/FAIL thresholds."
allowed-tools: Bash, Read
license: "Proprietary - Remaker Digital"
compatibility:
  - claude-code >= 1.0
metadata:
  project: agent-red-customer-experience
  category: governance
  spec: SPEC-2098
---

# Deliberation Archive Health Check

Run the 5-metric health check for the deliberation archive.

## Usage

```bash
python scripts/deliberation_health.py
```

For JSON output (useful for programmatic checks):
```bash
python scripts/deliberation_health.py --json
```

## Metrics

| # | Metric | PASS | WARN | FAIL |
|---|--------|------|------|------|
| 1 | Population coverage | >= 80% | >= 50% | < 50% |
| 2 | Linkage coverage | >= 40% | >= 20% | < 20% |
| 3 | Conflict quarantine | <= 5% | > 5% | - |
| 4 | Redaction survivors | 0 | - | > 0 |
| 5 | Duplicate suppression | 0 | - | > 0 |

## Interpretation

- **Population:** Ratio of archived deliberations to candidate source files. Should be near 100% after harvest.
- **Linkage:** Ratio of deliberations linked to SPEC/WI IDs. Many early reports lack IDs — WARN is expected.
- **Conflict quarantine:** High informational rate may indicate verdict parsing gaps.
- **Redaction:** Any AR key survivors in archived content = security concern.
- **Duplicates:** Should always be 0 due to idempotent upsert.

Run the script and report the results to the user. Flag any FAIL metrics for investigation.
