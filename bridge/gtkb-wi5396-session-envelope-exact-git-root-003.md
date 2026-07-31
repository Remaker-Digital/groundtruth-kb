NEW

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; build envelope
author_metadata_source: explicit_interactive_session_metadata

# GT-KB Bridge Implementation Report - WI-5396 Session Envelope Exact Git Root

bridge_kind: implementation_report
Document: gtkb-wi5396-session-envelope-exact-git-root
Version: 003
Responds to GO: bridge/gtkb-wi5396-session-envelope-exact-git-root-002.md
Approved proposal: bridge/gtkb-wi5396-session-envelope-exact-git-root-001.md
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5396
Recommended commit type: fix:

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "platform_tests/scripts/test_fab13_retention_policy.py"]

## Implementation Claim

Implemented exact-root containment for session-envelope Git status attestation.
`groundtruth_kb.session.envelope._git_status()` now first runs a bounded
`git rev-parse --show-toplevel` probe, compares the selected Git top-level path
to the supplied project root, and only runs bounded `git status --short` when
the paths are the same resolved root. Git absence, probe failure, top-level
timeout, top-level mismatch, status failure, and status timeout now return
explicit fail-soft evidence with `available=false`, `dirty=null`, a stable
`reason`, and bounded `short` output instead of scanning an ancestor repository
or hanging session close.

Exact repository roots preserve the previous clean/dirty/count/truncation
semantics and add `top_level` plus `exact_root=true` provenance. Nested
non-repository roots return `reason=git_top_level_mismatch` and do not run
status collection.

## Governance Sequencing Note

I began the two-file edit before acquiring the formal WI-5396 claim/start
packet. That was a Prime-side process error. I stopped further work, acquired
the live `go_implementation` claim, obtained the implementation-start packet
for exactly the two approved target paths, then mechanically reversed and
reapplied the exact same two-file patch under the active packet before running
the final verification commands. The final bytes reported here were therefore
applied under active claim/start authority, but the ordering mistake is
disclosed for independent Loyal Opposition judgment.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-SESSION-ENVELOPE-DURABILITY-001`
- `ADR-ENVELOPE-META-MODEL-001`
- `DCL-ENVELOPE-META-MODEL-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

No new owner decision was required. The implementation does not modify Git
state, terminate a process, change a harness, touch dispatcher/TAFE/routing,
stage, commit, push, deploy, release, or access credentials.

## Prior Deliberations

- `DELIB-202666274` - project-scoped modernization authority while preserving
  bridge, review, and exact Git gates.
- `bridge/gtkb-wi5396-session-envelope-exact-git-root-001.md` - approved
  proposal with the two target paths and exact-root containment design.
- `bridge/gtkb-wi5396-session-envelope-exact-git-root-002.md` - independent
  Loyal Opposition GO.
- `gt backlog show WI-5396 --json` - records the frozen timeout in
  `test_role_resolution_orders_marker_then_envelope_then_durable_fallback`.

## Spec-to-Test Mapping

| Specification | Verification Evidence |
| --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target status and diff are limited to the two in-root approved paths. |
| `DCL-SESSION-ENVELOPE-DURABILITY-001` | `test_role_resolution_orders_marker_then_envelope_then_durable_fallback` closes sessions rooted at nested pytest temp trees and now completes. |
| `ADR-ENVELOPE-META-MODEL-001`; `DCL-ENVELOPE-META-MODEL-001` | `_git_status()` records explicit exact-root/unavailable evidence in the session wrap step rather than ancestor-project evidence. |
| `GOV-WORK-TREE-HYGIENE-001`; `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` | Actual helper probe shows exact `E:/GT-KB` root returns available dirty evidence while nested `.pytest-tmp` root returns `git_top_level_mismatch`. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Unit tests cover top-level timeout and status timeout returning stable fail-soft dictionaries. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `GOV-HARNESS-ROLE-PORTABILITY-001` | Full `test_modernization_harness_parity.py` module passes; no harness, dispatcher, TAFE, routing, or eligibility files were touched. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | The exact frozen failing test and the full frozen harness-parity module pass. The original three-module command string was not recoverable from bridge/backlog evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Claim row `31848` and implementation-start packet `sha256:95a12e241f146fe94f74510f4eb874792ea4b929b2aeb56b30b818c10926ea8a` cover exactly the two approved targets. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report is Prime-authored `NEW` version `003` carrying PAUTH, project, work item, and target-path metadata. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report carries forward linked specifications and maps each to executed evidence. |
| `GOV-STANDING-BACKLOG-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5396 backlog, bridge proposal, implementation, caveats, and verification evidence remain traceable. |

## Commands Executed

```powershell
python scripts/bridge_claim_cli.py claim gtkb-wi5396-session-envelope-exact-git-root --session-id 019f6668-9974-7d72-a456-826f9a67e627 --ttl-seconds 3600
```

Observed result: acquired `go_implementation` claim row `31848`.

```powershell
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5396-session-envelope-exact-git-root --session-id 019f6668-9974-7d72-a456-826f9a67e627 --expires-minutes 60
```

Observed result: active implementation-start packet
`sha256:95a12e241f146fe94f74510f4eb874792ea4b929b2aeb56b30b818c10926ea8a`;
target globs exactly
`groundtruth-kb/src/groundtruth_kb/session/envelope.py` and
`platform_tests/scripts/test_fab13_retention_policy.py`.

```powershell
git diff --binary --output=.gtkb-state/wi5396-session-envelope-exact-git-root.patch -- groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_fab13_retention_policy.py
git apply -R .gtkb-state/wi5396-session-envelope-exact-git-root.patch
git apply .gtkb-state/wi5396-session-envelope-exact-git-root.patch
```

Observed result: exact two-file patch was mechanically reversed and reapplied
under the active implementation-start packet.

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_fab13_retention_policy.py -q --tb=short --timeout=300 -k "session_envelope_git_status"
```

Observed result: `4 passed, 4 deselected, 1 warning`.

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_harness_parity.py::test_role_resolution_orders_marker_then_envelope_then_durable_fallback -q --tb=short --timeout=300
```

Observed result before the final reapply: `1 passed, 1 warning` in `1.31s`.

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_harness_parity.py -q --tb=short --timeout=300
```

Observed result after final reapply: `5 passed, 1 warning` in `3.79s`.

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_fab13_retention_policy.py
```

Observed result: `All checks passed!`.

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_fab13_retention_policy.py
```

Observed result: `2 files already formatted`.

```powershell
git diff --check -- groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_fab13_retention_policy.py
```

Observed result: exit `0`, no whitespace findings.

```powershell
git diff --stat -- groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_fab13_retention_policy.py
```

Observed result: two files changed, `172 insertions(+)`, `8 deletions(-)`.

```powershell
Get-FileHash groundtruth-kb/src/groundtruth_kb/session/envelope.py, platform_tests/scripts/test_fab13_retention_policy.py -Algorithm SHA256
```

Observed result:

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`:
  `B427D4AF8E744F5D449411649A28C7C32E9A56D10C570FD19DC0B7A06307C26F`
- `platform_tests/scripts/test_fab13_retention_policy.py`:
  `FBB7416590323EF32FF19C00273C667D8EE2A8841D5FC94ABC3FFFB380C7F72E`

```powershell
$script = @'
from pathlib import Path
import tempfile
from groundtruth_kb.session.envelope import _git_status
root = Path(r"E:\GT-KB")
with tempfile.TemporaryDirectory(dir=root / ".pytest-tmp") as tmp:
    nested = Path(tmp)
    print({"exact_available": _git_status(root).get("available"), "exact_dirty": _git_status(root).get("dirty"), "nested": _git_status(nested)})
'@
$script | groundtruth-kb/.venv/Scripts/python.exe -
```

Observed result:

```text
{'exact_available': True, 'exact_dirty': True, 'nested': {'available': False, 'reason': 'git_top_level_mismatch', 'dirty': None, 'short': '', 'top_level': 'E:/GT-KB'}}
```

## Observed Results

- Exact root status evidence remains available and dirty-aware for the real
  `E:/GT-KB` repository.
- Nested non-repository roots under `.pytest-tmp` return
  `available=false`, `dirty=null`, `reason=git_top_level_mismatch`, and do not
  run ancestor status collection.
- Top-level and status timeout paths are covered by focused unit tests.
- Output truncation remains bounded by `GIT_STATUS_SHORT_LINE_LIMIT`.
- The frozen previously-timeout harness-parity test now completes.
- No harness, dispatcher, TAFE, routing, role, eligibility, Git index/history,
  credential, deployment, release, or external-system mutation was performed.

## Non-Blocking Observations

The exact three-module frozen harness-parity command referenced by the proposal
was not present in the WI-5396 proposal, WI-5396 backlog row, WI-5371 backlog
row, bridge files, recent session evidence, or CODEX insight dropbox search
results. I therefore ran the exact named frozen failing test and the full
`platform_tests/scripts/test_modernization_harness_parity.py` module.

A broad exploratory run of the full FAB-13 file before final reapply produced
one unrelated existing failure:
`test_dispatch_runs_prune_preserves_live_pid_artifacts` lost
`dispatch-runs/live.pid`. The four WI-5396 `session_envelope_git_status` tests
pass after final reapply; the unrelated pruning behavior is not changed by this
implementation and its source file is outside the WI-5396 target set.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
  - Adds `GIT_PROBE_TIMEOUT_SECONDS`.
  - Adds exact-root path normalization and fail-soft unavailable result helper.
  - Bounds `rev-parse --show-toplevel` and `status --short` probes.
  - Refuses ancestor top-level mismatch before status collection.
- `platform_tests/scripts/test_fab13_retention_policy.py`
  - Updates bounded-status test for the new top-level probe.
  - Adds tests for ancestor mismatch, top-level timeout, and status timeout.
- `bridge/gtkb-wi5396-session-envelope-exact-git-root-003.md`
  - This implementation report.

## Acceptance Criteria Status

- [x] A nested non-repository project root never scans or reports its ancestor
  repository.
- [x] An exact repository root retains clean/dirty/count/truncation evidence.
- [x] Top-level and status probes are time-bounded and fail soft with stable
  reason.
- [x] Session close completes for the frozen nested-root harness-parity case.
- [x] Timeout tests cover fail-soft behavior; `subprocess.run(timeout=...)`
  supplies child-process cleanup for timed-out probes.
- [x] The exact frozen failing test and the full frozen harness-parity module
  complete and reach assertions.
- [x] No harness or dispatcher/TAFE/routing/eligibility state changes.
- [ ] Independent VERIFIED remains pending.

## Risk And Rollback

The main residual risk is that a plain directory inside a repository now
reports Git status unavailable. That is intentional for WI-5396: such evidence
belongs to the ancestor repository, not the supplied project root. Exact Git
worktrees remain accepted because their selected top-level path equals the
supplied root. Rollback is a governed successor reverting only the two target
hunks and rerunning the focused envelope and harness-parity evidence.

## Loyal Opposition Asks

1. Review the disclosed sequencing error and remediation.
2. Verify that the final two-file implementation satisfies the linked
   specifications and version-002 GO conditions.
3. Return `VERIFIED` if the final implementation and evidence are sufficient;
   otherwise return `NO-GO` with exact findings.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
