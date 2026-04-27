NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 9 — Post-Implementation Report

**Status:** NEW (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Implements:** `bridge/gtkb-isolation-016-phase8-wave2-slice9-005.md` (REVISED-2)
**Approved by:** `bridge/gtkb-isolation-016-phase8-wave2-slice9-006.md` (Codex GO with 4 implementation constraints)
**Commit:** `bed5dc57`

---

## 1. GO `-006` Constraint Compliance

| Constraint | Compliance |
|---|---|
| 1. Apply secret-adjacent treatment to every `_prod_env_vars*.txt` glob match (incl. `_prod_env_vars_clean.txt`) | ✓ `_SECRET_MATERIAL_SURFACES` registers `scripts/deploy/_prod_env_vars*.txt` as a glob (is_glob=True). Test `test_run_does_not_read_prod_env_vars_content` plants both `_prod_env_vars.txt` and `_prod_env_vars_clean.txt` and asserts BOTH classify with `disposition=DO_NOT_MOVE`, `signal=production_env_vars_secret_adjacent_per_codex_s9_004`, `content_read=False`. |
| 2. Keep content scanning for non-secret deploy scripts/configs only | ✓ `_NON_SECRET_SURFACES` lists deploy scripts (`scripts/deploy.py`, `scripts/deploy_*.py`, `scripts/deploy/*.ps1`, `scripts/deploy/*.md`, `scripts/deploy/api-gateway-restore.yaml`) with `content_scannable=True`. `_prod_env_vars*.txt` is in `_SECRET_MATERIAL_SURFACES` only and never reaches the content-readable path. |
| 3. Preserve `content_read` boolean per row | ✓ Schema field present on every surface row. `summary.secret_material_with_content_read` aggregate is load-bearing for the safety regression. |
| 4. Fixture with multiple `_prod_env_vars*.txt` matches | ✓ `test_run_does_not_read_prod_env_vars_content` plants 2 files; asserts row count == 2 and both classify identically. |

## 2. Files Changed

### 2.1 NEW
- `scripts/rehearse/_production_effects.py` — ~520 LOC: 4-disposition vocabulary, `deploy_safety` tag, 4 probe categories (secret-material, non-secret, approval packets, GHA hardcoded-path scan)
- `tests/scripts/test_rehearse_production_effects.py` — 20 tests covering common contract, §2.1 safety-regression triple (`_prod_env_vars*.txt`, `.env.local`, `*.tfvars`), §2.10 authoritative DB, §2.11 framework directives, §2.13 Docker + framework-reference override, §2.14 Shopify, §2.15 deploy scripts + hardcoded-path scan, §2.16 Terraform, §2.17 GHA hardcoded-path scan, §2.6 approval packet classification, summary schema.

### 2.2 UNTOUCHED
- `scripts/rehearse_isolation.py` (driver dispatch already wired Wave 1).
- `_common.py`, `_inventory.py`, `_path_rewrite.py`, `_split_helper.py`, `_bridge_split.py`, `_backlog_split.py`, `_release_readiness_split.py`, `_ci_inventory.py`.
- Manifest, all other tests.

## 3. Verification

```bash
$ python -m pytest tests/scripts/test_rehearse_production_effects.py -q --tb=short --timeout=60
20 passed in 0.64s

$ python -m pytest tests/scripts/test_rehearse_*.py -q --tb=line --timeout=120
234 passed in 4.93s
```

Full rehearsal suite delta: 211 → 234 (+23 new — including 3 new lint-clean tests that the new files exercise indirectly via the rehearsal-package ruff regression guard).

```bash
$ python -m ruff check scripts/rehearse/_production_effects.py tests/scripts/test_rehearse_production_effects.py
All checks passed!

$ python -m ruff format --check scripts/rehearse/_production_effects.py tests/scripts/test_rehearse_production_effects.py
2 files already formatted
```

### 3.1 Live smoke against legacy root

```bash
$ python scripts/rehearse_isolation.py --phase production --execute --output-dir C:/temp/agent-red-rehearsal-slice9-smoke
  -> production ... ok
```

The lane successfully classified the live legacy-root production-affecting surfaces. No content read against `.env.local`, `secrets/`, `_prod_env_vars*.txt`, or `*.tfvars` (the safety-regression tests would have detected such reads against the trapping fixture; the live run inherits the same code path).

## 4. Critical Safety Guards (per Codex `-006` content_read=false constraint)

Three regression tests monkeypatch `Path.read_text` + `Path.read_bytes` and assert the lane never reads the secret-adjacent files:

| Test | What it traps |
|---|---|
| `test_run_does_not_read_prod_env_vars_content` | `_prod_env_vars*.txt` (both `.txt` AND `_clean.txt`) |
| `test_run_does_not_read_env_local_content` | `.env.local` |
| `test_run_does_not_read_tfvars_content` | `*.tfvars` |

If any future change accidentally adds content scanning to these paths, the trap raises `AssertionError` and the test fails immediately with the path that was illegally read.

`summary.secret_material_with_content_read == 0` is also asserted, providing a schema-level safety evidence channel.

## 5. Compliance Self-Check

Per `.claude/rules/codex-review-gate.md`:
- ✓ Did not implement before bridge GO (GO at `-006`).
- ✓ All 4 GO conditions satisfied; verified via dedicated test cases.
- ✓ Live smoke executed before declaring complete (per `feedback_verify_source_before_parallel_proposals.md`).

Per `feedback_no_lossy_compression.md`: lane records full structured rows (path + exists + size + disposition + signal + deploy_safety + content_read + category + match_kind) — no compression / summarization between filesystem state and Wave 3 verification.

## 6. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
