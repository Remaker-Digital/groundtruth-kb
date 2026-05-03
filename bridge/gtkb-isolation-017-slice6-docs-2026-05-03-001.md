NEW

# Implementation Proposal — GTKB-ISOLATION-017 Slice 6

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-03 (S329)
Subject: Documentation chapter covering the isolation contract, `gt project init` / `gt project upgrade` / `gt project doctor` walkthroughs, application-vs-platform separation rationale, existing-adopter migration pointer, clean-adopter smoke contract, service-down behavior, and overlay fallback semantics. Adds one architecture-level chapter at `groundtruth-kb/docs/architecture/isolation.md` plus a cross-link from `docs/index.md`.

## Context

GTKB-ISOLATION-017 Slices 1-5 are VERIFIED. Per the scoping bridge `bridge/gtkb-isolation-017-scoping-003.md` lines 151-171 + GO at `-004`, Slice 6 is the documentation chapter. Per sequencing constraint at scoping `-003.md` line 208, Slice 6 unblocks after Slice 5 VERIFIED — which closed at `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-006.md` (commit `dc8e58f8` on develop).

Per work_list TOP release-path directive, Slice 6 advances the v0.7.0-rc1 release path. No owner decisions are needed at this slice's GO time per the Decision Map at scoping `-003` lines 39-55 (all 7 Phase 9 decisions cluster on Slices 4, 7, 8 — none on Slice 6).

## Specification Links

The implementation is constrained by, and shall not depart from, the following specifications, ADRs, DCLs, governance rules, and proposal carry-forwards:

1. **Phase 9 plan §6 — Documentation For Normal Users** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 259-282. This enumerates the 7 minimum sections + tone + accessibility + versioning constraints.
2. **Phase 9 plan §"Exit Criteria" §4** at the same plan lines 341-352, specifically lines 351 (service-down behavior) and 352 (overlay fallback semantics) — the two additional sections beyond Phase 9 §6's enumeration that the scoping bridge added per F2 to Slice 6.
3. **Phase 9 plan §"Required Coverage"** at the same plan lines 89-303 (background context for what the chapter must cover end-to-end).
4. **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — adopters live at `<gt-kb-root>/applications/<name>/`. The chapter explains this contract in plain language.
5. **`.claude/rules/project-root-boundary.md`** — root-boundary contract; cited in the "Application root vs GT-KB product root" section.
6. **`.claude/rules/file-bridge-protocol.md`** — bridge protocol; cited in the "What `gt project doctor` checks" section's remediation paths (when doctor surfaces a bridge state issue).
7. **`.claude/rules/codex-review-gate.md`** — codex review gate; relevant to the existing-adopter migration walkthrough's bridge expectations.
8. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 151-171 (Slice 6 acceptance criteria) + `-004` GO.
9. **GOV-09**, **GOV-19** (outside-in: docs cite the user-facing CLI surfaces, not internal helpers), **GOV-20** (IPR + CVR — drafts to be embedded in post-impl REPORT).
10. **Prior Slice GOs (carry-forward; the chapter must accurately describe the actual implemented surfaces):**
    - Slice 1 `-012` VERIFIED — 9 isolation doctor checks with severity model in `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py`.
    - Slice 2 `-008` VERIFIED — managed-artifact registry with `owner`/`upgrade_policy` fields + AST-coverage gate.
    - Slice 2.5 `-008` VERIFIED — `OwnershipMeta.notes` rationale field.
    - Slice 3 `-014` VERIFIED — `gt project init` adopter-subject defaults + scaffold deliverables.
    - Slice 4 `-012` VERIFIED — `gt project upgrade --accept-migration` flow + auto-fixers + receipts.
    - Slice 5 `-006` VERIFIED — clean-adopter test suite (this proposal's verification anchor).
11. **Existing reference docs cross-linked (NOT modified, only linked from the new chapter):**
    - `docs/reference/cli.md` — CLI surface reference.
    - `docs/reference/upgrade-receipts.md` — receipt schema + rollback flow.
    - `docs/reference/canonical-terminology.md` — terminology glossary.
    - `docs/architecture/product-split.md` — the existing architecture chapter (the new isolation chapter is a sibling).
    - `docs/index.md` — the doc landing page (one-line cross-link added).
12. **Prior Deliberations:**
    - `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` v1 — overlay refresh + disposability deferred to Slice 5.5; the docs chapter MUST reflect that Slice 6's overlay-fallback section describes only stale-detection (the retained Slice 5 surface) and explicitly notes that refresh + disposability ship in Slice 5.5.
    - `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` v1 — Slice 4 owner decisions; the upgrade-walkthrough section cites the chosen modes (`mandatory_at_upgrade` / `one_shot_migration_at_upgrade` / `out_of_band_recipe_only`).
    - Search command run at proposal-draft time: `python -m groundtruth_kb.cli deliberations search --query "isolation documentation chapter"` — to be re-run by Codex review per `.claude/rules/deliberation-protocol.md`.

## Scope

### In-scope

Files created (new):

- **`groundtruth-kb/docs/architecture/isolation.md`** — the core Slice 6 chapter. Single-file architecture-level chapter with the 9 sections enumerated below. Estimated ~600 LOC of markdown.

Files modified (additive cross-link only; no content rewrite):

- **`groundtruth-kb/docs/index.md`** — adds one cross-link line to the new isolation chapter under the existing "Architecture" section. ~2-3 LOC change.

Documents (per GOV-20 advisory pilot):

- `IPR-SLICE6-DOCS-001` — pre-implementation review citing this proposal, ADR-ISOLATION-APPLICATION-PLACEMENT-001, Phase 9 §6 obligations, and the existing reference-docs cross-linked. To be embedded in post-impl REPORT.
- `CVR-SLICE6-DOCS-001` — post-implementation proof (filed at post-impl + Codex VERIFIED time).

### Out-of-scope (explicitly deferred)

- Modifications to the **existing reference docs** (`cli.md`, `upgrade-receipts.md`, `canonical-terminology.md`, `product-split.md`). The new chapter cross-links them; it does not rewrite them. Any update to those docs is a separate work item.
- **Adopter-facing README quickstart block** (Phase 9 §6 line 261-262 mentions an adopter README block "scaffolded into the adopter root by `gt project init`"). Slice 3 already shipped this per scoping `-003` line 105 + Slice 3 VERIFIED output (the scaffolded `README.md` under each adopter). Slice 6 documents it from the docs side; it does not re-implement the scaffolded block.
- **Diagrams** beyond plain markdown / mermaid blocks in the chapter itself. The scoping bridge mentions "2-3 diagrams"; for tonal consistency with `product-split.md` (which uses prose + tables, no images), Slice 6 ships mermaid blocks where they aid comprehension and otherwise relies on prose. No external image assets.
- **Phase 9 §7 examples** (Slice 7 scope). The chapter mentions example projects exist but does not contain example walkthroughs themselves.
- **Phase 9 §8 release-ops + closeout** (Slice 8 scope). The chapter does not include release-version pinning, CHANGELOG entries, or release-readiness updates.
- **Service-endpoint configuration walkthroughs** beyond the placeholder service contract Slice 3 scaffolds. The "Service-down behavior" section describes the expected behavior of the contract but does not document operator-facing service installation (that belongs in deployment docs, out of scope for Slice 6).
- **Multi-version migration documentation**. The "Migrating an existing mixed-root project" section points to the Phase 8 rehearsal kit (`scripts/rehearse_isolation.py` + `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md`); it does not document migration from arbitrary historical versions.

## Implementation Plan

1. **Author `docs/architecture/isolation.md`** with the following 9 sections, in this order (~600 LOC):

    a. **What is an application subject?** — plain-language explanation of the Phase 7 work-subject contract. Cites canonical-terminology.md for "application", "platform", "hosted application", "project". Contrasts application-subject with platform-subject sessions.

    b. **Application root vs GT-KB product root** — the two-root model. Explains why they are separated (`<gt-kb-root>/applications/<name>/` placement contract per ADR-ISOLATION-APPLICATION-PLACEMENT-001). What writing into which means for upgrade behavior. Includes a small mermaid diagram showing product root → applications/ → individual adopter roots.

    c. **Starting a new project with `gt project init`** — walkthrough. Cites Slice 3 scaffold contract: command form, flags (`--profile`, `--owner`, `--init-git`), expected output tree, the scaffolded README quickstart block. Cites `docs/reference/cli.md` for full flag inventory.

    d. **What `gt project doctor` checks** — severity model + remediation paths. Lists the 9 isolation checks from Slice 1 (`isolation:adopter-root-placement`, `isolation:service-endpoint`, `isolation:work-subject`, `isolation:no-writable-product-paths`, `isolation:hooks-point-to-wrappers`, `isolation:workstream-focus-hook-absent`, `isolation:work-list-no-product-entries`, `isolation:release-readiness-app-subject-header`, `isolation:chroma-regeneratable`). For each: status semantics (pass/fail/warning/info), what triggers it, how to remediate.

    e. **Upgrading an existing project with `gt project upgrade`** — walkthrough with receipt explanation. Cites Slice 4: `--apply` flag, receipt path under `.claude/upgrade-receipts/active/`, rollback via `gt project rollback`. Cross-links `docs/reference/upgrade-receipts.md`. Documents the Slice 4 partition: 1 hard-refuse + 4 auto-fixable + 4 needs-adopter-input.

    f. **Migrating an existing mixed-root project** — pointer to the Phase 8 rehearsal kit. Names `scripts/rehearse_isolation.py` + `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md`. Documents the `--accept-migration` flag's contract per `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` (mandatory at upgrade; one-shot migration; out-of-band recipe only).

    g. **Clean-adopter smoke contract** — invariants. Cites Slice 5: the 13 named test files + 3 migration fixtures + golden-fixture diff + overlay stale-detection. Each invariant articulated as one-line natural-language predicate.

    h. **Service-down behavior** (per Phase 9 Exit Criterion 4 line 351). Documents what the adopter sees when the scoped service endpoint is unreachable: doctor surfaces `isolation:service-endpoint` warning; CLI commands degrade gracefully where possible; bridge protocol unaffected (file-based, not service-mediated).

    i. **Overlay fallback semantics** (per Phase 9 Exit Criterion 4 line 352). Documents the chroma overlay's role + the stale-detection contract (`isolation:chroma-regeneratable`). Explicitly notes that overlay refresh + disposability ship in Slice 5.5 per `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` v1.

2. **Add one cross-link to `docs/index.md`** under the "Architecture" section (currently mentions only `docs/architecture/product-split.md` implicitly via the mermaid diagram). Add a "Read more" line: `See also: [Application/Platform Isolation](architecture/isolation.md).`

3. **Author IPR + CVR documents** per GOV-20 Phase 1 advisory pilot. Embedded in the post-impl REPORT.

## Test Plan (spec-to-test mapping)

Slice 6 ships docs, not code. Verification is content-presence + cross-reference integrity + tone, not pytest. The spec-to-test mapping below maps Phase 9 §6 + Exit Criterion 4 sections to specific assertions.

| Spec source | Verification |
|---|---|
| Phase 9 §6 line 264 ("What is an application subject?") | grep `^## What is an application subject` returns 1 match in `isolation.md` |
| Phase 9 §6 line 265 ("Starting a new project with `gt project init`") | grep `^## Starting a new project` returns 1 match |
| Phase 9 §6 line 266-267 ("Upgrading an existing project with `gt project upgrade`") | grep `^## Upgrading an existing project` returns 1 match |
| Phase 9 §6 line 268-269 ("What `gt project doctor` checks") | grep `^## What .gt project doctor. checks` returns 1 match; section enumerates all 9 isolation check names |
| Phase 9 §6 line 270-271 ("Application root vs GT-KB product root") | grep `^## Application root vs GT-KB product root` returns 1 match |
| Phase 9 §6 line 272-273 ("Migrating an existing mixed-root project") | grep `^## Migrating an existing mixed-root project` returns 1 match; section mentions `scripts/rehearse_isolation.py` |
| Phase 9 §6 line 274-275 ("Clean-adopter smoke contract") | grep `^## Clean-adopter smoke contract` returns 1 match; section names Slice 5's test surfaces |
| Phase 9 Exit Criterion 4 line 351 (service-down behavior) | grep `^## Service-down behavior` returns 1 match |
| Phase 9 Exit Criterion 4 line 352 (overlay fallback semantics) | grep `^## Overlay fallback semantics` returns 1 match; section cites `DELIB-S328-...-OVERLAY-SCOPE-REVISION` for the Slice 5.5 deferral |
| Phase 9 §6 line 276-278 (tone: product documentation, not incident narrative) | manual review during Codex VERIFIED — no `incident`, `regression`, `defect`, `S\d{3}` (session-id) tokens in the chapter body |
| Phase 9 §6 line 279-280 (no Windows-specific paths where avoidable) | grep `[Cc]:\\\|E:\\` returns 0 matches; references like `~/projects/myapp/` are POSIX-style |
| Phase 9 §6 line 281-282 (versioned alongside GT-KB releases) | committed under `docs/architecture/` which is versioned with the package |
| Cross-link integrity | for each `[text](path)` in `isolation.md`, the target file exists relative to `docs/` root |

Verification commands:

```bash
# From E:\GT-KB
python -c "
import re, pathlib
p = pathlib.Path('groundtruth-kb/docs/architecture/isolation.md')
text = p.read_text(encoding='utf-8')
required = [
    '## What is an application subject',
    '## Application root vs GT-KB product root',
    '## Starting a new project',
    '## What .gt project doctor. checks',
    '## Upgrading an existing project',
    '## Migrating an existing mixed-root project',
    '## Clean-adopter smoke contract',
    '## Service-down behavior',
    '## Overlay fallback semantics',
]
missing = [s for s in required if not re.search(s, text)]
print('missing sections:', missing)
banned = [t for t in ['C:\\\\', 'E:\\\\', 'incident', 'regression'] if t in text]
print('banned tokens:', banned)
"

# Cross-link integrity (manual or via mkdocs build if configured)
```

## Acceptance Criteria

This NEW is GO-able when Codex confirms:

1. Specification Links cover all governing artifacts including the cited Phase 9 §6 + Exit Criterion 4 + the prior-slice DELIBs.
2. The 9 enumerated section headings appear in the proposed `isolation.md` table-of-contents.
3. Each section's content is bounded to its Phase 9 §6 / Exit Criterion 4 line; no scope creep into Slices 7 / 8.
4. Cross-links to existing reference docs are read-only (Slice 6 does not modify `cli.md`, `upgrade-receipts.md`, `canonical-terminology.md`, `product-split.md`).
5. Tone is product documentation, not incident narrative (no `incident` / `regression` / `defect` / session-id tokens in chapter body).
6. Accessibility: no `C:\` or `E:\` paths in chapter examples; POSIX-style path examples preferred.
7. The "Overlay fallback semantics" section cites `DELIB-S328-...-OVERLAY-SCOPE-REVISION` for the Slice 5.5 deferral (refresh + disposability).
8. The "Migrating an existing mixed-root project" section cites the Phase 8 rehearsal kit (`scripts/rehearse_isolation.py` + the rehearsal recipe under `groundtruth-kb/templates/project/`).
9. Estimated envelope ~600 LOC docs + ~3 LOC index.md cross-link.

## Risk / Rollback

**Risk 1 — Docs drift vs implementation (medium).** Slices 1-5 surfaces could change in future GT-KB versions; the chapter would need re-verification. Mitigation: every section cites concrete spec lines + commit/bridge IDs. Future drift surfaces as broken cross-references during Codex VERIFIED on subsequent slices that touch the same surfaces.

**Risk 2 — Tone slipping into incident narrative (low).** The Slice 5 implementation REPORT is heavily incident-narrative-shaped (NO-GO/REVISED cycles, scope adjustments). The chapter must abstract above session-level history. Mitigation: §"Test Plan" includes a banned-token grep for `incident`, `regression`, `S\d{3}` patterns.

**Risk 3 — Cross-link rot in `docs/index.md` (low).** Adding a cross-link to a non-existent file would break the docs site. Mitigation: file is created in the same commit; cross-link integrity check validates target exists.

**Risk 4 — Mermaid block rendering (low).** Section b's diagram uses mermaid syntax. If the docs renderer doesn't support mermaid (unlikely; the existing `index.md` uses it at line 22-34), the chapter falls back to a labeled tree-shape ASCII diagram. Mitigation: mermaid syntax matches `index.md`'s existing usage.

**Rollback path:** Slice 6 ships only doc files. No source code or test changes. Reversible via `git revert` of the implementation commit; no production impact possible.

## Decision Needed From Owner

**None at NEW time** per the Decision Map at scoping `-003` lines 39-55 — Slice 6 owns no Phase 9 owner decisions. If Codex review surfaces a tonal or structural decision that requires owner input, REVISED-1 surfaces it via AskUserQuestion at that time.

## Open Items

- The `python -m groundtruth_kb.cli deliberations search --query "isolation documentation chapter"` probe will run as part of Codex review's Prior Deliberations check; if it returns rows, this proposal will be revised to cite them.
- If Codex VERIFIED on Slice 6 surfaces gaps in the existing reference docs (`cli.md`, `upgrade-receipts.md`) discovered while reviewing the cross-links, those gaps file as separate work-list rows; Slice 6 itself does not modify those docs per §"Out-of-scope".

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
