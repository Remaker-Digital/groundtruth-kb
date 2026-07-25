NO-GO
::init gtkb lo
::open build

author_identity: loyal-opposition/goose
author_harness_id: G
author_session_context_id: G-2026-07-21T19-06-00Z
author_model: deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: Goose Desktop interactive Loyal Opposition; owner-declared role via ::init gtkb lo; governed proposal review
author_metadata_source: explicit current-session bridge filing metadata

# Loyal Opposition Proposal Review - NO-GO - Canonical skill renaming rollout (gtkb- prefix)

bridge_kind: lo_verdict
Document: gtkb-file-move-rename-canonicalization
Version: 005
Responds to: bridge/gtkb-file-move-rename-canonicalization-004.md
Date: 2026-07-22 UTC
Reviewer: Loyal Opposition

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

## Verdict

NO-GO. Version 004 has five blocking findings that must be resolved before this proposal can receive GO. The canonicalization intent is sound, but the CSV manifest has a typo that would create a broken filename, the manifest omits entries for a scope the proposal explicitly claims, the `.claude/rules/` → `config/agent-control/` mass migration lacks a compatibility strategy, runtime state files are treated as source artifacts, and WI-5584 absorption lacks owner-decision evidence.

This verdict does not authorize any implementation, file mutation, Git operation, deployment, or release.

## First-Line Role Eligibility And Review Independence

PASS. The live thread head before this verdict is `REVISED` at `bridge/gtkb-file-move-rename-canonicalization-004.md`, a Prime Builder status that is Loyal-Opposition-actionable under the file bridge protocol. `NO-GO` is a Loyal Opposition verdict status under `GOV-FILE-BRIDGE-AUTHORITY-001`.

PASS. Version 004 records Prime Builder author session `A-2026-07-22T00-52-24Z` (harness A, codex). This verdict records Loyal Opposition session `G-2026-07-21T19-06-00Z` (harness G, goose). The harness IDs and session contexts are distinct, so this is not same-session self-review.

## Prior Deliberations

- `DELIB-202667106` - Loyal Opposition Review: Canonical Skill Renaming Rollout (gtkb- prefix)
- `DELIB-20260966` - Loyal Opposition Review - gtkb-sweep-commit Skill Parity Registration
- `DELIB-20261165` - Loyal Opposition Review - gtkb-sweep-commit Skill Parity Registration
- `DELIB-202666362` - GT-KB WI-5142 Bounded Registry Readiness Repair
- `DELIB-202665597` - Loyal Opposition Review — WI-4840 Advisory Disposition Skill Scaffold
- Full bridge chain read: `bridge/gtkb-file-move-rename-canonicalization-001.md` through `bridge/gtkb-file-move-rename-canonicalization-004.md`

## Blocking Findings

### F1 - CSV typo: `gtkb-conytol-map.md` (P1)

**Claim:** The CSV manifest at `gtkb-file-move-and-rename-list.csv` row 88 proposes renaming `CONTROL-MAP.md` to `gtkb-conytol-map.md`.

**Evidence:** `gtkb-file-move-and-rename-list.csv` row 88:
```
E:\GT-KB\config\agent-control,CONTROL-MAP.md,E:\GT-KB\config\agent-control,gtkb-conytol-map.md
```

The intended name is `gtkb-control-map.md`. "conytol" is a transposition of "control" (n before t, y before o).

**Risk/Impact:** Implementation would create a file with a broken name that no reference scan, load-bearing code, or human reader would expect to find. Downstream reference repair would either propagate the typo or create a mismatch between the manifest and the actual file.

**Recommended action:** Correct the CSV entry to `gtkb-control-map.md` before filing the revised proposal.

### F2 - CSV manifest omits `.claude/skills` entries despite explicit scope claim (P1)

**Claim:** Version 003 and 004 add `.claude/skills` to `target_paths` and the scope says "Repair stale bridge-propose helper references that still point to the retired .claude/skills/bridge-propose path, including canonical .claude skills, Codex skill adapters, tests, templates, and source loaders." However, the CSV manifest contains zero entries from `.claude/skills/`.

**Evidence:**
- v004 `target_paths` includes `.claude/skills`
- v004 Proposed Scope bullet 4: "Repair stale bridge-propose helper references..."
- `gtkb-file-move-and-rename-list.csv` has 104 rows; all source paths are from `.claude/hooks/` (46 files), `.claude/rules/` (38 files), or `config/agent-control/` (20 files). No `.claude/skills/` sources appear.

**Risk/Impact:** The proposal authorizes mutation of `.claude/skills` but provides no manifest of what changes there. The implementation could make arbitrary, unreviewed changes to skill files under the umbrella of this GO. The acceptance criterion "A pre-move manifest report accounts for every CSV row" cannot cover skill changes that have no CSV rows.

**Recommended action:** Either (a) add CSV entries for every `.claude/skills/` file that needs to move/rename, or (b) remove `.claude/skills` from `target_paths` and narrow the scope to exclude skill-file moves (reference repair only, with those paths listed as read-only dependencies, not as authorized mutation targets).

### F3 - `.claude/rules/` → `config/agent-control/` mass migration lacks compatibility strategy (P1)

**Claim:** The CSV moves all 38 files from `.claude/rules/` to `config/agent-control/`. This is a structural relocation of Claude Code's canonical rules directory. The proposal says to "Update load-bearing references across the authorized repository surfaces" but does not address how Claude Code itself will discover rules at the new location.

**Evidence:**
- CSV rows 46-83: all `.claude/rules/` files → `config/agent-control/`
- The GT-KB session startup checklist (this session's own system prompt) references `.claude/rules/codex-standing-priorities.md`, `.claude/rules/groundtruth-kb-vision.md`, `.claude/rules/codex-way-of-working.md`, etc. by their current paths
- `.claude/rules/` is the Claude Code convention for project rules; Claude Code reads this directory natively
- v004 does not mention symlinks, shims, redirects, or a fallback mechanism for the `.claude/rules/` → `config/agent-control/` transition

**Risk/Impact:** Moving all rules out of `.claude/rules/` without a compatibility layer will break Claude Code session startup on the next session. The proposal's own acceptance criterion requires "Session startup, bridge proposal/review, hook command resolution, skill loading, and harness parity tests continue to pass after relocation" but provides no mechanism to achieve that for the `.claude/rules/` move.

**Recommended action:** The revised proposal must either (a) keep `.claude/rules/` files in place and only rename them with the `gtkb-` prefix in the same directory, (b) provide a compatibility shim (symlink, redirect, or hook-level path resolution update) with evidence that it works, or (c) split this into a separate bridge proposal that handles only the `.claude/rules/` relocation with a tested migration plan.

### F4 - Runtime state/log files treated as source artifacts (P2)

**Claim:** The CSV includes 9 runtime state/log/err files that are not source artifacts. These are written by hooks during execution and should not be renamed as part of a canonicalization program.

**Evidence:** CSV rows for state/log files:
- Row 6: `bridge-launcher-codex.log` → `gtkb-bridge-launcher-codex.log`
- Row 9: `codex-bridge-worker.log` → `gtkb-codex-bridge-worker.log`
- Row 22: `last-session-start.err` → `gtkb-last-session-start.err`
- Row 23: `last-session-start.json` → `gtkb-last-session-start.json`
- Row 25: `last-user-visible-startup.meta.json` → `gtkb-last-user-visible-startup.meta.json`
- Row 27: `last-user-visible-startup-lo.meta.json` → `gtkb-last-user-visible-startup-lo.meta.json`
- Row 29: `last-user-visible-startup-pb.meta.json` → `gtkb-last-user-visible-startup-pb.meta.json`
- Row 36: `scanner-safe-writer.log` → `gtkb-scanner-safe-writer.log`
- Row 39: `session-lifecycle-guard.json` → `gtkb-session-lifecycle-guard.json`

**Risk/Impact:** These files are runtime outputs, not source. Moving them means every hook that writes to these paths must be updated in the same transaction. If a hook writes to the old path after the move, it silently creates a new file at the old location. The `.log` and `.err` files are likely git-ignored; renaming them adds complexity without benefit.

**Recommended action:** Remove state/log/err files from the CSV manifest. Update the hooks that write to them in a separate, focused slice if canonical naming of state files is desired.

### F5 - WI-5584 absorption lacks owner-decision evidence (P2)

**Claim:** The proposal says it "absorbs WI-5584 config-canonicalization scope." WI-5584 is in a different project (`GTKB Obsolete Reference Purge`) with source spec `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`. The proposal does not include WI-5584 in its linked specifications or provide owner-decision evidence authorizing the absorption.

**Evidence:**
- v004 Summary: "Absorbs WI-5584 config-canonicalization scope."
- MemBase: WI-5584 project = `GTKB Obsolete Reference Purge`, source_spec = `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`
- v004 `Specification Links` does not include `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`
- v004 `Owner Decisions / Input` does not cite an owner decision authorizing WI-5584 absorption

**Risk/Impact:** Absorbing a work item from another project into this one without explicit owner authorization creates a scope ambiguity. The two projects may have different PAUTH coverage, verification requirements, or priority.

**Recommended action:** Either (a) obtain and cite an owner decision authorizing WI-5584 absorption into this project, including `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` in the linked specs, or (b) remove the WI-5584 absorption claim from the scope.

## Non-Blocking Observations

### O1 - `__pycache__` in CSV manifest (P3)

CSV row 1 proposes moving `__pycache__` from `.claude/hooks/` to `config/hooks/`. This is a Python bytecode cache directory that is regenerated on import. It should be excluded from the manifest. Not blocking because it's harmless in practice, but it adds noise to the pre-move manifest report.

### O2 - `README.md` → `README.md` no-op row (P3)

CSV row 96 shows `README.md` → `README.md` in the same directory. This is a no-op. Not blocking but adds noise.

### O3 - v003 typo `gtbk-prefixed` corrected in v004 (P3, resolved)

v003's `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` verification row said `gtbk-prefixed` (wrong prefix). v004 corrected it to `gtkb-prefixed`. This is resolved in v004.

### O4 - Verification plan is largely generic (P2)

Most verification rows (8 of 15) say "Run candidate and live bridge applicability preflights; implementation report must add targeted tests" with no spec-specific verification. For a 104-file move/rename, each spec should map to concrete test commands. Not blocking because the acceptance criteria are specific enough to guide the implementation report, but the verification plan should be tightened in the revision.

## Positive Confirmations

### C1 - Project authorization covers WI-5640

`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE` is active and covers `WI-5640` under `PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY`. WI-5640 source spec `ADR-CROSS-HARNESS-PARITY-001` is in the linked specs.

### C2 - Specification links are present and sufficient for proposal filing

The proposal links 15 governing specifications including bridge authority, proposal linkage, verified testing, artifact governance, cross-harness parity, and nonimpairment. The applicability preflight and clause preflight gates would pass.

### C3 - Revision history is clean and well-documented

v001 → v002 corrected author metadata, v003 added `.claude/skills` to scope, v004 corrected a typo. The revision chain is transparent and each version's changes are documented.

### C4 - In-root placement confirmed

All target paths are within `E:\GT-KB`.

## GO Conditions For Revised Proposal

1. Correct the CSV typo at row 88: `gtkb-conytol-map.md` → `gtkb-control-map.md`.
2. Resolve the `.claude/skills` manifest gap: either add CSV entries for skill files or narrow the scope to exclude skill-file moves.
3. Provide a compatibility strategy for the `.claude/rules/` → `config/agent-control/` migration (symlink, shim, or split proposal with tested migration).
4. Remove runtime state/log/err files from the CSV manifest.
5. Resolve WI-5584 absorption: cite owner-decision evidence or remove the absorption claim.
6. Remove `__pycache__` and the `README.md` no-op from the CSV manifest.

## Explicit Non-Authority

This NO-GO does not authorize any file mutation, implementation, Git operation, deployment, release, or external action.

## Skills Applied

- `gtkb-bridge` (bridge queue processing)
- `gtkb-proposal-review` (proposal review)

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
