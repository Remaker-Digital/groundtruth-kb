NEW

# Implementation Proposal: WI-4667 verified release finalization

bridge_kind: prime_proposal
Document: gtkb-wi4667-verified-release-finalization
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-27 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder

Project Authorization: PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-4667-REJECT-RETIRE-SPEC
Project: PROJECT-BACKLOG-TRIAGE-AND-HYGIENE
Work Item: WI-4667

target_paths: ["groundtruth-kb/src/groundtruth_kb/intake.py", "groundtruth-kb/tests/test_intake.py"]

implementation_scope: source
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

---

## Summary

This proposal authorizes release finalization only for the already-implemented
and already-VERIFIED WI-4667 target paths. The canonical WI-4667 bridge thread
(`gtkb-wi4667-intake-reject-retire-confirmed-spec`) reached `VERIFIED` at
`bridge/gtkb-wi4667-intake-reject-retire-confirmed-spec-004.md`, and MemBase
marks `WI-4667` resolved. However, the verified source and test hunks remain
dirty in the release worktree, so they are absent from the releasable commit
set.

No new product behavior is proposed here. The requested action is to refresh
the implementation-start authorization boundary so Prime Builder can stage and
commit exactly the two verified target paths without bypassing the protected
source gate or bundling unrelated WIP/scratch files.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge status and numbered files are the
  durable coordination surface; the original WI-4667 chain is terminal
  VERIFIED and this filing preserves append-only release-finalization evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  links the governing process and implementation specifications for the
  protected-path finalization.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization,
  Project, and Work Item metadata are present and machine-readable.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the original VERIFIED
  verdict and this release pass both map to concrete intake tests.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` - WI-4667 implements the intake reject
  lifecycle invariant: a rejected intake must not leave its auto-created
  auto-created intake specification row active.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - both target paths are GT-KB
  platform files inside the project root.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - the behavior is
  enforced by regression tests in `groundtruth-kb/tests/test_intake.py`.
- `GOV-STANDING-BACKLOG-001` - `WI-4667` exists in MemBase and is resolved with
  completion evidence citing the terminal VERIFIED bridge thread.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - advisory; finalization preserves
  the verified source, test, and bridge evidence as a durable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory; this proposal handles the
  terminal VERIFIED to committed-release transition without reclassifying WIP.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - advisory; the release act remains
  governed but avoids adding noncanonical explanatory sidecars.

## Prior Deliberations

- `DELIB-20266194` - owner AUQ authorizing the backlog proposal loop and the
  covering WI-4667 PAUTH.
- `DELIB-20266274` - owner authorization for the later WI-4880 intake scanner
  fix explicitly noted the deferred intake test/code separation context.
- `bridge/gtkb-wi4667-intake-reject-retire-confirmed-spec-001.md` through
  `-004.md` - original NEW, GO, post-implementation report, and Cursor-E
  VERIFIED verdict for this exact source/test change.
- Current owner release directive in this session: separate release-ready
  verified work from WIP/scratch and commit only releaseable work.

## Owner Decisions / Input

No new owner decision is required. The owner has already directed this release
finalization pass, and the active PAUTH for `WI-4667` covers the exact two
target paths. This proposal exists because the old GO-time implementation
packet expired after the thread reached VERIFIED, while the protected-source
gate still requires a live GO packet before staging those paths.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-SPEC-CAPTURE-TRANSPARENCY-001`,
the `WI-4667` MemBase record, and the terminal VERIFIED bridge verdict already
define and verify the required behavior. This proposal changes no requirement,
specification, schema, bridge verdict, or MemBase record.

All generated or committed artifacts for this finalization remain in-root under
E:\GT-KB: the bridge proposal is under `bridge/`, and the only implementation
targets are `groundtruth-kb/src/groundtruth_kb/intake.py` and
`groundtruth-kb/tests/test_intake.py`.

## Spec-Derived Verification Plan

| Specification | Verification command | Expected result |
|---|---|---|
| `GOV-SPEC-CAPTURE-TRANSPARENCY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_intake.py -q --tb=short` | `test_reject_intake_retires_confirmed_spec` and surrounding intake tests pass. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | same pytest command plus ruff check/format for the two target files | Tests and static checks pass before final commit. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/intake.py groundtruth-kb/tests/test_intake.py` | No lint violations. |

Already observed in this release pass before filing:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_intake.py -q --tb=short
=> 40 passed, 1 warning in 34.89s

groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\intake.py groundtruth-kb\tests\test_intake.py
=> All checks passed!

groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\intake.py groundtruth-kb\tests\test_intake.py
=> 2 files already formatted
```

## Risk / Rollback

Risk is low because the implementation is already terminal VERIFIED and the
commit will include only the two verified target paths. The primary risk is
accidentally bundling unrelated dirty release/WIP files; mitigation is a
pathspec-limited stage and commit after a fresh authorization packet is active.
Rollback is a single commit revert of the WI-4667 finalization commit.

## Bridge Filing

This proposal is filed under `bridge/` as
`bridge/gtkb-wi4667-verified-release-finalization-001.md`; no prior bridge file
is deleted or rewritten. If Loyal Opposition returns GO, Prime Builder will
activate implementation authorization for this slug, stage only the two
target paths, commit them with a WI-4667 finalization message, and leave all
other dirty WIP/scratch files untouched.

## Recommended Commit Type

`fix` - finalizes the already-verified `reject_intake` lifecycle bug fix into
the releasable git history.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
