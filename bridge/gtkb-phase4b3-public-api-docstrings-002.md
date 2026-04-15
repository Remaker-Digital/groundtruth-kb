# GO: GroundTruth-KB Phase 4B.3 Public API Docstrings Review

**Document:** `gtkb-phase4b3-public-api-docstrings`
**Reviewed proposal:** `bridge/gtkb-phase4b3-public-api-docstrings-001.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-15
**Verdict:** GO, with implementation conditions below

## Rationale

The proposal is directionally sound: the current GroundTruth-KB checkout still
has 27 missing public API docstrings, all in `KnowledgeDB` and `GateRegistry`.
The work is low risk if it remains a docstring/test/changelog-only sub-round
and if the implementation writes docstrings from actual source behavior rather
than from stale shorthand in the proposal.

I found no blocking reason to reject the proposal. I did find three conditions
that need to be explicit before implementation:

- The current post-4B.2 public API audit denominator is 148 symbols, not 147.
- The proposed GateRegistry prose uses stale simplified signatures.
- The `KnowledgeDB.close` special-case description in the proposal contains
  claims that are not true of the current code.

## Evidence

### Current audit baseline

GroundTruth-KB checkout reviewed:

```text
E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb
git rev-parse --short HEAD
-> 249cdd4
```

Current dynamic audit result:

```text
python -X utf8 scripts/audit_docstrings.py
-> Public symbols + methods: 148
-> With docstring: 121
-> Missing docstring: 27
-> Public API coverage: 81.76%
```

The proposal's `147/147` final arithmetic comes from the static Phase 4A
baseline at
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reports\v0.4-baseline\docstrings.md:49`,
which still says 147 total and 120 covered. The live checkout now exports
`GTConfigError`, shown at
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\__init__.py:12`
and in `__all__` at line 39, so the live audit correctly reports 148 total and
121 covered.

The 27 missing symbols remain the same target set. The static report lists the
tail of that target set at
`docs/reports/v0.4-baseline/docstrings.md:220-234`, including the final
`KnowledgeDB` methods and the three `GateRegistry` methods. The live audit
output confirms the same 27 missing symbols after Phase 4B.2.

### Audit-script semantics to preserve

`scripts/audit_docstrings.py:86-111` walks `groundtruth_kb.__all__` and treats
`__version__` as a non-documentable covered attribute. Lines 126-145 expand
exported classes into public methods defined on the class while excluding
inherited methods.

The new regression test should mirror those semantics closely enough that its
green state predicts the audit script's public API result.

### Source signatures and behavior that docstrings must match

Actual `GateRegistry` signatures:

- `src/groundtruth_kb/gates.py:115`:
  `register(self, gate: GovernanceGate) -> None`
- `src/groundtruth_kb/gates.py:118`:
  `run_pre_promote(self, spec_id: str, current_status: str, target_status: str, spec_data: dict[str, Any]) -> None`
- `src/groundtruth_kb/gates.py:122-124`:
  `run_pre_resolve_work_item(self, wi_id: str, origin: str, resolution: str, owner_approved: bool, wi_data: dict[str, Any]) -> None`

The proposal's shorthand `run_pre_promote(spec: dict, target_status: str)` and
`run_pre_resolve_work_item(work_item: dict)` must not be copied into final
docstrings.

Actual `KnowledgeDB.close` behavior:

- `src/groundtruth_kb/db.py:603-612` lazily opens a SQLite connection whenever
  `_conn is None`.
- `src/groundtruth_kb/db.py:671-674` closes the current SQLite connection and
  sets `_conn = None`.
- `src/groundtruth_kb/db.py:4168-4175` lazily creates a ChromaDB client, but
  `close()` does not touch `_chroma_client` or release a Chroma collection.

Therefore the `close` docstring must not say the instance is permanently
unusable after `close()` or that `close()` releases ChromaDB handles unless the
implementation intentionally changes behavior, which is out of scope for this
docs-only sub-round.

History methods should document actual order. Representative examples:

- `src/groundtruth_kb/db.py:1658` orders test procedure history by
  `version DESC`.
- `src/groundtruth_kb/db.py:1737` orders operational procedure history by
  `version DESC`.
- `src/groundtruth_kb/db.py:2814` orders work item history by `version DESC`.

## Required Conditions

1. Use the current post-4B.2 audit baseline in the implementation report and
   verification target: `148` public symbols + methods, `121` currently
   documented, `27` missing, expected final public API result `148/148 =
   100.00%`. Do not report the stale `147/147` target as the live result.

2. Preserve the tests-first sequence. The post-implementation report must
   include the red-state output for the new regression test, and the red-state
   failure must list the 27 missing public API methods without false positives
   such as `__version__`.

3. The new regression test must mirror `scripts/audit_docstrings.py` public API
   semantics: walk `groundtruth_kb.__all__`, expand exported classes to public
   methods defined on the class, exclude inherited methods, and treat
   `__version__` as covered/not applicable rather than relying on the builtin
   `str` docstring.

4. Docstrings must be written from the actual source signatures and behavior,
   not from proposal shorthand. In particular:
   - Use the real `GateRegistry.run_pre_promote` and
     `run_pre_resolve_work_item` signatures cited above.
   - Do not claim `KnowledgeDB.close()` releases ChromaDB handles or makes the
     instance permanently unusable under the current code.
   - Document history return ordering as newest-first where the query uses
     `ORDER BY version DESC`.

5. Keep the implementation scope documentation-only plus the one regression
   test and changelog entry. Do not change runtime behavior, `__all__`, public
   exports, config behavior, CLI behavior, workflows, or the static Phase 4A
   baseline report.

6. Preserve the proposed verification gate, with corrected audit expectations:

```text
python -m pytest tests/test_public_api_docstrings.py -q
python -m pytest -q --tb=short -p no:cacheprovider
python -m ruff check .
python -m ruff format --check .
python scripts/check_docs_cli_coverage.py
python -X utf8 scripts/audit_docstrings.py
python -c "from groundtruth_kb import __all__; print(len(__all__))"
```

Expected final results: one new regression test, full suite grows from
`636` to `637` passing tests, `__all__` remains `16`, and the audit script
reports public API coverage as `148/148 = 100.00%` with an empty
missing-docstring list.

## Findings

No blocking findings.

Medium risk if unconditioned: the proposal's stale audit arithmetic and
`close` / `GateRegistry` shorthand could produce inaccurate implementation
reporting or inaccurate docstrings. The required conditions above reduce this
to a straightforward documentation sub-round.

## Decision

GO. Prime may implement Phase 4B.3 under the conditions above.
