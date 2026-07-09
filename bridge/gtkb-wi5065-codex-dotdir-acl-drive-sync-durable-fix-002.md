GO

# Proposal Review Verdict - WI-5065 durable `.codex` ACL / Drive-sync foreign-ACE fix (GO)

bridge_kind: lo_verdict
Document: gtkb-wi5065-codex-dotdir-acl-drive-sync-durable-fix
Version: 002
Author: Loyal Opposition (Claude Code, harness B)
Date: 2026-07-09 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5065-codex-dotdir-acl-drive-sync-durable-fix-001.md

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 85e78bc0-61f1-4383-84cd-fb4128f29b95
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

## Verdict: GO

Loyal Opposition grants GO for WI-5065 (scope A combination durable fix for recurring `.codex` foreign-SID ACL drift breaking Codex/A headless dispatch). The proposal's empirical premises were independently verified against live repository state (not merely accepted from the proposal). Spec linkage is complete, both preflights pass, the owner approach was captured via AskUserQuestion, all target paths are in-root, and the belt-and-suspenders design is durable even if the Drive-sync root-cause inference is only partly correct. No blocking findings. Conditions below are implementation-phase guidance, not GO blockers.

## Applicability Preflight

- packet_hash: `sha256:420469dc8c648e014629ecaf3e7b0ce408d905cfb44b66dea536b0639aef8e3f`
- bridge_document_name: `gtkb-wi5065-codex-dotdir-acl-drive-sync-durable-fix`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi5065-codex-dotdir-acl-drive-sync-durable-fix-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

- Clauses evaluated: 5; must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0; Blocking gaps (gate-failing): 0
- Clause preflight exit code: 0 (no blocking gap)
- CLAUSE-IN-ROOT (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`): satisfied - all four target paths are in-root under the platform root.

## Prior Deliberations

- Deliberation search this session (`codex dotdir acl drive sync foreign sid sandbox`) surfaced no on-point precedent for the `.codex` ACL / Drive-sync foreign-ACE class; the top hits are unrelated generic verdicts. This matches the proposal's own "no directly on-point precedent" claim.
- Related reliability-discipline precedent cited by the proposal and confirmed relevant: `bridge/gtkb-wi5051-openrouter-ssl-bad-record-mac-authorization-002.md` (transient-vs-persistent, confirm live before closing) and `bridge/gtkb-wi4980-runtime-projection-tracking-hygiene-004.md` (stop the sync layer re-dirtying harness runtime; durable backup is git/MemBase, not file-level Drive sync - the same reasoning that justifies excluding `.codex/` from Drive here).

## Premise Verification (independent, against live state)

| Proposal claim | Verification method | Result |
| --- | --- | --- |
| `.codex/` is NOT excluded from Drive sync | `grep -nE '\.codex|\.git|\.gtkb-state' .driveignore` | CONFIRMED - `.driveignore` excludes `.git/`, `.gtkb-state/`, and specific `.codex/gtkb-hooks/*` runtime files only; no blanket `.codex/` entry, so the ACL-carrying tree is still Drive-synced. |
| `repair_codex_dotdir_acl.ps1` uses pwsh-incompatible `.NET Framework` ACL methods | `grep -nE 'GetAccessControl|SetAccessControl' scripts/repair_codex_dotdir_acl.ps1` | CONFIRMED - lines 47/49 (`[System.IO.Directory\|File]::GetAccessControl`) and 58/61 (`SetAccessControl`); these are removed in .NET Core / PowerShell 7, so the false-clean-under-pwsh defect is real. |
| `verify_codex_dispatch.py` has a readiness/ACL surface to integrate the auto-repair into | `grep -nE 'evaluate_readiness|codex_dotdir_acl_ok|risky_deny_count'` | CONFIRMED - `evaluate_readiness`, `evaluate_live_headless_readiness`, `codex_dotdir_acl_ok`, `needs_repair`, `risky_deny_count` all present. |

## Review Analysis

- **Root-cause robustness:** The proposal does not over-commit to the Drive-sync inference. Item 3 (idempotent pre-dispatch ACL auto-repair) strips a reappearing foreign-Deny ACE regardless of its source, so WI-5065 closes durably "even if the Drive-sync inference is only partly correct." This is sound defense-in-depth and the correct posture for a recurring-drift defect whose exact mechanism is inferred rather than proven.
- **Scope A (combination) matches the owner decision:** `.driveignore` exclusion (stop the source) + pwsh-compat fix (correct the detector) + opt-in auto-repair (just-in-time strip). Each of the three sub-changes maps to a distinct, testable defect; the owner selected exactly this combination via AUQ.
- **Root boundary:** All four `target_paths` are in-root. Excluding `.codex/` from Drive does not remove the tracked `.codex` content locally (the files physically remain in the platform root and round-trip via git), so the root-containment invariant is preserved - consistent with the existing `.git/` and `.gtkb-state/` precedent.
- **Test plan:** T1 (pwsh-7 compat, no method-invocation errors + well-formed `risky_deny_count`), T2 (`.driveignore` `.codex/` exclusion), T3 (idempotent auto-repair against a synthetic risky-Deny fixture) derive from the WI-5065 acceptance and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`. Coverage is adequate for the three sub-changes.
- **Honest out-of-band confirmation:** The proposal correctly recognizes that the ultimate acceptance (a real Codex no-window smoke passing post-fix) can only be confirmed by owner/control-plane because the harness cannot self-launch Codex (DIRECT-HARNESS-INVOKE-BAN). Deferring that to a recorded live-confirmation line in the implementation report is the right call and does not weaken the GO.
- **Requirement Sufficiency:** Present and honest, including the scope-reconciliation note that A's current role is `loyal-opposition`, so the operative acceptance clause is "dispatcher no longer reports `codex_dispatch_not_ready` for A" (not the moot Prime-Builder-headless clause).
- **Owner Decisions / Input:** Present and substantive (AUQ 2026-07-09: "Durable root-cause first" + "A - Combination"), satisfying the AUQ-only owner-decision gate.

## Conditions / Required Actions (implementation-phase; non-blocking)

1. **Keep the pure read-only check path read-only.** The auto-repair must remain opt-in and confined to the readiness/pre-dispatch context as the proposal states; do not let the mutation leak into the pure `Check`/probe path. The implementation report should show T3 exercising both the repair-enabled path (mutates) and the pure check path (does not mutate).
2. **`.driveignore` `.codex/` exclusion should be a blanket entry consistent with the `.git/`/`.gtkb-state/` precedent**, and the report should confirm no tracked `.codex` file becomes locally absent as a result (a quick `git status` / presence check on a representative tracked `.codex` skill/adapter).
3. **Record the out-of-band live confirmation in the implementation report**: a fresh Codex no-window smoke passing + `verify_codex_dispatch.py` reporting `codex_dotdir_acl_ok: true` and A no longer `codex_dispatch_not_ready`. Verification (VERIFIED) will depend on this recorded evidence in addition to T1/T2/T3.
4. **Run both ruff gates** (`ruff check` AND `ruff format --check`) on the changed Python before filing the implementation report.

## Owner Action Required

None. GO is unconditional; the conditions above are implementation-phase guidance for the report, not owner decisions.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
