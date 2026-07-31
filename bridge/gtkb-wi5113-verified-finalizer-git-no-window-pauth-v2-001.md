NEW

# Implementation Proposal - Suppress Git console windows in VERIFIED finalization and tests

bridge_kind: prime_proposal
Document: gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-15T20:54:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6610-1bc5-7781-88bf-900dccbc6010
author_model: GPT-5 Codex
author_model_version: 5
author_model_configuration: Extra High

Project Authorization: PAUTH-WI-5113-VERIFIED-FINALIZER-GIT-NO-WINDOW-20260715
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5113

target_paths: [".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]

implementation_scope: configuration | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

This proposal supersedes the implementation-start path of
`gtkb-wi5113-verified-finalizer-git-no-window-001.md` without changing its
five-file implementation delta. That proposal received independent GO at
version 002, but its claim failed closed because the legacy standing PAUTH
contains the now-unregistered forbidden-operation label `spec_deletion`.

The dedicated owner-authorized PAUTH named above uses only registered
operation vocabulary and is bound to WI-5113 plus the exact target classes.
Implementation imports `scripts.windows_subprocess.no_window_subprocess_kwargs`
in the three verify helper projections, forwards those kwargs in production
and fixture Git wrappers, routes direct bridge-writer fixture Git setup through
the corrected wrapper, and adds focused forwarding coverage. Git arguments,
finalization semantics, dispatcher routing, and public APIs do not change.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO and matching work-intent/start evidence.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires registered PAUTH vocabulary at claim and start time.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - binds this work to the exact WI, target classes, and owner decision.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete requirement linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the project, PAUTH, WI, and target metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed finalizer, parity, lint, and format evidence.
- `GOV-RELIABILITY-FAST-LANE-001` - classifies this as a small single-defect reliability correction.
- `ADR-CROSS-HARNESS-PARITY-001` - requires equivalent Claude, Codex, and Cursor helper behavior.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires an explicit disposition for every affected harness surface.
- `GOV-WORK-TREE-HYGIENE-001` - requires preservation of unrelated same-path work.

## Prior Deliberations

- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` - owner directive to identify and durably suppress every visible workstation console source.
- `bridge/gtkb-wi5113-verified-finalizer-git-no-window-001.md` and `-002.md` - original proposal and independent GO; implementation could not start because its legacy PAUTH was operation-time invalid.
- `bridge/gtkb-wi5049-headless-spawn-guardrails-008.md` - VERIFIED canonical no-window launch guardrails.
- `bridge/gtkb-wi5107-bridge-helper-no-window-subprocess-006.md` - VERIFIED bridge-helper no-window predecessor.

## Owner Decisions / Input

`DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` explicitly authorizes continued
diagnosis and correction until visible console spawning is durably suppressed.
The owner repeated that direction on 2026-07-15: "Fix the window spawning
problem and then return to regular work." The governed backlog authorization
service created `PAUTH-WI-5113-VERIFIED-FINALIZER-GIT-NO-WINDOW-20260715`
from that owner decision after a successful dry run. No additional owner
decision is required.

## Requirement Sufficiency

Existing requirements are sufficient. The dedicated PAUTH corrects only the
operation-time authorization envelope; it does not broaden the implementation
behavior approved in the original proposal.

## Proposed Scope

1. In each of the three managed `write_verdict.py` copies, import
   `no_window_subprocess_kwargs` and forward its mapping from `_run_git`.
2. In the atomicity test, route `_git` and `_git_bytes` through the same helper
   and add a regression asserting production `_run_git` forwards the mapping.
3. In the bridge-writer test, route `_git` through the helper and replace the
   direct Git setup calls with `_git` calls.
4. Preserve byte-identical behavior across the three helper projections and
   preserve all unrelated pre-existing hunks in the target files.

## Cross-Harness Disposition

- Claude: `.claude/skills/verify/helpers/write_verdict.py` receives the shared no-window wrapper call.
- Codex: `.codex/skills/verify/helpers/write_verdict.py` receives byte-identical behavior.
- Cursor: `.cursor/skills/verify/helpers/write_verdict.py` receives byte-identical behavior.
- Antigravity, Ollama, OpenRouter, Goose, and Alibaba Cloud Studio: no dedicated verify-helper projection is present in the approved target set; these harnesses consume the governed bridge/finalization behavior and require no waiver.

## Specification-Derived Verification Plan

| Specification | Verification | Expected result |
| --- | --- | --- |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Acquire the exact thread claim and run `implementation_authorization.py begin` against this proposal. | PAUTH vocabulary resolves, both target classes are allowed, and the exact five paths are authorized. |
| Owner no-visible-console directive; `GOV-RELIABILITY-FAST-LANE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=short` | Focused suite passes while Git launches use shared no-window kwargs. |
| `ADR-CROSS-HARNESS-PARITY-001` | Assert the production wrapper forwards the monkeypatched kwargs and compare the three helper files byte-for-byte. | Forwarding is covered and projections remain identical. |
| `GOV-WORK-TREE-HYGIENE-001` | Compare the post-change diff with the captured pre-implementation target diffs. | Existing review-independence and bridge-writer compliance hunks remain unchanged. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run `ruff check` and `ruff format --check` on all five target paths. | Both Ruff gates pass. |

A post-test process check must show no surviving suite-owned `git.exe`,
`cmd.exe`, or `conhost.exe` process.

## Existing Worktree Preservation

Before this WI-5113 implementation, the three verify helpers contained
identical uncommitted review-independence changes and
`platform_tests/scripts/test_gtkb_bridge_writer.py` contained unrelated bridge
compliance fixture changes. Those bytes are foreign to this proposal and must
not be discarded, absorbed, or claimed. The approved hunk/finalization path
must isolate only the no-window delta.

## Acceptance Criteria

- Every approved production and fixture Git subprocess wrapper forwards the canonical Windows no-window kwargs.
- The focused regression suite and both Ruff gates pass.
- The three managed helper projections remain byte-identical.
- No suite-owned Git, cmd, or conhost process survives the test run.
- No path outside `target_paths` is modified by implementation.

## Risks / Rollback

Risk is limited to subprocess keyword compatibility and same-path worktree
commingling. The shared helper returns an empty mapping off Windows and valid
`creationflags`/`startupinfo` on Windows, so Git behavior is otherwise
unchanged. Rollback removes only the WI-5113 no-window hunks; historical and
unrelated same-path changes remain intact.

## Recommended Commit Type

`fix`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
