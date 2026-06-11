REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-05-rule-file-retirement
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4417
Project Authorization: PAUTH-FAB05-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 430d5513-21a1-4e1c-b244-743f2ca7ed00
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: [".claude/rules/bridge-permanent-operations-runbook.md", ".claude/rules/file-bridge-protocol.md", ".claude/rules/session-start-prompt.md", ".claude/rules/prompt-organize-reports-in-dropbox.md", ".claude/rules/exec-summary-report-guide.md", ".claude/rules/project-progress-dashboard-runbook.md", ".claude/rules/codex-knowledge-base-index.md", ".claude/rules/report-depth-prime-builder-context.md", ".claude/rules/report-depth.md", ".claude/rules/codex-review-operating-contract.md", ".claude/rules/acting-prime-builder.md", ".claude/rules/prime-builder.md", ".claude/rules/prime-builder-role.md", ".claude/rules/codex-standing-priorities.md", "independent-progress-assessments/bridge-automation/**", "archive/os-poller-2026-04-25/**", "independent-progress-assessments/archive/cursor-legacy/**", "platform_tests/scripts/**", "groundtruth-kb/docs/announcements/v0.7.0-rc1.md", ".groundtruth/formal-artifact-approvals/*.json", "groundtruth.db"]

KB mutation: the only MemBase mutation is the GOV-15-gated retire/reword of WI-3278 + WI-3465 (which presume the deleted memory/work_list.md); `groundtruth.db` is in target_paths to declare it.

---

# FAB-05 — Retire era-stranded + contradictory auto-loaded rule files, REVISED

WI-4417 (FAB-05) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-018, HYG-026, HYG-027, HYG-038.
Revises the proposal after the NO-GO at `bridge/gtkb-fab-05-rule-file-retirement-002.md`
(FINDING-P1-001).

## Revision Scope

This revision addresses the single finding in the `-002` NO-GO:

> FINDING-P1-001 — `target_paths` omit required implementation artifacts.

The proposal body and dispositions are unchanged; `target_paths` is completed to cover
every path the implementation plan mutates or creates. Added entries:

1. **`independent-progress-assessments/bridge-automation/**`** — the HYG-018 archive
   *source* tree (the `-001` listed only the `archive/os-poller-2026-04-25/**`
   destination; a `git mv`/archive must authorize the source as well).
2. **`.groundtruth/formal-artifact-approvals/*.json`** — the per-file
   narrative-approval packets for every protected `.claude/rules/*.md` edit (~10–12
   packets; the `-001` referenced them in prose but did not list the packet directory
   in `target_paths`).
3. **`platform_tests/scripts/**`** — the grep/pytest assertion test that encodes the
   grep-absence checks in the verification plan.
4. **`.claude/rules/prime-builder-role.md`** — the HYG-027 canonical home for the AUQ
   contract block (the `acting-prime-builder.md` duplicate is replaced with a pointer to
   it). Listed explicitly with its narrative-packet coverage in case the canonical block
   is edited to host the deduplicated content.

No disposition, owner decision, or verification claim changed; this is a scope-coverage
correction only.

## Summary

Four clusters of retired-era content that auto-load into **every session** and
misdirect work — the governance-active risk class:

- **HYG-018:** the retired OS-poller stack (25 files in `bridge-automation/`) is on
  disk un-archived, and `.claude/rules/bridge-permanent-operations-runbook.md`
  (auto-loaded) still **mandates** 3-minute pollers + repair commands, contradicting
  `bridge-essential.md`'s do-not-re-enable rule — accidental restoration is one
  command away. Residual echoes in `file-bridge-protocol.md:332,345`.
- **HYG-026:** four Cursor/Agent-Red-era rule files (~7K tokens/session) direct work
  to nonexistent `CURSOR-*` surfaces; `project-progress-dashboard-runbook.md` carries
  a live `e:/Claude-Playground` link violating `project-root-boundary.md`;
  `codex-knowledge-base-index.md` cites a wrong archive path.
- **HYG-027:** verbatim-duplicated normative blocks (two report-depth files; a
  duplicated + mislabeled Severity Model block; the AUQ contract byte-identical in
  two files; two overlapping PB files) — a lockstep-edit hazard.
- **HYG-038:** `codex-standing-priorities.md` anchors both roles' idle work to the
  **deleted** `memory/work_list.md` (S337), contradicting `GOV-STANDING-BACKLOG-001`.

All edits touch protected `.claude/rules/*.md` narrative artifacts, so each requires a
per-file narrative-approval packet at implementation (~10–12 packets).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle authority (the runbook/poller
  retirement + file-bridge-protocol echoes are bridge-governance edits).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — grep-absence verification below.
- `GOV-STANDING-BACKLOG-001` — the HYG-038 repoint restores the MemBase backlog as the
  sole idle-work authority.
- `GOV-ARTIFACT-APPROVAL-001` — every `.claude/rules/*.md` edit is a protected
  narrative artifact requiring a per-file approval packet at implementation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — FAB-05 relocates rule/automation files
  to **in-root** `archive/` directories and edits in-root rule files; it touches **no**
  `applications/` subtree and writes **no** out-of-root artifacts (this bridge file is
  under `E:\GT-KB\bridge\`). The retired content is *Agent-Red-era* by provenance, but
  the remediation is in-root archival/dedup — no application-placement change.

Governing rules (non-spec): `.claude/rules/bridge-essential.md` (the do-not-re-enable
authority the runbook contradicts); `.claude/rules/project-root-boundary.md` (the
`e:/Claude-Playground` link violates it); `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`.

## Isolation Placement Compliance

All FAB-05 edits and moves stay **in-root under `E:\GT-KB`**: the rule-file edits under
`.claude/rules/`, the archive destinations under `archive/os-poller-2026-04-25/` and
`independent-progress-assessments/archive/cursor-legacy/`, the archive source under
`independent-progress-assessments/bridge-automation/`, the test under
`platform_tests/scripts/`, the narrative-approval packets under
`.groundtruth/formal-artifact-approvals/`, and the doc fix under `groundtruth-kb/docs/`.
No `applications/` subtree is touched and no out-of-root artifact is created or required.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-018/026/027/038).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB05-REMEDIATION-20260610` — this cluster's owner-decision set (the 4 dispositions).
- _WI-4404 (Restore Scheduled Poller) is open, so the runbook is stubbed (pointing to it
  as the only sanctioned path back), not silently deleted; the orchestrator direction
  (`DELIB-BRIDGE-ORCHESTRATOR-VISION-20260610`) may later supersede WI-4404._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB05-REMEDIATION-20260610`:

1. **HYG-018 = Archive + DEPRECATED stub** — archive the 25 files to
   `archive/os-poller-2026-04-25/`; replace the runbook with a DEPRECATED stub citing
   `bridge-essential.md` + noting WI-4404; fix the `file-bridge-protocol.md:332,345` echoes.
2. **HYG-026 = Archive all four + fix index** — move the 4 Cursor/Agent-Red-era rule
   files to `independent-progress-assessments/archive/cursor-legacy/`; fix the index path.
3. **HYG-027 = One canonical home + pointers** — `report-depth.md` + `prime-builder-role.md`
   + a single contract block canonical; delete/pointer the duplicates; fix the mislabeled
   Severity Model heading; scope-note `prime-builder.md` vs `prime-builder-role.md`.
4. **HYG-038 = Repoint + fix WIs** — repoint Priority 1 to `gt backlog list`; retire/reword
   WI-3278 + WI-3465; fix the `v0.7.0-rc1.md:154` dead reference.

## Requirement Sufficiency

**Existing requirements sufficient.** Governed by `bridge-essential.md` (poller
retirement), `GOV-STANDING-BACKLOG-001` (backlog authority), `project-root-boundary.md`
(the Drive/Playground boundary), and `GOV-ARTIFACT-APPROVAL-001` (narrative packets); the
dispositions are fixed by `DELIB-FAB05-REMEDIATION-20260610`. No new requirement needed.

## Scope and Boundaries

In scope: the 4 dispositions above (archives, the DEPRECATED stub, the dedup/pointers,
the repoint, the doc/WI fixes). Out of scope: the open role-state prose-stripping work
item (a different concern); the broader orchestrator redesign (captured separately); any
poller *restoration* (forbidden — the stub points at WI-4404 only).

## Proposed Implementation

1. **HYG-018:** `git mv` / archive `independent-progress-assessments/bridge-automation/`
   → `archive/os-poller-2026-04-25/`; rewrite `bridge-permanent-operations-runbook.md` as
   a short DEPRECATED stub (mirroring `bridge-poller-canonical.md`'s pattern) citing
   `bridge-essential.md` + WI-4404; edit `file-bridge-protocol.md:332,345` to drop the
   stale "every 3 minutes" cadence.
2. **HYG-026:** move the 4 Cursor/Agent-Red-era rule files to
   `independent-progress-assessments/archive/cursor-legacy/`; correct
   `codex-knowledge-base-index.md:41-44` to the real archive path.
3. **HYG-027:** delete/pointer `report-depth-prime-builder-context.md`; remove the
   `codex-review-operating-contract.md:116-129` duplicate + rename/fill the Severity Model
   heading; replace the `acting-prime-builder.md` AUQ copy with a pointer to
   `prime-builder-role.md` (editing `prime-builder-role.md` only if needed to host the
   canonical block); add the `prime-builder.md` scope note.
4. **HYG-038:** repoint `codex-standing-priorities.md` Priority 1 to `gt backlog list`;
   retire/reword WI-3278 + WI-3465 via `kb-batch` dry-run + the GOV-15 gate; fix
   `v0.7.0-rc1.md:154`.

Each `.claude/rules/*.md` edit is preceded by its narrative-approval packet
(`.groundtruth/formal-artifact-approvals/*.json`) at implementation.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test (grep-absence / presence) |
|---|---|
| `bridge-essential.md` retirement | the runbook contains no PT3M mandate / repair commands (DEPRECATED stub only); `bridge-automation/` absent under `independent-progress-assessments/`; no "every 3 minutes" in `file-bridge-protocol.md` |
| `project-root-boundary.md` | no `e:/Claude-Playground` link in any active `.claude/rules/` file; no live `CURSOR-INSIGHT-DROPBOX` reference in active rules |
| `GOV-STANDING-BACKLOG-001` | `codex-standing-priorities.md` cites `gt backlog list`, not `memory/work_list.md`; WI-3278/WI-3465 resolved; no `work_list.md` ref in `v0.7.0-rc1.md` |
| HYG-027 dedup | the duplicated blocks appear once (single canonical + pointers); the Severity Model heading is no longer mislabeled |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | a `pytest`/grep-assertion test under `platform_tests/scripts/` encodes the above grep-absence checks |

## Acceptance Criteria

1. OS-poller stack archived; runbook is a DEPRECATED stub; no PT3M mandate loads.
2. The 4 Cursor/Agent-Red-era rule files archived; index path corrected; no
   `e:/Claude-Playground` link in active rules.
3. Duplicated normative blocks deduped to one canonical home + pointers; Severity Model
   heading fixed.
4. `codex-standing-priorities.md` repointed to `gt backlog list`; WI-3278/WI-3465
   retired/reworded; `v0.7.0-rc1.md:154` fixed.
5. Each rule edit has its narrative-approval packet; grep-absence test passes; ruff-clean.

## Backlog Visibility

WI-4417 is the governed backlog authority; the WI-3278/WI-3465 retire/reword runs through
`kb-batch` dry-run under the GOV-15 gate with formal-artifact-approval evidence (no silent
bulk mutation).

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-05-rule-file-retirement-003.md` with a matching `REVISED` entry
inserted at the top of the `gtkb-fab-05-rule-file-retirement` entry in `bridge/INDEX.md`;
append-only, no prior bridge version deleted or rewritten. The poller-runbook retirement is
a rule-text change; it does not alter `bridge/INDEX.md` as canonical workflow state or the
bridge versioning discipline (`GOV-FILE-BRIDGE-AUTHORITY-001` preserved). It removes a rule
that *contradicted* the bridge governance, strengthening it.

## Risk and Rollback

- **Risk:** archiving a rule that an external reference depends on → archives preserve the
  files (recoverable); the DEPRECATED stub keeps the runbook path stable; WI-4404 noted.
- **Risk:** a dedup pointer breaks a cross-reference → grep-absence + presence tests cover
  the canonical homes; pointers follow the proven CLAUDE.md L211 pattern.
- **Rollback:** restore the archived files from `archive/`; revert the rule edits (each is
  a discrete narrative-packet change); re-open WI-3278/WI-3465. No live-DB data loss.

## Recommended Implementation Routing

**Opus/Codex-supervised** — protected-narrative edits to governance rule files + a
KB mutation; not a cheap-model candidate. Each edit is gated by its narrative-approval
packet (owner acknowledgement) regardless of which model implements.

## Recommended Commit Type

`docs:` — governance/rule-file retirement + dedup + repoint (with `chore:`-class archive
moves and a `fix:`-class boundary-link removal).
