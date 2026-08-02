REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher/TAFE deliberately disabled

# WI-5368 Implementation Report Revision — Fresh Current-Authority Rebind

bridge_kind: implementation_report
Document: gtkb-wi5368-codex-git-window-command-family
Version: 019
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5368-codex-git-window-command-family-018.md
Approved proposal: bridge/gtkb-wi5368-codex-git-window-command-family-015.md
Controlling GO: bridge/gtkb-wi5368-codex-git-window-command-family-016.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5368
target_paths: ["scripts/ops/codex_snapshot_window_hider.py", "platform_tests/scripts/test_codex_snapshot_window_hider.py"]
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## First-Line Role Eligibility Check

PASS. Harness A is active as Prime Builder in the canonical harness projection,
and the transcript-resolved session role is Prime Builder. `REVISED` is a Prime
Builder status. This session is distinct from the Loyal Opposition session that
authored v018 and does not author a review verdict.

## Revision Claim

V018 rejected v017 only because its implementation-start packet had expired.
That defect is corrected. Prime Builder re-observed the exact approved two-file
cohort, acquired a fresh claim, created and finalized a fresh schema-v3 packet,
validated both targets against it, and reran current verification. No source or
test byte changed in this recovery.

The implementation remains present by reference in custodial commit
`02e12e7b0e1a1172ea8acf1b9a99e2ee9b8e54af`. Both current files are clean and
their hashes exactly match the frozen v015 postimages and the independent v016
re-observation.

## Findings Addressed

### F1 — Expired implementation-start packet

RESOLVED.

- Claim row: `36027`, session
  `019fb1f2-2f91-7b82-ac15-acdd56e13d1e`, acquired
  `2026-08-01T11:28:21Z`, expires `2026-08-01T15:28:21Z`.
- Finalized schema-v3 packet:
  `sha256:4767911f0d34ad699680a49d0f483b2de65332c11be2c07fbe0432af99335ec3`.
- Pre-start packet:
  `sha256:2de90fb14bfc8dca6214eb32014552392772013e5247bc93b58312ba588c77ac`.
- Finalized `2026-08-01T11:30:57Z`; expires
  `2026-08-01T15:30:57Z`.
- Packet resumption authority binds v015, v016, v017, and remediated NO-GO
  v018 as `resumable_report_no_go`.
- Operation-time PAUTH v3 allowed the exact source/test target classes.
- Direct `validate` checks returned `authorized: true` for both targets.

## Exact Current Cohort

| Target | Current SHA-256 | Status |
| --- | --- | --- |
| `scripts/ops/codex_snapshot_window_hider.py` | `88BFFC35E4AB9A9A18B243CC35993C086276C3ADD8CCB22326B87FFEA0A18BC1` | clean; exact frozen postimage |
| `platform_tests/scripts/test_codex_snapshot_window_hider.py` | `BB93F56AA55689002C470080094C0213313F5F16359895F2E1D79800CAF7A20A` | clean; exact frozen postimage |

## Scope Changes

None. This is an evidence-only current-authority rebind. It adds no target,
behavior, mutation, requirement, or owner decision and does not reuse the
expired v017 packet as authority.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202667709` — controlling whole-project Harness Parity PAUTH v3.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — active members
  inherit controlling whole-project authority.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` — marker-qualified hide-only
  requirement.
- `DELIB-202666274` — independent bridge, start, verification, and
  non-impairment gates.

## Owner Decisions / Input

No new owner decision is required. This revision remains within the active,
list-free Harness Parity PAUTH v3 and only corrects the live-evidence defect
identified by v018.

## Specification-Derived Verification

| Requirement | Fresh evidence | Result |
| --- | --- | --- |
| Strict marker-qualified Git command-family recognition and near-miss rejection | `python -m pytest platform_tests/scripts/test_codex_snapshot_window_hider.py platform_tests/scripts/test_check_artifact_evaluability.py -q --tb=short --timeout=600` | Combined cohort 56/56 passed; WI-5368 contributes 42 passing tests. |
| Code quality | Ruff check and format-check on the four combined WI-5368/WI-5359 recovery targets | All checks passed; four files formatted. |
| Exact target isolation | Current SHA-256, scoped Git status, and commit-by-reference observation | Both targets clean and exact; no third target. |
| Current project/start authority | Claim row 36027, finalized schema-v3 packet, two target validations | PASS through `2026-08-01T15:30:57Z`. |
| Independent terminal integrity | This REVISED report requests a new LO verdict | PENDING; Prime Builder makes no VERIFIED claim. |

## Pre-Filing Preflight Subsection

The governed revision helper must run applicability and mandatory ADR/DCL
clause preflights against the final candidate bytes. Filing is prohibited if
either returns a missing specification, blocking error, evidence gap, or
blocking gap.

## Verification Plan

Loyal Opposition should independently re-read the live named packet and claim,
confirm the two exact clean hashes and commit-by-reference provenance, rerun the
42-test focused WI-5368 suite plus Ruff gates, and issue VERIFIED only while the
current packet/claim evidence remains acceptable. Terminal publication and
finalization receipt recovery remain separate fail-closed gates.

## Risk And Rollback

The residual risk is authority expiry or publication-receipt incompleteness
before independent finalization. Either condition must fail closed and be
recovered append-only; it does not justify source mutation, staging, reset,
dispatcher/TAFE action, push, deployment, credential action, or destructive
cleanup. No source rollback is required because this revision changes no
source/test byte.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
