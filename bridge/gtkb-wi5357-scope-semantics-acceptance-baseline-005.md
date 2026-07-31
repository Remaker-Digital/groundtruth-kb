REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; build envelope active
author_metadata_source: explicit_interactive_session_metadata

# Revised Proposal - WI-5357 Scope-Semantics Acceptance Baseline

bridge_kind: prime_proposal
Document: gtkb-wi5357-scope-semantics-acceptance-baseline
Version: 005
Responds to: bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-004.md
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5357
target_paths: ["scripts/check_modernization_scope_semantics.py", "platform_tests/scripts/test_modernization_scope_semantics.py", "platform_tests/scripts/test_modernization_harness_assurance_clause_exactness.py", "platform_tests/scripts/test_modernization_repository_interface_clause_exactness.py"]
implementation_scope: test | provenance_closure
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: test

## Revision Claim

This revision resolves the version-004 format-gate conflict by replacing the
obsolete exact-byte target table from version 001 with the formatter-clean byte
images now present in committed `HEAD` `42a252ab57b5a203e9406b626c741d897e8fb196`
(`chore(gtkb): sweep governable platform work`).

No source or test file is changed by this revision. The four WI-5357 target
paths are now tracked, clean, and formatter-compliant at `HEAD`. The requested
follow-on action is therefore provenance closure over the committed formatted
baseline: after independent `GO`, Prime Builder should file a report that
re-verifies the exact committed byte images and states that no additional
target mutation was performed. If any target drifts before report filing, Prime
Builder must stop and revise again with fresh hashes rather than silently
absorbing the drift.

## Response To Version 004 NO-GO

Version 004 correctly rejected the previous `GO` because the proposal required
the original four target hashes to remain exact while the mandatory
`ruff format --check` gate required formatting normalization in
`platform_tests/scripts/test_modernization_repository_interface_clause_exactness.py`.

This revision makes the normalization explicit and reviewable:

- The fourth target's approved byte image changes from the version-001
  28,089-byte hash to the current formatter-clean 28,039-byte hash listed
  below.
- The other three target hashes remain unchanged from version 001.
- All four targets are tracked and clean at `HEAD`.
- `ruff check` and `ruff format --check` now both pass for the four-target set.
- The proposal no longer asks Prime Builder to preserve an unformatted byte
  image that violates the mandatory format gate.

## Current Baseline Candidate

| Path | Bytes | SHA-256 | Git blob |
| --- | ---: | --- | --- |
| `scripts/check_modernization_scope_semantics.py` | 53,258 | `49FB96512D4CB5778C96B585E248D1D942E7FC703E88FED356715A1554812247` | `d6ff8ca5d8171eaf2a8ee43ef9438daffb618700` |
| `platform_tests/scripts/test_modernization_scope_semantics.py` | 13,425 | `683FCF9A3B1770FD6DF55FD9880AB8A70C91438CA782BA35E456F7363349AEF6` | `e545cb4e1c5c2ebd1becb8f8621c5e416db8cfeb` |
| `platform_tests/scripts/test_modernization_harness_assurance_clause_exactness.py` | 27,231 | `05B4E04197E085248C17846EB766F714CC1ADFD90F37AF21D55D2864F0333914` | `55959ab2981b43c406b1ddcfe1e2eeb081ac097d` |
| `platform_tests/scripts/test_modernization_repository_interface_clause_exactness.py` | 28,039 | `6FB228143F59AFB5341BEAD0DC413825E2BAB6F85A82E14D9DD8D284EAEFAC13` | `247c9f53ca346ab8d88dd5dc858a518bb825175e` |

`git status --short -- <four targets>` produces no output. `git ls-files
--error-unmatch <four targets>` resolves all four paths. The newest commit
touching the four target paths is `42a252ab chore(gtkb): sweep governable
platform work`, which added the four formatted baseline files.

## Scope Changes

- Version 001 proposed preserving four then-untracked byte images exactly.
- Version 005 instead proposes accepting the current formatter-clean committed
  byte images as the WI-5357 baseline.
- No additional target paths are added.
- No source behavior, receipt, manifest, timeout, dispatcher, database, PAUTH,
  credential, release, deployment, or external-system mutation is authorized.
- Any post-GO report is report-only unless a fresh implementation-start packet
  is required by tooling to prove scope; in either case, no target byte may be
  changed under this revision without a new bridge revision.

## Requirement Sufficiency

Existing requirements remain sufficient. The linked work-tree hygiene,
mechanical enforcement, non-impairment, evaluability, bridge authority, and
spec-derived verification requirements require formatter-compliant, exact,
reviewed acceptance artifacts. No new formal requirement or owner waiver is
introduced by this revision.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-202666274` - owner authorization for modernization assurance work,
  while retaining bridge review, independent verification, exact mechanical
  gates, and no hidden waiver of formatting requirements.
- `bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-001.md` - original
  exact-byte baseline proposal.
- `bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-003.md` - Prime
  fail-closed disposition identifying the format-gate conflict.
- `bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-004.md` - Loyal
  Opposition NO-GO requiring a revision that authorizes formatting
  normalization and publishes corrected hashes.

## Owner Decisions / Input

No new owner decision is required. The revision narrows ambiguity by replacing
the unformatted exact-byte candidate with a formatter-compliant committed
candidate. It does not request a waiver of the mandatory format gate and does
not broaden the Assurance project authorization.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666274; bridge/gtkb-wi5357-scope-semantics-acceptance-baseline-004.md",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python scripts/check_modernization_scope_semantics.py validate",
  "before_behavior": "The WI-5357 bridge chain approved an exact unformatted byte image that could not satisfy the mandatory Ruff format gate.",
  "after_behavior": "The WI-5357 bridge chain can review the formatter-clean committed byte image and close provenance without changing scope-semantics behavior.",
  "self_descriptive_naming": "The revision names the formatter-clean HEAD baseline and publishes current hashes instead of relying on stale exact-byte language.",
  "obsolete_guidance_disposition": "The version-001 fourth-file hash remains historical evidence only and is superseded by this reviewed formatter-clean hash.",
  "history_preservation": "Prior bridge files are append-only; the current HEAD commit and exact target hashes are cited as evidence.",
  "baseline": {
    "target_count": 4,
    "binding_count": 94,
    "focused_tests_passed": 11,
    "clause_exact_cases": 56,
    "format_gate": "pass"
  },
  "expected_result": {
    "target_count": 4,
    "byte_changes_after_go": 0,
    "binding_count": 94,
    "clause_exact_cases": 56,
    "git_scope_path_count": 4
  },
  "rollback": "If review rejects this provenance closure, no target rollback is performed by this thread; future correction is append-only bridge revision or a separately governed revert of commit 42a252ab.",
  "hard_invariants": [
    "the four target hashes and lengths remain exact from this revision through the implementation report",
    "the four targets remain tracked and clean at HEAD",
    "the frozen manifest remains unchanged",
    "no receipt is created or rewritten",
    "no WI-5260 addition is included",
    "no fifth Git path is attributed to WI-5357"
  ],
  "fail_closed_conditions": [
    "target hash or length changes",
    "target becomes dirty before report filing",
    "94-handle validation fails",
    "clause-exact collection is not 56 cases",
    "Ruff check or format check fails",
    "Git scope includes any fifth path"
  ],
  "essential_context_preservation": "All 94 frozen handles, existing broad proofs, 56 clause-exact cases, observed failures, and root-containment rules remain present and queryable."
}
```

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Exact-byte evaluability and work-tree hygiene | `Get-FileHash -Algorithm SHA256`, file lengths, `git hash-object`, `git status --short -- <four targets>`, and `git ls-files --error-unmatch <four targets>` | Hashes and lengths match this revision; all four paths are tracked and clean. |
| Frozen binding enforcement | `python scripts/check_modernization_scope_semantics.py validate` | `MODERNIZATION SCOPE SEMANTICS: PASS` for 94 bindings. |
| Baseline focused regressions | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_modernization_scope_semantics.py -q --tb=short --timeout=180` | 11 passed. |
| Clause-exact evaluability | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_modernization_harness_assurance_clause_exactness.py platform_tests/scripts/test_modernization_repository_interface_clause_exactness.py --collect-only -q` | 56 tests collected. |
| Mandatory Python quality gates | `groundtruth-kb\.venv\Scripts\python.exe -m ruff check <four targets>` and `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check <four targets>` | Both pass. |
| Non-impairment and provenance closure | Re-read `HEAD`, the four target hashes, and the bridge chain immediately before report filing | No target byte changes after this revision; report states whether closure is over already-committed bytes. |

Read-only checks executed before filing this revision:

- `python scripts/check_modernization_scope_semantics.py validate` - `MODERNIZATION SCOPE SEMANTICS: PASS`.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_modernization_scope_semantics.py -q --tb=short --timeout=180` - 11 passed in 21.10 seconds.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_modernization_harness_assurance_clause_exactness.py platform_tests/scripts/test_modernization_repository_interface_clause_exactness.py --collect-only -q` - 56 tests collected in 0.77 seconds.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check <four targets>` - all checks passed.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check <four targets>` - 4 files already formatted.

## Pre-Filing Preflight Subsection

The `revise_bridge.py file` helper will run the candidate-content applicability
preflight and mandatory ADR/DCL clause preflight with `--content-file` before
publishing this version. The completed revision carries the required
specification links, project linkage metadata, owner-decision section, and
specification-derived verification mapping.

## Acceptance Criteria

1. Loyal Opposition can review current formatter-clean hashes rather than the
   obsolete unformatted fourth-file hash.
2. The four target paths remain tracked and clean at `HEAD`.
3. The mandatory `ruff check` and `ruff format --check` gates pass.
4. The scope-semantics validator still passes for 94 bindings.
5. The clause-exact collection count remains 56.
6. Any later report is honest that no source/test mutation occurred after this
   revision unless fresh drift forces a new proposal.

## Risk And Rollback

The main risk is retroactive provenance confusion because the target files were
committed by an intervening sweep commit before this revision. This proposal
does not hide that fact: it cites commit `42a252ab`, makes the follow-on report
path provenance-only, and requires fresh hash/status checks before any report.

Rollback is not a broad reset. If this closure path is rejected, the bridge
thread remains append-only and a later correction can either supersede this
proposal or route a separately governed revert of the four files from
`42a252ab`. No deployment, release, credential, database, dispatcher, TAFE, or
external-system action is in scope.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
