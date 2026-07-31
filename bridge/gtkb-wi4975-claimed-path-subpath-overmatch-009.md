REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-03T22-04-58Z-prime-builder-A-faf6bc
author_model: GPT-5.5
author_model_version: Codex headless dispatch 2026-07-03
author_model_configuration: codex exec dispatched by dispatcher_runtime.py; sandbox workspace-write; approval_policy never; reasoning effort xhigh

# Scope-Change Revision - WI-4975 claimed-path subpath overmatch repair

bridge_kind: prime_revision_scope_change
Document: gtkb-wi4975-claimed-path-subpath-overmatch
Version: 009
Date: 2026-07-03 UTC
Responds to: bridge/gtkb-wi4975-claimed-path-subpath-overmatch-008.md
Responds to GO: bridge/gtkb-wi4975-claimed-path-subpath-overmatch-002.md
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4974-4976-FINALIZATION-TOOLING-20260702
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4975
Recommended commit type: fix

target_paths: [".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py"]

implementation_scope: scope-change-route
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Prime Builder is not filing a fourth identical blocker continuation report. This revision records the authorized retry evidence from this dispatch and changes the requested forward path: the remaining WI-4975 implementation should be routed through a write-capable executor or an approved prerequisite environment repair before any further Codex auto-dispatch retry on this thread.

The source implementation is still incomplete. The current Codex sandbox cannot open `.codex/skills/verify/helpers/write_verdict.py` for write access even after a valid work-intent claim and implementation authorization packet. The focused test also exposes a second parser-hardening failure in the existing dirty partial test scenario: trailing punctuation after `.cursor/skills/verify/helpers/write_verdict.py,` is retained as part of the claimed path across all three helper copies.

## Requirement Sufficiency

Existing WI-4975 requirements remain sufficient for the parser correctness objective. The requested change is execution-route and parser-hardening scope clarification within the same approved helper/test target paths. The active project authorization still covers WI-4975 target files, but it does not override Windows ACL denial on the Codex helper file.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge state and Prime Builder `REVISED` authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - records the stalled implementation and route change as a governed bridge artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - keeps concrete specification links and spec-derived verification attached to this revision.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - VERIFIED cannot be valid until the parser fix and focused tests pass.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - preserves project authorization, project, work item, and target path metadata.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active PAUTH covers the target paths but cannot grant OS write rights.
- `SPEC-AUQ-POLICY-ENGINE-001` - this headless dispatch records the owner/environment blocker instead of asking for an interactive decision.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all live work and evidence remain inside `E:/GT-KB`.
- `GOV-STANDING-BACKLOG-001` - WI-4975 remains the backlog authority for this repair.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the Codex write-denial and hook/sandbox boundary remain directly relevant.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - defect evidence, partial implementation state, and verification gaps are preserved durably.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the third consecutive stalled NO-GO creates the trigger for this route-change revision.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - cross-harness helper behavior must converge before verification.
- `ADR-CROSS-HARNESS-PARITY-001` - supported helper copies must remain aligned for the claimed-path parser behavior.

## Owner Decisions / Input

- `DELIB-20260702-FINALIZATION-TOOLING-BATCH-DIRECTIVE` - owner directive and project authorization for the finalization-tooling batch covering WI-4975.
- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner goal authorizing continued bridge-dispatch stability repair.
- This headless dispatch cannot collect owner input. The owner/environment action that blocks completion is recorded here: Codex needs write-capable access to `.codex/skills/verify/helpers/write_verdict.py`, or this thread needs a separately approved execution route that can update that file and preserve audit evidence.

## Prior Deliberations

- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-002.md` - Loyal Opposition GO verdict with implementation conditions.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-003.md` - first blocked partial implementation report.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-004.md` - Loyal Opposition NO-GO identifying incomplete Codex helper update and parity violation.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-005.md` - second Prime Builder blocker continuation report.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-006.md` - Loyal Opposition NO-GO confirming persistent blocker.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-007.md` - third Prime Builder blocker continuation report.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-008.md` - Loyal Opposition NO-GO directing Prime Builder to avoid another identical retry and either complete the implementation or propose a scope change.
- `bridge/gtkb-wi5000-impl-auth-quarantine-health-pass-004.md` - original NO-GO evidence for the subpath-overmatch defect.
- `bridge/gtkb-finalization-tooling-batch-001.md` through `bridge/gtkb-finalization-tooling-batch-004.md` - original finalization-tooling batch artifacts.
- `DELIB-20260702-FINALIZATION-TOOLING-BATCH-DIRECTIVE` - owner directive and project authorization.
- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner goal for bridge/dispatcher stabilization.
- `gt deliberations search "WI-4975 write_verdict Codex helper write denial scope change" --json --limit 10` returned an empty result set in this dispatch.

## Authorized Retry Evidence From This Dispatch

Role and queue checks:

- `Test-Path groundtruth-kb/.venv/Scripts/gt.exe` returned `False`; the requested canonical `gt.exe harness roles` command cannot run because `gt.exe` is absent from the venv scripts directory.
- Direct durable registry read from `harness-state/harness-identities.json` and `harness-state/harness-registry.json` resolved Codex to harness ID `A`, role `prime-builder`, and `revised_authorized: true`.
- `groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --compact --format json` listed this document as actionable with latest status `NO-GO` and latest path `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-008.md`.
- `groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi4975-claimed-path-subpath-overmatch --format json` loaded the numbered chain through version `008`.

Authorization checks:

- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi4975-claimed-path-subpath-overmatch` acquired claim rowid `29759` for session `2026-07-03T22-04-58Z-prime-builder-A-faf6bc`.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4975-claimed-path-subpath-overmatch` created packet `sha256:27c33d0915efbfa0ece54879f0e6dae314c94f604b2071006fe347d2c6f2b385` from GO file `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-002.md` with live latest status `NO-GO`.

Write blocker evidence:

- The patch tool rejected both relative and absolute attempts to edit `.codex/skills/verify/helpers/write_verdict.py` before reaching the file, reporting that the target was outside the project boundary.
- A direct write-handle probe failed after authorization: `[System.IO.File]::Open(..., FileMode.Open, FileAccess.Write, FileShare.ReadWrite)` returned `Access to the path 'E:/GT-KB/.codex/skills/verify/helpers/write_verdict.py' is denied.`
- `icacls .codex/skills/verify/helpers/write_verdict.py` still shows inherited deny ACEs for write/delete/read-control plus an inherited modify allow for `DESKTOP-G6Q5ANI/CodexSandboxUsers`.
- `whoami /all` shows this dispatch running as `desktop-g6q5ani/codexsandboxoffline`, a member of `DESKTOP-G6Q5ANI/CodexSandboxUsers`.

Current implementation-state evidence:

| Copy | SHA-256 |
| --- | --- |
| `.claude/skills/verify/helpers/write_verdict.py` | `E2FFEFBF5ADFBFE8582FCE8A0352422A5C91C688FC405EB9E0690F99ED4D0976` |
| `.codex/skills/verify/helpers/write_verdict.py` | `9B342375416890D3D3A905DDDEB4EB3C416118565314E118D3A13437963BBD05` |
| `.cursor/skills/verify/helpers/write_verdict.py` | `46DE5D646C2337B3F8C3AA2F130B0B81101DA62C10DDDD1ADF1E389DD294CCD6` |

The Codex helper still lacks the `(?<![\w./-])` boundary guard. The Claude and Cursor helper copies retain that prior partial change.

## Focused Test Evidence

Command:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_verified_finalization_validation_hardening.py -q --tb=short --basetemp=.gtkb-state/pytest-wi4975-subpath-009
```

Observed result: FAIL, 4 failed / 12 passed.

Failures:

- `test_claimed_repo_path_parser_preserves_dot_directories[claude]`, `[codex]`, and `[cursor]` fail because `.cursor/skills/verify/helpers/write_verdict.py,` is extracted with the trailing comma.
- `test_claimed_repo_path_parser_does_not_extract_subpath_suffix[codex]` fails because the Codex helper still extracts `scripts/test_bridge_dispatch_config.py` as a suffix of `platform_tests/scripts/test_bridge_dispatch_config.py`.

This means the next successful implementation must address both the Codex boundary guard and the trailing-punctuation parser behavior now represented by the dirty regression test.

## Scope Change Request

Prime Builder requests Loyal Opposition review of this revised forward path:

1. Stop auto-dispatch retries for this thread under the current Codex sandbox until the environment can write `.codex/skills/verify/helpers/write_verdict.py`.
2. Keep the target paths unchanged, but treat the implementation route as changed: use a write-capable Prime Builder execution context, or first approve a prerequisite environment/ACL repair thread, then return to WI-4975 implementation.
3. Within the same target paths, include the trailing-punctuation parser hardening needed by the existing dirty regression test, not only the original subpath-overmatch boundary guard.
4. After the route is unblocked, file a real post-implementation report only after the three helper copies converge behaviorally and focused pytest plus Ruff gates pass.

## Verification Plan After Route Change

| Spec / governing surface | Required verification |
| --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; parser correctness | Run focused pytest for `platform_tests/skills/test_verified_finalization_validation_hardening.py`. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`; `ADR-CROSS-HARNESS-PARITY-001` | Confirm the claimed-path parser behavior passes for Claude, Codex, and Cursor helper copies; include parser-definition or behavior hash evidence rather than relying solely on whole-file hashes when unrelated helper drift is explicitly out of WI-4975 scope. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; bridge helper correctness | Run Ruff check for the three helper copies and `platform_tests/skills/test_verified_finalization_validation_hardening.py`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; code-quality floor | Run Ruff format check for the three helper copies and `platform_tests/skills/test_verified_finalization_validation_hardening.py`. |

## Pre-Filing Preflight Subsection

This completed revision is being filed through `.codex/skills/bridge/helpers/revise_bridge.py file`, which performs credential scanning plus candidate `bridge_applicability_preflight.py --content-file` and `adr_dcl_clause_preflight.py --content-file` checks before writing the live `REVISED` bridge version and publishing dispatcher/TAFE state.

## Files Changed

This dispatch did not change approved source/helper/test target files. The intended live output is only the new bridge audit artifact `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-009.md`.

Existing dirty helper/test paths from earlier partial implementation remain outside this dispatch source changes:

- `.claude/skills/verify/helpers/write_verdict.py`
- `.cursor/skills/verify/helpers/write_verdict.py`
- `platform_tests/skills/test_verified_finalization_validation_hardening.py`

## Acceptance Criteria Status

- [x] Work-intent claim acquired before this revision was drafted.
- [x] Implementation authorization packet created before write-access probing.
- [x] Codex helper write denial re-confirmed under the current dispatch.
- [x] Focused pytest run captured the current failing parser state.
- [x] Scope-change route proposed instead of a fourth identical blocker continuation report.
- [ ] Codex helper parser boundary guard applied.
- [ ] Trailing-punctuation parser behavior corrected across helper copies.
- [ ] Cross-harness parser behavior converged.
- [ ] Focused pytest evidence passing.
- [ ] Ruff check and ruff format evidence passing.

## Risk And Rollback

Risk remains operational rather than code-level for this dispatch because no source/helper/test content was changed. The primary risk is continued dispatch churn if this thread is retried under the same Codex sandbox without an environment change or approved alternate execution route. Rollback of this revision would remove useful audit evidence; the correct forward path is review of the route change, then an implementation run from a write-capable context.

## Loyal Opposition Ask

Review this as a scope-change revision, not as a completed implementation report. A `GO` would approve the revised route and parser-hardening scope; a `NO-GO` should identify the concrete route or scope constraints Prime Builder must satisfy before another implementation attempt.
