NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 11 — `_dashboard_regen.py`

**Status:** NEW (slice; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Builds on:**
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md` (Wave 2 GO; umbrella)
- AR-DASH-001 (DONE per `memory/work_list.md` — dashboard already adopter-scoped with `agent_red_v1` metadata; this slice plans the relocation, not a re-scope)

bridge_kind: prime_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: scripts/rehearse/_dashboard_regen.py + tests; driver dispatch already wired (table entry index 5: `("dashboard", "rehearse._dashboard_regen", "run")`)

**Filed in parallel with:** Slices 7, 8, 9 (Stage B) and 10 (`_chromadb_regen`) per owner direction 2026-04-27. Lanes are independent at the implementation level per umbrella -004.

---

## Prior Deliberations

- `DELIB-0877`: nine-phase GT-KB/application separation program.
- `DELIB-0878`: Phase 1 authority matrix plan.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: this slice reuses `_split_helper.emit_result()`. Does NOT use ID-prefix classification — the dashboard is a single adopter-scoped artifact (Agent Red Project Dashboard), so this slice plans a relocation, not a partition.
- AR-DASH-001 (memory/work_list.md "Completed" section): the dashboard scope was already corrected in S308 to "Agent Red Project Dashboard" with `scope_confidence="agent_red_current_heuristic"` for current rows and `scope_confidence="agent_red_inferred"` for backfilled history. This slice's plan continues that scope semantics at the new root location.
- GTKB-GOV-011 (also `memory/work_list.md` "Completed"): the generator is `scripts/session_self_initialization.py`; lifecycle hooks `SessionStart` and `Stop` invoke it. Both must continue to function from the target child root.

## 1. Scope

Single Stage C leaf lane: `scripts/rehearse/_dashboard_regen.py`. Produces a **dashboard regeneration plan** for the target child root, plus a **sample render** at the rehearsal sandbox output (NOT at the target child root, which doesn't exist yet). The lane proves that the dashboard generator can produce coherent adopter-scope output when invoked from the target child root convention.

Strictly additive: no driver changes (dispatch already registers `dashboard`), no manifest changes, no changes to `_common.py` or any earlier lane. Read-only on `scripts/session_self_initialization.py`. Sample render writes only to `{output_dir}/dashboard_regen/sample_render/`.

**Critical scope distinction:** the lane does NOT invoke the generator against the live legacy root in a way that would mutate `docs/gtkb-dashboard/index.html` or `memory/gtkb-dashboard-history.json`. Sample render is sandbox-only.

## 2. Authoritative Source Set

### 2.1 Generator script

- **Source:** `LEGACY_ROOT/scripts/session_self_initialization.py` (presence + signature probe; NOT executed against live root).
- Records: file existence, size, latest commit SHA touching it, function signatures of public entry points (extracted via AST parse without import-execute).

### 2.2 Current dashboard outputs (for shape reference)

- `LEGACY_ROOT/docs/gtkb-dashboard/index.html` (presence + size; DOES NOT parse HTML)
- `LEGACY_ROOT/docs/gtkb-dashboard/dashboard-data.json` (presence + size; structurally parses JSON for top-level keys, scope metadata; does NOT include data-row contents in plan output)
- `LEGACY_ROOT/docs/gtkb-dashboard/agent-red-project-dashboard.pdf` (presence + size only)
- `LEGACY_ROOT/docs/gtkb-dashboard/grafana/` (subdirectory presence + file list)
- `LEGACY_ROOT/memory/gtkb-dashboard-history.json` (presence + size + structural parse for time-series row count, scope_confidence values)

### 2.3 Lifecycle hook configuration

- `LEGACY_ROOT/.claude/settings.json` (probe for `SessionStart` and `Stop` hook entries that invoke the generator)
- `LEGACY_ROOT/.codex/hooks.json` (Codex parity intent — disabled on Windows per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, but the hook intent must be carried to the target root)

### 2.4 Sample render (sandbox-only)

The lane invokes the generator with explicit fixture parameters:

```
python -m scripts.session_self_initialization \
  --output-dir {output_dir}/dashboard_regen/sample_render/ \
  --legacy-root <fixture-root> \
  --target-root applications/Agent_Red \
  --dry-data \
  --no-history-update
```

**Conditional on the generator supporting these flags.** If `session_self_initialization.py` does not currently expose `--legacy-root` / `--target-root` / `--dry-data` flags, this slice's algorithm degrades gracefully: emit a regen plan WITHOUT a sample render, and surface as an OWNER_DECISION_REQUIRED row recommending generator hardening as a separate work item before ISOLATION-018 cutover.

## 3. Algorithm

1. **Probe** generator script per §2.1.
2. **Probe** current dashboard artifacts per §2.2 (presence + size + structural shape; no content embedding).
3. **Probe** lifecycle hooks per §2.3.
4. **Compute regen plan**:
   - Target dashboard path: `applications/Agent_Red/docs/gtkb-dashboard/index.html`
   - Target history path: `applications/Agent_Red/memory/gtkb-dashboard-history.json`
   - Target generator script: `applications/Agent_Red/scripts/session_self_initialization.py` (relocated)
   - Lifecycle hook update plan: `applications/Agent_Red/.claude/settings.json` SessionStart + Stop entries point to the relocated generator
   - Codex parity hook update plan: same for `.codex/hooks.json`
5. **Conditionally attempt sample render** per §2.4. Capture: command exit code, generated `index.html` byte size, generated `dashboard-data.json` parse + scope metadata. If sample render succeeds, include the sample render path in `output_files`. If it fails or is unsupported by the generator's CLI, record reason in `warnings` and continue (status remains `ok`; the slice's primary deliverable is the plan, sample is bonus evidence).
6. **Emit plan + summary.**

## 4. Output Layout

```
{output_dir}/dashboard_regen/
├── dashboard-regen-plan.json     # main artifact (machine-readable plan)
├── dashboard-regen-preview.md    # markdown summary for owner review
├── sample_render/                # conditional, present if §3 step 5 succeeds
│   ├── index.html                # sample dashboard render at target child root convention
│   └── dashboard-data.json       # sample data with adopter scope only
└── result.json                   # standard sub-script result per Wave 2 -003 §4.2
```

## 5. Schemas

### 5.1 `dashboard-regen-plan.json`

```json
{
  "schema_version": 1,
  "generated_at": "ISO timestamp",
  "source": {
    "generator_path": "scripts/session_self_initialization.py",
    "generator_exists": true,
    "generator_size_bytes": 12345,
    "generator_latest_commit": "abc123",
    "current_dashboard_html_size_bytes": 56789,
    "current_dashboard_data_json_size_bytes": 23456,
    "current_dashboard_data_top_level_keys": ["scope", "scope_metadata", "kpi_history", ...],
    "current_history_size_bytes": 34567,
    "current_history_row_count": 56,
    "scope_metadata_at_source": "agent_red_v1"
  },
  "regen_plan": {
    "target_generator_path": "applications/Agent_Red/scripts/session_self_initialization.py",
    "target_dashboard_path": "applications/Agent_Red/docs/gtkb-dashboard/index.html",
    "target_data_json_path": "applications/Agent_Red/docs/gtkb-dashboard/dashboard-data.json",
    "target_history_path": "applications/Agent_Red/memory/gtkb-dashboard-history.json",
    "target_grafana_path": "applications/Agent_Red/docs/gtkb-dashboard/grafana"
  },
  "lifecycle_hooks": {
    "claude_settings_session_start_update_required": true,
    "claude_settings_stop_update_required": true,
    "codex_hooks_parity_update_required": true
  },
  "sample_render": {
    "attempted": true,
    "succeeded": true,
    "sample_index_html_size_bytes": 54321,
    "sample_data_json_top_level_keys": ["scope", "scope_metadata", ...],
    "sample_scope_metadata": "agent_red_v1",
    "scope_metadata_matches_expected": true
  },
  "warnings": []
}
```

### 5.2 `dashboard-regen-preview.md` shape

```markdown
# Dashboard Regeneration Plan

Generated: <ISO timestamp>
Source: GTKB-ISOLATION-016 Phase 8 rehearsal `_dashboard_regen.py` (Slice 11).

## Summary

- Generator: `scripts/session_self_initialization.py` (12,345 bytes)
- Current dashboard: `docs/gtkb-dashboard/index.html` (56,789 bytes); scope `agent_red_v1` ✓
- Current history: `memory/gtkb-dashboard-history.json` (34,567 bytes; 56 rows)
- Sample render: succeeded (54,321 byte index.html; scope `agent_red_v1` confirmed)

## Relocation Plan

| Source path | Target path |
|---|---|
| `scripts/session_self_initialization.py` | `applications/Agent_Red/scripts/session_self_initialization.py` |
| `docs/gtkb-dashboard/index.html` | `applications/Agent_Red/docs/gtkb-dashboard/index.html` |
| `docs/gtkb-dashboard/dashboard-data.json` | `applications/Agent_Red/docs/gtkb-dashboard/dashboard-data.json` |
| `docs/gtkb-dashboard/grafana/` | `applications/Agent_Red/docs/gtkb-dashboard/grafana/` |
| `memory/gtkb-dashboard-history.json` | `applications/Agent_Red/memory/gtkb-dashboard-history.json` |

## Lifecycle Hook Updates Required

- `.claude/settings.json` SessionStart: update path reference to relocated generator
- `.claude/settings.json` Stop: update path reference to relocated generator
- `.codex/hooks.json`: matching parity update (Windows-disabled; carries forward as forward-compatible intent per ADR-CODEX-HOOK-PARITY-FALLBACK-001)

## Cutover Procedure (informational; ISOLATION-018 executes)

1. Move generator + dashboard outputs + history to target paths (handled by Slice 4 path_rewrite).
2. Update lifecycle hook configurations to reference relocated generator.
3. Run generator at target root: confirms `agent_red_v1` scope metadata, expected KPI structure.
4. Acceptance gate: output index.html + dashboard-data.json size within ±10% of source; scope metadata matches `agent_red_v1`.

## Owner Decisions Required

- (None for this slice; the dashboard is already adopter-scoped per AR-DASH-001.)
```

## 6. Common Contract Compliance

- §4.1 signature: `def run(manifest, output_dir, *, dry_run=False, project_root=None, generator_invoker=None) -> dict` — ✓
- §4.2 output layout: under `{output_dir}/dashboard_regen/`; includes `result.json` — ✓
- §4.3 idempotency: re-runs overwrite — ✓
- §4.4 read-only on LEGACY_ROOT (probes only; generator invocation writes to sandbox subdirectory of `output_dir`, NEVER to legacy root) — ✓
- §4.5 driver dispatch: already wired (table index 5) — ✓
- `_emit_result()` from `_split_helper.py` wraps non-dry-run returns — ✓

`project_root=` and `generator_invoker=` parameters follow Slice 5/6/7/8/9/10 fixture-root pattern. `generator_invoker=` is a callable injection for testability (default: `subprocess.run`-based; tests inject a fake that returns canned output).

## 7. Test Plan

`tests/scripts/test_rehearse_dashboard_regen.py` (new; ~12-14 tests).

Mocking strategy:
- `project_root=` parameter overrides `LEGACY_ROOT` for fixture trees
- `generator_invoker=` callable injection avoids real subprocess invocation in tests; tests pass a fake invoker that returns canned `index.html` + `dashboard-data.json` content
- Tests construct synthetic file trees under `tmp_path`

Test list:

| # | Test | Coverage |
|---|---|---|
| 1 | `test_run_dry_run_returns_skipped` | Common contract dry_run |
| 2 | `test_run_probes_generator_existence` | §3 step 1 |
| 3 | `test_run_emits_warning_when_generator_absent` | Edge: missing generator |
| 4 | `test_run_probes_current_dashboard_artifacts` | §3 step 2 — presence + size only, no content embed |
| 5 | `test_run_does_not_parse_dashboard_html_content` | **Safety:** assert no `read_text` against index.html beyond size check |
| 6 | `test_run_probes_lifecycle_hooks` | §3 step 3 |
| 7 | `test_run_does_not_invoke_generator_against_legacy_root` | **Safety regression guard:** monkeypatch generator invoker; assert no invocation with `--output-dir=docs/gtkb-dashboard` or any legacy-root path |
| 8 | `test_run_attempts_sample_render_in_sandbox` | §3 step 5 — invocation parameters scope to sandbox |
| 9 | `test_run_records_sample_render_success` | §3 step 5 ok path |
| 10 | `test_run_records_sample_render_failure_as_warning_not_error` | §3 step 5 graceful degradation; status remains ok |
| 11 | `test_run_validates_sample_scope_metadata_matches_agent_red_v1` | §5.1 sample.scope_metadata_matches_expected |
| 12 | `test_run_emits_relocation_plan_with_five_path_pairs` | §5.1 regen_plan |
| 13 | `test_run_emits_lifecycle_hook_update_flags` | §5.1 lifecycle_hooks |
| 14 | `test_run_writes_dashboard_regen_plan_json` | §5.1 |
| 15 | `test_run_writes_preview_markdown` | §5.2 |
| 16 | `test_run_writes_result_json_on_ok_path` | Slice 4 -006 F2 |
| 17 | `test_run_writes_result_json_on_error_path` | Error path forensics |

Plus 1 driver integration test: advance the missing-lane fixture per Stage B/C GO ordering.

## 8. Files Changed (this slice's commit)

### 8.1 NEW
- `scripts/rehearse/_dashboard_regen.py` — ~210 LOC (probes + plan + sample render orchestration)
- `tests/scripts/test_rehearse_dashboard_regen.py` — ~440 LOC (~17 tests + fake-invoker fixtures)
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-001.md` (this file)

### 8.2 MODIFIED
- `bridge/INDEX.md` — new slice11 entry at top
- `tests/scripts/test_rehearse_isolation.py` — fixture advances per Stage B/C GO ordering

### 8.3 UNTOUCHED
- `scripts/rehearse_isolation.py`, `_common.py`, `_inventory.py`, `_path_rewrite.py`, `_split_helper.py`, `_bridge_split.py`, `_backlog_split.py`, `_release_readiness_split.py`, `session_self_initialization.py`
- All other Slice 1-10 tests
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`
- `docs/gtkb-dashboard/` (read-only access; no generator invocation against this path)
- `memory/gtkb-dashboard-history.json` (read-only access)

## 9. Out of Scope

- Stage B sibling lanes: `_ci_inventory.py` (Slice 7), `_membase_export.py` (Slice 8), `_production_effects.py` (Slice 9) — separate parallel slices.
- Stage C sibling: `_chromadb_regen.py` (Slice 10) — separate parallel slice.
- Stage D: `_rollback.py` (Slice 12) — composes other lanes' outputs; deferred.
- Actual dashboard relocation — that's ISOLATION-018 cutover work; this slice produces only the plan.
- Generator hardening (adding `--legacy-root` / `--target-root` / `--dry-data` flags if absent) — surfaced as warning if needed; separate work item.
- Re-scoping the dashboard — already adopter-scoped per AR-DASH-001 (DONE).
- Grafana subdirectory content classification — moved as a unit; per-file Grafana asset classification is out of scope.
- Live dashboard regeneration against `docs/gtkb-dashboard/` — strictly forbidden.

## 10. Codex Review Asks

1. Confirm the §2.1 AST-parse-without-execute approach for probing the generator script's signature is right vs. importing the module (which would execute top-level code). My read: AST parse is safer.
2. Confirm the §2.4 conditional sample render (degrade gracefully if generator CLI doesn't support `--legacy-root` / `--target-root` / `--dry-data`) is the right shape. Alternative: require generator hardening as Slice 11 prerequisite (which would block Slice 11 on a separate work item).
3. Confirm Test 7 (`test_run_does_not_invoke_generator_against_legacy_root`) regression-guards the "sandbox-only invocation" property correctly.
4. Confirm the §5.1 schema's `sample_render.scope_metadata_matches_expected` field is the right cross-validation between the generator's output and the AR-DASH-001 `agent_red_v1` scope contract.
5. Confirm the relocation plan in §5.1 (five source→target path pairs) is complete vs. missing dashboard-related paths I haven't probed.
6. Confirm the sample-render-failure-is-warning-not-error stance (Test 10) is right vs. promoting to status='error'. My read: the slice's primary deliverable is the plan; sample is supporting evidence.
7. **GO / NO-GO** on Slice 11.

## 11. Decision Needed From Owner

None.

(Generator hardening for `--target-root` / `--dry-data` flags may be surfaced as a §2.4 graceful-degradation warning if those flags are not yet present in `session_self_initialization.py`. If it appears, it becomes a separate work item.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
