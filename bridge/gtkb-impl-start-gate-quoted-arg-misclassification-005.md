REVISED

# implementation_start_gate Quoted-Argument Misclassification Fix - Revised Implementation Report

bridge_kind: implementation_report_revision
Document: gtkb-impl-start-gate-quoted-arg-misclassification
Version: 005
Responds to: bridge/gtkb-impl-start-gate-quoted-arg-misclassification-004.md NO-GO
Revises: bridge/gtkb-impl-start-gate-quoted-arg-misclassification-003.md
Approved proposal: bridge/gtkb-impl-start-gate-quoted-arg-misclassification-001.md
Approved GO: bridge/gtkb-impl-start-gate-quoted-arg-misclassification-002.md
Author: Prime Builder (Codex, harness A)
Date: 2026-06-16 UTC
Recommended commit type: fix:
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3358
target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ed107-175f-7ae2-a0fd-7f5842689029
author_model: GPT-5
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override via ::init gtkb pb; approval_policy=never

implementation_scope: source, test
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

This REVISED implementation report addresses the Loyal Opposition NO-GO in
`bridge/gtkb-impl-start-gate-quoted-arg-misclassification-004.md`.

- FINDING-P1-001 addressed: `_has_mutating_signal()` now applies the existing quote-mask helper to the shell-level mutating-command regex, then separately parses actual `python -c` source with `ast` to preserve real Python mutation true positives. Descriptive Python string literals containing `sqlite3`, `write_text`, or `open(..., "w")` no longer trigger the gate.
- FINDING-P2-001 addressed: this report carries forward the broader specification set from the GO'd proposal and maps each governing surface to executed evidence or scoped rationale.

## Implementation Claim

The implementation-start gate now separates shell syntax from Python source semantics:

- `scripts/implementation_start_gate.py` adds `_has_python_mutating_signal()` and small AST helpers. It detects actual `python -c` calls to `write_text`, `open(..., "w")`, `insert_*`, `update_*`, `delete_*`, and unsafe sqlite operations, while ignoring mutation-shaped text that appears only as Python string data.
- `_has_mutating_signal()` scans `MUTATING_COMMAND_RE` against `_mask_quoted_spans(command, mask_double=True)` for shell-level command names, then ORs in AST-based Python mutation detection and existing quote-aware redirect detection.
- `platform_tests/scripts/test_implementation_start_gate.py` adds WI-3358 regression coverage for the NO-GO examples and the true-positive preservation cases.

No files outside the approved `target_paths` were modified for source or test implementation.

Implementation-start authorization was created before protected edits:

- Claim command: `python scripts/bridge_claim_cli.py claim gtkb-impl-start-gate-quoted-arg-misclassification --ttl-seconds 7200`
- Claim holder: `019ed107-175f-7ae2-a0fd-7f5842689029`
- Claim acquired: `2026-06-16T15:44:20Z`
- Packet command: `python scripts/implementation_authorization.py begin --bridge-id gtkb-impl-start-gate-quoted-arg-misclassification`
- Packet hash: `sha256:c67498bdfd313fd6966a168f9e1f5cf49ce2c9feed92ada7259e4c1508bdb5e2`
- Packet target path globs: `scripts/implementation_start_gate.py`, `platform_tests/scripts/test_implementation_start_gate.py`
- Packet latest status at creation: `NO-GO`
- Packet GO file: `bridge/gtkb-impl-start-gate-quoted-arg-misclassification-002.md`

## Owner Decisions / Input

No new owner decision was required. Existing authority is the active reliability fast-lane standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, owner-decision basis `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`, and the Loyal Opposition GO in `bridge/gtkb-impl-start-gate-quoted-arg-misclassification-002.md`.

## Specification Links

Carried forward from the approved proposal and applied to this revised implementation report:

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - primary gate behavior: protected implementation mutations require live authorization, while read-only descriptive commands must not false-block.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this append-only bridge revision preserves the versioned bridge audit chain under the dispatcher/TAFE-backed bridge protocol; the retired bridge index is not used as live authority.
- `GOV-RELIABILITY-FAST-LANE-001` - WI-3358 is a small single-concern reliability defect fix under the standing fast-lane authorization.
- `GOV-STANDING-BACKLOG-001` - this is a single work item, not a bulk backlog operation.
- `GOV-ARTIFACT-APPROVAL-001` - the gate remains the enforcement surface for protected mutation evidence; genuine mutations still require an authorization packet.
- `SPEC-AUQ-POLICY-ENGINE-001` - command classification remains deterministic and tested.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all source, test, and bridge artifacts are inside `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the approved proposal carried target paths, PAUTH/project/WI metadata, and linked governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps linked specifications to executed tests and observed results.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect, authorization, implementation evidence, and verification evidence are preserved as durable bridge artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the correction is represented as durable source/test artifacts plus a versioned bridge report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3358 remains in the bridge lifecycle until Loyal Opposition records terminal VERIFIED.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner basis for the reliability fast-lane standing authorization.
- `bridge/gtkb-impl-start-gate-comparison-operator-fix-006.md` - prior VERIFIED sibling for comparison-operator redirect false positives.
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-010.md` - prior VERIFIED sibling that introduced `_mask_quoted_spans`.
- `bridge/gtkb-s358-w4-enforcement-calibration-008.md` - prior VERIFIED sibling for redirect-token replacement.
- `bridge/gtkb-impl-start-gate-quoted-arg-misclassification-001.md` - approved proposal.
- `bridge/gtkb-impl-start-gate-quoted-arg-misclassification-002.md` - Loyal Opposition GO.
- `bridge/gtkb-impl-start-gate-quoted-arg-misclassification-004.md` - Loyal Opposition NO-GO addressed by this revision.

## Findings Addressed

| NO-GO finding | Response |
| --- | --- |
| `FINDING-P1-001` Raw `PYTHON_MUTATING_RE` still false-blocks quoted literals | Replaced raw full-command mutation detection with shell quote-masking plus AST-based `python -c` mutation detection. Added regression tests for quoted sqlite/write_text/open-w literal strings and true positives for actual Python write/sqlite/backlog-style calls. |
| `FINDING-P2-001` Post-implementation spec mapping is narrower than the GO'd proposal | This report carries forward all required and advisory specs from the approved proposal and maps each to verification evidence below. |

## Specification-Derived Verification Plan And Results

| Spec / governing surface | Executed verification evidence | Result |
| --- | --- | --- |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` false-positive removal | `test_gate_allows_quoted_python_mutation_literals` covers quoted Python string literals containing `sqlite3`, `write_text`, and `open(..., "w")`; `gate_decision()` returns `{}` for each. | PASS |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` true-positive preservation | `test_gate_preserves_python_mutation_true_positives` covers actual Python `write_text`, `open(..., "w")`, sqlite INSERT, and `insert_*` calls; `gate_decision()` blocks without authorization. | PASS |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` allowed bridge writes | `test_gate_allows_bridge_write_with_quoted_protected_path_mention` verifies a genuine `bridge/` write remains allowed when the value text mentions `scripts/secret.py`. | PASS |
| `GOV-ARTIFACT-APPROVAL-001` | The true-positive tests prove genuine protected implementation writes still require a live packet; implementation itself used packet `sha256:c67498bdfd313fd6966a168f9e1f5cf49ce2c9feed92ada7259e4c1508bdb5e2`. | PASS |
| `SPEC-AUQ-POLICY-ENGINE-001` | Focused classifier tests and ruff checks exercise deterministic classifier behavior. | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps linked specs to executed verification evidence and observed results. | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report is an append-only `REVISED` bridge version prepared for the governed bridge revision helper; no prior bridge file is rewritten or deleted. | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed implementation paths are `scripts/implementation_start_gate.py` and `platform_tests/scripts/test_implementation_start_gate.py`; both are inside `E:\GT-KB`. | PASS |
| `GOV-RELIABILITY-FAST-LANE-001` | Scope remains one defect fix, one source file, and one test file. No CLI/API/spec/deployment change. | PASS |
| `GOV-STANDING-BACKLOG-001` | This report implements only WI-3358 and performs no bulk backlog mutation. | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Implementation evidence, authorization evidence, and lifecycle response are preserved in this versioned bridge report. | PASS |

## Commands Run

```text
python scripts/bridge_claim_cli.py claim gtkb-impl-start-gate-quoted-arg-misclassification --ttl-seconds 7200
```

Observed: exit 0; claim holder `019ed107-175f-7ae2-a0fd-7f5842689029`; acquired `2026-06-16T15:44:20Z`.

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-impl-start-gate-quoted-arg-misclassification
```

Observed: exit 0; packet hash `sha256:c67498bdfd313fd6966a168f9e1f5cf49ce2c9feed92ada7259e4c1508bdb5e2`; target path globs exactly match the two approved implementation target paths.

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py::test_gate_allows_quoted_python_mutation_literals platform_tests/scripts/test_implementation_start_gate.py::test_gate_preserves_python_mutation_true_positives platform_tests/scripts/test_implementation_start_gate.py::test_gate_allows_bridge_write_with_quoted_protected_path_mention -q --tb=short
```

Observed: `8 passed in 6.41s`.

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short
```

Observed: `106 passed, 11 failed, 1 warning in 42.84s`.

The 11 failures are outside the WI-3358 assertions and were not introduced by the new tests:

- 10 failures occur before authorization assertions because `_claim_bridge(...)` attempts a `go_implementation` claim in a synthetic `tmp_path` root without a Prime session marker, so `scripts.bridge_work_intent_registry.WorkIntentRegistryError` reports `interactive session marker role None (not prime-eligible)`.
- 1 failure is `test_non_go_bridge_entry_cannot_create_authorization`, which still expects an AuthorizationError for non-GO latest status even though the live authorization helper now supports NO-GO continuation packets, as used for this thread.
- All new WI-3358 tests pass in the same file run.

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_implementation_start_gate.py::test_gate_allows_quoted_python_mutation_literals platform_tests/scripts/test_implementation_start_gate.py::test_gate_preserves_python_mutation_true_positives platform_tests/scripts/test_implementation_start_gate.py::test_gate_allows_bridge_write_with_quoted_protected_path_mention -q --tb=short
```

Observed: exit 1 before collection; venv pytest does not recognize the project-configured `--timeout=30` option. The default Python interpreter has the timeout plugin and was used for executable test evidence above.

```text
python -m ruff check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py
```

Observed: `All checks passed!`

```text
python -m ruff format --check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py
```

Observed: `2 files already formatted`

```text
git diff --check -- scripts\implementation_start_gate.py platform_tests\scripts\test_implementation_start_gate.py
```

Observed: exit 0, no output.

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-start-gate-quoted-arg-misclassification --content-file .gtkb-state\bridge-revisions\drafts\gtkb-impl-start-gate-quoted-arg-misclassification-005.md
```

Observed: exit 0; `packet_hash=sha256:a637e505cef63b318ff03b41dd1e734ead567083f02a5059274396866bc8d392`; `preflight_passed=true`; `missing_required_specs=[]`; `missing_advisory_specs=[]`.

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-gate-quoted-arg-misclassification --content-file .gtkb-state\bridge-revisions\drafts\gtkb-impl-start-gate-quoted-arg-misclassification-005.md
```

Observed: exit 0; clauses evaluated 5; must_apply 4; evidence gaps in must_apply clauses 0; blocking gaps 0.

## Files Changed

- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `bridge/gtkb-impl-start-gate-quoted-arg-misclassification-005.md` - this bridge revision after helper filing.

The broader worktree contains unrelated pre-existing dirty files. This implementation deliberately stayed inside the two approved source/test target paths plus the bridge revision/report filing.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: repairs an implementation-start-gate false-positive defect with focused regression coverage; no new user-facing API or deployment surface.

## Acceptance Criteria Status

- Quote-masked shell-level mutating-command scan: satisfied.
- AST-aware Python true-positive preservation: satisfied.
- Quoted sqlite/write_text/open-w literal false positives removed: satisfied by focused tests.
- Genuine Python write/sqlite/insert true positives preserved: satisfied by focused tests.
- Allowed `bridge/` write with quoted protected-path mention preserved: satisfied by focused test.
- Ruff lint and format checks: satisfied.
- Full implementation-start-gate file: residual non-WI-3358 failures disclosed above for Loyal Opposition disposition.

## Risk And Rollback

Risk is low and bounded to the command classifier. Rollback is to revert the helper additions and the `_has_mutating_signal()` change in `scripts/implementation_start_gate.py`, plus the WI-3358 regression tests. That would restore the previous raw-regex behavior and reintroduce the false-positive class documented in `-004`.
