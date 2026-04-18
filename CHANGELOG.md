# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.1] - 2026-04-17

### Added — Canonical terminology surface

- **Scaffolded canonical terminology glossary** — New
  `templates/rules/canonical-terminology.md` (full ADR-0001 glossary:
  MemBase, Deliberation Archive, MEMORY.md, Knowledge Database,
  GroundTruth KB, GT-KB, Prime Builder, Loyal Opposition + full
  `MEMBASE-4-CLAUDE.md` term set + alias disposition table) and
  `templates/rules/canonical-terminology.toml` (profile-aware doctor
  config for `local-only`, `dual-agent`, `dual-agent-webapp`,
  `harness-memory`). Both delivered as managed `rule` artifacts in
  `templates/managed-artifacts.toml` (ids
  `rule.canonical-terminology` and `rule.canonical-terminology-config`),
  copied to `.claude/rules/canonical-terminology.{md,toml}` in every
  new scaffold.
- **Startup-visible glossary blocks** — Concise glossary block added to
  `templates/CLAUDE.md` (all profiles) and `templates/project/AGENTS.md`
  (dual-agent profiles). One-line glossary pointer added to
  `templates/MEMORY.md` and
  `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md`.
- **Canonical Term Propagation Gate** — New section in
  `templates/rules/deliberation-protocol.md` requires bridge proposals
  that introduce NEW canonical terms to list propagation targets
  (MemBase record, CLAUDE.md glossary, AGENTS.md glossary,
  `.claude/rules/canonical-terminology.md`, doctor config) before Loyal
  Opposition issues GO.
- **Doctor canonical-terminology check** — New `gt project doctor`
  check reads the profile-aware matrix from
  `.claude/rules/canonical-terminology.toml` and verifies every
  required file contains every required term. ERROR on missing
  canonical terms (per owner decision `DELIB-0719`); WARN on minor
  drift. Profile inheritance supported via `extends` (e.g.,
  `dual-agent-webapp` extends `dual-agent`). `harness-memory` opt-in
  profile skips MEMORY.md content check for projects whose MEMORY.md
  lives outside the repo.
- **Registry-driven upgrade** — `gt project upgrade --apply` idempotently
  repairs missing canonical-terminology files via the existing
  registry-driven `_plan_missing_managed_files` path (no `_MANAGED_*`
  list re-introduction; AST gate `tests/test_no_parallel_manifests.py`
  remains green).

### Added — Artifact Ownership Matrix (sub-bridge `gtkb-artifact-ownership-matrix`)

- **OwnershipResolver query API** (`src/groundtruth_kb/project/ownership.py`)
  — new public module exposing `OwnershipResolver`, `OwnershipRecord`,
  `ClassificationRow`, and report renderers. Resolver joins
  registry-class rows (keyed by `target_path`) with sibling
  `ownership-glob` rows (keyed by `path_glob`) into a single query
  surface. Precedence: exact FILE-class match → glob match (priority
  desc, then longest-literal-prefix tiebreak) → synthetic `adopter-owned
  + preserve` fallback. Loads typed output from `managed_registry`
  (never re-parses TOML — GO Condition C2).

- **Ownership metadata on every managed artifact** — `FileArtifact`,
  `SettingsHookRegistration`, `GitignorePattern`, and the new
  `OwnershipGlobArtifact` dataclasses each carry an `OwnershipMeta`
  block with `ownership` / `upgrade_policy` / `adopter_divergence_policy`
  / `workflow_targets`. Extracted by shared `_extract_ownership_block`
  validator called from all four build helpers (GO C2).

- **Sibling ownership map** (`templates/scaffold-ownership.toml`) — new
  TOML file carrying 8 `ownership-glob` rows for adopter-tree paths
  outside the registry (`groundtruth.toml`, `groundtruth.db`,
  `bridge/**/*.md`, `memory/**/*.md`, `webapp/**`,
  `.gt-upgrade-staging/**`, plus the two requirement files mandated by
  GO Condition C3).

- **`gt project classify-tree` CLI subcommand** — manifest-independent
  classifier (`gt project classify-tree --dir <path> --output <report>`).
  Does NOT require `groundtruth.toml` in the target tree and does NOT
  call `gt project doctor`. Read-only tree walker writes a Markdown or
  JSON report with a deterministic header block and ordering (ownership
  enum, then alphabetical by path). Flags rows whose ownership equals
  `legacy-exception` as `owner_decision_pending = "YES"`.

### Added — DA harvest coverage

- **Thread-level DA harvest coverage helper + doctor check** — New
  `src/groundtruth_kb/reporting/harvest_coverage.py` computes DA
  coverage against the bridge INDEX + `bridge/*.md` thread roll-up.
  New doctor check reports uncovered bridge threads so the harvest gap
  surfaces in routine `gt project doctor` runs, not only on a wrap.
  See `gtkb-da-harvest-coverage-implementation-011` VERIFIED.

### Changed

- **Managed registry loader** (`managed_registry.py`) — now merges
  records from `templates/managed-artifacts.toml` and
  `templates/scaffold-ownership.toml` into a single list with enforced
  cross-file `id` uniqueness. New `ownership-glob` class; new enum
  literals `OwnershipEnum` / `UpgradePolicyEnum` / `DivergencePolicyEnum`.
  `artifacts_for_scaffold` / `artifacts_for_upgrade` /
  `artifacts_for_doctor` filter out `ownership-glob` rows so current
  scaffold/upgrade/doctor behavior is bit-identical (zero regression on
  40 existing rows; verified by per-profile id-set delta).

- **`templates/managed-artifacts.toml`** — all 42 rows (40 pre-existing
  + 2 new canonical-terminology) carry an explicit ownership block
  (`ownership` / `upgrade_policy` / `adopter_divergence_policy`).
  File-class rows default to `gt-kb-managed + overwrite + warn`;
  settings-hook-registration and gitignore-pattern rows use
  `gt-kb-managed + structured-merge + warn`. Defaults still apply if
  the entire block is absent from a row; partial ownership blocks raise
  `InvalidArtifactRecord` (GO Condition C1).

- **`plan_upgrade`** — consults each artifact's `OwnershipMeta` and
  skips rows whose `upgrade_policy` is `preserve` / `transient` /
  `adopter-opt-in`. No effect on current-HEAD behavior (all 42 rows use
  `overwrite` or `structured-merge`) but unlocks preserve/transient
  semantics for future registry / ownership-glob rows.

### Fixed

- `templates/project/AGENTS.md` startup checklist now names root
  `MEMORY.md` (not `memory/MEMORY.md`) — aligns with the GT-KB
  scaffold contract that places `MEMORY.md` at repo root per ADR-0001.
  Codex GO condition P1 carried forward from
  `bridge/gtkb-canonical-terminology-surface-implementation-006.md`
  via `-008`.

### Docs

- New `docs/reference/canonical-terminology.md` published reference page
  with Mermaid diagram of the ADR-0001 three-tier memory architecture.
- `mkdocs.yml` nav: added Canonical Terminology under Reference.
- `docs/reference/templates.md` and `templates/README.md`: updated
  inventory to list the two new canonical-terminology files.
- `docs/bootstrap.md`: manual-copy snippet now copies `rules/*.toml` as
  well as `rules/*.md` so manually bootstrapped projects receive the
  canonical-terminology TOML config.

### Registry

- `templates/managed-artifacts.toml` grew from 40 to 42 records (rule
  count 8 → 10). Both new canonical-terminology rows carry the
  `gt-kb-managed + overwrite + warn` ownership block matching all other
  rule-class rows.

### Reports

- **Agent Red classification report** (`docs/reports/agent-red-classification.md`)
  — generated via `gt project classify-tree` against the Agent Red
  checkout. 7,355 paths classified; 3 owner-decision-pending rows
  (`groundtruth.db`, `requirements-local.txt`, `requirements-test.txt`).
  Zero-write proof: Agent Red `git status --short` is byte-identical
  before and after the classify run.

### Tests

- `tests/test_doctor_canonical_terminology.py` — 16 tests covering 4
  profiles (local-only, dual-agent, dual-agent-webapp, harness-memory)
  + extends inheritance + missing-config ERROR + full-scaffold
  zero-ERROR + Codex P1 AGENTS.md path assertion.
- `tests/test_managed_registry.py` — updated counts (42 total, 10
  rules; `_registry_records()` helper filters `OwnershipGlobArtifact`
  rows; local-only scaffold/upgrade includes the two new
  canonical-terminology rule records).
- `tests/test_scaffold_project.py` — added
  `test_scaffold_agents_md_uses_root_memory_path` asserting generated
  `AGENTS.md` names `MEMORY.md` (not `memory/MEMORY.md`).
- `tests/test_harvest_coverage_helper.py` +
  `tests/test_harvest_coverage_doctor.py` — full coverage of the DA
  harvest coverage helper and doctor integration.
- `tests/test_ownership_loader_agreement.py`,
  `tests/test_ownership_resolver.py`,
  `tests/test_scaffold_consumes_resolver.py`,
  `tests/test_upgrade_dispatches_by_policy.py`,
  `tests/test_doctor_unchanged_without_classify_flag.py`,
  `tests/test_classify_tree_cli.py`,
  `tests/test_classify_tree_read_only.py` — full coverage of
  ownership matrix loader, resolver, scaffold consumption, upgrade
  dispatch, doctor isolation, and classify-tree CLI.

## [0.6.0] - 2026-04-17

### Added — Phase A Tier A operational skills bundle

- **Canonical credential patterns module** (Tier A #1, commit `862045d`) —
  New `src/groundtruth_kb/governance/credential_patterns.py` consolidating
  the credential-class regex catalog into one authoritative module.
  `CREDENTIAL_PATTERNS` + `BASH_EXTRAS` + `PII_PATTERNS` are the three
  named exports; `scan()` runs all three. DB `_REDACTION_PATTERNS` and
  the `credential-scan.py` hook both re-use this module. Immutable
  pre-migration fixture test locks the pattern set against unintended
  drift.

- **`scanner-safe-writer` PreToolUse hook** (Tier A #2, commits `b5e5c6c`
  + `37a88cc`) — New `templates/hooks/scanner-safe-writer.py` intercepts
  Write tool events targeting direct `bridge/*.md` paths and scans the
  proposed content against the canonical credential catalog. Schema v1
  deny-record log at `.claude/hooks/scanner-safe-writer.log` with stable
  `pattern_name`/`catalog_source` contract (`pattern_description` is
  explicitly non-contractual). Scaffold + upgrade + doctor integration
  via `_MANAGED_SETTINGS_PRETOOLUSE_HOOKS` and
  `_plan_missing_managed_files` unconditional repair. PII is passed
  through (email/phone/IPv4 are legitimate in prose).

- **`/gtkb-decision-capture` skill** (Tier A #4, commit `d9325c9`) —
  New `templates/skills/decision-capture/` with `SKILL.md` and
  `helpers/record_decision.py`. Wraps
  `KnowledgeDB.insert_deliberation()` with fixed governance metadata
  (`source_type="owner_conversation"`, `outcome="owner_decision"`,
  `changed_by="prime-builder/decision-capture-skill"`). First skill
  in GT-KB's skills inventory. Scaffold + upgrade + doctor integration
  via `_MANAGED_SKILLS_INITIAL` / `_MANAGED_SKILLS` / new
  `_check_skill_present()` doctor check.

- **`/gtkb-bridge-propose` skill** (Tier A #3, commit `0a60054`) —
  New `templates/skills/bridge-propose/` with `SKILL.md` and
  `helpers/write_bridge.py`. Writes bridge proposal files with a
  credential-only pre-flight scan (iterates `CREDENTIAL_PATTERNS +
  BASH_EXTRAS` directly; excludes PII), overlap-safe redaction via
  `_normalize_hit_intervals` (outermost-label merging), post-redaction
  re-scan as correctness gate, atomic INDEX update with `os.replace()`,
  and 2-attempt retry at INDEX layer only.

- **`/gtkb-spec-intake` skill** (Tier A #5, commit `9629091`) — New
  `templates/skills/spec-intake/` with `SKILL.md` and
  `helpers/spec_intake.py`. Wraps
  `intake.capture_requirement()` / `intake.confirm_intake()` /
  `intake.reject_intake()` with fixed governance metadata
  (`changed_by="prime-builder/spec-intake-skill"`) and
  confirm-before-mutate contract: capture writes a deliberation at
  `outcome="deferred"`; separate confirm or reject step is the only
  path that writes specs or records rejection.

- **Phase A scanner-safe-writer metrics collector** (Tier A #6, commit
  `41ac869`) — New `scripts/collect_phase_a_metrics.py` consumes
  `.claude/hooks/scanner-safe-writer.log` (schema v1 JSONL) and emits
  aggregated deny metrics (per pattern, catalog source, session, date,
  file path) in JSON (stable automation contract) or Markdown (human
  presentation). G5 stability contract: indexes only on `pattern_name`,
  never on `pattern_description`; guarded by
  `test_pattern_names_indexed_not_descriptions`. Forward-compat:
  warn-and-skip on unknown `schema_version` with stderr warning.

### Added — Quality

- **Phase 4C: Structured logging migration** (commit `b1c3359`) —
  New `_logging.py` with split-level defaults (CLI=WARNING,
  bridge=INFO), `_setup_bridge_logging()` with no-raise fallback,
  shared `tests/_print_guard.py` (single source of truth for CI +
  pytest). 12 files migrated from `print()` to structured logging.

- **Phase 4D: Broad exception governance** (commit `23cdf09`) —
  Narrowed 2 sites (db.py IntegrityError, launcher.py Windows),
  removed 1 redundant handler (launcher.py Unix), annotated 21
  non-reraising broad catches with `# intentional-catch:` markers.
  New `tests/test_exception_markers.py` AST-based CI gate enforces
  marker hygiene. Final inventory: 28 handlers (7 exempt re-raise +
  21 annotated + 0 unmarked).

- **Phase 1 operational governance hooks + `source_paths` migration**
  (commit `b9a2071`) — Additional governance hook suite for adopter
  projects plus schema migration adding `source_paths` field to
  specification records for traceability of where implementation
  lives.

### Added — Docs

- **Memory architecture alignment to ADR-0001 three-tier vocabulary**
  (commit `71ef2b0`) — 30 documentation files aligned to use the
  canonical ADR-0001 memory architecture terminology
  (MemBase / Deliberation Archive / Local Memory tiers) across docs,
  templates, and skill content.

### Fixed

- **`intake.py` governance metadata extension** (part of commit
  `9629091`) — Three `intake` functions
  (`capture_requirement`, `confirm_intake`, `reject_intake`) now
  accept optional keyword-only `changed_by: str = "intake-pipeline"`
  parameter; `capture_requirement` also accepts
  `change_reason: str = "..."`. Defaults preserve existing behavior
  for all pre-existing callers (CLI, hook classifier, tests).
  Skill helpers pass skill-specific actor metadata for audit-trail
  differentiation.

- **`source_paths` carry-forward in `update_spec`** (commit
  `8efcbb1`) — `update_spec` previously dropped `source_paths` on
  version update (column missing from INSERT). Now preserved
  through the version chain. Added regression guards.

- **4C CI test-package import resolution** (commit `a3fa4d2`) —
  Added empty `tests/__init__.py` so `from tests._print_guard`
  imports resolve on Linux CI alongside Windows local dev.

## [0.5.0] - 2026-04-15

### Added

- **Phase 4B.9: Whole-package docstring coverage 65% → 85%** — Google-style
  docstrings added to all 119 undocumented nodes across 4 bridge files:
  `bridge/worker.py` (36), `bridge/context.py` (31), `bridge/runtime.py` (29),
  `bridge/poller.py` (23). All 4 files reach 100% docstring coverage.
  Whole-package coverage: 65.1% → 85.3%. CI docstring ratchet in
  `.github/workflows/docstring-coverage.yml` bumped from `--fail-under 64` to
  `--fail-under 80`.

- **Phase 4B.8: Line and branch coverage gates** — ~163 new tests across 11
  new test files covering the bridge subpackage (`handshake`, `context`,
  `launcher`, `poller`, `worker`, `runtime`, import hygiene) and `project/`
  modules (`upgrade`, `doctor`, `scaffold`, `manifest`). Suite: 640 → ~803
  tests. Combined coverage ≥70% (statements ≥70%, branches ≥55%). CI gains
  `--cov-fail-under=70` on the main pytest invocation in the `test-base` job.

- **Phase 4B.7: `mypy --strict` regression guard for full source tree** — A new
  test `tests/test_full_tree_type_checks.py` runs `mypy --strict` against the
  entire `src/groundtruth_kb/` tree (31 source files) and asserts exit code 0.
  Extends the narrower Phase 4B.4 guard which covered only the 4 public API
  files. Test suite: 638 → 640. CI workflow gains a direct `mypy --strict
  src/groundtruth_kb/` step.

### Fixed (internal — no runtime behavior change)

- **Phase 4B.7: Closed 39 `mypy --strict` errors across 5 bridge/intake files** —
  `bridge/poller.py` (17 fixes): platform import stanza changed to
  `sys.platform == "win32"` discriminant; `_FileLock._fh` annotated as
  `BinaryIO | None` with local non-optional `fh: BinaryIO` handle in
  `__enter__`/`__exit__`; `TypedDict` shapes for `_NotificationBatchSummary`
  and `_InboxSummary` with `cast(dict[str, Any], summary)` at return boundaries;
  `subprocess.Popen(**cast(Any, popen_kwargs))` for kwargs unpacking.
  `bridge/worker.py` (10 fixes): same platform import and `_FileLock` pattern;
  two `subprocess.run(**cast(Any, popen_kwargs))` call sites; `event_batch:
  dict[str, Any]` forward declaration before the resident-worker loop.
  `intake.py` (7 fixes): None guard after `insert_deliberation` call (raises
  `RuntimeError`); None guard after `insert_spec` call (returns error dict).
  `bridge/runtime.py` (4 fixes): `mcp: FastMCP[Any] | None` annotation via
  `TYPE_CHECKING` import; `_loads_json` split-check `value is None or value ==
  ""` for str narrowing; `_queue_notification` None guard on `cur.lastrowid`;
  `send_correction_message` casts `recipient` to `Agent` after runtime
  membership check. `bridge/context.py` (1 fix): `artifact_path` variable name
  in second inner for-loop to avoid `Path | None` conflict with outer `Path`.

- **Phase 4B.4: `mypy --strict` regression guard for public API** — A new
  test `tests/test_public_api_type_checks.py` runs `mypy --strict` against
  the four public-API source files (`db.py`, `config.py`, `cli.py`,
  `gates.py`) and asserts exit code 0. The test skips gracefully when mypy
  is not installed. Test suite: 637 → 638.
- **Phase 4B.4: `mypy==1.20.1` added to `[dev]` optional dependency extra**
  — Pinned to the Phase 4A baseline version to prevent spurious regressions
  from mypy version drift. Install via `pip install ".[dev]"`.

### Fixed (internal — no runtime behavior change)

- **Phase 4B.4: Closed 48 `mypy --strict` errors on the public API surface**
  — `db.py` (42 fixes): `type-arg` fixes for bare `dict`/`tuple`/`list[dict]`
  annotations; `return-value` fixes on 22 `insert_*/update_*` methods that
  annotated `-> dict[str, Any]` but returned `dict[str, Any] | None` (public
  API contract correction — callers now statically see the possible `None`
  return). `config.py` (3 fixes): bare `dict` return annotations on two
  private helpers and one field default. `cli.py` (8 fixes): missing
  `-> None` on three `@main.group()` callbacks; bare `dict` function
  parameter; variable name collision (`cols` reused as `set` then `list`);
  `None` guard added at two `insert_deliberation` / `upsert_deliberation_source`
  call sites that now correctly reflect the `| None` return contract.
  `gates.py`: already clean, no changes.

- **Phase 4B.3: Public API docstrings for 27 `KnowledgeDB` and
  `GateRegistry` methods** — Every symbol in `groundtruth_kb.__all__` now
  has a Google-style docstring. Covered methods include `KnowledgeDB.close`,
  all `get_*` / `list_*` / `insert_*` methods on `KnowledgeDB` that were
  previously undocumented, and `GateRegistry.register`,
  `GateRegistry.run_pre_promote`, and
  `GateRegistry.run_pre_resolve_work_item`. A new regression guard test
  (`tests/test_public_api_docstrings.py`) locks public API docstring
  coverage at 100% and will fail CI if a new method is added without a
  docstring. Public API coverage: 81.76% → 100.00% (121/148 → 148/148).
  Test suite: 636 → 637.
- **Phase 4B.2: `PermissionError` wrapped in `GTConfigError`** — An
  unreadable config file (ownership or ACL problem) now raises
  `GTConfigError` instead of letting the raw `PermissionError` propagate.
  The original exception is chained via `__cause__` so debuggers retain
  full traceback access. The error message includes the file path and a
  permissions hint.
- **Phase 4B.2: Warning for missing `[groundtruth]` TOML section** —
  When a TOML config file is found but has no `[groundtruth]` section,
  `GTConfig.load()` now emits a `UserWarning` at the call site (not
  inside the library). The warning clarifies that only core
  `[groundtruth]` settings fall back to env vars and defaults; any
  `[gates]` and `[search]` sections present in the file are still
  applied. This catches the common typo of misspelling `[groundtruth]`.
- **Phase 4B.2: Warning for unknown keys in `[groundtruth]` section** —
  When the `[groundtruth]` section contains keys that are not recognized
  config fields (e.g. `bran_color` instead of `brand_color`),
  `GTConfig.load()` emits a `UserWarning` naming every unknown key.
  Known keys are still applied; only the unrecognized ones are ignored.
  This catches typos that would previously silently have no effect.
- **Phase 4B.1: `GTConfigError`** — New public exception class exported
  from `groundtruth_kb` (grows `__all__` from 15 → 16 symbols). Wraps
  `tomllib.TOMLDecodeError` raised during `GTConfig.load()` so the caller
  sees the offending file path in the message; the original decoder error
  is chained via `__cause__` for debuggers.
- **Phase 4B.1: `gt deliberations` CLI** — The six deliberation subcommands
  (`add`, `upsert`, `get`, `list`, `search`, `link`) that shipped in Phase 3
  now have a documented configuration story via the new Exceptions section
  in `docs/reference/configuration.md`.
- **Phase 4B-housekeeping: `python -m groundtruth_kb` entry point** — New
  `src/groundtruth_kb/__main__.py` shim delegates to `cli.main`, enabling
  `python -m groundtruth_kb <command>` in addition to the installed `gt`
  console script. Useful for CI matrices and for debugging without
  depending on console-script path resolution. Zero side effects at import.
- **Phase 4B-housekeeping: Anthropic API key redaction.** New
  `anthropic_api_key` pattern in `_REDACTION_PATTERNS` matches
  `sk-ant-api<version>-<token>` so leaked Anthropic keys in deliberation
  content are redacted at the DB layer alongside the existing AWS,
  GitHub PAT, Azure SAS, and Agent Red key families.
- **Phase 4B-housekeeping: Exit-code tables for `gt deliberations`
  subcommands.** `docs/reference/cli.md` now documents exit codes for
  `add`, `upsert`, `list`, and `search` (matching the previously-documented
  `rebuild-index`, `get`, and `link`).

### Changed

- **Phase 4B.1: Explicit missing `config_path` now raises
  `FileNotFoundError`.** Previously, `GTConfig.load(config_path=<missing>)`
  silently returned defaults, hiding typos from programmatic callers. The
  new behavior raises `FileNotFoundError` with a recovery hint. Auto-discovery
  (`config_path=None` with nothing found up the parent tree) is unchanged —
  it still falls back to defaults. CLI users are unaffected because
  `--config` already uses `click.Path(exists=True)`.
- **Phase 4B-housekeeping: `actions/checkout@v4 → @v6`.** All 14
  occurrences across 8 workflow files upgraded to the current stable
  major version (GA since 2025-11-20, currently `v6.0.2`). The
  `v6` release introduces Node 24 runtime support and moves
  `persist-credentials` storage to a per-job file under `$RUNNER_TEMP`;
  neither change affects our workflows (no container jobs, no
  authenticated git operations after checkout).

### Internal

- **Phase 4B.2: Test-suite growth.** `tests/test_config.py` grew from 15 to
  19 tests (+4). Two pre-existing tests were updated to include a
  `[groundtruth]` section header (previously empty TOML files; TOML content
  was irrelevant to those tests but the missing section now emits a
  warning). A latent bug in `tests/test_reconciliation.py` was fixed: the
  CLI smoke test was writing `[core]` instead of `[groundtruth]`, meaning
  the `db_path` in that TOML was never being read. Full suite: 632 → 636.
- **Phase 4B.1: Test-suite growth.** `tests/test_config.py` grew from 9 to
  15 tests (net +6). Three previously-passing tests that relied on the
  silent-defaults behavior were rewritten to use real temporary TOML files.
  Full suite: 624 → 630.
- **Phase 4B-housekeeping: Test-suite growth.** Added
  `test_anthropic_api_key_redacted` to `TestRedaction` and
  `test_python_m_groundtruth_kb_runs` to `TestVersion`. Full suite:
  630 → 632.

### Tracked for future sub-rounds (Phase 4B.2+)

- Wrap `PermissionError` in `GTConfigError` when `open()` fails (audit
  finding 4).
- Log a warning when a TOML file has no `[groundtruth]` section (finding 5).
- Log a warning when unknown keys are discarded (finding 6).

## [0.4.0] - 2026-04-14

### Added

- **F1: Spec Schema Enrichment** — New `authority`, `provisional_until`,
  `constraints`, `affected_by`, and `testability` fields on specifications
  with validation and carry-forward semantics. Enables machine-readable
  classification and dependency tracking across the spec graph.
- **F2: Change Impact Analysis** — `KnowledgeDB.compute_impact(operation, spec_data)`
  returns advisory blast radius, related specs, dependents (via `affected_by`
  traversal), applicable constraints, potential assertion conflicts, authority
  distribution, testability summary, and a tier-aware recommendation. Use this
  before editing a spec to see what it touches.
- **F3: Spec Quality Gate** — `score_spec_quality()`, `persist_quality_scores()`,
  `get_quality_history()`, and `get_quality_distribution()` with 5-dimension
  scoring and tier classification (gold / silver / bronze / needs-work).
- **F4: Cross-Cutting Constraint Propagation** — `check_constraints_for_spec()`,
  `get_constraint_coverage()`, `propagate_constraint()`, and
  `remove_constraint_link()` for append-only constraint graph maintenance.
- **F5: Requirement Intake Pipeline** — `classify_requirement()`,
  `capture_requirement()`, `confirm_intake()`, `reject_intake()`,
  `list_intakes()`; new `gt intake` CLI group
  (`classify`/`capture`/`confirm`/`reject`/`list`); and
  `templates/hooks/intake-classifier.py` hook for owner-intent classification
  (directive / constraint / preference / question / exploration) with numeric
  confidence. Confirm creates a KB spec and returns F2 impact, F3 quality
  tier, and F4 constraints in one call.
- **F6: Spec Scaffold** — `scaffold_specs()` generator and
  `SpecScaffoldConfig` API for bootstrapping spec stubs from project
  manifests. New `src/groundtruth_kb/spec_scaffold.py` module. Optional
  integration into `scaffold_project()` via `ScaffoldOptions.spec_scaffold`.
  New `gt scaffold specs` CLI command. 10 tests.
- **F7: Session Health Dashboard** — `session_snapshots` table with
  `INSERT OR REPLACE` write contract, `capture_session_snapshot()`,
  `compute_session_delta()` (current-vs-last with graceful no-prior
  degradation), `render_health_text()` with default thresholds,
  new `gt health` CLI group (`snapshot`/`trends`), and
  `templates/hooks/session-health.py` hook.
- **F8: Knowledge-Base Reconciliation** — `ReconciliationReport` API with
  five detectors: orphaned assertions, stale specs (quality vs age),
  authority conflicts, duplicate specs, and expired provisionals. New
  `src/groundtruth_kb/reconciliation.py` module. New `gt kb reconcile` CLI
  command with per-detector flags and `--all`. 28 tests (27 detector +
  1 CLI smoke).
- **Assertions depth guard** — `_extract_assertion_targets()` now accepts
  `depth: int = 0` kwarg and enforces `_MAX_COMPOSITION_DEPTH` to prevent
  runaway recursion in composed assertion targets. Regression test in
  `test_impact.py`.
- `pytest` test suite grew from 472 (v0.3.0) to 600 tests (+128 tests
  across F1-F8). Ruff clean, docs CLI coverage clean.

### Release gate

This release was the first to run through the `ci-gate` job in
`.github/workflows/publish.yml`, which executes ruff + pytest +
`check_docs_cli_coverage` before the artifact build step. The publish path
is now self-gating: a broken release commit cannot reach PyPI through the
GitHub Release trigger.

### Package maturity note

`groundtruth-kb` remains classified as **alpha** (see `pyproject.toml`
Development Status). This release enables the Deliberation Archive for
external developer use (Python API + CLI + docs) and adds the F1–F8 Spec
Pipeline, but does not claim production readiness for the full dual-agent,
scaffold, or bridge runtime surface.

## [0.3.1] - 2026-04-13

### Changed

- Release plumbing: PyPI publishing via Trusted Publishers (OIDC) is now
  the default distribution path. `pip install groundtruth-kb` works
  worldwide from this version forward.
- No functional changes from 0.3.0. This is a release-infrastructure-only
  version bump to align the tagged commit with the publish workflow.

## [0.3.0] - 2026-04-12

### Added
- **Start Here** first-run guide with verified command sequence
- **CLI Reference** documenting all 14 commands with options and examples
- **Configuration Reference** with full `groundtruth.toml` field inventory
- **Deliberation Archive Guide** for the review/decision capture system
- 10+ Mermaid diagrams across method, architecture, and reference docs
- Examples and templates sections in docs site navigation
- Docs drift prevention CI workflow (version pins, CLI coverage, link checks)
- `gt config` now displays `chroma_path` when configured or defaulted
- SonarCloud analysis workflow with coverage reporting
- CodeQL weekly security scanning
- Semgrep SAST and pip-audit dependency scanning
- Dependabot for pip and GitHub Actions
- Interrogate docstring coverage check (50% minimum)
- CodeRabbit AI code review on pull requests
- `develop` branch for active development

### Fixed
- All install references updated to v0.3.0 (previously mixed v0.1.2/v0.2.0)
- PyPI-style install examples removed (GitHub-installable only)
- CLI error message for missing ChromaDB uses GitHub install form
- `gt project init` snippets in docs include required PROJECT_NAME argument
- TemplateResponse updated to keyword-arg API for Starlette 0.37+
- ruff format applied to all source files
- pip-audit `mkdir` for output directory in CI
- CI installs `[web]` extras for test imports

## [0.2.1] - 2026-04-12

### Fixed
- Text-match contract test monkeypatches `HAS_CHROMADB` for
  ChromaDB-enabled environments

_Note: Git tag v0.2.1 exists but `__version__` was not updated in this
release. The package reports 0.2.0 when installed from the v0.2.1 tag._

## [0.2.0] - 2026-04-07

### Added
- **Layer 2: Project Scaffold** — `gt project init` with three profiles:
  `local-only`, `dual-agent`, `dual-agent-webapp`
- **Layer 3: Workstation Doctor** — `gt project doctor` with auto-install
  and profile-aware readiness checking
- `gt project upgrade` for scaffold file maintenance (dry-run and apply)
- Bridge runtime extracted from production (6 modules: runtime, worker,
  poller, handshake, launcher, context)
- `gt bootstrap-desktop` for same-day prototype setup
- `gt export` and `gt import` for database portability
- Project manifest persistence in groundtruth.toml
- Template sets for hooks, rules, CI workflows, dual-agent, and webapp
- Copilot coding agent instructions (`.github/copilot-instructions.md`)
- Operational configuration capture (method guide 11)
- Desktop setup guide for client workstation bootstrap

### Changed
- Governance gates now support `gate_config` for per-gate configuration
- `GateRegistry.from_config()` accepts `include_builtins` parameter
- Assertion engine expanded with `count`, `json_path`, `all_of`, `any_of` types

## [0.1.2] - 2026-03-28

### Fixed
- Publish workflow targets GitHub Releases (not PyPI)
- Removed stale PyPI install references from documentation
- Version sourced from single location (`__init__.py`)

## [0.1.1] - 2026-03-27

### Fixed
- Publish workflow corrected for GitHub-only distribution

## [0.1.0] - 2026-03-26

### Added
- Core knowledge database with append-only versioning (SQLite)
- 9 artifact types: specifications, tests, work items, operational
  procedures, documents, environment config, testable elements,
  test coverage, backlog snapshots
- Assertion engine with `grep`, `glob`, `grep_absent`, `file_exists`
  types and path confinement
- Pluggable governance gates (ADR/DCL assertion gate, owner approval gate)
- CLI (`gt`): init, seed, assert, summary, history, config, serve
- Web UI (FastAPI + Jinja2) with branding and 11 read-only routes
- 10 method documentation guides
- Example project (task-tracker) with 14-step walkthrough
- CI/CD templates for test, build, and deploy workflows
- Process templates (CLAUDE.md, MEMORY.md, hooks, rules)
- AGPL-3.0-or-later license

[Unreleased]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/Remaker-Digital/groundtruth-kb/releases/tag/v0.1.0
