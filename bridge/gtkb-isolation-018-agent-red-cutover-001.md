NEW
author_identity: Claude
author_harness_id: B
author_session_context_id: d48e213b-3071-4623-8f6a-eac31115e706
author_model: Claude
author_model_version: Opus 4.7 (1M context)
author_model_configuration: Claude Code default

# Implementation Proposal — GTKB-ISOLATION-018 Agent Red Child-Directory Cutover (Closeout Stragglers)

bridge_kind: prime_proposal
Document: gtkb-isolation-018-agent-red-cutover
Version: 001
Date: 2026-06-04 UTC
Author: Prime Builder (Claude Code, harness B)

Project Authorization: PAUTH-PROJECT-GTKB-ISOLATION-AGENT-RED-CUTOVER-AGENT-RED-CHILD-DIRECTORY-CUTOVER
Project: PROJECT-GTKB-ISOLATION-AGENT-RED-CUTOVER
Work Item: GTKB-ISOLATION-018

target_paths: ["applications/Agent_Red/shopify.app.toml", "applications/Agent_Red/package.json", "applications/Agent_Red/package-lock.json", "shopify.app.toml", "package.json", "package-lock.json", "applications/Agent_Red/CLAUDE.md"]

implementation_scope: source

## Claim

GTKB-ISOLATION-018 (Execute Agent Red child-directory cutover) is structurally complete for all bulk content (PDF/docs/legal/code/test-disposition sub-slices VERIFIED), but three tracked Agent-Red deployment-plumbing files remain at the GT-KB platform root and must be relocated into `applications/Agent_Red/` to satisfy ADR-ISOLATION-APPLICATION-PLACEMENT-001's strict-descendant boundary. This proposal narrowly cuts the closeout stragglers, retires the pending-migration waiver scope incrementally, and explicitly defers two ambiguous follow-ons (the 96-file `assets/` Docusaurus build artifacts and the untracked root `docs-site/` directory) to a hygiene slice.

The three files in scope are unambiguously Agent-Red-specific (Shopify app config + npm manifest naming Agent Red as the package), are not referenced from any non-Agent-Red GT-KB code path, and have direct destination homes in `applications/Agent_Red/`.

## Requirement Sufficiency

**Existing requirements sufficient.** ADR-ISOLATION-APPLICATION-PLACEMENT-001 ("The application's filesystem boundary is a strict descendant of `<gt-kb-root>/applications/`") and the Mandatory Project Root Boundary rule (`.claude/rules/project-root-boundary.md`: "All GT-KB application files MUST be within `E:\GT-KB\applications\`; Agent Red application files MUST be within `E:\GT-KB\applications\Agent_Red\`") both apply directly to the three target files. No new requirements needed.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`. Source paths (`shopify.app.toml`, `package.json`, `package-lock.json`) are at GT-KB platform root pending migration. Destination paths are inside `applications/Agent_Red/`. `applications/Agent_Red/CLAUDE.md` is the existing application-scope guidance file that may receive a documentation update (add operator note about the new `cd applications/Agent_Red/` requirement for Shopify CLI invocations).

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
- `DELIB-S334-OQ-E3-OPTION-A` — Owner-selected disposition for platform tests staying at GT-KB root (defines the boundary the cutover does NOT cross — platform-test files are out of scope).
- `DELIB-1948` — Bridge thread gtkb-isolation-018-slice-b-pdf-cluster (12 versions, VERIFIED) — sub-slice precedent.
- `DELIB-1915` — Bridge thread gtkb-isolation-018-slice-c-docs-cluster (11 versions, VERIFIED) — sub-slice precedent.
- `DELIB-1914` — Bridge thread gtkb-isolation-018-slice-d-non-functional-content (4 versions, VERIFIED) — sub-slice precedent.
- `DELIB-1907` — Bridge thread gtkb-isolation-018-slice-e3-platform-test-disposition (10 versions, VERIFIED) — establishes Option A test-disposition boundary.
- `DELIB-1952` — Bridge thread gtkb-isolation-018-agent-red-file-migration (parent re-scope, WITHDRAWN at -010 in favor of sub-slice decomposition; this proposal is one of the remaining sub-slice closures).

## Owner Decisions / Input

The proposal is authorized by `DELIB-20260875` (2026-06-04 AUQ in session 666f7050):

| Decision | Owner answer | Captured in |
|----------|--------------|-------------|
| Authorize the Agent Red child-directory cutover (GTKB-ISOLATION-018)? | "Authorize — mint PAUTH + schedule for next session" | DELIB-20260875 |

The mutation classes minted under PAUTH-PROJECT-GTKB-ISOLATION-AGENT-RED-CUTOVER-AGENT-RED-CHILD-DIRECTORY-CUTOVER (source, narrative_artifact_write, work_item_lifecycle_update, bridge_report_write, test_addition, hook_upgrade) cover the work in scope: source = `git mv` of three tracked files; narrative_artifact_write = `applications/Agent_Red/CLAUDE.md` documentation update for the operator path note.

No additional owner decisions are required for the in-scope work. Two deferral choices (assets/ migration scope, untracked docs-site/ cleanup) are explicitly NOT proposed for this slice; if the owner wants either pulled forward, that would require a separate AUQ.

## Proposed Scope

### IP-1: Relocate three tracked Agent-Red deployment-plumbing files

Move via `git mv` (preserves history):

1. `shopify.app.toml` → `applications/Agent_Red/shopify.app.toml`
   - File header explicitly self-identifies as "Agent Red Customer Experience - Shopify App Configuration".
   - Reference scan returned zero non-Agent-Red references in GT-KB (excluding `node_modules/` and `applications/Agent_Red/`).

2. `package.json` → `applications/Agent_Red/package.json`
   - `"name": "agent-red-customer-experience"`, `"description": "Agent Red Customer Experience - Shopify App"`.
   - Scripts (`shopify`, `deploy`, `dev`) wrap Shopify CLI invocations; only meaningful when run in the Shopify-app-rooted directory.

3. `package-lock.json` → `applications/Agent_Red/package-lock.json`
   - Lock companion to package.json; must move with it for npm reproducibility.

### IP-2: Documentation update in applications/Agent_Red/CLAUDE.md

Add a brief operator note under "Adding Commercial Features" (or a new "Shopify CLI workflow" subsection): "Shopify CLI commands (`shopify app deploy`, `shopify app dev`, `npm run shopify`) must now run from `applications/Agent_Red/` working directory; `shopify.app.toml`, `package.json`, and `package-lock.json` live there as of cutover."

### Explicit deferrals (NOT in scope for this proposal)

- **Root `assets/` directory** (96 tracked files: `assets/css/*.css`, `assets/js/*.js`). These appear to be Docusaurus build artifacts. `applications/Agent_Red/docs-site/` now contains the source. Recommendation: deferred to a follow-on hygiene slice that decides regenerate-from-source vs. relocate-as-is. AUQ would be required to choose.
- **Root `docs-site/` directory** (untracked; ~build/`.vale`/`docs`/`scripts`/`src`/`static`). The 18.C verification confirmed `git ls-files docs-site/` returned no tracked files. This is stale-build residue. Recommendation: deferred to hygiene-sweep cleanup (separate work item, untracked-file decision).

## Specification-Derived Verification Plan (spec-to-test mapping)

| Spec / Clause | Verification Action | Expected Evidence |
|--------------|---------------------|-------------------|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 ("strict descendant of `<gt-kb-root>/applications/`") | Assert post-move: `test -f applications/Agent_Red/shopify.app.toml && test -f applications/Agent_Red/package.json && test -f applications/Agent_Red/package-lock.json` | All three exist at destination |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 (corollary: not at platform root) | Assert post-move: `test ! -f shopify.app.toml && test ! -f package.json && test ! -f package-lock.json` (at GT-KB root) | All three absent from root |
| `.claude/rules/project-root-boundary.md` ("Agent Red files MUST be within `E:\GT-KB\applications\Agent_Red\`") | `git ls-files shopify.app.toml package.json package-lock.json` returns empty (no tracked instances at root) | Empty output |
| Git history preservation | `git log --follow applications/Agent_Red/shopify.app.toml` walks through pre-move history | Shows commits from before the move |
| No-broken-reference invariant | Reference scan (`grep -rln` on root paths from non-Agent-Red GT-KB code paths) returns empty | No stale root-relative references |
| `applications/Agent_Red/.gtkb-app-isolation.json` registry | Optional: append `shopify.app.toml`, `package.json`, `package-lock.json` to `top_level_artifacts` list with `bucket: "A"` (TBD — registry editing may be deferred to a separate update slice if owner prefers) | Registry updated OR explicit deferral note |

Verification command (composite):

```bash
test -f applications/Agent_Red/shopify.app.toml && \
  test -f applications/Agent_Red/package.json && \
  test -f applications/Agent_Red/package-lock.json && \
  test ! -f shopify.app.toml && \
  test ! -f package.json && \
  test ! -f package-lock.json && \
  git log --follow --oneline applications/Agent_Red/shopify.app.toml | head -3
```

Doctor + regression check (post-impl, to be executed at report time):

```bash
python -m pytest groundtruth-kb/tests/ -k "isolation or registry or root_boundary" --tb=short -q --timeout=60
python -m groundtruth_kb project doctor
ruff check applications/Agent_Red/CLAUDE.md scripts/ groundtruth-kb/src/ 2>&1 | tail -5
```

These exercise the spec-to-test mapping concretely: the `_check_root_boundary` doctor check enforces ADR-ISOLATION-APPLICATION-PLACEMENT-001 at runtime, and the targeted pytest selector covers the application-isolation registry test surface (matching pattern `test_.+\.py`).

## Acceptance Criteria

1. Three `git mv` operations complete cleanly with history preserved.
2. The composite verification command above exits 0.
3. `applications/Agent_Red/CLAUDE.md` includes the operator-path note (single subsection or paragraph addition).
4. No code, test, CI workflow, or documentation reference at non-Agent-Red GT-KB paths now points at a moved file (deferred reference fixup if discovered → AUQ).
5. Doctor checks that currently pass continue to pass (no new failures introduced).
6. The `.gtkb-app-isolation.json` registry edit is either landed in this slice or explicitly noted as deferred (owner choice; default = deferred so this slice stays minimal).

## Risks / Rollback

### Risks

- **Shopify CLI workflow break (likely):** any operator habit of running `shopify app deploy` from GT-KB root will fail. Mitigated by CLAUDE.md operator-note update (IP-2) and the note in the post-implementation report.
- **External Agent Red CI/repo dependency:** the hosted Agent Red repository at `https://github.com/mike-remakerdigital/agent-red` is lifecycle-independent. The in-tree `shopify.app.toml`/`package.json` may have been historical-only. The move within GT-KB does not affect that external repo.
- **Working-tree hygiene:** at draft time, the working tree has 129 unpushed commits + many modified files. Implementation must wait for a clean working tree (or owner authorization to git mv against the dirty state). Stop condition per briefing — flagged.

### Rollback

Trivial: `git mv` is fully reversible. To roll back: `git mv applications/Agent_Red/shopify.app.toml shopify.app.toml` (and the two npm files). The `applications/Agent_Red/CLAUDE.md` documentation update is reverted by Edit/git revert.

## Files Expected To Change (Inventory)

Concrete inventory of file mutations for this slice:

- `shopify.app.toml` → moved to `applications/Agent_Red/shopify.app.toml`
- `package.json` → moved to `applications/Agent_Red/package.json`
- `package-lock.json` → moved to `applications/Agent_Red/package-lock.json`
- `applications/Agent_Red/CLAUDE.md` — added operator-path note (one short paragraph or subsection)
- `bridge/gtkb-isolation-018-agent-red-cutover-001.md` (this proposal)
- `bridge/INDEX.md` — INDEX entry inserted at top: `Document: gtkb-isolation-018-agent-red-cutover` + `NEW: bridge/gtkb-isolation-018-agent-red-cutover-001.md`

The bridge/INDEX.md update is the canonical workflow-state mutation per GOV-FILE-BRIDGE-AUTHORITY-001 CLAUSE-INDEX-IS-CANONICAL: append-only entry, no rewrite of prior versions. Subsequent versions (REVISED / GO / NO-GO / VERIFIED / Post-Impl Report) will be inserted at the top of this thread's version list per the file-bridge-protocol.md INDEX maintenance convention.

This inventory is small (3 file moves + 1 doc update); the slice is not a bulk operation requiring a separate inventory artifact or formal-artifact-approval packet. The DELIB-20260875 owner authorization is the equivalent visibility marker per GOV-STANDING-BACKLOG-001 CLAUSE-VISIBILITY-BULK-OPS for the work-item-level approval.

## Open Questions (Optional — surfaced for Codex review)

- **Q1 (assets/):** Should the 96 tracked `assets/css|js/*` Docusaurus build artifacts be migrated in a follow-on slice, or deleted-and-regenerated from `applications/Agent_Red/docs-site/`? Recommendation: defer to follow-on with explicit owner AUQ.
- **Q2 (.gtkb-app-isolation.json registry):** Update the application-isolation registry inline with this slice, or in a separate registry-hygiene slice? Recommendation: separate (smaller blast radius for this slice).
- **Q3 (waiver expiry):** Does this slice (combined with prior VERIFIED sub-slices) constitute sufficient evidence to retire `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` in full, or does waiver-retirement require its own bridge thread? Recommendation: separate retirement-decision thread; this slice contributes evidence but does not claim full waiver-expiry on its own.

## Recommended Commit Type

`refactor:` — file moves preserving behavior; no new capability surface, no fix of broken behavior. Per `.claude/rules/file-bridge-protocol.md` § "Conventional Commits Type Discipline (Implementation Reports)", `refactor:` is the correct tag for restructuring without behavior change.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
