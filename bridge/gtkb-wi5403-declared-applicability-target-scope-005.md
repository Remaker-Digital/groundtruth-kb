REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never

# WI-5403 - Revised implementation report with hunk-scoped ownership

bridge_kind: implementation_report
Document: gtkb-wi5403-declared-applicability-target-scope
Version: 005
Responds to: bridge/gtkb-wi5403-declared-applicability-target-scope-004.md
Carries forward implementation report: bridge/gtkb-wi5403-declared-applicability-target-scope-003.md
Approved proposal: bridge/gtkb-wi5403-declared-applicability-target-scope-001.md
Responds to GO: bridge/gtkb-wi5403-declared-applicability-target-scope-002.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5403-DECLARED-TARGET-SCOPE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5403

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]

implementation_scope: source | test | hunk_scoped_finalization
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

This report revision accepts both blocking findings in version 004 and
withdraws every WI-5403 ownership claim over PAUTH-amendment validation.
No source or test byte changed after the NO-GO.

The declared-target-scope feature independently verified as correct in version
004 remains the complete WI-5403 implementation. Terminal verification must
use hunk-scoped finalization for only that feature, leaving WI-5387 operative
version logic and every WI-5408 amendment-validation byte unstaged and
unchanged in the working tree.

This revision does not remove, rewrite, adopt, complete, or validate foreign
work. It does not mutate dispatcher/TAFE configuration or runtime state,
MemBase, claims beyond this drafting claim, Git history, credentials, external
systems, deployments, or releases.

## Resolution Of NO-GO Findings

### Finding 1 - Live PAUTH-amendment false positive

Accepted. `_pauth_amendment_blocking_errors`, its constants/helpers, the
`blocking_errors` packet/Markdown output, and the change making
`preflight_passed` depend on those blocking errors are not WI-5403 work.
They are excluded from this report and from any WI-5403 commit.

WI-5408 owns the canonical repair through
`validate_structured_pauth_spec_amendment` and its realistic no-amendment
regression. WI-5403 makes no correctness or test claim for the currently dirty
candidate implementation.

### Finding 2 - Cross-thread scope conflict

Accepted. WI-5403 finalization is limited to exact declared-target separation.
The finalizer must stage a reviewed hunk patch rather than either whole file.
The current source/test files may remain dirty after WI-5403 finalization;
that is expected evidence that foreign work was preserved, not a failure to
finalize WI-5403.

## Requirement Sufficiency

Existing requirements sufficient.

The approved proposal, active PAUTH, version 004 independent findings, and
existing specification set fully define this finalization correction. No new
requirement or owner waiver is needed because scope is being narrowed back to
the originally approved feature.

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

## Prior Deliberations

- `bridge/gtkb-wi5403-declared-applicability-target-scope-001.md` - approved
  proposal and exact two-target scope.
- `bridge/gtkb-wi5403-declared-applicability-target-scope-002.md` - original
  independent GO.
- `bridge/gtkb-wi5403-declared-applicability-target-scope-003.md` - initial
  implementation report whose PAUTH-adjacent ownership claim is withdrawn.
- `bridge/gtkb-wi5403-declared-applicability-target-scope-004.md` - independent
  NO-GO that validates the core feature and rejects the bundled validator.
- `bridge/gtkb-wi5408-pauth-amendment-owner-evidence-applicability-005.md` -
  corrected GO assigning the amendment-validation repair to WI-5408 and
  requiring a later clean baseline.
- `bridge/gtkb-wi5387-applicability-corrected-go-operative-004.md` - existing
  foreign operative-version work preserved outside this finalization.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`

The mandatory Deliberation Archive search found no decision authorizing
WI-5403 to absorb WI-5408 or WI-5387 work.

## Owner Decisions / Input

`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` and
`PAUTH-DISPATCHER-BLACK-BOX-WI5403-DECLARED-TARGET-SCOPE-20260717` remain the
owner/authorization evidence. They authorize the bounded declared-target
feature and require foreign shared-file bytes to be preserved.

The owner-directed dispatcher configuration/troubleshooter hold remains fully
controlling. This report performs no dispatcher configuration or runtime-state
inspection or mutation.

## Exact WI-5403 Ownership

### Source hunk ownership

Only these logical changes in `scripts/bridge_applicability_preflight.py` are
claimed:

1. `extract_declared_target_paths(content)` parsing only explicit
   `target_paths` metadata;
2. `build_packet` deriving `declared_target_paths` separately from broad
   `applicability_path_evidence`;
3. applicability matching continuing to receive the broad evidence set;
4. packet fields `target_paths` and `declared_target_paths` receiving only the
   declared set, plus `applicability_path_evidence` receiving the broad set;
5. Markdown lines for `declared_target_paths` and
   `applicability_path_evidence`.

### Test hunk ownership

Only these two tests in
`platform_tests/scripts/test_bridge_applicability_preflight.py` are claimed:

- `test_declared_target_paths_exclude_incidental_applicability_evidence`;
- `test_packet_separates_declared_scope_from_applicability_path_evidence`.

### Explicit exclusions

The WI-5403 hunk patch must exclude:

- `OPERATIVE_REFERENCE_RE`, corrected GO/VERIFIED selection,
  `_operative_reference_versions`, `_write_bridge_version`, and their
  NO-ACTION/WITHDRAWN tests, which belong to WI-5387;
- `PAUTH_AMENDMENT_SPEC_ID`, `OWNER_EVIDENCE_RE`, `JSON_FENCE_RE`,
  `_load_json_fence`, `_current_pauth_specs`,
  `_pauth_amendment_blocking_errors`, its `build_packet` call,
  `blocking_errors` packet/Markdown output, and the corresponding
  `preflight_passed` condition, which are not WI-5403 and remain for WI-5408
  disposition;
- any other working-tree or bridge file.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5403; PAUTH-DISPATCHER-BLACK-BOX-WI5403-DECLARED-TARGET-SCOPE-20260717; bridge/gtkb-wi5403-declared-applicability-target-scope-004.md",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; GOV-WORK-TREE-HYGIENE-001; DCL-PROJECT-DEPENDENCY-ORDERING-001",
  "primary_route": "Hunk-finalize only declared target-scope separation while preserving every foreign shared-file byte.",
  "before_behavior": "The initial report bundled a correct declared-target feature with an out-of-scope and defective PAUTH-amendment validator.",
  "after_behavior": "WI-5403 terminal evidence and commit contain only the declared-target feature; foreign WI-5387 and WI-5408 bytes remain uncommitted and independently governed.",
  "self_descriptive_naming": "declared_target_paths and applicability_path_evidence distinguish mutation scope from conservative evidence.",
  "obsolete_guidance_disposition": "The version-003 claim that minimal PAUTH validation was WI-5403 preservation work is withdrawn.",
  "history_preservation": "All prior bridge versions remain append-only; foreign working-tree bytes remain untouched; the terminal commit exposes the exact WI-5403 staged hunk set.",
  "baseline": {
    "source_sha256": "f88c46da39e36ac33fd47b7fc73284ef19453d6034dba810091686619b5fbcf2",
    "test_sha256": "df9478795918c64cf4574557f82aa5e6794cb1abf549b17797fb806c678b74bf",
    "working_tree": "two shared files dirty with separable WI-5387, WI-5403, and WI-5408 ownership"
  },
  "expected_result": {
    "wi5403_commit_scope": "exact source and two-test hunks only",
    "foreign_worktree_state": "preserved and still dirty after focused finalization",
    "declared_scope_behavior": "exact declared targets remain separate from conservative applicability path evidence"
  },
  "rollback": {
    "instructions": "Revert only the focused WI-5403 commit; do not reset either shared working-tree file.",
    "verification": "The two WI-5403 tests disappear while foreign WI-5387/WI-5408 bytes remain unchanged."
  },
  "hard_invariants": [
    "No whole-file staging for either target.",
    "No PAUTH-amendment validator byte enters the WI-5403 commit.",
    "No WI-5387 operative-version byte enters the WI-5403 commit.",
    "No foreign working-tree byte is removed, reformatted, or rewritten.",
    "No dispatcher, TAFE, harness, configuration, runtime-state, database, credential, external, deployment, release, or push action occurs."
  ],
  "fail_closed_conditions": [
    "The current source or test hash changes before finalization.",
    "The hunk patch touches any explicit exclusion.",
    "The disposable-index staged diff contains a path other than the two targets and the new VERIFIED verdict.",
    "The staged diff omits either declared-target test or any claimed source behavior.",
    "Focused tests, Ruff, format, diff-check, applicability preflight, or mandatory clause preflight fails."
  ],
  "essential_context_preservation": "The terminal verdict must record the current whole-file hashes, exact hunk patch, staged diff, two focused tests, foreign-byte exclusions, and expected post-commit dirty shared-file state."
}
```

## Specification-Derived Verification

| Specification / invariant | Executed or required evidence | Result / required result |
|---|---|---|
| Declared-target behavior; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the two exact WI-5403 tests by node ID. | Both pass; declared mutation scope is separate while conservative applicability evidence remains active. |
| `GOV-WORK-TREE-HYGIENE-001`; `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Review `git diff --unified=2` and the final hunk patch against the explicit ownership/exclusion lists. | No WI-5387 or WI-5408 line is staged. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the focused file, Ruff check, Ruff format check, `py_compile`, and `git diff --check` on both targets. | All pass; broader shared-file failures, if any, are attributed to their owning thread rather than hidden. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Independent LO uses `write_verdict.py --finalize-verified --hunk-patch` and a disposable index. | VERIFIED verdict and exact WI-5403 hunks commit atomically; foreign bytes remain unstaged. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Re-read PAUTH, project, WI, and exact targets. | Active authorization remains bounded to WI-5403 and the two shared paths. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Inspect final staged paths. | Every path is inside E:/GT-KB and no adopter path is present. |

## Commands Re-Executed For This Revision

Executed from `E:/GT-KB` on 2026-07-18 UTC:

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_applicability_preflight.py::test_declared_target_paths_exclude_incidental_applicability_evidence platform_tests\scripts\test_bridge_applicability_preflight.py::test_packet_separates_declared_scope_from_applicability_path_evidence -q --tb=short`
  - PASS: 2 passed in 0.32s; one pre-existing unknown-`asyncio_mode` configuration warning.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_applicability_preflight.py -q --tb=short`
  - PASS: 33 passed in 1.07s; the same pre-existing warning.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\bridge_applicability_preflight.py platform_tests\scripts\test_bridge_applicability_preflight.py`
  - PASS: all checks passed.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\bridge_applicability_preflight.py platform_tests\scripts\test_bridge_applicability_preflight.py`
  - PASS: both files already formatted.
- `groundtruth-kb\.venv\Scripts\python.exe -m py_compile scripts\bridge_applicability_preflight.py platform_tests\scripts\test_bridge_applicability_preflight.py`
  - PASS.
- `git diff --check -- scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py`
  - PASS.
- SHA-256:
  - `scripts/bridge_applicability_preflight.py`: `f88c46da39e36ac33fd47b7fc73284ef19453d6034dba810091686619b5fbcf2`
  - `platform_tests/scripts/test_bridge_applicability_preflight.py`: `df9478795918c64cf4574557f82aa5e6794cb1abf549b17797fb806c678b74bf`

## Pre-Filing Preflight Subsection

Both mandatory candidate preflights were run against this completed report:

- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi5403-declared-applicability-target-scope-005.md`
  - PASS: `preflight_passed: true`, no missing required or advisory
    specifications, and no blocking errors.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi5403-declared-applicability-target-scope-005.md`
  - PASS: five clauses evaluated, four `must_apply`, zero evidence gaps, and
    zero blocking gaps.

## Acceptance Criteria Status

- PASS: the declared-target split is correctly implemented.
- PASS: conservative applicability matching remains on broad path evidence.
- PASS: the exact WI-5403 ownership map is now explicit.
- PASS: all PAUTH-amendment ownership is withdrawn.
- PASS: all WI-5387 ownership remains explicitly excluded.
- PENDING independent verification: exact hunk patch and atomic focused commit.

## Risk And Rollback

Risk is limited to finalization construction over shared files. Whole-file
staging would misattribute foreign work; the hunk patch and disposable-index
staged diff are therefore mandatory fail-closed controls.

Rollback is a later governed revert of only the focused WI-5403 commit. It must
not reset, checkout, clean, or otherwise alter the shared working-tree files or
their foreign bytes.

## Recommended Commit Type

`feat(bridge)` for the declared-target scope separation only.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
