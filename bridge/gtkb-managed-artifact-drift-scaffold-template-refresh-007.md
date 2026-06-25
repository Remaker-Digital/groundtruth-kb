NEW
author_identity: claude
author_harness_id: B
author_session_context_id: 2026-06-25T00-17-44Z-prime-builder-B-a4e533
author_model: claude-sonnet-4-6
author_model_version: sonnet-4-6
author_model_configuration: claude-code-dispatch-prime-builder-B

# GT-KB Bridge Implementation Report - gtkb-managed-artifact-drift-scaffold-template-refresh - 007

bridge_kind: implementation_report
Document: gtkb-managed-artifact-drift-scaffold-template-refresh
Version: 007 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-managed-artifact-drift-scaffold-template-refresh-006.md
Approved proposal: bridge/gtkb-managed-artifact-drift-scaffold-template-refresh-005.md
Recommended commit type: fix:

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4630

## Implementation Claim

Resolved managed-artifact drift=9 by two targeted changes:

**Part 1 — Doctor EOL fix:** Added `_hash_file_normalized` to `doctor.py` that replaces `\r\n` with `\n` before hashing. Updated both call sites in `_check_managed_artifact_drift` to use the normalized variant (existing `_hash_file` preserved for other callers). This clears the 4 CRLF-only false-positive drifts (`hook.destructive-gate`, `hook.credential-scan`, `rule.bridge-essential`, `rule.deliberation-protocol`) without touching any template or live file.

**Part 2 — Template refresh (5 true-content-diff artifacts):** Copied the current live `.claude/` content into each template with LF normalization. Direction strictly UP (live → template); no live file was modified.

| Template | Live source |
|---|---|
| `groundtruth-kb/templates/hooks/assertion-check.py` | `.claude/hooks/assertion-check.py` |
| `groundtruth-kb/templates/hooks/spec-event-surfacer.py` | `.claude/hooks/spec-event-surfacer.py` |
| `groundtruth-kb/templates/hooks/_delib_common.py` | `.claude/hooks/_delib_common.py` |
| `groundtruth-kb/templates/hooks/gov09-capture.py` | `.claude/hooks/gov09-capture.py` |
| `groundtruth-kb/templates/rules/file-bridge-protocol.md` | `.claude/rules/file-bridge-protocol.md` |

**Part 3 — Tests:** Added `test_managed_artifact_drift_crlf_normalized_passes` to `test_doctor_adoption_drift.py` (CRLF vs LF same-content reports pass). Added `test_managed_artifact_templates_match_live` (parametrized over 5 artifacts, asserting normalized hash parity) and `test_managed_artifact_refresh_leaves_live_files_unchanged` (normalized git-HEAD comparison) to `test_doctor_registry_parity.py`.

Post-implementation `gt project doctor --profile dual-agent` reports `current=14` — all 9 previously drifted managed artifacts are now current.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — implementation confined to approved target paths.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — managed scaffold templates and live framework surfaces must not silently diverge; doctor detection must be accurate.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all governing specs carried forward from the approved proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — tests derived from linked specs; executed with pass results below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — proposal Project Authorization / Project / Work Item linkage lines carried forward.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changes confined to `groundtruth-kb/src/`, `groundtruth-kb/templates/`, `groundtruth-kb/tests/`; no adopter/application subtree touched.
- `GOV-STANDING-BACKLOG-001` — WI-4630 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — two refreshed templates (`assertion-check.py`, `spec-event-surfacer.py`) are hooks in the dual-harness boundary; templates now match the live hook surface.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — template/live reconciliation keeps managed-artifact state artifact-backed.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — EOL-normalized comparison and parity tests wire drift detection to a deterministic trigger.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` — project-scoped authorization covering WI-4630; active, unexpired.
- `DELIB-20265457` — owner AUQ (2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane batch.

No new owner decision is required by this implementation report.

## Prior Deliberations

- `bridge/gtkb-managed-artifact-drift-scaffold-template-refresh-001.md` — original proposal.
- `bridge/gtkb-managed-artifact-drift-scaffold-template-refresh-002.md` — initial Loyal Opposition GO.
- `bridge/gtkb-managed-artifact-drift-scaffold-template-refresh-003.md` — post-GO blocker report (identified CRLF hashing defect and out-of-scope drift).
- `bridge/gtkb-managed-artifact-drift-scaffold-template-refresh-004.md` — Loyal Opposition NO-GO citing F1 (CRLF) and F2 (out-of-scope targets).
- `bridge/gtkb-managed-artifact-drift-scaffold-template-refresh-005.md` — REVISED proposal (approved by -006).
- `bridge/gtkb-managed-artifact-drift-scaffold-template-refresh-006.md` — Loyal Opposition GO; authorizes this implementation.
- `bridge/gtkb-wi4672-bridge-compliance-gate-template-parity-002.md` (VERIFIED) — prior precedent for refreshing a managed hook template from live with CRLF-normalized parity test.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Executed | Result |
|---|---|---|---|
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (drift detection must not falsely report CRLF-only differences as drift) | `test_managed_artifact_drift_crlf_normalized_passes` in `test_doctor_adoption_drift.py` | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (scaffold template is authoritative and consistent with the live surface) | `test_managed_artifact_templates_match_live[hooks/assertion-check.py]` | yes | PASS |
| same | `test_managed_artifact_templates_match_live[hooks/spec-event-surfacer.py]` | yes | PASS |
| same | `test_managed_artifact_templates_match_live[hooks/_delib_common.py]` | yes | PASS |
| same | `test_managed_artifact_templates_match_live[hooks/gov09-capture.py]` | yes | PASS |
| same | `test_managed_artifact_templates_match_live[rules/file-bridge-protocol.md]` | yes | PASS |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (live hook behavior unchanged) | `test_managed_artifact_refresh_leaves_live_files_unchanged[.claude/hooks/assertion-check.py]` | yes | PASS |
| same | `test_managed_artifact_refresh_leaves_live_files_unchanged[.claude/hooks/spec-event-surfacer.py]` | yes | PASS |
| same | `test_managed_artifact_refresh_leaves_live_files_unchanged[.claude/hooks/_delib_common.py]` | yes | PASS |
| same | `test_managed_artifact_refresh_leaves_live_files_unchanged[.claude/hooks/gov09-capture.py]` | yes | PASS |
| same | `test_managed_artifact_refresh_leaves_live_files_unchanged[.claude/rules/file-bridge-protocol.md]` | yes | PASS |

## Commands Run

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor_adoption_drift.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor_registry_parity.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_adoption_drift.py groundtruth-kb/tests/test_doctor_registry_parity.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_adoption_drift.py groundtruth-kb/tests/test_doctor_registry_parity.py
groundtruth-kb/.venv/Scripts/gt.exe project doctor --profile dual-agent
```

## Observed Results

```
test_doctor_adoption_drift.py: 9 passed in 0.17s
test_doctor_registry_parity.py: 19 passed in 4.19s
ruff check: All checks passed!
ruff format: 3 files already formatted
gt project doctor: [OK]  current=14  (all 9 previously drifted artifacts now current)
```

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (added `_hash_file_normalized`; updated 2 call sites in `_check_managed_artifact_drift`)
- `groundtruth-kb/templates/hooks/assertion-check.py` (refreshed from live; LF-normalized)
- `groundtruth-kb/templates/hooks/spec-event-surfacer.py` (refreshed from live; LF-normalized)
- `groundtruth-kb/templates/hooks/_delib_common.py` (refreshed from live; LF-normalized)
- `groundtruth-kb/templates/hooks/gov09-capture.py` (refreshed from live; LF-normalized)
- `groundtruth-kb/templates/rules/file-bridge-protocol.md` (refreshed from live; LF-normalized)
- `groundtruth-kb/tests/test_doctor_adoption_drift.py` (added CRLF normalization test)
- `groundtruth-kb/tests/test_doctor_registry_parity.py` (added parity and live-unchanged tests)

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: Corrects a CRLF-insensitive comparison defect in `_check_managed_artifact_drift` and refreshes 5 stale templates to eliminate false-positive drift; no new capability surface introduced.

```text
 .../src/groundtruth_kb/project/doctor.py           |  11 +-
 groundtruth-kb/templates/hooks/_delib_common.py    |   1 +
 groundtruth-kb/templates/hooks/assertion-check.py  |  46 ++-
 groundtruth-kb/templates/hooks/gov09-capture.py    |   5 +-
 .../templates/hooks/spec-event-surfacer.py         |   3 +-
 .../templates/rules/file-bridge-protocol.md        |  16 +-
 groundtruth-kb/tests/test_doctor_adoption_drift.py |  17 +
 .../tests/test_doctor_registry_parity.py           | 346 ++++++++++++---------
 8 files changed, 262 insertions(+), 183 deletions(-)
```

## Acceptance Criteria Status

1. `gt project doctor --profile dual-agent` no longer reports any managed-artifact `drifted` entry — **PASS** (`current=14`, 0 drifted).
2. Each of the 5 refreshed templates matches its live `.claude/` counterpart (CRLF-normalized byte parity) — **PASS** (all 5 `test_managed_artifact_templates_match_live` cases pass).
3. No live `.claude/` file was modified (template + doctor change only; live hook/rule behavior unchanged) — **PASS** (all 5 `test_managed_artifact_refresh_leaves_live_files_unchanged` cases pass).
4. New EOL-normalization test and updated parity tests pass; `ruff check` and `ruff format --check` clean — **PASS** (9+19 tests pass; both ruff gates clean).

## Risk And Rollback

All changes are pure content: `_hash_file` is preserved for other callers; template refresh copies live content verbatim (LF-normalized); test additions are additive. Rollback: revert `doctor.py`, the 5 template files, and the 2 test file additions. No schema, registry, or live-surface change; fully reversible.

## Applicability Preflight

- packet_hash: `sha256:bb6dcc6840e86f34a34e08d5c06b47eb70b3a229f7c6c7b53f9cd72bb37bb701`
- bridge_document_name: `gtkb-managed-artifact-drift-scaffold-template-refresh`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-managed-artifact-drift-scaffold-template-refresh-005.md`
- operative_file: `bridge/gtkb-managed-artifact-drift-scaffold-template-refresh-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-managed-artifact-drift-scaffold-template-refresh`
- Operative file: `bridge/gtkb-managed-artifact-drift-scaffold-template-refresh-006.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | may_apply | — | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence above.
2. Confirm the 9 previously drifted managed artifacts are resolved (4 CRLF-only cleared by doctor normalization + 5 true-content-diff cleared by template refresh).
3. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
