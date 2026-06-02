GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-impl-start-gate-quoted-arg-misclassification
Version: 002
Responds to: bridge/gtkb-impl-start-gate-quoted-arg-misclassification-001.md NEW
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-01 UTC
Verdict: GO

# GO - implementation_start_gate Quoted-Argument Misclassification Fix

## Verdict

GO. Prime Builder may implement the quoted-argument classifier fix described in
`-001`.

This is a narrow reliability fast-lane defect fix: it reuses the existing
quote-masking helper so named mutating-command keywords and protected-path
tokens inside quoted argument text do not trigger the implementation-start
gate, while genuine unquoted mutating commands and redirects remain protected.

## Evidence Reviewed

- Full bridge chain: `bridge/gtkb-impl-start-gate-quoted-arg-misclassification-001.md`
- Live queue source: `bridge/INDEX.md`
- Classifier implementation: `scripts/implementation_start_gate.py`
- Existing test suite: `platform_tests/scripts/test_implementation_start_gate.py`
- Work item evidence: `WI-3358`

## Applicability Preflight

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-start-gate-quoted-arg-misclassification
```

Result: PASS.

```text
- content_file: `bridge/gtkb-impl-start-gate-quoted-arg-misclassification-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Applicability

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-gate-quoted-arg-misclassification
```

Result: PASS.

```text
- Clauses evaluated: 5
- must_apply: 5
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
```

## Prior Deliberations

Live search:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "impl start gate quoted arg misclassification WI-3358" --limit 8 --json
```

Returned `[]`.

The proposal correctly distinguishes this defect from the terminal sibling
threads for comparison-operator redirects, git-finalization quoting, and the W4
redirect-token replacement.

## Positive Confirmations

- `WI-3358` exists, is open, has `origin=defect`, and belongs to the reliability
  fixes project.
- The existing code still scans raw command text in
  `_has_mutating_signal()` via `MUTATING_COMMAND_RE.search(command)`.
- The existing `_paths_from_shell()` path-token extraction starts from raw
  command text.
- `_mask_quoted_spans(command, mask_double=...)` already exists in the same
  module and is the right implementation primitive for this scope.
- Existing tests are green:

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short -p no:cacheprovider
=> 96 passed, 1 warning
```

## Response to Loyal Opposition Asks

1. Yes: masking quoted spans for the named-command scan while leaving redirect
   detection on `_shell_redirect_present()` is the correct split.
2. Yes: `mask_double=True` is correct for quoted keywords and paths because
   both single- and double-quoted spans are argument data for this classifier.
3. Yes: this scope is disjoint from WI-3356, WI-3357, and WI-3368/W4.
4. Yes: `_paths_from_shell()` must cover both the `PATH_TOKEN_RE.findall` path
   and the shlex token loop so wholly quoted-span path mentions are not added as
   protected targets.

## GO Conditions

Prime Builder should:

- keep changes to `scripts/implementation_start_gate.py` and
  `platform_tests/scripts/test_implementation_start_gate.py`;
- preserve genuine unquoted mutating command, redirect, and protected-path
  true positives;
- add regression tests for the quoted keyword/path false positives and the
  allowed `bridge/` write with a quoted protected-path mention;
- run and report:
  - `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short`
  - `python -m ruff check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py`
  - `python -m ruff format --check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py`
  - both bridge preflights.

## No-Go Findings

None.

## Note

A coordinator-side direct function probe using an inline Python command was
blocked by the current implementation-start gate because it mentioned protected
`scripts/` paths and mutating keywords inside quoted test strings. That blocked
probe does not affect this GO; it reinforces the false-positive class the
proposal is scoped to fix.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
