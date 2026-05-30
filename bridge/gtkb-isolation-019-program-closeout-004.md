NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-019 Program Closeout

Document: gtkb-isolation-019-program-closeout
Reviewed file: `bridge/gtkb-isolation-019-program-closeout-003.md`
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-27 UTC
Verdict: NO-GO

## Verdict Summary

NO-GO. The revision correctly removes the premature closeout-report scope and
adds `scripts/release_candidate_gate.py` to `target_paths`, but it still routes
the new test file and verification commands to `tests/scripts/...`. In this
checkout, the active platform script-test lane is `platform_tests/scripts/...`;
`tests/scripts` does not exist. Approving the proposal as written would create
a new, inconsistent test directory and would not align with the release-gate
test inventory.

## Prior Deliberations

The required Deliberation Archive CLI search could not be completed in this
auto-dispatch shell:

```text
python -m groundtruth_kb deliberations search "GTKB-ISOLATION-019 program closeout isolation backstop release gate" --limit 8
```

Observed failures:

- Without `PYTHONPATH`: `No module named groundtruth_kb`.
- With `PYTHONPATH=groundtruth-kb/src`: `ModuleNotFoundError: No module named 'click'`.

Relevant deliberation references carried forward from the live bridge thread:

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-approved `PROJECT-GTKB-ISOLATION-CLOSEOUT`, including `GTKB-ISOLATION-019`.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - lifecycle independence and single-active-application contract.
- `DELIB-1965` - compressed VERIFIED bridge thread for `gtkb-isolation-017-slice3-init-defaults-2026-05-02`.
- `DELIB-1969` - compressed VERIFIED bridge thread for `gtkb-isolation-017-slice2-registry-isolation`.

No available bridge-thread evidence authorizes creating a new `tests/scripts`
lane for this platform-script test.

## Findings

### FINDING-P1-001 - Test target path is inconsistent with the live platform test layout

Observation: The proposal places the new test at
`tests/scripts/test_isolation_program_backstop.py` and maps all focused pytest
and ruff commands to that path, but the live repository uses
`platform_tests/scripts/` for platform script tests.

Evidence:

- `bridge/gtkb-isolation-019-program-closeout-003.md:23` lists `tests/scripts/test_isolation_program_backstop.py` in `target_paths`.
- `bridge/gtkb-isolation-019-program-closeout-003.md:93` says to add `tests/scripts/test_isolation_program_backstop.py`.
- `bridge/gtkb-isolation-019-program-closeout-003.md:109-113` maps the focused pytest and ruff commands to `tests/scripts/test_isolation_program_backstop.py`.
- `Test-Path tests\scripts` returned `False`.
- `Test-Path platform_tests\scripts` returned `True`.
- `scripts/release_candidate_gate.py:343-364` lists platform script tests under `platform_tests/scripts/...`.
- `platform_tests/scripts/test_release_candidate_gate.py` is the existing release-gate test surface for `scripts/release_candidate_gate.py`.
- The applicability preflight emitted `warnings.missing_parent_dirs: ["tests/scripts/test_isolation_program_backstop.py"]`.

Deficiency rationale: This is not just a missing directory warning. The
proposal's verification path conflicts with the active repo convention and with
the release-gate inventory it intends to extend. A GO would let implementation
create a parallel `tests/scripts` lane instead of extending the existing
`platform_tests/scripts` lane.

Impact: The backstop could be implemented with tests outside the active
platform-test organization, making release-gate integration and future
maintenance noisier. The proposal's own verification commands would also be
misaligned with the repository's current test layout.

Recommended action: Revise the proposal to use
`platform_tests/scripts/test_isolation_program_backstop.py` in `target_paths`,
scope, verification commands, acceptance criteria, and ruff commands. If Prime
Builder intentionally wants to recreate `tests/scripts`, the revision must
justify that structural change and cite the governing test-layout authority.

## Mechanical Review Gates

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-019-program-closeout
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:25148ff681628a4e6394f8bb7013495b5d355766990fe90d60a3ef918e3ac943`
- bridge_document_name: `gtkb-isolation-019-program-closeout`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-019-program-closeout-003.md`
- operative_file: `bridge/gtkb-isolation-019-program-closeout-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["tests/scripts/test_isolation_program_backstop.py"]
- missing_required_specs: []
- missing_advisory_specs: []
```

The missing-parent warning is not a mechanical hard gate by itself, but it
corroborates FINDING-P1-001.

## Clause Applicability

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-019-program-closeout
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-isolation-019-program-closeout`
- Operative file: `bridge\gtkb-isolation-019-program-closeout-003.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

## Required Revision

1. Replace `tests/scripts/test_isolation_program_backstop.py` with `platform_tests/scripts/test_isolation_program_backstop.py` everywhere in the proposal unless intentionally proposing a governed test-layout change.
2. Update the pytest and ruff commands to use the revised path.
3. Re-run and embed the bridge applicability and clause preflights after filing the revision.

Decision needed from owner: None.

