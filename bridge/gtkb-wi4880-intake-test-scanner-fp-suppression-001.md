NEW

# gtkb-wi4880-intake-test-scanner-fp-suppression — suppress pre-existing scanner false-positive in test_intake.py; commit verified WI-4665 test

bridge_kind: prime_proposal
Document: gtkb-wi4880-intake-test-scanner-fp-suppression
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: ba2cbba9-87c3-41df-af06-ba16eea854be
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4880-INTAKE-TEST-SCANNER-FP
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4880

target_paths: ["groundtruth-kb/tests/test_intake.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

During the WI-4871 untracked-VERIFIED durability cleanup (S20260627), the WI-4665
implementation (`intake.py` `confirm_intake` `description=raw_text`) and its
VERIFIED verdict were committed (commit `e3014345b`), but the verified
spec-derived test `test_confirm_intake_populates_description_from_raw_text`
could **not** be committed. `groundtruth-kb/tests/test_intake.py` carries a
pre-existing AWS-access-key-shaped fixture in `test_redaction` (introduced by the
`GTKB-RELOCATION` vendor commit `b33c8008c`) that the `scripts/scan_secrets.py`
pre-commit gate flags. The codebase-standard remedy for legitimate
documentation/example fixtures is a same-line comment containing a marker token
that `scan_secrets.py` skips (the `placeholder` marker is one such token). The
prior session could not author that one-line suppression because the WI-4665
thread is terminal VERIFIED (no implementation-start authorization packet was
obtainable for it).

This proposal adds the `placeholder` suppression comment to **both**
pre-existing AWS-access-key-shaped fixture lines in `test_redaction` (the
assignment line and the assertion line), making the file pass `scan_secrets.py`,
and thereby unblocks committing the already-verified WI-4665 test. The change is
confined to `groundtruth-kb/tests/test_intake.py`; no production code and no test
*logic* changes — only the two fixture lines gain a trailing suppression comment,
and the previously-deferred WI-4665 test function is committed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this proposal is
  filed as the next status-bearing numbered bridge file under `bridge/` in the
  append-only chain.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` — the governing spec the deferred WI-4665
  test verifies (a confirmed intake spec must carry the full captured owner text
  in its description); committing the test restores that test coverage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the deferred test is the
  spec-derived regression for the clause above; this proposal lets it land in
  git so the coverage is durable, not merely asserted in a verdict.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: this
  section cites every governing spec and the verification plan maps to them.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: WI-4880 +
  PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY + active PAUTH metadata are in the
  header block.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the single changed path
  `groundtruth-kb/tests/test_intake.py` is GT-KB platform test source in-root
  under `E:\GT-KB`; no out-of-root path is created, read as a dependency, or
  required. The commit operates only on the in-root working tree.
- `GOV-STANDING-BACKLOG-001` — WI-4880 is the canonical backlog record for this
  work, authorized under the cited PAUTH.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the work is tracked as
  durable artifacts (WI-4880, this bridge thread, the committed test).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — advances WI-4880 toward
  verified; the deferred test transitions from uncommitted to committed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — owner decision, work item,
  and spec linkage are preserved as artifacts.

## Prior Deliberations

- `DELIB-20266274` — owner AUQ (S20260627) authorizing WI-4880 implementation
  with scope "Both lines + commit test"; the basis for the covering PAUTH.
- `bridge/gtkb-wi4665-intake-confirm-description-from-raw-text-004.md` — the
  WI-4665 VERIFIED verdict (independent Cursor-E LO) recording the test's
  verification evidence (38 passed); this proposal commits the test that verdict
  verified.
- WI-4871 untracked-VERIFIED durability cleanup (S20260627) — the finalization
  pass that surfaced this deferred-test gap (commit `e3014345b` committed the
  WI-4665 impl + verdict but not the test).

## Owner Decisions / Input

- `DELIB-20266274` — owner AskUserQuestion (S20260627): "Authorize WI-4880
  implementation … Pick the fix scope." → answer **"Both lines + commit test"**.
  This authorizes suppressing both pre-existing fixture lines and committing the
  verified WI-4665 test. No further owner decision is required.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-SPEC-CAPTURE-TRANSPARENCY-001` already
mandates the behavior the deferred test verifies; no new or revised requirement
is needed. The scanner-suppression is plumbing that lets an already-verified
test enter git history. No formal spec/governance mutation is in scope
(`kb_mutation_in_scope: false`).

## Spec-Derived Verification Plan

| Spec / clause | Test or command | Expected result |
|---|---|---|
| `GOV-SPEC-CAPTURE-TRANSPARENCY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest groundtruth-kb/tests/test_intake.py` (incl. `test_confirm_intake_populates_description_from_raw_text`) | all pass |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (file passes credential gate) | `python scripts/scan_secrets.py --staged` with `test_intake.py` staged | 0 potential secrets |
| Code quality | `ruff check` + `ruff format --check` on `test_intake.py` | both pass |

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_intake.py -q --no-header
```

## Risk / Rollback

- **Risk:** essentially none — the change adds a trailing comment to two
  pre-existing test fixture lines and commits a pure-assertion test; no
  production code, no test logic, no schema, no governed record is touched.
- **Isolation:** `target_paths` is restricted to `groundtruth-kb/tests/test_intake.py`;
  the in-flight `reject_intake` hunks in the same file are out of scope and must
  not be swept in (hunk-selective staging at implementation time).
- **Rollback:** single-commit revert removes the suppression comments and the
  committed test. No KB mutation; the append-only bridge history is untouched.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4880-intake-test-scanner-fp-suppression`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` — commits a previously-deferred spec-derived test plus a two-line
credential-scanner suppression on pre-existing fixtures; no production capability
surface is introduced.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
