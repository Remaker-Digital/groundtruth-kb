NEW

# gtkb-auto-retire-actuation-helper-parity — Lock in auto-retire-on-VERIFIED actuation parity across the three verify-helper copies

bridge_kind: prime_proposal
Document: gtkb-auto-retire-actuation-helper-parity
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 6e9eb87a-50f6-492f-b3fe-b230cb088350
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; Prime Builder role (::init gtkb pb); MAY29-HYGIENE retirement drive

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-OUT-OF-SNAPSHOT-6-2026-06-24
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4750

target_paths: [".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/skills/test_auto_retire_actuation_helper_parity.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4750 flagged that the auto-retire-on-VERIFIED Slice 1 actuation risked landing
only in `.claude/skills/verify/helpers/write_verdict.py` and omitting the `.codex`
(and `.cursor`) copies, so a Codex/Cursor VERIFIED finalization would commit the
verdict but never trigger automatic project retirement.

Current canonical state (verified 2026-06-24): the actuation
`_auto_retire_completed_projects_after_verified` and its call site from
`finalize_verified_commit` are **present in all three tracked helper copies**
(`.claude`, `.codex`, `.cursor`). The parity gap WI-4750 warned about is therefore
already closed in the wiring. What is still missing is the **regression coverage**
WI-4750 explicitly requires ("regression coverage for both"): there is no test that
asserts all three helper copies trigger the auto-retire actuation from VERIFIED
finalization, so the parity can silently regress (one copy edited, the others not —
exactly the divergence class this WI is about).

This proposal (1) verifies the actuation is behaviorally equivalent across the three
copies and aligns any divergence found, and (2) adds a parity regression test that
asserts each copy's `finalize_verified_commit` invokes the auto-retire actuation on a
successful VERIFIED finalization, locking in the parity and converting the WI-4750
risk into a mechanically-enforced invariant.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — defines the automatic
  member-WI-terminal retirement trigger (v6); the auto-retire actuation is the
  VERIFIED-finalization implementation of that trigger, so this spec governs the work.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — owns the VERIFIED Commit-Finalization Gate that
  hosts the actuation call; cross-harness finalization must behave equivalently.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the fix adds spec-derived
  parity regression coverage; the new test is the spec-to-test mapping.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all
  relevant governing specs; satisfied by the applicability preflight.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project/PAUTH/work-item
  linkage metadata is present in the header.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation is authorized by
  the cited PAUTH covering WI-4750.
- `GOV-STANDING-BACKLOG-001` — WI-4750 is an active MAY29-HYGIENE backlog member.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the regression test makes the
  cross-harness parity a durable, mechanically-checked invariant.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — keeps the three helper copies
  a coherent artifact set rather than drift-prone duplicates.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — auto-retirement is a lifecycle
  transition; parity coverage keeps the transition uniform across harnesses.

## Prior Deliberations

- `DELIB-20265569` — owner decision (AUQ 2026-06-22) to build the
  auto-retire-on-VERIFIED automation (WI-4741) now; this proposal closes the
  parity/coverage tail of that automation rather than re-opening the design.
- `DELIB-20265584` — owner decision reconciling the project-retirement criterion to
  member-WI terminal resolution (GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v6);
  the actuation implements this criterion.
- `DELIB-20265881` — owner clarification that the retirement trigger is all
  member WIs terminal (incl. withdrawn/superseded); the parity test asserts the
  actuation fires consistently regardless of harness.
- Deliberation search query `"auto-retire VERIFIED actuation codex helper parity
  write_verdict finalize project retirement"` (2026-06-24) surfaced the decisions
  above and no decision specific to the helper-parity regression-coverage tail.

## Owner Decisions / Input

Authorized by owner AskUserQuestion on 2026-06-24 (option "Authorize all 6"),
captured as `DELIB-20265880`, which created
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-OUT-OF-SNAPSHOT-6-2026-06-24` covering the six
out-of-snapshot member work items (including WI-4750) for bounded implementation
(allowed mutation classes: source, test_addition, hook_upgrade, cli_extension,
scaffold_update). No further owner decision is required to proceed through the
bridge protocol; this section records the standing authorization evidence.

## Requirement Sufficiency

Existing requirements sufficient. The requirement is specified by
`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (the automatic retirement trigger
the actuation implements), `GOV-FILE-BRIDGE-AUTHORITY-001` (the finalization gate),
and the WI-4750 acceptance ("shared or mirrored auto-retire actuation across both
helper surfaces with regression coverage for both"). No new or revised requirement
is needed.

## Spec-Derived Verification Plan

New parity regression test `platform_tests/skills/test_auto_retire_actuation_helper_parity.py`
imports each helper copy's module and asserts (a) each defines
`_auto_retire_completed_projects_after_verified`, (b) each `finalize_verified_commit`
invokes that actuation after a successful commit (monkeypatched/spied), and (c) the
actuation behavior is equivalent across the three copies.

| Specification | Test / Verification | Expected |
|---|---|---|
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (actuation present) | `test_each_helper_copy_defines_auto_retire_actuation` | all three define it |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (actuation invoked) | `test_each_finalize_invokes_auto_retire_after_commit` | actuation called on successful finalize in each copy |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (parity) | `test_auto_retire_actuation_behaviour_is_equivalent_across_copies` | equivalent behavior; divergence fails |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | full test module run | all assertions pass |

Execution command (repo venv for reproducibility):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_auto_retire_actuation_helper_parity.py -q --no-header
```

Pre-file code-quality gates on changed Python (both, separate):

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check <changed.py>
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <changed.py>
```

## Risk / Rollback

- **Risk: the three copies have already diverged behaviorally.** If verification finds
  divergence (e.g., a stale `.codex` actuation), this proposal aligns them; that
  reclassifies the change from test-only (`test`) to `fix` and the implementation
  report will declare the actual type per the diff.
- **Risk: parity test is brittle to legitimate harness-specific differences.** The
  test asserts the auto-retire *invocation* and *behavior*, not byte-identity, so
  harness-specific path/skill strings do not trip it.
- **Risk: import side effects when loading three same-named modules.** Mitigated by
  loading each copy under a distinct module name via importlib spec-from-file.
- **Rollback:** single-commit revert of the test (and any alignment edit) restores
  prior behavior; no data migration.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-auto-retire-actuation-helper-parity`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` — the primary deliverable is parity regression coverage for an actuation that
already exists in all three copies. If verification finds behavioral divergence that
must be aligned, the implementation report will reclassify to `fix` per the diff.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
