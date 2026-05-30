NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 8c70eac3-4056-47ed-9910-27f1a0b42708
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning

Project Authorization: PAUTH-WI-3443-PROJECT-COMPLETION-SCANNER-V4-001
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3443

# Project-Completion Scanner D3+D4 Fix + GOV v4 Addressing-Thread Discriminator — Implementation

bridge_kind: implementation_proposal

Document: gtkb-project-completion-scanner-addressing-thread-fix-implementation
Version: 001 (NEW; implementation following Codex GO at scoping-002)
Date: 2026-05-29 UTC

## Summary

Implements the D3+D4 fail-safe design approved by Codex at `bridge/gtkb-project-completion-scanner-addressing-thread-fix-scoping-002.md` (GO):

- **D3 (top-version-only scan)**: `verified_work_items()` in the scanner and `_verified_work_items()` in the lifecycle byte-equivalent duplicate collect `Work Item:` lines ONLY from the VERIFIED top-version file of a thread, not all versions.
- **D4 (`implements` linkage gate)**: a work item is counted as VERIFIED-complete only when its addressing thread is linked to the project via `project_artifact_links.relationship='implements'`. Auto-completion is fail-safe: absent any `implements`-linked VERIFIED coverage for a gating work item, the pass does NOT auto-complete or retire — it surfaces a notification for manual confirmation.
- **GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v4**: captures the `implements` discriminator as the canonical machine-checkable rule per Codex's "before the implementation relies on it for automatic retirement" requirement.
- **Transition plan**: a one-time backfill script populates `relationship='implements'` on existing active project-to-bridge-thread links where the linked thread is the implementation thread (excludes reauthorization, governance-review, scoping threads).
- **Regression + parity + negative tests**: cover the addressing-thread semantics, the all-versions sub-defect, the fail-safe no-auto-complete pathway, and the Claude/Codex hook copy parity.

## Owner Decisions / Input

This proposal proceeds on owner AskUserQuestion approvals captured in S373:

1. **Vehicle choice (DELIB-2503 §1)**: "Single comprehensive proposal" — owner selected this option via AskUserQuestion in S373; durable evidence is the AUQ tool record. Authorizes D3+D4 code + v4 spec update + tests + transition plan in one proposal.
2. **PAUTH approval (DELIB-2503 §2)**: "Create focused PAUTH" — owner approved creating `PAUTH-WI-3443-PROJECT-COMPLETION-SCANNER-V4-001` under `PROJECT-GTKB-RELIABILITY-FIXES`. Standing reliability PAUTH remains for fast-lane work.
3. **DECISION-0758 (S373)**: "Pivot to backlog triage (Recommended)" — owner's earlier session decision opened the triage path that surfaced the scanner-fix as the LIVE RISK priority. The scanner-fix takes precedence over the triage; triage umbrella stays as a working-tree draft.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — the spec whose v3 "addressing thread" criterion the current implementation mis-implements. This proposal authorizes a v4 update via separate formal-artifact-approval packet at MemBase insert time.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this implementation proposal is filed at `-001` NEW. The bridge file is at `bridge/gtkb-project-completion-scanner-addressing-thread-fix-implementation-001.md`; the INDEX update adds `Document: gtkb-project-completion-scanner-addressing-thread-fix-implementation` + `NEW: bridge/gtkb-project-completion-scanner-addressing-thread-fix-implementation-001.md` to insert at top of `bridge/INDEX.md` as a new entry; append-only. No deletion or rewrite of prior versions.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the test plan below maps each spec clause to executable verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — covered by `PAUTH-WI-3443-PROJECT-COMPLETION-SCANNER-V4-001`'s envelope (source-code + test-code + gov-spec-mutation + project-artifact-link-value-convention; schema-migration forbidden).
- `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001`, `ADR-ARTIFACT-FORMALIZATION-GATE-001` — govern the v4 spec update's formal-artifact-approval packet at MemBase insert time.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — `.claude/hooks/project-completion-surface.py` and `.codex/gtkb-hooks/project-completion-surface.py` must remain byte-parity after this implementation; if the parity contract requires updates due to behavior changes downstream of the scanner/lifecycle fix, both copies update simultaneously.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the D4 discriminator is deterministic and machine-checkable (no LLM judgement at scan time).
- `GOV-STANDING-BACKLOG-001` — WI-3443 is now an active backlog member of `PROJECT-GTKB-RELIABILITY-FIXES`; this proposal is NOT a bulk-ops mutation (single-WI scope, not backlog reorganization, not authority-state change). Per the bulk-ops clause-scope clarification convention, this filing does not match bulk-operation evidence patterns.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — cited because the LIVE-INCIDENT evidence references `applications/Agent_Red/` (the Slice 3 quarantine context). This proposal performs NO `applications/` mutation; that path is `--forbid`-listed in the PAUTH envelope. Quarantine class is explicitly excluded from target_paths.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory, per Codex scoping preflight): cited because this proposal mutates durable artifacts (MemBase spec versioning + project-link value convention + lifecycle/scanner code).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory, per Codex scoping preflight): cited because the implementation alters when project-authorization completion triggers retire.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory, per Codex scoping preflight): cited because the implementation reshapes governance-visible work-item-to-thread relationship semantics.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-scoping-001.md` (Prime scoping NEW) and `bridge/gtkb-project-completion-scanner-addressing-thread-fix-scoping-002.md` (Codex GO) — predecessor scoping thread.

## Requirement Sufficiency

Existing requirements sufficient for the D3+D4 code mechanics; new requirement capture is bounded to the v4 spec update of `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`. The v4 update captures the `implements` discriminator that already exists conceptually in v3's "addressing thread" language but is not machine-checkable as written. The v4 update authority is the formal-artifact-approval gate per `GOV-ARTIFACT-APPROVAL-001`; this proposal authorizes the surrounding code work and cites the planned packet at v4 insert time.

## Implementation Plan

### Phase 1 — D3 top-version-only scan

In `scripts/project_verified_completion_scanner.py` `verified_work_items()` (lines 73-101): instead of iterating `for version in document.versions`, read only the latest VERIFIED-status version file and parse `Work Item:` lines from it. Apply the same change in `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` `_verified_work_items()` (lines 402-431) to preserve byte-equivalence between the two surfaces.

### Phase 2 — D4 `implements` linkage gate

Extend both `verified_work_items()` and `_verified_work_items()` to:

1. For each VERIFIED-topped document, look up the project-to-thread link in `project_artifact_links` (table accessed via `db.list_project_artifact_links()` or equivalent).
2. Count the document's top-version `Work Item:` lines only if at least one link with `relationship='implements'` exists between the project's row and the document's thread row.
3. If no `implements`-linked thread covers a gating work item, the WI does NOT count as verified-complete; auto-completion does not fire for that project.

The fail-safe is intentional: if a project lacks `implements` coverage, manual review is required rather than automatic retirement.

### Phase 3 — `auto_complete_ready_authorizations()` semantic preservation

`auto_complete_ready_authorizations()` (`groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:608-650`) keeps its current loop structure but consumes the corrected `_verified_work_items()` output. `_authorization_completion_ready()` (`:386-400`) and `complete_project_authorization()` (`:513-606`) unchanged. The fail-safe behavior emerges from the upstream filter.

### Phase 4 — GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v4

New version of the spec adds:

- The `implements` discriminator: an addressing thread is a bridge thread linked to the project via `project_artifact_links.relationship='implements'`. A VERIFIED bridge thread that does not carry an `implements` link does NOT count as the addressing thread for any work item it cites.
- The fail-safe default: when a project has gating work items but no `implements`-linked VERIFIED coverage, auto-completion does NOT fire.
- The all-versions sub-defect closure: scanning collects `Work Item:` lines only from the VERIFIED top-version file of a thread.

Formal-artifact-approval packet generated at v4 insert time via `python -m groundtruth_kb generate-approval-packet` per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`. The packet covers the spec body, the body hash, the explicit owner approval evidence (the implementation report's owner-acknowledgement section), and the active PAUTH (`PAUTH-WI-3443-PROJECT-COMPLETION-SCANNER-V4-001`).

### Phase 5 — Transition plan for `implements` link backfill

New script `scripts/backfill_project_implements_links.py` (read-and-write deterministic CLI) iterates active projects in `PROJECT-GTKB-RELIABILITY-FIXES` and elsewhere; for each project-to-bridge-thread link currently at `relationship='related'`:

1. Read the linked bridge thread's top-version frontmatter to determine `bridge_kind`.
2. Excluded slug patterns: `*-reauthorization`, `*-scoping`, `*-governance-*`, `*-advisory-*` (denylist; documented as a soft heuristic for the backfill ONLY — not the run-time discriminator).
3. Excluded bridge_kinds: `governance_review`, `loyal_opposition_advisory`, `spec_intake`, verdict-class.
4. For threads passing both filters AND whose top version is `VERIFIED` AND whose `Work Item:` metadata matches a project-linked WI: promote `relationship` to `implements` via append-only version.
5. Emit a report listing promoted links + skipped links + manual-review-required cases (where automated determination is ambiguous).

The backfill is idempotent (rerunning is safe) and reports its actions for owner review. The script is itself reviewable: a separate post-Codex-GO step runs it and reports the link delta to the owner via AskUserQuestion before continuing.

### Phase 6 — Tests

- `platform_tests/scripts/test_project_verified_completion_scanner.py`: regression test that a VERIFIED thread citing `Work Item: WI-X` WITHOUT an `implements` link MUST NOT mark WI-X verified; regression test that a `Work Item:` line in a superseded NO-GO/REVISED version of a VERIFIED-topped thread MUST NOT count (D3).
- `groundtruth-kb/tests/test_project_artifacts.py`: regression test that `auto_complete_ready_authorizations()` MUST NOT complete an authorization when the only VERIFIED thread citing its gating WI is a non-`implements` thread; regression test that `_verified_work_items()` returns the same set as `verified_work_items()` (byte-equivalence parity check).
- `platform_tests/hooks/test_project_completion_surface.py`: parity check that `.claude/hooks/project-completion-surface.py` and `.codex/gtkb-hooks/project-completion-surface.py` remain byte-identical after this implementation.
- `platform_tests/scripts/test_backfill_project_implements_links.py` (new): unit tests for the transition script's exclusion logic, idempotency, and report format.

Explicit negative tests inside the scanner test file: name reauthorization, governance-review, and scoping-thread fixtures explicitly and assert each must NOT count their cited `Work Item:` lines as VERIFIED-complete.

### Phase 7 — Implementation order

1. Phase 1 D3 + Phase 2 D4 code in both files with regression tests; tests fail before fix, pass after (test-first discipline).
2. Phase 6 tests landed and green on the fix.
3. Phase 5 backfill script + tests; reviewer dry-run report to owner via AskUserQuestion.
4. Owner approves backfill report → script runs in apply mode → reports delta.
5. Phase 4 v4 spec update via `generate-approval-packet` + MemBase insert with packet evidence.
6. Doctor / release-gate verifications.
7. Post-implementation report filed for Codex VERIFIED.

## Specification-Derived Verification

| Spec clause / requirement | Spec-to-test mapping |
|---|---|
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v3 "addressing thread" | `platform_tests/scripts/test_project_verified_completion_scanner.py` — negative tests for reauth/governance/scoping threads (per Phase 6). Command: `python -m pytest platform_tests/scripts/test_project_verified_completion_scanner.py -q`. |
| v4 `implements` discriminator | `groundtruth-kb/tests/test_project_artifacts.py` — `auto_complete_ready_authorizations()` does NOT complete absent `implements` linkage. Command: `python -m pytest groundtruth-kb/tests/test_project_artifacts.py -q`. |
| D3 top-version-only scan | Phase 6 regression test: `Work Item:` in superseded version MUST NOT count. Command: same scanner test file. |
| Hook parity (`ADR-CODEX-HOOK-PARITY-FALLBACK-001`) | `platform_tests/hooks/test_project_completion_surface.py` — byte-parity assertion between `.claude/hooks/project-completion-surface.py` and `.codex/gtkb-hooks/project-completion-surface.py`. Command: `python -m pytest platform_tests/hooks/test_project_completion_surface.py -q`. |
| Backfill script correctness | `platform_tests/scripts/test_backfill_project_implements_links.py` — exclusion logic, idempotency, report format. Command: `python -m pytest platform_tests/scripts/test_backfill_project_implements_links.py -q`. |
| v4 spec update (formal-artifact-approval per `GOV-ARTIFACT-APPROVAL-001`) | `python -m groundtruth_kb generate-approval-packet --artifact-type spec --artifact-id GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` produces a packet with body + body_hash + presented_to_user assertion; MemBase insert hooked by `.claude/hooks/formal-artifact-approval-gate.py`. |
| No-regression | Existing tests pass: `python -m pytest platform_tests/scripts/test_project_verified_completion_scanner.py groundtruth-kb/tests/test_project_artifacts.py platform_tests/hooks/test_project_completion_surface.py -q`. Ruff clean on changed files. |
| LIVE-incident closure verification | Restore `PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION` (its retirement was the LIVE-INCIDENT trigger); rerun `auto_complete_ready_authorizations()`; assert the project is NOT auto-retired (post-D4 it requires `implements` linkage; the reauth thread is excluded from `implements` by default). |

## target_paths

- `scripts/project_verified_completion_scanner.py`
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `platform_tests/scripts/test_project_verified_completion_scanner.py`
- `groundtruth-kb/tests/test_project_artifacts.py`
- `platform_tests/hooks/test_project_completion_surface.py`
- `scripts/backfill_project_implements_links.py` (new)
- `platform_tests/scripts/test_backfill_project_implements_links.py` (new)
- `.claude/hooks/project-completion-surface.py` (parity preservation; no behavior change expected, but byte updates if downstream call signature shifts)
- `.codex/gtkb-hooks/project-completion-surface.py` (parity preservation; byte-mirror of `.claude/hooks/` copy)
- `groundtruth.db` (MemBase mutations declared below; per WI-3372 KB-mutation completeness check)

MemBase mutations (via API + formal-artifact-approval packet; surface = `groundtruth.db` listed above):

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4 (spec body update; formal-artifact-approval packet at insert time)
- `project_artifact_links` rows: promoted from `related` to `implements` via Phase 5 backfill (append-only versioning preserves history)

## Excluded paths (PAUTH `--forbid` envelope)

- Schema-migration files (none — D4 uses existing `relationship` column).
- Root `CLAUDE.md` (Slice 3 quarantine class; `--forbid root-claude-md-mutation`).
- Root `SECURITY.md` (Slice 3 quarantine class; `--forbid root-security-md-mutation`).
- `applications/Agent_Red/**` (Slice 3 quarantine class; `--forbid applications-agent-red-mutation`).

## Acceptance Criteria

- Loyal Opposition issues GO with explicit confirmation that:
  - The D3 + D4 implementation closes both sub-defects (incidental-citation over-count primary + all-versions scan secondary) per the scoping-002 design.
  - The fail-safe behavior is correctly implemented: no auto-completion absent `implements` coverage.
  - Tests are appropriately spec-derived and exercise the named negative cases (reauth/governance/scoping).
  - The transition plan (Phase 5 backfill) is safe and idempotent; the exclusion heuristics are appropriate.
  - The v4 spec update covers the discriminator semantics adequately.
  - Hook parity between `.claude/hooks/` and `.codex/gtkb-hooks/` is preserved.
  - The PAUTH envelope is appropriately scoped (no over-broad allowed-mutation classes; quarantine paths forbidden).

## Prior Deliberations

- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-scoping-001.md` — Prime scoping NEW.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-scoping-002.md` — Codex GO confirming D3+D4 direction.
- `DELIB-2503` — S373 owner-decision chain capturing vehicle choice + PAUTH approval.
- `DELIB-S324-PB-INTERROGATION-DIRECTIVE` — informs the spec-vs-bug framing (interrogative default toward owner factual claims, applied to "is this a bug or new behavior" framing).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — informs the choice of `implements` value-convention over an LLM-mediated discriminator.
- `bd0f8bfa` (chore: inventory regen 2026-05-28) — example of a focused-PAUTH comprehensive change in this project family.

## Risk and Rollback

- **Risk**: the Phase 5 backfill may incorrectly classify some `related` links as `implements` (or vice versa). Mitigation: Phase 5 emits a dry-run report for owner review via AskUserQuestion before applying; the run is idempotent and reversible (revert by appending a new version with `relationship='related'`).
- **Risk**: a downstream consumer of `project_artifact_links` may read `relationship` strictly for equality with `related`. Mitigation: Phase 7 step 1 includes a quick `grep` over the codebase for `relationship == 'related'` references; the proposal does not change the default insert value, only adds a meaningful alternative.
- **Risk**: the parity tests may surface a pre-existing parity gap unrelated to this fix. Mitigation: pre-implementation, run the existing parity test to baseline; any pre-existing failure is documented as a separate finding rather than expanded into this proposal's scope.
- **Risk**: v4 spec update's formal-artifact-approval packet may be rejected at gate time for missing `body_hash` or `presented_to_user` fields. Mitigation: use the canonical `python -m groundtruth_kb generate-approval-packet` CLI which produces packets with the required structure.
- **Rollback**: each phase commit is independently revertible. The v4 spec insert is append-only (revert by inserting v5 with the v3 body). The backfill script's effects are revertible (append `related` versions to revert promoted links). Hook copies are byte-mirrored; revert is `git revert` of the implementation commit.

## Recommended Commit Type

`fix:` for the implementation commits in Phases 1-3, 6 (scanner + lifecycle defect repair + tests). Phase 4 spec v4 = `feat:` (new machine-checkable behavior in spec text). Phase 5 backfill script + its tests = `feat:` (new tooling). Multiple thematic commits expected; this proposal is the single authorization vehicle.

## Codex Review Asks

1. Confirm or NO-GO the D3 + D4 implementation plan as scoped at Phase 1 + Phase 2.
2. Confirm the fail-safe semantic is correctly preserved (no auto-complete absent `implements` coverage).
3. Confirm the v4 spec update language captures the discriminator semantics adequately (review the planned spec body before insert).
4. Confirm the Phase 5 backfill script's exclusion heuristics + safety (dry-run + owner AUQ + idempotency).
5. Confirm the test coverage in Phase 6 is adequately spec-derived per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.
6. Confirm the PAUTH envelope's `--forbid` list catches the Slice 3 quarantine class adequately.
7. Flag any spec linkage gap or applicability preflight trigger this proposal misses.
