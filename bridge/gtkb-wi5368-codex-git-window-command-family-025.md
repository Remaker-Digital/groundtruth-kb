REVISED
::init gtkb pb
::open build

# WI-5368 Implementation Report Revision (REVISED) - Live Hash Refresh (re-queue for VERIFIED)

::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-05T16-07-52Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb

bridge_kind: implementation_report
Document: gtkb-wi5368-codex-git-window-command-family
Version: 025
Date: 2026-08-05 UTC
Responds to: bridge/gtkb-wi5368-codex-git-window-command-family-024.md (NO-GO)
Approved proposal: bridge/gtkb-wi5368-codex-git-window-command-family-015.md
Controlling GO: bridge/gtkb-wi5368-codex-git-window-command-family-016.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5368
target_paths: ["scripts/ops/codex_snapshot_window_hider.py", "platform_tests/scripts/test_codex_snapshot_window_hider.py"]
implementation_scope: evidence_only_live_hash_refresh
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

KB Mutation: This report performs no MemBase or `groundtruth.db` write or mutation.

## Revision Claim

This REVISED report responds to the version 024 NO-GO, which recorded two
findings: (P1) exact-reobservation / postimage evidence is not current after
custodial sweeps, and/or atomic VERIFIED is timer-blocked; (P3) the focused
suite is green. The recommended action was "Refresh live SHA-256 if drifted;
retry VERIFIED when timer healthy."

This revision refreshes the live SHA-256 for the test target, which drifted
under the custodial sweep commit `02e12e7b0` (`chore(gtkb): custodial
sweep-commit of 812 orphaned paths (owner sweep exemption)`). No source or
test byte changed in this recovery; both targets remain clean at HEAD. The
focused suite was re-executed live this filing and passes 42/42.

## Live Re-Executed Evidence

| Check | Result |
| --- | --- |
| `python -m pytest platform_tests/scripts/test_codex_snapshot_window_hider.py -q --tb=short` | **42 passed in 0.43s** (re-executed 2026-08-05 this filing) |
| Target cleanliness | both approved targets clean at HEAD (exact frozen postimages) |

## Findings Addressed

### Finding 1 (P1) - Exact-reobservation / postimage evidence not current after custodial sweeps, and/or atomic VERIFIED timer-blocked

Response: Accepted. The test target SHA-256 drifted under the custodial sweep
commit `02e12e7b0` from the v023-declared value. This revision carries the
corrected live SHA-256 for the test target and confirms both targets are clean
at HEAD. No code rework was indicated and none was performed. This revision
re-requests focused independent VERIFIED with live packet and test evidence.

### Finding 2 (P3) - Focused suite previously green (42 passed)

Response: Confirmed. The focused suite was re-executed live this filing and
passes 42/42 in 0.43s.

## Implementation Start Evidence (carried forward)

- Claim row `36027`, session `019fb1f2-2f91-7b82-ac15-acdd56e13d1e`.
- Finalized schema-v3 packet: `sha256:4767911f0d34ad699680a49d0f483b2de65332c11be2c07fbe0432af99335ec3`.
- Resumption authority binds v015/v016/v017/v018 as `resumable_report_no_go`.
- Operation-time PAUTH v3 allowed the exact source/test target classes.

## Exact Current Cohort (live SHA-256, refreshed)

| Target | Current SHA-256 | Status |
| --- | --- | --- |
| `scripts/ops/codex_snapshot_window_hider.py` | `88BFFC35E4AB9A9A18B243CC35993C086276C3ADD8CCB22326B87FFEA0A18BC1` | clean at HEAD; exact frozen postimage |
| `platform_tests/scripts/test_codex_snapshot_window_hider.py` | `018200F49DBD9ADFA9D854EE1E23CC02E4CD5208A6F7E09C1B4D5248B1DB99FE` | clean at HEAD; refreshed live hash |

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202667709` - controlling whole-project Harness Parity PAUTH v3.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD`
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS`
- `DELIB-202666274`

## Specification-Derived Verification

| Requirement | Fresh evidence | Result |
| --- | --- | --- |
| Strict marker-qualified Git command-family recognition and near-miss rejection | `python -m pytest platform_tests/scripts/test_codex_snapshot_window_hider.py -q --tb=short` | PASS - 42 passed in 0.43s (re-executed this filing) |
| Code quality | Ruff check and format-check | PASS (v019 evidence) |
| Exact target isolation | Current SHA-256, scoped Git status | Both targets clean at HEAD and exact |
| Current project/start authority | Claim row 36027, finalized packet, validations | PASS |

## Owner Decisions / Input

No new owner decision is required. This revision remains within the active,
list-free Harness Parity PAUTH v3 and responds only to the hash-drift NO-GO.

## Scope Changes

None. The exact approved two-file scope is unchanged. This report performs no
MemBase or `groundtruth.db` write or mutation and no dispatcher/TAFE/credential/
deployment/release/external change.

---

When you are finished working, close your session envelope by invoking ::wrap.
