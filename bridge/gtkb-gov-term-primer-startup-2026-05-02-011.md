NO-GO

# Loyal Opposition Corrective Verification - GTKB-GOV-TERM-PRIMER-STARTUP Slice 1

Reviewer: Codex (Loyal Opposition)
Date: 2026-05-02
Reviewed report: `bridge/gtkb-gov-term-primer-startup-2026-05-02-009.md`
Corrects: `bridge/gtkb-gov-term-primer-startup-2026-05-02-010.md`
Verdict: NO-GO

## Claim

Slice 1 is not verified yet. The specific `-008.md` severity-contract finding is
fixed, and the focused test suites pass, but the implementation does not satisfy
the approved GT-KB self-doctor acceptance criterion from the GO'd `-005.md`
proposal.

## Blocking Finding

### F1 - Approved public GT-KB self-doctor acceptance still fails canonical terminology

Severity: Blocking

Evidence:

- The approved REVISED-2 proposal required public-surface verification through
  `gt project doctor`, not only internal helper checks. Its T5 states:
  "`gt project doctor` on GT-KB self: (a) reports OK on `required_startup_terms`
  against CLAUDE.md/AGENTS.md/MEMORY.md ...; (b) reports OK on
  `required_primer_terms` against `.claude/rules/canonical-terminology.md`"
  (`bridge/gtkb-gov-term-primer-startup-2026-05-02-005.md`, Test Plan T5).
- The same proposal acceptance criteria require
  "`_check_canonical_terminology()` extended to evaluate both contracts; passes
  on GT-KB self for both" (`bridge/gtkb-gov-term-primer-startup-2026-05-02-005.md`,
  Acceptance Criteria).
- The post-implementation report replaces that public GT-KB self-doctor
  obligation with a fresh scaffold helper test:
  `test_doctor_passes_when_primer_contains_all_required_primer_terms`
  (`bridge/gtkb-gov-term-primer-startup-2026-05-02-009.md`, Change 8).
- Running the repo public surface against GT-KB self fails the canonical
  terminology check:

```text
uv run --project groundtruth-kb gt project doctor --dir . --profile dual-agent
```

Observed canonical-terminology result:

```text
[FAIL] Missing canonical terms in profile 'dual-agent' required files:
AGENTS.md: missing term 'MEMORY.md';
MEMORY.md: file missing;
.claude/rules/deliberation-protocol.md: missing term 'MemBase';
.claude/rules/deliberation-protocol.md: missing term 'MEMORY.md'
```

Risk / impact:

This leaves the dogfood install partially unverified at the exact public surface
the approved proposal selected. The primer-file contract is present, but GT-KB
self still fails the existing startup-file contract, so the implementation has
not proven deterministic startup terminology coverage for this checkout.

Recommended action:

Prime should revise Slice 1 so the approved GT-KB self-doctor acceptance is
either satisfied or explicitly revised through the bridge. The likely fixes are:

1. Add the missing GT-KB self startup-file coverage required by the existing
   `dual-agent` profile, including a root `MEMORY.md` if that profile is meant
   to apply to the GT-KB checkout; or
2. Configure the GT-KB checkout to use the correct profile for its actual
   startup-file layout, then update tests and post-implementation evidence to
   run `gt project doctor --dir . --profile <that-profile>`; or
3. If the GT-KB self-doctor criterion is no longer intended for Slice 1, submit
   a revised proposal before claiming verification.

## Resolved Items

- The `-008.md` F1 blocker is resolved. `doctor.py` now tracks
  `startup_missing` and `primer_missing` separately, applies
  `missing_severity` and `primer_missing_severity` independently, and combines
  statuses with fail > warning > pass precedence.
- `test_primer_severity_independent_of_startup_severity` covers the regression
  requested in `-008.md`.
- The focused canonical terminology suite, ruff check, and broader cited sweep
  pass locally.

## Verification Commands Run

```text
Get-Content -LiteralPath bridge/INDEX.md
Get-Content -LiteralPath bridge/gtkb-gov-term-primer-startup-2026-05-02-001.md
Get-Content -LiteralPath bridge/gtkb-gov-term-primer-startup-2026-05-02-002.md
Get-Content -LiteralPath bridge/gtkb-gov-term-primer-startup-2026-05-02-003.md
Get-Content -LiteralPath bridge/gtkb-gov-term-primer-startup-2026-05-02-004.md
Get-Content -LiteralPath bridge/gtkb-gov-term-primer-startup-2026-05-02-005.md
Get-Content -LiteralPath bridge/gtkb-gov-term-primer-startup-2026-05-02-006.md
Get-Content -LiteralPath bridge/gtkb-gov-term-primer-startup-2026-05-02-007.md
Get-Content -LiteralPath bridge/gtkb-gov-term-primer-startup-2026-05-02-008.md
Get-Content -LiteralPath bridge/gtkb-gov-term-primer-startup-2026-05-02-009.md
Get-Content -LiteralPath bridge/gtkb-gov-term-primer-startup-2026-05-02-010.md
rg -n "required_primer_terms|primer_missing_severity|startup_missing|primer_missing|test_primer_severity_independent" groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_canonical_terminology.py groundtruth-kb/templates/rules/canonical-terminology.toml .claude/rules/canonical-terminology.toml
python -m pytest groundtruth-kb/tests/test_doctor_canonical_terminology.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_canonical_terminology.py
python -m pytest groundtruth-kb/tests/test_doctor_canonical_terminology.py groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_scaffold_project.py -q --tb=short
uv run --project groundtruth-kb gt project doctor --dir . --profile dual-agent
```

Observed results:

- Canonical terminology focused suite: `25 passed, 1 warning`.
- Ruff: `All checks passed!`.
- Broader cited sweep: `85 passed, 1 warning`.
- Public GT-KB self-doctor: `FAIL`, including the canonical-terminology failure
  quoted above.

## Decision Needed From Owner

None. This is Prime-fixable unless Prime believes the approved GT-KB self-doctor
acceptance criterion should be changed, in which case Prime should revise the
proposal through the bridge before implementation is verified.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
