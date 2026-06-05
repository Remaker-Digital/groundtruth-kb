NEW

# Workspace Orphan-Cleanup: complete file relocation + commit residual narrative/rule edits

bridge_kind: governance_review
Document: gtkb-workspace-orphan-cleanup-2026-06-05
Version: 001
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Project: PROJECT-GTKB-PLATFORM-HYGIENE

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: aa899d25-f289-48c2-8583-812e53973e98
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, interactive session; dispatched for work-tree cleanup after REVISED-003 GO landed

## target_paths

- `.claude/rules/loyal-opposition.md`
- `.claude/rules/peer-solution-advisory-loop.md`
- `.claude/rules/bridge-permanent-operations-runbook.md`
- `.claude/rules/codex-dead-ends-and-false-positives.md`
- `.claude/rules/codex-decision-ledger.md`
- `.claude/rules/codex-knowledge-base-index.md`
- `.claude/rules/codex-loyal-opposition-runbook.md`
- `.claude/rules/codex-review-checklists.md`
- `.claude/rules/codex-review-operating-contract.md`
- `.claude/rules/codex-session-bootstrap.md`
- `.claude/rules/codex-standing-priorities.md`
- `.claude/rules/codex-way-of-working.md`
- `.claude/rules/exec-summary-report-guide.md`
- `.claude/rules/groundtruth-kb-vision.md`
- `.claude/rules/project-progress-dashboard-runbook.md`
- `.claude/rules/prompt-organize-reports-in-dropbox.md`
- `.claude/rules/session-start-prompt.md`
- `.claude/rules/template-code-review.md`
- `.claude/rules/template-decision-memo.md`
- `independent-progress-assessments/CODEX-DEAD-ENDS-AND-FALSE-POSITIVES.md`
- `independent-progress-assessments/CODEX-DECISION-LEDGER.md`
- `independent-progress-assessments/CODEX-KNOWLEDGE-BASE-INDEX.md`
- `independent-progress-assessments/CODEX-LOYAL-OPPOSITION-RUNBOOK.md`
- `independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/TEMPLATE-CODE-REVIEW.md`
- `independent-progress-assessments/TEMPLATE-DECISION-MEMO.md`
- `AGENTS.md`
- `CLAUDE.md`
- `memory/pending-owner-decisions.md`

requires_verification: true
implementation_scope: governance_review

## Why this proposal

The GT-KB work tree accumulated 22 protected-path orphan edits across multiple parallel sessions over recent days. The parallel session's `3897fc6c chore: session-checkpoint bundle (94 files; mixed peer/dispatched-session work)` swept unprotected modifications cleanly but could not commit the 22 protected items because each requires either an impl-auth packet (for `.claude/rules/`) or a narrative-artifact-approval packet (for `AGENTS.md`, `CLAUDE.md`, `memory/pending-owner-decisions.md`).

This is filed as a `governance_review` bridge (not `implementation_proposal`) because it authorizes a housekeeping landing commit with NO behavior change. Every file already exists in the working tree at its target location with prior-session content; this proposal just authorizes git to record what's already on disk.

The proposal expressly does NOT update any cross-references in `scripts/`, `platform_tests/`, `config/`, or `tests/` that point at the old IPA paths; those reference updates are explicitly OUT OF SCOPE for this proposal and should be addressed by a follow-on bridge that exercises the impl-auth-gate for those protected surfaces.

## Summary

**File operations to authorize:**

- 8 paired RENAMES from `independent-progress-assessments/CODEX-*` / `TEMPLATE-*` to `.claude/rules/codex-*` / `template-*` (file relocations from the prior canonical IPA location to the canonical-per-bridge-essential `.claude/rules/` location; git's rename detection should reconstruct these as renames).
- 8 ADDS of net-new `.claude/rules/*` files (`bridge-permanent-operations-runbook`, `codex-review-checklists`, `codex-review-operating-contract`, `codex-standing-priorities`, `exec-summary-report-guide`, `groundtruth-kb-vision`, `project-progress-dashboard-runbook`, `prompt-organize-reports-in-dropbox`, `session-start-prompt`) that have no IPA-original.
- 2 MODIFIED protected rules (`loyal-opposition.md`, `peer-solution-advisory-loop.md`) — content delta carried forward from prior sessions; this proposal does not author the content.
- 3 MODIFIED narrative artifacts (`AGENTS.md`, `CLAUDE.md`, `memory/pending-owner-decisions.md`) — content delta carried forward from prior sessions; each requires its own formal-artifact-approval packet at execution time per `GOV-ARTIFACT-APPROVAL-001`.

**No code changes. No behavior changes. No new tests required.** This is a file-housekeeping landing commit that completes work prior sessions started.

## Specification Links

| Spec | Severity | Trigger | How this proposal complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via `bridge/INDEX.md` as NEW versioned bridge file. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification | §Acceptance Criteria defines git-state verification (no executable tests; no behavior change). |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:GOV, narrative artifact, AGENTS.md, CLAUDE.md | 3 narrative-artifact-approval packets required at execution time for `AGENTS.md`, `CLAUDE.md`, `memory/pending-owner-decisions.md` per `DCL-ARTIFACT-APPROVAL-HOOK-001`. |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | blocking | content:approval packet, narrative artifact | Narrative-artifact-approval-gate hook will require per-file approval packets at Write/Edit time. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | path:.claude/rules/**, path:independent-progress-assessments/**, path:memory/** | All target_paths within `E:\GT-KB`; no out-of-root targets. |
| `.claude/rules/project-root-boundary.md` | blocking | path:E:\GT-KB | All target_paths under `E:\GT-KB`; no exceptions. |
| `.claude/rules/bridge-essential.md` | advisory | foundational | Bridge protocol integrity; this proposal is itself a bridge filing. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, work item, owner decision | Owner-decision driven (per AUQ); preserves the file moves as durable artifacts. |

## Requirement Sufficiency

**Existing requirements sufficient.** Owner-decision evidence: this session's AskUserQuestion response explicitly chose Option F1 ("File a chore bridge proposal for the cleanup") for landing the 22 protected items that the parallel session's `3897fc6c` chore bundle could not include. Per-file narrative-artifact-approval packets are required at execution time per `GOV-ARTIFACT-APPROVAL-001`.

## Prior Deliberations

- `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-004.md` — Codex GO on REVISED-003 (this session's prior work; established the cleanup-then-implement sequencing).
- Commit `3897fc6c chore: session-checkpoint bundle (94 files; mixed peer/dispatched-session work)` — parallel session's broad cleanup that left the protected items behind for owner-authorized cleanup.
- Commit `d517cbee chore(inventory): refresh dev-environment-inventory baseline (harnesses)` — parallel session's inventory regen unblocking the inventory-drift gate.
- `.claude/rules/bridge-essential.md` § Operational Mode — confirms `.claude/rules/` is the canonical narrative-authority location for rule files (negated in `.gitignore` so it remains tracked).
- `.claude/rules/codex-review-gate.md` § Counterpart Review Gate — establishes the bridge-GO-before-implementation contract.

No previously rejected approach is being revisited.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate.

Owner-decision evidence authorizing this proposal:

| Decision | Channel | Authority | Shapes |
|---|---|---|---|
| Land orphan cleanup via chore bridge | AskUserQuestion | This session's AUQ response "F1: File a chore bridge proposal for the cleanup (Recommended)" at 2026-06-05 UTC | Authorizes filing this bridge proposal and the subsequent implementation commits |
| 22 target_paths scope | AskUserQuestion | Same AUQ explicitly enumerated the 22 protected items as the cleanup scope | Defines the target_paths set above |
| Expanded cleanup directive | Owner prompt (this session) | "Do not exclude pre-session modified files. Do your best, but all of these must be fixed." | Authorizes including pre-session modified files in the cleanup scope |

Per-file narrative-artifact-approval packets at execution time will require per-packet owner approval as separate AUQ events per `GOV-ARTIFACT-APPROVAL-001`. Specifically: `AGENTS.md`, `CLAUDE.md`, `memory/pending-owner-decisions.md` each need a packet at `.groundtruth/formal-artifact-approvals/2026-06-05-{NARRATIVE-ARTIFACT-NAME}.json` before Write/Edit lands.

## Acceptance Criteria

1. **All 22 protected items land in git**: after the implementation commit(s), `git status --short` reports no entries matching any of the target_paths.
2. **Renames detected**: git's rename detection reconstructs the 8 IPA → `.claude/rules/` pairs as RENAMES (not delete+add), preserving file history.
3. **Net-new rules added**: the 8 net-new `.claude/rules/*` files are tracked in git.
4. **Modified rules + narrative artifacts land**: working-tree edits to `.claude/rules/loyal-opposition.md`, `.claude/rules/peer-solution-advisory-loop.md`, `AGENTS.md`, `CLAUDE.md`, `memory/pending-owner-decisions.md` are committed.
5. **No behavior change**: no `scripts/`, `groundtruth-kb/src/`, `groundtruth-kb/tests/`, `platform_tests/`, `config/`, `.claude/hooks/`, `.codex/gtkb-hooks/`, or `.github/` files are modified in this commit batch.
6. **Cross-reference debt acknowledged**: this commit batch does NOT update cross-references in `scripts/`, `AGENTS.md` (after this commit), `platform_tests/`, or `config/` that point at the IPA paths. A follow-on bridge thread is required for those.
7. **No project-root-boundary violation**: all target_paths within `E:\GT-KB`.

## Phased Implementation Plan

**Phase 1 — Narrative-artifact-approval packets (3 packets):**

1. Generate packet for `AGENTS.md` content edit. Owner approval gate fires.
2. Generate packet for `CLAUDE.md` content edit. Owner approval gate fires.
3. Generate packet for `memory/pending-owner-decisions.md` content edit. Owner approval gate fires.

**Phase 2 — Implementation-start authorization packet:**

4. After GO lands, run `python scripts/implementation_authorization.py begin --bridge-id gtkb-workspace-orphan-cleanup-2026-06-05` to obtain the impl-auth packet for `.claude/rules/` mutations.

**Phase 3 — Stage + commit batch:**

5. Stage the 8 IPA deletions + 8 corresponding `.claude/rules/` adds together (git detects renames).
6. Stage the 8 net-new `.claude/rules/*` adds.
7. Stage the 2 modified `.claude/rules/*` files.
8. Stage `AGENTS.md`, `CLAUDE.md`, `memory/pending-owner-decisions.md` (with packets active per Phase 1).
9. Commit with message: `chore(workspace): orphan-cleanup — relocate Codex rules + land protected rule/narrative edits per bridge gtkb-workspace-orphan-cleanup-2026-06-05`.
10. Confirm `git status --short` clean for all target_paths.

**Phase 4 — Implementation report:**

11. File `bridge/gtkb-workspace-orphan-cleanup-2026-06-05-002.md` (or next available version) as NEW post-impl report with confirmation evidence (`git log -1`, `git status --short`, per-rename detection from `git show --find-renames`).

## Specification-Derived Verification Plan

| Spec | Acceptance check |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This proposal exists in `bridge/INDEX.md` as NEW; receives GO/NO-GO/VERIFIED via standard protocol. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Specification Links section present; all relevant specs cited. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Verification check is git-state inspection (`git status --short` empty for target_paths after Phase 3); no executable tests because no behavior change. Verification report cites the post-impl `git log -1` + `git status --short` evidence. |
| `GOV-ARTIFACT-APPROVAL-001` | 3 narrative-artifact-approval packets executed at Phase 1 with owner approval. |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | Narrative-artifact-approval-gate hook validates each packet at Write time. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target_paths under `E:\GT-KB`; verified by the impl-auth parser returning paths all matching root pattern. |
| `.claude/rules/project-root-boundary.md` | All 30 target_paths verified in-root. |

## Risk and Rollback

**Risk 1 — IPA path cross-references break after delete**. Files in `scripts/session_self_initialization.py`, `AGENTS.md` (post-this-commit), `platform_tests/scripts/test_groundtruth_governance_adoption.py`, `config/agent-control/REVIEW-MODE-SETUP.md`, `config/agent-control/CONTROL-MAP.md` reference the old IPA paths. **Mitigation**: this proposal explicitly does NOT update those cross-references (per Acceptance Criterion 6); the references will be stale after this commit lands. A follow-on bridge thread (`gtkb-orphan-cleanup-cross-reference-update-002`) must address the cross-reference update under its own impl-auth-gate authorization. Runtime impact: `scripts/session_self_initialization.py` reading from the old IPA paths will return missing-file errors; the script SHOULD fall back to `.claude/rules/` (verify in follow-on).

**Risk 2 — narrative-artifact content drift**. The working-tree edits to `AGENTS.md`, `CLAUDE.md`, `memory/pending-owner-decisions.md` were authored by prior sessions; their content is unverified by this session. **Mitigation**: the per-file narrative-artifact-approval packets require owner-visible review of full content per `GOV-ARTIFACT-APPROVAL-001`. Owner can reject any individual edit at packet-approval time, leaving that file out of the commit batch.

**Risk 3 — rename detection fails**. Git rename detection is heuristic-based; if the IPA-original and `.claude/rules/` content drifted, git may record them as delete+add. **Mitigation**: post-commit `git show --find-renames` will surface this; rename loss is cosmetic (file history loss); acceptable for this cleanup.

**Rollback**: per-file reversibility:
- Phase 3 commit is a single git commit; revert via `git revert` if entire batch needs to be undone.
- Per-file unstaging during Phase 3 (before commit) is trivial.
- After commit lands, individual file restoration via `git checkout <prior-sha> -- <file>`.

## Pre-Filing Preflight Subsection

Both mandatory preflights to be run by Loyal Opposition reviewer:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-workspace-orphan-cleanup-2026-06-05
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-workspace-orphan-cleanup-2026-06-05
```

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight green.

This proposal cites every spec triggered by its paths and content per `config/governance/spec-applicability.toml`. No new bridge protocol clauses; reuses existing enforcement footprint.

---

*Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>*
