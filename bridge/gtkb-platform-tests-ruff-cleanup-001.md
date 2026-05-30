NEW

# Implementation Proposal - Run ruff check --fix + ruff format on platform_tests/ to Resolve 66 Lint Violations

bridge_kind: implementation_proposal
Document: gtkb-platform-tests-ruff-cleanup
Version: 001 (NEW)
Date: 2026-05-28 UTC
Author: Prime Builder (Claude, harness B)

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-28T13-30-29Z-prime-builder-ruff-cleanup-001
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: explanatory output style; interactive Prime Builder session; reliability fast-lane

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3423

target_paths: ["platform_tests/**/*.py"]

## Claim

`platform_tests/` has 66 ruff violations across 42 files, which the Lint job of Phase 2 CI reports as a failure. 61 of 66 are mechanically auto-fixable via `ruff check --fix` + `ruff format`; 5 require manual review (one SIM117 nested-with case where the contexts have semantic ordering, and one SIM103 return-condition case where the wrapper improves readability for the test). This proposal resolves all 66 violations and restores Lint job pass.

## Defect / Reproduction

Live probe (2026-05-28, this session):

```
$ python -m ruff check platform_tests/
[...66 violation lines...]
Found 66 errors.
[*] 61 fixable with the `--fix` option (1 hidden fix can be enabled with the `--unsafe-fixes` option).
```

Violation breakdown by class:

| Class | Count | Auto-fixable | Description |
|---|---:|---:|---|
| `I001` | 30 | yes | Import block sorting or formatting |
| `SIM117` | 14 | 11 yes / 3 manual | Nested `with` statements (combinable) |
| `F401` | 9 | yes | Unused imports |
| `SIM300` | 7 | yes | Yoda condition (constant on left) |
| `UP017` | 3 | yes | Use `datetime.UTC` alias |
| `UP035` | 1 | yes | Import `Mapping` from `collections.abc` |
| `SIM114` | 1 | yes | Combine `if` branches using `or` |
| `SIM103` | 1 | manual | Return condition directly |

61 auto-fix + 5 manual = 66 total.

## In-Root Placement Evidence

Target path glob `platform_tests/**/*.py` resolves entirely within `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. No `applications/**` files touched. The 42 affected files all live under `platform_tests/governance/`, `platform_tests/groundtruth_kb/`, `platform_tests/scripts/`, `platform_tests/transport/`, `platform_tests/unit/`, and `platform_tests/test_*.py` (top level).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this proposal follows NEW/GO/REVISED/NO-GO/VERIFIED workflow.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - test files are governed code artifacts; lint compliance is a quality property.
- `GOV-RELIABILITY-FAST-LANE-001` - governing fast-lane spec; eligibility argued in the subsection below.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the relevant cross-cutting specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below maps acceptance to verification commands.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization + Project + Work Item header lines present.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner-decision evidence captured via AskUserQuestion this session.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - target path glob within `E:\GT-KB`; no `applications/**` paths.
- `GOV-SESSION-SELF-INITIALIZATION-001` - Lint job is one of the testing/tool integrations surfaced in the startup payload; this fix removes a hard-fail signal.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - test-file-only change; no hook surface impact; parity preserved.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - lint cleanup is a code-artifact lifecycle operation.
- `GOV-STANDING-BACKLOG-001` - WI-3423 created and linked to PROJECT-GTKB-RELIABILITY-FIXES; appears in the standing backlog.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-approved standing fast-lane authorization underlying `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
- S363 Phase 2 CI gate triage (2026-05-27) - the lint job's red status was identified during S363 Phase 2 work-front review.
- This session's AskUserQuestion answer (2026-05-28): owner directed "File proposal for full 66-violation cleanup" when presented with the live-state-versus-S363-resume-directive scope discrepancy.

## Owner Decisions / Input

- 2026-05-28 UTC, this session: owner answered AskUserQuestion "How should I proceed?" with "File proposal for full 66-violation cleanup". The option was described as "Author a reliability-fast-lane proposal to run ruff check --fix and ruff format on platform_tests/ (61 of 66 auto-fixable) + manually address the 5 non-auto-fixable". This authorizes the proposal scope including the auto-fix and manual-fix mix.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: active standing project authorization; `allowed_mutation_classes=["source","test_addition","hook_upgrade"]`. The mutation class for this proposal is documented in the Reliability Fast-Lane Eligibility subsection below; the proposal explicitly notes the PAUTH wording and argues coverage.

## Requirement Sufficiency

Existing requirements sufficient. Lint compliance is implicit in the project's CI gate definition (Lint job on develop). No new or revised specification is required; the change is a defect repair against the existing implicit lint contract.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One work item (WI-3423), one concern (lint compliance in `platform_tests/`), one verification target (Lint job pass). The number of files touched is incidental to the automated nature of the fix; ruff applies one cohesive set of corrections, not a sweep across independent work items. No `inventory` sweep, no batch MemBase mutation, no specification promotion. References to "work item" and "standing backlog" describe this single work item only.

### Reliability Fast-Lane Eligibility (per GOV-RELIABILITY-FAST-LANE-001)

1. **Small single-concern defect fix**: lint compliance is one concern; the fix is one ruff invocation plus a small set of manual edits.
2. **Source / test target paths**: `platform_tests/**/*.py` are test source files. The standing PAUTH's `allowed_mutation_classes=["source","test_addition","hook_upgrade"]` lists `test_addition` (for adding new tests) but not `test_modification`. Two possible readings:
   - Inclusive reading: lint cleanup of test files is "source"-class because tests are code; PAUTH covers it.
   - Exclusive reading: "test_modification" is its own class, not covered; this proposal requires a finding either way.
   - This proposal explicitly surfaces the ambiguity rather than assume coverage. If Codex prefers exclusive reading, the appropriate response is NO-GO with a finding that the PAUTH needs a `test_modification` mutation class added, OR per-WI owner authorization is required. Either is acceptable from Prime Builder's perspective.
3. **No forbidden operations**: no deploy, no `git push --force`, no spec deletion, no MemBase mutation (beyond the WI-3423 record already created via the backlog-add CLI).
4. **Bounded scope**: 42 files in one subdirectory tree; one tooling invocation (`ruff check --fix` + `ruff format`); approximately 60-100 lines changed across the affected files (import re-ordering and small syntactic transformations).
5. **Reversible**: a single `git checkout platform_tests/` reverts the entire change. No state outside the test files is touched.

## Proposed Scope

### IP-1: Run ruff auto-fix on platform_tests/

```
python -m ruff check --fix platform_tests/
```

Expected: 61 of 66 violations resolved automatically. Five violations remain after this step.

### IP-2: Run ruff format on platform_tests/

```
python -m ruff format platform_tests/
```

Expected: whitespace and formatting normalized; no additional behavioral changes.

### IP-3: Manually address remaining 5 violations

Inspect each of the 5 non-auto-fixable violations and decide whether to manually rewrite, suppress with a per-line `# noqa: <code>` (only if the violation is behaviorally meaningful and the suppression is documented), or restructure to remove the violation source. The 5 violations and tentative dispositions:

- `platform_tests/scripts/test_bridge_index_writer.py:161,249` (SIM117 nested with) - if the inner `with` depends on the outer's setup, combining changes semantics; if not, manual flatten. Inspect on implementation.
- `platform_tests/scripts/test_bridge_scheduler_leases.py:210` (SIM117) - same disposition.
- `platform_tests/scripts/test_kb_attribution.py:67` (SIM117) - same disposition.
- `platform_tests/test_no_active_smart_poller_wording.py:192` (SIM103 return condition) - the explicit form may be more readable for the test; suppress with `# noqa: SIM103` if so, otherwise rewrite.

### IP-4: Verify zero lint errors

```
python -m ruff check platform_tests/
python -m ruff format --check platform_tests/
```

Expected: both commands return 0 errors / "All checks passed!".

### IP-5: Verify pytest still passes

```
python -m pytest platform_tests/ -q --tb=short
```

Expected: same pass/fail set as the pre-change baseline (this proposal does not aim to fix any test failures, only to clean lint).

## Specification-Derived Verification Plan

| Specification | Test or verification command | Behavior verified |
|---|---|---|
| `GOV-SESSION-SELF-INITIALIZATION-001` | `python -m ruff check platform_tests/` post-implementation | Lint job pass restored; no `Found N errors` line. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `python -m ruff format --check platform_tests/` | Code-artifact formatting is governed and conformant. |
| `GOV-RELIABILITY-FAST-LANE-001` | Reliability Fast-Lane Eligibility subsection above | Eligibility argued; PAUTH coverage explicitly surfaced for Codex disposition. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge protocol inspection (NEW -> GO -> impl -> report -> VERIFIED) | Bridge protocol path followed. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-platform-tests-ruff-cleanup` | Applicability preflight passes; no `missing_required_specs`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table populated end-to-end in the post-impl report | Spec-to-test mapping evidence present. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header inspection (Project Authorization / Project / Work Item lines) | All three present. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-platform-tests-ruff-cleanup` | In-root clause passes. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Inspection: implementation is test-file-only | No hook surface touched. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Bridge thread + post-impl report inspection | Test artifacts continue governed; cleanup is lifecycle-state-preserving. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Owner Decisions / Input section above | Owner direction collected via AskUserQuestion. |
| `GOV-STANDING-BACKLOG-001` | `SELECT id FROM current_work_items WHERE id = 'WI-3423'` returns one row; `SELECT ... FROM current_project_work_item_memberships WHERE work_item_id = 'WI-3423' AND project_id = 'PROJECT-GTKB-RELIABILITY-FIXES'` returns active membership | WI exists; project-membership row present. |

Run commands during post-implementation verification:

```
python -m ruff check platform_tests/
python -m ruff format --check platform_tests/
python -m pytest platform_tests/ -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-platform-tests-ruff-cleanup
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-platform-tests-ruff-cleanup
```

## Acceptance Criteria

1. `ruff check platform_tests/` returns 0 errors.
2. `ruff format --check platform_tests/` returns "All checks passed!".
3. `pytest platform_tests/` shows the same pass/fail count as the pre-change baseline (no new test failures introduced by lint cleanup).
4. Both bridge preflights pass on the operative file.
5. Any `# noqa` suppression added in IP-3 carries an inline comment explaining the suppression reason.

## Risks / Rollback

- Risk: a ruff auto-fix unexpectedly changes test semantics (e.g., a Yoda-condition swap that interacts with custom equality). Mitigation: IP-5 (pytest) catches this; if any test fails post-fix that passed pre-fix, the violation in question is reverted manually and re-suppressed.
- Risk: the SIM117 manual cases involve `with` statements whose context-manager order matters (e.g., a `tmp_path` fixture depending on a `monkeypatch` setter). Mitigation: IP-3 instructs case-by-case inspection rather than blind flattening.
- Risk: the PAUTH does not list `test_modification` in `allowed_mutation_classes`. Mitigation: this proposal surfaces the gap explicitly in the Reliability Fast-Lane Eligibility subsection; Codex disposition will direct the path forward (proceed under standing PAUTH, or require per-WI owner approval, or require PAUTH amendment).
- Rollback: `git checkout HEAD -- platform_tests/` reverts the entire change. WI-3423 transitions back to `open` from any intermediate state.

## Files Expected To Change

- 42 files under `platform_tests/**/*.py` (full enumeration available in the live `ruff check platform_tests/` output cited in the Defect / Reproduction section). Each file's edit is small: import-block re-ordering, syntactic alias swap, or unused-import removal. No file's logic is changed.

## Recommended Commit Type

`refactor:` - mechanical lint cleanup; no behavior change, no new capability. The fix repairs an implicit conformance gap (CI lint job red) but does not change observable behavior of any test or covered code. Alternative `chore:` could also be argued; `refactor:` is preferred because the edits restructure import blocks and statement nesting rather than maintenance-only operations like dependency bumps.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
