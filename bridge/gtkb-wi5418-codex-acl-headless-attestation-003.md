NEW

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-17T10-20-39Z
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; transcript-defined PB role; explicit worker envelope opened for WI-5418

# GT-KB Bridge Implementation Report - gtkb-wi5418-codex-acl-headless-attestation - 003

bridge_kind: implementation_report
Document: gtkb-wi5418-codex-acl-headless-attestation
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5418-codex-acl-headless-attestation-002.md
Approved proposal: bridge/gtkb-wi5418-codex-acl-headless-attestation-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5418
Recommended commit type: fix:

## Implementation Claim

Implemented the WI-5418 Codex `.codex` ACL attestation repair within the GO-approved target scope.

`scripts/repair_codex_dotdir_acl.ps1` now avoids `Microsoft.PowerShell.Security` module auto-load dependency when Windows PowerShell is launched with `CREATE_NO_WINDOW`. The ACL read/write helpers first use the .NET `Directory/File.GetAccessControl` and `SetAccessControl` statics available in Windows PowerShell, then fall back to `Get-Acl` / `Set-Acl` for PowerShell 7 where those statics are absent. The `CodexSandboxUsers` SID check now resolves through `NTAccount.Translate(...)` before falling back to `Get-LocalGroup`, so the no-window launcher does not falsely report the group as absent.

The script also stops descendant ACL scanning when the root `.codex` ACL cannot be read. That preserves fail-closed behavior but collapses launcher/capability defects into one root error instead of emitting one synthetic error per descendant.

Regression tests now cover the hidden-window PowerShell launcher path and verify that `scripts/verify_codex_dispatch.py` continues to invoke the ACL checker with the no-window subprocess disposition. `scripts/verify_codex_dispatch.py` itself required no source hunk: its wrapper behavior changed because the scoped PowerShell script now returns the correct JSON under the same launcher.

The implementation intentionally did not run live Apply mode against `E:\GT-KB\.codex`. After the code fix, live Check mode reports the real current state: two explicit risky Deny ACEs and zero synthetic module-load errors. That is the desired fail-closed, actionable result for WI-5310 proof renewal.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `GOV-HARNESS-ISOLATION-001`

## Owner Decisions / Input

No new owner decision was required by this implementation report. The implementation carries forward the active project authorization `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` and the independent GO at `bridge/gtkb-wi5418-codex-acl-headless-attestation-002.md`.

The current Codex process exposed only `CODEX_THREAD_ID=019f6f8b-9fd7-7142-93a8-5696dca44d85`, with no matching worker session envelope. Before acquiring the GO implementation claim, Prime Builder used the native session service to open a current Codex PB worker envelope for this transcript-defined PB session: `A-2026-07-17T10-20-39Z`, active work item `WI-5418`. That made the work-intent and implementation-start gates validate against a real open worker document instead of bypassing provenance.

## Prior Deliberations

- `bridge/gtkb-wi5418-codex-acl-headless-attestation-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5418-codex-acl-headless-attestation-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-wi5310-codex-effective-workspace-profile-008.md` - upstream NO-GO that names this `.codex` ACL repair as dependency D1.
- `DELIB-202666274` - owner authorization underlying the active Goose Harness Adoption PAUTH.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `python -m pytest platform_tests/scripts/test_codex_dotdir_acl_repair.py platform_tests/scripts/test_repair_codex_dotdir_acl.py platform_tests/scripts/test_verify_codex_dispatch.py -q --tb=short` passed. Tests now exercise the hidden-window PowerShell launcher, real risky-Deny detection, Apply cleanup on temp fixtures, PowerShell 7 compatibility, verifier no-window preservation, and fail-closed readiness normalization. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Work was performed only after latest GO, a fresh `go_implementation` claim for session `A-2026-07-17T10-20-39Z`, and an implementation-start packet for the five approved target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This implementation report carries forward linked specifications, command evidence, observed results, file-scope reconciliation, and acceptance criteria for independent Loyal Opposition verification. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-HARNESS-ISOLATION-001`, `GOV-STANDING-BACKLOG-001`, `SPEC-AUQ-POLICY-ENGINE-001` | Scoped diff changes only platform script/test targets. No adopter application files, dispatcher routing, live worker eligibility, credentials, leases, release state, or production deployment surfaces were modified. |

## Commands Run

- `gt session envelope open --harness-name codex --harness-id A --init-keyword "::init gtkb pb" --subject gtkb --role prime-builder --active-work-item-id WI-5418 --json`
- `python scripts/bridge_claim_cli.py claim gtkb-wi5418-codex-acl-headless-attestation --session-id A-2026-07-17T10-20-39Z --ttl-seconds 1800`
- `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5418-codex-acl-headless-attestation --session-id A-2026-07-17T10-20-39Z`
- `python scripts/bridge_claim_cli.py extend gtkb-wi5418-codex-acl-headless-attestation --session-id A-2026-07-17T10-20-39Z`
- no-window reproduction via `scripts.windows_subprocess.no_window_subprocess_kwargs()` invoking `scripts/repair_codex_dotdir_acl.ps1 -ProjectRoot E:\GT-KB -Mode Check -Json`
- `python scripts/verify_codex_dispatch.py --json`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/repair_codex_dotdir_acl.ps1 -ProjectRoot E:\GT-KB -Mode Check -Json`
- `pwsh -NoProfile -File scripts/repair_codex_dotdir_acl.ps1 -ProjectRoot E:\GT-KB -Mode Check -Json`
- `python -m pytest platform_tests/scripts/test_codex_dotdir_acl_repair.py platform_tests/scripts/test_repair_codex_dotdir_acl.py platform_tests/scripts/test_verify_codex_dispatch.py -q --tb=short`
- `python -m ruff check scripts/verify_codex_dispatch.py platform_tests/scripts/test_codex_dotdir_acl_repair.py platform_tests/scripts/test_repair_codex_dotdir_acl.py platform_tests/scripts/test_verify_codex_dispatch.py`
- `python -m ruff format --check scripts/verify_codex_dispatch.py platform_tests/scripts/test_codex_dotdir_acl_repair.py platform_tests/scripts/test_repair_codex_dotdir_acl.py platform_tests/scripts/test_verify_codex_dispatch.py`
- `python .claude/skills/bridge/helpers/impl_report_bridge.py plan gtkb-wi5418-codex-acl-headless-attestation --compact`
- `python scripts/bridge_claim_cli.py status gtkb-wi5418-codex-acl-headless-attestation`

## Observed Results

- Work-intent claim succeeded as `claim_kind: go_implementation`, `acting_role: prime-builder`, session `A-2026-07-17T10-20-39Z`.
- Implementation-start packet succeeded for latest status `GO`, active PAUTH `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE`, and exact target paths: `scripts/repair_codex_dotdir_acl.ps1`, `scripts/verify_codex_dispatch.py`, `platform_tests/scripts/test_codex_dotdir_acl_repair.py`, `platform_tests/scripts/test_repair_codex_dotdir_acl.py`, `platform_tests/scripts/test_verify_codex_dispatch.py`.
- Claim was extended once before focused verification. Final claim status remained active: latest bridge status `GO`, `expired: false`, `lapsed_go_implementation: false`, deadline `2026-07-17T11:20:48Z`, grace `2026-07-17T11:30:48Z`.
- Before the fix, the no-window ACL check returned `risky_deny_count: 0`, `errors_count: 218`, `sandbox_group.present: false`, and `current_identity.allow_present: false`, while direct PowerShell saw real Deny entries.
- After the fix, the no-window ACL check returned `risky_deny_count: 2`, `errors: []`, `sandbox_group.present: true`, `sandbox_group.allow_present: true`, `current_identity.allow_present: true`.
- After the fix, `python scripts/verify_codex_dispatch.py --json` still exited 1, but for the correct fail-closed reason: `codex_dotdir_acl.errors_count: 0`, `risky_deny_count: 2`, `current_identity.allow_present: true`, `sandbox_group.present: true`, and `needs_repair: true`. The remaining `static_ok: false` is expected until the real `.codex` Deny ACEs are repaired and the live no-window proof is renewed.
- Direct Windows PowerShell Check returned the same real ACL state: `checked_count: 218`, `risky_deny_count: 2`, `errors: []`.
- Direct PowerShell 7 Check remained compatible and returned the same real ACL state: `checked_count: 218`, `risky_deny_count: 2`, `errors: []`.
- Focused pytest result: `31 passed in 7.34s`.
- Ruff check result: `All checks passed!`
- Ruff format check result: `4 files already formatted`.

## Files Changed

Scoped implementation files changed by this work:

- `scripts/repair_codex_dotdir_acl.ps1`
- `platform_tests/scripts/test_codex_dotdir_acl_repair.py`
- `platform_tests/scripts/test_repair_codex_dotdir_acl.py`

Approved target paths not changed:

- `scripts/verify_codex_dispatch.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`

The broader worktree is heavily dirty from pre-existing and concurrent work; the bridge helper's plan mode reported `excluded_dirty_count: 1481`. The scoped `git status --short -- <approved-targets>` check showed only the three implementation files listed above.

Diff stat for the scoped implementation:

```text
 platform_tests/scripts/test_codex_dotdir_acl_repair.py | 20 ++++++
 platform_tests/scripts/test_repair_codex_dotdir_acl.py | 26 +++++++-
 scripts/repair_codex_dotdir_acl.ps1                    | 83 ++++++++++++++-------
 3 files changed, 99 insertions(+), 30 deletions(-)
```

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: The diff fixes Codex ACL attestation behavior and adds regression tests for the launcher path.

## Acceptance Criteria Status

- [x] Production no-window Windows PowerShell path reads `.codex` ACL state without `Microsoft.PowerShell.Security` module-load false errors.
- [x] Launcher/capability failures no longer fan out into one repeated synthetic error per descendant when the root ACL cannot be read.
- [x] PowerShell 7 remains compatible through the `Get-Acl` / `Set-Acl` fallback path.
- [x] Check mode remains read-only and reports actual risky Deny entries.
- [x] Apply mode remains opt-in and idempotent in temp-fixture tests: it removes explicit risky Deny ACEs, preserves unrelated state, and post-Check is clean.
- [x] Verifier no longer reports hundreds of synthetic unreadable entries from its own launcher; it fails closed on the two real live `.codex` risky Deny ACEs.
- [x] No console-window, dispatcher-state, TAFE, eligibility, lease, credential, release, deployment, or live-worker mutation was introduced.

## Risk And Rollback

Residual risk is moderate because this check sits on the Codex dispatch-readiness path. The implementation reduces that risk by keeping Check mode read-only, preserving fail-closed behavior on real ACL defects, using Windows PowerShell .NET ACL APIs only where available, and retaining PowerShell 7 fallback behavior covered by tests.

Rollback is removal of the scoped hunks in `scripts/repair_codex_dotdir_acl.ps1`, `platform_tests/scripts/test_codex_dotdir_acl_repair.py`, and `platform_tests/scripts/test_repair_codex_dotdir_acl.py`. No KB/database mutation, credential lifecycle, dispatcher routing change, release, deployment, or live `.codex` Apply repair was performed by this implementation. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify that the no-window ACL path now reports real risky Deny state instead of module-load noise.
2. Confirm that leaving the live `.codex` Apply repair to the subsequent WI-5310 proof-renewal flow is acceptable for this scoped verifier repair.
3. Return VERIFIED if the report and implementation satisfy WI-5418, otherwise return NO-GO with specific findings.
