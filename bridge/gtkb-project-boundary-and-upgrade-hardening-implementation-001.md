# Implementation Bridge: GT-KB Project Boundary and Upgrade Hardening

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, capped automated spawn S299-continuation)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb` (GT-KB product scope — no Agent Red writes; Agent Red is read-only dogfood target)
**Scope parent:** `bridge/gtkb-project-boundary-and-upgrade-hardening-002.md` (Codex GO, 5 conditions)
**Scope proposal:** `bridge/gtkb-project-boundary-and-upgrade-hardening-001.md`
**Target GT-KB HEAD observed:** `cf29738` (feat(reporting): DA harvest coverage helper + doctor check)
**Agent Red HEAD observed:** `aa6a5fe5`
**Precedent pattern:** follows `gtkb-da-harvest-coverage-implementation-*` and `gtkb-canonical-terminology-surface-implementation-*`
  (comprehensive implementation bridge that translates scope-GO + conditions into discrete, Codex-reviewable phases).

## Purpose of This Bridge

Translate the scope-level GO at `-002` into a concrete, Codex-reviewable implementation plan
that discharges all 5 GO conditions, sequences the 10 phases of the scope proposal with
explicit phase gates, and holds Agent Red as classification-only per Condition 4.

Per `.claude/rules/codex-review-gate.md`, no GT-KB source/doc/registry/script/CI/KB mutation
can begin until Codex GOs this implementation bridge.

## Tier Alignment

This bridge is scope-level-GO'd but is NOT in the Tier 1 forward-work ordering
(`bridge/post-phase-a-prioritization-003.md` + `-004.md`). It extends the C1 managed-artifact
registry surface (commit `e12aab3` on GT-KB main) with ownership, rollback, retrofit, and
parity machinery. Sequencing note:

- **Does NOT block** Tier 1 A1 (`bridge-spawn-revalidation`, GO'd at -006, headless in flight),
  Tier 1 B1 (`agent-red-cto-cleanup`, REVISED-1 at -003 Codex reviewing).
- **Consumes** Tier 1 C1 (registry consolidation, commit `e12aab3` landed on GT-KB main) — the
  ownership field extension and sibling map in this bridge extend the live registry.
- **Does NOT block and is not blocked by** Tier 2 C2 (`gtkb-upgrade-pre-flight-checks`),
  but this bridge MAY subsume C2's pre-flight concerns (dirty-tree refusal, preflight checks).
  Codex review will confirm whether to merge C2 scope into this bridge or keep separate.

## Discharge of GO Conditions

### Discharge of Condition 1 — Rollback receipts restore-capable

Receipt shape expands beyond `{file_path, pre_hash, post_hash, action}` to
carry restorable state per artifact class:

| Artifact class | Receipt payload | Restore semantics |
|----------------|-----------------|-------------------|
| Overwritten file | Full pre-change bytes (gzipped base64 in receipt JSON, path in `.gt-upgrade-staging/pre/<receipt_id>/<rel_path>.gz`, both recorded) | Copy back pre-change file verbatim |
| Deleted file (upgrade removes) | Full pre-delete bytes + deletion marker | Recreate file with stored bytes |
| New file (upgrade adds) | Addition marker + post-write path | Delete file on rollback |
| Settings.json merge (`.claude/settings.json`) | Full pre-merge JSON object + full post-merge JSON object + JSON Patch (RFC 6902) between them | Apply inverse JSON Patch, or (if merge drift detected) offer `--force-restore` to overwrite |
| gitignore append | Pre-file lines + appended lines + post-file lines | Remove exactly the appended lines; leave unrelated adopter edits alone |
| TOML config merge (`groundtruth.toml`, `pyproject-sections.toml`) | Pre-content + post-content + merge strategy label | Restore pre-content if no adopter edit detected since upgrade; else offer `--force-restore` |
| Workflow file update | Full pre-bytes + full post-bytes | Copy back pre-bytes |
| Manifest update | Scaffold_version before/after + touched-artifact list | Reset manifest to before state |

**Key decisions (open for Codex):**
1. **Receipt storage:** pre-change bytes stored both inline in receipt JSON (gzipped base64
   for files < 256 KiB) AND on disk under `.gt-upgrade-staging/pre/<receipt_id>/`. Inline
   copy is primary (survives staging cleanup); on-disk copy is backup/audit.
2. **Staging directory lifecycle:** `.gt-upgrade-staging/` created at upgrade start, promoted
   on success (the staged "post" tree becomes the live tree via atomic rename where possible),
   retained on failure, cleaned up after successful rollback OR after owner-opt-in `--prune-staging`.
   Default retention: staging kept 7 days, receipts kept indefinitely (append-only).
3. **Rollback API:** `gt project upgrade --rollback <receipt_path>` reverses a prior upgrade.
   Loud failure if any restore step fails; partial rollback records a new receipt noting
   which files restored vs which failed. No silent best-effort.
4. **Rollback tests:** 6 mandatory test cases (one per artifact class row above) + 1
   end-to-end "upgrade → modify unrelated adopter file → rollback → verify adopter file
   untouched" test.

**Phase gate:** Phase 3 (transactional upgrade + rollback) lands behind these tests.
CI blocks on any test regression.

### Discharge of Condition 2 — Ownership covers generated + non-registry artifacts

Two-source ownership model:

**Source 1 — `templates/managed-artifacts.toml`** (existing registry, 40 records observed
at `groundtruth-kb\templates/managed-artifacts.toml`). Extend every record with:

```toml
# Example extension
[[managed]]
# ... existing fields ...
ownership = "gt-kb-managed"        # enum: gt-kb-managed | gt-kb-scaffolded | shared-structured | adopter-owned | legacy-exception
upgrade_policy = "overwrite"       # enum: overwrite | preserve | structured-merge | adopter-opt-in
adopter_divergence_policy = "warn" # enum: warn | error | silent | force-merge-on-upgrade
workflow_targets = []              # list[str]: GitHub Actions workflow filenames if this record manages CI surface
```

**Source 2 — `templates/scaffold-ownership.toml`** (new sibling file, co-located). Covers
generated/scaffolded/adopter globs that don't live as registry rows:

```toml
# Sibling ownership map for artifacts not in managed-artifacts.toml
[[glob]]
path_glob = "groundtruth.toml"
ownership = "gt-kb-scaffolded"      # provided once at scaffold, adopter may edit freely
upgrade_policy = "preserve"         # never overwrite unless --force with adopter opt-in

[[glob]]
path_glob = "groundtruth.db"
ownership = "legacy-exception"      # NEW category for S299: adopter decision pending
upgrade_policy = "preserve"
notes = "Fresh scaffold gitignores; Agent Red tracks. Owner decision pending on product default."

[[glob]]
path_glob = ".github/workflows/*.yml"
ownership = "gt-kb-managed"
upgrade_policy = "overwrite"
adopter_divergence_policy = "warn"

[[glob]]
path_glob = ".github/dependabot.yml"
ownership = "gt-kb-managed"
upgrade_policy = "overwrite"

[[glob]]
path_glob = ".coderabbitai.yaml"
ownership = "gt-kb-managed"
upgrade_policy = "overwrite"

[[glob]]
path_glob = "src/tasks.py"
ownership = "gt-kb-scaffolded"
upgrade_policy = "preserve"

[[glob]]
path_glob = "pyproject-sections.toml"
ownership = "shared-structured"
upgrade_policy = "structured-merge"

[[glob]]
path_glob = "bridge/**/*.md"
ownership = "shared-structured"     # GT-KB provides protocol, adopter owns content
upgrade_policy = "preserve"         # never overwrite individual bridge files

[[glob]]
path_glob = ".claude/settings.json"
ownership = "shared-structured"
upgrade_policy = "structured-merge"

[[glob]]
path_glob = "memory/**/*.md"
ownership = "adopter-owned"
upgrade_policy = "preserve"          # never touch

[[glob]]
path_glob = "webapp/**"
ownership = "adopter-owned"
upgrade_policy = "preserve"

[[glob]]
path_glob = ".gt-upgrade-staging/**"
ownership = "gt-kb-managed"
upgrade_policy = "transient"         # generated/pruned by GT-KB
```

**Unified reader API:** new `src/groundtruth_kb/project/ownership.py` exposes a single
`OwnershipResolver` class that:

1. Loads both sources at startup
2. Resolves a given path to an ownership record (registry row wins over glob on exact match)
3. Exposes `classify_path(path) -> OwnershipRecord` used by `doctor`, `upgrade`, scaffold,
   preflight, and the `artifact-ownership-matrix.md` doc generator

**`docs/reference/artifact-ownership-matrix.md`** is GENERATED from the two sources at
release time (script `scripts/generate_ownership_matrix.py`). Never hand-edited. Parity
script (see Condition 5) asserts doc matches generator output.

**"Managed is not silent overwrite":** even for `ownership = "gt-kb-managed"`, the upgrade
flow must: (1) run preflight (scan for adopter divergence via content hash compare),
(2) record receipt, (3) offer rollback token, (4) honor `adopter_divergence_policy` to
warn/error/merge on divergence. Codex-mandated.

**Phase gate:** Phase 2 lands the ownership sources + `OwnershipResolver` + all downstream
integrations (doctor, upgrade, scaffold, preflight). Tests cover all 5 ownership enum values
and all 4 upgrade_policy enum values.

### Discharge of Condition 3 — `bootstrap-desktop` explicit decision

**Evidence:** `groundtruth-kb\src\groundtruth_kb\bootstrap.py:134-164`
(`bootstrap_desktop_project()`) glob-copies hooks/rules/root-CI templates, parallel to
`gt project init` but NOT using the managed-artifact registry.

**Decision (proposed; Codex to confirm/reject):** **Bring `bootstrap-desktop` under the
registry contract.** Rationale: deprecation+removal creates a migration burden for any
existing desktop-bootstrapped projects and is out of scope for this bridge; bringing it
under the contract is additive and aligns both entry points to the same ownership/receipt/
rollback semantics.

**Required implementation actions:**
1. Refactor `bootstrap_desktop_project()` to delegate to the same managed-artifact copy logic
   used by `gt project init` (the `_plan_managed_files` / `_plan_missing_managed_files`
   primitives established in Tier A #2 and #4).
2. Preserve current desktop-specific behavior (e.g., desktop hook subset) via an optional
   profile flag on the copy planner, not via a parallel code path.
3. Add tests: `tests/test_bootstrap_desktop.py` exercises the same registry/ownership
   semantics as `gt project init`, plus desktop-specific profile coverage.
4. Update `docs/reference/templates.md` to reflect that both entry points consume the same
   registry (previously claimed in docs but not true in code).

**Alternative for Codex consideration:** If Codex prefers deprecation, this bridge can
instead mark `bootstrap-desktop` as deprecated with a scheduled-removal tag in a future
minor, add an emit-warning at invocation, and document the replacement path (`gt project
init` with a new `--desktop` flag). This alternative is viable but adds migration work
that the consolidation option avoids.

**Phase gate:** Phase 4 (bootstrap-desktop unification) lands after Phase 2 (ownership)
so it can consume the new resolver.

### Discharge of Condition 4 — Agent Red dogfood is classification-only

**Absolute boundary:** this bridge makes **zero writes** to the Agent Red checkout.
Agent Red appears only as:
1. Read-only target of `gt project upgrade --dry-run --dir "<agent-red-path>"` in retrofit mode
2. Read-only target of `gt project doctor --dir "<agent-red-path>"` in retrofit mode
3. Source of a generated classification report: `docs/reports/agent-red-classification.md`
   (report lives in GT-KB repo, NOT in Agent Red repo)

**Prerequisite:** `gt project init --retrofit` (Phase 5) must be implemented first;
current `gt project init` rejects non-empty directories (`bootstrap.py:75-79` `_validate_target()`)
and current `gt project upgrade --dry-run --dir <agent-red>` returns only
`[SKIP] groundtruth.toml - No [project] manifest found - run 'gt project init' first`
(Codex-002 evidence).

**Classification report contract** (Condition 4's "generated classification report"):

- Format: Markdown table with columns
  `path | classification | upgrade_policy | notes | matches_current_state`
- Classifications: `gt-kb-managed`, `gt-kb-scaffolded`, `shared-structured`, `adopter-owned`, `legacy-exception`
- One row per file up to a depth cap; directory roll-ups for large trees (e.g., `webapp/` as one row)
- `legacy-exception` rows explicitly enumerate:
  - Tracked `groundtruth.db` (product-default decision pending)
  - Any divergence between Agent Red and fresh-scaffold gitignore defaults
  - Stale GT-KB version pin (`requirements-local.txt:17`, `requirements-test.txt:49` →
    pins `v0.2.1` while current GT-KB ships `v0.6.0`)
- `notes` column flags `owner-decision-pending` for `legacy-exception` rows
- Report header includes Agent Red HEAD, GT-KB HEAD used, timestamp, and owner-decision-pending
  summary count

**Out of scope (per Condition 4 ultimatum):**
- No change to `groundtruth.db` tracking in Agent Red
- No bump to `requirements-local.txt` / `requirements-test.txt`
- No modification of any `.gitignore`, `groundtruth.toml`, or other Agent Red file
- A follow-on Agent Red adoption bridge will handle those changes AFTER owner decides
  on the `groundtruth.db` tracking default

**Phase gate:** Phase 8 (dogfood classification report) runs after Phase 5 (retrofit) lands.
Report is reviewed in the post-impl report for this bridge.

### Discharge of Condition 5 — Docs parity from live registry truth

**Anti-pattern to avoid (Codex-flagged):** hard-coded counts in docs that drift from registry.
Current `docs/reference/templates.md:3` says 30 templates while live registry has 40 records.

**Implementation:**

1. `scripts/generate_ownership_matrix.py` — reads `managed-artifacts.toml` + `scaffold-ownership.toml`,
   emits `docs/reference/artifact-ownership-matrix.md`. Deterministic ordering (sorted by
   ownership, then by path). Header includes a fingerprint hash of both sources.
2. `scripts/regenerate_templates_doc.py` (or a `templates` section in the same script) —
   emits `docs/reference/templates.md` counts and lists directly from registry, not hard-coded.
3. `scripts/check_docs_vs_registry.py` — CI gate. Re-runs generators, diffs against committed
   docs, fails if drift. Replaces any hard-coded counts in docs.
4. New CI workflow step: `.github/workflows/docs.yml` (or existing `docs-check.yml`) adds
   the parity gate. Must fail PR merge on drift.
5. Tests: `tests/test_docs_parity.py` asserts (a) generator output matches committed doc,
   (b) hard-coded counts do not appear in docs (regex scan), (c) generator is deterministic
   across runs.

**Phase gate:** Phase 7 (docs parity) lands before Phase 8 (dogfood). Ensures the
classification report generator reuses the same doc generation infrastructure.

## Phase Plan (with explicit review gates)

Each phase is implemented as a single commit on a GT-KB feature branch. After each phase,
I post an intra-bridge status note under the bridge thread (not a version bump) and proceed
to the next phase. Codex may halt progress at any phase gate by posting NO-GO on the
overall bridge at that point.

| Phase | Target | Discharges | Depends on |
|-------|--------|------------|-----------|
| P1 | GT-KB spec recording (~8 specs: boundary, ownership, rollback, retrofit, dirty-tree, workflow-merge, docs-parity, bootstrap-unify) in KB with `type='governance'` or `type='architecture_decision'` as appropriate | Scope documentation | — |
| P2 | Ownership sources (`managed-artifacts.toml` extension + `scaffold-ownership.toml` new) + `OwnershipResolver` module + doctor/scaffold/upgrade integration + tests | Condition 2 | P1 |
| P3 | Transactional upgrade + rollback receipt + `gt project upgrade --rollback` + receipt format + 7 rollback tests | Condition 1 | P2 |
| P4 | `bootstrap-desktop` unification under registry, tests, docs update | Condition 3 | P2 |
| P5 | Dirty-tree upgrade refusal + preflight (per-artifact-class ownership check) + `--force` flag with adopter opt-in confirmation + retrofit path `gt project init --retrofit <existing-dir>` + tests | Scope §D (retrofit) + scope §C (dirty-tree) + subsumes Tier 2 C2 pre-flight scope | P2, P3 |
| P6 | Managed workflow/integration upgrade surface (`.github/workflows/*.yml`, `.github/dependabot.yml`, `.coderabbitai.yaml`, `.claude/settings.json`, `sonar-project.properties`, `pyproject-sections.toml`) via extended registry; settings.json uses structured-merge not overwrite | Scope §E | P2 |
| P7 | Docs parity automation (`generate_ownership_matrix.py`, `regenerate_templates_doc.py`, `check_docs_vs_registry.py`, CI gate, `test_docs_parity.py`) | Condition 5 | P2 |
| P8 | Agent Red dogfood classification report (read-only, written to GT-KB repo only) | Condition 4 | P5, P7 |
| P9 | Post-implementation report + Codex VERIFIED | — | P1-P8 |

**Phase size estimate:** P1 small, P2 medium-large, P3 medium-large, P4 small-medium,
P5 medium, P6 medium, P7 medium, P8 small (tooling-heavy but file-light), P9 small.

**Total estimated scope:** ~12-18 commits on GT-KB feature branch, ~80-120 new tests,
~15-25 new or modified source files.

## Test Plan

Per Codex direct answer #3 (extend existing + focused new modules):

- **Extend** `tests/test_upgrade.py` with rollback cases (one per artifact class) and
  settings-merge round-trip cases
- **Extend** `tests/test_managed_registry.py` with ownership-field roundtrip tests
- **Add** `tests/test_ownership_resolver.py` — classification correctness across all 5
  ownership enum values; registry-row-vs-glob precedence; adopter-divergence policy dispatch
- **Add** `tests/test_preflight.py` — dirty-tree refusal, adopter-divergence detection,
  `--force` confirmation semantics, legacy-exception handling
- **Add** `tests/test_retrofit.py` — `gt project init --retrofit <existing-dir>` on
  mock non-empty directory; classification report generation on mock adopter
- **Add** `tests/test_bootstrap_desktop.py` — desktop profile under registry contract
- **Add** `tests/test_docs_parity.py` — generator determinism + committed-doc parity +
  no-hard-coded-counts regex scan
- **Add** `tests/test_rollback_e2e.py` — full upgrade → modify adopter file → rollback
  → verify adopter file untouched

Projected test delta: ~80-120 new assertions across ~8 new/extended modules.

## Source Touchpoints

New files in GT-KB (`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`):
- `src/groundtruth_kb/project/ownership.py` — OwnershipResolver
- `src/groundtruth_kb/project/preflight.py` — dirty-tree refusal + divergence detection
- `src/groundtruth_kb/project/rollback.py` — rollback engine + receipt serde
- `src/groundtruth_kb/project/retrofit.py` — retrofit entry point (may subsume into `bootstrap.py`)
- `templates/scaffold-ownership.toml` — sibling ownership map
- `scripts/generate_ownership_matrix.py`
- `scripts/check_docs_vs_registry.py`
- `docs/reference/artifact-ownership-matrix.md` (GENERATED — never hand-edited)

Modified files:
- `src/groundtruth_kb/bootstrap.py` — consume `OwnershipResolver`, support `--retrofit`,
  unify `bootstrap_desktop_project()` under registry
- `src/groundtruth_kb/project/scaffold.py` — consume `OwnershipResolver`
- `src/groundtruth_kb/project/upgrade.py` — transactional + rollback + preflight integration
- `src/groundtruth_kb/cli.py` — `--rollback`, `--retrofit`, `--force-restore` flags
- `src/groundtruth_kb/project/doctor.py` (or equivalent) — consume `OwnershipResolver`
- `templates/managed-artifacts.toml` — extend every record with ownership/upgrade_policy/divergence_policy
- `docs/reference/templates.md` — replace hard-coded counts with generator output
- `.github/workflows/docs-check.yml` — add parity gate step
- `.gitignore` — add `.gt-upgrade-staging/` (generated, ignored)

## Risk + Blast Radius

- **HIGH.** Changes affect every GT-KB adopter's upgrade behavior and scaffold semantics.
- **Mitigation 1:** transactional upgrade + rollback is the primary safety net. No upgrade
  lands without a receipt; every receipt is restore-capable.
- **Mitigation 2:** ownership sources are authoritative; doctor+upgrade+scaffold all
  consume the same resolver. No more silent "managed means overwrite" semantics.
- **Mitigation 3:** phase gates let Codex halt progress on any phase without losing prior
  phase work (each phase is its own commit).
- **Mitigation 4:** Agent Red as read-only dogfood surfaces edge cases on a real adopter
  before anything ships to PyPI.
- **Rollout:** no PyPI release until all 9 phases VERIFIED. v0.6.1 or v0.7.0 carries this
  work. Release planning deferred to post-VERIFIED owner decision.

## Open Owner Decisions (deferred, not blocking implementation start)

1. **`groundtruth.db` product-default.** Fresh scaffold gitignores; Agent Red tracks.
   Three options (from scope proposal §Open Questions Q1): (a) adopters SHOULD track,
   (b) adopters SHOULD gitignore, (c) adopter opt-in per project. **Default during
   implementation:** preserve current scaffold default (gitignored); classify Agent
   Red's tracked DB as `legacy-exception`. Codex already affirmed this default in -002
   §"Decision Needed From Owner".
2. **Bootstrap-desktop policy:** proposed consolidation under registry (this bridge) vs
   deprecation-with-sunset (alternative). **Default during implementation:** consolidation.
   Owner may override at post-impl review.
3. **Rollback receipt retention:** append-only indefinitely (proposed). Owner may later
   opt into pruning via `gt project upgrade --prune-receipts --older-than <duration>`.
4. **Agent Red follow-on bridge.** After this bridge is VERIFIED, a separate bridge
   (`agent-red-adoption-post-boundary-hardening-001.md`) will land the Agent Red-side
   cleanup (db tracking decision application, version pin bump, retrofit if any).
   Not in scope here.

## Open Questions for Codex (review of this implementation bridge)

1. **Subsume Tier 2 C2 (`gtkb-upgrade-pre-flight-checks`)?** P5 of this bridge covers
   dirty-tree refusal + preflight. If Codex prefers keeping C2 separate, P5 narrows
   to retrofit-only and a separate C2 bridge handles preflight. Current proposal:
   consolidate for coherence.
2. **Bootstrap-desktop decision.** GO condition 3 allows either consolidation or
   deprecation. Proposal picks consolidation. Does Codex agree or prefer the
   deprecation path?
3. **Receipt inline-bytes cap at 256 KiB.** Files above that cap use on-disk-only
   staging under `.gt-upgrade-staging/pre/`. Does Codex want a different threshold,
   or always-on-disk regardless of size?
4. **Phase gates.** Bridge thread stays single (this -001) with intra-phase notes,
   or split each phase into its own `-implementation-pN-*.md` sub-bridge for independent
   Codex review? Precedent from `gtkb-da-harvest-coverage-implementation-011` is single
   bridge with intra-phase notes. Proposal follows that precedent.
5. **`shared-structured` ownership enum value.** Accepted shape is structured-merge for
   `.claude/settings.json`, preserve-only for `bridge/**/*.md`. Does Codex want the
   enum split into `structured-merge` and `cooperative-preserve` to make intent
   machine-readable?

## Prior Deliberations

- `bridge/gtkb-project-boundary-and-upgrade-hardening-001.md` (scope proposal)
- `bridge/gtkb-project-boundary-and-upgrade-hardening-002.md` (Codex scope GO, 5 conditions)
- `bridge/gtkb-managed-artifact-registry-*.md` (Tier 1 C1, registry consolidation at commit `e12aab3`)
- `bridge/gtkb-non-disruptive-upgrade-investigation-006.md` (VERIFIED — Gap 2.8 motivates this work)
- `bridge/gtkb-canonical-terminology-surface-implementation-*` (architectural precedent for
  ownership-registry-based scaffold/upgrade contract)
- `bridge/gtkb-da-harvest-coverage-implementation-*` (procedural precedent for phased
  implementation bridge with intra-phase review gates)
- `bridge/post-phase-a-prioritization-003.md` + `-004.md` (Tier 1/2 forward-work ordering)

## Non-scope (explicit)

- Agent Red file modifications (classification report ONLY, written to GT-KB repo)
- Agent Red `requirements-local.txt` / `requirements-test.txt` version bump
- Agent Red `groundtruth.db` tracking decision application
- PyPI release (release planning deferred to post-VERIFIED)
- GT-KB metrics/telemetry for upgrade success rates
- Tier 2 D1/D2 (Azure spec scaffold, ADR template activation)
- Tier 1 A1/B1 work (separate in-flight threads)

## Post-Implementation Report Contract

When all 9 phases land, I will post `-002.md` as the post-impl report containing:
- Commit SHA range
- Test delta (before/after counts, new tests per module)
- Phase completion checklist with evidence links
- Classification report artifact (P8 output path)
- Rollback round-trip test evidence
- CI status (all green)
- Doc parity verification output
- Owner decisions captured during implementation (if any)

## Next Steps After Codex GO

1. Archive Codex -002 GO as a DELIB.
2. File GT-KB feature branch `feature/project-boundary-hardening` off current `main`.
3. Execute Phase 1 (spec recording).
4. Post intra-phase status note, proceed to Phase 2.
5. Continue through Phase 8.
6. File post-impl report at `-002` of this implementation bridge.
7. Codex VERIFIED.
8. File Agent Red adoption follow-on bridge.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
