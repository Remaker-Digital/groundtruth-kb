NEW
author_identity: prime-builder/cursor
author_session_context_id: cursor-e-20260628-orientation-gate-pb

# GT-KB Session-Start Orientation Gate

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17 (S300)
**Scope:** GT-KB product (templates + doctor + adopter inheritance). Zero Agent Red writes.
**Sequencing:** **BLOCKED** on `gtkb-da-governance-completeness-implementation-016` VERIFIED. Do not schedule Codex review or Prime implementation of this proposal until that thread completes. Rationale: governance-completeness in flight owns the session-start `UserPromptSubmit` hook tier; forking scope now risks merge-conflict surface in that thread's hook registration.

## Summary

Introduce a mandatory 7-item **ORIENT block** at session start, mirroring the discipline of the POLLER block. Produced once per session (after memory read + bridge scan, before first substantive work). Each answer sourced from a live command (git, bridge/INDEX.md, DA search, gh run list). Static questionnaires banned — ORIENT is structurally incapable of stale-answer drift because inputs are live.

Add an extended **baseline-audit skill** (`/baseline-audit`) triggered by explicit owner request via keyword family ("baseline status", "release readiness", "production readiness", "project handoff", "baseline audit", "where do we stand", "full status").

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, DA searched before drafting:

- **Owner conversation 2026-04-17 S300 evening** (will be archived as `DELIB-S300-002` prior to Codex review of this bridge): two-tier design settled after rejecting a 25-50 item questionnaire proposal. Owner directive: "At session start, after bridge obligations are clear, run the short orientation checklist. If the user asks for baseline status, release readiness, production readiness, or project handoff, run the extended baseline audit checklist and answer with evidence class..."
- `DELIB-0715` (MemBase canonical definition) — establishes the live-source / authoritative-truth split that ORIENT block leverages.
- `DELIB-0820` (S299 final wrap) — framing of session-start orientation as the carryover-fidelity problem the wrap-side hooks address.
- `gtkb-da-governance-completeness-implementation-016` GO — owns `UserPromptSubmit` hook tier; this proposal coordinates with that thread via the blocking-sequence note above.

No prior deliberation rejects the two-tier approach.

## Motivation

S290-S294 silent POLLER failure, S294 `.gitignore` blanket-ignore bypass, S296 SPEC-1834 promotion without bridge: all rooted in **procedural governance failing silently under context pressure**. S299 diagnosis: "encoded is not enforced." A 25-50 item questionnaire would regress to that tier. The two-tier design (mandatory short gate + on-demand extended audit) solves the orientation problem without the stale-answer failure mode.

## Scope

### In scope

1. **ORIENT block directive** in `templates/CLAUDE.md` and `templates/project/AGENTS.md` (profiles: all). Directive text + output format spec.
2. **`/baseline-audit` skill** in `templates/skills/baseline-audit/SKILL.md` — on-demand extended audit with evidence-class tagging.
3. **Doctor check** `_check_session_wrap_had_orient()` that scans the previous session's last transcript turn (via `~/.claude/projects/<hash>/history/` or equivalent) for the ORIENT block. Mechanical enforcement: the NEXT session at bootstrap sees whether the PREVIOUS session properly terminated with orientation evidence.
4. **Managed-artifact registry entries** for the new skill (class `skill`, flat-field ownership metadata per `gt-kb-managed + overwrite + warn`) and the doctor config (class `rule`).
5. **Scaffold inheritance** — every fresh `gt project init` scaffolds the ORIENT directive + `/baseline-audit` skill.
6. **Upgrade path** — `gt project upgrade --apply` installs the new artifacts on existing adopter projects via the existing `_plan_missing_managed_files` registry-driven path.
7. **Tests:** ORIENT format validator, baseline-audit skill smoke, doctor check unit tests (3 profiles × ORIENT-present / ORIENT-missing / ORIENT-malformed × expected-severity), managed-artifact registry parse tests for the new rows.

### Out of scope

- Orientation-block content *inside* MEMORY.md (different problem — memory-density, handled by `memory-density-remediation` if filed).
- Replacing the POLLER block (ORIENT coexists; POLLER is per-turn, ORIENT is per-session).
- Back-populating ORIENT into historical sessions (the block is a going-forward discipline).
- Agent Red adoption (separate follow-on bridge filed AFTER VERIFIED of this).

## Proposed Files

### New

- `templates/skills/baseline-audit/SKILL.md` — extended audit skill. Output format: 29-item table with evidence class per item. Keyword triggers documented.
- `templates/rules/session-start-orientation.md` — ORIENT block format spec + live-source rules.
- `tests/test_session_start_orientation_doctor.py` — doctor check unit tests.
- `tests/test_baseline_audit_skill.py` — skill smoke tests.

### Modified

- `templates/CLAUDE.md` (all profiles) — add "Session Start: ORIENT Block (Mandatory)" subsection, 7-item format spec, live-source rule.
- `templates/project/AGENTS.md` (dual-agent profiles) — parallel directive for Codex / Loyal Opposition session start.
- `templates/managed-artifacts.toml` — 2 new rows (skill.baseline-audit, rule.session-start-orientation) with flat-field ownership metadata.
- `src/groundtruth_kb/project/doctor.py` — add `_check_session_wrap_had_orient()` function + wire into `check_project()`.
- `CHANGELOG.md` — `[Unreleased]` §Added subsection.

### Deleted

None.

## ORIENT Block Format Specification

Verbatim format (to be encoded in `templates/rules/session-start-orientation.md`):

```
ORIENT S{N} @ HH:MMZ
  1 bridge:     <status>                                  # bridge/INDEX.md head scan
  2 branch:     <repo>@<sha-short>  (<ahead/behind N>)    # git rev-parse + git status -sb
  3 worktree:   <N modified, M untracked>  [relevant: <scoped subset>]
  4 wrap:       DELIB-<id> / INSIGHTS-<date>-<topic>.md   # DA search + LO dropbox latest
  5 blockers:   <list or 'none'>                          # active NO-GO + GO-unverified + release-blocking
  6 refresh:    <list or 'none'>                          # evidence that must be refreshed
  7 next:       <action>                                  # synthesis of 1-6
```

**Live-source requirement:** Every answer must be obtained from a live command in the current session's first turn. If a live source cannot be obtained, mark `UNKNOWN — <reason>` rather than infer from memory.

**Count is exactly 7, not a range.** Pinned count makes cross-session comparison grep-friendly and makes skipped items visually obvious.

## Doctor Check Semantics

`_check_session_wrap_had_orient()` semantics:

- **Data source:** Scans the most recent session transcript at `~/.claude/projects/<hash>/history/` (or equivalent harness-resolved path per ADR-0001). If transcript access unavailable (harness not running, permission denied), return `WARN` with explanatory message, not `ERROR` (doctor should not false-positive on valid "can't check" states).
- **Pass condition:** Last session's final Prime turn contains a well-formed ORIENT block at the top, with all 7 items answered (or marked `UNKNOWN`).
- **ERROR:** Last session's final turn exists but has no ORIENT block. Indicates the previous session skipped the mandate.
- **WARN:** Transcript access unavailable or malformed ORIENT (count != 7, missing items, unknown format).
- **INFO:** No prior session transcript found (first-ever session on this machine).

## Tests

At minimum:

- `test_orient_block_format_parses_well_formed` — valid format accepts 7 items.
- `test_orient_block_format_rejects_count_mismatch` — 6 or 8 items fails validation.
- `test_orient_block_format_rejects_malformed_header` — header must match `ORIENT S\d+ @ \d+:\d+Z`.
- `test_doctor_warns_on_transcript_unavailable` — permission-denied scenario.
- `test_doctor_errors_on_missing_orient_in_prior_session` — prior session transcript present, no ORIENT.
- `test_doctor_passes_on_well_formed_prior_orient` — full golden-path.
- `test_baseline_audit_skill_triggers_on_keyword_family` — "baseline status", "release readiness", etc.
- `test_baseline_audit_evidence_class_tagging` — each answer includes one of the 6 evidence classes.
- `test_managed_registry_includes_new_orientation_rows` — 44 total (42 + 2 new: rule.session-start-orientation + skill.baseline-audit).

## Adopter Rule Compliance

All governance + hook + doctor + scaffold artifacts land in GT-KB as product. Zero Agent Red writes. Agent Red inherits via `gt project upgrade --apply` as a **separate downstream bridge** filed AFTER this thread VERIFIED.

Per `feedback_agent_red_is_adopter_not_author.md`: "When drafting any bridge proposal, before writing scope, ask: 'Who else would benefit from this fix?' If the answer is 'every GT-KB adopter' or 'every project using this pattern', scope is GT-KB product." Answer here: every adopter benefits, therefore GT-KB product scope.

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| ORIENT block becomes a ritual skipped under pressure | Mechanical doctor check validates prior session produced one; missing ORIENT = ERROR next session |
| `UNKNOWN` usage inflates over time (escape hatch) | Test coverage: count of `UNKNOWN` items trend-tracked; alert if >20% of items in a session are UNKNOWN |
| Transcript access varies by harness | Doctor returns WARN (not ERROR) on unavailable; `INFO` on first-ever session |
| Extended audit triggers too aggressively on keyword family | Skill prompt clarifies: "If unsure, produce short audit only and confirm with owner before running full" |
| Scope duplicates wrap-side governance-completeness hooks | Explicit blocking-sequence on that thread VERIFIED; coordinated hook-tier ownership |

## Sequencing (Hard Block)

**Do not schedule Codex review of this bridge until `gtkb-da-governance-completeness-implementation-016` is VERIFIED.** Rationale above. After that thread VERIFIED, Prime updates this bridge's status line to indicate readiness and Codex enters review cycle.

## Open Questions for Codex Review (post-unblock)

1. Should the doctor check path-resolution use the existing `harness-memory` profile convention for locating the transcript, or introduce a new `harness-history` concept?
2. Is `UNKNOWN` an acceptable escape hatch, or should the format instead require a reason-tag like `UNKNOWN:<category>` (e.g., `UNKNOWN:no-remote-access`, `UNKNOWN:first-session`)?
3. Should the extended audit skill enforce evidence-class tagging at format level (reject an audit output missing class tags), or accept Prime's self-discipline?
4. Trigger phrase detection: keyword family is Prime's judgment (proposal position) vs. explicit list exact-match (conservative). Codex opinion welcomed.
5. Should `/baseline-audit` be also runnable by Codex (Loyal Opposition) with a different question set, or is it Prime-only?

## Next Step

Bridge stays NEW pending governance-completeness VERIFIED. No Codex action requested yet.


## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- ADR-0001
- GOV-DOCUMENT-AUTHOR-PROVENANCE-001

## Requirement Sufficiency

Existing requirements sufficient. The two-tier orientation design is settled in owner conversation S300 and feedback memory/feedback/feedback_session_start_orient_block.md. No new governed specification is required before this product-template and doctor enforcement slice.

## target_paths

```json
[
  "groundtruth-kb/templates/rules/session-start-orientation.md",
  "groundtruth-kb/templates/skills/baseline-audit/SKILL.md",
  "groundtruth-kb/templates/CLAUDE.md",
  "groundtruth-kb/templates/project/AGENTS.md",
  "groundtruth-kb/templates/managed-artifacts.toml",
  "groundtruth-kb/src/groundtruth_kb/project/session_start_orientation.py",
  "groundtruth-kb/src/groundtruth_kb/project/baseline_audit.py",
  "groundtruth-kb/src/groundtruth_kb/project/doctor.py",
  "groundtruth-kb/tests/test_session_start_orientation_doctor.py",
  "groundtruth-kb/tests/test_baseline_audit_skill.py",
  "groundtruth-kb/tests/test_managed_registry.py",
  "groundtruth-kb/CHANGELOG.md"
]
```

## Specification-derived verification plan

- python -m pytest groundtruth-kb/tests/test_session_start_orientation_doctor.py -q
- python -m pytest groundtruth-kb/tests/test_baseline_audit_skill.py -q
- python -m pytest groundtruth-kb/tests/test_managed_registry.py::test_registry_total_matches_current_manifest -q
- python -m pytest groundtruth-kb/tests/test_managed_registry.py::test_registry_class_counts_match_proposal -q

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
