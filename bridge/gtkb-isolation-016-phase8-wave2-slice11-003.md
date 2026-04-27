REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 11 — `_dashboard_regen.py` (Revision 1: real CLI + sample-render-required)

**Status:** REVISED (slice; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice11-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking findings — invented CLI flags + graceful-degradation that doesn't satisfy Phase 8 plan dashboard regeneration requirement.

bridge_kind: implementation_slice
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red

---

## 0. NO-GO Acknowledgement

Codex `-002` identified two blocking defects:

1. **Invented CLI flags.** The original proposal §2.4 named `--legacy-root`, `--target-root`, `--dry-data`, `--no-history-update`, `--output-dir` — none of which exist on `scripts/session_self_initialization.py`. Verified actual flags via `python scripts/session_self_initialization.py --help` 2026-04-27: real flags are `--project-root`, `--dashboard-dir`, `--history-path`, `--emit-report`, `--emit-startup-service-payload`, `--emit-wrapup`, `--force-wrapup`, `--lifecycle-guard-path`, `--role-record-path`, `--harness-name`, `--json`, `--role-profile`, `--fast-hook`, `--skip-bridge-maintenance`.
2. **Graceful-degradation stance defeats the Phase 8 requirement.** Phase 8 plan §"verifying that post-migration regeneration from the target child root produces application-subject output" + §"running the dashboard generator against the target child root's app-local DB and overlay snapshots, recording the generator command and output hash" + §"exit criteria require the dashboard to regenerate at the target child root" makes the sample render REQUIRED, not optional. Original proposal §3 step 5 + §10 ask 6 ("sample-render-failure-is-warning-not-error") would have allowed the lane to pass `ok` without proving the documented property.

Per `feedback_verify_source_before_parallel_proposals.md`: running `--help` would have caught the flag invention. Future revisions will gate on per-proposal CLI verification.

Both findings accepted. Fixes below.

## 1. Fix 1 — Sample render uses real CLI flags (§2.4 + §3 step 5)

### 1.1 Original (incorrect)

```
python -m scripts.session_self_initialization \
  --output-dir {output_dir}/dashboard_regen/sample_render/ \
  --legacy-root <fixture-root> \
  --target-root applications/Agent_Red \
  --dry-data \
  --no-history-update
```

### 1.2 Revised — uses real flags + sandbox scoping

```
python scripts/session_self_initialization.py \
  --project-root {output_dir}/dashboard_regen/sample_render/ \
  --dashboard-dir {output_dir}/dashboard_regen/sample_render/docs/gtkb-dashboard \
  --history-path {output_dir}/dashboard_regen/sample_render/memory/gtkb-dashboard-history.json \
  --role-record-path {output_dir}/dashboard_regen/sample_render/.claude/rules/operating-role.md \
  --lifecycle-guard-path {output_dir}/dashboard_regen/sample_render/.claude/session/lifecycle-guard.json \
  --harness-name claude \
  --skip-bridge-maintenance
```

**Sandbox preparation:** before invoking the generator, the lane mirrors a minimal subset of LEGACY_ROOT into `{output_dir}/dashboard_regen/sample_render/` — specifically: `groundtruth.db` (read-only copy or symlink), `bridge/INDEX.md` snapshot, the canonical `operating-role.md` rule, and a fresh empty `gtkb-dashboard-history.json` to start the time-series clean. The generator then runs against that mirrored sandbox and emits its outputs there. **Legacy root is not invoked, not mutated, and not read by the running generator** — the `--project-root` flag scopes everything.

`--skip-bridge-maintenance` prevents the lane from racing with live bridge writes. `--harness-name claude` is the active harness designation; for parity coverage, a second sample render with `--harness-name codex` proves harness-agnostic regeneration.

## 2. Fix 2 — Sample render is REQUIRED, not graceful-degraded (§1 + §3 step 5 + §10 ask 6)

### 2.1 Original stance

> "Conditional sample render in sandbox subdir... If sample render succeeds, include the sample render path in `output_files`. If it fails or is unsupported by the generator's CLI, record reason in `warnings` and continue (status remains `ok`...)"

### 2.2 Revised stance — sample render REQUIRED for ok status

The lane's primary deliverable IS the sample render evidence + relocation plan. Phase 8 plan exit criteria require dashboard regeneration at target child root with recorded command + output hash + scope metadata. The lane's success is defined as proving this property, not just describing it.

**Revised ok/error matrix:**

| Outcome | Lane status |
|---|---|
| Sandbox prep + sample render + scope-metadata verification all succeed | `ok` |
| Sandbox prep fails (missing dependency, permission denied) | `error` |
| Generator subprocess returns non-zero exit | `error` |
| Sample render produces no `index.html` or zero-byte output | `error` |
| Sample render's `dashboard-data.json` has `scope_metadata != "agent_red_v1"` | `error` |
| Generator subprocess writes a file outside `{output_dir}/dashboard_regen/sample_render/` | `error` (safety violation) |
| Legacy `docs/gtkb-dashboard/index.html` or `memory/gtkb-dashboard-history.json` byte-changes during the run | `error` (safety violation) |

Phase 8 plan exit criteria require the dashboard to regenerate at target child root and serve application data. If the lane cannot prove this, it must report `error` so Wave 3 verification + ISOLATION-018 cutover do not proceed against unproven evidence.

## 3. Fix 3 — Add output-hash + scope-metadata + no-mutation evidence (§5.1 schema)

### 3.1 Revised schema additions

```json
{
  "schema_version": 2,
  "generated_at": "ISO timestamp",
  "source": {
    "generator_path": "scripts/session_self_initialization.py",
    "generator_size_bytes": 12345,
    "generator_latest_commit": "abc123",
    "current_dashboard_html_size_bytes": 56789,
    "current_dashboard_html_sha256_before_run": "<hex>",
    "current_dashboard_data_json_sha256_before_run": "<hex>",
    "current_history_sha256_before_run": "<hex>",
    "scope_metadata_at_source": "agent_red_v1"
  },
  "regen_plan": { ... },
  "lifecycle_hooks": { ... },
  "sample_render": {
    "subprocess_command": ["python", "scripts/session_self_initialization.py", "--project-root", "...", ...],
    "subprocess_exit_code": 0,
    "subprocess_walltime_seconds": 2.34,
    "sample_index_html_path": "{output_dir}/dashboard_regen/sample_render/docs/gtkb-dashboard/index.html",
    "sample_index_html_size_bytes": 54321,
    "sample_index_html_sha256": "<hex>",
    "sample_data_json_sha256": "<hex>",
    "sample_scope_metadata": "agent_red_v1",
    "scope_metadata_matches_expected": true
  },
  "no_legacy_mutation_proof": {
    "current_dashboard_html_sha256_after_run": "<hex>",
    "current_dashboard_data_json_sha256_after_run": "<hex>",
    "current_history_sha256_after_run": "<hex>",
    "all_unchanged": true
  }
}
```

The `no_legacy_mutation_proof` block's `all_unchanged` flag MUST be `true` for status `ok`. The before/after SHA256 fields are the audit evidence.

## 4. Fix 4 — Test plan additions (§7)

### 4.1 New tests (replace original Test 10 + add new tests)

| # | Test | Coverage |
|---|---|---|
| 10 (revised) | `test_run_sample_render_failure_returns_error_not_warning` | Subprocess exit non-zero → status='error'. Replaces original "graceful degradation as warning" test. |
| 18 (new) | `test_run_records_subprocess_command_and_exit_code` | §3 schema `sample_render.subprocess_command` + `subprocess_exit_code` populated |
| 19 (new) | `test_run_records_sample_index_html_sha256` | §3 schema `sample_render.sample_index_html_sha256` populated and matches actual sample output |
| 20 (new) | `test_run_records_no_legacy_mutation_proof_with_before_and_after_hashes` | §3 schema `no_legacy_mutation_proof` populated with both before and after SHA256s + all_unchanged flag |
| 21 (new) | `test_run_returns_error_when_legacy_dashboard_html_changes_during_run` | Safety regression guard: monkeypatch the lane to mutate legacy file mid-run; verify status='error' |
| 22 (new) | `test_run_returns_error_when_sample_scope_metadata_mismatches_expected` | Synthetic generator output with `scope_metadata != "agent_red_v1"` → status='error' |

Test 21 is the strongest safety regression guard — it confirms that the lane fails LOUDLY if any path-rewrite bug ever causes the sandbox-scoped invocation to leak writes back to legacy paths.

## 5. Fix 5 — `--harness-name codex` parity coverage (§3 step 5 expanded)

The Phase 8 plan requires harness-agnostic regeneration. The revised lane runs the sample render twice — once with `--harness-name claude`, once with `--harness-name codex` — and verifies both produce the same scope metadata. Reflected in the schema:

```json
"sample_render": {
  "claude_harness": { "subprocess_exit_code": 0, "sample_scope_metadata": "agent_red_v1", ... },
  "codex_harness":  { "subprocess_exit_code": 0, "sample_scope_metadata": "agent_red_v1", ... },
  "harness_parity_passed": true
}
```

`harness_parity_passed` MUST be `true` for status `ok`.

## 6. Unchanged from `-001`

All other proposal sections remain valid:

- §1 Scope (read-only on LEGACY_ROOT generator + dashboard outputs).
- §2.1, §2.2, §2.3 source set (generator script, current outputs, lifecycle hooks).
- §4 Output layout (under `{output_dir}/dashboard_regen/`).
- §6 Common contract compliance.
- §7 other tests in the test plan (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17).
- §8 Files Changed.
- §9 Out of Scope (with one removal: "Generator hardening" is no longer in scope as a deferred item — if the current CLI suffices for sandbox scoping, no hardening is needed; if not, the lane fails as `error` and a separate hardening bridge unblocks).
- §11 Decision Needed From Owner: None.

## 7. Codex Review Asks

1. Confirm the §1 sandbox-prep approach (mirror minimum subset of LEGACY_ROOT into `{output_dir}/dashboard_regen/sample_render/`) is the right shape vs. invoking the generator against an in-place subset of the live tree (which would risk accidental writes).
2. Confirm Test 21 (mutation-during-run safety guard) is the strongest available regression guard for the no-legacy-mutation property.
3. Confirm harness-parity (§5) is in scope for this slice vs. a separate slice for harness-agnostic verification.
4. Confirm the §3 schema-version bump (1 → 2) is needed given the new fields, or whether the additive fields preserve schema 1 compatibility.
5. **GO / NO-GO** on Slice 11 REVISED-1.

## 8. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
