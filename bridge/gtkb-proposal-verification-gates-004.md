NO-GO

# GT-KB Proposal And Verification Gates Post-Implementation Review

**Status:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-22
**Reviewed report:** `bridge/gtkb-proposal-verification-gates-003.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Verdict

NO-GO for post-implementation verification.

The implementation is directionally correct and the focused verification lane
passes, but it does not yet satisfy all binding conditions from
`bridge/gtkb-proposal-verification-gates-002.md`.

This NO-GO does not reject the architecture. It requires a narrow revision for
metadata precedence, affected-spec evidence, and waiver/metadata failure-mode
tests before `GTKB-GOV-012` can be marked `VERIFIED`.

## Finding 1 - Metadata precedence can misclassify implementation reports

Severity: P1 / blocks `VERIFIED`.

`BridgeEntry.metadata` can let older proposal metadata overwrite newer
implementation-report metadata for the same key.

Evidence:

- `src/groundtruth_kb/file_bridge.py:675` defines hard-gate metadata checks.
- `src/groundtruth_kb/file_bridge.py:709` contains the implementation-report
  missing-`spec_ids` violation.
- Reproduction in the upstream checkout with a metadata-rich
  `proposal -> GO review -> implementation_report` thread produced:

```text
effective_bridge_kind= proposal
violation_reasons= ['latest bridge entry is awaiting Loyal Opposition review']
```

Expected: effective `bridge_kind` should remain `implementation_report`, and
the hard gate should also report missing affected `spec_ids` for the
implementation report.

Impact: a clean adopter following the new metadata guidance can file an
implementation report whose latest `bridge_kind` is hidden by the original
proposal. That weakens fail-closed metadata behavior and post-verification
spec-status review.

Required revision:

1. Fix effective metadata precedence so latest-version identity fields such as
   `bridge_kind`, `requires_verification`, waiver fields, and implementation
   status-review fields are not overwritten by older proposal metadata.
2. Preserve inherited fields that should carry forward, such as `target_paths`,
   `spec_ids`, and `work_item_ids`, when the latest response omits them.
3. Add a regression test for a full metadata-rich
   `proposal -> GO review -> implementation_report` sequence.

## Finding 2 - Current report lacks affected spec metadata

Severity: P1 / blocks `VERIFIED`.

`bridge/gtkb-proposal-verification-gates-003.md:5-10` declares
`bridge_kind: implementation_report`, `work_item_ids: [GTKB-GOV-012]`,
`target_paths`, and `requires_verification: true`, but it does not declare
affected `spec_ids`.

The live protocol gate confirms this remains visible after the NO-GO response:

```text
python -m groundtruth_kb bridge gate --dir . --require-verified --scope protocol --json
```

Result: exit code `1`; violations include:

```text
gtkb-proposal-verification-gates - implementation report is missing affected spec_ids metadata
```

Impact: if this implementation were marked `VERIFIED` without a revised
affected-spec record or explicit no-affected-spec semantics, `gt bridge
spec-review` would have no affected formal records to surface for the very
workflow `GTKB-GOV-012` is introducing.

Required revision:

- Add affected `spec_ids` to the revised post-implementation report and ensure
  `gt bridge spec-review --scope protocol` can surface them after verification;
  or
- revise the gate semantics and tests to support an explicit
  no-affected-specs rationale instead of relying on absent metadata.

## Finding 3 - Binding waiver and metadata failure-mode tests are incomplete

Severity: P1 / blocks `VERIFIED`.

`bridge/gtkb-proposal-verification-gates-002.md:56-58` made the following test
coverage binding before verification:

```text
Tests must cover missing bridge_kind, ambiguous scope, missing target paths
for implementation-linked proposals, missing implementation report metadata,
and malformed waiver metadata.
```

The current tests cover only a subset:

- `tests/test_file_bridge.py:75` covers missing `bridge_kind` plus missing all
  blocking target metadata in one generic proposal case.
- `tests/test_file_bridge.py:134` covers the valid waiver path.
- `src/groundtruth_kb/file_bridge.py:480` implements an invalid waiver
  violation, and `:726` implements waiver validation, but there is no focused
  test for malformed, expired, incomplete, or wrong-bypass waiver metadata.
- There is no focused test that an `implementation_report` missing affected
  `spec_ids` fails the hard `require-verified` gate.
- There is no focused test for the ambiguous-scope fail-closed case required
  by the GO.

Impact: the most governance-sensitive escape hatch, waiver handling, is only
proved for the happy path. The implementation may be correct, but the binding
GO required regression evidence that is not yet present.

Required revision:

Add focused tests proving at least:

1. incomplete waiver metadata fails with `--allow-waivers`;
2. expired waiver metadata fails with `--allow-waivers`;
3. wrong-bypass waiver metadata fails with `--allow-waivers`;
4. malformed waiver expiry fails closed;
5. an implementation report missing affected `spec_ids` fails
   `require-verified`;
6. the approved ambiguous-scope case fails closed, or a revised scope policy is
   explicitly justified and tested.

## Positive Evidence

The implementation satisfies several important parts of the GO:

- The parser lives outside the legacy `groundtruth_kb.bridge` package:
  `src/groundtruth_kb/file_bridge.py`.
- CLI commands exist for status, gates, and spec-review:
  `src/groundtruth_kb/cli.py:751-843`.
- The hook template prefers the shared parser when available:
  `templates/hooks/bridge-compliance-gate.py:28-33`.
- Doctor surfaces bridge lifecycle counts:
  `src/groundtruth_kb/project/doctor.py:1124-1146`.
- Live Agent Red bridge status keeps GT-KB protocol entries visible under
  `--scope protocol`.

## Verification Commands

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
python -m pytest tests/test_file_bridge.py tests/test_cli_bridge.py tests/test_preflight_checks.py tests/test_doctor_bridge_accuracy.py tests/test_scaffold_bridge_index.py tests/test_governance_hooks.py tests/test_bridge_import_hygiene.py -q --tb=short
131 passed, 1 warning in 106.96s

python -m ruff check .
All checks passed!

python -m ruff format --check .
185 files already formatted
```

Additional reproduction command for Finding 1 exited `0` and produced the
metadata-precedence result quoted above.

Commands run in
`E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement` with
`PYTHONPATH` pointed at the upstream source:

```text
python -m groundtruth_kb bridge status --dir . --scope protocol
```

Result: exit code `0`; `gtkb-proposal-verification-gates` is now `NO-GO`.

```text
python -m groundtruth_kb bridge gate --dir . --require-verified --scope protocol --json
```

Result: exit code `1`, including the expected `NO-GO` violation and the
missing affected `spec_ids` metadata violation for
`gtkb-proposal-verification-gates`.

The warning is the existing ChromaDB/Python 3.14 deprecation warning from
`chromadb.telemetry.opentelemetry`.

## Required Prime Builder Actions

1. File a revised post-implementation report or implementation revision as
   `bridge/gtkb-proposal-verification-gates-005.md`.
2. Fix metadata precedence for lifecycle-kind fields while preserving intended
   inheritance of proposal target metadata.
3. Include affected `spec_ids`, or explicitly revise and test
   no-affected-spec semantics.
4. Add the focused waiver/metadata failure-mode tests above.
5. Re-run focused bridge tests, ruff check, and ruff format check; run the full
   upstream suite if the revision touches shared behavior beyond the parser
   tests.

No owner decision is required for these revisions.
