NO-GO

# gtkb-wi4561-chromadb-py314-gate-fix - Loyal Opposition Verification

bridge_kind: verification_verdict
Document: gtkb-wi4561-chromadb-py314-gate-fix
Version: 004
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-14 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4561-chromadb-py314-gate-fix-003.md
Recommended commit type: fix:
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: keep-working-lo-2026-06-14T1804Z-codex-A
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; durable Loyal Opposition role; workspace E:\GT-KB

## Verdict

NO-GO.

The source/test portion of the implementation is directionally correct: the
Python-version ceiling is removed, ChromaDB availability flips to true in the
current gt venv, the focused regression test passes, ruff passes, and stale
`pip install "groundtruth-kb[search]"` guidance is gone from the touched source
files.

However, the implementation report does not satisfy the GO's required
end-to-end semantic-search verification. Replaying the semantic-only search in
this checkout returned no semantic rows and logged ChromaDB query failures. A
`VERIFIED` verdict would therefore overstate the restored source-of-truth
freshness behavior.

## Same-Harness Guard

The implementation report was authored by Prime Builder Claude harness B
(`author_harness_id: B`). This verdict is authored by Codex harness A. The
bridge separation rule is satisfied.

## Applicability Preflight

`python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4561-chromadb-py314-gate-fix`

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs:
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
packet_hash: sha256:80eaa3a4fdba583ecb2d4ec75476e578b9783be339c6e250a7e355f20aa5abaa
```

The omissions are advisory-only and do not block this verdict.

## Clause Applicability

`python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4561-chromadb-py314-gate-fix`

```text
Clauses evaluated: 5
must_apply: 3
may_apply: 2
not_applicable: 0
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
```

## Citation Freshness

`python scripts\bridge_citation_freshness_preflight.py --bridge-id gtkb-wi4561-chromadb-py314-gate-fix`

```text
No stale cross-thread citations detected.
```

## Positive Confirmations

- `groundtruth-kb/src/groundtruth_kb/db.py` now computes ChromaDB availability
  through `_compute_has_chromadb()` and no longer contains
  `sys.version_info < (3, 14)`.
- `groundtruth-kb/src/groundtruth_kb/cli.py` and
  `groundtruth-kb/src/groundtruth_kb/dashboard.py` no longer contain the stale
  `pip install "groundtruth-kb[search]"` guidance in the checked remediation
  paths.
- `groundtruth-kb/.venv/Scripts/python.exe -c "from groundtruth_kb import db;
  print(db.HAS_CHROMADB); print(db._load_chromadb() is not None)"` returned
  `True` and `True`; `chromadb` reports version `1.5.9`.
- Focused test: `groundtruth-kb\.venv\Scripts\python.exe -m pytest
  platform_tests\scripts\test_chromadb_py314_gate.py -q --no-header -o
  addopts=""` returned `7 passed, 1 warning in 0.84s`.
- Ruff check returned `All checks passed!`.
- Ruff format check returned `4 files already formatted`.
- Stale-guidance check
  `rg -n 'pip install "groundtruth-kb\[search\]"'
  groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\src\groundtruth_kb\cli.py
  groundtruth-kb\src\groundtruth_kb\dashboard.py` returned no hits.

## Blocking Finding

### F1 - Required semantic-search verification still fails

Severity: P1 / blocking.

The GO verdict required manual semantic-path evidence after the fix: rebuild or
otherwise exercise the Deliberation Archive semantic path and run a deliberation
search that returns semantic results, not only LIKE fallback rows. The
implementation report explicitly did not complete that final bullet, citing
environmental ChromaDB/ONNX initialization latency.

I attempted the semantic-only query directly:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli deliberations search "omnigent meta-harness alignment" --limit 5 --semantic-only --json
```

Observed output:

```text
[]
2026-06-14T11:03:50 groundtruth_kb.db WARNING ChromaDB search failed (attempt 1/2), falling back to SQLite LIKE: Error executing plan: Error sending backfill request to compactor: Failed to apply logs to the hnsw segment writer
2026-06-14T11:03:51 groundtruth_kb.db WARNING ChromaDB search failed (attempt 2/2), falling back to SQLite LIKE: Error executing plan: Internal error: Error querying knn
```

That is not semantic-search success. It shows that `HAS_CHROMADB` is now true,
but the actual semantic query path still degrades before producing semantic
rows. Because `--semantic-only` filters fallback rows after `search_deliberations`
returns, the command exits with an empty JSON list instead of proving semantic
results. This leaves `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` and the GO's final
verification bullet unsatisfied.

## Required Revisions

1. File the next bridge version as `REVISED`.
2. Preserve the passing source predicate, remediation-string, pytest, ruff, and
   stale-guidance evidence unless source changes are needed.
3. Add successful end-to-end semantic-search evidence, for example a bounded
   `gt deliberations search ... --semantic-only --json` run that returns one or
   more rows with `search_method == "semantic"`.
4. If the persistent Chroma index is unhealthy, either repair/rebuild it and
   report the successful semantic query, or revise the implementation so
   `--semantic-only` fails closed with a clear non-zero error when ChromaDB
   query execution falls back instead of silently returning an empty semantic
   set.
5. Re-run the focused pytest, ruff check, ruff format check, stale-guidance
   check, and the semantic-path command before resubmission.

## Owner Action Required

None. Prime Builder can revise the implementation report and, if needed, the
CLI semantic-only failure behavior under the existing PAUTH. Owner input is
only required if Prime chooses to expand scope beyond the approved source/test
repair.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
