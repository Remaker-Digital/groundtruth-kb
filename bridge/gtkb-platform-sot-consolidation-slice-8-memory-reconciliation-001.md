NEW

# Platform SoT Consolidation — Slice 8: MEMORY.md + topic-file reconciliation (WI-4346, WI-4347)

bridge_kind: prime_proposal
Document: gtkb-platform-sot-consolidation-slice-8-memory-reconciliation
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-21 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: f8a1abee-94b2-4e6c-a9c7-795a8e7c7dae
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI explanatory output style, interactive session

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-SLICE-8-MEMORY-RECONCILIATION
Project: PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION
Work Item: WI-4346

target_paths: ["memory/MEMORY.md", "memory/SESSION-HANDOFF-2026-06-19-production-readiness-roadmap.md", "memory/canonical-terminology-md-new-section.md", "memory/canonical-terminology-md-rewrite-preview.md", "memory/codex-review-gate-md-rewrite-preview.md", "memory/dispatched-2026-06-11-fab01-step4-5-completed.md", "memory/dispatched-2026-06-11-fab04-fab01-stand-down.md", "memory/dispatched-2026-06-11T20Z-fab01-fab03-stand-down.md", "memory/dispatched-2026-06-11T20Z-fab04-git-reclamation-executed.md", "memory/dispatched-789f0e-wi4522-author-metadata-owner-blocked.md", "memory/draft_bridge_gtkb_platform_sot_consolidation_umbrella_001.md", "memory/handoff-2026-06-11-pb-fab20-and-hooks-restoration.md", "memory/handoff-2026-06-11-pb-fab21-fable-program.md", "memory/handoff-2026-06-11-pb-fab21-hyg025-hyg028-done.md", "memory/handoff-2026-06-11-stage2-filed-stage3-gated.md", "memory/handoff-2026-06-11-stage3-collision-yielded.md", "memory/handoff-2026-06-11-stage3-proposal-filed.md", "memory/handoff-2026-06-11-wi4459-verified-wi4461-impl.md", "memory/handoff-2026-06-12-cheap-harness-program-and-fab05-verify.md", "memory/handoff-2026-06-12-cheap-harness-program-progress-and-wi4472-collision.md", "memory/handoff-2026-06-12-tafe-program-drive.md", "memory/handoff-2026-06-12-wi4472-awaiting-go.md", "memory/handoff-2026-06-12-wi4472-closed.md", "memory/handoff-2026-06-12-wi4472-proposal-filed.md", "memory/handoff-2026-06-13-S438-tafe-telemetry-stuckflow.md", "memory/handoff-2026-06-13-pb-implementation-loop.md", "memory/handoff-2026-06-13-s436-governance.md", "memory/handoff-2026-06-13-tafe-live-pilot-parked-draft.md", "memory/handoff-2026-06-13-tafe-swarm-drive-S437.md", "memory/handoff-2026-06-13-tafe-swarm-drive-S438.md", "memory/handoff-2026-06-14-S440-backlog-loop.md", "memory/handoff-2026-06-14-S445-repo-cleanup-push-merge.md", "memory/handoff-2026-06-14-interactive-pb-marker-block-advisory.md", "memory/handoff-2026-06-14-tafe-cutover-driver.md", "memory/keep-working-pb-2026-06-11-0608z-outcome.md", "memory/nogo-backlog-triage-2026-06-18.md", "memory/phase-1-glossary-backfill-draft.md", "memory/phase-2-template-pre-population-draft.md", "memory/phase-3-glossary-expansion-hook-draft.md", "memory/phase_2_worktree_audit_2026_05_11.md", "memory/recovery-2026-06-11-fab20-commit-collision.md", "memory/research_sot_consolidation_2026_06_04.md", "memory/s133-live-test-migration.md", "memory/session-wrap-2026-04-29.md", "memory/slice-4-smart-poller-retirement-continuation.md", "memory/sot_consolidation_owner_decisions_2026_06_04.md", "memory/spec_content_dcl_sot_registry_projection_parity_001.md", "memory/spec_content_dcl_sot_registry_record_schema_001.md", "memory/spec_content_gov_platform_sot_registry_001.md", "memory/topics/session_s231_summary.md", "memory/topics/session_s259.md", "memory/topics/session_s262_summary.md", "platform_tests/scripts/test_slice8_memory_reconciliation.py"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Slice 8 of the Platform SoT Consolidation umbrella
(`bridge/gtkb-platform-sot-consolidation-umbrella-008.md` GO) reconciles the
in-repo operational notepad: `memory/MEMORY.md` becomes an index-only template
(per `ADR-0001`'s "MEMORY.md is the operational notepad / index, not a content
store" tier) and the accumulated session ephemera under `memory/` is retired so
durable knowledge (MemBase, the Deliberation Archive, and git history) is the
substrate of record.

A deterministic classifier (`.gtkb-state/slice8/classify_memory.py`, read-only)
bucketed all 173 tracked `memory/` files into RETIRE (51 clear ephemera),
PRESERVE (75 durable), and AMBIGUOUS (47, default-preserve). This proposal:

1. **WI-4346** — rewrites `memory/MEMORY.md` (currently 201 lines / 109 KB) to an
   index-only template; the bulky session-state content is removed (it lives in
   MemBase / Deliberation Archive / git).
2. **WI-4347** — `git rm` the 51 RETIRE-bucket ephemera files; preserves the
   other 122 (75 PRESERVE + 47 AMBIGUOUS).

Disposition is **delete** (`git rm`) per owner decision `DELIB-20265460`: git
history is the authoritative record for the retired ephemera. WI-4348 (strip
role/current-state prose from `.claude/rules/*.md`) is explicitly OUT of scope
(split to a separate audit-first effort per owner decision this session).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed as the next status-bearing numbered
  bridge file; numbered file chain + dispatcher/TAFE state are canonical.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched paths (`memory/**`,
  `platform_tests/**`, the bridge file) are in-root under `E:\GT-KB`; no
  application/out-of-root placement is involved. The root-boundary/placement
  contract is satisfied.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section cites
  every governing spec; the verification tests derive from them.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Project
  Authorization / Work Item metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Verification
  Plan maps each spec to an executed test.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — MemBase is the source of truth;
  `MEMORY.md` is the non-authoritative operational notepad. Reducing it to an
  index reinforces the freshness contract (state derives from canonical reads,
  not stale notepad copies).
- `GOV-STANDING-BACKLOG-001` — future-work / backlog lives in MemBase
  `work_items`, not `MEMORY.md`; the index template carries no backlog content.
- `GOV-08` — Knowledge Database is the single source of truth; retiring
  superseded notepad copies (e.g. `spec_content_*`, already in MemBase) removes
  drift surfaces.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` /
  `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — covered by
  `PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-SLICE-8-MEMORY-RECONCILIATION`
  (cites `DELIB-20265460`; allowed mutations `file_deletion`, `documentation`,
  `test_addition`).
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — PAUTH cites
  `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` + `GOV-STANDING-BACKLOG-001`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — retirement uses explicit
  lifecycle disposition (retire) rather than silent deletion.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the notepad is reorganized
  toward durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — retire/preserve is an
  explicit lifecycle-state transition.

Note: `memory/MEMORY.md` is NOT a protected narrative artifact (the
narrative-artifact-approval set is `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE.md`,
`applications/*/CLAUDE*.md`), so no narrative-artifact-approval packet is required
for the rewrite. The file deletions are authorized by `DELIB-20265460` per the
CLAUDE.md "Protected Behaviors & Removal Rule" (explicit owner approval to
remove).

## Prior Deliberations

- `DELIB-20260671` — owner 7-AUQ pass authorizing the Platform SoT consolidation
  umbrella (Slice 8 is in the approved 9-slice sequence).
- `DELIB-20265460` — owner AUQ this session (2026-06-21) authorizing this
  destructive plan (delete the 51 ephemera; rewrite MEMORY.md as index; preserve
  the other 122). Owner-decision evidence for this filing.
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` — precedent for
  retiring a transitional markdown memory surface once its content authority
  migrated to MemBase.
- `bridge/gtkb-platform-sot-consolidation-umbrella-008.md` — umbrella GO.
- `ADR-0001` (Three-Tier Memory Architecture) — MemBase (canonical) / MEMORY.md
  (operational notepad/index) / Deliberation Archive (reasoning). This slice
  realigns MEMORY.md to its index tier.

## Owner Decisions / Input

This proposal depends on owner approval and cites it here:

- **AUQ (2026-06-21, this interactive PB session), recorded as `DELIB-20265460`**
  (`source_type=owner_conversation`, `outcome=owner_decision`,
  `presented_to_user=true`, `transcript_captured=true`).
  - Question: authorize the re-scoped Slice 8 destructive plan (delete the 51
    classifier-identified ephemera files, rewrite MEMORY.md as index, preserve
    the other 122).
  - Owner answer: **"Authorize — delete the 51 (`git rm`); rewrite MEMORY.md as
    index; preserve the other 122."**
- Prior same-session AUQs: owner directed "proceed autonomously + queue
  GO/VERIFIED-dependent items for Codex" and "author the re-scoped Slice 8 plan +
  file the proposal now; split WI-4348 out."

No further owner decision is required to file this NEW proposal.

## Requirement Sufficiency

**Existing requirements sufficient.** `ADR-0001` (memory tiers),
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `GOV-STANDING-BACKLOG-001`, and the
WI-4346/WI-4347 scope define the intended end state. No new/revised requirement
is needed; the destructive scope is bounded by `DELIB-20265460`.

## Planned Changes

### WI-4346 — rewrite `memory/MEMORY.md` to an index-only template

New template shape (bootstrap + index; no bulky session-state):

```text
# GroundTruth-KB Operational Memory — Index

> MEMORY.md is the operational notepad INDEX, not a content store. Canonical
> knowledge lives in MemBase (groundtruth.db); reasoning lives in the
> Deliberation Archive; retired session detail lives in git history.

## Session Bootstrap
- Location: E:\GT-KB ; key files: CLAUDE.md, this index.
- Role/bridge/backlog: resolve live (harness-registry, gt bridge dispatch
  status, gt backlog list).

## Recent Sessions
- <one line per recent session: id + focus + outcome pointer>

## Preserved Topic Index
- memory/feedback/ — owner feedback corpus (durable behavioral guidance).
- memory/topics/ — durable architecture / reference / decision notes.
- memory/release-readiness.md — current release-readiness state.
- memory/CLAUDE_ARCHIVE.md — historical archive.
- <one line per preserved cluster>
```

### WI-4347 — `git rm` the 51 RETIRE-bucket files

The complete delete list (also in `.gtkb-state/slice8/retire.txt`; equals the
`target_paths` minus `memory/MEMORY.md` and the test):

**Session handoffs (23):** all `memory/handoff-2026-06-*.md` (the 11/12/13/14
series enumerated in `target_paths`).
**Dispatched-worker notes (5):** `memory/dispatched-2026-06-11-*.md`,
`memory/dispatched-2026-06-11T20Z-*.md`, `memory/dispatched-789f0e-*.md`.
**Spec-content drafts now in MemBase (3):** `memory/spec_content_dcl_sot_registry_projection_parity_001.md`,
`memory/spec_content_dcl_sot_registry_record_schema_001.md`,
`memory/spec_content_gov_platform_sot_registry_001.md`.
**Rewrite previews / new-section drafts (3):** `memory/canonical-terminology-md-new-section.md`,
`memory/canonical-terminology-md-rewrite-preview.md`,
`memory/codex-review-gate-md-rewrite-preview.md`.
**Phase drafts / audits (4):** `memory/phase-1-glossary-backfill-draft.md`,
`memory/phase-2-template-pre-population-draft.md`,
`memory/phase-3-glossary-expansion-hook-draft.md`,
`memory/phase_2_worktree_audit_2026_05_11.md`.
**Other one-off ephemera (16):** `memory/SESSION-HANDOFF-2026-06-19-production-readiness-roadmap.md`,
`memory/draft_bridge_gtkb_platform_sot_consolidation_umbrella_001.md`,
`memory/keep-working-pb-2026-06-11-0608z-outcome.md`,
`memory/nogo-backlog-triage-2026-06-18.md`,
`memory/recovery-2026-06-11-fab20-commit-collision.md`,
`memory/research_sot_consolidation_2026_06_04.md`,
`memory/s133-live-test-migration.md`, `memory/session-wrap-2026-04-29.md`,
`memory/slice-4-smart-poller-retirement-continuation.md`,
`memory/sot_consolidation_owner_decisions_2026_06_04.md`,
`memory/topics/session_s231_summary.md`, `memory/topics/session_s259.md`,
`memory/topics/session_s262_summary.md`.

PRESERVE (122 files) — untouched: all `memory/feedback/**` + root `feedback_*`,
`memory/archive/**`, durable `memory/topics/**` (reference/decision/architecture
topics + the 47 AMBIGUOUS default-preserve project/program topics),
`memory/release-readiness.md`, `memory/CLAUDE_ARCHIVE.md`,
`memory/gt-cli-invocation-harness-b.md`,
`memory/project_external_resource_registry.md`,
`memory/pending-owner-decisions.md`.

### Verification guard — `platform_tests/scripts/test_slice8_memory_reconciliation.py`

New pytest with three assertions (below).

## Spec-Derived Verification Plan

| Specification | Test / Command | Expected |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` + `GOV-STANDING-BACKLOG-001` (WI-4346) | `test_memory_md_is_index_template` — asserts `memory/MEMORY.md` is index-shaped (has the index headings, carries no bulk session-state / backlog content, under an index-size threshold) | PASS |
| WI-4347 (retire) | `test_retired_ephemera_absent` — asserts each of the 51 RETIRE paths no longer exists | PASS |
| WI-4347 (preserve) + `GOV-08` | `test_preserved_files_present` — asserts the PRESERVE anchors (feedback/, release-readiness.md, CLAUDE_ARCHIVE.md, project_external_resource_registry.md, pending-owner-decisions.md, topics/reference_*) still exist | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | the pytest suite, run with the repo venv | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | applicability + clause preflights on this file | PASS |

Execution interpreter (repo venv):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_slice8_memory_reconciliation.py -q --no-header
```

## Risk / Rollback

Destructive but bounded and reversible:

- Deletions are strictly the 51 RETIRE-bucket files; the PAUTH forbids deleting
  any PRESERVE/AMBIGUOUS file, and the classifier is deterministic and
  re-runnable.
- `git rm` keeps full content in git history; rollback = `git revert` the single
  VERIFIED commit (restores files + prior MEMORY.md).
- No source logic, config, or KB schema change; `MEMORY.md` is a notepad, not a
  protected narrative artifact, so no behavior/runtime change.

Contamination note: `memory/MEMORY.md` currently carries an unrelated
uncommitted hunk from another work stream. The VERIFIED finalization stages only
the `target_paths`; implementation must ensure that pre-existing hunk is either
committed by its owning thread or cleanly subsumed by the index rewrite before
the Slice 8 commit, so the verified commit contains only Slice 8 changes.

## Bridge Filing

Filed under `bridge/` as the next status-bearing numbered bridge file for
`gtkb-platform-sot-consolidation-slice-8-memory-reconciliation` (append-only).
Dispatcher/TAFE state + the numbered file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`chore` — operational-notepad maintenance: retire superseded session ephemera and
reshape `MEMORY.md` to its index tier. No new capability, no source/behavior
change; the guard test is the regression boundary.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
