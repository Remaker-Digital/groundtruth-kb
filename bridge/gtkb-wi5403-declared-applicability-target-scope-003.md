NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: 5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never

# GT-KB Bridge Implementation Report - gtkb-wi5403-declared-applicability-target-scope - 003

bridge_kind: implementation_report
Document: gtkb-wi5403-declared-applicability-target-scope
Version: 003 (NEW; post-implementation report)
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5403-DECLARED-TARGET-SCOPE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5403

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]

Responds to GO: bridge/gtkb-wi5403-declared-applicability-target-scope-002.md
Approved proposal: bridge/gtkb-wi5403-declared-applicability-target-scope-001.md
Recommended commit type: feat:

## Summary

Implemented WI-5403 declared target-scope separation in the bridge applicability preflight. The preflight now reports exact declared mutation scope separately from the broader normalized path evidence used to compute conservative specification applicability, so incidental prose citations no longer inflate the implementation target inventory.

The implementation preserves conservative path-driven applicability matching, packet hashing, missing-parent warning behavior, corrected operative-version handling after `NO-ACTION`, and existing project-authorization amendment owner-evidence validation behavior in the shared file. No MemBase mutation, dispatcher/TAFE mutation, lease mutation outside the work-intent claim, Git commit/push/history operation, release, deployment, credential lifecycle action, or destructive cleanup was performed.

## Implementation Claim

- Latest bridge status before implementation/reporting: `GO` at `bridge/gtkb-wi5403-declared-applicability-target-scope-002.md`.
- Work-intent claim: `go_implementation`, rowid `32154`, session `019f6668-9974-7d72-a456-826f9a67e627`, acquired `2026-07-17T11:48:45Z`, extended once, TTL/grace through `2026-07-17T12:58:45Z` at implementation time.
- Implementation-start packet created `2026-07-17T11:49:03Z`; pre-start packet hash `sha256:65c72e0c33dfec79021761e78ab06413b9be77b9ab314f846bbdfef180f5dc05`; packet hash `sha256:360cef5accd1ffab9863e5a5497398f6f4359e04494fa23ca1d0cd8ad4602364`.
- Implementation stayed inside the two approved target paths: `scripts/bridge_applicability_preflight.py` and `platform_tests/scripts/test_bridge_applicability_preflight.py`.

## Foreign Work Disclosure

Both authorized target files were already dirty before WI-5403 implementation began. The pre-existing hunks included operative-version handling for corrected `GO`/`VERIFIED` after `NO-ACTION` and tests covering `NO-ACTION` bridge version ordering. The test file also already contained PAUTH amendment owner-evidence validation expectations while the source file lacked the corresponding implementation.

This report claims only the WI-5403 declared-target split, the focused regression tests for that split, the minimal shared PAUTH owner-evidence validation needed to preserve the existing test contract and WI-5408-adjacent behavior called out by the approved proposal, and mechanical Ruff formatting of the two authorized files. It does not claim ownership of the pre-existing `NO-ACTION` operative-version hunks.

## Files Changed

- `scripts/bridge_applicability_preflight.py`
  - Added `extract_declared_target_paths()` to parse only declared `target_paths` metadata from JSON code fences.
  - Kept conservative applicability matching on broad normalized cited path evidence via `extract_target_paths()`.
  - Updated packet output to expose `target_paths` and `declared_target_paths` as exact declared mutation scope while exposing prose-derived evidence as `applicability_path_evidence`.
  - Updated Markdown output to show declared target scope, applicability path evidence, and blocking errors separately.
  - Added minimal PAUTH amendment owner-evidence `blocking_errors` validation for existing shared-file test expectations.
- `platform_tests/scripts/test_bridge_applicability_preflight.py`
  - Added coverage proving incidental applicability prose paths are excluded from declared mutation scope.
  - Added packet-level coverage proving broad applicability evidence still drives conservative spec matching while declared scope remains exact.
  - Preserved and passed existing PAUTH owner-evidence and `NO-ACTION` operative-version tests.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner-decision evidence cited by the active project authorization.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5403-DECLARED-TARGET-SCOPE-20260717` - active project authorization for `WI-5403` and the exact two target paths.
- Owner previously approved finalizing or clearing foreign work in the shared applicability preflight files; this report still limits its ownership claim to the WI-5403 split and the minimal shared preservation work described above.
- No new owner decision, waiver, credential action, release, deployment, destructive cleanup, or Git history operation is requested by this implementation report.

## Prior Deliberations

- `bridge/gtkb-wi5403-declared-applicability-target-scope-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5403-declared-applicability-target-scope-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `DELIB-20260710-GTKB-MODERNIZATION-GIT-AUTHORITY-TRANSITION-COMPLETION` - carried forward from the approved proposal as relevant Git authority context.

## Spec-To-Test Mapping

| Spec | Evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Thread state remained latest `GO`; this Prime-authored `NEW` implementation report is version `003` and responds to LO GO `-002`; work-intent claim and implementation-start packet were created before mutation. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | This report preserves implementation claim, owner/PAUTH evidence, linked specs, target inventory, command evidence, observed results, residual risk, rollback, and LO asks as durable bridge evidence. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python .codex\skills\bridge\helpers\impl_report_bridge.py plan gtkb-wi5403-declared-applicability-target-scope --compact` carried forward the approved linked specification set and reported next version `003`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests\scripts\test_bridge_applicability_preflight.py -q --tb=short` passed `33 passed in 0.64s`, including the new declared-scope split tests and existing shared PAUTH/NO-ACTION tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report includes Project Authorization, Project, Work Item, `target_paths`, owner evidence, and implementation-start packet hashes for the exact authorized scope. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Owner/PAUTH evidence is explicitly listed; the PAUTH amendment validation path checks owner approval packet shape and coverage before accepting authorization-envelope amendment claims. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed paths are in-root GT-KB platform script/test paths; no Agent Red, adopter application, or out-of-root path is involved. |
| `GOV-STANDING-BACKLOG-001` | Work is bound to `WI-5403` under the dispatcher black-box hardening project; this report makes the bridge thread LO-actionable rather than silently resolving backlog state. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Codex self-enforced implementation authorization through `scripts\implementation_authorization.py begin` and work-intent claim status; compile, Ruff, format, diff-check, and pytest ran under the Codex/Windows execution surface. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The implementation removes a false-closure artifact shape by separating declared mutation targets from applicability evidence and preserving both as durable packet fields. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The lifecycle advances from approved proposal `GO` to implementation report `NEW`, awaiting independent LO verification; no Prime-authored terminal claim is made. |
| `GOV-WORK-TREE-HYGIENE-001` | `git diff --check -- scripts\bridge_applicability_preflight.py platform_tests\scripts\test_bridge_applicability_preflight.py` exited 0 with no output; out-of-scope dirty work was not adopted by this claim. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Conservative applicability behavior remains intact because specification matching still uses broad path evidence; only the declared mutation inventory is narrowed. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `python scripts\implementation_authorization.py begin --bridge-id gtkb-wi5403-declared-applicability-target-scope --session-id 019f6668-9974-7d72-a456-826f9a67e627` produced an active packet for only the two authorized target paths. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | The implementation preserves existing shared-file behavior and discloses foreign hunks instead of treating adjacent nonterminal work as terminal WI-5403 ownership. |

## Commands Executed

```powershell
python scripts\bridge_claim_cli.py status gtkb-wi5403-declared-applicability-target-scope
```

Observed result: exit 0; claim kind `go_implementation`, rowid `32154`, session `019f6668-9974-7d72-a456-826f9a67e627`, latest bridge status `GO`, extended once, `expired: false`.

```powershell
python scripts\implementation_authorization.py begin --bridge-id gtkb-wi5403-declared-applicability-target-scope --session-id 019f6668-9974-7d72-a456-826f9a67e627
```

Observed result: exit 0; implementation-start packet created with packet hash `sha256:360cef5accd1ffab9863e5a5497398f6f4359e04494fa23ca1d0cd8ad4602364`; pre-start packet hash `sha256:65c72e0c33dfec79021761e78ab06413b9be77b9ab314f846bbdfef180f5dc05`.

```powershell
python -m py_compile scripts\bridge_applicability_preflight.py platform_tests\scripts\test_bridge_applicability_preflight.py
```

Observed result: exit 0.

```powershell
python -m ruff check scripts\bridge_applicability_preflight.py platform_tests\scripts\test_bridge_applicability_preflight.py
```

Observed result: exit 0; `All checks passed!`.

```powershell
python -m ruff format scripts\bridge_applicability_preflight.py platform_tests\scripts\test_bridge_applicability_preflight.py
python -m ruff format --check scripts\bridge_applicability_preflight.py platform_tests\scripts\test_bridge_applicability_preflight.py
```

Observed result: format applied to the two authorized files; subsequent format-check exited 0 with `2 files already formatted`.

```powershell
python -m pytest platform_tests\scripts\test_bridge_applicability_preflight.py -q --tb=short
```

Observed result after formatting: exit 0; `33 passed in 0.64s`.

```powershell
git diff --check -- scripts\bridge_applicability_preflight.py platform_tests\scripts\test_bridge_applicability_preflight.py
```

Observed result: exit 0; no output.

## Candidate Preflight Evidence

- Candidate applicability preflight: `python scripts\bridge_applicability_preflight.py --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-wi5403-declared-applicability-target-scope-003.md --json` exited 0; `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; `blocking_errors: []`; packet hash `sha256:2b100d6282b93dd6515c7f47ee6396aafe64a0466e278ef140bf5ca09a618a10`.
- Candidate ADR/DCL clause preflight: `python scripts\adr_dcl_clause_preflight.py --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-wi5403-declared-applicability-target-scope-003.md` exited 0; clauses evaluated `5`; evidence gaps in must-apply clauses `0`; blocking gaps `0`.
- Live preflights will be rerun after the helper writes `bridge/gtkb-wi5403-declared-applicability-target-scope-003.md`.

## Acceptance Criteria Result

- `target_paths` in JSON packet and Markdown output reflect exact declared mutation scope, not incidental prose path evidence: PASS. New focused tests cover this split directly.
- Conservative path-driven applicability remains intact for cited/prose paths: PASS. The packet preserves `applicability_path_evidence`, and tests prove prose evidence can still trigger path-scoped applicability without inflating declared targets.
- Packet hashing and Markdown report behavior remain available with explicit separated fields: PASS. Candidate and live preflights are run through the same applicability tool before and after filing.
- Existing shared behaviors for missing-parent warnings, operative-version handling after `NO-ACTION`, and PAUTH amendment owner-evidence validation remain covered: PASS. The focused test file passed all 33 tests.
- Focused tests pass with no source/test path outside the two approved files: PASS. `impl_report_bridge.py plan --compact` reported two changed files and 1508 excluded dirty paths.

## Residual Risk

Residual risk is moderate because `target_paths` now intentionally narrows to declared mutation scope and downstream consumers that historically treated `target_paths` as mixed declared-plus-cited evidence must migrate to `applicability_path_evidence`. WI-5403 makes that separation explicit to avoid false closure and scope inflation. Applicability itself remains conservative because it still runs on the broad evidence set.

The overall black-box bridge/TAFE/harness program is not claimed terminal by this report. WI-5403 only corrects one applicability-preflight artifact shape and then returns the thread for independent Loyal Opposition verification.

## Rollback

Rollback is a normal revert of the WI-5403 hunks in:

- `scripts/bridge_applicability_preflight.py`
- `platform_tests/scripts/test_bridge_applicability_preflight.py`

Bridge files, claim records, implementation-start packets, and project authorization evidence are append-only audit artifacts and must not be deleted as rollback.

## Recommended Commit Type

Recommended commit type: `feat:`. This implementation changes the applicability preflight contract by separating declared mutation targets from applicability evidence while preserving conservative matching behavior.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
