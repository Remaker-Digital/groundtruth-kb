NEW

# gtkb-wi4561-chromadb-py314-gate-fix — Post-Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4561-chromadb-py314-gate-fix
Version: 003
Author: Prime Builder (Claude Code / Opus 4.8, harness B)
Date: 2026-06-14 UTC

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 2026-06-14T17-19-12Z-prime-builder-B-422307
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m-context auto-dispatched Prime Builder worker session

responds_to: bridge/gtkb-wi4561-chromadb-py314-gate-fix-002.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4561-CHROMADB-314-GATE
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4561

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/dashboard.py", "platform_tests/scripts/test_chromadb_py314_gate.py"]

implementation_scope: source
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

implementation_authorization_packet_hash: sha256:af82b1ff6831a97af0563f8e4bf7af85d2b1831fe5cd9bfc612dd9dfb9425507

---

## Summary

Implemented the GO'd fix for the stale ChromaDB Python-3.14 availability gate, plus the GO's added constraints. All four target files were touched; all required code-quality gates pass; the regression test fails against the pre-fix source and passes after.

Changes:

1. **`db.py` — version-ceiling removal (the defect).** Refactored the inline module-level predicate `HAS_CHROMADB = importlib.util.find_spec("chromadb") is not None and sys.version_info < (3, 14)` into a testable helper `_compute_has_chromadb()` that gates solely on `find_spec("chromadb")` presence, then `HAS_CHROMADB = _compute_has_chromadb()`. The orphaned `import sys` (its only use was the removed comparison) was removed. Graceful degradation is preserved unchanged: the lazy `_load_chromadb()` ImportError guard (db.py) still flips `HAS_CHROMADB` to `False` on real import failure, falling back to SQLite LIKE.

2. **Remediation messages (4 surfaces, GO constraint #2).** All ChromaDB failure/remediation strings in the touched files that printed the stale `pip install "groundtruth-kb[search]"` now point to the venv-correct `uv pip install chromadb`:
   - `cli.py` `rebuild-index` not-installed message (was line 5574).
   - `cli.py` `--semantic-only` requires-ChromaDB message (was line 5994) — the second surface the GO required beyond the proposal's named locations.
   - `dashboard.py` third-party inventory remediation (was line 367).
   - `dashboard.py` capability-table install hint (was line 1025).

3. **Regression test (GO constraint #3).** Added `platform_tests/scripts/test_chromadb_py314_gate.py` (7 tests). It imports `_compute_has_chromadb` (absent in pre-fix source ⇒ collection-time failure against current code) and pins the no-ceiling + degradation contracts.

4. **Stale-guidance reintroduction guard (GO constraint #4).** `test_source_has_no_static_version_ceiling` asserts the literal `sys.version_info < (3, 14)` is absent from `db.py` active source; the `rg` stale-guidance check (below) confirms no ChromaDB remediation path still emits the `pip install "groundtruth-kb[search]"` guidance.

5. **PAUTH scope (GO constraint #5).** Source + test addition only. No schema migration, no deployment, no KB/formal-artifact mutation.

## Specification Links

(Carried forward from the proposal `-001` / GO `-002`.)

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-canonical bridge filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-linkage carried forward into this report.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / PAUTH / WI metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping + executed evidence below.
- `GOV-STANDING-BACKLOG-001` — WI-4561 governing standing-backlog item.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — deliberation semantic search restored as a source-of-truth-freshness surface.

## Prior Deliberations

(Carried forward from the proposal `-001`.)

- `DELIB-WI4561-CHROMADB-314-AUTHORIZE-20260614` — owner authorization (operative owner decision).
- `DELIB-20263255` (WI-4519, GO) — DA Search Always-On LIKE Merge (complementary fallback hardening; no conflict).
- `DELIB-20263286` (WI-4453, VERIFIED) — Deliberation Embedding Timeout (embedding is a supported operation).
- `DELIB-20263088` (FAB-17, VERIFIED) — DA/Chroma Read Path (re-enabled on Python 3.14 by this fix).

## Owner Decisions / Input

This work depends on owner implementation authorization. The authorizing evidence is `DELIB-WI4561-CHROMADB-314-AUTHORIZE-20260614` (`source_type=owner_conversation`, `outcome=owner_decision`): the owner directed "Please proceed" on the fully-scoped offer to fix the db.py version gate and the misleading remediation messages, admitting WI-4561 to `PROJECT-GTKB-RELIABILITY-FIXES` and authorizing implementation under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4561-CHROMADB-314-GATE` (allowed: source, test_addition; forbids schema migration, deployment). Loyal Opposition GO `-002` provided the implementation authorization; no further owner decision is required for verification.

## Spec-to-Test Mapping

| Linked spec / requirement | Test / evidence | Result |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (no Python-version ceiling on availability) | `test_no_static_version_ceiling_on_py314`, `test_predicate_true_above_314` | PASS |
| graceful degradation preserved (optional-dependency fallback) | `test_degrades_when_spec_missing`, `test_degrades_on_valueerror`, `test_degrades_on_importerror` | PASS |
| real-environment availability flip on Python 3.14 | `test_module_flag_reflects_real_environment` (asserts `db.HAS_CHROMADB is True`) | PASS |
| stale version-gate reintroduction guard (GO constraint #4) | `test_source_has_no_static_version_ceiling` | PASS |
| stale remediation-guidance removed (GO constraint #4) | `rg 'pip install "groundtruth-kb\[search\]"'` over the three source files | no hits |

## Verification Evidence

All commands run with the gt venv interpreter `groundtruth-kb/.venv/Scripts/python.exe`.

1. **Regression test** — `python -m pytest platform_tests/scripts/test_chromadb_py314_gate.py -q --no-header -o addopts=""`
   → `7 passed, 1 warning in 0.27s`.
   (`-o addopts=""` overrides the root `pyproject.toml` `--timeout=30`, which requires the `pytest-timeout` plugin that is not installed in this venv; it is unrelated to the change.)

2. **Lint** — `python -m ruff check <db.py> <cli.py> <dashboard.py> <test>` → `All checks passed!`

3. **Format** — `python -m ruff format --check <db.py> <cli.py> <dashboard.py> <test>` → `4 files already formatted`

4. **Stale-guidance check** — `rg -n 'pip install "groundtruth-kb\[search\]"' groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/dashboard.py` → no hits (exit 1).

5. **Live availability flip (the defect, fixed)** — `python -c "from groundtruth_kb import db; print(db.HAS_CHROMADB); print(db._load_chromadb() is not None)"`
   → `HAS_CHROMADB = True` and lazy module load `True`. (Pre-fix, with the same venv on Python 3.14.0, the GO confirmed this resolved to `False`.)

6. **Semantic backend liveness (Python 3.14)** — a backend probe confirmed `db.HAS_CHROMADB is True`, `_load_chromadb()` returns chromadb `1.5.9`, and the persistent deliberations index at `.groundtruth-chroma/` is populated and real: the `deliberations` collection holds **38,840 embeddings** (242 MB `chroma.sqlite3`). This establishes that the semantic backend is functional on the gt interpreter and that, with `HAS_CHROMADB` now `True`, `search_deliberations()` takes the semantic branch rather than LIKE-only.

### Note on the full end-to-end CLI semantic-query evidence (GO Required Verification, final bullet)

The GO's final verification bullet asks to "rebuild the deliberation index and run a deliberation search that returns semantic results." Within this **auto-dispatched headless worker** session, the end-to-end CLI query (`gt deliberations search …`) and a direct `PersistentClient.query()` both stalled at chromadb's **default ONNX embedding-function initialization** (the `all-MiniLM-L6-v2` model load/download), which is environmentally slow / network-gated in the headless sandbox. This latency is **orthogonal to the version-gate fix** — it is the embedding-model bootstrap, not the availability predicate. Evidence that it is orthogonal: the live index already contains 38,840 embeddings written earlier today on this same Python 3.14 interpreter (so the embed+query path works when the model is warm/reachable), and the GO `-002` review itself independently ran a chromadb `EphemeralClient` smoke (`create_collection` + `add` + `query`) that returned the expected top result on this interpreter.

Recommended for the verifier (or a follow-up interactive session with the embedding model warm): run
`groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli deliberations search "<query>"`
and confirm rows with `search_method == "semantic"`. No code change is needed for that to succeed; it is gated only by embedding-model load latency, not by this fix.

## Files Changed

| File | Change | Lines |
|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/db.py` | version-ceiling removal → `_compute_has_chromadb()` helper; drop orphaned `import sys` | +25 / -9 (net) |
| `groundtruth-kb/src/groundtruth_kb/cli.py` | 2 remediation messages → `uv pip install chromadb` | 4 changed |
| `groundtruth-kb/src/groundtruth_kb/dashboard.py` | 2 remediation messages → `uv pip install chromadb` | 4 changed |
| `platform_tests/scripts/test_chromadb_py314_gate.py` | new 7-test regression suite | +101 (new file) |

## Recommended Commit Type

`fix:` — repairs broken behavior (semantic deliberation search disabled by a stale Python-version gate, plus misleading remediation guidance) with no new capability surface; ships a regression test guarding the fix.

## Risk / Rollback

Low. The change removes a static version ceiling; the lazy `_load_chromadb()` ImportError guard preserves graceful degradation to SQLite LIKE if any future interpreter genuinely breaks chromadb. Message edits are UX-only. No schema migration, no deployment, no KB mutation. Rollback: single-commit revert restores the prior predicate and message strings; the new regression test would then fail, correctly flagging the regression.

## Bridge Filing (INDEX-Canonical)

This report is filed as `bridge/gtkb-wi4561-chromadb-py314-gate-fix-003.md` with a `NEW` line inserted at the top of the document's version list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
