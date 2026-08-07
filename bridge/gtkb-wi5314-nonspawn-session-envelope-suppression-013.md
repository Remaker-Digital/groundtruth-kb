REVISED
::init gtkb pb
::open build

author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-05T16-07-52Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb

# Revised Proposal - Extend non-spawn worker-session envelope undo to the LO verdict-claim path

bridge_kind: prime_proposal
Document: gtkb-wi5314-nonspawn-session-envelope-suppression
Version: 013
Responds to: bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-012.md (NO-GO)
Date: 2026-08-05 UTC
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5314
target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]
implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: fix

## First-Line Role Eligibility Check

PASS. This is a Prime Builder session (declared `::init gtkb pb`). This session
acquired the required draft work-intent claim for
`gtkb-wi5314-nonspawn-session-envelope-suppression` at `2026-08-05T16:59:45Z`
(row 36757). Latest live thread status was verified as `NO-GO` at
`bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-012.md` before this
filing. Prime Builder may author a `REVISED` bridge file.

This filing grants no implementation authority. Protected implementation still
requires a fresh independent `GO`, a matching implementation claim, and a
successful implementation-start packet.

## Revision Disposition

The `-012` NO-GO (2026-07-18) records a P0 design-coverage finding: a new
LO-verdict-claim acquisition-failure path (introduced by WI-5400 commit
`948b550e`, terminal VERIFIED) exhibits the same non-spawn worker-session
envelope leak WI-5314 exists to eliminate, and the reviewed version-007 design
never accounted for it because that path did not exist at review time. The
NO-GO offers two acceptable paths:

- (a) *Preferred:* Prime Builder files a fresh REVISED proposal that re-reads
  current `scripts/dispatcher_runtime.py` and
  `platform_tests/scripts/test_dispatcher_runtime.py` bytes, extends the
  compare-and-restore undo to the `lo_claim_result["ok"] is False` branch
  symmetrically with the Prime branch, and adds a focused regression proving an
  LO verdict-claim acquisition failure (both `lo_verdict_claim_held` and
  `lo_verdict_claim_acquire_failed`) leaves zero net-new worker-session
  envelopes.
- (b) *Acceptable with transparency:* explicitly narrow to Prime-only and
  record the LO gap as a new/sibling work item.

This revision selects **path (a)**. It re-reads current bytes, extends the
compare-and-restore undo to cover both the Prime non-spawn paths and the new
LO-verdict-claim-failure path, and adds focused regressions for both LO failure
outcomes. This is the preferred, self-contained correction and does not require
a new work item or owner visibility deferral.

## Current-State Facts (re-read 2026-08-05, not carried from the review)

- Target hashes (live SHA-256):
  - `scripts/dispatcher_runtime.py` =
    `A22634BC282245C74C44AA87FB0950652D2B2584318067D2F6B9E48029234297`
  - `platform_tests/scripts/test_dispatcher_runtime.py` =
    `75E95131BFE08090FEE279050F7A7603A358DC8272ECBFFD7AA291E6569B893B`
- Both targets clean at HEAD (`git status --short` over both paths: no output).
- Current line references (offset by the WI-5400 `+250` insertion vs the
  version-010-reviewed baseline, as the NO-GO's Secondary Note P3 predicted):
  - `def _acquire_lo_verdict_work_intent_batch(` at line **2222**
  - `def _ensure_dispatch_worker_session(` at line **2339**
  - `def _acquire_prime_work_intent_batch(` at line **2411**
  - `def _spawn_harness(` at line **5148**
  - `worker_session_result = _ensure_dispatch_worker_session(` at line **7547**
  - `if not lo_claim_result["ok"]:` at line **7576**
  - `acquired_lo_verdict_claim_slugs = list(...)` at line **7603**
  - `acquire_result = _acquire_prime_work_intent_batch(` at line **7605**
  - `if not acquire_result["ok"]:` at line **7615**
- The version-007 compare-and-restore undo design remains unimplemented in
  current bytes; this revision carries it forward and extends its coverage.

## Finding Responses

### F1 (P0, blocking) - WI-5400 reintroduced WI-5314's exact defect class on a new, unreviewed code path

Response: Accepted. Current `run_dispatch_cycle` writes the worker-session
envelope at line 7547 (`worker_session_result = _ensure_dispatch_worker_session(...)`
for both Prime and LO targets), then on the LO-verdict-claim path, when
`lo_claim_result["ok"] is False` at line 7576, the handler releases document
leases, records the failed attempt, and `continue`s **without removing or
restoring the worker-session envelope** written two lines of logic earlier.
This is precisely the non-spawn "held-lease" / "acquire-failed" envelope leak
WI-5314's own MemBase description names.

This revision extends the version-007 compare-and-restore undo so it covers
this branch symmetrically with the Prime branch. Specifically, after a
successful `_ensure_dispatch_worker_session` write, the dispatcher retains an
in-memory cleanup token describing exactly this dispatch's envelope writes. On
every non-spawn outcome - Prime work-intent acquisition failure (line 7615),
LO verdict-claim acquisition failure (line 7576), and spawn failure (`launched`
False) - the dispatcher releases acquired intents and compare-and-restores or
removes only the envelope state written by this dispatch. This leaves zero
net-new worker-session envelopes for `lo_verdict_claim_held` and
`lo_verdict_claim_acquire_failed` outcomes.

### F2 / P3 (non-blocking) - stale line references throughout the reviewed proposal

Response: Accepted. This revision re-reads current bytes and records the
current line references (above) rather than reusing the version-007 "approx"
references that are now offset by the WI-5400 `+250`-line insertion.

## Proposed Implementation

Carry forward and extend the version-007 compare-and-restore design:

1. Allocate dispatch/session identifiers.
2. Acquire the complete work-intent batch (Prime) or verdict-claim batch (LO)
   as applicable.
3. Snapshot the exact pre-issuance envelope path state.
4. Issue authority and retain an in-memory cleanup token describing only this
   dispatch's writes.
5. Attempt spawn.
6. If spawn returns `launched=True`, retain exactly one correlated worker
   envelope.
7. If spawn returns `launched=False`, OR work-intent/verdict-claim acquisition
   fails (Prime line 7615 or LO line 7576), release acquired intents/claims and
   compare-and-restore or remove only the envelope state written by this
   dispatch.

Undo is not `close_session`. The cleanup token records prior and issued bytes
for the authoritative worker document, harness current envelope, and shared
projection written by `ensure_worker_session`. Each path is derived through
canonical envelope helpers. Undo restores or removes a path only if its current
bytes still equal this issuance's bytes. A mismatch records
`worker_session_undo_conflict`, preserves newer bytes, and fails closed instead
of overwriting a concurrent writer. Partial undo is a hard failure.

## Requirement Sufficiency

Existing requirements remain sufficient. This revision does not change the
session-envelope, dispatcher, role-authority, or work-intent requirements. It
only refreshes the target baselines and extends the previously approved
compare-and-restore design to cover the WI-5400-introduced LO verdict-claim
acquisition-failure path.

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

## Prior Deliberations And Bridge Evidence

- `DELIB-20266201` - bounded daemon process-lifecycle hardening authorization.
- `DELIB-20260658` - worker-envelope containment model.
- `DELIB-202666274` - modernization required-work authorization with bridge and mechanical gates retained.
- `DELIB-20260710-GTKB-RUNTIME-CHARTER-SESSION-ROLE-ENVELOPE` - worker authority must bind a real worker context.
- `DELIB-202666762` - WI-5400 owner decision (work-intent claim release on incomplete exit); the worker-session envelope artifact WI-5314 owns was never in scope there.
- `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-007.md` - prior substantive REVISED compare-and-restore proposal (operative reviewed design).
- `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-012.md` - current NO-GO this revision responds to.
- `bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-005.md` - terminal VERIFIED; introduced the LO verdict-claim path.

## Owner Decisions / Input

No new owner decision is required. The active project authorization and prior
owner decisions cover this bounded source/test correction, and this revision
requests no dispatcher restart, runtime configuration change, database mutation,
Git operation, credential action, deployment, release, external-system effect,
or destructive cleanup.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5314 revision 013; extends compare-and-restore undo to the WI-5400-introduced LO verdict-claim path",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, SPEC-CENTRALIZED-DISPATCH-SERVICE-001, GOV-SESSION-ROLE-AUTHORITY-001, DCL-SESSION-ROLE-RESOLUTION-001",
  "primary_route": "dispatcher_runtime Prime and LO work-intent/verdict-claim acquisition plus worker-session spawn path",
  "before_behavior": "Failed acquisition (Prime or LO verdict-claim) or failed spawn can leave dispatcher-composed worker authority for a worker that never launched.",
  "after_behavior": "Failed acquisition writes no envelope; failed spawn restores this dispatch's exact pre-issuance envelope state; successful launch retains one correlated envelope; LO verdict-claim held/acquire-failed leaves zero net-new envelopes.",
  "self_descriptive_naming": "Cleanup-token and worker-session-undo-conflict names expose the non-spawn rollback boundary symmetrically across Prime and LO.",
  "obsolete_guidance_disposition": "The WI-5400-introduced LO verdict-claim leak is closed within this scope; no public guidance changes.",
  "history_preservation": "No phantom worker envelope is archived and no unrelated or concurrent envelope bytes are overwritten.",
  "baseline": {
    "target_hashes": {
      "scripts/dispatcher_runtime.py": "sha256:A22634BC282245C74C44AA87FB0950652D2B2584318067D2F6B9E48029234297",
      "platform_tests/scripts/test_dispatcher_runtime.py": "sha256:75E95131BFE08090FEE279050F7A7603A358DC8272ECBFFD7AA291E6569B893B"
    },
    "predecessor": "WI-5400 VERIFIED (terminal); WI-5255 VERIFIED (terminal)",
    "target_diff": "git status --short over the two target paths produced no output"
  },
  "expected_result": {
    "failed_acquisition_net_new_envelopes": 0,
    "lo_verdict_claim_held_net_new_envelopes": 0,
    "lo_verdict_claim_acquire_failed_net_new_envelopes": 0,
    "failed_spawn_net_new_envelopes": 0,
    "successful_launch_envelopes": 1,
    "concurrent_overwrites": 0
  },
  "essential_context_preservation": "Dispatch id, worker session id, harness, role, provenance, selected work, intents, verdict claims, telemetry, document leases, and all foreign hunks remain available at their existing boundaries.",
  "hard_invariants": [
    "No worker authority remains for a decision that launches no worker (Prime or LO).",
    "Worker authority exists before a real subprocess consumes it.",
    "Successful launch retains exactly one correlated envelope.",
    "Acquired Prime intents and LO verdict claims are released when issuance or spawn fails.",
    "LO verdict-claim held and acquire-failed outcomes leave zero net-new envelopes.",
    "Undo never overwrites concurrent bytes.",
    "Loyal Opposition leases and foreign hunks remain unchanged."
  ],
  "fail_closed_conditions": [
    "pre-start target hash drift",
    "implementation-start packet missing or outside target paths",
    "undo path escapes project root",
    "issued bytes no longer match at undo time",
    "partial rollback",
    "non-spawn leaves net-new envelope state on Prime or LO path",
    "focused dispatcher regression"
  ],
  "rollback": "Reverse only the exact WI-5314 source and test hunks; never restore either whole target."
}
```

## Spec-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Snapshot target path hashes, run failed-acquisition, LO verdict-claim held/acquire-failed, and failed-spawn cycles in disposable in-root test fixtures, and require zero net envelope changes for all non-spawns. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Assert order: acquire work intents/verdict claims, issue authority, spawn, then retain or undo. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Successful launch retains one correlated worker envelope; every non-spawn (Prime or LO) retains none. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Assert exact harness, role, dispatch id, session id, and dispatcher composition provenance. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Prove exact new hunks preserve all foreign pre-start hunks and do not rewrite whole target files. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` and `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Require fresh independent GO, fresh claim, and successful implementation-start packet before mutation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused dispatcher tests, Ruff check/format, and scope/hash checks before implementation report. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run mutations only in disposable in-root test repositories. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use only append-only bridge proposal, GO, implementation report, and independent verification states. |

Expected commands after GO:

- `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short`
- `python -m ruff check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py`
- `python -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py`
- exact pre/post target hash and hunk-isolation checks.

## Acceptance Criteria

1. Repeated acquisition failures (Prime) create zero new worker documents or projections.
2. LO verdict-claim `held` and `acquire_failed` outcomes create zero net-new worker-session envelopes.
3. Issuance failure releases every acquired Prime intent and LO verdict claim and launches nothing.
4. Successful acquisition plus `launched=False` releases intents/claims and restores the exact pre-issuance path set and bytes.
5. Undo conflict records `worker_session_undo_conflict` and preserves newer bytes.
6. Successful launch retains exactly one correlated worker envelope.
7. Loyal Opposition lease and successful-dispatch tests remain green.
8. Exact WI-5314 hunks preserve all foreign edits; no whole-file Git operation occurs.
9. No daemon, config, database, Git, credential, deployment, release, or external effect occurs.

## Risk And Rollback

Rollback can race with a newer envelope writer. Byte-level compare-and-restore
turns that into a visible non-destructive conflict. Revert only the exact
independently reviewed WI-5314 source and test hunks.

## Pre-Filing Self-Check Evidence

The completed content was prepared after a Prime drafting claim for this
thread. The filing helper will rerun the mandatory applicability and ADR/DCL
clause preflights against this exact candidate before writing the live bridge
file, and filing must fail on any nonzero result, credential hit, chain
conflict, or metadata failure.

---

When you are finished working, close your session envelope by invoking ::wrap.
