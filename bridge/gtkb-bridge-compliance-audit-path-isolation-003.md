REVISED

Document: gtkb-bridge-compliance-audit-path-isolation
Version: 003
Author: prime-builder
Date: 2026-05-15

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3320

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_codex_bridge_compliance_gate.py"]

# Implementation Proposal: Make `--audit-only` output path test-isolatable

## Revision History

- `-001` NEW: initial proposal.
- `-002` NO-GO (Codex): F1 (P1) — missing `## Owner Decisions / Input` section
  for a proposal that relies on an owner-authorized standing project scope.
  No technical redesign requested.
- `-003` REVISED (this file): adds the `## Owner Decisions / Input` section
  making the owner-decision chain explicit. Technical scope unchanged from
  `-001`.

## Summary

`platform_tests/scripts/test_codex_bridge_compliance_gate.py::test_audit_only_accepts_compliant_files_without_blocking`
is a flaky test. In full-suite runs it intermittently fails with
`json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)` at the
`json.loads(AUDIT_PATH.read_text(...))` call. Run in isolation it passes
reliably (verified 3/3, ~0.5s each). This is a test-isolation defect, not a
product defect.

Root cause: the `--audit-only` mode of `.claude/hooks/bridge-compliance-gate.py`
writes its audit result to a single fixed shared path,
`.codex/gtkb-hooks/last-bridge-audit.json` (`AUDIT_OUTPUT_RELATIVE_PATH`). Two
audit tests (`test_audit_only_detects_non_compliant_files_without_blocking` and
`test_audit_only_accepts_compliant_files_without_blocking`) each delete, write,
and read that one path; the real Codex `bridge-compliance-audit.cmd` PostToolUse
hook also writes it. Concurrent invocations interleave delete/write/read, so a
test occasionally reads the file mid-write (empty) or after another writer's
`unlink`. The `char 0` error is an empty-file read.

This proposal makes the audit output sink injectable so each test owns a
private output path under pytest `tmp_path`, eliminating the shared-fixture
race. The real consumer is unchanged: when no explicit path is supplied the
hook keeps writing the existing fixed default.

## Fast-Lane Eligibility (GOV-RELIABILITY-FAST-LANE-001)

This work item is reliability fast-lane eligible:

1. Origin is `defect` (WI-3320 `origin=defect`, `component=tests`). Not `new`.
2. No new product behavior. The added `--audit-output` argument is internal
   test-isolation plumbing; when absent, behavior is byte-identical to today.
3. No new or revised requirement or specification is required.
4. Small and single-concern: 3 files, well under ~150 net lines (~25 net
   lines of hook change applied to two byte-identical copies, plus localized
   test edits).

WI-3320 is a member of `PROJECT-GTKB-RELIABILITY-FIXES` (membership active) and
is covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (active, no
expiry, no included/excluded WI restriction). No per-fix deliberation,
per-fix project authorization, or per-fix formal-artifact-approval packet is
required. Bridge review, Codex GO, the implementation-start authorization
packet, a post-implementation report, and Codex VERIFIED are preserved.

## Owner Decisions / Input

This fast-lane defect fix proceeds under a standing, owner-approved project
authorization. No new per-fix owner decision is required; this section makes
the owner-decision chain explicit per `.claude/rules/file-bridge-protocol.md`
(Mandatory Owner Decisions / Input Section Gate) and resolves F1 of the `-002`
NO-GO.

- Owner decision of record: `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`
  ("Owner direction - build a standing reliability fast-lane for small defect
  fixes"). This is the owner decision that created the reliability fast-lane;
  it is recorded as `owner_decision_deliberation_id` on the project
  authorization below.
- Project authorization: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` —
  active, no expiry, with `included_work_item_ids = null` and
  `excluded_work_item_ids = null` (coverage by active project membership, not
  an enumerated work-item list).
- Project / work item: `PROJECT-GTKB-RELIABILITY-FIXES` is active; `WI-3320`
  ("Fix flaky bridge-compliance-audit test (shared audit-file race)",
  `origin=defect`, `component=tests`) is an active member of that project.
  Active project membership is the mechanism by which the standing
  authorization covers this fix, so no per-fix project authorization is
  created.
- Authorization limits relevant to this fix:
  - `allowed_mutation_classes = ["source", "test_addition", "hook_upgrade"]` —
    this proposal's edits (hook source plus test changes) fall within these
    classes.
  - `forbidden_operations = ["deploy", "git_push_force", "spec_deletion"]` —
    this proposal performs none of these.
- No additional owner decision is needed for this specific defect fix. Per
  `GOV-RELIABILITY-FAST-LANE-001`, a fast-lane-eligible fix requires no per-fix
  deliberation, no per-fix project authorization, and no per-fix
  formal-artifact-approval packet. Bridge review (this thread), Codex GO, the
  implementation-start authorization packet, the post-implementation report,
  and Codex VERIFIED remain required and are preserved.

## Specification Links

- GOV-RELIABILITY-FAST-LANE-001 — reliability fast-lane governance; defines
  eligibility and the preserved-gates contract for this fix.
- GOV-FILE-BRIDGE-AUTHORITY-001 — file bridge authority; this proposal is
  filed and reviewed under the bridge protocol.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — mandatory
  specification linkage for implementation proposals.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification must be
  derived from linked specifications and executed; see the verification plan
  below.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 — project-linkage
  metadata lines (Project Authorization / Project / Work Item) carried above.
- DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 — WI-3320 belongs to an
  approved project with an active authorization.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — GT-KB project root boundary; the
  per-test audit output uses pytest `tmp_path` (regenerable test evidence,
  not a canonical GT-KB artifact), consistent with existing suite practice.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — the defect and its fix are tracked
  as the WI-3320 work item and this bridge thread.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across work item,
  proposal, tests, and implementation report is preserved.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — WI-3320 advances through the standard
  created -> implemented -> verified lifecycle states.
- .claude/rules/file-bridge-protocol.md — bridge proposal, GO, and
  post-implementation verification workflow.
- .claude/rules/codex-review-gate.md — pre-implementation review gate.
- .claude/rules/project-root-boundary.md — root-boundary discipline for the
  audit output path decision.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-concern source/test defect fix. It performs no bulk
backlog mutation, no batch spec promotion, and no batch work-item resolution.
It touches one work item (WI-3320) and three files. The standing-backlog
references above are provenance citations (the WI and its project), captured
through the normal formal-artifact provenance path, not a bulk operation.

## Current Behavior

`.claude/hooks/bridge-compliance-gate.py`:

- `AUDIT_OUTPUT_RELATIVE_PATH = Path(".codex") / "gtkb-hooks" / "last-bridge-audit.json"` (module constant).
- `_audit_only(argv)` parses `--file-path` (and otherwise reads a stdin
  payload), computes the deny reason, then calls `_write_audit_result(...)`.
- `_write_audit_result(*, cwd_path, file_path, content, reason)` always writes
  to `cwd_path / AUDIT_OUTPUT_RELATIVE_PATH`.

Real (non-test) consumer:

- `.codex/gtkb-hooks/bridge-compliance-audit.cmd` runs
  `python "E:\GT-KB\.claude\hooks\bridge-compliance-gate.py" --audit-only`
  (registered as the Codex `PostToolUse:Bash` audit hook). It supplies no
  output path and depends on the fixed default.
- No production code reads `.codex/gtkb-hooks/last-bridge-audit.json`; it is a
  last-run diagnostic. The only readers are the two audit tests.

## Proposed Change

### 1. Hook: injectable audit output path (applied identically to both copies)

Apply the same change to `.claude/hooks/bridge-compliance-gate.py` and
`groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (the test
`test_hook_matches_template_or_documented_divergence` requires byte equality).

- Add an optional `--audit-output <path>` argument, parsed in `_audit_only`.
- `_write_audit_result` gains an `audit_output: str = ""` keyword parameter.
  When non-empty, the result is written to that path (resolved relative to
  `cwd_path` if not absolute); when empty, it writes the existing
  `cwd_path / AUDIT_OUTPUT_RELATIVE_PATH` default — unchanged behavior.

`AUDIT_OUTPUT_RELATIVE_PATH` remains the default; the real consumer
(`bridge-compliance-audit.cmd`) passes no `--audit-output` and is unaffected.

### 2. Tests: per-test isolated audit path

In `platform_tests/scripts/test_codex_bridge_compliance_gate.py`:

- `test_audit_only_detects_non_compliant_files_without_blocking` and
  `test_audit_only_accepts_compliant_files_without_blocking` take the pytest
  `tmp_path` fixture, pass `--audit-output <tmp_path>/audit.json` to the hook,
  and assert on that private file.
- Drop the shared-path delete dance (`if AUDIT_PATH.exists(): AUDIT_PATH.unlink()`).
- Remove the now-unused module-level `AUDIT_PATH` constant. `SKIPPED_PATH`
  stays (still used by `test_adapter_writes_skipped_extraction_diagnostic`).

The two tests no longer share any output path with each other or with the real
PostToolUse hook, so they cannot race.

## Alternatives Considered

- Atomic write (temp file + `os.replace`) in `_write_audit_result`: fixes
  torn-read but not cross-test value contamination (test A could still read
  test B's result). Rejected: does not fully isolate, and adds behavior beyond
  the defect.
- Pointing the hook at `tmp_path` via the working directory: the non-compliant
  test's `NEW` first line triggers the pending-applicability-preflight
  subprocess, which needs the real repo layout; changing `cwd` breaks it.
  Rejected as fragile.
- Explicit `--audit-output` argument with the real consumer unchanged
  (chosen): full isolation, zero production-behavior change, smallest surface.

## Requirement Sufficiency

Existing requirements sufficient. GOV-RELIABILITY-FAST-LANE-001 and the cited
bridge/test-isolation specifications fully govern this defect fix. No new or
revised requirement or specification is required before implementation.

## Specification-Derived Verification Plan

Spec-to-test mapping:

- GOV-RELIABILITY-FAST-LANE-001 (preserved-gates contract) — verified by this
  bridge thread itself: NEW proposal, Codex GO, implementation-start packet,
  post-implementation report, Codex VERIFIED.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (defect removed) — verified
  by the two updated audit tests plus a repeated full-file run:
  - `python -m pytest platform_tests/scripts/test_codex_bridge_compliance_gate.py -p no:randomly` (all tests PASS).
  - `python -m pytest platform_tests/scripts/test_codex_bridge_compliance_gate.py -n auto` run repeatedly (>=10x) — zero `JSONDecodeError`, zero flake.
- Real-consumer non-regression — `python .claude/hooks/bridge-compliance-gate.py --audit-only --file-path <bridge file>`
  with no `--audit-output` still writes `.codex/gtkb-hooks/last-bridge-audit.json`
  with the expected JSON.
- Template parity — `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py::test_hook_matches_template_or_documented_divergence` PASS (hook still byte-equal to template).
- Hook parity — `python -m pytest platform_tests/scripts/test_codex_hook_parity.py` PASS (`bridge-compliance-audit.cmd` still references the hook + `--audit-only`).

## Verification Already Performed

- Confirmed `--audit-only` writes only `AUDIT_OUTPUT_RELATIVE_PATH` and that no
  production code reads `last-bridge-audit.json` (grep across the repo: only
  the two tests read it).
- Confirmed `.claude/hooks/bridge-compliance-gate.py` and
  `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` are currently
  byte-identical (sha256 equal).
- Confirmed `check_codex_hook_parity.py` requires `bridge-compliance-audit.cmd`
  to contain the hook path and `--audit-only` only — adding an optional
  argument does not affect parity.

## Recommended Commit Type

`fix:` — repairs a flaky test (broken behavior) with no new capability surface.

## Risks / Gaps

- Low risk. Production path (no `--audit-output`) is byte-identical to today.
- The hook edit must be applied identically to both copies or the
  template-parity test fails; the implementation report will show both sha256.

## Prior Deliberations

Deliberation searches were run before proposing: semantic searches for
"flaky test audit path race", "bridge-compliance audit shared file", and
"test isolation tmp_path" returned only unrelated Loyal Opposition reviews;
this single-test audit-path isolation defect has no DA precedent. The
governing owner-decision record for the reliability fast-lane this fix uses
is `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` (see Owner Decisions / Input
above); no prior deliberation reviews the WI-3320 audit-output race itself.

## Acceptance Criteria

1. `--audit-only` accepts an optional `--audit-output <path>`; when absent the
   hook writes the unchanged `.codex/gtkb-hooks/last-bridge-audit.json`.
2. The two audit tests use private `tmp_path` audit files and no longer touch a
   shared path.
3. The full `test_codex_bridge_compliance_gate.py` file passes under repeated
   parallel runs with no `JSONDecodeError`.
4. `.claude/hooks/bridge-compliance-gate.py` remains byte-equal to the template.
5. `test_codex_hook_parity.py` and the workspace hard-block test suite pass.
