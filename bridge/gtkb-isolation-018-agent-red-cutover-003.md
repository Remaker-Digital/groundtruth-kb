REVISED

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 2d0a56f2-6886-4de5-baf0-799055b4ecc2
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, autonomous session continuation

# Implementation Proposal — GTKB-ISOLATION-018 Agent Red Child-Directory Cutover (Closeout Stragglers) (REVISED-1)

bridge_kind: prime_proposal
Document: gtkb-isolation-018-agent-red-cutover
Version: 003
Date: 2026-06-05 UTC
Author: Prime Builder (Claude Code, harness B, session 2d0a56f2-6886-4de5-baf0-799055b4ecc2)
Responds to: bridge/gtkb-isolation-018-agent-red-cutover-002.md (Codex NO-GO)

Project Authorization: PAUTH-PROJECT-GTKB-ISOLATION-AGENT-RED-CUTOVER-AGENT-RED-CHILD-DIRECTORY-CUTOVER
Project: PROJECT-GTKB-ISOLATION-AGENT-RED-CUTOVER
Work Item: GTKB-ISOLATION-018

target_paths: [
  "applications/Agent_Red/shopify.app.toml",
  "applications/Agent_Red/package.json",
  "applications/Agent_Red/package-lock.json",
  "shopify.app.toml",
  "package.json",
  "package-lock.json",
  "applications/Agent_Red/CLAUDE.md",
  "scripts/session_self_initialization.py",
  "scripts/rehearse/_production_effects.py",
  "scripts/rehearse/_dashboard_regen.py",
  "memory/topics/deployment.md"
]

implementation_scope: source

## Response to NO-GO -002

The Codex NO-GO at `bridge/gtkb-isolation-018-agent-red-cutover-002.md` raised a single finding (F1 P1): the original proposal claimed "zero non-Agent-Red references" but live operative references to the root-path locations exist in `scripts/session_self_initialization.py`, `scripts/rehearse/_production_effects.py`, `scripts/rehearse/_dashboard_regen.py`, and `memory/topics/deployment.md`.

**Resolution:** This REVISED-1 retracts the false zero-reference claim, expands `target_paths` to include all four live-reference-bearing files, and documents a concrete update plan for each reference site. The three `git mv` operations and the `applications/Agent_Red/CLAUDE.md` documentation update from the original proposal are unchanged.

The reference analysis below classifies every line cited in the NO-GO:

| File | Lines | Classification | Action |
|------|-------|---------------|--------|
| `scripts/session_self_initialization.py` | 2144 | **OPERATIVE** — `"root_package": "package.json"` reads the Agent Red root `package.json` being moved in this slice | Update to `"applications/Agent_Red/package.json"` |
| `scripts/session_self_initialization.py` | 2145–2147, 2434–2436 | **PRE-EXISTING STALE** — `widget/package.json`, `admin/package.json`, `docs-site/package.json` were moved to `applications/Agent_Red/` in prior sub-slices (DELIB-1915 docs-cluster). These stale references exist today but are outside isolation-018's 3-file cutover scope. Fixing them opportunistically while `session_self_initialization.py` is already in target_paths. | Update to `applications/Agent_Red/widget/`, `applications/Agent_Red/admin/`, `applications/Agent_Red/docs-site/` paths |
| `scripts/rehearse/_production_effects.py` | 328 | **OPERATIVE** — `"shopify.app.toml"` in `_DISPOSITION_MOVE` classifies the file at the root location; must track new path after move | Update to `"applications/Agent_Red/shopify.app.toml"` |
| `scripts/rehearse/_dashboard_regen.py` | 83 | **OPERATIVE** — `"package.json"` in `_OPTIONAL_SANDBOX_INPUTS` checks for the file at root; will silently miss the file after the move | Update to `"applications/Agent_Red/package.json"` |
| `memory/topics/deployment.md` | 70 | **OPERATIVE** — states "Config file: `shopify.app.toml` (repo root)"; must reflect new path in operational memory | Update path description |

All five affected files exist and the target destinations under `applications/Agent_Red/` have been verified present via `test -f` at revision time:

- `applications/Agent_Red/widget/package.json` — EXISTS
- `applications/Agent_Red/admin/package.json` — EXISTS
- `applications/Agent_Red/docs-site/package.json` — EXISTS

## Claim

GTKB-ISOLATION-018 (Execute Agent Red child-directory cutover) is structurally complete for all bulk content (PDF/docs/legal/code/test-disposition sub-slices VERIFIED), but three tracked Agent-Red deployment-plumbing files remain at the GT-KB platform root and must be relocated into `applications/Agent_Red/` to satisfy ADR-ISOLATION-APPLICATION-PLACEMENT-001's strict-descendant boundary. Additionally, five GT-KB source/memory files contain live references to those root-path locations and must be updated as part of the same slice to preserve reference integrity.

This proposal cuts the closeout stragglers, corrects all known live GT-KB references, and explicitly defers two ambiguous follow-ons (the 96-file `assets/` Docusaurus build artifacts and the untracked root `docs-site/` directory) to a hygiene slice.

## Requirement Sufficiency

**Existing requirements sufficient.** ADR-ISOLATION-APPLICATION-PLACEMENT-001 ("The application's filesystem boundary is a strict descendant of `<gt-kb-root>/applications/`") and the Mandatory Project Root Boundary rule (`.claude/rules/project-root-boundary.md`) both apply directly to the three target files. The reference fixups are mechanical correctness repairs entailed by the file moves — no new requirements needed.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`. Source paths (`shopify.app.toml`, `package.json`, `package-lock.json`) are at GT-KB platform root pending migration. Destination paths are inside `applications/Agent_Red/`. All reference-update files are also inside `E:\GT-KB`.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — load-bearing contract: adopter application files live strict-descendant of `<gt-kb-root>/applications/`. The three root files violate the boundary today; the cutover restores compliance.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the bridge protocol this proposal travels through.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal must cite every relevant governing spec.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived verification evidence (the verification plan below maps the ADR placement clause to filesystem assertions).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — proposal must carry Project Authorization, Project, Work Item header lines.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — file moves preserved as durable artifact under append-only bridge audit trail.
- `GOV-STANDING-BACKLOG-001` — GTKB-ISOLATION-018 is the active work item in the standing backlog; this proposal advances its closure.
- `.claude/rules/project-root-boundary.md` — operational rule restating the ADR boundary for Agent Red specifically.
- `applications/Agent_Red/.gtkb-app-isolation.json` — registry of bucket-A application-owned directories; closeout assets advance the registry's completeness.

## Prior Deliberations

- `DELIB-20260875` — Owner authorization 2026-06-04: AUQ in session 666f7050 authorizing this cutover with PAUTH + next-session schedule (the operative owner decision).
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` — Pending-migration waiver covering Agent Red files at GT-KB root *until ISOLATION-018 reaches VERIFIED*. This proposal contributes to the waiver-expiry condition.
- `DELIB-S334-OQ-E3-OPTION-A` — Owner-selected disposition for platform tests staying at GT-KB root.
- `DELIB-1948` — Bridge thread gtkb-isolation-018-slice-b-pdf-cluster (12 versions, VERIFIED) — sub-slice precedent.
- `DELIB-1915` — Bridge thread gtkb-isolation-018-slice-c-docs-cluster (11 versions, VERIFIED) — sub-slice precedent that moved `docs-site/`, `widget/`, `admin/` to `applications/Agent_Red/`, creating the pre-existing stale references in `session_self_initialization.py` at lines 2145–2147 and 2434–2436 that this REVISED also fixes.
- `DELIB-1914` — Bridge thread gtkb-isolation-018-slice-d-non-functional-content (4 versions, VERIFIED).
- `DELIB-1907` — Bridge thread gtkb-isolation-018-slice-e3-platform-test-disposition (10 versions, VERIFIED).
- `DELIB-1952` — Bridge thread gtkb-isolation-018-agent-red-file-migration (parent re-scope, WITHDRAWN at -010).

## Owner Decisions / Input

The proposal is authorized by `DELIB-20260875` (2026-06-04 AUQ in session 666f7050):

| Decision | Owner answer | Captured in |
|----------|--------------|-------------|
| Authorize the Agent Red child-directory cutover (GTKB-ISOLATION-018)? | "Authorize — mint PAUTH + schedule for next session" | DELIB-20260875 |

The mutation classes minted under PAUTH-PROJECT-GTKB-ISOLATION-AGENT-RED-CUTOVER-AGENT-RED-CHILD-DIRECTORY-CUTOVER (source, narrative_artifact_write, work_item_lifecycle_update, bridge_report_write, test_addition, hook_upgrade) cover all work in scope: `source` = `git mv` of three tracked files + reference fixes in GT-KB scripts/memory; `narrative_artifact_write` = `applications/Agent_Red/CLAUDE.md` documentation update.

No additional owner decisions are required for the in-scope work.

## Proposed Scope

### IP-1: Relocate three tracked Agent-Red deployment-plumbing files

Move via `git mv` (preserves history):

1. `shopify.app.toml` → `applications/Agent_Red/shopify.app.toml`
   - File header explicitly self-identifies as "Agent Red Customer Experience - Shopify App Configuration".
   - Confirmed present at root: `test -f shopify.app.toml` → true at revision time.

2. `package.json` → `applications/Agent_Red/package.json`
   - `"name": "agent-red-customer-experience"`, `"description": "Agent Red Customer Experience - Shopify App"`.
   - Confirmed present at root: `test -f package.json` → true at revision time.

3. `package-lock.json` → `applications/Agent_Red/package-lock.json`
   - Lock companion to package.json; must move with it for npm reproducibility.

### IP-2: Documentation update in applications/Agent_Red/CLAUDE.md

Add a brief operator note: "Shopify CLI commands (`shopify app deploy`, `shopify app dev`, `npm run shopify`) must now run from `applications/Agent_Red/` working directory; `shopify.app.toml`, `package.json`, and `package-lock.json` live there as of ISOLATION-018 cutover."

### IP-3: Update live GT-KB references to moved/relocated Agent Red paths

**`scripts/session_self_initialization.py` — 7 edits:**

Lines 2144–2147 (dict literal):
```python
# Before:
        "root_package": "package.json",
        "widget": "widget/package.json",
        "admin": "admin/package.json",
        "docs_site": "docs-site/package.json",
# After:
        "root_package": "applications/Agent_Red/package.json",
        "widget": "applications/Agent_Red/widget/package.json",
        "admin": "applications/Agent_Red/admin/package.json",
        "docs_site": "applications/Agent_Red/docs-site/package.json",
```

Lines 2434–2436 (`_package_json` direct calls):
```python
# Before:
    widget_package = _package_json(project_root, "widget/package.json")
    docs_package = _package_json(project_root, "docs-site/package.json")
    admin_package = _package_json(project_root, "admin/package.json")
# After:
    widget_package = _package_json(project_root, "applications/Agent_Red/widget/package.json")
    docs_package = _package_json(project_root, "applications/Agent_Red/docs-site/package.json")
    admin_package = _package_json(project_root, "applications/Agent_Red/admin/package.json")
```

**`scripts/rehearse/_production_effects.py` — 1 edit (line 328):**
```python
# Before:
        "shopify.app.toml",
# After:
        "applications/Agent_Red/shopify.app.toml",
```
Context: `_DISPOSITION_MOVE` classification table — classifies the Shopify config as a "MOVE" disposition file; must track at new path.

**`scripts/rehearse/_dashboard_regen.py` — 1 edit (line 83):**
```python
# Before:
    "package.json",
# After:
    "applications/Agent_Red/package.json",
```
Context: `_OPTIONAL_SANDBOX_INPUTS` — rehearsal lane warns if missing; must track at new location.

**`memory/topics/deployment.md` — 1 edit (line 70):**
```
# Before:
Config file: `shopify.app.toml` (repo root).
# After:
Config file: `applications/Agent_Red/shopify.app.toml` (moved from repo root in ISOLATION-018).
```

### Explicit deferrals (NOT in scope)

- **Root `assets/` directory** (96 tracked Docusaurus build artifacts) — deferred to follow-on hygiene slice.
- **Root `docs-site/` directory** (untracked stale-build residue) — deferred to hygiene-sweep cleanup.

## Specification-Derived Verification Plan

| Spec / Clause | Verification Action | Expected Evidence |
|--------------|---------------------|-------------------|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 ("strict descendant of `<gt-kb-root>/applications/`") | `test -f applications/Agent_Red/shopify.app.toml && test -f applications/Agent_Red/package.json && test -f applications/Agent_Red/package-lock.json` | All three exist at destination |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 (corollary: not at platform root) | `test ! -f shopify.app.toml && test ! -f package.json && test ! -f package-lock.json` | All three absent from root |
| `.claude/rules/project-root-boundary.md` | `git ls-files shopify.app.toml package.json package-lock.json` returns empty | Empty output |
| Git history preservation | `git log --follow --oneline applications/Agent_Red/shopify.app.toml` | Shows commits from before the move |
| Reference fix — session_self_initialization.py | `grep -c 'applications/Agent_Red' scripts/session_self_initialization.py` increases; root-relative package.json refs absent | 7 updated lines |
| Reference fix — _production_effects.py | `grep -n 'shopify\.app\.toml' scripts/rehearse/_production_effects.py` shows `applications/Agent_Red/` | Correct path |
| Reference fix — _dashboard_regen.py | `grep -n '"package\.json"' scripts/rehearse/_dashboard_regen.py` shows `applications/Agent_Red/` | Correct path |
| Reference fix — deployment.md | `grep -n 'shopify.app.toml' memory/topics/deployment.md` shows new path | Correct path |

Composite verification command:

```bash
test -f applications/Agent_Red/shopify.app.toml && \
  test -f applications/Agent_Red/package.json && \
  test -f applications/Agent_Red/package-lock.json && \
  test ! -f shopify.app.toml && \
  test ! -f package.json && \
  test ! -f package-lock.json && \
  git log --follow --oneline applications/Agent_Red/shopify.app.toml | head -3 && \
  grep -q '"root_package".*applications/Agent_Red/package.json' scripts/session_self_initialization.py && \
  grep -q 'applications/Agent_Red/shopify.app.toml' scripts/rehearse/_production_effects.py && \
  grep -q 'applications/Agent_Red/package.json' scripts/rehearse/_dashboard_regen.py && \
  echo "ALL CHECKS PASS"
```

Doctor + regression:

```bash
python -m pytest groundtruth-kb/tests/ -k "isolation or registry or root_boundary" --tb=short -q --timeout=60
python -m groundtruth_kb project doctor
ruff check scripts/session_self_initialization.py scripts/rehearse/_production_effects.py scripts/rehearse/_dashboard_regen.py
ruff format --check scripts/session_self_initialization.py scripts/rehearse/_production_effects.py scripts/rehearse/_dashboard_regen.py
```

## Acceptance Criteria

1. Three `git mv` operations complete cleanly with history preserved.
2. The composite verification command above exits 0 / prints "ALL CHECKS PASS".
3. `applications/Agent_Red/CLAUDE.md` includes the operator-path note.
4. No live GT-KB code, rehearsal script, or operational-memory reference points at a root-relative location for any of the three moved files. All five known live reference sites updated by IP-3.
5. Doctor checks that currently pass continue to pass.
6. The `.gtkb-app-isolation.json` registry edit is deferred (default) or landed inline.

## Risks / Rollback

- **Shopify CLI workflow break:** mitigated by CLAUDE.md operator-note.
- **Session startup behavior change:** `session_self_initialization.py` will find sub-package `package.json` files at their correct `applications/Agent_Red/` locations, rather than silently failing on stale paths. This is a fix; startup version display will improve.
- **Rollback:** trivial — `git mv` reversible; IP-3 edits are single-line string replacements.

## Files Expected To Change

- `shopify.app.toml` → `applications/Agent_Red/shopify.app.toml` (git mv)
- `package.json` → `applications/Agent_Red/package.json` (git mv)
- `package-lock.json` → `applications/Agent_Red/package-lock.json` (git mv)
- `applications/Agent_Red/CLAUDE.md` — operator-path note
- `scripts/session_self_initialization.py` — 7 path string updates (lines 2144–2147, 2434–2436)
- `scripts/rehearse/_production_effects.py` — 1 path update (line 328)
- `scripts/rehearse/_dashboard_regen.py` — 1 path update (line 83)
- `memory/topics/deployment.md` — 1 path description update (line 70)

## Recommended Commit Type

`refactor:` — file moves preserving behavior + reference fixes maintaining reference integrity.

## Pre-Filing Preflight Evidence

The applicability preflight was run on the indexed operative file `bridge/gtkb-isolation-018-agent-red-cutover-001.md` (NO-GO review version). The preflight passed with `preflight_passed: true`, `missing_required_specs: []`, packet_hash `sha256:a02b4576c6d24f780215bcfb3be5c02d10cfcf59b2c8785054d62ebce4a8169a`. This REVISED-1 adds no new required-spec triggers (additional target_paths are source/memory, no new governance artifacts). The same preflight result is carried forward for this REVISED.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
