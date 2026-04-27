NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 7 — `_ci_inventory.py`

**Status:** NEW (slice; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Builds on:**
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md` (Wave 2 GO; umbrella)
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-010.md` (Slice 6 VERIFIED; release-readiness split shipped)

bridge_kind: implementation_slice
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: scripts/rehearse/_ci_inventory.py + tests; driver dispatch already wired (table entry index 2: `("ci", "rehearse._ci_inventory", "run")`)

---

## Prior Deliberations

- `DELIB-0877`: nine-phase GT-KB/application separation program.
- `DELIB-0878`: Phase 1 authority matrix plan — defines the framework-vs-adopter classification basis.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: this slice reuses `_split_helper.emit_result()` for the standard sub-script result envelope. Does NOT use `classify_by_id_prefix()` — CI surfaces lack ID prefixes; classification is filename + content based.
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-010.md` (VERIFIED): classified `release-candidate-gate.yml` as `framework` with signal `release_gate_framework_surface`. Slice 7 inherits this classification verbatim for cross-slice consistency.

No prior bridge thread proposed `_ci_inventory.py`; this is the first slice that lights it up.

## 1. Scope

Single Stage B leaf lane: `scripts/rehearse/_ci_inventory.py`. Produces the CI surface inventory required by Phase 8 plan §2 "Zero-Destructive Dry-Run Output", specifically the two named artifacts:

- `ci-command-inventory.csv` — per-CI-file inventory with classification
- `ci-rewrite-preview.md` — markdown preview of per-CI-file cutover action (move / keep / owner-decide)

Strictly additive: no driver changes (dispatch already registers `ci`), no manifest changes, no changes to `_common.py` or any earlier lane.

## 2. Authoritative Source Set

CI surfaces are filesystem artifacts at known root-relative locations. Two source sweeps:

### 2.1 Workflow files via `.github/workflows/*.yml`

- **Source:** glob `LEGACY_ROOT/.github/workflows/*.yml`. Empirical inventory (verified 2026-04-27 against this checkout):
  - `accessibility.yml`, `build-agent-containers.yml`, `build-api-gateway.yml`, `build-slim-gateway.yml`, `build-test-host.yml`, `chromatic.yml`, `deploy-docs.yml`, `docs-quality.yml`, `lint.yml`, `python-tests.yml`, `release-candidate-gate.yml`, `security-scan.yml`, `sonarcloud.yml`, `visual-regression.yml` (14 files).
- **Classification approach:** filename pattern (highest priority) + content scan (when filename is ambiguous). Rule table in §3.
- **Output rows:** `{path, type=workflow, classification, classification_signal, size_bytes, exists}`.

### 2.2 CI configuration files at root

- **Source:** known root-relative paths probed for existence:
  - `sonar-project.properties`
  - `.coderabbit.yaml` / `.coderabbit.yml`
  - `.pre-commit-config.yaml`
  - `pytest.ini`, `pyproject.toml` (only the `[tool.pytest.ini_options]` / `[tool.ruff]` / `[tool.coverage]` presence is recorded — no parsing of body)
  - `.github/dependabot.yml`
- **Classification approach:** filename + content scan (if file mentions `groundtruth_kb` package → framework signal; if mentions Agent Red app paths like `src/` → adopter signal; root config files default to `adopter` per Sonar org `mike-remakerdigital`/agent-red being adopter scope).
- **Output rows:** `{path, type=ci_config, classification, classification_signal, size_bytes, exists}`.

### 2.3 Cross-reference (read-only)

For each inventoried path, record `gt_classify_tree_ownership` if available. Lane does NOT invoke `gt project classify-tree` itself (that's Slice 4's source) — instead, if `{output_dir}/path_rewrite/classification.json` exists from a prior Slice 4 run in the same rehearsal output dir, look up the row for cross-validation. If absent, leave the column empty. This makes Slice 4 + Slice 7 mutually validating but not strictly ordered.

## 3. Classification Rules

Filename heuristics (matched in declaration order; first match wins):

| Pattern | Classification | Signal |
|---|---|---|
| `release-candidate-gate.yml` | framework | `release_gate_workflow_per_slice6` |
| `^(build\|deploy)-(agent\|api-gateway\|slim-gateway\|test-host).*\.yml$` | adopter | `application_build_or_deploy_workflow` |
| `^(accessibility\|chromatic\|visual-regression)\.yml$` | adopter | `application_ui_gate_workflow` |
| `^(deploy-docs\|docs-quality)\.yml$` | adopter | `application_docs_workflow` |
| `dependabot\.yml` | adopter | `application_dependabot_config` |

Content-based fallback (when no filename rule matches):

| Content signal | Classification | Signal |
|---|---|---|
| Workflow body references `groundtruth_kb` (package import or directory) | framework | `groundtruth_kb_reference` |
| Workflow body references `src/` or `admin-spa/` or `transport-tests/` (Agent Red top-level dirs) | adopter | `agent_red_source_reference` |
| Workflow runs a root-scope linter against both adopter and framework code (`lint.yml` running ruff against the whole tree) | unclassified | `mixed_scope_linter_owner_decision_required` |
| No content signal matched | unclassified | `no_classification_signal` |

Specific calls per content scan:

- `python-tests.yml` — content scan: if it runs `pytest tests/` against Agent Red test paths, classify `adopter` with signal `agent_red_pytest_workflow`. If it runs `pytest tests/groundtruth_kb/`, classify `framework`. If both: `unclassified` with signal `mixed_scope_pytest_owner_decision_required`.
- `lint.yml` — likely `unclassified` (mixed-scope linter); annotated for owner decision.
- `security-scan.yml`, `sonarcloud.yml` — content scan: SonarCloud project key `mike-remakerdigital_agent-red` → adopter; security scan likely scope-neutral but currently scoped to adopter source, so default `adopter` with `security_scan_against_adopter_source`. If content shows otherwise → reclassify.

Per Slice 5 `-004` F1 lesson: classification heuristics are filename + content, NOT just filename. A surface that LOOKS adopter-named but contains framework references is reclassified.

## 4. Output Layout

```
{output_dir}/ci_inventory/
├── ci-command-inventory.csv  # main artifact (per Phase 8 plan §2)
├── ci-rewrite-preview.md     # main artifact (per Phase 8 plan §2)
├── ci_inventory.json         # machine-readable companion (schema in §5)
└── result.json               # standard sub-script result per Wave 2 -003 §4.2
```

The CSV + Markdown outputs are owner-readable; the JSON companion is for downstream lanes / Wave 3 verification matrix consumption.

## 5. Schemas

### 5.1 `ci-command-inventory.csv` columns

```
path,type,classification,classification_signal,size_bytes,exists,gt_classify_tree_ownership
.github/workflows/release-candidate-gate.yml,workflow,framework,release_gate_workflow_per_slice6,1234,true,gt-kb-managed
.github/workflows/build-agent-containers.yml,workflow,adopter,application_build_or_deploy_workflow,5678,true,adopter-owned
sonar-project.properties,ci_config,adopter,agent_red_sonar_config,496,true,adopter-owned
.coderabbit.yaml,ci_config,unclassified,no_classification_signal,0,false,
...
```

### 5.2 `ci-rewrite-preview.md` shape

```markdown
# CI Surface Cutover Preview

Generated: <ISO timestamp>
Source: GTKB-ISOLATION-016 Phase 8 rehearsal `_ci_inventory.py` (Slice 7).

## Summary

- Workflow files: 14 (12 adopter / 1 framework / 1 unclassified)
- CI config files: 5 probed (4 present / 1 absent)
- Owner decisions required: <N> rows

## Per-File Disposition

### Move to `applications/Agent_Red/.github/workflows/` (adopter)

- `.github/workflows/build-agent-containers.yml` — signal: `application_build_or_deploy_workflow`
- `.github/workflows/accessibility.yml` — signal: `application_ui_gate_workflow`
- ...

### Keep at GT-KB root (framework)

- `.github/workflows/release-candidate-gate.yml` — signal: `release_gate_workflow_per_slice6`. Cross-reference: classified `framework` in Slice 6 release-readiness split.

### Owner decision required (unclassified)

- `.github/workflows/lint.yml` — signal: `mixed_scope_linter_owner_decision_required`. Wave 3 verification matrix to resolve.
- ...
```

### 5.3 `ci_inventory.json` schema

```json
{
  "schema_version": 1,
  "generated_at": "ISO timestamp",
  "summary": {
    "workflow_count": 14,
    "ci_config_count": 5,
    "framework_count": 1,
    "adopter_count": 12,
    "unclassified_count": 1,
    "absent_probed_count": 1,
    "owner_decisions_required": 1
  },
  "workflows": [
    {
      "path": ".github/workflows/release-candidate-gate.yml",
      "type": "workflow",
      "classification": "framework",
      "classification_signal": "release_gate_workflow_per_slice6",
      "size_bytes": 1234,
      "exists": true,
      "gt_classify_tree_ownership": "gt-kb-managed"
    },
    ...
  ],
  "ci_configs": [...],
  "warnings": []
}
```

## 6. Common Contract Compliance

Per Wave 2 -003 §4 + Slice 4/5/6 lessons:

- §4.1 signature: `def run(manifest, output_dir, *, dry_run=False, ci_root=None, ci_configs_root=None) -> dict` — ✓
- §4.2 output layout: under `{output_dir}/ci_inventory/`; includes `result.json` from start (Slice 4 -006 F2) — ✓
- §4.3 idempotency: re-runs overwrite — ✓
- §4.4 read-only on LEGACY_ROOT: only reads workflow files + config probes; writes only to `output_dir` — ✓
- §4.5 driver dispatch: already wired (table index 2) — ✓
- §4.6 manifest validation precondition: lane assumes validated manifest (consumes `excluded_paths` only) — ✓
- `_emit_result()` from `_split_helper.py` wraps non-dry-run returns — ✓

Source-override parameters (`ci_root=`, `ci_configs_root=`) follow Slice 5/6 fixture-root pattern — tests pass synthetic state without monkeypatching module constants.

## 7. Test Plan

`tests/scripts/test_rehearse_ci_inventory.py` (new; ~14-16 tests).

Mocking strategy:
- `ci_root=` parameter overrides `.github/workflows/` root for fixture trees
- `ci_configs_root=` parameter overrides project root for CI config probes
- No subprocess invocations; classification is file content based, not `gt classify-tree` based

Test list:

| # | Test | Coverage |
|---|---|---|
| 1 | `test_run_dry_run_returns_skipped` | Common contract dry_run |
| 2 | `test_run_classifies_release_candidate_gate_as_framework` | §3 filename rule + Slice 6 cross-consistency |
| 3 | `test_run_classifies_build_agent_containers_as_adopter` | §3 filename rule for build/deploy workflows |
| 4 | `test_run_classifies_accessibility_chromatic_visual_regression_as_adopter` | §3 UI gate workflows |
| 5 | `test_run_classifies_deploy_docs_as_adopter` | §3 docs workflow rule |
| 6 | `test_run_content_scan_groundtruth_kb_reference_classifies_framework` | §3 content fallback for framework |
| 7 | `test_run_content_scan_src_reference_classifies_adopter` | §3 content fallback for adopter |
| 8 | `test_run_lint_yml_classifies_unclassified_when_mixed_scope` | §3 mixed-scope owner-decision rule |
| 9 | `test_run_pytest_workflow_classifies_by_pytest_target` | §3 python-tests.yml content scan |
| 10 | `test_run_sonar_properties_classifies_adopter` | §2.2 root config classification |
| 11 | `test_run_absent_ci_configs_recorded_with_exists_false` | Probe for absent files records existence flag |
| 12 | `test_run_writes_csv_with_correct_columns` | §5.1 CSV column ordering + escaping |
| 13 | `test_run_writes_preview_markdown_with_three_sections` | §5.2 preview structure |
| 14 | `test_run_writes_ci_inventory_json` | §5.3 JSON companion |
| 15 | `test_run_writes_result_json_on_ok_path` | Slice 4 -006 F2 (ok path) |
| 16 | `test_run_writes_result_json_on_error_path` | Error path forensics |
| 17 | `test_run_cross_references_path_rewrite_classification_when_present` | §2.3 Slice 4 cross-ref optional |
| 18 | `test_run_cross_reference_absent_leaves_column_empty` | §2.3 absent Slice 4 output |
| 19 | `test_run_excluded_paths_skip_workflow_files_under_excluded_top_level` | Manifest `excluded_paths` honored |

Plus 1 driver integration test: advance the missing-lane fixture from `"ci"` to `"membase"` (next-still-missing in dispatch order, since Slice 7 lights up `ci`).

## 8. Files Changed (this slice's commit)

### 8.1 NEW
- `scripts/rehearse/_ci_inventory.py` — ~220 LOC (filename rules + content scanner + 2 emitters)
- `tests/scripts/test_rehearse_ci_inventory.py` — ~480 LOC (~18 tests + workflow fixtures)
- `bridge/gtkb-isolation-016-phase8-wave2-slice7-001.md` (this file)

### 8.2 MODIFIED
- `bridge/INDEX.md` — new slice7 entry at top
- `tests/scripts/test_rehearse_isolation.py` — fixture advances `"ci"` → `"membase"` as next-missing-lane (one-line change; pattern established in Slices 4/5/6)

### 8.3 UNTOUCHED
- `scripts/rehearse_isolation.py`, `_common.py`, `_inventory.py`, `_path_rewrite.py`, `_split_helper.py`, `_bridge_split.py`, `_backlog_split.py`, `_release_readiness_split.py`
- All other Slice 1-6 tests
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`

## 9. Out of Scope

- Stage B remaining lanes: `_membase_export.py`, `_production_effects.py` — separate slices (proposed Slices 8-9).
- Stage C: `_chromadb_regen.py`, `_dashboard_regen.py` — separate slices.
- Stage D: `_rollback.py` — separate slice.
- Resolving `unclassified` rows — surfaced as warnings + owner-decision section in preview markdown; resolution belongs to Wave 3 verification matrix.
- Modifying any workflow file — read-only.
- Invoking `gt project classify-tree` — Slice 4's source. Slice 7 only consumes Slice 4's output if it's present in the same rehearsal output dir.
- Predicting whether a workflow will pass at the new root post-cutover — that's Wave 3 + ISOLATION-018 cutover scope. This slice only inventories and classifies.

## 10. Codex Review Asks

1. Confirm the 14-workflow-file roster + 5-CI-config-probe list in §2 is the correct source set, or flag missing CI surfaces (e.g., a workflow file I overlooked, a config file at a non-root path, a per-language CI config like `tsconfig.json` that should be inventoried here vs. left to a separate lane).
2. Confirm the filename-rules table in §3 is correctly ordered (most-specific first) and that no rule overlaps cause double-classification. Specifically: should `release-candidate-gate.yml` rule be `framework` (matching Slice 6) or should this slice independently classify it? My read: same classification, by Slice 6 reuse, with explicit cross-reference signal.
3. Confirm the content-fallback rules for `lint.yml` (mixed-scope owner-decision-required) vs auto-classifying as `framework` or `adopter`. The risk of auto-classification is silent misallocation; the cost of `unclassified` is one more owner decision.
4. Confirm Test 17 (cross-reference Slice 4's `path_rewrite/classification.json` when present) is the right shape for Slice 4 ↔ Slice 7 mutual validation, vs. either skipping cross-reference entirely or making it strictly required (which would force Slice 4 to run before Slice 7, breaking the umbrella's "lanes 2-11 in any order" promise).
5. Confirm the CSV + Markdown + JSON triple output is appropriate — the Phase 8 plan §2 names CSV + Markdown explicitly; the JSON companion is my addition for machine-readable downstream consumption. If JSON is overkill, drop it.
6. **GO / NO-GO** on Slice 7.

## 11. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
