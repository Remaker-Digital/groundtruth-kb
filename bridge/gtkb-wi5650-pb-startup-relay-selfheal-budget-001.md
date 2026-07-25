NEW
::init gtkb lo
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 21474841-699e-40ec-8057-757596fd5e2d
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; explanatory output style; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal
Document: gtkb-wi5650-pb-startup-relay-selfheal-budget
Version: 001
Author: Prime Builder (claude, harness B)
Date: 2026-07-22 UTC
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-SESSION-STARTUP-LATENCY-WI-5650-SLICE-A-STARTUP-RELAY-SELF-HEAL-OBSERVABILITY-AND-DIAGNOSTIC-ACCURACY
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-SESSION-STARTUP-LATENCY
Work Item: WI-5650
Related Work Items: WI-3447, WI-4827, WI-5084, WI-5565
Recommended commit type: fix:

target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py"]

# Make the PB Startup-Relay Self-Heal Failure Measurable and Honestly Diagnosed (WI-5650, Slice A)

## Problem Statement

The Prime Builder startup-disclosure relay reports `GTKB STARTUP RELAY FAILURE` on every
`::init gtkb pb` turn on harness B, and its stale-cache self-heal path can never succeed.

Measured evidence (2026-07-22, production code path, two consecutive runs):

| Element | Value | Source |
|---|---|---|
| Cache freshness TTL | 1800s | `STARTUP_RELAY_CACHE_MAX_AGE_SECONDS`, `scripts/workstream_focus.py:112` |
| Refresh budget | 5.0s | `STARTUP_RELAY_REFRESH_TIMEOUT_SECONDS`, `scripts/workstream_focus.py:118` |
| Actual render wall time | 38.97s | measured; returns a VALID 8908-char report |
| Bounded-refresh result | `False` at exactly 5.00s, twice | `_refresh_startup_relay_cache_bounded`, line 1654 |
| Resulting pointer | `fresh=False`, `consistent=False` | `_startup_relay_pointer`, line 1742 |

The render succeeds; only its budget fails. Abandonment is therefore deterministic, roughly
7.8x over budget, and not a race. Because refresh can never complete, the PB cache cannot
self-heal: the observed cache was generated 2026-07-18T20:31:35Z, about 354000s old against
an 1800s TTL, so every PB session since 2026-07-18 hit the same wall. The LO cache is current
only because SessionStart writes it directly, bypassing this timeout-bounded path.

Two consequences motivate this slice:

1. **The failure is silent.** Three fail-soft layers each swallow the signal:
   `_render_role_startup_report` catches `Exception` and returns `None`
   (`scripts/session_start_dispatch_core.py:810`); `_refresh_startup_relay_cache_bounded`
   catches `Exception` and returns `False` (line 1645) and also returns `False` on timeout
   abandonment with no record; the hook is documented fail-soft. Nothing measures or logs
   the abandonment, so a deterministic performance regression produced no alarm for 4+ days.

2. **The diagnostic misdirects.** `_startup_relay_failure_context` (line 1887) emits
   "does not match its metadata sidecar (sha256, byte-length, harness id, role, freshness,
   or startup-disclosure shape mismatch); it may be stale, wrong-role, or displaced by a
   non-disclosure payload". In this case the cache was byte-identical to its sidecar, correct
   harness, correct role, and correct shape. Only freshness failed. The message points the
   reader at file corruption, which cost the originating session several turns of misdirected
   investigation before measurement identified the budget overrun.

## Proposed Change (Slice A: observability and diagnostic accuracy only)

**A1. Record the refresh outcome with its measured duration.**
Instrument `_refresh_startup_relay_cache_bounded` so each invocation appends a bounded record
(outcome one of `completed` / `timeout_abandoned` / `error`, measured elapsed seconds, the
budget in force, and `role_mode`) to the existing startup diagnostic directory resolved by
`_startup_diagnostic_dir`. Fail-soft is preserved: a failure to write the record must never
raise into the hook path.

**A2. Classify the relay failure honestly.**
When `relay_identity_ok` and `content_matches_meta` are both true and only `freshness_ok` is
false, emit a distinct diagnostic naming the real condition -- cache identity-intact and
content-consistent but stale (measured age vs TTL), self-heal refresh abandoned after the
budget -- instead of the current corruption-shaped message. Genuine identity, shape, or
content mismatches keep the existing message unchanged.

No change to gate semantics, no change to timeout values, no change to what is or is not
relayed. This slice makes the existing behavior measurable and correctly described.

## Explicitly Out of Scope (deliberate; forbidden by the governing PAUTH)

- **Raising the timeout.** Setting the budget above the render time would hang every
  stale-cache PB session start for 39+ seconds. That is a worse defect than the current one
  and must not be adopted as a reflex fix.
- **Fixing the ~39s render.** The underlying latency regression is unexplained. The comment at
  `scripts/workstream_focus.py:115-117` shows 5.0s was sized expecting rendering to "exceed two
  seconds", implying roughly 2.5x headroom that something later consumed. Diagnosing that
  belongs in a follow-on slice informed by A1's measurements.
- **Relaying a stale cache with a staleness banner.** Treating identity-intact-but-stale as
  degraded-but-relayable is defensible and consistent with the recoverable / non-recoverable
  split established by WI-3447, but it is a governance-semantics change to
  `GOV-SESSION-SELF-INITIALIZATION-001` delivery and should be decided by the owner on its own
  merits, not bundled into an observability fix.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` -- fresh sessions self-initialize with a startup
  disclosure. The defect prevents delivery on PB interactive sessions; this slice does not yet
  restore delivery but makes the failure diagnosable, which is prerequisite to restoring it.
  Included spec on the governing PAUTH.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` -- the init-keyword relay contract that
  governs the surface being instrumented. Included spec on the governing PAUTH.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` -- state claims derive from fresh canonical reads; the
  freshness evaluation being misreported is the subject of A2. Included spec on the governing
  PAUTH.
- `GOV-FILE-BRIDGE-AUTHORITY-001` -- governs this bridge artifact. This proposal is filed as the
  next numbered file in the versioned bridge file chain,
  `bridge/gtkb-wi5650-pb-startup-relay-selfheal-budget-001.md`. The numbered bridge files are
  append-only: no prior version is deleted, rewritten, or renumbered, and every subsequent
  verdict or report in this thread is added as a new numbered bridge file.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` -- this proposal cites every relevant
  governing specification; the linkage above is the mechanical satisfaction of that constraint.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` -- the Test Plan below derives at least one
  executable test from each linked specification, and no `VERIFIED` may issue for an untested
  linked specification.
- `GOV-STANDING-BACKLOG-001` -- WI-5650 is the governed backlog authority for this work.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` -- govern the PAUTH cited above.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` -- `scripts/workstream_focus.py` is a shared
  cross-harness hook surface; changes must not break Codex-side parity.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` -- durable capture of the measured evidence.

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-SESSION-SELF-INITIALIZATION-001` and
`DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` already require the disclosure to be delivered
and already define the relay contract. This slice adds no new required behavior; it adds
measurement and corrects an inaccurate diagnostic string for behavior those specs already
govern. No new or revised requirement is needed before implementation.

## Cross-Harness Disposition

- **codex** -- shared-surface-unaffected. `scripts/workstream_focus.py` is invoked by both
  harnesses. The change adds a fail-soft diagnostic record and refines one message string,
  altering no hook contract, exit code, or payload shape.
- **cursor** -- shared-surface-unaffected. Same rationale as codex; no registration or contract
  change.

## Prior Deliberations

- `DELIB-202667181` (owner decision, 2026-07-22) -- the AUQ authorization that created the
  governing PAUTH for this slice and bounded its scope to the two target paths.
- `DELIB-20265664` (VERIFIED, WI-3447, `gtkb-pb-startup-disclosure-cache-freshness-contract`)
  established the recoverable-content-drift vs non-recoverable-identity-mismatch split that
  the current self-heal path implements. This proposal does not alter that contract; it reveals
  that the recoverable branch is unreachable in practice for PB because refresh cannot finish.
- `DELIB-20266279` (owner decision DECISION-0729, 2026-05-28) -- when the startup relay was
  previously degraded the owner chose "Defer startup, take direct task instruction", evidence
  that this failure has recurred and that blocking the owner's first turn on it is unwanted.
- `DELIB-20261025` (LO Advisory: Startup Disclosure Relay Truncation) and `DELIB-20264940` /
  `DELIB-20264942` (relay truncation fix review and verification) -- prior work on this same
  relay surface; the truncation class is distinct from the budget class addressed here.
- `DELIB-20261086` (GO, Startup Payload Profiler + Compact SessionStart Context) -- prior
  startup-latency work on the payload path; relevant precedent for measuring startup cost.
- WI-4827 (deferred) diagnoses a TOCTOU ordering bug with a cryptographically intact,
  seconds-stale cache. Its candidate fixes would NOT resolve this defect, because regeneration
  never completes at any check ordering. Recorded so the two are not conflated.
- WI-5084 and WI-5565 cover startup-input-gate blocking behavior. Both reproduced during the
  originating investigation, but they are a separate surface from the relay refresh path and
  are explicitly out of scope here.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Test Plan (spec-derived)

| Specification | Derived test | Assertion |
|---|---|---|
| `GOV-SESSION-SELF-INITIALIZATION-001` | `test_refresh_records_timeout_abandonment` | With a stubbed render exceeding the budget, `_refresh_startup_relay_cache_bounded` returns `False` AND a record with `outcome="timeout_abandoned"`, a measured elapsed value, and the budget is persisted. |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | `test_refresh_records_completion` | With a stubbed fast render, the helper returns `True` and records `outcome="completed"` with elapsed below budget. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_stale_but_intact_cache_reports_staleness_not_corruption` | For an identity-intact, content-consistent, stale cache whose refresh failed, the diagnostic names staleness and refresh abandonment and does NOT claim sha256/byte-length/harness/role/shape mismatch. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_genuine_identity_mismatch_message_unchanged` | For a wrong-role or shape-broken cache the existing corruption-shaped message is emitted unchanged (no regression). |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | existing `platform_tests/hooks/test_workstream_focus.py` suite | Full suite passes; no cross-harness regression. |
| `GOV-STANDING-BACKLOG-001` | WI-5650 present and linked | Backlog linkage verified. |

Commands to execute: `python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short`,
`python -m ruff check <changed>`, `python -m ruff format --check <changed>`.

## Acceptance Criteria

1. A stale-cache PB startup that abandons refresh leaves a durable record containing the
   measured elapsed time, the budget, the outcome, and `role_mode`.
2. The owner-visible diagnostic for an identity-intact-but-stale cache names staleness and
   refresh abandonment rather than corruption.
3. The diagnostic for genuine identity/shape mismatch is byte-unchanged.
4. Refresh-path behavior (return values, fail-soft posture, gate semantics) is otherwise
   unchanged; no timeout or TTL constant value is modified.
5. Full `test_workstream_focus.py` suite passes; ruff check and ruff format --check pass.

## Risk and Rollback

Risk is low. The change adds a fail-soft diagnostic write and refines one message string on an
already-failing branch. The principal risk is the new record write itself raising inside a
`UserPromptSubmit` hook; it is therefore wrapped so any exception is swallowed, matching the
surrounding fail-soft contract. A second risk is diagnostic-log growth, bounded by writing a
single small record per relay evaluation into the existing diagnostic directory.

Rollback: revert the single commit touching `scripts/workstream_focus.py` and its test file.
No state migration, no config change, no schema change, nothing to undo outside those files.

## Owner Decisions / Input

This proposal depends on owner approval and cites the AskUserQuestion evidence that authorizes
it, per `.claude/rules/prime-builder-role.md` AskUserQuestion-only channel.

1. **AUQ 2026-07-22, "Startup relay".** Owner selected **"Investigate the mismatch"** -- read-only
   inspection of the cache and sidecar to identify the exact cause. This authorized the
   investigation that produced the measured evidence above.
2. **AUQ 2026-07-22, "Next step".** Owner selected **"Dig deeper before recording anything"** --
   confirm or refute with source evidence before recording. This authorized the empirical
   measurement and led to retracting an incorrect `ActivityProfileError` hypothesis before it
   entered any durable artifact.
3. **AUQ 2026-07-22, "Disposition".** Owner selected **"File item + draft a fix proposal"** --
   capture the work item AND draft a bridge implementation proposal for Loyal Opposition review.
4. **AUQ 2026-07-22, "Authorization".** Owner selected **"Authorize this project scope"**,
   recorded as `DELIB-202667181`, which created the governing PAUTH bounded to WI-5650 and the
   two target paths. This is the direct authorization for filing this proposal.

No owner decision is requested by this proposal itself. The three deferred items under
"Explicitly Out of Scope" are forbidden operations on the governing PAUTH and would each
require their own owner decision if a later slice pursues them; they are named here so the
deferral is visible rather than silent.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
