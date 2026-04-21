# Sub-Bridge: GT-KB Artifact Ownership Matrix (Design + Implementation Scope)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, capped automated spawn S299-continuation)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`
**Parent structural GO:** `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-004.md`
**Scope parent (grandparent):** `bridge/gtkb-project-boundary-and-upgrade-hardening-002.md` (Conditions 2, 4, 5)
**Target GT-KB HEAD:** `cf29738`
**Agent Red HEAD:** `aa6a5fe5`

## Why This Sub-Bridge Exists

Codex structural GO at parent `-004` F3 required:

> Extend the existing `[[artifacts]]` records; do not introduce a parallel root.
>
> State whether ownership metadata is loaded through the existing managed
> registry dataclasses or a raw-TOML ownership resolver.
>
> Add tests proving the registry loader and ownership resolver agree on record
> IDs and target paths.

And F4 assigned this sub-bridge (or the preflight/retrofit sub-bridge) the
specific deliverable:

> At least one sub-bridge, probably preflight/retrofit or docs parity, must own
> the generated Agent Red classification report as an explicit deliverable.

This sub-bridge accepts the classification-report deliverable (F4) because the
report is a direct product of the ownership resolver. Other sub-bridges may
still run their own read-only dogfood checks.

## Agent Red Dogfood Boundary (explicit)

Per parent structural GO F4 condition:

- **Zero writes** to the Agent Red checkout from any code, test, or script
  introduced by this sub-bridge.
- Agent Red appears only as:
  1. READ-ONLY target of `gt project doctor --dir <agent-red-path>` (via the
     new ownership resolver integration in doctor) — doctor may not pass
     today because Agent Red lacks `groundtruth.toml`; the resolver is
     expected to classify files WITHOUT requiring the manifest (this is the
     retrofit path's value).
  2. Source file tree from which the classification report is generated.
- **The generated Agent Red classification report is written to the GT-KB
  repo only**, at `docs/reports/agent-red-classification.md`. The report is
  an artifact of THIS sub-bridge, not of Agent Red.
- No change is made to Agent Red's `groundtruth.db` tracking, version pins,
  `.gitignore`, or any other file.

## 1. Ownership Model

### 1.1 Existing registry root is `[[artifacts]]` (confirmed)

`templates/managed-artifacts.toml` uses `[[artifacts]]` at line 26+. The
loader (`src/groundtruth_kb/project/managed_registry.py:339-358`) reads
`data.get("artifacts", [])`. This sub-bridge **extends existing
`[[artifacts]]` records** with new fields. No parallel root introduced.

### 1.2 New fields on every existing `[[artifacts]]` record

```toml
[[artifacts]]
# ... existing fields: id, type, src, dest, condition, etc. ...

# NEW — machine-checkable ownership metadata:
ownership = "gt-kb-managed"
upgrade_policy = "overwrite"
adopter_divergence_policy = "warn"
workflow_targets = []  # optional; list of related workflow filenames if this row manages CI surface
```

Enum value definitions:

**`ownership`** (who is authoritative for content):

| Value | Meaning |
|-------|---------|
| `gt-kb-managed` | GT-KB owns the content verbatim; upgrade overwrites unless divergence policy blocks |
| `gt-kb-scaffolded` | GT-KB provides the initial content once at scaffold time; adopter may edit freely; upgrade leaves alone |
| `shared-structured` | Content is structured data (JSON/TOML) that supports merge; GT-KB owns schema, adopter owns specific keys/sections |
| `adopter-owned` | GT-KB never touches content (even at scaffold); path existence may be required but content is adopter's |
| `legacy-exception` | Transitional category: adopter state differs from current product default and is awaiting owner decision |

**`upgrade_policy`** (what the upgrade flow does with this row):

| Value | Meaning |
|-------|---------|
| `overwrite` | Write GT-KB content verbatim; if adopter has diverged, apply `adopter_divergence_policy` |
| `preserve` | Never touch at upgrade time (only writes at initial scaffold if file absent) |
| `structured-merge` | Compute semantic merge between GT-KB and adopter versions (applies to JSON/TOML) |
| `adopter-opt-in` | Require explicit adopter flag (e.g., `--accept-managed <id>`) before touching |
| `transient` | Managed by GT-KB tools at runtime; not subject to upgrade semantics (e.g., `.gt-upgrade-staging/**`) |

**`adopter_divergence_policy`** (what to do when adopter content differs from
GT-KB content at upgrade time, for `overwrite` and `structured-merge` rows):

| Value | Meaning |
|-------|---------|
| `warn` | Log a warning; proceed with upgrade unless `--strict` |
| `error` | Fail the upgrade; operator must use `--force` or resolve manually |
| `silent` | Proceed silently (ONLY for `transient` upgrade_policy) |
| `force-merge-on-upgrade` | Attempt structured-merge; fail if merge is not safe |

**Invariant:** `upgrade_policy = "silent"` is only valid with `ownership =
"gt-kb-managed"` AND with a documented rationale. Tests enforce this.

### 1.3 Sibling ownership map for non-registry artifacts

New file: **`templates/scaffold-ownership.toml`**. This file uses the same
`[[artifacts]]` root as the registry, so one loader reads both and merges
results. Integration mechanics:

- `managed-artifacts.toml` is the **existing** registry; records refer to
  specific scaffolded files with known paths and templates.
- `scaffold-ownership.toml` is the **new sibling** file; records use
  `path_glob` instead of `src`/`dest`/`template`, matching generated,
  scaffolded-once, or adopter-owned paths that don't participate in the
  upgrade copy/merge mechanism but DO need an ownership classification.

Example records:

```toml
# templates/scaffold-ownership.toml (new)

[[artifacts]]
id = "adopter-groundtruth-toml"
path_glob = "groundtruth.toml"
ownership = "gt-kb-scaffolded"
upgrade_policy = "preserve"
adopter_divergence_policy = "warn"
notes = "Written once at scaffold; adopter edits freely; upgrade only updates scaffold_version via structured patch."

[[artifacts]]
id = "adopter-groundtruth-db"
path_glob = "groundtruth.db"
ownership = "legacy-exception"
upgrade_policy = "preserve"
adopter_divergence_policy = "warn"
notes = "Fresh scaffold gitignores; Agent Red tracks. Owner decision pending on product default."

[[artifacts]]
id = "adopter-bridge-files"
path_glob = "bridge/**/*.md"
ownership = "shared-structured"
upgrade_policy = "preserve"
adopter_divergence_policy = "silent"
notes = "GT-KB defines protocol (in docs + scaffold); adopter owns individual bridge file content."

[[artifacts]]
id = "adopter-memory-files"
path_glob = "memory/**/*.md"
ownership = "adopter-owned"
upgrade_policy = "preserve"
adopter_divergence_policy = "silent"

[[artifacts]]
id = "adopter-webapp"
path_glob = "webapp/**"
ownership = "adopter-owned"
upgrade_policy = "preserve"
adopter_divergence_policy = "silent"

[[artifacts]]
id = "gt-kb-staging"
path_glob = ".gt-upgrade-staging/**"
ownership = "gt-kb-managed"
upgrade_policy = "transient"
adopter_divergence_policy = "silent"
```

### 1.4 Records discriminate by presence of `src`/`template` vs `path_glob`

The unified dataclass is a tagged union:

```python
@dataclass(frozen=True)
class OwnershipRecord:
    id: str
    ownership: OwnershipEnum
    upgrade_policy: UpgradePolicyEnum
    adopter_divergence_policy: DivergencePolicyEnum
    workflow_targets: tuple[str, ...] = ()
    notes: str = ""
    # Exactly one of the following two must be set:
    source: ManagedArtifactRef | None = None   # existing registry row
    path_glob: str | None = None               # sibling map row
```

Validation at load time: records with both `source` and `path_glob`, or
neither, are rejected with a loud error naming the row ID.

## 2. Loader/Resolver Architecture

### 2.1 Single loader extended; no parallel parser

**Decision:** ownership metadata is loaded through the existing managed
registry dataclasses, NOT via a raw-TOML parallel parser.

Rationale:
- One reader, one TOML parse, one cached result.
- Loader already validates record IDs + target paths; extending it guarantees
  loader-resolver agreement (Codex F3 condition) by construction.
- Parallel parser would drift; the F3 test requirement is trivially satisfied
  because both consumers use the same parsed data.

### 2.2 `OwnershipResolver` as the query API

New module: `src/groundtruth_kb/project/ownership.py`.

```python
class OwnershipResolver:
    def __init__(self, registry_path: Path, sibling_path: Path) -> None: ...
    
    def classify_path(self, relpath: str) -> OwnershipRecord: ...
    """
    Resolution precedence:
    1. Exact-match `[[artifacts]]` row in managed-artifacts.toml (by dest path)
    2. Exact-match `path_glob` row in scaffold-ownership.toml
    3. Glob-match `path_glob` row in scaffold-ownership.toml (first match wins; ordering deterministic by glob specificity)
    4. Fallback: synthesized record with ownership='adopter-owned', upgrade_policy='preserve'
    """
    
    def all_records(self) -> list[OwnershipRecord]: ...
    
    def classify_tree(self, tree_root: Path, *, max_depth: int = 10) -> list[ClassificationRow]: ...
    """Walk tree_root (read-only), classify each file, return rows for report generation."""
```

### 2.3 Downstream integrations

| Consumer | Before | After |
|----------|--------|-------|
| `scaffold.py` | Reads `managed-artifacts.toml` directly for copy planning | Consumes `OwnershipResolver.all_records()`; filters to `has(source)` rows for copy planning |
| `doctor.py` | Queries registry for coverage check | Uses `OwnershipResolver` to classify every file under project root; flags unclassified paths when they should be classified |
| `upgrade.py` | Applies overwrite per registry | Consults `OwnershipResolver.classify_path()` for each upgrade action; dispatches on `upgrade_policy` + `adopter_divergence_policy` |
| Docs parity generator (sibling sub-bridge `gtkb-docs-parity-automation-001`) | N/A | Consumes `OwnershipResolver.all_records()` to emit `docs/reference/artifact-ownership-matrix.md` |
| Classification report generator (this sub-bridge) | N/A | Uses `OwnershipResolver.classify_tree(agent_red_path)` to produce `docs/reports/agent-red-classification.md` |

## 3. Test Catalog

### 3.1 Loader-resolver agreement tests (Codex F3 explicit requirement)

Module: `tests/test_ownership_loader_agreement.py` (new).

| Test | Asserts |
|------|---------|
| `test_loader_reads_both_files_and_all_record_ids_unique` | All record IDs across `managed-artifacts.toml` + `scaffold-ownership.toml` are unique |
| `test_loader_rejects_records_with_both_source_and_path_glob` | Malformed record raises at load time |
| `test_loader_rejects_records_with_neither_source_nor_path_glob` | Malformed record raises at load time |
| `test_resolver_sees_every_loader_record` | `OwnershipResolver.all_records()` count == number of rows parsed by loader |
| `test_resolver_and_registry_agree_on_target_paths` | For every `[[artifacts]]` row with `src`/`dest`, resolver's `classify_path(dest)` returns a record with matching `id` |
| `test_resolver_registry_row_wins_over_glob_on_exact_match` | When a registry row's dest path is also covered by a sibling glob, the registry row's classification wins |

### 3.2 Enum + policy dispatch tests

Module: `tests/test_ownership_resolver.py` (new).

| Test | Asserts |
|------|---------|
| `test_classify_tracked_managed_file` | Returns `gt-kb-managed` + `overwrite` |
| `test_classify_scaffolded_file` | Returns `gt-kb-scaffolded` + `preserve` |
| `test_classify_shared_structured_settings` | `.claude/settings.json` returns `shared-structured` + `structured-merge` |
| `test_classify_adopter_owned_memory` | `memory/sample.md` returns `adopter-owned` + `preserve` |
| `test_classify_legacy_exception_groundtruth_db` | `groundtruth.db` returns `legacy-exception` + `preserve` |
| `test_classify_transient_staging` | `.gt-upgrade-staging/foo.tmp` returns `gt-kb-managed` + `transient` |
| `test_classify_unknown_path_falls_back_to_adopter_owned` | Unclassified path gets fallback record |
| `test_silent_divergence_invariant` | Any row with `upgrade_policy='silent'` must have `ownership='gt-kb-managed'` (invariant enforced at load) |

### 3.3 Downstream integration tests

- `tests/test_scaffold_consumes_resolver.py` — scaffold copy planning reads from `OwnershipResolver`, not raw registry loader.
- `tests/test_doctor_classifies_project_tree.py` — doctor run in a scaffolded project classifies every file; unclassified count is 0.
- `tests/test_upgrade_dispatches_by_policy.py` — upgrade correctly dispatches per row's `upgrade_policy` and `adopter_divergence_policy`; covers `overwrite` + `preserve` + `structured-merge` + `transient` paths.

### 3.4 Agent Red classification report test

- `tests/test_agent_red_classification_report.py` — runs `classify_tree(<fixture copy of simplified Agent Red tree>)`; asserts the report contains:
  - At least one `legacy-exception` row for `groundtruth.db`
  - At least one `adopter-owned` row
  - Deterministic ordering (sorted by ownership, then path)
  - Header with GT-KB version + timestamp + tree root path + `owner-decision-pending` count
  - No row with empty ownership field

Total projected test delta: ~18-22 new tests.

## 4. Classification Report Contract

**Path:** `docs/reports/agent-red-classification.md` (in GT-KB repo).

**Columns (Markdown table):**

| path | ownership | upgrade_policy | divergence_policy | notes | owner_decision_pending |

**Ordering:** sorted by ownership enum (gt-kb-managed → gt-kb-scaffolded →
shared-structured → adopter-owned → legacy-exception), then alphabetical by path.

**Large-tree roll-ups:** directories over a depth/file-count threshold (e.g.,
`webapp/`, `.groundtruth-chroma/`) appear as a single row with path ending in
`/**`.

**Header block:**

```markdown
# Agent Red Classification Report

- Generated: <ISO8601 timestamp>
- GT-KB version: <__version__>
- GT-KB HEAD: <short sha>
- Target tree: <agent-red-path>
- Target HEAD: <short sha>
- Total paths classified: <n>
- Owner-decision-pending rows: <n> (search for `YES` in owner_decision_pending column)
```

**Owner-decision-pending flagged rows (expected at minimum for Agent Red as
of 2026-04-17):**
- `groundtruth.db` (legacy-exception; product default decision pending)
- `requirements-local.txt` / `requirements-test.txt` (stale v0.2.1 pin; adoption decision pending)

## 5. Proposed Source Files

New:
- `src/groundtruth_kb/project/ownership.py` — `OwnershipResolver`,
  `OwnershipRecord`, enum types, tree walker.
- `templates/scaffold-ownership.toml` — sibling ownership map (~10-15 records
  to start).
- `scripts/generate_agent_red_classification.py` — one-shot script that runs
  `classify_tree(<agent-red-path>)` and writes the report; may also be
  wrapped in a CLI subcommand.
- `tests/test_ownership_loader_agreement.py`, `tests/test_ownership_resolver.py`,
  `tests/test_scaffold_consumes_resolver.py`, `tests/test_doctor_classifies_project_tree.py`,
  `tests/test_upgrade_dispatches_by_policy.py`, `tests/test_agent_red_classification_report.py`.

Modified:
- `templates/managed-artifacts.toml` — add `ownership`, `upgrade_policy`,
  `adopter_divergence_policy`, `workflow_targets` fields to every existing
  `[[artifacts]]` record (40 rows).
- `src/groundtruth_kb/project/managed_registry.py` — extend dataclass to carry
  new fields; validate invariants at load time.
- `src/groundtruth_kb/project/scaffold.py` — consume `OwnershipResolver`
  instead of reading registry directly for copy planning.
- `src/groundtruth_kb/project/upgrade.py` — dispatch per `upgrade_policy` +
  `adopter_divergence_policy`; replace implicit "managed = silent overwrite"
  behavior.
- `src/groundtruth_kb/project/doctor.py` (or equivalent) — classify every
  project-tree file via resolver; report unclassified-paths count.
- `src/groundtruth_kb/project/__init__.py` — export `OwnershipResolver` +
  types.

## 6. Post-Implementation Verification Criteria

Post-impl report at `gtkb-artifact-ownership-matrix-00N.md` must demonstrate:

1. All tests from §3 pass; no skips, no xfails.
2. Full test suite passes on GT-KB main.
3. `mypy --strict` clean on `src/groundtruth_kb/project/ownership.py` and
   every modified file.
4. `ruff check` + `ruff format --check` pass on new files.
5. `docs/reports/agent-red-classification.md` is generated and committed; the
   report conforms to the contract in §4.
6. The classification report's owner-decision-pending rows include
   `groundtruth.db` at minimum.
7. No Agent Red file modified (git diff on Agent Red repo post-generation
   shows 0 changes attributable to this sub-bridge's code).
8. CHANGELOG entry added to GT-KB `CHANGELOG.md`.

## 7. Open Questions for Codex

1. **`shared-structured` split.** Codex `-002` F5 suggested splitting into
   `structured-merge` and `cooperative-preserve` to make intent
   machine-readable. This sub-bridge argues `upgrade_policy` already carries
   that discrimination (structured-merge vs preserve), so `ownership` can
   remain single-valued. Does Codex concur, or is the enum split still
   desired?
2. **Classification report at CI time.** Should the report be regenerated as
   part of GT-KB CI (ensuring it's never stale vs. Agent Red HEAD), or
   generated manually at release time? Proposal: CI-regenerated weekly, diff
   reviewed manually. Owner decision.
3. **Path glob ordering precedence.** Proposal says first glob match wins,
   ordered by glob specificity. Should specificity be lexical (longer pattern
   first) or by explicit priority field? Proposal: longest-literal-prefix
   first, fallback to order-in-file.
4. **Invariant for `silent` divergence policy.** Proposal enforces at load
   time that `adopter_divergence_policy='silent'` requires
   `ownership='gt-kb-managed'` + explicit `notes` rationale. Is that the
   right invariant scope, or should it be broader (e.g., also require
   `upgrade_policy in {overwrite, transient}`)?

## 8. Non-Scope

- Rollback mechanics (sibling sub-bridge `gtkb-rollback-receipts-001`).
- Docs parity automation script + CI gate — those live in sibling sub-bridge
  `gtkb-docs-parity-automation-001`. This sub-bridge provides the
  `all_records()` API the parity script consumes, nothing more.
- Preflight / retrofit / dirty-tree refusal — sibling sub-bridge
  `gtkb-upgrade-preflight-and-retrofit-001`.
- Bootstrap-desktop consolidation — sibling sub-bridge
  `gtkb-bootstrap-desktop-consolidation-001`.
- Managed workflow/settings upgrade surface — sibling sub-bridge
  `gtkb-managed-workflow-upgrade-surface-001`.
- Modification of Agent Red files beyond READ-ONLY classification.
- PyPI release timing.

## 9. Sequencing and Dependencies

- **Blocks** sibling sub-bridges:
  - `gtkb-bootstrap-desktop-consolidation-001` (needs `OwnershipResolver`)
  - `gtkb-upgrade-preflight-and-retrofit-001` (needs `OwnershipResolver`)
  - `gtkb-managed-workflow-upgrade-surface-001` (needs `OwnershipResolver`)
  - `gtkb-docs-parity-automation-001` (consumes `OwnershipResolver.all_records()`)
- **Does NOT block** `gtkb-rollback-receipts-001` (rollback works on git
  commits + receipts; ownership metadata is advisory for conflict resolution
  only in v1).
- **Does NOT depend on** any sibling sub-bridge. Can proceed first.

## 10. Prior Deliberations

- `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-004.md`
  (parent structural GO, F3 + F4 conditions sourced here)
- `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-002.md`
  (NO-GO identifying `[[managed]]` vs `[[artifacts]]` registry-root mismatch)
- `bridge/gtkb-project-boundary-and-upgrade-hardening-002.md`
  (Conditions 2 and 5 originated here)
- `bridge/gtkb-managed-artifact-registry-*.md` (Tier 1 C1 precursor; registry
  consolidation)
- `bridge/gtkb-non-disruptive-upgrade-investigation-006.md` (VERIFIED;
  Gap 2.8 enumeration motivates the sibling ownership map)

## 11. Next Steps After Codex GO

1. Archive Codex GO as a DELIB.
2. Create GT-KB feature branch `feature/ownership-matrix` off current main.
3. Implement `OwnershipResolver` in `src/groundtruth_kb/project/ownership.py`.
4. Create `templates/scaffold-ownership.toml` with initial record set per §1.3.
5. Extend `templates/managed-artifacts.toml` with new fields on all 40 rows.
6. Wire scaffold + upgrade + doctor to the resolver.
7. Add tests from §3.
8. Generate `docs/reports/agent-red-classification.md` (READ-ONLY dogfood).
9. File post-impl report at `gtkb-artifact-ownership-matrix-00N.md`.
10. Codex VERIFIED.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
