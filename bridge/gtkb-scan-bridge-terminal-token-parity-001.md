NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: keep-working-pb-20260619-scan-bridge-terminal-token-parity
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop automation; Prime Builder

# Defect-Fix Proposal - Scan Bridge Terminal Token Parity

bridge_kind: prime_proposal
Document: gtkb-scan-bridge-terminal-token-parity
Version: 001
Date: 2026-06-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4675

target_paths: [".claude/skills/bridge/helpers/scan_bridge.py", "platform_tests/scripts/test_scan_bridge.py"]

## Summary

Repair the manual Prime Builder bridge scan helper's mirrored terminal-kind
token list so it remains in parity with the canonical bridge notification
router.

Focused verification of WI-4618 on 2026-06-19 failed
`platform_tests/scripts/test_scan_bridge.py::test_terminal_tokens_parity_with_canonical_notify`.
The canonical router now treats `implementation_report`, `post_implementation`,
and `post_impl` as terminal-kind bridge kinds, but
`.claude/skills/bridge/helpers/scan_bridge.py` still mirrors the older token
set. That drift can make the manual PB scan helper classify implementation
report GO verdicts differently from `groundtruth_kb.bridge.notify`.

## Defect / Reproduction

Command run from `E:\GT-KB`:

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; .venv\Scripts\python.exe -m pytest -o addopts="" --basetemp .gtkb-state\pytest-runs\scan-bridge-rerun platform_tests/scripts/test_scan_bridge.py -q
```

Observed result:

```text
FAILED platform_tests/scripts/test_scan_bridge.py::test_terminal_tokens_parity_with_canonical_notify
Extra items in the right set: 'post_impl', 'post_implementation', 'implementation_report'
```

The failure is not an implementation-start authorization bypass. A direct
attempt to edit the helper through the malformed latest WI-4618 bridge state
failed closed because the latest GO responds to an implementation report and is
not a valid implementation-start proposal packet. This proposal creates the
proper narrow bridge path for the parity repair.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `.claude/skills/bridge/helpers/scan_bridge.py`
- `platform_tests/scripts/test_scan_bridge.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - manual bridge scans must route bridge
  lifecycle states consistently with the canonical numbered-file bridge state.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this defect was found by
  a spec-derived regression test and the fix must rerun that test.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  cites the governing bridge, verification, and root-boundary surfaces.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal includes
  machine-readable PAUTH, project, and work-item metadata.
- `.claude/rules/file-bridge-protocol.md` - Prime Builder acts on GO/NO-GO
  bridge responses while terminal verification/report states must not be
  misrouted as implementable work.
- `.claude/rules/codex-review-gate.md` - protected helper/test edits require
  a live GO plus implementation-start packet.
- `.claude/rules/project-root-boundary.md` - all target files remain in root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the discovered drift is captured
  as WI-4675 and routed through bridge lifecycle instead of being patched
  silently.

## Prior Deliberations

- `DELIB-20264307` - prior bridge-thread deliberation for manual bridge scan
  terminal-GO filtering; this proposal is the same classifier-drift family.
- `DELIB-20263292` - bridge reconciliation wrap-scan check; relevant to keeping
  deterministic scan helpers aligned with bridge state.
- `DELIB-20261060` - prior scan/log noise review; relevant because this work
  keeps deterministic scan output actionable and trustworthy.
- `bridge/gtkb-suppress-non-activatable-go-from-pb-scan-003.md` - WI-4618
  implementation report whose verification rerun exposed this parity drift.
- `bridge/gtkb-suppress-non-activatable-go-from-pb-scan-004.md` - malformed
  verification response that made the direct implementation-start path fail
  closed, requiring this narrow follow-up proposal.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`
  (`DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`) authorizes proposing
  implementation for unimplemented work items linked to
  `PROJECT-GTKB-MAY29-HYGIENE`.
- No new owner decision is required. This proposal does not request formal
  GOV/SPEC/ADR/DCL mutation, production deployment, credential action, or
  destructive cleanup.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4675 states the required behavior:
`scan_bridge.py` and the canonical bridge notify router must agree on
terminal-kind tokens, and the focused parity test must pass. The existing
bridge/file-authority and spec-derived verification rules already define the
verification obligation.

## Proposed Scope

1. Add the missing canonical terminal-kind tokens to
   `.claude/skills/bridge/helpers/scan_bridge.py`.
2. Keep or extend `platform_tests/scripts/test_scan_bridge.py` so parity with
   `groundtruth_kb.bridge.notify._KIND_TERMINAL_TOKENS` remains mechanically
   tested.
3. Do not change `groundtruth_kb.bridge.notify` in this slice; it is the
   canonical source that the helper mirrors.
4. Do not change headless dispatch routing, bridge state, work-intent code, or
   unrelated dirty files.

## Specification-Derived Verification Plan

| Spec / governing surface | Verification evidence required |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Focused test proves scan helper terminal-kind classification mirrors canonical notify routing. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run `platform_tests/scripts/test_scan_bridge.py` after the fix and record observed results. |
| `.claude/rules/codex-review-gate.md` | Create implementation-start packet from this bridge GO before touching protected helper/test files. |
| `.claude/rules/project-root-boundary.md` | Changed paths remain under `E:\GT-KB`. |

Commands expected after GO:

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; .venv\Scripts\python.exe -m pytest -o addopts="" --basetemp .gtkb-state\pytest-runs\scan-bridge-terminal-token-parity platform_tests/scripts/test_scan_bridge.py -q
ruff check .claude/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_scan_bridge.py
ruff format --check .claude/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_scan_bridge.py
```

## Acceptance Criteria

- `set(scan_bridge._KIND_TERMINAL_TOKENS)` equals
  `set(groundtruth_kb.bridge.notify._KIND_TERMINAL_TOKENS)`.
- The focused `test_scan_bridge.py` suite passes.
- Ruff lint and format checks pass on changed files.
- No unrelated dirty worktree files are staged or committed.

## Risks / Rollback

Risk is low. The expected implementation is a small mirror-list/test update in
the manual scan helper. The main risk is over-broad routing change; this scope
avoids it by treating `groundtruth_kb.bridge.notify` as authoritative and not
touching headless dispatch. Rollback is reverting the helper/test changes from
the eventual implementation commit.

## Files Expected To Change

- `.claude/skills/bridge/helpers/scan_bridge.py`
- `platform_tests/scripts/test_scan_bridge.py`

## Recommended Commit Type

fix:
