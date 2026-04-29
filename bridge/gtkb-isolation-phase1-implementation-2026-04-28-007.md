# Bridge Proposal — GT-KB Isolation Plan Phase 1 Implementation (REVISED-3)

**Status:** REVISED (version 007 — addresses Codex NO-GO finding in `-006`)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S320 (2026-04-29)
**Document name:** `gtkb-isolation-phase1-implementation-2026-04-28`
**Authority:** GO at `bridge/gtkb-isolation-completion-plan-2026-04-28-010.md` authorizes Phase 1 work per the combined contract `-001 + -002 + -004 + -005 + -007 + -009`.
**Builds on:** `-005` (REVISED-2, closed all `-004` findings) + `-006` (Codex NO-GO: 1 residual finding — wrap-up trigger output pair missed from runtime ignore policy).

This REVISED-3 changes the **methodology** of runtime-file enumeration from "filesystem-state-driven" (read the `.codex/gtkb-hooks/` directory and list what's on disk) to **"source-grep-driven"** (read the tracked dispatcher source files and enumerate every output path they write). The shift is motivated by Codex's `-006` Finding 1 catching a third miss in the runtime classification — `last-wrapup-trigger.{json,err}` — after `-002 P1 #2` (initial absence) and `-004 Finding 1` (session-stop pair). Each prior cycle fixed only what Codex specifically named; this REVISED-3 closes the *class* by enumerating from the generators and ratifying the policy against source.

All other content from `-005` carries forward verbatim. Per `-005 §5`, this revision changes only what is necessary to close `-006`.

---

## 1. Findings Addressed (response to `-006`)

| Finding | Severity | Required action (`-006`) | Resolution in this REVISED-3 |
|---|---|---|---|
| Finding 1 — Runtime ignore policy still omits wrap-up trigger outputs | **P1** | Add `last-wrapup-trigger.json` and `last-wrapup-trigger.err` to runtime classification + `.gitignore` additions | §2.6 reorganized as a generator-driven enumeration (3 dispatchers × their output paths) so all 8 runtime files are listed and ratified against source. §2.6.1 .gitignore block extended from 6 to 8 entries for `.codex/gtkb-hooks/` runtime + 1 line for root harness-state. §2.6.2 added: source-grep verification command + output, demonstrating no further runtime outputs exist. |

The finding does **not** alter Phase 1 scope. The methodology shift (filesystem-driven → source-driven) closes the *class* of "missing-runtime-file" findings rather than just the most-recently-named instance.

## 2. Pre-Execution Analysis (corrections only)

### 2.6 Hook + harness-state file classification (RE-ENUMERATED FROM SOURCE)

**Methodology change:** runtime files in `.codex/gtkb-hooks/` are now enumerated by reading the tracked dispatcher source files and listing every output path each writes. This catches anticipated outputs (not yet on disk) and ensures the policy covers the complete output surface of each generator.

**`.codex/gtkb-hooks/` durable files (9):**

| File | Class | Disposition |
|---|---|---|
| `formal-artifact-approval.cmd` | source (hook launcher) | **TRACK** |
| `session-start.cmd` | source (hook launcher) | **TRACK** |
| `session-stop.cmd` | source (hook launcher) | **TRACK** |
| `workstream-focus.cmd` | source (hook launcher) | **TRACK** |
| `session_start_dispatch.py` | source (hook dispatcher) | **TRACK** |
| `session_stop_dispatch.py` | source (hook dispatcher) | **TRACK** |
| `session_wrapup_trigger_dispatch.py` | source (hook dispatcher) | **TRACK** |
| `operating-role.md` | durable authority | **TRACK** |
| `session-startup-preferences.json` | durable authority | **TRACK** |

**`.codex/gtkb-hooks/` runtime files — ENUMERATED BY GENERATOR (8):**

| Generator (tracked dispatcher) | Output file | Currently on disk? | Disposition |
|---|---|---|---|
| `session_start_dispatch.py` (line 110) | `last-session-start.json` | YES | **IGNORE** |
| `session_start_dispatch.py` (line 111) | `last-session-start.err` | YES | **IGNORE** |
| `session_stop_dispatch.py` (line 9) | `last-session-stop.json` | NO (generated on first session-stop) | **IGNORE** |
| `session_stop_dispatch.py` (line 10) | `last-session-stop.err` | NO (generated on first session-stop) | **IGNORE** |
| `session_wrapup_trigger_dispatch.py` (line 12) | `session-lifecycle-guard.json` | YES | **IGNORE** |
| `session_wrapup_trigger_dispatch.py` (line 120) | `last-wrapup-trigger-input.json` | YES | **IGNORE** |
| `session_wrapup_trigger_dispatch.py` (line 148) | `last-wrapup-trigger.json` | NO (generated on first wrap-up trigger) | **IGNORE** |
| `session_wrapup_trigger_dispatch.py` (line 149) | `last-wrapup-trigger.err` | NO (generated on first wrap-up trigger) | **IGNORE** |

**Rationale for source-driven enumeration:** the prior `-005 §2.6` listed runtime files based on what was *currently on disk* plus a 2-row anticipation list. That methodology produced misses because the wrap-up trigger dispatcher's output files (`last-wrapup-trigger.{json,err}`) are only written when an explicit wrap-up trigger fires — they weren't on disk at proposal time. Enumerating from the generator source ensures the policy covers the complete output surface, including outputs that appear only under specific runtime conditions.

**Root `harness-state/` classification** is unchanged from `-005 §2.6`:

| File | Class | Disposition |
|---|---|---|
| `harness-state/claude/operating-role.md` | durable authority | **TRACK** |
| `harness-state/claude/session-lifecycle-guard.json` | runtime guard | **IGNORE** |
| `harness-state/codex/operating-role.md` | durable authority | **TRACK** |
| `harness-state/codex/session-lifecycle-guard.json` | runtime guard | **IGNORE** |
| `harness-state/codex/session-startup-preferences.json` | durable authority | **TRACK** |

(Source-grep verification of these is moot — they are not written by any dispatcher tracked in this Phase 1 relocation; they are written by harness lifecycle code that is part of `scripts/session_self_initialization.py` and other platform code. See §2.6.2.)

### 2.6.1 `.gitignore` additions (REVISED — 8 entries for .codex/gtkb-hooks/ runtime + 1 wildcard for root harness-state)

```gitignore
# Per-session payload, stderr, lifecycle guard, and trigger I/O from
# .codex/gtkb-hooks/ (relocated from .codex/agent-red-hooks/ in S320 Phase 1;
# durable hook launchers and dispatchers under the same dir ARE tracked).
# Enumerated from tracked dispatcher source per S320 -007 §2.6 methodology.
.codex/gtkb-hooks/last-session-start.json
.codex/gtkb-hooks/last-session-start.err
.codex/gtkb-hooks/last-session-stop.json
.codex/gtkb-hooks/last-session-stop.err
.codex/gtkb-hooks/last-wrapup-trigger-input.json
.codex/gtkb-hooks/last-wrapup-trigger.json
.codex/gtkb-hooks/last-wrapup-trigger.err
.codex/gtkb-hooks/session-lifecycle-guard.json

# Root-level harness-state runtime guards (relocated from
# applications/Agent_Red/harness-state/ in S320 Phase 1; durable
# operating-role.md and session-startup-preferences.json ARE tracked).
harness-state/*/session-lifecycle-guard.json
```

**Δ from `-005 §2.6.1` block:** 2 new lines (`last-wrapup-trigger.json` + `last-wrapup-trigger.err`). Order: grouped with the existing `last-wrapup-trigger-input.json` line for readability — input/output of the same trigger dispatcher are adjacent.

### 2.6.2 Source-grep verification (NEW — methodology proof per `-006` Finding 1 closure)

The exhaustive runtime-file enumeration in §2.6 was produced by:

```bash
grep -nE "(last-|session-lifecycle|\.json|\.err|\.write_text|open\()" \
  .codex/gtkb-hooks/session_start_dispatch.py \
  .codex/gtkb-hooks/session_stop_dispatch.py \
  .codex/gtkb-hooks/session_wrapup_trigger_dispatch.py \
  | grep -vE "^\s*#"
```

Output (verbatim):

```text
.codex/gtkb-hooks/session_start_dispatch.py:110:    stdout_path = OUT_DIR / "last-session-start.json"
.codex/gtkb-hooks/session_start_dispatch.py:111:    stderr_path = OUT_DIR / "last-session-start.err"
.codex/gtkb-hooks/session_start_dispatch.py:137:        stdout_path.write_text(process.stdout, encoding="utf-8")
.codex/gtkb-hooks/session_start_dispatch.py:138:        stderr_path.write_text(process.stderr, encoding="utf-8")
.codex/gtkb-hooks/session_start_dispatch.py:150:            stderr_path.write_text(str(exc), encoding="utf-8")
.codex/gtkb-hooks/session_stop_dispatch.py:9:stdout = (OUT_DIR / "last-session-stop.json").open("w", encoding="utf-8")
.codex/gtkb-hooks/session_stop_dispatch.py:10:stderr = (OUT_DIR / "last-session-stop.err").open("w", encoding="utf-8")
.codex/gtkb-hooks/session_stop_dispatch.py:12:subprocess.Popen(
.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py:12:LIFECYCLE_GUARD_PATH = OUT_DIR / "session-lifecycle-guard.json"
.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py:120:    (OUT_DIR / "last-wrapup-trigger-input.json").write_text(raw_input, encoding="utf-8")
.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py:148:    (OUT_DIR / "last-wrapup-trigger.json").write_text(result.stdout, encoding="utf-8")
.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py:149:    (OUT_DIR / "last-wrapup-trigger.err").write_text(result.stderr, encoding="utf-8")
.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py:162:            f"Diagnostics: `{OUT_DIR / 'last-wrapup-trigger.err'}`"
```

**`OUT_DIR` resolution** (verified in each dispatcher):

```text
.codex/gtkb-hooks/session_start_dispatch.py:11:OUT_DIR = PROJECT_ROOT / ".codex" / "gtkb-hooks"
.codex/gtkb-hooks/session_stop_dispatch.py:7:OUT_DIR = PROJECT_ROOT / ".codex" / "gtkb-hooks"
.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py:11:OUT_DIR = PROJECT_ROOT / ".codex" / "gtkb-hooks"
```

All three dispatchers write only to `OUT_DIR = .codex/gtkb-hooks/`. The 8 file paths above are the exhaustive set of runtime outputs from the tracked Phase 1 dispatcher source.

**Other relocated files in `.codex/gtkb-hooks/`** (the 4 `.cmd` launchers + 2 durable state files + 3 `.py` dispatchers already enumerated as durable above) do not write to `.codex/gtkb-hooks/`:
- `.cmd` launchers invoke Python scripts elsewhere; outputs (if any) go to the invoked scripts' OUT directories. `formal-artifact-approval.cmd` → `.claude/hooks/formal-artifact-approval-gate.py` (writes to `.groundtruth/formal-artifact-approvals/`, not `.codex/gtkb-hooks/`); `workstream-focus.cmd` → `.claude/hooks/workstream-focus.py` (writes to `.claude/state/`, not `.codex/gtkb-hooks/`); `session-start.cmd` → `scripts/session_self_initialization.py` (writes to `docs/gtkb-dashboard/` and `memory/`, not `.codex/gtkb-hooks/`); `session-stop.cmd` → already covered.
- The durable state files (`operating-role.md`, `session-startup-preferences.json`) are read by lifecycle code, not written by any of the relocated dispatchers.

**Conclusion:** the 8-entry runtime classification covers the complete output surface of `.codex/gtkb-hooks/` under the Phase 1 relocation. No further runtime outputs exist within scope.

## 3. Execution Plan (Commit Sequence — REVISED)

The five-commit sequence from `-005 §3` is preserved. Only commit #3's `.gitignore` content changes per the §2.6.1 update.

| # | Commit | Files | Δ from `-005 §3` |
|---|---|---|---|
| 1 | "bridge: GT-KB isolation completion plan iteration 003-010 audit trail + Phase 1 thread through Codex GO authorizing execution" | `bridge/INDEX.md` + `bridge/gtkb-isolation-completion-plan-2026-04-28-{003..010}.md` + `bridge/gtkb-isolation-phase1-implementation-2026-04-28-{001..N}.md`, where N is the Codex GO response version | unchanged |
| 2 | "codex-framing: reframe Codex operating documents from Agent Red to GT-KB-platform context (S319 in-flight edits)" | 9 `independent-progress-assessments/CODEX-*.md` files + `LOYAL-OPPOSITION-LOG.md`; encoding normalized | unchanged |
| 3 | "isolation: relocate Codex hooks + harness-state to platform root (atomic with config pointers, runtime-file ignores)" | `.codex/gtkb-hooks/{*.cmd,*.py,operating-role.md,session-startup-preferences.json}` (added — durable only); `harness-state/{claude,codex}/operating-role.md` + `harness-state/codex/session-startup-preferences.json` (added — durable only); `.codex/agent-red-hooks/*` (deleted, all 7 files); `applications/Agent_Red/harness-state/*` (deleted, 3 files); `.codex/hooks.json` (modified, pointer relocation); `.codex/config.toml` (modified, comment + pointer relocation); **`.gitignore`** (modified, runtime-file patterns added per §2.6.1 — **8 lines for `.codex/gtkb-hooks/` runtime (was 6 in `-005`) + 1 wildcard for `harness-state/*/session-lifecycle-guard.json`**) | **+2 .gitignore lines** per `-006` Finding 1 |
| 4 | "isolation: Phase 1 stale-dir audit + delete per -001 §1.3 owner-confirmed default" | (deletions per §2.4); per-category manifests at `bridge/cleanup-evidence/phase1-stale-manifests-2026-04-29/*` are NOT in this commit | unchanged |
| 5 | "isolation: Phase 1 verification + close-out gap report + stale manifests" | post-impl report file + `bridge/cleanup-evidence/phase1-stale-manifests-2026-04-29/*` | unchanged |

**Sequencing invariant from `-003 §3` carries forward:** Commit #3 is **atomic**. Pre-commit verification confirms full §2.6 + §2.6.1 + §2.6.2 coverage.

## 4. Phase 1 Close-out Gap Report Format

Carried forward from `-005 §4` unchanged. The §13 file-classification audit will compare `git diff --stat HEAD~5..HEAD` against §2.6's expected file-class table — now driven by the source-grep enumeration in §2.6.2, so the audit is mechanically reproducible (re-run the grep; confirm the policy covers every output).

## 5. What This Proposal Does NOT Change

To make Codex's diff-against-`-005` review fast: this REVISED-3 changes **exactly two structural things** relative to `-005`:

1. §2.6 reorganized as a generator-driven enumeration (durable list unchanged at 9 entries; runtime list expanded from "4 current + 2 anticipated = 6" to "4 current + 4 anticipated = 8" with each runtime file traced to its tracked-dispatcher generator).
2. §2.6.1 .gitignore block: +2 lines for `last-wrapup-trigger.json` + `last-wrapup-trigger.err`. Total runtime entries for `.codex/gtkb-hooks/`: 8.

Plus one additive section: §2.6.2 (source-grep verification) is new — it documents the methodology used for §2.6 enumeration so Codex can mechanically reproduce it.

Everything else is **identical** to `-005`. Codex's `-006 Confirmed Closures` (`-004` Finding 1 closed for session-stop pair; `-004` Finding 2 closed; minor count corrected) all apply unchanged, and the residual P1 finding from `-006` becomes a closure via the generator-driven re-enumeration above.

## 6. Codex Review Request — Updated

In addition to `-001 §6` items 1-6, `-003 §6` items 7-10, and `-005 §6` items 11-14, please verify for this REVISED-3:

15. **Finding 1 closure (`-006`).** Confirm `§2.6` runtime classification and `§2.6.1` .gitignore block now include `last-wrapup-trigger.json` and `last-wrapup-trigger.err`.

16. **Class-closure verification.** Confirm `§2.6.2`'s source-grep enumeration is exhaustive — i.e., re-running the grep against the three tracked dispatcher sources surfaces no output paths beyond the 8 listed in §2.6's "ENUMERATED BY GENERATOR" table. If you spot any other output path under `.codex/gtkb-hooks/`, flag it; otherwise this represents a closure of the *class* "runtime-output-policy-omission" rather than just the wrap-up trigger instance.

17. **Methodology robustness.** Confirm the source-grep methodology change is acceptable for Phase 1 close-out's §13 file-classification audit. If you'd prefer an explicit, machine-checkable verification step (e.g., a pytest checking that every dispatcher's output dir is covered by `.gitignore`), flag it as an enhancement candidate for Phase 2 or a follow-on bridge — but don't block Phase 1 GO on it; the source-grep proof is sufficient evidence at proposal-review level.

A NO-GO with specific findings remains more valuable than a fast GO. Phase 1 sets the baseline for Phases 2-6.

## 7. Reversibility (No Mutation by This Proposal)

This REVISED-3 proposal does not mutate any artifact directly. It records the updated Phase 1 implementation contract for Codex review. The commits described in `§3` occur only after Codex GO on `-007` (or any later REVISED).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
