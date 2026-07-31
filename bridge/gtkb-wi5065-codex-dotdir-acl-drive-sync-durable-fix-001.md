NEW

# gtkb-wi5065-codex-dotdir-acl-drive-sync-durable-fix — Durable fix for recurring `.codex` ACL drift (foreign-SID deny ACEs re-materialized by Drive sync) that breaks Codex/A workspace-write sandbox (0xc0000142)

bridge_kind: prime_proposal
Document: gtkb-wi5065-codex-dotdir-acl-drive-sync-durable-fix
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-09 UTC

author_identity: Prime Builder (Claude Code)
author_harness_id: B
author_session_context_id: a7996a03-6874-411a-9c40-cee06222cedd
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5065

target_paths: [".driveignore", "scripts/repair_codex_dotdir_acl.ps1", "scripts/verify_codex_dispatch.py", "platform_tests/scripts/test_codex_dotdir_acl_repair.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-5065 was filed as "Codex/A headless live shell smoke fails Windows sandbox
setup 0xc0000142." Triage against live runtime state (2026-07-09) found the
originally-suspected cause (`--disable plugins`) is a red herring: the failing
2026-07-07 smoke already carried `--disable plugins` and still failed, while the
passing 2026-07-08 smoke differs only in being run *post-ACL-repair* (evidence
path `...disable-plugins-post-acl.stderr.log`). The real root cause is the
`.codex` directory ACL.

`verify_codex_dispatch.py` (via reliable Windows PowerShell 5.1) reports the
`.codex` ACL broken again on 2026-07-09: `codex_dotdir_acl_ok: false`,
`needs_repair: true`, `risky_deny_count: 2`. Both risky-Deny ACEs belong to a
single **foreign, unresolvable SID**
(`S-1-5-21-2908765920-875073000-2352713335-4168283502`) whose authority prefix
differs entirely from this machine's
(`S-1-5-21-955887351-2727327028-1487890216-*`). One ACE is inheritable
(`ContainerInherit, ObjectInherit, InheritOnly`), so it propagates through the
`.codex` tree and breaks the Codex `workspace-write` sandbox setup (0xc0000142).
The 2026-07-08 one-shot repair did **not** persist — the foreign deny ACEs
re-appeared within ~a day. `E:` is Google-Drive-synced (the same corruption
class the root-boundary snapshot/rehearsal exceptions and the existing
`.driveignore` entries exist for: S311 SQLite corruption, dropped `.git`
objects, `.env.local` replication). `.codex/` is currently NOT excluded from
Drive sync, so Drive re-materializes files carrying the foreign-authority ACEs
on each sync — the recurring-drift mechanism.

A secondary defect surfaced during triage: `repair_codex_dotdir_acl.ps1` calls
`[System.IO.Directory]::GetAccessControl` / `[System.IO.File]::GetAccessControl`,
which exist in Windows PowerShell 5.1 but were removed in .NET Core /
PowerShell 7. Under `pwsh` the script throws on every path and falsely reports
`risky_deny_count: 0` — a false-clean ACL result for any caller that reaches it
via `pwsh`.

This proposal implements the owner-approved **scope A (combination)** durable
fix:

1. **Stop the source** — add `.codex/` to `.driveignore` so Drive stops
   re-materializing the foreign-SID ACEs (mirrors the `.git/` and `.gtkb-state/`
   precedent; git remains the durable backup for the tracked `.codex` content,
   which physically stays in `E:\GT-KB`, satisfying the root boundary).
2. **Fix the check/repair reliability** — make `repair_codex_dotdir_acl.ps1`
   PowerShell-7-compatible so the ACL check/repair produces correct results
   regardless of shell.
3. **Belt-and-suspenders** — add an idempotent, opt-in pre-attestation ACL
   auto-repair in the Codex readiness path (`verify_codex_dispatch.py`), forcing
   Windows PowerShell 5.1 (or the PS7-fixed path from item 2), so any foreign
   deny that reappears before a sync-exclusion settles is stripped just-in-time
   before the no-window smoke/dispatch. This closes WI-5065 durably even if the
   Drive-sync inference is only partly correct.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the append-only bridge audit trail this proposal is filed under.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites the governing specs constraining the work.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the proposal declares its Project / Work Item / Project Authorization linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan derives focused tests from the linked requirements.
- `GOV-STANDING-BACKLOG-001` — WI-5065 is a work item in the canonical MemBase backlog under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `GOV-RELIABILITY-FAST-LANE-001` — this is a reliability defect repair executed under the reliability fast-lane standing authorization (`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the triage findings and the owner scope decision are preserved as durable artifacts (this proposal, the linked WI, and the owner-decision evidence) rather than chat-only context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the durable-fix work is expressed as bounded, reviewable artifacts (bridge proposal → GO → implementation report → VERIFIED).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — WI-5065's lifecycle advances through the standard defect-fix triggers (proposal → review → implement → verify) with recorded state transitions.

## Prior Deliberations

- _No directly on-point Deliberation Archive precedent exists for the `.codex` ACL / Drive-sync foreign-ACE drift; the two deliberation searches run this session (`codex dotdir acl drive sync sandbox 0xc0000142 foreign sid`; `driveignore acl repair recurring drift codex readiness`) returned only tangential verdicts._
- Related F/dispatch reliability precedent: `bridge/gtkb-wi5051-openrouter-ssl-bad-record-mac-authorization-002.md` (WI-5051 verification-only closure) established the "transient-vs-persistent, confirm live before closing" discipline this fix honors for the sibling WI-5064.
- Related no-window/containment precedent: `bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-004.md` (Codex no-window containment) is the adjacent Codex-dispatch reliability work.
- Related sync/regen-churn hygiene precedent: `bridge/gtkb-wi4980-runtime-projection-tracking-hygiene-004.md` (stop the sync layer from perpetually re-dirtying harness runtime state) is the same failure class as excluding `.codex/` from Drive here — the durable backup is git/MemBase, not file-level Drive sync.

## Owner Decisions / Input

This proposal's *implementation authority* is the project-scoped standing
authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (reliability
fast-lane). Its *approach* was chosen by the owner via `AskUserQuestion` in this
interactive session (2026-07-09), detected_via: ask_user_question:

- WI-5065 disposition: owner selected **"Durable root-cause first"** — investigate why the ACL keeps regressing before any re-repair, and file a bridge proposal for the durable fix + the pwsh-incompat script bug.
- Fix scope: owner selected **"A — Combination"** — `.driveignore` exclusion of `.codex/` + idempotent pre-dispatch ACL auto-repair + fix the `repair_codex_dotdir_acl.ps1` pwsh-incompatibility.

No further owner decision is required to proceed to Loyal Opposition review.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements are WI-5065's
acceptance summary ("Codex/A live no-window smoke can run a single shell command
under the approved headless execution envelope with no visible window detection
and no Windows sandbox 0xc0000142 failure; dispatcher no longer reports
codex_dispatch_not_ready for A"), `GOV-RELIABILITY-FAST-LANE-001` (reliability
fast-lane for defect fixes), and the standing PAUTH scope. This is a defect
repair; no new or revised requirement is required before implementation.

Scope reconciliation note (carried into the implementation report): WI-5065's
original framing named A as blocked for *Prime Builder* work, but A's current
registry role is `loyal-opposition`. The operative acceptance clause is
therefore "dispatcher no longer reports `codex_dispatch_not_ready` for A" (A
returning to the dispatchable LO pool), not the moot "process Prime Builder work
headlessly" clause.

## Spec-Derived Verification Plan

Focused tests land in `platform_tests/scripts/test_codex_dotdir_acl_repair.py`.
Reproducible evidence via the repo venv interpreter:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_codex_dotdir_acl_repair.py -q --no-header
```

Spec-to-test mapping:

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` + WI-5065 acceptance →
  - **T1 (pwsh-7 compatibility):** invoke `repair_codex_dotdir_acl.ps1 -Mode Check -Json` under `pwsh` (PowerShell 7) against a fixture directory and assert the output contains **no** `GetAccessControl`/`SetAccessControl` method-invocation errors and returns a well-formed `risky_deny_count` (proving the false-clean-under-pwsh defect is fixed).
  - **T2 (`.driveignore` source exclusion):** assert `.driveignore` contains a `.codex/` exclusion entry (with the file's existing gitignore-syntax conventions), so Drive no longer syncs the ACL-carrying tree.
  - **T3 (idempotent auto-repair):** assert `verify_codex_dispatch.py`, invoked in its repair-enabled readiness mode against a fixture with a synthetic risky-Deny ACE, escalates Check→Repair, strips the risky Deny, and reports `codex_dotdir_acl_ok: true` on the post-repair recheck; and that a second invocation is a no-op (idempotence).
- `GOV-RELIABILITY-FAST-LANE-001` → the change set is bounded to the four declared `target_paths`; the full focused suite plus `ruff check` and `ruff format --check` on the changed Python are run before the implementation report is filed.

Live-confirmation acceptance (recorded in the implementation report, owner/control-plane run since the harness cannot self-launch Codex per DIRECT-HARNESS-INVOKE-BAN): after the fix, a fresh Codex no-window smoke passes and `verify_codex_dispatch.py` reports `codex_dotdir_acl_ok: true` + `live_headless_ready` with A no longer `codex_dispatch_not_ready`.

## Risk / Rollback

- **Risk — Drive backup scope:** excluding `.codex/` from Drive stops cloud-backup of Codex config, consistent with the existing `.git/` and `.gtkb-state/` exclusions; git remains the durable backup for tracked `.codex` content. Low risk.
- **Risk — ACL mutation:** the auto-repair modifies `.codex` ACLs. It is scoped to the `.codex` tree, idempotent, opt-in (readiness/pre-dispatch context only, not the pure read-only check path), and uses the same `repair_codex_dotdir_acl.ps1` logic already trusted for manual repair. Medium-low risk.
- **Risk — PS script behavior change:** the pwsh-compat fix changes the ACL read/write mechanism; T1 + the existing 5.1 path guard against regression. Medium-low risk.
- **Rollback:** single-commit revert restores the prior `.driveignore`, `repair_codex_dotdir_acl.ps1`, and `verify_codex_dispatch.py`; no data migration or KB mutation is involved.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5065-codex-dotdir-acl-drive-sync-durable-fix`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — repairs broken, recurring behavior (foreign-SID ACL drift breaking Codex/A headless dispatch, plus the pwsh-incompatible ACL check/repair). The added opt-in auto-repair and `.driveignore` entry serve the defect repair; no new user-facing capability surface is introduced.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
