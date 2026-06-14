NEW

# gtkb-wi4561-chromadb-py314-gate-fix — Restore ChromaDB semantic deliberation search on Python 3.14

bridge_kind: implementation_proposal
Document: gtkb-wi4561-chromadb-py314-gate-fix
Version: 001
Author: Prime Builder (Claude Code / Opus 4.8, harness B)
Date: 2026-06-14 UTC

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 2026-06-14-PB-B-interactive
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m-context interactive Prime Builder session

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4561-CHROMADB-314-GATE
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4561

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/dashboard.py", "platform_tests/scripts/test_chromadb_py314_gate.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

GT-KB's ChromaDB-backed semantic deliberation search has been silently non-functional. Diagnosis on 2026-06-14 found the root cause is **not** a missing package but a stale version gate in the platform's own source: `groundtruth-kb/src/groundtruth_kb/db.py:50` computes `HAS_CHROMADB = importlib.util.find_spec("chromadb") is not None and sys.version_info < (3, 14)`. The `gt` venv runs Python 3.14.0, so the `< (3, 14)` clause forces `HAS_CHROMADB = False` even when chromadb is installed and fully functional. The gate was introduced in an undocumented sweep commit (`d04880bcf`, 2026-06-11) with no recorded rationale.

The gate is empirically stale: chromadb 1.5.9 was installed into the venv this session and verified to import **and** functionally embed + query on Python 3.14 (EphemeralClient `create_collection` + `add` + `query` returned ranked results; the native Rust bindings and onnxruntime embedding path both executed). The lazy `_load_chromadb()` loader (db.py:57–73) already flips `HAS_CHROMADB` to `False` on any real `ImportError`, so removing the static version ceiling preserves graceful degradation: if a future interpreter genuinely breaks chromadb, search still falls back to SQLite LIKE rather than crashing.

This proposal: (1) removes the `and sys.version_info < (3, 14)` clause at db.py:50 so `HAS_CHROMADB` reflects actual chromadb presence; and (2) corrects the misleading remediation messages at `cli.py:5574` and `dashboard.py:367,1025` that print `pip install "groundtruth-kb[search]"` — wrong on two counts in this environment: chromadb is already installed, and the uv-managed venv has no pip (`No module named pip`). The corrected guidance points to `uv pip install` / the gt venv. Impact: restores the governance-mandated pre-proposal deliberation search (per `.claude/rules/deliberation-protocol.md`), which has been degraded to substring-only LIKE matching.

The package install (chromadb 1.5.9) is already complete and owner-approved; this proposal is the source change that actually re-enables the capability.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-canonical bridge filing; this proposal is filed and tracked per the bridge protocol.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section satisfies the mandatory spec-linkage gate for the proposed source change.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — proposal carries Project Authorization / Project / Work Item metadata (WI-4561 under the reliability-fixes PAUTH).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Spec-Derived Verification Plan maps the fix to an executed regression test + manual semantic-search evidence before VERIFIED.
- `GOV-STANDING-BACKLOG-001` — WI-4561 is the governing standing-backlog work item for this defect.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — deliberation semantic search is a source-of-truth-freshness surface; a disabled search backend silently degrades fresh-state retrieval. This fix restores it.

## Prior Deliberations

- `DELIB-WI4561-CHROMADB-314-AUTHORIZE-20260614` — owner authorization (this session) directing the fix via the reliability fast-lane; the operative owner-decision for this proposal.
- `DELIB-20263255` (WI-4519, **GO**) — "DA Search Always-On LIKE Merge": made the SQLite LIKE path always-on. This proposal is complementary: WI-4519 hardened the *fallback*; this restores the *primary* (semantic) path that the LIKE fallback was compensating for. No conflict.
- `DELIB-20263286` (WI-4453, **VERIFIED**) — "Deliberation Embedding Timeout": prior work on the chroma embedding path, confirming embedding is an expected, supported operation (not to be disabled wholesale).
- `DELIB-20263088` (FAB-17, **VERIFIED**) — "DA/Chroma Read Path": prior verification of the chroma read path. This proposal re-enables that path on Python 3.14.
- No prior deliberation proposed or ratified the `sys.version_info < (3, 14)` gate; it entered via an undocumented sweep commit, so this proposal does not revisit a previously-ratified decision.

## Owner Decisions / Input

This proposal depends on owner approval (implementation authorization for a source change). The authorizing evidence is `DELIB-WI4561-CHROMADB-314-AUTHORIZE-20260614` (`source_type=owner_conversation`, `outcome=owner_decision`): in response to a fully-scoped offer to fix the db.py:50 gate and the misleading messages to restore deliberation semantic search, the owner directed "Please proceed" (2026-06-14). That decision admitted WI-4561 to `PROJECT-GTKB-RELIABILITY-FIXES` and authorized implementation under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4561-CHROMADB-314-GATE` (allowed mutations: source, test_addition; forbids schema migration, deployment). No further owner decision is required for implementation; Loyal Opposition GO remains required before any source edit.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements are `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (search-backed source-of-truth freshness) and the mandatory deliberation-search protocol in `.claude/rules/deliberation-protocol.md`. This is a defect fix restoring a previously-specified, regression-broken capability (semantic deliberation search); it adds no new behavior surface and therefore requires no new or revised requirement.

## Spec-Derived Verification Plan

| Linked spec / requirement | Test or command | Expected result |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | New regression test `platform_tests/scripts/test_chromadb_py314_gate.py`: with chromadb present (`find_spec` truthy), the availability guard must NOT be force-disabled on Python ≥ 3.14. Implementation refactors the guard into a testable predicate (e.g. `_compute_has_chromadb()`) and asserts it is True for a stubbed Python 3.14 + present chromadb, and degrades only on genuine `ImportError`. | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Manual: `gt deliberations rebuild-index` then `gt deliberations search "omnigent meta-harness alignment"` | rebuild-index succeeds (no "ChromaDB is not installed"); semantic search returns `DELIB-OMNIGENT-ADVISORY-20260614` + `DELIB-20263229` via semantic (not just `text_match`) ranking |
| code quality | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check <changed.py>` and `ruff format --check <changed.py>` | clean (both gates) |

Verification command:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_chromadb_py314_gate.py -q --no-header
```

## Risk / Rollback

Low risk. The change removes a static version ceiling; the lazy `_load_chromadb()` ImportError guard (db.py:57–73) preserves graceful degradation to SQLite LIKE if any future interpreter actually breaks chromadb. The message edits are UX-only. No schema migration, no deployment, no KB mutation. Rollback: a single-commit revert restores db.py:50 and the prior message strings. The new regression test would then fail, correctly flagging the regression.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of
the `gtkb-wi4561-chromadb-py314-gate-fix` document list in `bridge/INDEX.md`; no prior version is deleted or
rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state
per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`fix:` — repairs broken behavior (semantic deliberation search disabled by a stale version gate) with no new capability surface; includes a regression test guarding the fix.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
