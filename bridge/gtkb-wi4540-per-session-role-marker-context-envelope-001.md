NEW

# WI-4540: Per-session/per-context session-role marker keyed to the stable context id — the `::init gtkb` envelope persists for the model-context lifetime

bridge_kind: prime_proposal
Document: gtkb-wi4540-per-session-role-marker-context-envelope
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-14 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 62a726da-80e5-4088-b2c4-796ab354da32
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B; session-stated role declared `::init gtkb pb`); explanatory output style; model claude-opus-4-8[1m]

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-4540-PER-SESSION-MARKER
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-4540

target_paths: ["scripts/workstream_focus.py", "scripts/bridge_work_intent_registry.py", "scripts/session_start_dispatch_core.py", "scripts/session_role_resolution.py", "scripts/gtkb_session_id.py", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/hooks/test_session_start_marker_invalidation.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Recommended commit type: fix:

---

## Summary

This proposal converts the Loyal-Opposition advisory `bridge/gtkb-session-role-marker-architecture-advisory-001.md` (ADVISORY) into an implementation proposal, merging its owner-decided fix direction (per-session marker files) with the owner's subsequent context-lifetime invariant captured as `DELIB-20263212`.

**The defect.** The session-stated-role marker `.claude/session/active-session-role.json` is a **single shared file** across all concurrent sessions on a workstation. Two coupled failures result:
1. **Cross-session clobber (advisory Defect 1 / WI-4463):** `scripts/session_start_dispatch_core.py` `_invalidate_session_role_marker()` deletes the marker **unconditionally** at SessionStart (no session-id check), so any *peer* session's SessionStart wipes *this* session's marker; and the writer's freshness heuristic can lock a live owner-Prime session out of its own marker slot.
2. **Mid-context vanish (advisory Defect 2):** the owner observed the marker present in one turn and absent the next, with no owner-visible SessionStart — caused by (1) plus the writer's session-id fallback chain (`scripts/gtkb_session_id.py` `MARKER_CONTINUITY_ORDER`) resolving a **phantom session id** that does not match the querying session's `CLAUDE_CODE_SESSION_ID` (observed: marker written under `1d33598a…` while the live session was `62a726da…`).

**The owner invariant (`DELIB-20263212`).** "A session is not a turn." The `::init gtkb (pb|lo)` envelope persists for the full lifetime of one contiguous model context — across every turn and across compaction/resume that preserve that context — invalidated only by a genuine context reset. This **revises** the `.claude/rules/canonical-terminology.md` "session-stated role" clause "does not survive compaction or resume": compaction/resume preserve the context, so the envelope must survive them.

**Consequence today:** interactive owner-Prime sessions cannot hold a `go_implementation` claim (the WI-4534 guard correctly reports "marker role None") and so cannot implement GO'd proposals or do stall-recovery — implementation becomes dispatch-only. This bit the very implementation of WI-4542 this session.

## Design

The stable identifier the advisory proved exists — the transcript UUID, constant across ~7h of contiguous turns including compaction — is the key. Five coordinated source changes (no hook-registration change; the contract-doc revision is a deferred follow-on):

### 1. Per-context marker keying (`scripts/workstream_focus.py`)
Replace the single-file path with a per-session file: `.claude/session/role-<session_id>.json`, keyed to the querying session's resolved id. Each session writes/reads only its own marker — no contention, no freshness heuristic, no peer clobber. Retain the legacy single-file path as a read-only transition fallback (removed once the guard reader is migrated).

### 2. Context-id-scoped SessionStart invalidation (`scripts/session_start_dispatch_core.py`)
`_invalidate_session_role_marker()` must NOT unconditionally delete the shared file. Under per-session keying it sweeps only marker files whose `session_id` ≠ the current context id (or whose transcript is stale by mtime) — preserving the current context's marker. Because compaction/resume preserve the transcript UUID, the current marker survives them; only a genuine new context (new UUID) leaves the prior marker to be swept. This is the mechanical realization of the `DELIB-20263212` invariant.

### 3. Session-id-validating guard reader (`scripts/bridge_work_intent_registry.py`)
`_interactive_marker_role()` (lines 321-337) currently reads the role with NO session-id validation. Migrate the WI-4534 guard's interactive branch to call `session_role_resolution.resolve_interactive_session_role(..., current_session_id=...)` (lines 137-145), which already validates that the marker's `session_id` matches the querying session — eliminating the unvalidated-reader divergence.

### 4. Consistent id resolution (`scripts/gtkb_session_id.py`, `scripts/session_role_resolution.py`)
The writer and the guard reader must resolve the SAME context id for a given session. Reconcile `MARKER_CONTINUITY_ORDER` usage so the write-side id and the read-side `current_session_id` agree (prefer the live `CLAUDE_CODE_SESSION_ID` / hook-payload `session_id` over stale env fallbacks for Claude-harness interactive sessions).

### 5. Stale-marker sweeper
A transcript-mtime-based sweeper (callable from session-wrap and/or the SessionStart sweep in change 2) removes `role-<session_id>.json` files whose transcript `mtime < now - N`. No periodic hook registration is added in this slice.

**Deferred to a follow-on (own approval packets):** the narrative revision of the `.claude/rules/canonical-terminology.md` "does not survive compaction or resume" clause and the corresponding `DCL-SESSION-ROLE-RESOLUTION-001` clause update. This slice implements the *behavior*; the contract-doc alignment is a small narrative/formal follow-on requiring `narrative-artifact-approval` + `formal-artifact-approval` packets, explicitly outside this PAUTH's `source`+`test_addition` scope.

## Specification Links

- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` — the interactive-session role-override contract; per-context keying realizes it correctly. The compaction-survival behavior aligns the implementation with the owner's `DELIB-20263212` clarification.
- `DCL-SESSION-ROLE-RESOLUTION-001` — deterministic marker>durable resolution table; the validated reader (change 3) enforces its session-id-match assertion uniformly across both reader paths.
- `GOV-SESSION-ROLE-AUTHORITY-001` — durable-vs-stated authority split; unchanged (headless dispatch still keys to the durable role; only the interactive marker substrate changes).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant governing specs cited; the bridge applicability preflight harvests them from this section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the project-linkage triple cites the bounded WI-4540 PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps each behavior to a spec-derived test.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the change preserves the WI-4534 write-time enforcement (the guard still rejects non-Prime interactive sessions); it removes the false-negative, not the enforcement.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — no `bridge/INDEX.md` write surface; bridge authority unchanged. The marker fix restores interactive Prime's ability to hold `go_implementation` claims through the governed claim path.
- `GOV-STANDING-BACKLOG-001` — `WI-4540` is the backlog authority (P2, defect, `bridge_dispatch`); this proposal also addresses `WI-4463` and the advisory's Defect 2.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all `target_paths` are in-root (`scripts/`, `platform_tests/`).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory), `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — durable, tested fix; advisory→implementation-proposal lifecycle; explicit deferral of the contract-doc revision stated rather than silently overreached.

## Requirement Sufficiency

Existing requirements sufficient. The owner's context-lifetime invariant is durably captured in `DELIB-20263212` (owner decision), and the governing `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` / `DCL-SESSION-ROLE-RESOLUTION-001` are sufficient to govern the source mechanics (per-context keying is consistent with marker>durable precedence). The advisory's per-session-marker direction is owner-decided (advisory AUQ, 2026-06-14). No new formal specification is required *before* implementing the source mechanics; the canonical-terminology + DCL contract-doc revision that aligns the documented invariant is a separate deferred follow-on artifact, not a precondition for this slice.

## Prior Deliberations

- `bridge/gtkb-session-role-marker-architecture-advisory-001.md` (ADVISORY, prior interactive PB session `7752bc97`, 2026-06-14 ~06:42Z) — the umbrella advisory this proposal converts. Owner AUQ chose per-session marker files (Option A; rejected Option C minimal-patch and Option D defer), umbrella scope, P1, drive-implementation-next-session. Its §"Implementation Recommendation" is the basis for changes 1-5 above.
- `DELIB-20263212` (this session, 2026-06-14) — owner context-lifetime envelope requirement + AUQ "capture spec + scope fix now" then "author now, anchor on WI-4540". Sharpens the advisory's previously-`unconfirmed` Defect 2 into the specified compaction-survival invariant.
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-003.md` — Slice 2 landed the current single-file marker writer in `scripts/workstream_focus.py`; this proposal amends that writer's keying model and the corresponding reader path.
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation` thread — Slice 3 landed the unconditional SessionStart invalidation in `scripts/session_start_dispatch_core.py`; change 2 amends it to be context-id-scoped.
- `WI-4534` — the role-eligibility guard correctly enforces the contract; the defect is substrate-side (marker keying/lookup), not guard-side. `WI-4463` — cross-session attribution bleed, the same single-file root cause, addressed by per-session keying. _(These sibling WI ids are related-work citations, not this proposal's primary work item; the WI-ID collision check flags them by design — declared work item is WI-4540.)_

## Owner Decisions / Input

Authorized by durable owner-decision evidence; no further owner AskUserQuestion is pending to file or (post-GO) implement the source mechanics.

- `DELIB-20263212` — owner AUQ (2026-06-14): "Capture spec + scope fix now" then "Author now, anchor on WI-4540". Authorizes this conversion proposal under `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-4540-PER-SESSION-MARKER` (allowed: `source` + `test_addition`; forbids formal-artifact, narrative-artifact, KB bulk status, config/hook registration, deploy/release, force pushes, credential lifecycle).
- The prior advisory's owner AUQ (2026-06-14 ~06:42Z) — per-session marker files, P1, drive implementation. Carried forward as the direction this proposal implements.
- **Scope note (informational):** the canonical-terminology + DCL contract-doc revision requires `narrative-artifact-approval` + `formal-artifact-approval` packets outside this PAUTH; it is deferred to a follow-on. No owner action is required for the source mechanics to proceed post-GO.

## Spec-Derived Verification Plan

Tests extend `platform_tests/` for the session-role substrate. Run with the repo venv (`-o addopts=` per the venv's missing `pytest-timeout`):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/hooks/test_session_start_marker_invalidation.py -q
```

| Behavior / spec | Test |
|---|---|
| Per-context marker write+read round-trips for the querying session id (DCL-SESSION-ROLE-RESOLUTION-001) | per-session keying write/read test |
| A peer session's SessionStart invalidation does NOT delete another session's marker (WI-4463; advisory Defect 1) | concurrent-session non-interference test |
| The current context's marker SURVIVES a SessionStart that carries the same context id (compaction/resume); only a different/stale context id is swept (DELIB-20263212 invariant) | context-id-scoped invalidation test |
| The WI-4534 guard's interactive branch validates session-id and accepts only the querying session's marker (DCL-SESSION-ROLE-RESOLUTION-001 assertion 6) | guard validated-reader test |
| Stale marker (transcript mtime older than threshold) is swept; live one retained | sweeper test |
| Legacy single-file marker still readable during the transition (no regression) | legacy-fallback test |

Plus `ruff check` and `ruff format --check` on every changed file.

## Risk / Rollback

- **Risk — invalidation change leaves stale markers.** Mitigated by the transcript-mtime sweeper (change 5) + the SessionStart sweep (change 2). Per-session files are individually small and self-expiring.
- **Risk — id-resolution reconciliation regresses dispatched-worker eligibility.** The dispatch-id path (`<ts>-<role>-<harness>-<hash>`) is unchanged; only the interactive-session id resolution is reconciled. A dedicated test asserts dispatched eligibility is preserved.
- **Risk — documented contract lags behavior** until the deferred follow-on revises the canonical-terminology clause. Disclosed; the behavior follows `DELIB-20263212`, and the follow-on aligns the glossary.
- **Rollback.** Per-session keying is additive — the legacy single-file path is retained as a fallback, so a single-commit revert restores prior behavior. No KB schema change, no bridge-authority change, no hook registration change.

## Bridge Filing (INDEX-Canonical)

Filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-wi4540-per-session-role-marker-context-envelope` document list in `bridge/INDEX.md` via the serialized `bridge index add-document` writer; append-only. `bridge/INDEX.md` remains canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`fix:` — repairs two coupled reliability defects (cross-session marker clobber + mid-context vanish) that block interactive owner-Prime implementation. The per-session keying is a structural change in service of the fix, not a standalone feature. (`refactor:` is a defensible alternative for the keying restructure; declared per the Conventional-Commits discipline.)

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
