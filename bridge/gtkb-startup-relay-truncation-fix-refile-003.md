REVISED

Document: gtkb-startup-relay-truncation-fix-refile

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3323
target_paths: ["scripts/workstream_focus.py", ".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/scripts/test_codex_session_start_dispatcher.py", "platform_tests/scripts/test_claude_session_start_dispatcher.py", "platform_tests/scripts/test_workstream_focus_hook_parity.py"]

# Implementation Proposal: Fix Init-Keyword Startup-Disclosure Relay Truncation

Status: REVISED
Author: Prime Builder (claude / harness B)
Date: 2026-05-15 (S353+)
Origin: Loyal Opposition advisory, converted to scoped implementation work per the peer-solution / advisory loop.
Source advisory: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-10-36-startup-disclosure-relay-truncation.md`

## Supersession Note

This proposal re-files the work originally proposed in the bridge thread
`gtkb-startup-disclosure-relay-truncation-fix` (`-001` NEW, `-002` GO). That
thread received a valid Codex GO, but its `target_paths` were written as a
human-readable `### target_paths` subsection that
`scripts/implementation_authorization.py` cannot parse, so no
implementation-start packet could be created. Bridge files are append-only and
`REVISED` is a post-`NO-GO` state, so the GO'd thread could not be corrected in
place. Per owner decision (AskUserQuestion, 2026-05-15) this thread re-files the
identical substance with a machine-readable `target_paths:` JSON metadata line
and a `## Files Expected To Change` section. The original thread has been withdrawn at
`bridge/gtkb-startup-disclosure-relay-truncation-fix-003.md` (status
`WITHDRAWN`). There is no scope change from the original GO'd content; the seven
authorized paths and all implementation conditions from the original `-002` GO
carry forward unchanged.

This proposal is filed under `bridge/` with a `bridge/INDEX.md` entry at status
`NEW`. The superseded thread's prior versions (`-001`, `-002`) are preserved
unchanged with no deletion or rewrite; that thread has received the append-only
`WITHDRAWN` version `-003` and its `bridge/INDEX.md` entry now records latest
status `WITHDRAWN`, consistent with the append-only bridge audit trail.

## Revision Note (-003 vs -001)

-003 addresses the `-002` NO-GO:

- FINDING-P1-001 (blocking) — the original thread
  `gtkb-startup-disclosure-relay-truncation-fix` has now been genuinely
  withdrawn: `bridge/gtkb-startup-disclosure-relay-truncation-fix-003.md`
  (status `WITHDRAWN`) is filed and `bridge/INDEX.md` records that thread's
  latest status as `WITHDRAWN`. A single same-work-item implementation route
  now remains; the Supersession Note above reflects the actual withdrawn state.
- FINDING-P3-002 — the helper-file wording is tightened so the machine-readable
  `target_paths` and the prose scope agree exactly.

No technical-scope change from `-001`; the seven `target_paths` and the
verification plan are unchanged.

## Summary

The init-keyword startup-disclosure relay transports an exact-relay startup
message (~15 KB) inline through the UserPromptSubmit hook `additionalContext`
channel. That channel can be truncated before the assistant model reads it.
When truncated, the assistant cannot satisfy the exact-relay contract and
either stops (observed Codex failure) or, in a harness with a persisted-output
escape hatch, must perform a recovery file read that the gate wording forbids.

This proposal converts the LO advisory into a scoped, testable fix with three
parts:

1. Convert the relay transport from oversized in-band content to a bounded
   pointer contract plus a harness-scoped startup-disclosure cache file.
2. Replace the contradictory "do not use tools" fallback wording with an
   explicit single read-only-read exception.
3. Remove the shared dashboard report from the automatic exact-relay fallback
   path so a multi-harness session cannot relay a wrong-role disclosure.

The fix changes startup hook transport and recovery only. It does not change
startup content generation; `scripts/session_self_initialization.py` remains
the single startup-content producer.

## Specification Links

- DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 — central governing constraint; status `specified`. Its Required Behavior items 1-6, Test Expectations, and Evidence section describe this exact defect (the relay must render the disclosure visibly, the interactive cache must be isolated from bridge auto-dispatch payloads, and an unavailable/displaced cache must fail visibly). This proposal implements that specified DCL.
- DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 — receiver-side role authority; constrains the role-correctness aspect of Finding 3 (a relay must not present a disclosure for a role that is not the active harness's durable role).
- GOV-SESSION-SELF-INITIALIZATION-001 — fresh-session self-initialization disclosure requirement; the relay is the delivery mechanism for that disclosure.
- PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001 — sessions must treat the governance startup disclosure as a first-class relay obligation, not optional context.
- DCL-SESSION-STARTUP-TOKEN-BUDGET-001 — startup token-cost discipline; the bounded-pointer change reduces `additionalContext` from ~15 KB to a small pointer, directly serving this constraint.
- SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 — the `::init gtkb <mode>` syntax whose match activates the relay path under change.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — Claude / Codex SessionStart hook parity; the harness-scoped cache write must land symmetrically in both harness dispatchers.
- GOV-RELIABILITY-FAST-LANE-001 — governs the filing path; this proposal is filed as a reliability fast-lane defect fix and cites the standing project artifacts.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge protocol authority governing this proposal as a bridge artifact.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — cross-cutting constraint requiring this proposal to cite every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — cross-cutting constraint requiring the post-implementation VERIFIED step to rest on executed spec-derived tests; the Spec-Derived Test Plan below maps every linked spec to a test.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — artifact-oriented governance baseline; this fix is captured as governed work (WI-3323) with a bridge artifact and spec-derived tests.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — durable artifact-graph model; the WI, bridge thread, and linked specs form the artifact graph for this work.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle trigger discipline; the LO advisory triggered a work item which triggers this implementation proposal and its tests.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`
already specifies the required relay behavior (Required Behavior items 1-6),
the cache-isolation constraint, and the fail-visibly constraint. This proposal
implements that existing `specified` DCL. No new or revised requirement or
specification is created by this work. The owner explicitly declined SPEC/DCL
formalization for this fix (see Owner Decisions / Input). If the implementation
fully satisfies the DCL, a separate `kb-promote` operation may later advance
`DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` from `specified` toward
`implemented`; that promotion is out of scope here and is noted as a follow-on.

## Prior Deliberations

- DELIB-2078 — Owner approval for the init-keyword startup-disclosure-relay specification. Establishes owner intent that a matched init keyword must produce the owner-visible disclosure; this proposal implements the approved constraint.
- DELIB-1536 — Loyal Opposition review of SessionStart formalization (init-keyword contract). Prior review of the SessionStart / init-keyword path this proposal modifies.
- DELIB-1530 / DELIB-1531 — Loyal Opposition reviews of Loyal Opposition startup symmetry. Relevant to Finding 3 (role-correct relay; the LO startup path must not be shadowed by a Prime Builder disclosure).
- DELIB-1076 / DELIB-1077 / DELIB-1079 / DELIB-1080 — SessionStart hook dispatcher and schema repair deliberations. Prior repairs to the SessionStart dispatcher surface (`session_start_dispatch.py`) that this proposal extends with a harness-scoped cache write.

No prior deliberation rejected a bounded-pointer relay transport; this is the
first proposal to convert the relay from in-band content to a pointer contract.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by the following
AskUserQuestion decisions captured in this session (2026-05-15, S353+):

1. Disposition of LO advisory `INSIGHTS-2026-05-15-10-36-startup-disclosure-relay-truncation.md` — owner selected **"Draft bridge proposal now"**: file a NEW bridge proposal to implement the pointer-contract fix, proceeding to Codex review.
2. Governance project path for WI-3323 — owner selected **"Reliability fast-lane"**: file the fix under `PROJECT-GTKB-RELIABILITY-FIXES` against the standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, with no new per-fix deliberation, project authorization, or formal-artifact-approval packet.
3. The owner did not select SPEC/DCL formalization; no new formal artifact is created by this proposal (see Requirement Sufficiency).

WI-3323 was converted (v2) from an advisory-routing work item (origin `hygiene`)
to a defect-origin fast-lane work item and linked to `PROJECT-GTKB-RELIABILITY-FIXES`
(membership record `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3323`).

## Problem Statement

### Finding 1 — Exact relay depends on an oversized in-band hook payload

`scripts/session_self_initialization.py` emits the exact-relay startup content
after the `## User-Visible Startup Message` marker. `scripts/workstream_focus.py`
`_startup_gate_response` (line ~1140) extracts that content via
`_cached_startup_disclosure` (line ~1101) and inlines it into `additionalContext`
under `## Cached User-Visible Startup Message` (line ~1145). The startup contract
requires exact, unabridged relay, but the transport channel can be truncated
before the model reads it. A local reproduction reported an `additionalContext`
length of ~15 KB. Once truncated, the assistant cannot satisfy exact relay.

### Finding 2 — The fallback instruction is internally contradictory

The gate message (`workstream_focus.py` line ~1127) tells the assistant to read
`docs/gtkb-dashboard/session-startup-report.md` if the SessionStart payload is
unavailable, while the same instruction block forbids tool use on the
disclosure-relay turn. The only useful recovery path requires a file read, but
the wording forbids it; a correct assistant stops instead.

### Finding 3 — Shared markdown fallback can relay the wrong role

`STARTUP_REPORT_RELATIVE_PATH` (`workstream_focus.py` line ~96) is the shared
path `docs/gtkb-dashboard/session-startup-report.md`. In a multi-harness session
that file can be overwritten by the counterpart harness. If a Loyal Opposition
session falls back to it, it can relay a Prime Builder disclosure — a wrong-role
relay that looks authoritative. `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`
Required Behavior 5 already requires interactive relay cache files to be isolated
from bridge auto-dispatch payloads.

## Proposed Implementation

### Part A — Bounded pointer contract (Finding 1)

1. During SessionStart, after `_valid_session_start_payload(...)` passes, the
   dispatcher extracts the `## User-Visible Startup Message` content and writes
   a harness-scoped startup-disclosure cache file plus a metadata sidecar
   (harness name, harness id, durable role, generated timestamp, byte length,
   SHA-256). Cache files are runtime evidence, not committed artifacts.
2. `_startup_gate_response` is converted so `additionalContext` carries a small
   pointer contract: the cache path plus expected length and SHA-256, not the
   full ~15 KB body.
3. The gate wording explicitly authorizes exactly one read-only filesystem read
   of the named cache file when the full disclosure is not already present in
   model context, followed by verbatim relay then stop.

### Part B — Explicit read-only fallback exception (Finding 2)

Replace the contradictory wording with an explicit single read-only-read
exception: no ordinary task work, no file mutation, no session-focus mapping,
no broad exploration on the relay turn; but exactly one read-only read of the
named harness-scoped cache is permitted when the disclosure is not fully in
context, then verbatim relay then stop.

### Part C — Remove shared-report auto-fallback (Finding 3)

Remove `docs/gtkb-dashboard/session-startup-report.md` from the automatic
exact-relay fallback candidate list. The automatic fallback is the
harness-scoped cache only. If the shared dashboard report is retained at all,
it is gated behind strict validation (generated timestamp not older than the
current SessionStart request; harness id matches the active durable harness id;
role matches the active role map entry; hash / length metadata matches). When
the cache is unavailable, malformed, or displaced by a non-disclosure payload,
the gate fails visibly with an actionable diagnostic and does not mark
`startup_response_pending` satisfied.

### target_paths

Implementation edits are authorized only within these paths:

- `scripts/workstream_focus.py`
- `.claude/hooks/session_start_dispatch.py`
- `.codex/gtkb-hooks/session_start_dispatch.py`
- `platform_tests/hooks/test_workstream_focus.py`
- `platform_tests/scripts/test_codex_session_start_dispatcher.py`
- `platform_tests/scripts/test_claude_session_start_dispatcher.py`
- `platform_tests/scripts/test_workstream_focus_hook_parity.py`

`scripts/session_self_initialization.py` is NOT a target path; the startup
content producer is unchanged. Shared extraction / SHA-256 helper logic is
added ONLY as local helper functions inside the three listed source files
above. A new helper file is NOT authorized by this proposal; if one becomes
necessary during implementation, work stops and a revised proposal listing
that path is filed. This carries the original `-002` GO condition forward verbatim.

## Spec-Derived Test Plan

Each linked specification maps to at least one test. Tests are added or updated
within the `target_paths` test files.

- T1 — `test_workstream_focus.py`: `_startup_gate_response` returns a bounded `additionalContext` (byte length below a conservative ceiling, e.g. 4096) containing the harness-scoped cache path plus expected SHA-256 and length, not the full disclosure body. Covers DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 Finding 1 and DCL-SESSION-STARTUP-TOKEN-BUDGET-001.
- T2 — `test_workstream_focus.py`: the gate wording contains the explicit single read-only-read exception and prohibits substituting a status acknowledgement for the disclosure; it does not contain a blanket "do not use tools" instruction that forbids the recovery read. Covers DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 Required Behavior 2-4 and Finding 2.
- T3 — `test_workstream_focus.py`: the shared `docs/gtkb-dashboard/session-startup-report.md` path is absent from the automatic relay fallback candidate list (or, if retained, is reached only after strict harness/role/timestamp/hash validation). Covers DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 Required Behavior 5 and Finding 3.
- T4 — `test_claude_session_start_dispatcher.py` and `test_codex_session_start_dispatcher.py`: SessionStart writes the harness-scoped startup-disclosure cache plus metadata sidecar only after `_valid_session_start_payload` passes; a bridge auto-dispatch SessionStart payload does not populate the interactive relay cache. Covers DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 Required Behavior 5 (cache isolation) and GOV-SESSION-SELF-INITIALIZATION-001.
- T5 — `test_workstream_focus.py`: when the relay cache is missing or contains a non-disclosure payload, the gate emits an actionable visible diagnostic and does not mark startup-response state satisfied. Covers DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 fail-visibly constraint and Finding 2.
- T6 — `test_workstream_focus_hook_parity.py`: the harness-scoped cache write and UserPromptSubmit gate behavior are parity-equivalent across the Claude and Codex dispatchers. Covers ADR-CODEX-HOOK-PARITY-FALLBACK-001 and DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001.

Verification commands:

```
python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short
python -m pytest platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py -q --tb=short
python -m pytest platform_tests/scripts/test_workstream_focus_hook_parity.py -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

## Acceptance Criteria

1. `_startup_gate_response` `additionalContext` is bounded (below the chosen
   conservative ceiling) and carries the cache pointer plus SHA-256 and length.
2. The gate wording authorizes exactly one read-only read of the named cache
   and prohibits status-acknowledgement substitution; the contradictory
   "do not use tools" blanket is removed.
3. The shared dashboard report is no longer an automatic exact-relay fallback;
   the automatic fallback is the harness-scoped cache only.
4. Both SessionStart dispatchers write the harness-scoped cache plus metadata
   only on a validated payload; the interactive relay cache is isolated from
   bridge auto-dispatch payloads.
5. A missing or non-disclosure relay cache produces a visible actionable
   diagnostic and never a falsely-satisfied startup-response state.
6. All listed tests pass; `ruff check` and `ruff format --check` are clean.
7. Startup content generation in `scripts/session_self_initialization.py` is
   unchanged.

## Fast-Lane Eligibility

This proposal is filed under the reliability fast-lane. Eligibility against
`GOV-RELIABILITY-FAST-LANE-001`:

1. Origin is `defect` — WI-3323 v2 carries origin `defect` (broken init-keyword
   startup relay).
2. No new public API or CLI surface; the harness-scoped cache file and gate
   pointer are internal startup-transport behavior introduced solely to remove
   the defect.
3. No new or revised requirement or specification; the work implements the
   already-`specified` `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`.
4. Single concern (startup-disclosure relay transport), three source files.
   Net source size is expected within the fast-lane guide; if Loyal Opposition
   judges the change too large, NO-GO and refile under a standard project path
   is the expected enforcement outcome and is accepted by the owner per the
   Owner Decisions / Input AUQ.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this proposal content before
filing:

- `bridge_applicability_preflight.py` — `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- `adr_dcl_clause_preflight.py` — exit 0; `must_apply` clauses 3/3 with evidence; blocking gaps: 0.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-defect source-and-test fix. It is not a bulk
backlog operation. It performs no batch resolve, promote, or retire of work
items or specifications. References to "work item", "backlog", "standing
backlog", and "fast-lane" describe the single work item WI-3323 and its
governed filing path only. The applicable evidence pattern is a single-WI
defect-fix implementation proposal with formal-artifact-approval discipline
preserved unchanged (no formal artifact is created; the inventory of touched
files is the seven `target_paths` entries above).

## Files Expected To Change

- `scripts/workstream_focus.py` — bounded pointer contract in `_startup_gate_response`; gate wording; shared-report fallback removal.
- `.claude/hooks/session_start_dispatch.py` — harness-scoped startup-disclosure cache write after payload validation.
- `.codex/gtkb-hooks/session_start_dispatch.py` — harness-scoped startup-disclosure cache write after payload validation.
- `platform_tests/hooks/test_workstream_focus.py` — T1, T2, T3, T5 spec-derived tests.
- `platform_tests/scripts/test_claude_session_start_dispatcher.py` — T4 cache-write test.
- `platform_tests/scripts/test_codex_session_start_dispatcher.py` — T4 cache-write test.
- `platform_tests/scripts/test_workstream_focus_hook_parity.py` — T6 parity test.

## Risk and Rollback

- Scope is isolated to startup hook transport and recovery; startup content
  generation is untouched. Blast radius is the fresh-session relay turn only.
- Rollback: revert the pointer-contract change in `workstream_focus.py` and the
  cache-write additions in the two dispatchers; the existing
  `last-session-start.json` diagnostic cache remains as the prior behavior.
- Interim operator workaround if a regression appears before rollback: on a
  truncated relay, read the harness-scoped startup cache (or
  `.codex/gtkb-hooks/last-session-start.json` / `.claude/hooks/last-session-start.json`),
  extract content after `## User-Visible Startup Message`, relay verbatim, and
  do not use the shared dashboard report unless harness/role/freshness is
  manually verified.

## Review Questions for Loyal Opposition

1. Is the fast-lane eligibility argument acceptable, or should this refile
   under a standard project path?
2. Is the chosen `additionalContext` byte ceiling approach (assert below a
   conservative constant) the right regression guard?
3. Should the shared dashboard report be fully removed from the fallback path,
   or retained behind strict validation? The proposal permits either; LO
   guidance is welcome.
