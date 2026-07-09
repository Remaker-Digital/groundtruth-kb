NEW

# GT-KB Bridge Implementation Report - gtkb-wi5065-codex-dotdir-acl-drive-sync-durable-fix - 003

bridge_kind: implementation_report
Document: gtkb-wi5065-codex-dotdir-acl-drive-sync-durable-fix
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5065-codex-dotdir-acl-drive-sync-durable-fix-002.md
Approved proposal: bridge/gtkb-wi5065-codex-dotdir-acl-drive-sync-durable-fix-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5065
Recommended commit type: fix:

author_identity: Prime Builder (Claude Code)
author_harness_id: B
author_session_context_id: a7996a03-6874-411a-9c40-cee06222cedd
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

## Implementation Claim

The recurring `.codex` ACL drift (foreign-SID Deny ACEs re-materialized by
Google Drive, breaking the Codex workspace-write sandbox with `0xc0000142`) is
addressed by the owner-approved scope-A combination:

1. **Source exclusion** — `.driveignore` now excludes `.codex/`, so Google Drive
   stops re-syncing the foreign-authority ACEs (same rationale as the existing
   `.git/` and `.gtkb-state/` exclusions; git remains the durable backup, and
   `.codex` stays physically in `E:\GT-KB`).
2. **PowerShell-7 reliability** — `scripts/repair_codex_dotdir_acl.ps1` now uses
   `Get-Acl`/`Set-Acl` (cross-version) instead of the .NET Core-removed
   `[System.IO.Directory]::GetAccessControl` / `SetAccessControl` statics that
   threw under pwsh and falsely reported `risky_deny_count=0`.
3. **Idempotent pre-attestation auto-repair** — `verify_codex_dispatch.py` gains
   an opt-in `--repair-acl` (threaded to `evaluate_readiness(repair_acl=...)` ->
   `_check_codex_dotdir_acl(repair=...)`): when the read-only Check finds
   removable risky-Deny ACEs, it escalates to `-Mode Apply` and re-Checks. The
   default readiness path stays read-only.

## Files Changed

- `.driveignore` — add `.codex/` exclusion (WI-5065 comment block).
- `scripts/repair_codex_dotdir_acl.ps1` — `Get-AccessOnlyAcl`/`Set-AccessOnlyAcl` now use `Get-Acl`/`Set-Acl`.
- `scripts/verify_codex_dispatch.py` — `_check_codex_dotdir_acl(repair=...)` Check->Apply->re-Check; `evaluate_readiness(repair_acl=...)`; `--repair-acl` CLI flag.
- `platform_tests/scripts/test_codex_dotdir_acl_repair.py` (new).

## Specification Links

- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — Windows headless dispatch safety (the `0xc0000142` sandbox failure this repairs).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-gated source change.
- `GOV-RELIABILITY-FAST-LANE-001` — reliability defect repair under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec linkage carried forward.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived tests executed (below).
- `GOV-ENV-LOCAL-AUTHORITY-001` — no credential handling changed.
- `GOV-STANDING-BACKLOG-001` — WI-5065 backlog record.

## Specification-Derived Verification Plan

| Spec / surface | Executed verification evidence |
| --- | --- |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (PS7 reliability) | `test_repair_script_check_mode_is_pwsh7_compatible` runs `repair_codex_dotdir_acl.ps1 -Mode Check` under **pwsh 7** against a clean `.codex` fixture and asserts **no** `GetAccessControl` error + a valid integer `risky_deny_count` + `errors == []`. This directly proves the reported false-clean-under-pwsh bug is fixed. |
| Auto-repair escalation | `test_auto_repair_escalates_check_to_apply` (Check->Apply->Check), `test_default_check_is_read_only` (Check only), `test_no_apply_when_check_is_clean` (no Apply when clean). |
| Source exclusion | `test_driveignore_excludes_codex_dir` asserts `.codex/` is a `.driveignore` entry. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | pytest + ruff below. |

Executed commands and results:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_codex_dotdir_acl_repair.py -q --tb=short --no-header
=> 5 passed, 1 warning in 1.26s   (includes the live pwsh Check run)

groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/verify_codex_dispatch.py platform_tests/scripts/test_codex_dotdir_acl_repair.py
=> All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/verify_codex_dispatch.py platform_tests/scripts/test_codex_dotdir_acl_repair.py
=> 2 files already formatted
```

## Scope / Evidence Note (honest bounds)

- The script's valid modes are `Check`/`Apply`; the proposal's "Repair" wording maps to `-Mode Apply`, which the auto-repair uses.
- **Verified in this environment:** the PS7 read-compat (real pwsh Check, no `GetAccessControl` error), the `.driveignore` exclusion, and the auto-repair Check->Apply escalation (mocked subprocess).
- **NOT reproduced in this environment:** the live removal of the actual foreign-SID Deny ACE on the real drifted `.codex` (that requires the live corrupt ACL state, which cannot be safely staged here). Live acceptance — a fresh Codex no-window smoke passing and `verify_codex_dispatch` reporting `codex_dotdir_acl_ok: true` after a control-plane/owner-run `--repair-acl` — is the owner/control-plane confirmation step, consistent with WI-5065's acceptance and the DIRECT-HARNESS-INVOKE-BAN (the harness cannot self-launch Codex).
- Scope reconciliation (carried forward): WI-5065's original "Prime Builder work" framing is moot — Codex/A's current registry role is `loyal-opposition`; the operative acceptance clause is A returning to the dispatchable pool with no `codex_dispatch_not_ready`.

## Owner Decisions / Input

- Owner directed the durable-root-cause approach and selected **scope A (combination)** via `AskUserQuestion` (2026-07-09), and selected "All three, WI-5107 first" for the GO'd-fix implementation order. detected_via: ask_user_question.
- No credential, deployment, provider-account, or sandbox-weakening action was made.

## Recommended Commit Type

`fix:` — repairs a recurring reliability defect (foreign-SID `.codex` ACL drift breaking Codex headless dispatch) at its source (Drive exclusion), makes the ACL check/repair PS7-reliable, and adds an opt-in idempotent auto-repair; no new user-facing capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
