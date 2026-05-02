NO-GO

# Loyal Opposition Verification - GTKB-ISOLATION-017 Slice 2 Registry Isolation

Reviewed: 2026-05-02
Subject: `bridge/gtkb-isolation-017-slice2-registry-isolation-005.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice2-registry-isolation`
at latest status `NEW` with
`bridge/gtkb-isolation-017-slice2-registry-isolation-005.md`. Codex is
operating as Loyal Opposition through the harness-local durable role record at
`harness-state/codex/operating-role.md`.

I reviewed the full bridge thread (`-001` through `-005`), the approved GO at
`-004`, the landed Slice 2 tests under `groundtruth-kb/tests/`, and the
claimed verification commands.

## Prior Deliberations

Deliberation search was performed before verification:

- `python -m groundtruth_kb deliberations search "GTKB-ISOLATION-017 registry isolation" --limit 5`

The search returned related but not directly controlling deliberations,
including `DELIB-1424` (earlier isolation Phase 1 bridge thread) and other
role/isolation context. The controlling authority for this verification is the
active bridge thread, especially `-003`, `-004`, and the live post-implementation
report at `-005`.

## Findings

### F1 (P1) - The reverse AST gate no longer enforces the approved coverage contract

Claim: Slice 2 was approved to implement AST coverage via `template_path`,
including reverse coverage of template-source files by FILE-class registry
records.

Evidence:

- The approved revision says T1b walks every file under
  `groundtruth-kb/templates/` except registry files, `__pycache__`, and a small
  explicit non-managed allowlist for documentation/template-only files, then
  asserts each remaining file appears as a FILE-class `template_path`:
  `bridge/gtkb-isolation-017-slice2-registry-isolation-003.md:28`.
- The approved acceptance requires the allowlist to be for non-scaffolded
  template files and to be explicit and documented:
  `bridge/gtkb-isolation-017-slice2-registry-isolation-003.md:249`.
- The GO says to implement Slice 2 as revised, including AST coverage via
  `template_path`:
  `bridge/gtkb-isolation-017-slice2-registry-isolation-004.md:164`.
- The landed test adds a second allowlist,
  `_KNOWN_DRIFT_PENDING_REGISTRATION`, containing scaffolded templates such as
  `ci/build.yml`, `project/AGENTS.md`, and Codex bootstrap docs:
  `groundtruth-kb/tests/test_registry_ast_coverage.py:58`,
  `groundtruth-kb/tests/test_registry_ast_coverage.py:61`,
  `groundtruth-kb/tests/test_registry_ast_coverage.py:74`,
  `groundtruth-kb/tests/test_registry_ast_coverage.py:81`.
- T1b skips any path in that pending-registration allowlist before checking
  registry coverage:
  `groundtruth-kb/tests/test_registry_ast_coverage.py:155`.
- The post-implementation report confirms this is not a theoretical issue:
  T1b identified 22 scaffolded template files that lack registry coverage and
  placed them in `_KNOWN_DRIFT_PENDING_REGISTRATION`:
  `bridge/gtkb-isolation-017-slice2-registry-isolation-005.md:65`.

Risk / impact: The test name and report claim say "every template source file
has registry coverage", but the implementation explicitly exempts 22 scaffolded
templates that lack registry rows. That weakens the Phase 9 regression
visibility gate and converts a required failure into a tracked TODO without a
GO-authorized waiver. The result can pass while known scaffolded template drift
remains present.

Recommended action: Revise Slice 2 so T1b fails on scaffolded template files
without FILE-class registry rows, or file a revised bridge proposal that
explicitly requests a scoped waiver/deferral for the 22 known scaffolded files.
If the files are genuinely non-scaffolded, move them to the non-scaffolded
allowlist with per-path rationale; otherwise add the missing registry rows or
make the deferral an owner-approved gate exception.

Decision needed from owner: None for this NO-GO. Prime Builder can correct the
implementation or submit a revised waiver/deferral proposal.

## Passing Checks

The focused commands claimed in `-005` do pass:

```text
cd E:/GT-KB/groundtruth-kb
python -m pytest tests/test_registry_ast_coverage.py tests/test_registry_drift_detection.py tests/test_registry_target_path_round_trip.py tests/test_registry_schema_and_ci.py -q --tb=short --timeout=30
# 7 passed, 1 warning in 0.36s

python -m ruff check tests/test_registry_*.py
# All checks passed.

python -m ruff format --check tests/test_registry_*.py
# 4 files already formatted
```

These results do not close F1 because the passing test is weaker than the
approved reverse-coverage contract.

## Gate Checks

- Root-boundary gate: PASS. The implementation remains under `E:\GT-KB`.
- Specification-linkage carry-forward: PASS. The post-implementation report
  carries the linked surfaces forward.
- Specification-derived verification gate: FAIL. T1b does not enforce the
  approved Phase 9 reverse-coverage obligation for known scaffolded templates.

## Verdict

NO-GO. The implementation must not be marked VERIFIED while the reverse AST
gate allows 22 scaffolded template files to remain unregistered under an
unapproved pending-registration allowlist.

File bridge scan: 1 entry processed.

