GO

# gtkb-wi4561-chromadb-py314-gate-fix - Loyal Opposition GO

bridge_kind: review_verdict
Document: gtkb-wi4561-chromadb-py314-gate-fix
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-14 UTC

author_identity: loyal-opposition/codex
author_harness_id: A
responds_to: bridge/gtkb-wi4561-chromadb-py314-gate-fix-001.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4561-CHROMADB-314-GATE
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4561

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/dashboard.py", "platform_tests/scripts/test_chromadb_py314_gate.py"]

---

## Verdict

GO, with the implementation constraints below.

The proposal is sufficiently scoped and authorized. The core technical claim is
live in the current checkout: the GT-KB venv runs Python 3.14.0, `chromadb`
1.5.9 is importable, and an in-process smoke test can create, add to, and query
an ephemeral ChromaDB collection. Despite that, `groundtruth_kb.db.HAS_CHROMADB`
currently resolves to `False` because `db.py` still gates availability with
`sys.version_info < (3, 14)`.

## Mandatory Preflight Results

- Applicability preflight: PASS. Packet hash
  `sha256:d70343c0baf055b1ebb2bdb2977a4582bd62d10cd2974c37e1b0bb68b2fe5b2a`.
  No missing required specs. Advisory-only omissions were artifact-oriented
  governance references.
- ADR/DCL clause preflight: PASS. Five clauses evaluated; three must-apply;
  zero must-apply evidence gaps.
- Citation freshness preflight: PASS. No stale cross-thread citations detected.

## Owner Authorization And Backlog Check

- `DELIB-WI4561-CHROMADB-314-AUTHORIZE-20260614` exists and records owner
  authorization to fix the stale Python-3.14 ChromaDB gate and misleading
  remediation messages.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4561-CHROMADB-314-GATE` is active,
  includes `WI-4561`, and allows `source` plus `test_addition`; it forbids
  schema migration and deployment.
- Live `current_work_items` shows `WI-4561` as open/backlogged, P1,
  component `deliberation-search`.
- Related work check: `WI-4519` and `WI-4453` are already resolved and are
  complementary, not duplicative. `WI-4519` protects the LIKE fallback, and
  `WI-4453` bounds ChromaDB embedding/index operations. This proposal restores
  the primary semantic availability gate and does not interfere with either
  resolved change.

## Evidence Reviewed

- `groundtruth-kb/src/groundtruth_kb/db.py:50` currently computes
  `HAS_CHROMADB = importlib.util.find_spec("chromadb") is not None and
  sys.version_info < (3, 14)`.
- `groundtruth-kb/.venv/Scripts/python.exe` reports Python 3.14.0 and can
  import `chromadb` 1.5.9.
- With the current code loaded from `groundtruth-kb/src`,
  `groundtruth_kb.db.HAS_CHROMADB` is `False` and `_load_chromadb()` returns
  `None`, confirming the source gate disables an available backend.
- A ChromaDB `EphemeralClient` smoke test created a collection, added two
  documents, and returned the expected top result for a query.

## Required Implementation Constraints

1. Remove the stale static Python-version ceiling from the ChromaDB
   availability predicate while preserving lazy import and graceful degradation
   on real import failure.
2. Include the second stale CLI remediation message found during review:
   `groundtruth-kb/src/groundtruth_kb/cli.py:5994` still prints
   `pip install "groundtruth-kb[search]"` for `--semantic-only`. The proposal
   names `cli.py:5574` and the dashboard locations, but implementation must
   update all ChromaDB failure/remediation surfaces in the touched files.
3. Add the proposed regression test for the Python-3.14 availability guard.
   It should fail against the current code and pass after the fix.
4. Add either a targeted assertion or an `rg` verification step proving that
   no ChromaDB-specific failure/remediation path in `db.py`, `cli.py`, or
   `dashboard.py` still directs the operator to the stale
   `pip install "groundtruth-kb[search]"` guidance.
5. Keep the work inside the active PAUTH: source plus test addition only; no
   schema migration, deployment, or formal artifact mutation.

## Required Verification

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_chromadb_py314_gate.py -q --no-header`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/dashboard.py platform_tests/scripts/test_chromadb_py314_gate.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/dashboard.py platform_tests/scripts/test_chromadb_py314_gate.py`
- A targeted stale-guidance check equivalent to:
  `rg -n 'pip install "groundtruth-kb\\[search\\]"' groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/dashboard.py`
  returning no ChromaDB remediation hits.
- Manual semantic-path evidence after the fix, as proposed:
  rebuild the deliberation index and run a deliberation search that returns
  semantic results, not only LIKE fallback rows.

## Owner Action Required

None.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
