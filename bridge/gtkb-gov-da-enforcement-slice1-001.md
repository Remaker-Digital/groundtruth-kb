NEW

# GTKB-GOV Deliberation Archive Enforcement — Slice 1: Pre-Commit Gate

**Status:** NEW
**Date:** 2026-04-24
**Work item:** GTKB-GOV-DA-ENFORCEMENT (new standing-backlog item)
**Author:** Prime Builder (Claude Sonnet 4.6, S306)
**Priority slot:** queued after `GTKB-ISOLATION-015` Slice 2; ahead of
`GTKB-ISOLATION-016` Phase 8 execution.

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, this proposal searched the DA
for prior governance enforcement decisions:

- `DELIB-0830` / `GOV-ACTING-PRIME-BUILDER-001` — role-assignment
  durability (establishes that rules must be mechanically enforced, not
  procedurally asserted).
- `DELIB-0836` / `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — precedent for
  hook-based governance with Windows-compatible fallback verifiers.
- `DELIB-0838` / `GOV-STANDING-BACKLOG-001` — standing-backlog authority
  (this item becomes a tracked backlog entry).
- No prior deliberation exists specifically for DA-citation enforcement or
  for `bridge/*.md` pre-commit gates. This thread is net-new.

---

## 1. Problem Statement

`.claude/rules/deliberation-protocol.md` mandates that:

1. **Prime Builder** must `search_deliberations()` before writing a bridge
   proposal and cite DELIB-IDs in a `## Prior Deliberations` section.
2. **Loyal Opposition** must search deliberations before reviewing, and
   add a Prior Deliberations section to reviews.
3. Both agents must archive owner decisions immediately as
   `source_type=owner_conversation`.

**Observed compliance (S306 audit, 2026-04-24):**

| Actor | Rule | Compliance |
|---|---|---|
| Prime Builder | Pre-proposal DELIB search + citation | **0 of 7 proposals this session cited DELIBs** (`gtkb-isolation-015` -001, -003, -005, -007, -009, -011; `gtkb-dashboard-industry-alignment-slice1` -001). |
| Loyal Opposition | Pre-review DELIB search + citation | Codex cited DELIBs in `gtkb-isolation-015` -002 (DELIB-0876/0877/0878/0879). Intermittent on later reviews. |
| Either agent | Immediate owner-decision archival | Only 1 `owner_conversation` DELIB captured 2026-04-24; at least 3 owner decisions occurred in this session (Slice 1/Slice 2 scope strategy; commit-to-main-vs-develop; dashboard Slice 1 approval). |

**Baseline DA statistics (as of 2026-04-24):**
- Total DELIBs: 914 (up from 710 in prior MEMORY snapshot).
- `source_type` mix: 71% `lo_review` (649 from one WI-3162 batch backfill),
  23% `bridge_thread` (mostly session-wrap harvest), 5% `owner_conversation`
  (49 total).
- DELIBs with `work_item_id`: 12% (106 of 914).
- DELIBs with `spec_id`: 18% (169 of 914).
- Organic daily capture rate: 2–20/day, punctuated by batch backfills.

**Root cause:** the protocol exists in a read-on-demand rules file. No
mechanical enforcement exists. A documentation-only rule does not survive
contact with the bridge hot-loop, especially on the Prime side where drafting
velocity is high.

**Risk:** without citation discipline, bridge proposals lose continuity with
prior rejected alternatives and owner decisions. Future agents (including
fresh sessions) cannot trace *why* a decision was made. The DA exists but
functions closer to a write-only archive than a living deliberation record.

---

## 2. Slice 1 Scope: Pre-Commit Gate

This slice delivers the **minimum mechanical enforcement** that produces
measurable behavior change without requiring a full DA-linkage backfill or
runtime tooling.

### A. Pre-commit hook `.claude/hooks/require-prior-deliberations.py`

Behavior:

1. On every `git commit` that touches a `bridge/*.md` file (not `INDEX.md`),
   inspect the file's header and content.
2. Only enforce on files whose first non-blank line is `NEW` or `REVISED`
   (Prime-authored). `GO`, `NO-GO`, `VERIFIED` files are LO-authored and
   live under a separate rule track already partially met by Codex.
3. Require the file to contain a `## Prior Deliberations` section **and** at
   least one `DELIB-` reference **or** an explicit opt-out statement:
   `No prior deliberations found for <topic>.` (matches the protocol's
   prescribed opt-out language).
4. On violation: print the file path, the rule source
   (`.claude/rules/deliberation-protocol.md`), and the required section
   template. Exit non-zero. Respect `--no-verify` the same way other hooks
   do — do not silently bypass.
5. Skip files under `bridge/` that match the LO side
   (`bridge/*-{GO,NO-GO,VERIFIED}-*.md` equivalents are detected by content
   header, not filename, since the project's file naming is version-indexed
   not status-indexed).

### B. Wire into the existing pre-commit chain

- Add to `scripts/pre_commit/run_quality_guardrails.py` (or equivalent)
  alongside the existing gates: Test deletion guard, Assertion ratchet,
  Architectural guards, Credential scan, TSX commit gate.
- The new gate reports `[PASS]` or `[FAIL]` in the same style.

### C. Tests

`tests/hooks/test_require_prior_deliberations.py` covers:

- File with `## Prior Deliberations` + `DELIB-NNNN` → PASS.
- File with `## Prior Deliberations` + explicit opt-out sentence → PASS.
- File without `## Prior Deliberations` → FAIL with actionable message.
- File with `## Prior Deliberations` but no citations or opt-out → FAIL.
- `bridge/INDEX.md` edits → SKIPPED (not a proposal file).
- LO review files (first line `GO`/`NO-GO`/`VERIFIED`) → SKIPPED by this
  hook (covered by Slice 2).
- Non-`bridge/` files → SKIPPED.

### D. Backlog entry in `memory/work_list.md`

Add new entry `GTKB-GOV-DA-ENFORCEMENT` documenting the 3-slice plan, the
Slice 1 scope of this bridge, and the DA-audit baseline that motivated it.

### E. Retrospective self-citation

Not in this slice. After this gate lands, any subsequent Prime proposal
must include the section; the gate back-fills going forward but does not
retroactively amend existing bridge files (audit trail is append-only).

---

## 3. Out of Scope for This Bridge

Filed as follow-on bridges after Slice 1 VERIFIED:

- **`gtkb-gov-da-enforcement-slice2`** (Prime-side assistance):
  `UserPromptSubmit` hook that detects when Prime is about to author a
  bridge file and prompts for a DELIB search; an `archive-owner-decision`
  helper that detects AskUserQuestion outputs and records the decision as
  `source_type=owner_conversation` DELIB.
- **`gtkb-gov-da-enforcement-slice3`** (LO-side enforcement + backfill):
  equivalent pre-commit gate for LO review files; retroactive backfill
  pass that scans historical bridge files for implicit DELIB references and
  adds linkage rows to the DA. Adds a dashboard tile for "DELIB capture
  rate last 7 days".
- **`gtkb-gov-da-linkage-uplift`**: backfill `work_item_id` and `spec_id`
  linkage on existing DELIBs so `search_deliberations(work_item_id=...)`
  is not mostly empty.

---

## 4. Implementation Sequence

1. Write `.claude/hooks/require-prior-deliberations.py`.
2. Write `tests/hooks/test_require_prior_deliberations.py` (7+ cases above).
3. Wire into `scripts/pre_commit/run_quality_guardrails.py`.
4. Add `GTKB-GOV-DA-ENFORCEMENT` entry to `memory/work_list.md`.
5. Verify lane GREEN; ensure existing pre-commit gates still fire and the
   new gate fires only on Prime-authored bridge files.
6. Self-dogfood: this bridge proposal (`-001`) already contains a
   Prior Deliberations section, so the gate passes on its own file at
   the same commit that introduces the gate.
7. Post-impl report.

---

## 5. Verification Matrix

| Risk | Test requirement |
|------|-----------------|
| Gate fires on LO review files it shouldn't touch | Test: `GO`/`NO-GO`/`VERIFIED` file first-line → skipped. |
| Gate fires on `bridge/INDEX.md` edits | Test: INDEX.md path → skipped. |
| Gate misses a missing-section case | Test: NEW file without section → FAIL. |
| Gate fires false-positive on opt-out | Test: NEW file with opt-out sentence → PASS. |
| Gate bypass via --no-verify is silent | Hook output explains what was checked and points at the rule file even when exit is non-zero; user can deliberately bypass but the decision is visible. |
| Gate breaks the existing pre-commit chain | All 5 existing gates (Test deletion, Assertion ratchet, Architectural, Credential, TSX) still produce their `[PASS]` lines. |
| Performance regression on large commits | Gate only reads `bridge/*.md` files whose name matches the version-indexed pattern; skips all other commit content. Timing < 100 ms on this repo. |

---

## 6. Files Touched

**New:**
- `.claude/hooks/require-prior-deliberations.py`
- `tests/hooks/test_require_prior_deliberations.py`

**Modified:**
- `scripts/pre_commit/run_quality_guardrails.py` (or equivalent gate chain)
- `memory/work_list.md` (add `GTKB-GOV-DA-ENFORCEMENT` entry)

**Not touched:**
- Any `bridge/*.md` files (audit trail append-only).
- DA schema / `groundtruth.db` (no backfill this slice).
- `src/`, `tests/integrations/`, upstream `groundtruth-kb/`.

---

## 7. Decision Needed From Owner

**None for approval.** Owner has already directed (this session) that the
bridge proposal should be filed and queued after GTKB-ISOLATION-015 Slice 2
and before GTKB-ISOLATION-016 Phase 8 execution.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
