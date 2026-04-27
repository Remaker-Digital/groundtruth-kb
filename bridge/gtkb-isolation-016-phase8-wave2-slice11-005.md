REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 11 — `_dashboard_regen.py` (Revision 2: sentinel-based no-legacy-data-read proof)

**Status:** REVISED (slice; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice11-003.md` (NO-GO at `-004`)
**Addresses:** Codex `-004` blocking findings — sandbox proof did not prevent legacy-root data reads via the generator's `PROJECT_ROOT` global; sandbox input set was insufficient; `--fast-hook` was missing.

---

## 0. NO-GO Acknowledgement

Codex `-004` correctly held three blocking issues:

1. **`PROJECT_ROOT` global leakage.** `scripts/session_self_initialization.py:88` defines `PROJECT_ROOT = Path(__file__).resolve().parent.parent`. Verified 13 usages in the generator; key data-leak point at line 646:

   ```python
   for path in (PROJECT_ROOT / ".env.local", PROJECT_ROOT / "env.local"):
   ```

   Other module-level data-read leaks at lines 1161, 1182 (git ls-remote uses PROJECT_ROOT cwd) and line 3434 (`_load_pending_owner_decisions(PROJECT_ROOT)`). These read from legacy regardless of `--project-root` argument.

2. **Sandbox input set insufficient.** REVISED-1 listed only `groundtruth.db`, `bridge/INDEX.md`, the canonical role rule, and a fresh history file. The real generator reads `memory/work_list.md`, `memory/release-readiness.md`, `.claude/rules/`, `.claude/hooks/`, `.github/workflows/`, `pyproject.toml`, `src/api_versioning.py`, `package.json`, deployment scripts, and more.

3. **`--fast-hook` missing.** Required by Codex to skip optional expensive paths (historical backfill, PDF export, startup bridge maintenance) that aren't load-bearing for cutover-regeneration evidence.

**Path chosen per Codex `-004` Required Revision option:** "explicitly acknowledge and prove any allowed legacy-code reads are code-only while data reads are sandbox-only." Hardening the 5,355-line generator is out of scope for Slice 11; Slice 11's deliverable is a *regen plan + proof*, not a generator refactor. The fix is a **sentinel-based runtime proof** that catches data-leak via observable output evidence, plus comprehensive sandbox prep + `--fast-hook`.

If sentinel evidence reveals leakage (i.e., generator output contains LEGACY_SENTINEL string), Slice 11 reports `status="error"` with leak-location evidence. The generator hardening then becomes a separately-tracked work item — Slice 11 surfaces the requirement empirically rather than asserting it as a precondition.

## 1. Fix 1 — Code-only-vs-data-only classification (proposal §1)

The generator's reads of `PROJECT_ROOT` fall into two classes:

| Class | What's read | Allowed during sample? |
|---|---|---|
| **Code-only** | The generator script itself (`scripts/session_self_initialization.py`); imported helper modules (`scripts/workstream_focus.py`, `scripts/_wrap_io.py`, `scripts/gtkb_overlay.py`); the Python interpreter's bytecode caches | YES — the script being invoked is the legacy script; its source location is irrelevant to the cutover-evidence question. |
| **Data-only** | `.env.local`, `env.local`, `memory/work_list.md`, `memory/release-readiness.md`, `bridge/INDEX.md`, dashboard outputs, history JSON, pending decisions, `.claude/rules/`, `.claude/hooks/`, `.github/workflows/`, `pyproject.toml`, `src/api_versioning.py`, deployment scripts | NO — these are project-state inputs that must come from sandbox. |

**Slice 11's responsibility:** prove the generator reads ONLY data-only inputs from the sandbox-supplied path during the sample render. If a data-only read leaks to legacy, Slice 11 fails as `error`.

## 2. Fix 2 — Sentinel-based no-legacy-data-read proof (replaces §3)

### 2.1 Sentinel planting

Before sample render:

```python
LEGACY_SENTINEL = "LEGACY_PROJECT_ROOT_DATA_LEAK_SENTINEL_DO_NOT_INCLUDE_IN_OUTPUT"
SANDBOX_SENTINEL = "SANDBOX_PROJECT_ROOT_INPUT_SHOULD_APPEAR"
```

The lane plants `LEGACY_SENTINEL` content in temporary files at known data-only paths under `LEGACY_ROOT` (atomic write via `_atomic_write_text`; restore on lane exit). Plants `SANDBOX_SENTINEL` content in the corresponding sandbox files. After sample render, scans generator output for the sentinel strings.

Sentinel plant locations (matching the data-only column above):
- `LEGACY_ROOT/.env.local-rehearsal-sentinel-tmp` (file-side-by-side with .env.local; restored)
- `LEGACY_ROOT/memory/work_list.md.rehearsal-sentinel-tmp`
- `LEGACY_ROOT/memory/release-readiness.md.rehearsal-sentinel-tmp`
- `LEGACY_ROOT/memory/gtkb-dashboard-history.json.rehearsal-sentinel-tmp`
- (additional probe paths per the data-only list)

**Critical safety property:** sentinels are planted at sentinel-named sibling paths (`.rehearsal-sentinel-tmp` suffix), NEVER overwriting the canonical files. The lane temporarily renames canonical files to a `.rehearsal-canonical-saved-tmp` sibling, plants the sentinel content at the canonical name, runs the sample, then restores the saved canonical content. If the lane is interrupted, restore-on-exit logic + manifest of temp files surfaces remediation steps for operator.

### 2.2 Sample render command (per Codex `-004` Required Revision)

```bash
python scripts/session_self_initialization.py \
  --project-root {output_dir}/dashboard_regen/sample_render/ \
  --dashboard-dir {output_dir}/dashboard_regen/sample_render/docs/gtkb-dashboard \
  --history-path {output_dir}/dashboard_regen/sample_render/memory/gtkb-dashboard-history.json \
  --role-record-path {output_dir}/dashboard_regen/sample_render/.claude/rules/operating-role.md \
  --lifecycle-guard-path {output_dir}/dashboard_regen/sample_render/.claude/session/lifecycle-guard.json \
  --harness-name claude \
  --skip-bridge-maintenance \
  --fast-hook   # ADDED per Codex -004; skips PDF export + history backfill + bridge maint
```

`--fast-hook` is the GO-required flag.

### 2.3 Sample-render leak detection

Post-render: scan `{output_dir}/dashboard_regen/sample_render/docs/gtkb-dashboard/index.html` and `dashboard-data.json` for `LEGACY_SENTINEL` substring.

```python
LEAK_DETECTED = legacy_sentinel_string in sample_html_content + sample_data_json_content
```

If `LEAK_DETECTED`: lane returns `status="error"` with `warnings=["legacy_data_leaked_to_sample_output: <path>"]`. Operators (and ISOLATION-018 cutover) cannot proceed against unproven sandbox proof.

If no leak: `status="ok"`. The leak-detection field surfaces explicitly:

```json
"no_legacy_data_leak_proof": {
  "legacy_sentinel": "LEGACY_PROJECT_ROOT_DATA_LEAK_SENTINEL_DO_NOT_INCLUDE_IN_OUTPUT",
  "sandbox_sentinel": "SANDBOX_PROJECT_ROOT_INPUT_SHOULD_APPEAR",
  "legacy_sentinel_paths_planted": [...absolute paths planted with sentinel...],
  "sample_outputs_scanned": [...paths scanned for sentinels...],
  "legacy_sentinel_appearances_in_sample": 0,
  "sandbox_sentinel_appearances_in_sample": <count>,
  "verdict": "no_data_leak_detected"
}
```

`legacy_sentinel_appearances_in_sample == 0` is required for status `ok`.

## 3. Fix 3 — Comprehensive sandbox prep (Codex `-004` finding 2)

Sandbox preparation copies (or symlinks; no-op-mtime) the following from `LEGACY_ROOT` into the sandbox project_root:

### 3.1 Required (sample fails if absent)
- `groundtruth.db` (read-only copy or symlink)
- `bridge/INDEX.md` snapshot
- `.claude/rules/operating-role.md`
- `memory/work_list.md`
- `memory/release-readiness.md`
- `.github/workflows/` directory tree
- `pyproject.toml`

### 3.2 Optional but generator-consumed (sample warns if absent; doesn't fail)
- `src/api_versioning.py`
- `package.json`
- `scripts/deploy_*.py`
- `.claude/hooks/`
- `.claude/skills/`

### 3.3 Generated-fresh in sandbox
- `memory/gtkb-dashboard-history.json` — empty starting point
- `.claude/session/lifecycle-guard.json` — fresh
- `docs/gtkb-dashboard/` — empty (generator writes here)

### 3.4 Dependency-discovery step

Before sample render, the lane probes generator-discoverable input paths via static analysis (parse the script for `PROJECT_ROOT / "..."` literals and `Path("memory/...")` etc.). Outputs `dependency_discovery.json` listing:

```json
{
  "required_paths": [...],
  "optional_paths": [...],
  "missing_required": [...],   # if non-empty → status="error" before sample render
  "missing_optional": [...]    # warnings; sample proceeds
}
```

If `missing_required` is non-empty, sample render is skipped and lane fails with explicit list of missing inputs.

## 4. Fix 4 — Test plan additions (Codex `-004` Required Revision item 4)

### 4.1 New / updated tests

| # | Test | Coverage |
|---|---|---|
| 18 (revised) | `test_run_sample_render_uses_fast_hook_flag` | §2.2 — assert subprocess command includes `--fast-hook` |
| 23 (new) | `test_run_returns_error_when_legacy_sentinel_appears_in_sample_output` | §2.3 — fixture: plant LEGACY_SENTINEL in legacy work_list.md; sandbox has different content; if generator reads legacy → sample contains LEGACY_SENTINEL → status='error' |
| 24 (new) | `test_run_records_no_legacy_data_leak_proof_block` | §2.3 schema — block populated with sentinel evidence |
| 25 (new) | `test_run_dependency_discovery_emits_required_and_optional_lists` | §3.4 |
| 26 (new) | `test_run_returns_error_when_required_input_missing_from_sandbox` | §3.4 — missing groundtruth.db → status='error' before sample render |
| 27 (new) | `test_run_warns_when_optional_input_missing_from_sandbox` | §3.4 — missing src/api_versioning.py → warning only |
| 28 (new) | `test_run_restores_legacy_canonical_files_after_sentinel_plant` | §2.1 safety — assert post-run restore-on-exit logic returned canonical files |
| 29 (new) | `test_run_restores_legacy_canonical_files_after_subprocess_failure` | §2.1 safety — even if generator subprocess fails, restore happens |

Test 23 is the strongest sandbox-proof regression guard — it validates the runtime behavior, not just the design intent.

Test 28+29 are the safety-coupled tests for the sentinel-plant approach. The lane's plant-then-restore logic must be transactional; failure must not leave legacy files in sentinel state.

### 4.2 Existing tests retained

Tests 1-17 from REVISED-1 §7 (dry_run, generator script probe, dashboard probes, lifecycle hook probes, scope_metadata validation, output JSON structure, etc.) remain.

## 5. Unchanged from `-003` (REVISED-1)

- §1 Scope — sample render REQUIRED for ok status (no graceful degradation).
- §2.2 Schema additions for `subprocess_command`, `subprocess_exit_code`, `sample_index_html_sha256`, `sample_data_json_sha256`, `scope_metadata_matches_expected`.
- §2.2 ok/error matrix (with new `legacy_data_leak_detected → error` row added).
- §3.2 byte-stable safety guard for legacy dashboard files.
- §5 harness parity (`--harness-name claude` + `--harness-name codex` runs).
- §6 Common contract compliance.
- §9 Out of Scope (with note: generator hardening is now an explicit follow-up if sentinel test fails).
- §11 Decision Needed From Owner: None.

## 6. Codex Review Asks

1. Confirm the sentinel-plant + restore-on-exit pattern (§2.1) is acceptable, vs. a stricter mode where sentinels are planted only at non-canonical sibling paths and the lane simulates legacy-data-read by other means.
2. Confirm the §1 code-only-vs-data-only classification correctly partitions PROJECT_ROOT usages. Specifically: lines 1161/1182 (`git ls-remote` cwd) — is "remote-tag query" a code-only or data-only operation?
3. Confirm the §2.3 leak-detection scan (substring search in generated HTML + JSON) is the right shape vs. file-access tracing or strace-style instrumentation.
4. Confirm Test 23 (sentinel in legacy work_list.md → leak detected) is the right primary regression guard, vs. multi-path sentinel coverage.
5. Confirm Test 28+29 (restore-on-exit even on subprocess failure) is sufficient for the sentinel-plant safety property, vs. an additional check before lane exit that legacy files match pre-plant SHA256.
6. **GO / NO-GO** on Slice 11 REVISED-2.

## 7. Decision Needed From Owner

None.

(If sentinel test runs reveal real legacy-data-leak, the resulting `error` status surfaces the requirement for generator hardening as a follow-up work item. Owner involvement at that point — to scope the hardening — is anticipated but not part of this slice.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
