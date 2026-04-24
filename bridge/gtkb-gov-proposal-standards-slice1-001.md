NEW

# GTKB-GOV Proposal Standards — Slice 1: Required Section Enforcement (Upstream-Routed)

**Status:** NEW
**Date:** 2026-04-24
**Work item:** GTKB-GOV-PROPOSAL-STANDARDS (new standing-backlog item)
**Author:** Prime Builder (Claude Sonnet 4.6, S306)
**Priority slot:** parallel to upstream `gtkb-da-governance-completeness-implementation`; adoption in Agent Red follows its VERIFIED + next `gt project upgrade`.

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`:

- `DELIB-0830` / `GOV-ACTING-PRIME-BUILDER-001` — precedent that governance
  rules must be mechanically enforced, not procedurally asserted.
- `DELIB-0836` / `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — hook-based governance
  pattern with Windows-compatible fallback verifier.
- `DELIB-0838` / `GOV-STANDING-BACKLOG-001` — standing-backlog authority (this
  is a tracked entry).
- `DELIB-0841` / `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` — session
  lifecycle hook authority (the surface this hook attaches to).
- `bridge/agent-red-session-wrap-automation-004.md:17-21,63-69,83-89,105` —
  **binding prior ruling** that GT-KB governance hook / template / scaffold
  / upgrade / test work routes through upstream GT-KB managed-artifact
  threads, not through new parallel Agent Red-local hook authority. This
  proposal complies with that ruling from the outset (unlike the withdrawn
  `gtkb-gov-da-enforcement-slice1-001`).
- No prior deliberation exists for proposal-structure enforcement
  specifically. Thread is net-new.

---

## 1. Problem Statement

`.claude/rules/file-bridge-protocol.md` and the observed review workflow
define an informal structure for implementation proposals:

1. `## Prior Deliberations` (covered by upstream `hook.delib-preflight-gate`).
2. `## Verification Matrix` — risk/evidence table mapping scope to tests.
3. `## Files Touched` — **New**, **Modified**, and **Not touched** subsections.
4. `## Out of Scope` — explicit boundary + follow-on bridge names.
5. `## Decision Needed From Owner` — "None" or itemized.
6. `## Cross-NO-GO Discipline` table on REVISED proposals — shows how every
   prior NO-GO finding is addressed.
7. Test-evidence blocks with real pytest output on post-implementation
   reports.

None of these are mechanically enforced. **Audit evidence (S306,
2026-04-24)** across 14 NO-GO findings this session:

| Failure class | Count | Example NO-GO |
|---|---|---|
| Missing/incomplete scope boundary | 3 | Phase 7 -004 "full integration" vs delivered scope |
| Unverified test claim in post-impl | 1 | Phase 7 -010 "44 tests pass" vs "7 failed, 16 passed" live |
| Work item ID collision (wrong follow-on target) | 1 | Phase 7 -006 routing §D to already-assigned -016 |
| Verification-matrix row cites wrong test | 2 | Phase 7 -010/-012 counterpart-subject row |
| Targeted generated artifact instead of generator | 1 | Dashboard -002 Grafana JSON direct edit |
| Non-existent metric/path name | 2 | Dashboard -004 alert metric keys; DA-enforcement -002 `run_quality_guardrails.py` |
| Forked enforcement family already centralized | 1 | DA-enforcement -002 competing with existing GT-KB managed hook |

Total preventable by proposal-structure enforcement: **11 of 14** (79%).

## 2. Scope: Upstream-Owned Managed Hook

**Implementation is owned upstream** in `groundtruth-kb` as a new managed
artifact `hook.bridge-proposal-standards`. This Agent Red bridge is a
**scope and adoption contract** — it defines what the hook must check,
commits Agent Red to adopting via `gt project upgrade` when upstream
VERIFIED, and records the S306 audit evidence as motivation. No Agent
Red code changes land in this bridge.

### 2.1 New upstream managed artifact

Filed as part of the upstream bridge (out of this Agent Red thread's scope):

- `groundtruth-kb/templates/hooks/bridge-proposal-standards-gate.py` — author-time
  `UserPromptSubmit` + `PreToolUse(Write,Edit)` hook. Inspects the file path
  being authored; when the target matches `bridge/<slug>-NNN.md` and the
  file content header is `NEW` or `REVISED`, validates required-section
  presence and emits a system-message checkpoint if any are missing.
- `groundtruth-kb/templates/managed-artifacts.toml` — register
  `hook.bridge-proposal-standards` with settings registrations on
  `UserPromptSubmit` and `PreToolUse`.
- `groundtruth-kb/tests/test_scaffold_settings.py` — extend existing
  hook-presence assertions to cover the new hook.
- `groundtruth-kb/tests/hooks/test_bridge_proposal_standards.py` — new.
  Required test cases enumerated in §4 below.

### 2.2 Required sections the hook enforces

| Section | Applies to | Content requirement |
|---|---|---|
| `## Prior Deliberations` | All NEW/REVISED | Handled by the separate `hook.delib-preflight-gate`; this hook does NOT re-check. |
| `## Verification Matrix` | NEW/REVISED proposals | Must contain a Markdown table with at least 3 rows; each row must have ≥2 columns; second column must be non-empty (cannot be "TBD" / "TODO" / empty). |
| `## Files Touched` | NEW/REVISED | Must contain `**New:**` + `**Modified:**` + `**Not touched:**` subsections. Each subsection may be "(none)" but must be present. |
| `## Out of Scope` | NEW/REVISED | Must be present and non-empty. "None" acceptable. |
| `## Decision Needed From Owner` | ALL | Must be present. "None" acceptable. |
| `## Cross-NO-GO Discipline` | REVISED only | Required when the file status header is `REVISED`. Must contain a Markdown table with ≥1 row. Each row's "This revision" column must be non-empty and non-TBD. |
| `## Test Evidence` with fenced pytest block | Post-impl NEW (header `NEW` AND filename contains `post-implementation` or the file content contains `Implements proposal:`) | Must contain at least one fenced code block that starts with `python -m pytest` and ends with a line matching `\d+ passed`. |

### 2.3 Hook behavior

- **Soft checkpoint (not hard block)**: emits a `systemMessage` listing which
  sections are missing; author can override by explicit text in a second
  pass. Design parallel to `bridge-compliance-gate.py`.
- **Skips**: LO review files (header `GO`/`NO-GO`/`VERIFIED`), `bridge/INDEX.md`,
  any non-`bridge/` file.
- **Windows-compatible fallback verifier** pattern from
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — same shape as
  `check_codex_hook_parity.py` for the `.codex` adapter surface.

---

## 3. Agent Red Adoption Contract

- When the upstream thread VERIFIED lands, Agent Red runs `gt project upgrade`
  (or equivalent) to pull the hook file, settings.json registration, and
  scaffold-test expectations. No new Agent Red-local files.
- The backlog entry `GTKB-GOV-PROPOSAL-STANDARDS` (added in this bridge's
  commit) tracks the upstream thread. When upstream closes, the Agent Red
  entry closes too.
- **Interim Agent Red override**: not planned by default. If the owner
  wants interim local enforcement before upstream lands, it would require
  a new bridge proposal with explicit retirement criteria.

---

## 4. Verification Matrix (for the upstream implementation)

| Risk | Test requirement (to land upstream) |
|------|-----------------|
| Hook fires on LO review files it shouldn't touch | `GO`/`NO-GO`/`VERIFIED` file first-line → skipped. |
| Hook fires on `bridge/INDEX.md` edits | INDEX.md path → skipped. |
| NEW proposal without Verification Matrix | → checkpoint emitted, section listed. |
| REVISED without Cross-NO-GO Discipline table | → checkpoint emitted, section listed. |
| Proposal with "TBD" / "TODO" in Verification Matrix cells | → checkpoint emitted, row index listed. |
| Post-impl report without Test Evidence block | → checkpoint emitted. |
| Post-impl report with Test Evidence block that has no `\d+ passed` line | → checkpoint emitted. |
| Compliant proposal (all sections present) | → no checkpoint. |
| Windows `.codex` adapter parity (fallback verifier) | Same pattern as existing `check_codex_hook_parity.py`. |
| Scaffold-test coverage | Upstream `tests/test_scaffold_settings.py` asserts the hook is registered on `UserPromptSubmit` and `PreToolUse`. |

---

## 5. Files Touched

**New (Agent Red side):** none.

**Modified (Agent Red side):**
- `memory/work_list.md` — adds `GTKB-GOV-PROPOSAL-STANDARDS` backlog entry
  pointing at the upstream implementation thread and the S306 audit
  evidence that motivates it.

**Not touched (Agent Red side):**
- `.claude/hooks/` — nothing new, nothing modified.
- `.claude/settings.json` — unchanged.
- `scripts/`, `tests/`, `src/` — unchanged.

**Out of scope — upstream work (to be filed separately in groundtruth-kb):**
- `groundtruth-kb/templates/hooks/bridge-proposal-standards-gate.py` (new).
- `groundtruth-kb/templates/managed-artifacts.toml` (new hook registration).
- `groundtruth-kb/tests/test_scaffold_settings.py` (presence assertion).
- `groundtruth-kb/tests/hooks/test_bridge_proposal_standards.py` (new).

---

## 6. Out of Scope

- Upstream `groundtruth-kb` implementation — filed separately there; this
  Agent Red bridge does not commit that repo.
- Test-claim re-run verifier (parses claimed pytest output blocks and
  re-runs them) — filed as follow-on `gtkb-gov-proposal-standards-slice2`.
- Work-item-ID collision gate (cross-references proposal routing targets
  against `work_list.md`) — filed as follow-on
  `gtkb-gov-proposal-standards-slice3`.
- `/gtkb-propose` skill that scaffolds a compliant proposal — filed as
  follow-on `gtkb-gov-proposal-standards-slice4` (skill, not hook).
- DA-citation enforcement — owned by upstream
  `gtkb-da-governance-completeness-implementation`
  (`hook.delib-preflight-gate`), not this thread.

---

## 7. Decision Needed From Owner

**One optional question:** do you want an Agent Red-local interim hook
before the upstream thread lands? Default recommendation: **No** — wait
for upstream. The same reasoning that applied to DA-enforcement applies
here: the fix belongs in GT-KB's managed-artifact family where it
propagates to all adopters, not as a local hook that would need to be
retired.

Otherwise: none. Awaiting Loyal Opposition GO, after which the Agent Red
backlog entry + adoption contract land in a single commit. Actual hook
implementation happens upstream.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
