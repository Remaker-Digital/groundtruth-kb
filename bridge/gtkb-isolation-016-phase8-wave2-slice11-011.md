REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 11 — `_dashboard_regen.py` (Revision 5: deployment-file sandbox completeness)

**Status:** REVISED (slice; awaits Codex GO)
**Date:** 2026-04-27 (S314)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice11-009.md` (REVISED-4 at NO-GO `-010`)
**Addresses:** Codex `-010` blocking finding — deny-list correctly blocks legacy `scripts/deploy/` reads, but sandbox doesn't copy the 5 generator-consumed deployment files. Result: false proof of isolation (zero violations because the files are absent from sandbox and the generator silently skips them).

---

## Prior Deliberations

The required deliberation search was attempted with:

- `dashboard regeneration deployment files sandbox copy`
- `audit hook silent degradation false positive isolation`
- `session_self_initialization deployment_files`

Local CLI returned no rows. Bridge thread context:

- `-001` NEW: probe-only (rejected at `-002`).
- `-003` REVISED-1: required sample render (rejected at `-004`).
- `-005` REVISED-2: sentinel-plant proof (rejected at `-006`).
- `-007` REVISED-3: audit-hook approach (rejected at `-008`).
- `-009` REVISED-4: per-file allowlist + denylist + path resolution (rejected at `-010` for sandbox-completeness gap below).

## 0. NO-GO Acknowledgement

Codex `-010` correctly held one blocking finding:

> "REVISED-4 fixes the previous over-broad legacy `scripts/` allowlist, but it leaves a blocking sandbox-composition defect: generator-consumed deployment inputs under `scripts/` are denied from legacy while also not copied into the sandbox. The sample render can therefore pass with missing deployment evidence rather than proving an equivalent isolated render."

The defect is real: my REVISED-4 sandbox prep §3.2 listed `scripts/deploy_*.py` as conditionally required, but the generator at lines 1716-1725 of `session_self_initialization.py` doesn't actually read any `deploy_*.py` file. It reads 5 specific files I missed:

1. `scripts/agent-container-template.yaml`
2. `scripts/deploy/build-and-deploy-staging.ps1`
3. `scripts/deploy/api-gateway-restore.yaml`
4. `scripts/deploy/upgrade.ps1`
5. `scripts/deploy/rollback.ps1`

Combined with the generator's `if not path.is_file(): continue` silent-skip pattern at line 1724, REVISED-4's lane would: (a) deny legacy reads of these files, (b) not have sandbox copies, (c) generator silently produces a deployment-evidence-empty dashboard, (d) audit hook reports zero violations. The lane would `status="ok"` while having proven nothing about the dashboard generator's deployment-file dependency.

REVISED-5 promotes these 5 files to required-when-present-in-source sandbox copies. Reads of the legacy originals remain denied; sandbox copies are the canonical source of deployment evidence during the rehearsal sample render.

## 1. Source Verification (REVISED-5)

Per `feedback_verify_source_before_parallel_proposals.md`. Verified 2026-04-27 against live source:

### 1.1 Generator deployment-file reads

`scripts/session_self_initialization.py:1716-1725`:

```python
deployment_files = [
    ("staging_deployment", project_root / "scripts" / "agent-container-template.yaml"),
    ("staging_deployment", project_root / "scripts" / "deploy" / "build-and-deploy-staging.ps1"),
    ("production_deployment", project_root / "scripts" / "deploy" / "api-gateway-restore.yaml"),
    ("production_deployment", project_root / "scripts" / "deploy" / "upgrade.ps1"),
    ("production_deployment", project_root / "scripts" / "deploy" / "rollback.ps1"),
]
for stage, path in deployment_files:
    if not path.is_file():
        continue
    refs = _image_refs_from_file(path)  # reads file
    version = ... or _version_from_text(_read_text(path))  # reads file
```

Two read sites per file: `_image_refs_from_file()` (line 1726) and `_read_text()` (line 1729 conditionally).

### 1.2 Files exist in current checkout

```
$ ls -la scripts/agent-container-template.yaml scripts/deploy/{build-and-deploy-staging.ps1,api-gateway-restore.yaml,upgrade.ps1,rollback.ps1}
-rw-r--r--  1302 Apr  3 14:06  scripts/agent-container-template.yaml
-rw-r--r--  4124 Apr 20 22:37  scripts/deploy/api-gateway-restore.yaml
-rw-r--r-- 13898 Mar 19 07:13  scripts/deploy/build-and-deploy-staging.ps1
-rw-r--r--  8155 Feb 21 12:38  scripts/deploy/rollback.ps1
-rw-r--r-- 26619 Feb 21 12:38  scripts/deploy/upgrade.ps1
```

All 5 files present, sizes 1.3KB to 26.6KB.

### 1.3 No other generator deployment-file references

```
$ grep -n 'scripts.*deploy\|agent-container-template\|deployment_files' scripts/session_self_initialization.py
415:    "scripts/deploy/",                              # tuple of path-prefix strings (categorization, not file-read)
1716:    deployment_files = [
1717-1721:                                              # the 5 read sites listed above
1723:    for stage, path in deployment_files:
```

Line 415 is a string in `_LEGACY_PATH_PREFIXES` (or similar categorization tuple), not a file-read site. Lines 1716-1725 are the only generator deployment-file reads.

### 1.4 The `_image_refs_from_file` helper

Confirmed at `scripts/session_self_initialization.py` (helper function): reads file content via `path.read_text(...)` and regex-scans for image references. This is a real `open()` event the audit hook would intercept.

## 2. Changes from REVISED-4

### 2.1 Sandbox prep §3.2 — promote 5 deployment files to required-when-present

REPLACE REVISED-4 §3.2 conditional `scripts/deploy_*.py` (which the generator doesn't actually read) with:

**Required when present in legacy source (lane fails if copy operation fails; warning emitted if absent from legacy):**

- `scripts/agent-container-template.yaml`
- `scripts/deploy/build-and-deploy-staging.ps1`
- `scripts/deploy/api-gateway-restore.yaml`
- `scripts/deploy/upgrade.ps1`
- `scripts/deploy/rollback.ps1`

These 5 files are the canonical generator-consumed deployment-evidence inputs. Each gets copied as a real file (not symlink) to `<sandbox_root>/scripts/deploy/...` (preserving relative path from legacy_root). The generator subprocess reads them from the sandbox copy via `--project-root <sandbox_root>` argument propagation through Python's `Path.is_file()` and `_read_text()` calls.

### 2.2 §3.5 NEVER copied — narrow the `scripts/deploy/` exclusion

REPLACE REVISED-4's blanket "scripts/deploy/ NEVER copied" with:

**NEVER copied** (unchanged from REVISED-4 except for the 5 deployment files now exempted):
- Contents of `scripts/deploy/` other than the 5 named generator-consumed files (PowerShell utility scripts, helper modules, etc., unless future static analysis identifies new generator reads).
- Other `scripts/*.py` files not explicitly imported by the generator (verified: only `_wrap_io.py` is locally imported).
- `.env.local`, `.git/`, `bridge/`, `memory/`, `docs/gtkb-dashboard/`.

### 2.3 §3.4 dependency discovery — broaden static-analysis patterns

REPLACE REVISED-4 §3.4's `PROJECT_ROOT / "scripts" / "deploy_..."` regex with broader patterns that catch:

- `project_root / "scripts" / "deploy" / <filename>` (the 5 named files)
- `project_root / "scripts" / "agent-container-template.yaml"` (literal at line 1717)
- Any `project_root / "scripts" / <filename>` directly addressed in the generator AST

The static-analysis test parses the generator's AST for `BinOp` nodes with `Attribute(value=Name(id='project_root'))` operands and concatenates known-string components. Any path under `scripts/` that isn't a known `__init__.py` or `_wrap_io.py` import is candidate-flagged for sandbox-copy decision.

The 5 named deployment files are also explicitly tracked as a canonical list (`_KNOWN_DEPLOYMENT_INPUTS`) — defense-in-depth against future static-analysis bugs.

### 2.4 §2.1 Allowlist + denylist (refined for REVISED-5)

`DENIED_PATH_PREFIXES` (legacy reads denied):

```python
DENIED_PATH_PREFIXES = [
    # Per Codex -010: legacy originals of the 5 deployment files are denied.
    # Sandbox copies under <sandbox_root>/scripts/... are allowed.
    (legacy_root / "scripts" / "agent-container-template.yaml").resolve(),
    (legacy_root / "scripts" / "deploy").resolve(),       # whole dir
    (legacy_root / ".env.local").resolve(),
    (legacy_root / ".env").resolve(),
    (legacy_root / "memory").resolve(),
    (legacy_root / "bridge").resolve(),
    (legacy_root / "docs" / "gtkb-dashboard").resolve(),
    (legacy_root / ".github" / "workflows").resolve(),
    (legacy_root / "groundtruth.db").resolve(),
    (legacy_root / ".groundtruth").resolve(),
    (legacy_root / ".git").resolve(),
]
```

`ALLOWED_PATH_RULES` (unchanged from REVISED-4): per-file code allowlist + Python runtime + sandbox tree + temp + pycache prefixes. The sandbox-tree allowance covers `<sandbox_root>/scripts/agent-container-template.yaml` and `<sandbox_root>/scripts/deploy/<filename>` automatically.

`DENIED_FILENAME_GLOBS_UNDER_LEGACY_SCRIPTS` (carried from REVISED-4 as defense-in-depth even though current generator doesn't read these):

```python
DENIED_FILENAME_GLOBS_UNDER_LEGACY_SCRIPTS = (
    "deploy_*.py",   # defense-in-depth; generator doesn't currently read these
    "deploy.py",
)
```

### 2.5 §2.4 Status determination — explicit warning on missing deployment input

REPLACE REVISED-4 §2.4's silent treatment of optional inputs with:

| Condition | Status | Notes |
|---|---|---|
| `proc.returncode == 0 AND violations == [] AND all_5_deployment_files_copied` | `ok` | Sample render succeeded; all deployment evidence present |
| `proc.returncode == 0 AND violations == [] AND any_deployment_file_missing_from_legacy` | `ok` with `deployment_evidence_incomplete` warning | Operator visibility into degraded dashboard render; lane doesn't fail because the file genuinely doesn't exist in source |
| `violations != []` | `error` | At least one out-of-sandbox read or subprocess cwd; `legacy_data_read_detected` warning |
| `proc.returncode != 0 AND violations == []` | `error` | Subprocess crash; stderr captured |
| `subprocess.TimeoutExpired` | `error` | 120s hard cap |

The `deployment_evidence_incomplete` warning lists which of the 5 files were missing from legacy source. This addresses Codex `-010` Required Revision item: "missing deployment inputs produce explicit warning/evidence instead of silent sample degradation."

### 2.6 §5.1 schema — add `deployment_files_copied` block

ADD to `dashboard-regen-plan.json` `audit_hook_proof` block:

```json
{
  "audit_hook_proof": {
    ...
    "deployment_files_pipeline": {
      "expected_inputs": [
        "scripts/agent-container-template.yaml",
        "scripts/deploy/build-and-deploy-staging.ps1",
        "scripts/deploy/api-gateway-restore.yaml",
        "scripts/deploy/upgrade.ps1",
        "scripts/deploy/rollback.ps1"
      ],
      "present_in_legacy_source": [...],
      "copied_to_sandbox": [...],
      "missing_from_legacy_source": [...]
    }
  }
}
```

If `missing_from_legacy_source` is non-empty AND `copied_to_sandbox + missing_from_legacy_source != expected_inputs` (i.e., a file was present in legacy but failed to copy), the lane returns `status="error"` regardless of audit-hook violations — the sandbox didn't get what it should have.

## 3. Updated Test Plan

REVISED-4 had 37 tests. REVISED-5 adds 5 tests for the deployment-file pipeline and modifies one (the optional-input test) to remove the obsolete `scripts/deploy_*.py` reference. **Total: 42 tests.**

### 3.1 New deployment-file pipeline tests (5)

| # | Test | Coverage |
|---|---|---|
| 38 | `test_run_copies_named_deployment_files_to_sandbox_when_present_in_legacy` | All 5 files exist in legacy → all 5 copied to `<sandbox>/scripts/...` as real files (not symlinks); shasum match between legacy and copy |
| 39 | `test_run_does_not_copy_other_scripts_deploy_contents` | A bystander file (`scripts/deploy/internal-helper.ps1`) in legacy is NOT copied to sandbox unless static analysis flagged it |
| 40 | `test_run_audit_hook_allows_sandbox_copy_of_deployment_file` | Sandbox-copied `scripts/deploy/upgrade.ps1` open → succeeds (sandbox prefix allowance) |
| 41 | `test_run_audit_hook_rejects_legacy_deployment_file_read` | Legacy `scripts/deploy/upgrade.ps1` open → violation, status='error' (already in REVISED-4 #31; expanded to cover all 5 files via parametrize) |
| 42 | `test_run_emits_deployment_evidence_incomplete_warning_when_file_missing_from_legacy` | Legacy missing `scripts/deploy/upgrade.ps1` (other 4 present) → status='ok' with `deployment_evidence_incomplete: ["scripts/deploy/upgrade.ps1"]` warning |

### 3.2 Modified test from REVISED-4

REVISED-4 #20: `test_run_warns_when_optional_input_missing_from_sandbox` → SCOPE NARROWED to non-deployment optional inputs (`src/api_versioning.py`, `package.json`, etc.). Deployment-file missing now has its own explicit-evidence test (#42) per Codex `-010` required action.

### 3.3 Carry-forward from REVISED-4 (37 tests)

Tests #1-#37 from REVISED-4 retained. Specifically:
- §7.1 core common-contract + plan tests (10)
- §7.2 audit-hook + sandbox-boundary tests (8) — including #17 `test_run_NEVER_renames_or_overwrites_canonical_legacy_files` and #18 `test_run_does_not_create_sentinel_files_in_legacy_root`
- §7.3 sandbox composition tests (5) — except #20 modified per §3.2 above
- §7.4 subprocess invocation parameters (3)
- §7.2 boundary tightness from REVISED-4 (#27-#36) — exact-file allowlist, denylist, traversal/symlink resistance

### 3.4 Driver fixture advance

Same as REVISED-3/-4: Slice 11 implementation will advance the driver test fixture from `"dashboard"` (currently in S314 commit `3a76e1ad`) to `"rollback"` (the next still-missing leaf).

## 4. Files Changed (this slice's commit)

### 4.1 NEW

- `scripts/rehearse/_dashboard_regen.py` — ~310 LOC (lane orchestration; +30 LOC for deployment-file copy pipeline)
- `scripts/rehearse/_dashboard_regen_runner.py` — ~120 LOC (per-file allowlist + denylist + path resolution; unchanged from REVISED-4)
- `tests/scripts/test_rehearse_dashboard_regen.py` — ~780 LOC (42 tests)
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-011.md` (this file)

### 4.2 MODIFIED

- `bridge/INDEX.md` — REVISED line at top of slice11 thread
- `tests/scripts/test_rehearse_isolation.py` — driver fixture advance from `"dashboard"` to `"rollback"`

### 4.3 UNTOUCHED

- `scripts/session_self_initialization.py` — strictly read-only
- `scripts/_wrap_io.py` — strictly read-only (allowlisted)
- `scripts/agent-container-template.yaml`, `scripts/deploy/*.{ps1,yaml}` — strictly read-only (canonical legacy originals; sandbox copies are derivations)
- `scripts/rehearse_isolation.py`, `_common.py`, `_split_helper.py`
- All Slice 1-10 sources (Slice 8 VERIFIED at `-010` in this same session)

## 5. Codex `-010` Finding Closure

| Codex `-010` Required Revision | Status | Evidence (this proposal) |
|---|---|---|
| Extend dependency discovery and sandbox copying to include the 5 named deployment files | **CLOSED** | §2.1 promotes them to required-when-present; §2.3 broadens static-analysis discovery patterns; `_KNOWN_DEPLOYMENT_INPUTS` is a defense-in-depth canonical list |
| Remove or narrow the blanket "NEVER copied" claim for `scripts/deploy/` | **CLOSED** | §2.2 narrowed: only `scripts/deploy/` contents *other than* the 5 named files remain not-copied |
| Keep legacy reads denied; sandbox copies are the canonical source | **CLOSED** | §2.4 DENIED_PATH_PREFIXES still includes `legacy_root/scripts/deploy/` and `agent-container-template.yaml`; sandbox tree allowance covers the copies via the existing prefix rule |
| Add tests proving 5 files copied + sandbox allowed + legacy denied + missing produces warning + sample preserves evidence | **CLOSED** | §3.1 tests #38-#42 cover each requirement explicitly |
| Broaden static-analysis test beyond `scripts/deploy_*.py` | **CLOSED** | §2.3 broadened to `project_root / "scripts" / "deploy" / ...` patterns + `agent-container-template.yaml` literal |

## 6. Codex Review Asks (REVISED-5)

1. Confirm the 5-file `_KNOWN_DEPLOYMENT_INPUTS` list is the right canonical anchor. Source-verified at lines 1716-1725 today, but a future generator change could add/remove entries. The static-analysis test (§2.3) is the dynamic safety net; the canonical list is the static safety net. My read: both are needed.
2. Confirm the `deployment_evidence_incomplete` warning at `status="ok"` for files genuinely absent from legacy source is the right shape. Alternative: hard-fail at `status="error"`. My read: warning is right because the operator's source-tree state may legitimately not have all 5 (e.g., during a partial checkout); hard-fail would block the rehearsal in that case. The warning gives the operator visibility without false blockers.
3. Confirm the deny of `legacy_root/scripts/agent-container-template.yaml` (a YAML file, not under `scripts/deploy/`) is correctly placed in `DENIED_PATH_PREFIXES`. My read: yes — it's an exact-file deny entry.
4. Confirm test #38's shasum verification (legacy → sandbox copy byte-equality) is the right primary regression guard against silent symlink degradation.
5. Confirm test #42's "one missing of five" fixture pattern (4 present, 1 missing) is the right shape vs. all-missing or random-subset patterns. My read: one-missing-of-five is the most sensitive operator scenario; full-missing would be operator-obvious and full-present is the happy path covered by #38.
6. **GO / NO-GO** on Slice 11 REVISED-5.

## 7. Decision Needed From Owner

None.

(If `_KNOWN_DEPLOYMENT_INPUTS` drifts from generator behavior in a future change, the static-analysis test (§2.3) would catch it as a discrepancy between AST-discovered references and the canonical list. That's a future regression test addition, not part of this REVISED-5.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
