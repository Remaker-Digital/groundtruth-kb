REVISED

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 77a7836d-1aac-4786-ae0f-3cf8b433b66c
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, interactive Prime Builder session driving 5-item dispatch

# Implementation Proposal — GTKB-ISOLATION-018 Agent Red Child-Directory Cutover (Closeout Stragglers) (REVISED-3)

bridge_kind: implementation_proposal
Document: gtkb-isolation-018-agent-red-cutover
Version: 007
Date: 2026-06-05 UTC
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Responds to: bridge/gtkb-isolation-018-agent-red-cutover-006.md (Codex NO-GO)

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
  "scripts/rehearse/_dashboard_regen.py",
  "memory/topics/deployment.md",
  "Dockerfile.test",
  "memory/topics/testing.md"
]

implementation_scope: source

## Response to NO-GO -006

Codex NO-GO `-006` raised two findings on REVISED-2 (`-005`):

- **F1 (P1):** Production-effects map would double-prefix the moved Shopify path. The renderer at `scripts/rehearse/_production_effects.py:928-931` unconditionally prefixes every `MOVE` row with `applications/Agent_Red/`. The -005 plan to change the source list from `"shopify.app.toml"` to `"applications/Agent_Red/shopify.app.toml"` (while keeping disposition `MOVE`) would produce `applications/Agent_Red/applications/Agent_Red/shopify.app.toml` in the rendered map — corrupting the migration-evidence surface.
- **F2 (P2):** ruff `check` and `format --check` commands omit `platform_tests/scripts/test_rehearse_production_effects.py` (one of the changed Python files declared in -005's target_paths).

This REVISED-3 closes both findings by **selecting Codex's recommended Option 1**: preserve the renderer invariant by leaving `_production_effects.py` and `test_rehearse_production_effects.py` UNCHANGED. The classifier's source path `"shopify.app.toml"` is a **legacy-root probe**: post-cutover, the file does not exist at the legacy root, the classifier reports `exists=false`, and that absence IS the closure evidence the production-effects map needs to record. The renderer's unconditional `applications/Agent_Red/` prefix is correct **post-cutover semantics** for a MOVE row, not double-prefix. Mutating the probe path corrupts the contract.

F2 is auto-resolved: with `_production_effects.py` and `test_rehearse_production_effects.py` removed from target_paths, the ruff scope for the remaining changed Python files is complete.

All other -005 changes (3 `git mv` operations, `applications/Agent_Red/CLAUDE.md` doc, IP-3 session_self_initialization.py + _dashboard_regen.py + deployment.md edits, IP-4 Dockerfile.test + testing.md edits) carry forward byte-equivalent.

## What changed vs -005

| Element | -005 | -007 (this REVISED-3) | Rationale |
|---|---|---|---|
| target_paths count | 14 | 12 | F1 fix: drop _production_effects.py + test_rehearse_production_effects.py |
| IP-3 _production_effects.py edit | 1 line change | **REMOVED** | F1 Option 1: legacy-root probe semantics preserved |
| IP-4 test_rehearse_production_effects.py edit | 2 line changes | **REMOVED** | F1: dropped because the change was conditional on the _production_effects.py edit |
| ruff scope | session_self_initialization, _production_effects, _dashboard_regen | session_self_initialization, _dashboard_regen | F2 auto-resolved: scope matches the now-narrower set of changed Python files |
| Composite verification command | grep on _production_effects.py | **REPLACED** with no-double-prefix assertion against production-effects map | F1 backup: defense-in-depth check that post-cutover output does not contain `applications/Agent_Red/applications/Agent_Red/` |
| Acceptance criteria #6 (production-effects test) | required PASS with updated path | **REPLACED** with: production-effects-map.md output contains no double-prefixed MOVE target | F1: test behavior unchanged (no edit) but defense-in-depth check added |

## Bridge INDEX Audit-Trail Evidence

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`, bridge/INDEX.md is the canonical workflow state; bridge files are append-only and prior versions are never rewritten or deleted.

For this thread, the INDEX entry after this REVISED-3 filing will be:

```
Document: gtkb-isolation-018-agent-red-cutover
REVISED: bridge/gtkb-isolation-018-agent-red-cutover-007.md  ← this revision
NO-GO: bridge/gtkb-isolation-018-agent-red-cutover-006.md
REVISED: bridge/gtkb-isolation-018-agent-red-cutover-005.md
NO-GO: bridge/gtkb-isolation-018-agent-red-cutover-004.md
REVISED: bridge/gtkb-isolation-018-agent-red-cutover-003.md
NO-GO: bridge/gtkb-isolation-018-agent-red-cutover-002.md
NEW: bridge/gtkb-isolation-018-agent-red-cutover-001.md
```

The REVISED status line is inserted at the top of the version list for this Document entry; no prior version is removed or modified.

## Cutover Surface Inventory (review packet)

Per `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`, the bulk-operation review-packet inventory of all surfaces touched by this cutover is enumerated below. The inventory is supported by the formal-artifact-approval packet for the governing ADR (`.groundtruth/formal-artifact-approvals/2026-04-26-adr-isolation-application-placement.json`, sha256 `c682522806d79d0b27123ac3d2833aaaf83f5e050ab5618df3afe3b16e9e59b8`) and the owner-AUQ packet captured at `DELIB-20260875` for the PAUTH mint.

| # | Surface | Operation | Rationale |
|---|---------|-----------|-----------|
| 1 | `shopify.app.toml` → `applications/Agent_Red/shopify.app.toml` | git mv | Agent Red config; ADR placement boundary |
| 2 | `package.json` → `applications/Agent_Red/package.json` | git mv | Agent Red npm config; ADR boundary |
| 3 | `package-lock.json` → `applications/Agent_Red/package-lock.json` | git mv | npm lock companion |
| 4 | `applications/Agent_Red/CLAUDE.md` | edit | Operator-path note for Shopify CLI |
| 5 | `scripts/session_self_initialization.py` (lines 2144, 2145–2147, 2434–2436) | edit | Live root-package + sub-package references |
| 6 | `scripts/rehearse/_production_effects.py` (line 328) | **probe-only (no edit)** | Legacy-root probe semantics preserved; renderer's MOVE-prefix invariant requires source list to point at legacy-root paths |
| 7 | `scripts/rehearse/_dashboard_regen.py` (line 83) | edit | `_OPTIONAL_SANDBOX_INPUTS` |
| 8 | `memory/topics/deployment.md` (line 70) | edit | Operational memory of config path |
| 9 | `Dockerfile.test` (line 111) | edit | `COPY shopify.app.toml` source path |
| 10 | `memory/topics/testing.md` (lines 125, 127) | edit | Container file availability docs |
| 11 | `platform_tests/scripts/test_rehearse_production_effects.py` (lines 228–236) | **probe-only (no edit)** | Test exercises the renderer's MOVE-prefix invariant; the probe-only treatment of item 6 means the test's assertion `row["path"] == "shopify.app.toml"` continues to be correct post-cutover |
| 12 | `.github/workflows/build-test-host.yml` (line 26) | inspect (no change) | Docker build context is `.`; Dockerfile.test edit propagates |

## Reference Analysis (carried forward from -005 minus the F1-blocked rows)

| File | Lines | Classification | Action |
|------|-------|---------------|--------|
| `scripts/session_self_initialization.py` | 2144 | **OPERATIVE** — `"root_package": "package.json"` reads the Agent Red root `package.json` being moved in this slice | Update to `"applications/Agent_Red/package.json"` |
| `scripts/session_self_initialization.py` | 2145–2147, 2434–2436 | **PRE-EXISTING STALE** — `widget/package.json`, `admin/package.json`, `docs-site/package.json` were moved to `applications/Agent_Red/` in prior sub-slices (DELIB-1915 docs-cluster). | Update to `applications/Agent_Red/widget/`, `applications/Agent_Red/admin/`, `applications/Agent_Red/docs-site/` paths |
| `scripts/rehearse/_production_effects.py` | 328 | **PROBE-ONLY (no edit)** — `"shopify.app.toml"` in `_DISPOSITION_MOVE` is the legacy-root probe; renderer at L928-931 unconditionally prefixes `applications/Agent_Red/` for MOVE rows. Post-cutover the probe correctly reports absence and the renderer correctly emits the relocation target. | No edit |
| `scripts/rehearse/_dashboard_regen.py` | 83 | **OPERATIVE** — `"package.json"` in `_OPTIONAL_SANDBOX_INPUTS` | Update to `"applications/Agent_Red/package.json"` |
| `memory/topics/deployment.md` | 70 | **OPERATIVE** — states "Config file: `shopify.app.toml` (repo root)" | Update path description |
| `Dockerfile.test` | 111 | **OPERATIVE** — `COPY shopify.app.toml ./shopify.app.toml` reads root path that no longer exists after move | Update source to `applications/Agent_Red/shopify.app.toml` |
| `memory/topics/testing.md` | 125, 127 | **OPERATIVE** — Container file availability docs list `shopify.app.toml` as a root-COPY'd file | Update path description |
| `platform_tests/scripts/test_rehearse_production_effects.py` | 228–236 | **PROBE-ONLY (no edit)** — Test exercises renderer's MOVE-prefix invariant. With the probe-only treatment of `_production_effects.py:328`, the test's existing assertions `row["path"] == "shopify.app.toml"` and `disposition == "MOVE"` remain correct: the classifier sees the file's absence at the legacy root, classifies as MOVE-disposition closure, and the renderer correctly emits `applications/Agent_Red/shopify.app.toml` as the relocation target. | No edit |
| `.github/workflows/build-test-host.yml` | 26 | **INSPECTED** — `docker build -f Dockerfile.test ... .` uses `.` as build context; the Dockerfile.test edit (item 9 above) provides the new source path. The workflow line itself requires no change. | No edit |

## Claim

GTKB-ISOLATION-018 (Execute Agent Red child-directory cutover) is structurally complete for all bulk content (PDF/docs/legal/code/test-disposition sub-slices VERIFIED), but three tracked Agent-Red deployment-plumbing files remain at the GT-KB platform root and must be relocated into `applications/Agent_Red/` to satisfy ADR-ISOLATION-APPLICATION-PLACEMENT-001's strict-descendant boundary. Additionally, six GT-KB source/memory/docker files contain live references to those root-path locations and must be updated as part of the same slice to preserve reference integrity and prevent build/test breakage after the move. The production-effects classifier and its regression test exercise a legacy-root probe invariant; per Codex NO-GO -006 F1 Option 1, those two surfaces are inspected and confirmed to require no edit.

This proposal cuts the closeout stragglers, corrects all known live GT-KB references (including build, test container, and operational-memory surfaces), preserves the legacy-root probe semantics in the production-effects classifier, and explicitly defers two ambiguous follow-ons (the 96-file `assets/` Docusaurus build artifacts and the untracked root `docs-site/` directory) to a hygiene slice.

## Requirement Sufficiency

Existing requirements sufficient.

ADR-ISOLATION-APPLICATION-PLACEMENT-001 and the Mandatory Project Root Boundary rule (`.claude/rules/project-root-boundary.md`) both apply directly to the three target files. The reference fixups are mechanical correctness repairs entailed by the file moves — no new requirements needed. The F1 finding's preservation of the legacy-root probe is a renderer-invariant-respecting interpretation of the existing ADR-driven cutover requirement.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`. Source paths (`shopify.app.toml`, `package.json`, `package-lock.json`) are at GT-KB platform root pending migration. Destination paths are inside `applications/Agent_Red/`. All reference-update files (`Dockerfile.test`, `memory/topics/testing.md`, plus carried-forward IP-3 sites) are also inside `E:\GT-KB`.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — load-bearing contract: adopter application files live strict-descendant of `<gt-kb-root>/applications/`. The three root files violate the boundary today; the cutover restores compliance. Formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-04-26-adr-isolation-application-placement.json` (sha256 `c682522806d79d0b27123ac3d2833aaaf83f5e050ab5618df3afe3b16e9e59b8`).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the bridge protocol; bridge/INDEX.md is canonical workflow state per `CLAUSE-INDEX-IS-CANONICAL`. See § Bridge INDEX Audit-Trail Evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal must cite every relevant governing spec.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived verification evidence (the verification plan below maps the ADR placement clause to filesystem assertions plus the Dockerfile/memory surface checks plus the no-double-prefix regression assertion).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — proposal carries Project Authorization, Project, Work Item header lines.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — file moves preserved as durable artifact under append-only bridge audit trail.
- `GOV-STANDING-BACKLOG-001` — GTKB-ISOLATION-018 is the active work item in the standing backlog; this proposal advances its closure. See § Cutover Surface Inventory for the bulk-operation review-packet evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; cutover artifacts are MemBase-tracked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; work item lifecycle preserved.
- `.claude/rules/project-root-boundary.md` — operational rule restating the ADR boundary for Agent Red specifically.
- `applications/Agent_Red/.gtkb-app-isolation.json` — registry of bucket-A application-owned directories.

## Prior Deliberations

- `DELIB-20260875` — Owner authorization 2026-06-04: AUQ in session 666f7050 authorizing this cutover with PAUTH + next-session schedule (the operative owner decision; review-packet captured in DA).
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` — Pending-migration waiver covering Agent Red files at GT-KB root *until ISOLATION-018 reaches VERIFIED*. This proposal contributes to the waiver-expiry condition.
- `DELIB-S334-OQ-E3-OPTION-A` — Owner-selected disposition for platform tests staying at GT-KB root.
- `DELIB-1948` — Bridge thread gtkb-isolation-018-slice-b-pdf-cluster (12 versions, VERIFIED) — sub-slice precedent.
- `DELIB-1915` — Bridge thread gtkb-isolation-018-slice-c-docs-cluster (11 versions, VERIFIED) — moved `docs-site/`, `widget/`, `admin/` to `applications/Agent_Red/`, creating the pre-existing stale references this REVISED also fixes.
- `DELIB-1914` — Bridge thread gtkb-isolation-018-slice-d-non-functional-content (4 versions, VERIFIED).
- `DELIB-1907` — Bridge thread gtkb-isolation-018-slice-e3-platform-test-disposition (10 versions, VERIFIED).
- `DELIB-1952` — Bridge thread gtkb-isolation-018-agent-red-file-migration (parent re-scope, WITHDRAWN at -010).
- `DELIB-1382`, `DELIB-1384`, `DELIB-1385` — production-effects-map review history (surfaced by Codex -006 prior-deliberations search).

## Owner Decisions / Input

The proposal is authorized by `DELIB-20260875` (2026-06-04 AUQ in session 666f7050):

| Decision | Owner answer | Captured in |
|----------|--------------|-------------|
| Authorize the Agent Red child-directory cutover (GTKB-ISOLATION-018)? | "Authorize — mint PAUTH + schedule for next session" | DELIB-20260875 |

In addition, this REVISED-3 cites the standing formal-artifact-approval packet for the governing ADR (`.groundtruth/formal-artifact-approvals/2026-04-26-adr-isolation-application-placement.json`) as the bulk-operation evidence anchor required by `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`. The packet sha256 is `c682522806d79d0b27123ac3d2833aaaf83f5e050ab5618df3afe3b16e9e59b8`.

The mutation classes minted under PAUTH-PROJECT-GTKB-ISOLATION-AGENT-RED-CUTOVER-AGENT-RED-CHILD-DIRECTORY-CUTOVER (source, narrative_artifact_write, work_item_lifecycle_update, bridge_report_write, test_addition, hook_upgrade) cover all in-scope work: `source` covers the `git mv` operations plus reference fixes in GT-KB scripts/memory/docker surfaces; `narrative_artifact_write` covers the `applications/Agent_Red/CLAUDE.md` documentation update.

No additional owner decisions are required for the in-scope work. The F1 finding's preserve-the-probe choice is a deterministic re-interpretation of the existing renderer-invariant contract, not a new owner-decision class.

## Proposed Scope

### IP-1: Relocate three tracked Agent-Red deployment-plumbing files

Move via `git mv` (preserves history):

1. `shopify.app.toml` → `applications/Agent_Red/shopify.app.toml`
2. `package.json` → `applications/Agent_Red/package.json`
3. `package-lock.json` → `applications/Agent_Red/package-lock.json`

(Confirmed present at root via `test -f` at revision time.)

### IP-2: Documentation update in applications/Agent_Red/CLAUDE.md

Add a brief operator note: "Shopify CLI commands (`shopify app deploy`, `shopify app dev`, `npm run shopify`) must now run from `applications/Agent_Red/` working directory; `shopify.app.toml`, `package.json`, and `package-lock.json` live there as of ISOLATION-018 cutover."

### IP-3: Update live GT-KB references to moved/relocated Agent Red paths

**`scripts/session_self_initialization.py` — 7 edits** (lines 2144–2147 dict literal + 2434–2436 `_package_json` calls) per the -005 spec.

**`scripts/rehearse/_dashboard_regen.py` — 1 edit (line 83):** `"package.json"` → `"applications/Agent_Red/package.json"`.

**`memory/topics/deployment.md` — 1 edit (line 70):** `Config file: \`shopify.app.toml\` (repo root)` → `Config file: \`applications/Agent_Red/shopify.app.toml\` (moved from repo root in ISOLATION-018)`.

**`scripts/rehearse/_production_effects.py` — REMOVED from scope.** Per Codex NO-GO -006 F1 Option 1, line 328's `"shopify.app.toml"` entry in `_DISPOSITION_MOVE` is a legacy-root probe; the renderer at L928-931 unconditionally prefixes `applications/Agent_Red/` for MOVE rows. Post-cutover, the probe correctly reports `exists=false` and the renderer correctly emits the relocation target. Mutating the probe path would corrupt the renderer invariant by causing double-prefix.

### IP-4: Cover NO-GO -004 F2 build/container surfaces

**`Dockerfile.test` — 1 edit (line 111):**

```dockerfile
# Before:
COPY shopify.app.toml ./shopify.app.toml
# After:
COPY applications/Agent_Red/shopify.app.toml ./shopify.app.toml
```

Container destination path is preserved (`./shopify.app.toml` inside the test-host image) so downstream container-runtime callers see the same file location; only the build-context source path changes to track the moved file. The build context `.` already includes `applications/Agent_Red/`, so this single edit is sufficient.

**`memory/topics/testing.md` — 1 edit (line 127):**

```
# Before:
- `pyproject.toml`, `shopify.app.toml`, `CLAUDE.md`
# After:
- `pyproject.toml`, `shopify.app.toml` (sourced from `applications/Agent_Red/shopify.app.toml`), `CLAUDE.md`
```

The container path inside the test-host image remains `shopify.app.toml` (unchanged), but the operational-memory doc clarifies that the file is sourced from the new `applications/Agent_Red/` location.

**`platform_tests/scripts/test_rehearse_production_effects.py` — REMOVED from scope.** Per Codex NO-GO -006 F1 Option 1, since the underlying `scripts/rehearse/_production_effects.py:328` change is dropped, the test's existing assertions remain correct without edit. The test stages `shopify.app.toml` at the temp project root, the classifier sees it as MOVE-disposition (or absent post-cutover, classified by the same `_DISPOSITION_MOVE` probe), and the renderer correctly emits the relocation target. No test edit is required because no classifier source change occurs.

**`.github/workflows/build-test-host.yml` — non-mutating (inspected only):**

Line 26 invokes `docker build -f Dockerfile.test ... .`. The build context `.` is the repository root. After the `git mv` operations and the Dockerfile.test edit (IP-4 above), the Dockerfile references `applications/Agent_Red/shopify.app.toml` which resolves correctly in the build context. The workflow YAML itself requires no edit; the Dockerfile.test edit propagates.

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
| Reference fix — _dashboard_regen.py | `grep -n '"package\.json"' scripts/rehearse/_dashboard_regen.py` shows `applications/Agent_Red/` | Correct path |
| Reference fix — deployment.md | `grep -n 'shopify.app.toml' memory/topics/deployment.md` shows new path | Correct path |
| Dockerfile.test COPY source resolves after move | `grep -n 'COPY applications/Agent_Red/shopify.app.toml' Dockerfile.test` | Match present |
| testing.md doc updated | `grep -n 'applications/Agent_Red/shopify.app.toml' memory/topics/testing.md` | Match present |
| F1 backup: production-effects-map output has no double-prefixed MOVE target | Generate map via `python scripts/rehearse/_production_effects.py` (or via the production-effects-map artifact in evidence dir); `grep -c 'applications/Agent_Red/applications/Agent_Red' production-effects-map.md` returns 0 | No double-prefix in output |
| Production-effects regression suite green (no edit; verifies probe + renderer still work) | `python -m pytest platform_tests/scripts/test_rehearse_production_effects.py -q --tb=short` | All pass |
| Production-effects classifier probe correctness | `grep -n '"shopify\.app\.toml"' scripts/rehearse/_production_effects.py` confirms legacy-root probe is preserved | Match at line 328 |

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
  grep -q 'applications/Agent_Red/package.json' scripts/rehearse/_dashboard_regen.py && \
  grep -q 'COPY applications/Agent_Red/shopify.app.toml' Dockerfile.test && \
  grep -q 'applications/Agent_Red/shopify.app.toml' memory/topics/testing.md && \
  grep -q '"shopify\.app\.toml"' scripts/rehearse/_production_effects.py && \
  echo "ALL CHECKS PASS"
```

Doctor + targeted regression:

```bash
python -m pytest platform_tests/scripts/test_rehearse_production_effects.py -q --tb=short --timeout=60
python -m pytest groundtruth-kb/tests/ -k "isolation or registry or root_boundary" --tb=short -q --timeout=60
python -m groundtruth_kb project doctor
ruff check scripts/session_self_initialization.py scripts/rehearse/_dashboard_regen.py
ruff format --check scripts/session_self_initialization.py scripts/rehearse/_dashboard_regen.py
```

(The ruff scope is now `session_self_initialization.py` and `_dashboard_regen.py` only — `_production_effects.py` is dropped from scope per F1, so it does not need ruff coverage in this slice. F2 is auto-resolved.)

## Acceptance Criteria

1. Three `git mv` operations complete cleanly with history preserved.
2. The composite verification command above exits 0 / prints "ALL CHECKS PASS".
3. `applications/Agent_Red/CLAUDE.md` includes the operator-path note.
4. No live GT-KB code, rehearsal script, build-test container, test fixture, or operational-memory reference points at a root-relative location for any of the three moved files — EXCEPT the `scripts/rehearse/_production_effects.py:328` legacy-root probe, which is intentionally preserved per F1.
5. `Dockerfile.test` builds cleanly when invoked via the build-test-host workflow (the COPY source resolves at the new path; the container destination path is preserved).
6. `test_rehearse_production_effects.py::test_run_classifies_shopify_app_toml_as_move_with_deploy_blocking` passes UNCHANGED (no edit) — confirming the probe + renderer invariant is preserved.
7. **F1 backup:** the production-effects-map output (whether emitted by direct invocation or by the regression test fixture) contains no instance of `applications/Agent_Red/applications/Agent_Red/`.
8. Doctor checks that currently pass continue to pass.
9. Both bridge applicability preflight and ADR/DCL clause preflight exit 0 (no blocking gaps) when run against `bridge/gtkb-isolation-018-agent-red-cutover-007.md` after INDEX is updated to point at this REVISED.

## Risks / Rollback

- **Shopify CLI workflow break:** mitigated by CLAUDE.md operator-note.
- **Session startup behavior change:** `session_self_initialization.py` will find sub-package `package.json` files at their correct `applications/Agent_Red/` locations rather than silently failing on stale paths. This is a fix.
- **Test-host container build break risk:** mitigated by IP-4 Dockerfile.test edit; build context already includes `applications/Agent_Red/`.
- **Production-effects probe regression risk:** mitigated by the F1 backup acceptance criterion (no double-prefix in output); the probe + renderer invariant is preserved by leaving the classifier source unchanged.
- **Rollback:** trivial — `git mv` reversible; IP-3 edits are single-line string replacements; `git revert <cutover-commit>` restores prior state in one operation.

## Files Expected To Change

- `shopify.app.toml` → `applications/Agent_Red/shopify.app.toml` (git mv)
- `package.json` → `applications/Agent_Red/package.json` (git mv)
- `package-lock.json` → `applications/Agent_Red/package-lock.json` (git mv)
- `applications/Agent_Red/CLAUDE.md` — operator-path note
- `scripts/session_self_initialization.py` — 7 path string updates
- `scripts/rehearse/_dashboard_regen.py` — 1 path update
- `memory/topics/deployment.md` — 1 path description update
- `Dockerfile.test` — 1 COPY source update
- `memory/topics/testing.md` — 1 path description update

(Files INSPECTED-ONLY, no edit: `scripts/rehearse/_production_effects.py` line 328, `platform_tests/scripts/test_rehearse_production_effects.py` lines 228–236, `.github/workflows/build-test-host.yml` line 26.)

## Recommended Commit Type

`refactor:` — file moves preserving behavior + reference fixes maintaining reference integrity across source, build, and container surfaces. The production-effects probe + test surfaces are explicitly preserved unchanged per the F1 renderer-invariant constraint.

## Revision Notes (REVISED-3 vs REVISED-2 / -005)

- **F1 (P1) resolution:** Selected Codex Option 1. Dropped `scripts/rehearse/_production_effects.py` from `target_paths` and removed its IP-3 edit. Dropped `platform_tests/scripts/test_rehearse_production_effects.py` from `target_paths` and removed its IP-4 edit. Updated § Cutover Surface Inventory (items 6 and 11) and § Reference Analysis to mark these surfaces as PROBE-ONLY (no edit). Added an F1-backup acceptance criterion + verification action that the rendered production-effects map contains no double-prefix. Rationale: the `_production_effects.py:328` entry is a legacy-root probe whose absence post-cutover IS the closure evidence; the renderer's unconditional `applications/Agent_Red/` prefix for MOVE rows is correct post-cutover semantics, not a defect. Mutating the probe would corrupt the renderer invariant.
- **F2 (P2) resolution:** Auto-resolved by F1. With `_production_effects.py` and `test_rehearse_production_effects.py` removed from the change set, the ruff scope (`session_self_initialization.py`, `_dashboard_regen.py`) correctly matches the now-narrower set of changed Python files.
- **All -005 surface inventory carried forward** for the 9 remaining edit surfaces + 3 inspected-non-mutating surfaces.
- **Specification Links unchanged** vs -005 (all clauses already cited).
- **Owner Decisions / Input unchanged** vs -005 (no new owner-decision class introduced by the F1 re-interpretation).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

*Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>*
