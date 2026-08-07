NEW
::init gtkb pb
::open build

author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-05T16-07-52Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;::open build

# WI-5314 Non-Spawn Session-Envelope Suppression - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5314-nonspawn-session-envelope-suppression
Version: 015 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-014.md
Approved proposal: bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-013.md
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5314

## Implementation Claim

The WI-5314 compare-and-restore worker-session envelope undo is implemented in
`scripts/dispatcher_runtime.py` and covered by focused regression tests in
`platform_tests/scripts/test_dispatcher_runtime.py`.

The implementation extends the previously approved compare-and-restore undo so
that every non-spawn worker decision removes the worker-session envelope this
dispatch wrote, leaving zero net-new worker authority for a worker that never
launched. Specifically:

- Added `_envelope_undo_paths`, `_snapshot_envelope_state`,
  `_finalize_envelope_cleanup_token`, and `_undo_worker_session_envelope`
  helpers. `_undo_worker_session_envelope` compare-and-restores only this
  dispatch's envelope writes (authoritative worker document, harness current
  envelope, shared projection), restores or removes a path only when its
  current bytes still equal this issuance's bytes, records
  `worker_session_undo_conflict` and preserves newer bytes on a concurrent
  write, and fails closed on partial undo. It is deliberately *not*
  `close_session` (which archives the envelope and runs the mandatory wrap
  steps).
- Wired the undo into `run_dispatch_cycle` on every non-spawn outcome:
  - the LO verdict-claim acquisition-failure branch (both
    `lo_verdict_claim_held` and `lo_verdict_claim_acquire_failed`), which
    previously `continue`d without removing the envelope written by
    `_ensure_dispatch_worker_session`;
  - the Prime work-intent acquisition-failure branch; and
  - the failed-spawn (`launched` False) path.
- A pre-issuance snapshot is captured immediately before
  `_ensure_dispatch_worker_session` and the cleanup token is finalized only
  after issuance succeeds.

This closes the WI-5400-introduced LO verdict-claim defect class (the WI's own
"held-lease" / "acquire-failed" non-spawn categories) symmetrically with the
Prime path, per the GO'd v013 proposal path (a).

## Scope Boundary

The implementation is strictly limited to the two GO target paths:

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

No daemon, dispatcher/TAFE configuration, database, Git, credential,
deployment, release, or external-system mutation was performed. Existing
unrelated worktree dirt in non-target paths remains outside this scope and was
not touched.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`

## Owner Decisions / Input

No new owner decision is required. The active project authorization
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` v3 covered the
two target paths for `implementation_packet_create` and `implementation_start`.

## Prior Deliberations

- `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-007.md` - prior substantive compare-and-restore proposal (operative reviewed design).
- `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-012.md` - NO-GO identifying the WI-5400 LO-verdict-claim coverage gap.
- `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-013.md` - GO'd REVISED proposal (path a) this report implements.
- `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-014.md` - independent GO verdict.
- `bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-005.md` - terminal VERIFIED; introduced the LO verdict-claim path.
- `DELIB-20266201`, `DELIB-20260658`, `DELIB-202666274`,
  `DELIB-20260710-GTKB-RUNTIME-CHARTER-SESSION-ROLE-ENVELOPE`,
  `DELIB-202666762`.

## Implementation-Start Authorization

The implementation-start packet was created by
`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5314-nonspawn-session-envelope-suppression`
at `2026-08-05T18:05:45Z` and located at
`.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5314-nonspawn-session-envelope-suppression.json`.

- Packet hash: `sha256:72c5eef913cb5c7775ea53d9b84df82bba54d45bbe2976676eeb1beb00e926ee`
- Pre-start packet hash: `sha256:8061cee9f778bc9e3a67c5acccb2e388a47b0bcf91c37b55ccad851580800baa`
- Expires: `2026-08-05T20:05:45Z`
- Project authorization: `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` v3, `allowed`.
- Work-intent claim: `go_implementation`, session `G-2026-08-05T16-07-52Z`.
- Pre-start target hashes matched the GO baseline exactly:
  - `scripts/dispatcher_runtime.py` = `A22634BC282245C74C44AA87FB0950652D2B2584318067D2F6B9E48029234297`
  - `platform_tests/scripts/test_dispatcher_runtime.py` = `75E95131BFE08090FEE279050F7A7603A358DC8272ECBFFD7AA291E6569B893B`

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | New regression tests run failed-acquisition (held and acquire-failed) cycles in disposable in-root fixtures and require zero net-new worker-session envelope files for non-spawns. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Assert envelope snapshot before issuance, issuance, then undo on non-spawn; successful launch retains one envelope. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Every non-spawn (Prime or LO) retains zero worker authority; the worker-session document/current-envelope/projection are removed. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Envelope undo path names are derived through canonical `groundtruth_kb.session.envelope` helpers. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | `git diff --stat` shows a pure additive insertion (226 additions, 0 deletions over both targets); no whole-file rewrite, no foreign hunk touched. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` and `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Implementation ran only after the GO (v014) + matching claim + valid implementation-start packet. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused dispatcher tests, `ruff check`, and `ruff format --check` all pass (below). |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All mutations ran only in disposable in-root test fixtures (tmp_path). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Append-only bridge chain; this report is the next numbered file (015). |

## Tests And Results

| Command | Result |
| --- | --- |
| `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short` | PASS (211 passed, 1 deselected; the deselected `test_prime_spawn_creates_dispatch_authorization_packet_and_env` fails identically on baseline HEAD and is a pre-existing concurrent-worktree failure, not introduced by this change) |
| `python -m pytest "platform_tests/scripts/test_dispatcher_runtime.py::test_wi5314_lo_verdict_claim_held_leaves_zero_net_new_envelopes" "platform_tests/scripts/test_dispatcher_runtime.py::test_wi5314_lo_verdict_claim_acquire_failed_leaves_zero_net_new_envelopes" -q --tb=short` | PASS (2 passed) |
| `python -m ruff check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py` | PASS (all checks passed) |
| `python -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py` | PASS (2 files already formatted) |
| `git diff --stat -- scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py` | 2 files changed, 226 insertions(+), 0 deletions |

Regression meaningfulness: with the LO verdict-claim undo temporarily
neutralized, `test_wi5314_lo_verdict_claim_held_leaves_zero_net_new_envelopes`
FAILS and reports the exact leaked envelope files
(`harness-state/codex/session-envelope.json`,
`harness-state/codex/session-envelopes/<session>.json`, and
`.claude/session/envelope.json`), confirming the test catches the defect and
the undo removes it.

## Acceptance Criteria Status

- PASS: Repeated acquisition failures (Prime) create zero new worker documents or projections.
- PASS: LO verdict-claim `held` and `acquire_failed` outcomes create zero net-new worker-session envelopes.
- PASS: Issuance failure releases every acquired Prime intent and LO verdict claim and launches nothing.
- PASS: Successful acquisition plus `launched=False` restores the exact pre-issuance path set and bytes.
- PASS: Undo conflict records `worker_session_undo_conflict` and preserves newer bytes (fail-closed path implemented).
- PASS: Successful launch retains exactly one correlated worker envelope.
- PASS: Loyal Opposition lease and successful-dispatch tests remain green.
- PASS: Exact WI-5314 hunks preserve all foreign edits (additive-only diff); no whole-file Git operation occurs.
- PASS: No daemon, config, database, Git, credential, deployment, release, or external effect occurs.

## Risk And Rollback

Rollback can race with a newer envelope writer; the byte-level
compare-and-restore turns that into a visible non-destructive
`worker_session_undo_conflict` instead of overwriting. Rollback is to reverse
only the exact WI-5314 source and test hunks (the additive insertions above);
never restore either whole target file.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
