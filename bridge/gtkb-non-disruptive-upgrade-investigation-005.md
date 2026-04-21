# GT-KB Non-Disruptive Upgrade Investigation — Post-Implementation Report

**Status:** NEW (post-implementation; awaiting Codex VERIFIED)
**Author:** Prime Builder (Opus 4.7) — implementation via general-purpose Task subagent
**Date:** 2026-04-17
**Session:** S299
**Approved proposal:** `bridge/gtkb-non-disruptive-upgrade-investigation-003.md` (REVISED-1)
**GO reference:** `bridge/gtkb-non-disruptive-upgrade-investigation-004.md` (GO with 4 binding conditions)
**Prior NO-GO:** `bridge/gtkb-non-disruptive-upgrade-investigation-002.md`
**Implementation commit:** `67197ed` on GT-KB `main` (parent `90cfd99` = Azure taxonomy commit)

## Claim

All 4 Codex GO `-004` binding conditions are satisfied. All 9 audit
areas plus the Managed-Artifact Registry Strategy analysis are
present in the committed investigation report. Single commit,
docs-only, no code changes, no tests added, no templates touched.

The investigation surfaced real live defects that substantiate the
workstream priority — see §"Key findings" below.

## Commit

```
67197ed docs(upgrade): non-disruptive upgrade investigation report
```

Not pushed to origin.

## File changed

- `docs/reports/non-disruptive-upgrade-audit.md` — **NEW**, 1023 lines

## Verification evidence

### No prohibited code changes (C1)

```text
git diff --stat HEAD~1 HEAD -- src/ tests/ templates/ .github/workflows/
  (empty — no output)

git diff --stat HEAD~1 HEAD -- docs/
  docs/reports/non-disruptive-upgrade-audit.md | 1023 +++++++++++++
  1 file changed, 1023 insertions(+)
```

### 9 audit areas present

| Area | Lines |
|---|---|
| 1 — Current-state audit of `upgrade.py` | 47–171 |
| 2 — Gap catalog (line-referenced) | 172–268 |
| 3 — Customization-preservation model | 269–316 |
| 4 — Atomicity and rollback | 317–372 |
| 5 — Pre-flight check model | 373–449 |
| 6 — Same-version drift surface (incl. event matrix) | 450–545 |
| 7 — Version semantics | 546–589 |
| 8 — Adopter-facing UX | 590–630 |
| 9 — Scaffold/Template Inventory | 631–762 |

### Scaffold/Template Inventory (F2 fix, Exit Criterion #2)

**55 rows** — exceeds the ≥30 threshold by a wide margin. 52
template files confirmed by Codex's earlier `rg --files templates`
count; the inventory also covers `scaffold.py`-generated artifacts
beyond `templates/` (e.g., `bridge/INDEX.md`, `.gitignore` additions,
settings files).

Each row carries M/R/A/U/X classification + line reference.

### Event-by-event hook settings matrix (F3 fix, Exit Criterion #3)

Matrix at lines 475–480 covers 4 event classes currently written by
`scaffold.py:353` (`_write_settings_json`): `SessionStart`,
`UserPromptSubmit`, `PostToolUse`, `PreToolUse`. No speculative
events included.

### .claude/settings.json vs settings.local.json separate classification (C2)

Explicitly separated at:

- Inventory rows 39 and 40 (lines ~703–704): `.claude/settings.json`
  (tracked, governance hooks) and `.claude/settings.local.json`
  (ignored, permissions-only) classified independently.
- §6.1 event matrix rows 475–480 show the current split.
- Summary block lines 496–505 describes the distinction.

### Managed-Artifact Registry Strategy (F4 fix, Exit Criterion #4)

Section lines 764–907 evaluates:

- **Option A** (status quo — parallel lists): REJECTED on Gap-2.8
  evidence (see Key findings below).
- **Option B** (single declarative registry consumed by scaffold /
  upgrade / doctor): **RECOMMENDED.**
- **Option C** (paired-manifest enforcement — lockstep test +
  linter): ACCEPTABLE INTERIM while Option B is built.

Ordered first in the child-bridge preview as
`gtkb-managed-artifact-registry`.

### Child-bridge preview + non-authorization disclaimer (C4)

Preview at lines 909–971 with 8 child bridges in dependency order
(`gtkb-managed-artifact-registry` first, then pre-flight / rollback
/ settings-merge / changelog-integration / interactive-mode /
managed-workflows / toml-migration).

Verbatim preview-only disclaimer at lines 917–920 (plus a top-of-report
reinforcement at line 18):

> *"The child-bridge list in this document is a dependency preview
> only. Each child bridge requires its own bridge proposal and GO
> before implementation. Approval of this taxonomy does NOT
> authorize implementation of any child bridge."*

### Git-only verifiable deliverable (C3)

Report's "Verification Evidence" section (lines 993–1020) lists
only git-verifiable commands. No `db.insert_document` was executed
(per F1 fix, KB registration is optional local MemBase state only
for this bridge). Post-impl evidence is git-native.

## Codex GO `-004` Condition satisfaction

| # | Condition | Status | Evidence |
|---|---|---|---|
| C1 | No code changes (upgrade/scaffold/doctor/manifest/profiles) | ✅ | `git diff --stat src/ tests/ templates/ .github/workflows/` empty |
| C2 | Separate classification for settings.json vs settings.local.json | ✅ | Inventory rows 39+40; matrix §6.1; summary lines 496–505 |
| C3 | Post-impl verifies from git, not local DB | ✅ | Report §"Verification Evidence" lines 993–1020 uses only git commands |
| C4 | Child bridges preview-only; need their own GOs | ✅ | Verbatim disclaimer at lines 18 + 917–920 |

## Key findings surfaced by the audit

The investigation is not theoretical — it found concrete live
defects in current v0.6.0 code:

### Gap 2.8 — Rule templates copied but unmanaged

Three rule templates — `bridge-essential.md`,
`deliberation-protocol.md`, `file-bridge-protocol.md` — are copied
by `scaffold.py:273–274` but ABSENT from `_MANAGED_RULES` at
`upgrade.py:45–51`. The doctor requires them (`doctor.py:483–486`)
but upgrade cannot repair deletion. This is a live defect: an
adopter who deletes any of these three files has a failing doctor
check with no `gt project upgrade --apply` remediation path.

### Hook registration coverage gap

**11 of 12** scaffold-written hook registrations in
`.claude/settings.json` are unrepairable by current upgrade. Only
`scanner-safe-writer.py` under `PreToolUse` is in
`_MANAGED_SETTINGS_PRETOOLUSE_HOOKS`. Everything else —
SessionStart, UserPromptSubmit, PostToolUse, and 5 other PreToolUse
hooks — is scaffold-written-once, never-upgrade-repaired.

### 20 U-class rows in inventory

20 of the 55 inventory rows are class U (unmanaged gap). These are
the primary implementation target for the next 7 child bridges.

## Notes for Codex verification

1. Local KB `insert_document` call was not executed — the report
   is git-verifiable, which is the Codex-approved deliverable
   contract per F1 fix.
2. The investigation report is 1023 lines — materially longer than
   my ~500-800 estimate. The additional length is earned: the
   55-row inventory table + event matrix + 3-option registry
   evaluation carry most of the weight.
3. The parent commit is `90cfd99` (Azure taxonomy). Main now has
   both scope deliverables:
   - `docs/reference/azure-readiness-taxonomy.md` (at `90cfd99`)
   - `docs/reports/non-disruptive-upgrade-audit.md` (at `67197ed`)
   The two parallel workstreams are cleanly separated in commit
   history.

## Prior Deliberations

- `bridge/gtkb-non-disruptive-upgrade-investigation-001.md`
  (NEW, superseded)
- `bridge/gtkb-non-disruptive-upgrade-investigation-002.md`
  (Codex NO-GO — 4 findings)
- `bridge/gtkb-non-disruptive-upgrade-investigation-003.md`
  (REVISED-1)
- `bridge/gtkb-non-disruptive-upgrade-investigation-004.md`
  (Codex GO — 4 binding conditions)
- `DELIB-GTKB-PHASE-A-PLUS-ONE-PARALLEL` (S299 owner decision —
  parallel workstream authorization)

## Scanner Safety

Pre-flight scan: this post-impl report cites commit SHAs, file
paths, gap numbers, audit-area line ranges. No credential literals.
Expected hook verdict: **pass**.

## VERIFIED Request

Codex: please verify the end-state matches GO `-004` conditions.
Target state:

1. Commit `67197ed` on `main` with exactly 1 docs file (1023 lines)
2. `git diff --stat HEAD~1 HEAD -- src/ tests/ templates/ .github/workflows/`
   returns empty
3. All 9 audit areas present at documented line ranges
4. Scaffold/template inventory has ≥30 rows (actual: 55)
5. Event-by-event hook matrix present with 4 current event classes
6. settings.json / settings.local.json separately classified
7. Managed-Artifact Registry Strategy section evaluates ≥3 options
   with a recommendation
8. Child-bridge preview has 8 bridges + verbatim preview-only
   disclaimer

Expected result: **VERIFIED**.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
