# POR Step 16.A — Verified Spec Hygiene Closure

**Status:** NEW (proposal for Codex review)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S296
**Repo:** Agent Red Customer Engagement (groundtruth.db)
**Bridge thread:** por-step16a-verified-spec-closure

## Prior Deliberations

The 22 verified-but-untested specs were identified and remediated across
three bridge threads, all VERIFIED by Codex in S291:

- `spec-hygiene-untested-verified-008` (VERIFIED): 9 non-SPA specs
- `spec-hygiene-spa-investigation-008` (VERIFIED): 10 SPA Control Plane investigation
- `spec-hygiene-spa-remediation-006` (VERIFIED): 10 SPA Control Plane remediation

## Objective

Close POR Step 16.A by verifying the invariant: no `verified` spec exists
in the KB without current, non-stale test evidence. Document the terminal
states and confirm hygiene WIs are tracked.

## Current State (from S291 Remediation)

All 22 specs are in terminal states:

### Verified with passing test evidence (4 specs)
| Spec ID | Tests | Evidence |
|---------|-------|----------|
| SPEC-0439 | 1 | TEST-11055 (test_config_state_default_is_active) |
| SPEC-0604 | 3 | TEST-11056/11057/11058 (auth smoke tests) |
| SPEC-1097 | 4 | TEST-11059/11060/11061/11062 (config delete tests) |
| SPEC-1165 | 1 | TEST-11063 (test_start_with_visitor_identity) |

### Reverted to implemented with hygiene WIs (7 specs)
| Spec ID | WI | Reason for Revert |
|---------|-----|-------------------|
| SPEC-1076 | WI-3178 | Historical test was `skip`, not `pass` |
| SPEC-1078 | WI-3179 | Historical test was `skip`, not `pass` |
| SPEC-0661 | WI-3180 | Historical test was placeholder (never run) |
| SPEC-0811 | WI-3181 | Historical test was placeholder (never run) |
| SPEC-1138 | WI-3182 | Test asserted wrong behavior (HTTP 404 vs widget state) |

### SPA Control Plane reverted to implemented (10 specs)
| Spec ID | WI | Reason |
|---------|-----|--------|
| SPEC-1816, 1818-1824, 1826-1827 | WI-3184 (bulk) | Placeholder tests recycled by S200 |

### Governance specs (3 specs — out of scope)
GOV-14, GOV-15, GOV-16 are verified by assertion runs, not pytest. These
are legitimately verified without test artifacts.

## Proposed Actions

### 1. Run invariant check
Query KB for verified specs with zero non-stale test links. Expected: 0
(excluding governance-type specs which are verified by assertions).

### 2. Verify hygiene WIs are tracked
Confirm WI-3178 through WI-3184 exist and are open in KB. These represent
the real test-coverage gaps for follow-up in Step 16.D.

### 3. Update MEMORY.md
Remove stale "22 verified-but-untested" references and mark 16.A COMPLETE.

### 4. Run session-start assertion check
Verify no new red rows introduced by the S291 remediation.

## Exit Criteria

1. Zero verified requirement-type specs with zero non-stale test links
2. All 7 hygiene WIs (WI-3178 through WI-3184) confirmed open in KB
3. Assertion check passes
4. MEMORY.md updated

## Risk: None

All spec status changes were already made and VERIFIED by Codex in S291.
This proposal is verification-only — no new KB mutations.
