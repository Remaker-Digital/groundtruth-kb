NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# GT-KB Bridge Implementation Report - gtkb-wi5554-lo-verdict-candidate-preflight - 005

bridge_kind: implementation_report
Document: gtkb-wi5554-lo-verdict-candidate-preflight
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5554-lo-verdict-candidate-preflight-004.md
Approved proposal: bridge/gtkb-wi5554-lo-verdict-candidate-preflight-003.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5554
Recommended commit type: fix:

## Implementation Claim

Implemented the approved narrow freshness mechanism in both byte-identical
bridge-compliance hook copies and added the exact focused test carrier.

For a `GO`, `NO-GO`, or `VERIFIED` candidate that carries `## Applicability
Preflight`, the hook now:

- resolves the exact root-contained `Responds to` artifact and requires it to
  be an existing version of the same bridge thread;
- requires `bridge_document_name` and `content_file` (or legacy
  `operative_file`) to identify that exact source;
- reruns `scripts.bridge_applicability_preflight.build_packet` against the
  source and compares the embedded packet hash; and
- validates `candidate_evidence_hash` over the normalized repository-relative
  candidate path, one LF, and LF-normalized candidate bytes with only that
  field's value replaced by `<CANDIDATE_EVIDENCE_HASH>`.

`PENDING_PREFLIGHT_STATUSES` remains exactly `{"NEW", "REVISED"}`.
`NO-GO` without an applicability section remains valid, and the freshness
helper accepts valid `GO` and `VERIFIED` shapes without adding a verdict-level
`Specification Links` requirement.

The implementation is not verification-ready because one required adjacent
legacy fixture outside this PAUTH's exact target set still asserts the old
passing-shaped packet contract. The production gate correctly denies that
fixture for missing `Responds to` and freshness anchors. This report asks for
an independent bounded `NO-GO` so Prime Builder can revise the proposal to add
only that stale fixture path; no production weakening or unauthorized test
mutation occurred.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

No new owner decision is required. The implementation remains within
`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` and
`PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-20260718`.
The owner-directed dispatcher-configuration hold was preserved; no dispatcher,
TAFE, harness, lease, worker, provider, credential, Git publication,
deployment, release, or unrelated worktree state was mutated.

## Prior Deliberations

- `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-003.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-004.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`; `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Focused suite proves wrong source/thread/version, stale packet, and one-byte final-candidate mutation fail closed in both hook copies; `23 passed`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Focused suite proves valid `GO`/`VERIFIED` freshness without verdict-level `Specification Links`, and both valid `NO-GO` forms; `23 passed`. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`; `ADR-CROSS-HARNESS-PARITY-001`; `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Active/template SHA-256 both `50AEED9C1D3AAF7DA866F59F60B2DEB265F6E158F95A6328A2CEA6B762EB29D3`; focused cases are parameterized over both copies. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Latest v004 remained `GO`; exact rowid `33266` claim held by this session; schema-v3 packet remained live; all three operation-time target validations returned `authorized: true`. |
| `GOV-WORK-TREE-HYGIENE-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `impl_report_bridge.py plan --compact` found exactly three changed in-scope files and excluded 1,867 unrelated dirty paths; `git diff --check`, Ruff, format, and `py_compile` pass. |
| `DCL-NO-ACTION-STATUS-SEMANTICS-001`; `SPEC-AUQ-POLICY-ENGINE-001`; artifact-oriented authorities | No status semantics, AUQ behavior, artifact lifecycle, dispatcher state, or unrelated canonical artifact was modified. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py platform_tests/scripts/test_bridge_compliance_gate_disposition.py platform_tests/hooks/test_bridge_compliance_gate_envelope_head.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/ruff.exe check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`
- `groundtruth-kb/.venv/Scripts/ruff.exe format --check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m py_compile .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`
- `git diff --check -- .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`
- SHA-256 comparison of the active and packaged hook copies.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5554-lo-verdict-candidate-preflight`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5554-lo-verdict-candidate-preflight`

## Observed Results

- Focused WI-5554 suite: `23 passed`.
- Required adjacent regression set: `162 passed, 1 failed`.
- The sole failure is
  `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py::test_go_with_clean_applicability_preflight_passes`.
  Its fixture has only a syntactically shaped packet hash and
  `missing_required_specs: []`; it omits `Responds to`,
  `bridge_document_name`, source-file anchors, and
  `candidate_evidence_hash`. The new gate correctly denies it before
  publication. That test file is outside the exact three-target PAUTH and
  implementation-start packet, so it was not changed.
- Ruff check: pass.
- Ruff format check: pass after formatting the two authorized hook copies.
- `py_compile`: pass.
- `git diff --check`: pass; one Git EOL advisory only.
- Active/template hook parity: pass, byte-identical.
- Applicability preflight for approved proposal v003: pass with
  `missing_required_specs: []`.
- Clause preflight against the current latest LO GO v004 reports one
  `GOV-STANDING-BACKLOG-001` evidence-pattern gap because the GO text itself
  discusses a review packet. This does not invalidate the already-issued GO
  or change implementation scope, but it is disclosed for independent review.

## Files Changed

- `.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- `platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`

Excluded out-of-scope dirty paths: 1867.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: the change repairs a concrete governed verdict
  evidence-freshness defect and adds its focused regression carrier.

```text
     .claude/hooks/bridge-compliance-gate.py            | 159 +++++++++++++++++++++
     .../templates/hooks/bridge-compliance-gate.py      | 159 +++++++++++++++++++++
     2 files changed, 318 insertions(+)
```

## Acceptance Criteria Status

- [x] Wrong source/thread/version evidence is denied in both hook copies.
- [x] Embedded packet hash is mechanically recomputed from the exact source.
- [x] One-byte final candidate mutation is denied with the expected hash.
- [x] Valid `GO` and freshness-valid `VERIFIED` shapes do not gain a new
  verdict-level `Specification Links` requirement.
- [x] `NO-GO` without applicability remains valid; a present section is
  freshness-checked.
- [x] Active/template bytes are identical and `PENDING_PREFLIGHT_STATUSES`
  remains `{"NEW", "REVISED"}`.
- [ ] The full required adjacent suite is green. One stale legacy fixture
  outside authorized scope must be revised under a widened exact target set.

## Risk And Rollback

Residual risk is bounded to the stale legacy fixture and the disclosed
current-GO clause-preflight false-positive. Production behavior is fail-closed;
no bypass was added.

Rollback, only under separate authority, is to revert the focused WI-5554
hunks from the two byte-identical hooks and remove the focused WI-5554 test,
then rerun the same focused/adjacent suite, parity, Ruff, format, compile, and
diff checks. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Independently confirm the narrow mechanism and `23 passed` focused evidence.
2. Return bounded `NO-GO` because the required adjacent suite is `162 passed,
   1 failed` and the stale fixture is outside the current exact target set.
3. Scope the finding to adding only
   `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`
   to a revised proposal/PAUTH/start packet and updating
   `test_go_with_clean_applicability_preflight_passes` to construct the new
   source-bound, candidate-bound clean packet. Do not request weakening the
   production freshness gate.
