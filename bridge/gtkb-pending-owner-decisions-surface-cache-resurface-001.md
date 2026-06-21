NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - Pending-owner-decisions surface caches at SessionStart and re-surfaces resolved entries on subsequent turns

bridge_kind: prime_proposal
Document: gtkb-pending-owner-decisions-surface-cache-resurface
Version: 001
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4282

target_paths: [".claude/hooks/owner-decision-tracker.py", "platform_tests/hooks/test_owner_decision_tracker.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The pending-owner-decisions surface re-presents already-resolved decisions on owner turns after they were resolved by a concurrent session. The `### Pending Owner Decisions` block is rendered once at SessionStart by `scripts/session_self_initialization.py` and injected as SessionStart `additionalContext`; that snapshot is then relayed by the model on later turns even though the durable file `memory/pending-owner-decisions.md` has since moved those entries from `## Pending` to `## Resolved` (with the question text blanked). The per-turn UserPromptSubmit nudge in `.claude/hooks/owner-decision-tracker.py` reads the durable file live, so it correctly reflects current state — but it stays silent when there are zero live pending decisions and therefore does not actively contradict a stale SessionStart relay. The fix makes the live per-turn surface authoritative: it emits a freshness marker (durable-file mtime + a question-hash set of the current `## Pending` IDs) on every turn so a stale SessionStart relay is mechanically distinguishable from current state, and it always emits when the live pending set has changed since SessionStart (including the empty case).

## Defect / Reproduction

Observed S386 2026-06-03: DECISION-0925, DECISION-0931, DECISION-0936 were resolved at 21:01:34Z by a concurrent triage-monitor session (status set to `resolved`, answer `Dismiss as stale or false-positive`, and the question text blanked to empty string per the recursive-re-trigger feedback memory). On a subsequent owner prompt in the original session, the `### Pending Owner Decisions` banner re-surfaced all three as if still pending, including the original (pre-blanking) question text.

Root cause: the banner the model relayed was the SessionStart snapshot. SessionStart rendering path: `.claude/settings.json` registers `SessionStart -> session_start_dispatch.py --startup-service scripts/session_self_initialization.py`; that service calls `render_report()`, which calls `_load_pending_owner_decisions(project_root)` (`session_self_initialization.py` lines 4724-4747, 4984-4993) once and emits a static `### Pending Owner Decisions` section. The original-question-text symptom (text that no longer exists in the durable file at relay time) proves the relayed content is the SessionStart snapshot, not a live read. The live UserPromptSubmit nudge (`owner-decision-tracker.py::_user_prompt_handler` -> `_format_nudge`, lines 1537-1604, 1629-1659) reads `## Pending` fresh each turn via `_read_pending_file` (lines 1550-1552), so it does NOT re-surface resolved entries; but when the live pending set is empty it returns `""` (line 1600-1601), leaving the stale SessionStart relay uncontradicted.

Reproduction (deterministic, hook-level): write `memory/pending-owner-decisions.md` with DECISION-0925/-0931/-0936 under `## Pending`; run the UserPromptSubmit hook once and capture the nudge (baseline). Move all three to `## Resolved` (blank their question) to simulate the concurrent-session resolution. Run the UserPromptSubmit hook again with an unrelated prompt: today it returns empty additionalContext (no contradiction of the stale banner). Expected after fix: the per-turn surface emits a freshness marker reflecting the now-empty `## Pending` set so the stale SessionStart banner is recognizable as superseded.

This is distinct from the detector-over-match issue tracked by `bridge/gtkb-owner-decision-tracker-startup-relay-known-match-suppression-004.md` (Stop-mode false-positive on relaying a known decision); this defect is the per-turn freshness of the surfaced banner, not the Stop-mode detector.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/hooks/owner-decision-tracker.py`, `platform_tests/hooks/test_owner_decision_tracker.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the durable file `memory/pending-owner-decisions.md` is the authoritative pending-decision state; this fix makes the per-turn surface read that authority every turn instead of letting a cached SessionStart snapshot stand in for it.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - keeps the owner-decision surface consistent with the durable artifact's current lifecycle state (pending vs resolved) rather than a transient SessionStart snapshot.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all governing specs (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below derives each test from a cited spec clause (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `SPEC-AUQ-POLICY-ENGINE-001` - the pending-owner-decisions surface is part of the AskUserQuestion-only owner-decision enforcement stack; re-surfacing resolved decisions undermines the integrity of that surface, and this fix restores per-turn accuracy of the owner-decision queue presentation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to a GT-KB platform hook (`.claude/hooks/...`) and platform tests; no adopter/application surface is touched and no application-placement boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-4282 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the surface is a Claude-side hook; this fix preserves the existing hook contract (graceful degradation, additionalContext output) without adding a cross-harness dependency, so harness-parity posture is unchanged.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the surfaced decision state remains artifact-backed (read from the durable file each turn) rather than inferred from a cached payload.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - aligns the surface with the durable artifact's resolved/pending lifecycle transitions so a resolution event is reflected on the next turn.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` already establishes the durable file as the authoritative pending-decision state, and `SPEC-AUQ-POLICY-ENGINE-001` already governs the owner-decision surface; this fix enforces those contracts at the per-turn surfacing boundary by adding a freshness marker and always-emit-on-change behavior. No new or revised requirement/specification is introduced.

## Prior Deliberations

- `DELIB-20265457` - Owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch (this WI is in scope).
- See `bridge/gtkb-owner-decision-tracker-startup-relay-known-match-suppression-004.md` - sibling thread on the Stop-mode relay false-positive; this proposal is explicitly scoped to the distinct per-turn freshness symptom, not that detector.
- See `bridge/gtkb-decision-tracker-cached-pending-block-exclusion-006.md` - prior treatment of cached pending-block relays in the Stop-mode structural-context check; relevant precedent that cached relays of the pending section are a recognized failure class, which this fix addresses on the surfacing (UserPromptSubmit) side.
- _No prior deliberation directly addresses the SessionStart-snapshot-vs-live-file per-turn freshness gap for the pending-owner-decisions surface; this proposal is the first to scope that specific symptom._

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-4282 is origin=defect, single-concern, introduces no new public surface and no new/revised spec, and is bounded to ~1 source file + 1 test (well under the fast-lane size guide), so it is covered by the reliability fast-lane standing authorization through active PROJECT-GTKB-RELIABILITY-FIXES membership.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for all open PROJECT-GTKB-RELIABILITY-FIXES work items; WI-4282 is P3 and in scope for the batch.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing owner direction establishing the reliability fast-lane for small defect fixes, the authorization vehicle carried by PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING.

## Proposed Scope

1. In `.claude/hooks/owner-decision-tracker.py`, make the UserPromptSubmit surface authoritative per turn:
   - Compute a deterministic freshness signature from the durable file each turn: the file mtime (when present) plus a stable hash over the sorted set of current `## Pending` DECISION IDs (the "question-hash set" the WI recommends, keyed by ID so it is robust to question-text blanking). Reuse the already-loaded `sections["pending"]` from `_read_pending_file` (lines 1550-1552) so no extra file read is added.
   - When live `## Pending` is non-empty and the prompt does not reference it, continue to emit `_format_nudge(...)`, but append a single freshness-marker line `(live as of <mtime/utc>; pending-set <short-hash>)` so a relayed stale SessionStart banner is mechanically distinguishable from the current live surface.
   - When live `## Pending` is empty, emit a concise `additionalContext` line stating the live pending set is empty (e.g. `[owner-decision-tracker] live pending owner-decision set is empty (<short-hash>); disregard any earlier cached "Pending Owner Decisions" banner.`) instead of returning `""`, so a stale SessionStart relay is actively superseded. This emission is gated to fire only when a non-empty SessionStart snapshot could plausibly be stale — implemented as: emit the empty-state marker whenever the durable file exists and parses (the common case), keeping the hook's graceful-degradation contract (any exception returns `""`).
   - Keep all existing owner-shortcut behavior (`clear pending`, `resolve`, `defer`, `defer all`) and the existing `_prompt_references_pending` suppression unchanged.
2. Add regression tests in `platform_tests/hooks/test_owner_decision_tracker.py` (see verification plan), reusing the existing `_run_hook("user-prompt-submit", ...)` / `_ups_payload(...)` harness already present in that file.

This is the defect-removal path. The WI's alternative framing (modeling/displaying that the banner may legitimately lag) is a behavior/contract change requiring a new requirement and is explicitly out of scope for this fast-lane defect fix; the SessionStart renderer in `scripts/session_self_initialization.py` is intentionally left unchanged (its Codex GO condition forbids reintroducing a separate SessionStart hook as the primary surface), and the per-turn live hook is the correct place to assert current state.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (durable file is authoritative; surface must reflect resolution) | `test_ups_emits_empty_marker_after_pending_resolved` | After all `## Pending` entries are moved to `## Resolved`, the UserPromptSubmit hook emits an empty-state freshness marker (non-empty additionalContext) rather than `""`, so a stale SessionStart banner is superseded. |
| `SPEC-AUQ-POLICY-ENGINE-001` (owner-decision surface accuracy per turn) | `test_ups_nudge_includes_live_freshness_marker_when_pending` | With live `## Pending` non-empty and an unrelated prompt, the emitted nudge includes the live freshness marker line (mtime/UTC + pending-set short-hash) alongside the existing nudge body. |
| `SPEC-AUQ-POLICY-ENGINE-001` (freshness signature reflects current pending set) | `test_ups_freshness_hash_changes_when_pending_set_changes` | The pending-set short-hash differs between a state with DECISION-0925/-0931/-0936 pending and the post-resolution empty state (hash is keyed on the sorted ID set, robust to question-text blanking). |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (resolution reflected on next turn) + graceful degradation | `test_ups_emits_nothing_when_durable_file_absent` | When `memory/pending-owner-decisions.md` does not exist (or parsing fails), the hook returns `""` (no marker), preserving the existing graceful-degradation contract and avoiding noise on fresh repos. |

Execution commands:
- `python -m pytest platform_tests/hooks/test_owner_decision_tracker.py -q --tb=short`
- `python -m ruff check .claude/hooks/owner-decision-tracker.py platform_tests/hooks/test_owner_decision_tracker.py`
- `python -m ruff format --check .claude/hooks/owner-decision-tracker.py platform_tests/hooks/test_owner_decision_tracker.py`

## Acceptance Criteria

1. After concurrent resolution moves all pending entries to `## Resolved`, the next UserPromptSubmit turn emits a live empty-state freshness marker that supersedes a stale SessionStart banner (no `""` in that case).
2. When live `## Pending` is non-empty, the nudge still emits its existing body plus a live freshness marker (mtime/UTC + pending-set short-hash); existing owner shortcuts and `_prompt_references_pending` suppression are unchanged.
3. The pending-set freshness hash is keyed on the sorted DECISION-ID set and changes when the live pending set changes (including the empty case), and is robust to question-text blanking.
4. When the durable file is absent or unparseable, the hook returns `""` (graceful degradation preserved).
5. The four derived tests pass; `ruff check` and `ruff format --check` are clean on the changed files.

## Risks / Rollback

- Risk: the empty-state marker could add per-turn additionalContext noise on every turn after the queue drains. Mitigation: the marker is a single concise line and is gated to emit only when the durable file exists and parses; it is far cheaper than re-surfacing resolved decisions, and it is the minimal signal needed to supersede a stale SessionStart relay.
- Risk: hashing the pending set adds per-turn work. Mitigation: the hash is over a small set of DECISION IDs already loaded in memory by `_read_pending_file`; no extra file read or I/O is introduced.
- Risk: changing the empty-pending return from `""` to a marker could surprise downstream consumers expecting empty output. Mitigation: the additionalContext channel is advisory; the change is covered by `test_ups_emits_empty_marker_after_pending_resolved` and the absent-file test confirms the no-file path still returns `""`.
- Rollback: revert the `_user_prompt_handler` / `_format_nudge` changes and the freshness-signature helper in `owner-decision-tracker.py`; the change is a small guarded addition plus tests, fully reversible with no migration and no schema change to the durable file.

## Files Expected To Change

- `.claude/hooks/owner-decision-tracker.py`
- `platform_tests/hooks/test_owner_decision_tracker.py`

## Recommended Commit Type

`fix`
