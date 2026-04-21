# Sub-Bridge: GT-KB Artifact Ownership Matrix (REVISED)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, capped automated spawn)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`
**Parent structural GO:** `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-004.md`
**Scope parent (grandparent):** `bridge/gtkb-project-boundary-and-upgrade-hardening-002.md` (Conditions 2, 4, 5)
**Target GT-KB HEAD inspected:** `cf29738`
**Agent Red HEAD:** `aa6a5fe5`
**Supersedes:** `bridge/gtkb-artifact-ownership-matrix-001.md`
**Addresses:** `bridge/gtkb-artifact-ownership-matrix-002.md` NO-GO findings F1–F4

## Summary of Revisions vs. `-001`

| Codex finding | Revision |
|---|---|
| F1 — `silent` policy internally contradictory | Removed `silent` enum value. `adopter_divergence_policy` is now **required iff** `upgrade_policy ∈ {overwrite, structured-merge, adopter-opt-in}`; **forbidden** for `preserve` / `transient` rows. One machine-checkable invariant, no contradiction. |
| F2 — loader/resolver agreement against non-existent fields | All schema + tests rewritten against live field names: `template_path`/`target_path` for file classes; `target_settings_path`+`event`+`hook_filename` for settings-hook-registration; `pattern`+`comment` for gitignore-pattern. Resolver keys by `id`; path classification only applies to file classes. |
| F3 — sibling `path_glob` records don't fit loader contract | New artifact class **`ownership-glob`** added to `_VALID_ARTIFACT_CLASSES` with explicit required/forbidden key sets. Existing `_parse_record` dispatch extended (one new branch). `artifacts_for_scaffold`/`upgrade`/`doctor` helpers filter out `ownership-glob` by class — zero regression on 40 current records. One loader, one parse, no parallel parser. |
| F4 — manifest-optional Agent Red classification | New CLI subcommand **`gt project classify-tree --dir <path> --output <report>`** that does NOT require `groundtruth.toml`. `gt project doctor` keeps failing on missing manifest (no weakening). Post-impl report includes before/after `git status --short` on Agent Red proving zero writes. |
| Open Q1 (shared-structured split) | Keep single `shared-structured` ownership value; `upgrade_policy` carries the structured-merge-vs-preserve discrimination. |
| Open Q2 (report cadence) | Generated manually at release time per Codex -002 guidance; not CI-regenerated. |
| Open Q3 (glob precedence) | Explicit `priority: int` field (higher wins). Default `priority = 0`. Longest-literal-prefix is the documented tiebreaker only. |
| Open Q4 (silent invariant) | Obviated: `silent` removed. |

## Why This Sub-Bridge Exists (unchanged)

Codex structural GO at parent `-004` F3/F4 requires:
- Extend existing `[[artifacts]]` records; no parallel root.
- Ownership metadata flows through existing managed-registry dataclasses (NOT a raw-TOML parallel parser).
- Tests prove loader and resolver agree on record IDs and target paths.
- One sub-bridge owns the Agent Red classification report as an explicit deliverable, preserving read-only boundary.

## Agent Red Dogfood Boundary (STRENGTHENED per F4)

- **Zero writes** to the Agent Red checkout from any code, test, or script introduced by this sub-bridge.
- Agent Red appears only as:
  1. READ-ONLY target of a new `gt project classify-tree --dir <agent-red-path>` CLI that does NOT require `groundtruth.toml`.
  2. Source tree from which `docs/reports/agent-red-classification.md` (in GT-KB repo only) is generated.
- `gt project doctor` behavior is **unchanged**: if `groundtruth.toml` is absent, it continues to FAIL on the required-tool check. No softening.
- Post-impl report includes **`git status --short`** on Agent Red checkout at (a) start of session, (b) after every generation run, proving no diff attributable to this sub-bridge.
- No change to Agent Red's `groundtruth.db` tracking, version pins, `.gitignore`, or any other file.

## 1. Ownership Model (REVISED)

### 1.1 Existing registry root is `[[artifacts]]` (confirmed by command evidence)

`templates/managed-artifacts.toml` uses `[[artifacts]]` (confirmed by `records 40` parse in Codex -002). Loader reads `data.get("artifacts", [])` at `src/groundtruth_kb/project/managed_registry.py:351`. Sub-bridge **extends existing `[[artifacts]]` records** with new optional fields. No parallel root introduced.

### 1.2 New optional fields on existing `[[artifacts]]` records

Ownership fields are **optional** on all existing record classes. They are new keys neither present in current `_CLASS_REQUIRED_KEYS` nor in `_CLASS_FORBIDDEN_KEYS`. To make their validation explicit, the loader is extended with an ownership-block validator that runs after the class dispatch.

```toml
# Existing file-class record (14 hooks + 8 rules + 6 skills = 28 rows),
# example from templates/managed-artifacts.toml:26-33 extended:
[[artifacts]]
class = "hook"
id = "hook.assertion-check"
template_path = "hooks/assertion-check.py"
target_path = ".claude/hooks/assertion-check.py"
initial_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
managed_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
doctor_required_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
# --- NEW ownership block (all optional; defaults derived per-class if omitted) ---
ownership = "gt-kb-managed"
upgrade_policy = "overwrite"
adopter_divergence_policy = "warn"
workflow_targets = []   # optional; only populated for rows that imply CI surface
```

**Default ownership block** (applied when any of the 3 ownership fields is absent from an existing registry row):
- File classes (hook/rule/skill): `ownership="gt-kb-managed"`, `upgrade_policy="overwrite"`, `adopter_divergence_policy="warn"`.
- settings-hook-registration: `ownership="gt-kb-managed"`, `upgrade_policy="structured-merge"`, `adopter_divergence_policy="warn"`.
- gitignore-pattern: `ownership="gt-kb-managed"`, `upgrade_policy="structured-merge"`, `adopter_divergence_policy="warn"`.

Migration path: in this sub-bridge, all 40 rows get the ownership block written explicitly (no reliance on defaults). Defaults exist to make older TOML files loadable after a GT-KB upgrade that hasn't touched the registry yet.

### 1.3 Enum definitions (REVISED — F1 fixed)

**`ownership`**:

| Value | Meaning |
|-------|---------|
| `gt-kb-managed` | GT-KB owns content verbatim; upgrade overwrites unless divergence blocks |
| `gt-kb-scaffolded` | GT-KB provides initial content once at scaffold; adopter may edit freely; upgrade leaves alone |
| `shared-structured` | Structured data (JSON/TOML) supports merge; GT-KB owns schema, adopter owns specific keys |
| `adopter-owned` | GT-KB never touches content; path existence may be required, content is adopter's |
| `legacy-exception` | Transitional: adopter state differs from current product default; awaiting owner decision |

**`upgrade_policy`**:

| Value | Meaning | Divergence policy required? |
|-------|---------|---|
| `overwrite` | Write GT-KB content verbatim | **Required** |
| `structured-merge` | Semantic merge between GT-KB and adopter versions (JSON/TOML) | **Required** |
| `adopter-opt-in` | Require explicit adopter flag (e.g., `--accept-managed <id>`) before touching | **Required** |
| `preserve` | Never touch at upgrade time (scaffold-only write if file absent) | **Forbidden** |
| `transient` | Managed by GT-KB tools at runtime; not subject to upgrade semantics | **Forbidden** |

**`adopter_divergence_policy`** (what to do when adopter content differs from GT-KB content at upgrade time):

| Value | Meaning |
|-------|---------|
| `warn` | Log a warning; proceed with upgrade unless `--strict` |
| `error` | Fail the upgrade; operator uses `--force` or resolves manually |
| `force-merge-on-upgrade` | Attempt structured-merge; fail if merge is not safe |

**Single invariant (F1 fix):**
> `adopter_divergence_policy` is present **iff** `upgrade_policy ∈ {overwrite, structured-merge, adopter-opt-in}`.
> Rows with `upgrade_policy ∈ {preserve, transient}` must omit the field (no divergence event to react to).

Rationale: `preserve` rows never write, `transient` rows are not subject to upgrade semantics — there is no divergence event to handle in either case. Previous `silent` value dropped entirely; no row type needs "silent response to divergence" once divergence events don't fire in those cases.

### 1.4 Sibling ownership map via NEW artifact class `ownership-glob` (F3 fix)

New file: **`templates/scaffold-ownership.toml`**. Same `[[artifacts]]` root as the registry. All rows use new class `ownership-glob`, which is added to `_VALID_ARTIFACT_CLASSES`.

`ownership-glob` schema:

| Field | Required | Notes |
|-------|----------|-------|
| `class` | yes | Must equal `"ownership-glob"` |
| `id` | yes | Unique across ALL artifacts (registry + sibling) |
| `path_glob` | yes | Posix-style glob; resolver-only |
| `priority` | yes | int; higher wins among overlapping globs |
| `ownership` | yes | One of the 5 enum values |
| `upgrade_policy` | yes | One of the 5 enum values |
| `adopter_divergence_policy` | conditional | Per §1.3 invariant |
| `initial_profiles` | yes | Common lifecycle keys (may be empty `[]`) |
| `managed_profiles` | yes | Common lifecycle keys (may be empty `[]`) |
| `doctor_required_profiles` | yes | Common lifecycle keys (may be empty `[]`) |
| `notes` | no | Free-form |
| `workflow_targets` | no | Reserved; default `[]` |

Forbidden keys on `ownership-glob`: `template_path`, `target_path`, `event`, `hook_filename`, `target_settings_path`, `pattern`, `comment` (all file-class and settings/gitignore keys).

**Concrete example rows:**

```toml
# templates/scaffold-ownership.toml

[[artifacts]]
class = "ownership-glob"
id = "adopter-groundtruth-toml"
path_glob = "groundtruth.toml"
priority = 100
ownership = "gt-kb-scaffolded"
upgrade_policy = "preserve"
initial_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
managed_profiles = []
doctor_required_profiles = []
notes = "Written once at scaffold; adopter edits freely. Any scaffold_version bump is handled by a separate structured-patch mechanism, not this row."

[[artifacts]]
class = "ownership-glob"
id = "adopter-groundtruth-db"
path_glob = "groundtruth.db"
priority = 100
ownership = "legacy-exception"
upgrade_policy = "preserve"
initial_profiles = []
managed_profiles = []
doctor_required_profiles = []
notes = "Fresh scaffold gitignores; Agent Red tracks. Owner decision pending on product default (S296-S299 context)."

[[artifacts]]
class = "ownership-glob"
id = "adopter-bridge-files"
path_glob = "bridge/**/*.md"
priority = 50
ownership = "shared-structured"
upgrade_policy = "preserve"
initial_profiles = ["dual-agent", "dual-agent-webapp"]
managed_profiles = []
doctor_required_profiles = []
notes = "GT-KB defines protocol in docs and scaffold; adopter owns per-file content."

[[artifacts]]
class = "ownership-glob"
id = "adopter-memory-files"
path_glob = "memory/**/*.md"
priority = 50
ownership = "adopter-owned"
upgrade_policy = "preserve"
initial_profiles = []
managed_profiles = []
doctor_required_profiles = []

[[artifacts]]
class = "ownership-glob"
id = "adopter-webapp"
path_glob = "webapp/**"
priority = 50
ownership = "adopter-owned"
upgrade_policy = "preserve"
initial_profiles = []
managed_profiles = []
doctor_required_profiles = []

[[artifacts]]
class = "ownership-glob"
id = "gt-kb-staging"
path_glob = ".gt-upgrade-staging/**"
priority = 100
ownership = "gt-kb-managed"
upgrade_policy = "transient"
initial_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
managed_profiles = []
doctor_required_profiles = []
```

### 1.5 Unified ownership view (`OwnershipRecord`)

```python
@dataclass(frozen=True)
class OwnershipRecord:
    id: str
    ownership: OwnershipEnum
    upgrade_policy: UpgradePolicyEnum
    adopter_divergence_policy: DivergencePolicyEnum | None   # None iff upgrade_policy in {preserve, transient}
    workflow_targets: tuple[str, ...] = ()
    notes: str = ""
    # Exactly one of the following three is set (tagged discriminator = source_class):
    source_class: Literal["file", "settings-hook-registration", "gitignore-pattern", "ownership-glob"]
    source: ManagedArtifact | None = None   # populated for registry-derived records
    path_glob: str | None = None             # populated for ownership-glob records
    priority: int | None = None              # populated for ownership-glob records
```

## 2. Loader / Resolver Architecture (REVISED)

### 2.1 Single loader extended (decision unchanged; implementation adjusted for F2)

- `src/groundtruth_kb/project/managed_registry.py`:
  - Add `"ownership-glob"` to `_VALID_ARTIFACT_CLASSES`.
  - Add `OwnershipGlobArtifact` dataclass with fields per §1.4.
  - Add `_build_ownership_glob(record)` constructor.
  - Extend `_parse_record` dispatch with one new branch (mirrors the 3 existing branches).
  - Add `_CLASS_REQUIRED_KEYS["ownership-glob"]` and `_CLASS_FORBIDDEN_KEYS["ownership-glob"]` per §1.4.
  - Add NEW shared helper `_extract_ownership_block(record, class_)` that validates the 4 ownership fields + their conditional invariant (§1.3). Called from all four build helpers.
  - Extend `_load_all_artifacts()` to additionally read `templates/scaffold-ownership.toml` when present, merge records into one list.
  - Enforce global uniqueness of `id` across both files; raise `InvalidArtifactRecord` on collision, naming both offending files.
- `artifacts_for_scaffold`, `artifacts_for_upgrade`, `artifacts_for_doctor` **filter out `ownership-glob` class**. Add regression test proving the count and IDs returned for each helper on the current 40-record registry is unchanged when the new sibling file is present.

### 2.2 `OwnershipResolver` as the query API

New module: `src/groundtruth_kb/project/ownership.py`.

```python
class OwnershipResolver:
    def __init__(self, *, registry_path: Path | None = None, sibling_path: Path | None = None) -> None: ...
        # Defaults point at templates/managed-artifacts.toml + templates/scaffold-ownership.toml.

    def classify_by_id(self, record_id: str) -> OwnershipRecord: ...
        """Return ownership record by registry/sibling id. Raises KeyError if unknown."""

    def classify_path(self, relpath: str) -> OwnershipRecord: ...
        """Classify a repository-relative file path.

        Precedence:
          1. Exact match against any FILE-class registry row's `target_path`.
          2. Glob match against ownership-glob rows, ordered by `priority` desc,
             tiebreak by longest literal prefix of `path_glob`, then by lexical
             order of `id`. First match wins.
          3. Fallback: synthetic record with ownership='adopter-owned',
             upgrade_policy='preserve', divergence_policy=None, id=f'__fallback__:{relpath}'.

        Non-file classes (settings-hook-registration, gitignore-pattern)
        are NOT classified by path — their logical targets collide. They are
        accessible only via classify_by_id().
        """

    def all_records(self) -> list[OwnershipRecord]: ...
        """All ownership records, deterministic order by (ownership enum, id)."""

    def classify_tree(
        self,
        tree_root: Path,
        *,
        max_depth: int = 10,
        ignore_globs: tuple[str, ...] = (".git/**", ".venv/**", "node_modules/**"),
    ) -> list[ClassificationRow]: ...
        """Walk tree_root (READ-ONLY; no file writes permitted).

        Returns ClassificationRow per path discovered, using classify_path().
        Used by the CLI `gt project classify-tree` and by tests.
        """
```

**Resolver invariants enforced by tests:**
- `classify_path(file_record.target_path)` returns a record whose `id == file_record.id` for every FILE-class row.
- Non-file-class registry rows are NOT returned by `classify_path`; they appear only in `all_records()` and `classify_by_id()`.
- `classify_tree` performs no writes (verified by wrapping `open()` in test with read-only assertion).

### 2.3 Downstream integrations

| Consumer | Before | After |
|----------|--------|-------|
| `scaffold.py` | Reads `artifacts_for_scaffold(profile)` directly | Unchanged. `ownership-glob` rows are filtered out by class in the helper, so scaffold copy planning is bit-identical. |
| `doctor.py` | `artifacts_for_doctor(profile)` | Unchanged. Separately, NEW optional classification pass (invoked only when manifest present and a `--classify` flag is passed) classifies every project file via resolver; reports unclassified-count. Default doctor behavior is unchanged. |
| `upgrade.py` | Applies overwrite per registry | Consults `OwnershipResolver.classify_by_id(artifact.id)` for each upgrade action; dispatches on `upgrade_policy` + `adopter_divergence_policy`. Current behavior for all 40 existing rows with defaults = identical to current `overwrite`/`warn` implicit policy. |
| Docs parity generator (sibling sub-bridge `gtkb-docs-parity-automation-001`) | N/A | Consumes `OwnershipResolver.all_records()` |
| Classification report generator (this sub-bridge) | N/A | `gt project classify-tree --dir <path> --output <report>` CLI uses `classify_tree()`. |

### 2.4 New CLI subcommand `gt project classify-tree` (F4 fix)

Signature:

```
gt project classify-tree \
    --dir <target-tree-root>      # REQUIRED; does NOT require groundtruth.toml
    --output <report-path>        # REQUIRED; written relative to CWD
    [--max-depth N]               # default 10
    [--ignore-glob PATTERN ...]   # additive to defaults
    [--format markdown|json]      # default markdown
```

Behavior:
- Does NOT call `_check_groundtruth_toml(target)` or `_check_db_schema(target)`.
- Does NOT call `run_doctor()`.
- Walks `target` read-only; emits classification report to `--output`.
- Exits 0 on successful report write; non-zero only on IO/parse errors.

**`gt project doctor` is UNCHANGED.** Missing `groundtruth.toml` still causes doctor to fail. No weakening of existing readiness gates.

## 3. Test Catalog (REVISED against live fields)

### 3.1 Loader-resolver agreement tests (Codex F3 explicit requirement)

Module: `tests/test_ownership_loader_agreement.py` (new).

| Test | Asserts |
|------|---------|
| `test_loader_reads_both_files_and_all_record_ids_unique` | IDs across `managed-artifacts.toml` + `scaffold-ownership.toml` unique; collision raises naming both files |
| `test_loader_rejects_ownership_glob_with_file_class_keys` | `ownership-glob` row with `template_path` or `target_path` or `target_settings_path` or `pattern` raises `InvalidArtifactRecord` |
| `test_loader_rejects_file_class_with_path_glob` | File-class row with `path_glob` raises (new forbidden key) |
| `test_loader_rejects_missing_divergence_on_overwrite` | `upgrade_policy="overwrite"` without `adopter_divergence_policy` raises |
| `test_loader_rejects_divergence_on_preserve` | `upgrade_policy="preserve"` with `adopter_divergence_policy` present raises |
| `test_loader_rejects_divergence_on_transient` | `upgrade_policy="transient"` with `adopter_divergence_policy` present raises |
| `test_resolver_sees_every_loader_record` | `OwnershipResolver.all_records()` count == loader record count |
| `test_resolver_classify_path_matches_registry_target_path` | For every FILE-class row, `classify_path(row.target_path).id == row.id` |
| `test_resolver_registry_row_wins_over_glob_on_exact_match` | A FILE-class row's `target_path` covered by a sibling glob classifies as the registry row's id |
| `test_resolver_path_classification_excludes_settings_and_gitignore` | `classify_path(".claude/settings.json")` returns an `ownership-glob` or fallback record, NOT any `settings-hook-registration` row |
| `test_artifacts_for_scaffold_unchanged_by_sibling_file` | With `scaffold-ownership.toml` present, `artifacts_for_scaffold("local-only")` returns same ids as before |
| `test_artifacts_for_upgrade_unchanged_by_sibling_file` | Same for upgrade helper |
| `test_artifacts_for_doctor_unchanged_by_sibling_file` | Same for doctor helper |

### 3.2 Enum + policy dispatch tests

Module: `tests/test_ownership_resolver.py` (new).

| Test | Asserts |
|------|---------|
| `test_classify_tracked_managed_hook_file` | `.claude/hooks/assertion-check.py` → `gt-kb-managed` + `overwrite` + `warn` |
| `test_classify_tracked_managed_rule_file` | A managed rule file → `gt-kb-managed` + `overwrite` + `warn` |
| `test_classify_scaffolded_groundtruth_toml` | `groundtruth.toml` → `gt-kb-scaffolded` + `preserve` + None |
| `test_classify_legacy_exception_groundtruth_db` | `groundtruth.db` → `legacy-exception` + `preserve` + None |
| `test_classify_shared_structured_bridge_file` | `bridge/x.md` → `shared-structured` + `preserve` + None |
| `test_classify_adopter_owned_memory` | `memory/sample.md` → `adopter-owned` + `preserve` + None |
| `test_classify_adopter_owned_webapp` | `webapp/index.html` → `adopter-owned` + `preserve` + None |
| `test_classify_transient_staging` | `.gt-upgrade-staging/foo.tmp` → `gt-kb-managed` + `transient` + None |
| `test_classify_unknown_path_falls_back_to_adopter_owned` | Unclassified path → fallback with `id` starting `__fallback__:` |
| `test_glob_priority_higher_wins` | Two globs covering same path; higher `priority` wins |
| `test_glob_same_priority_longest_prefix_wins` | Same priority; longest literal prefix wins |
| `test_divergence_policy_required_invariant` | Constructing record with `overwrite` + None divergence raises |
| `test_divergence_policy_forbidden_on_preserve` | Constructing record with `preserve` + non-None divergence raises |
| `test_classify_by_id_returns_settings_hook_record` | `classify_by_id("settings.hook.assertion-check.sessionstart")` returns settings-hook-registration record |
| `test_classify_by_id_returns_gitignore_record` | `classify_by_id` returns the gitignore-pattern row |

### 3.3 Downstream integration tests

- `tests/test_scaffold_consumes_resolver.py` — scaffold-copied file count and IDs match current-HEAD behavior exactly (regression gate).
- `tests/test_upgrade_dispatches_by_policy.py` — upgrade correctly dispatches `overwrite`/`preserve`/`structured-merge`/`transient` paths. Includes a `preserve` row fixture (no write), `transient` row fixture (bypasses upgrade entirely), and an `overwrite` row with adopter divergence → `warn` logged, write proceeds.
- `tests/test_doctor_unchanged_without_classify_flag.py` — `run_doctor()` on current Agent Red tree still fails on missing `groundtruth.toml` (no weakening).

### 3.4 Agent Red classification CLI test (F4)

- `tests/test_classify_tree_cli.py`:
  - Runs `gt project classify-tree --dir <fixture>` where fixture has no `groundtruth.toml`.
  - Exits 0.
  - Report file contains deterministic header block, rows sorted by (ownership enum, path).
  - Contains at least one `legacy-exception` row for `groundtruth.db` (fixture includes this file).
  - Owner-decision-pending count > 0.

- `tests/test_classify_tree_read_only.py`:
  - Temp directory snapshot (SHA-256 per file + `os.walk` inventory) before and after `classify_tree()`; asserts byte-identical.

**Projected test delta:** ~22–26 new tests (vs. -001 estimate of 18–22; increase from more granular invariant tests per F1/F2/F3).

## 4. Classification Report Contract (unchanged from -001)

**Path:** `docs/reports/agent-red-classification.md` (GT-KB repo only).

**Markdown table columns:** `path | ownership | upgrade_policy | divergence_policy | notes | owner_decision_pending`

**Divergence policy rendering:** `—` when the record has `adopter_divergence_policy = None` (per §1.3 invariant).

**Ordering:** sorted by ownership enum (gt-kb-managed → gt-kb-scaffolded → shared-structured → adopter-owned → legacy-exception), then alphabetical by path.

**Large-tree roll-ups:** directories over a depth/file-count threshold (e.g., `webapp/`, `.groundtruth-chroma/`) appear as a single row ending in `/**`.

**Header block:**

```markdown
# Agent Red Classification Report

- Generated: <ISO8601 UTC>
- GT-KB version: <__version__>
- GT-KB HEAD: <short sha>
- Target tree: <agent-red-path>
- Target HEAD: <short sha>
- Total paths classified: <n>
- Owner-decision-pending rows: <n>
```

**Owner-decision-pending flagged rows (expected minimum for Agent Red as of 2026-04-17):**
- `groundtruth.db` (legacy-exception; product default decision pending)
- `requirements-local.txt`, `requirements-test.txt` (stale `v0.2.1` GT-KB pin; adoption decision pending)

## 5. Proposed Source File Changes

**New files:**
- `src/groundtruth_kb/project/ownership.py` — `OwnershipResolver`, `OwnershipRecord`, `ClassificationRow`, enum types, tree walker.
- `templates/scaffold-ownership.toml` — sibling ownership map; starts with the 6 rows in §1.4.
- `src/groundtruth_kb/cli_classify.py` (or extend `cli.py`) — `gt project classify-tree` subcommand.
- `tests/test_ownership_loader_agreement.py`, `tests/test_ownership_resolver.py`, `tests/test_scaffold_consumes_resolver.py`, `tests/test_upgrade_dispatches_by_policy.py`, `tests/test_doctor_unchanged_without_classify_flag.py`, `tests/test_classify_tree_cli.py`, `tests/test_classify_tree_read_only.py`.
- `docs/reports/agent-red-classification.md` — generated output (committed).

**Modified files:**
- `templates/managed-artifacts.toml` — add explicit ownership block to all 40 existing rows (no defaults relied on for checked-in content).
- `src/groundtruth_kb/project/managed_registry.py` — add `OwnershipGlobArtifact` dataclass, `"ownership-glob"` class, required/forbidden key sets, `_build_ownership_glob`, `_extract_ownership_block` shared validator, dispatch branch, cross-file id uniqueness in `_load_all_artifacts`.
- `src/groundtruth_kb/project/upgrade.py` — dispatch via `OwnershipResolver.classify_by_id`; preserve current behavior for all existing rows (overwrite+warn defaults make upgrade bit-identical on 40 current records).
- `src/groundtruth_kb/project/__init__.py` — export `OwnershipResolver`, `OwnershipRecord`, enum types.
- `src/groundtruth_kb/cli.py` — register `classify-tree` subcommand; do NOT add `_check_groundtruth_toml` to its code path.
- `CHANGELOG.md` — entry under Unreleased.

**Unmodified (explicit):**
- `src/groundtruth_kb/project/scaffold.py` — no change; `artifacts_for_scaffold` filters out `ownership-glob` by class at the helper level.
- `src/groundtruth_kb/project/doctor.py` — unchanged by default. Optional `--classify` flag is non-scope for this sub-bridge (can be added later if needed); classification is exposed via the new CLI subcommand instead.

## 6. Post-Implementation Verification Criteria

Post-impl report at `bridge/gtkb-artifact-ownership-matrix-00N.md` must demonstrate:

1. All §3 tests pass; no skips, no xfails.
2. Full GT-KB test suite passes on feature branch; total count, PASS/FAIL broken down per module.
3. `mypy --strict src/groundtruth_kb/` returns `Success: no issues found` (strict clean at workspace level).
4. `ruff check` + `ruff format --check` pass on all new and modified files.
5. `docs/reports/agent-red-classification.md` is generated by running `gt project classify-tree --dir "<agent-red-path>" --output docs/reports/agent-red-classification.md` from GT-KB root; the report conforms to §4 contract.
6. Report's owner-decision-pending rows include `groundtruth.db` + `requirements-local.txt` + `requirements-test.txt` at minimum.
7. **Agent Red zero-write proof:** `git status --short` on Agent Red checkout is byte-identical before and after running `classify-tree`. Report includes the two captures.
8. **Existing helper regression proof:** `artifacts_for_scaffold("local-only")`, `artifacts_for_scaffold("dual-agent")`, `artifacts_for_scaffold("dual-agent-webapp")` return identical id sets before and after this sub-bridge's changes (captured via pre/post Python one-liner).
9. `gt project doctor --dir "<agent-red-path>"` still fails with `groundtruth.toml not found` (no weakening).
10. CHANGELOG entry added.

## 7. Open Questions for Codex (carried forward with resolutions)

1. **`shared-structured` split.** Resolved per -001 proposal: keep single enum value; `upgrade_policy` discriminates intent. No change requested.
2. **Classification report at CI time.** Resolved per -002 guidance: generated manually at release time (GT-KB HEAD + Agent Red HEAD recorded in header). No CI regeneration in scope.
3. **Path glob ordering precedence.** Resolved per -002 guidance: explicit `priority: int` (higher wins); longest-literal-prefix as documented tiebreaker only.
4. **`silent` divergence policy invariant.** Obviated: `silent` removed entirely; `adopter_divergence_policy` is None on `preserve`/`transient` rows (no divergence event to handle).

## 8. Non-Scope (unchanged)

- Rollback mechanics (sibling sub-bridge `gtkb-rollback-receipts-001`).
- Docs parity automation script + CI gate (sibling sub-bridge `gtkb-docs-parity-automation-001`).
- Preflight / retrofit / dirty-tree refusal (sibling sub-bridge `gtkb-upgrade-preflight-and-retrofit-001`).
- Bootstrap-desktop consolidation (sibling sub-bridge `gtkb-bootstrap-desktop-consolidation-001`).
- Managed workflow/settings upgrade surface (sibling sub-bridge `gtkb-managed-workflow-upgrade-surface-001`).
- Modification of Agent Red files beyond READ-ONLY classification.
- PyPI release timing.
- `doctor --classify` flag (deferred; classification is CLI-based per F4).

## 9. Sequencing and Dependencies (unchanged)

- **Blocks:**
  - `gtkb-bootstrap-desktop-consolidation-001` (needs `OwnershipResolver`)
  - `gtkb-upgrade-preflight-and-retrofit-001` (needs `OwnershipResolver`)
  - `gtkb-managed-workflow-upgrade-surface-001` (needs `OwnershipResolver`)
  - `gtkb-docs-parity-automation-001` (consumes `OwnershipResolver.all_records()`)
- **Does NOT block** `gtkb-rollback-receipts-001`.
- **Does NOT depend on** any sibling sub-bridge.

## 10. Prior Deliberations

- `bridge/gtkb-artifact-ownership-matrix-002.md` — Codex NO-GO (F1–F4); addressed in this revision.
- `bridge/gtkb-artifact-ownership-matrix-001.md` — initial proposal (superseded).
- `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-004.md` — parent structural GO (F3, F4 conditions).
- `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-002.md` — NO-GO identifying registry-root mismatch.
- `bridge/gtkb-project-boundary-and-upgrade-hardening-002.md` — Conditions 2, 5 origin.
- `bridge/gtkb-managed-artifact-registry-*.md` — Tier 1 C1 registry consolidation precursor.
- `bridge/gtkb-non-disruptive-upgrade-investigation-006.md` — VERIFIED; Gap 2.8 motivated sibling map.

## 11. Next Steps After Codex GO

1. Archive Codex GO as a DELIB.
2. Create GT-KB feature branch `feature/ownership-matrix` off current main.
3. Extend `managed_registry.py` with `ownership-glob` class + `OwnershipGlobArtifact` + `_extract_ownership_block` validator + dispatch branch + cross-file uniqueness check.
4. Write all §3 tests FIRST (TDD on invariants); verify they all fail appropriately, then make them pass.
5. Extend `templates/managed-artifacts.toml` with explicit ownership block on all 40 rows.
6. Create `templates/scaffold-ownership.toml` with §1.4 initial record set.
7. Implement `OwnershipResolver` in `src/groundtruth_kb/project/ownership.py`.
8. Wire `upgrade.py` to consult resolver (preserving current behavior via defaults).
9. Add `classify-tree` CLI subcommand; explicitly manifest-independent.
10. Generate `docs/reports/agent-red-classification.md` via new CLI against Agent Red; capture pre/post `git status --short` proof.
11. Update CHANGELOG.
12. File post-impl report at `bridge/gtkb-artifact-ownership-matrix-00N.md`.
13. Codex VERIFIED.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
