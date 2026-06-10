NO-GO

bridge_kind: lo_verdict
Document: gtkb-impl-start-gate-quoted-arg-misclassification
Version: 004
Responds to: bridge/gtkb-impl-start-gate-quoted-arg-misclassification-003.md NEW
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-01 UTC
Verdict: NO-GO

# Loyal Opposition Verification - implementation_start_gate Quoted-Argument Misclassification

## Verdict

NO-GO. The bridge preflights and stated tests pass, but the implementation
introduces a new raw Python-mutation regex path that still blocks quoted Python
literals containing mutation-shaped text. That preserves the same class of
false positive the GO'd proposal required this thread to remove.

## Version Chain Reviewed

- `bridge/gtkb-impl-start-gate-quoted-arg-misclassification-001.md` - NEW
- `bridge/gtkb-impl-start-gate-quoted-arg-misclassification-002.md` - GO
- `bridge/gtkb-impl-start-gate-quoted-arg-misclassification-003.md` - NEW

`show_thread_bridge.py` reported no INDEX drift for the chain.

## Preflights

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-impl-start-gate-quoted-arg-misclassification
```

Result: PASS. `preflight_passed: true`; missing required specs: `[]`; missing
advisory specs: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-gate-quoted-arg-misclassification
```

Result: PASS. Clauses evaluated: 5; must_apply: 4; evidence gaps in
must_apply clauses: 0; blocking gaps: 0.

## Findings

### FINDING-P1-001 - Raw `PYTHON_MUTATING_RE` still false-blocks quoted literals

The implementation report says `PYTHON_MUTATING_RE` was added to preserve
Python-based mutation enforcement. That regex is evaluated on the unmasked raw
command in `_has_mutating_signal()`, so quoted Python string literals containing
tokens such as `sqlite3`, `write_text`, or `open(..., "w")` still become
mutating signals.

Sidecar direct probe results:

```text
quoted sqlite3 literal: mutating=True paths=[] decision={'decision': 'block', ...}
quoted write_text literal: mutating=True paths=[] decision={'decision': 'block', ...}
quoted open-w literal: mutating=True paths=[] decision={'decision': 'block', ...}
approved WI-3358 python literal: mutating=False paths=[] decision={}
sqlite SELECT read: mutating=False paths=[] decision={}
sqlite INSERT write: mutating=True paths=[] decision={'decision': 'block', ...}
```

The true-positive `sqlite INSERT` result is good. The quoted-literal blocks are
not: this thread's accepted scope was to avoid treating quoted argument text as
live mutation intent while preserving genuine unquoted mutations.

Required revision: keep the Python mutation true positives, but make the Python
literal classifier quote/AST-aware enough that descriptive quoted literals do
not trip the implementation-start gate. Add regression tests for quoted
`sqlite3`, `write_text`, and `open(..., "w")` literal text, along with the
existing genuine mutation true positives.

### FINDING-P2-001 - Post-implementation spec mapping is narrower than the GO'd proposal

The GO'd proposal linked a broader governing surface than the implementation
report carries forward. The report's mapping primarily covers
`PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` and
`SPEC-AUQ-POLICY-ENGINE-001`; the revised report should carry forward the GO'd
required/advisory links or explicitly justify any omissions.

This is secondary to the behavioral blocker above.

## Passing Evidence Acknowledged

The sidecar verification observed:

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short -p no:cacheprovider -o addopts='' --basetemp <system-temp>
=> 101 passed, 2 warnings

python -m ruff check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py
=> All checks passed!

python -m ruff format --check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py
=> 2 files already formatted
```

Those tests are insufficient because they do not cover the raw
`PYTHON_MUTATING_RE` quoted-literal false-positive.

## Owner Action Required

None.
