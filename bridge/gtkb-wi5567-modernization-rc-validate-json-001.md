NEW
::init gtkb lo
::open build

# WI-5567 Modernization RC Validate JSON Contract

bridge_kind: prime_proposal
Document: gtkb-wi5567-modernization-rc-validate-json
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-18T17:32:18Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5567

target_paths: ["scripts/check_modernization_release_candidate.py", "platform_tests/scripts/test_modernization_release_candidate.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Add a backward-compatible `--json` option to the modernization
release-candidate checker's `validate` subcommand and cover it with focused
CLI tests. The existing plain `validate` command continues to emit its current
human-readable PASS line. The JSON form emits deterministic machine-readable
validation evidence including the unchanged frozen scope digest, capability
count, handle count, and validation result.

The repair aligns the production CLI with canonical RC evidence that invokes
`validate --json`. It does not modify the frozen manifest, change its digest,
record release evidence, run a release, or alter dispatcher, TAFE, harness,
credential, deployment, or external-system state.

## Specification Links

- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - requires release-readiness
  evidence to be deterministic, executable, and governed rather than a prose
  claim.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires the canonical RC
  checker and its evidence interface to fail closed and remain directly
  evaluable.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires JSON automation support
  without impairing the existing human-readable command or frozen contract.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves independent proposal review,
  claim/start, implementation reporting, and VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - binds the exact
  checker and test changes to these requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds the two-file
  repair to WI-5567 and the active modernization assurance PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires both success
  forms and invalid-manifest failure behavior to be executed before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - recognizes WI-5567 and TEST-11619 as the durable
  hygiene record for the discovered RC audit-interface defect.

## Prior Deliberations

- `DELIB-202666274` - provides active project-level modernization assurance
  authority while retaining independent bridge review, claim/start, testing,
  and exact finalization gates.

No additional prior deliberation defines this newly discovered CLI mismatch.
WI-5567 and TEST-11619 are its canonical intake and executable assertion.

## Owner Decisions / Input

No new owner decision is required. The owner directed that discovered flaws
be added to the hygiene backlog and that modernization implementation continue.
The active project PAUTH under `DELIB-202666274` covers source and test work,
while independent GO, matching claim/start, VERIFIED, and exact mechanical
finalization remain mandatory.

## Requirement Sufficiency

Existing requirements sufficient. WI-5567 and TEST-11619 state the exact
compatibility and machine-readable evidence contract, while
`GOV-RELEASE-READINESS-GOVERNED-TESTING-001`,
`DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`, and the frozen manifest
govern the result. No manifest or requirement amendment is needed.

## Spec-Derived Verification Plan

1. `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`,
   `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`, and TEST-11619:

   ```text
   groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_release_candidate.py -q --tb=short
   ```

   Expected: all existing tests plus new assertions for plain validation,
   deterministic JSON validation, unchanged digest/counts, and invalid-manifest
   rejection pass.

2. Human-readable compatibility:

   ```text
   groundtruth-kb/.venv/Scripts/python.exe scripts/check_modernization_release_candidate.py validate
   ```

   Expected: exit 0 and the existing
   `PASS modernization acceptance manifest (8 capabilities, 94 handles)` line.

3. Machine-readable RC evidence:

   ```text
   groundtruth-kb/.venv/Scripts/python.exe scripts/check_modernization_release_candidate.py validate --json
   ```

   Expected: exit 0; stdout parses as deterministic JSON whose result is PASS,
   capability count is 8, handle count is 94, and frozen digest is
   `AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240`.

4. Source quality:

   ```text
   groundtruth-kb/.venv/Scripts/ruff.exe check scripts/check_modernization_release_candidate.py platform_tests/scripts/test_modernization_release_candidate.py
   groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/check_modernization_release_candidate.py platform_tests/scripts/test_modernization_release_candidate.py
   ```

   Expected: both commands pass.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5567; TEST-11619; DELIB-202666274",
  "canonical_authority": "GOV-RELEASE-READINESS-GOVERNED-TESTING-001 and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "governed bridge GO, matching claim/start, focused implementation, independent VERIFIED, and exact two-file finalization",
  "before_behavior": "The plain validate command passes, but validate --json is rejected by argparse and cannot produce the machine-readable RC evidence named by canonical acceptance records.",
  "after_behavior": "Plain validate remains unchanged and validate --json emits deterministic parseable evidence for the same frozen manifest validation.",
  "self_descriptive_naming": "The validate --json option and payload fields directly identify validation result, digest, capabilities, and handles.",
  "obsolete_guidance_disposition": "No active guidance is retired; the repair makes the already named machine-readable invocation executable.",
  "history_preservation": "The frozen manifest, digest, numbered bridge chain, and existing release evidence remain unchanged and append-only.",
  "baseline": {
    "plain_validate": "pass",
    "json_validate": "argument-parse-failure",
    "frozen_contract_sha256": "AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240"
  },
  "expected_result": {
    "plain_validate": "same PASS line",
    "json_validate": "deterministic JSON PASS payload",
    "frozen_contract_sha256": "AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240"
  },
  "rollback": {
    "instructions": "Under separate exact authority, revert only the checker and focused test commit while preserving the bridge chain and frozen manifest.",
    "verification": "Rerun the focused test file, plain validate command, and source quality checks."
  },
  "hard_invariants": [
    "Plain validate output and exit semantics remain compatible.",
    "JSON output is deterministic and contains no runtime receipt or fabricated release evidence.",
    "Invalid manifests still fail nonzero and never emit a false PASS.",
    "The frozen manifest and digest are not modified.",
    "No dispatcher, TAFE, harness, credential, deployment, release, or external-system state is mutated."
  ],
  "fail_closed_conditions": [
    "The active PAUTH, independent GO, claim, or implementation-start evidence is missing or stale.",
    "Either target has concurrent worktree changes before implementation.",
    "The JSON payload omits the digest or inventory counts, is nondeterministic, or changes plain output.",
    "Any focused test, CLI check, quality check, or frozen-digest assertion fails."
  ],
  "essential_context_preservation": "The repair preserves the frozen acceptance contract, human CLI compatibility, deterministic evidence semantics, exact two-file ownership, and independent review history."
}
```

## Risk / Rollback

The primary risk is an output compatibility regression or a JSON payload that
looks successful while validation actually failed. The implementation must
derive both output modes from the same `validate_manifest` result, print JSON
only after successful validation, and preserve the existing ManifestError
failure path.

Rollback is a separately authorized revert of only the checker and focused test
commit. The manifest, digest, runtime receipts, bridge records, and unrelated
working-copy changes are never part of this scope.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5567-modernization-rc-validate-json`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - the change repairs a production RC checker interface that canonical
acceptance evidence already invokes but the CLI currently rejects.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
