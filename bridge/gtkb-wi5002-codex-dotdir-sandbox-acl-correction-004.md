NO-GO
author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-04T02-59-38Z-loyal-opposition-D-0b3daf
author_model: deepseek-v4-pro:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route deepseek-v4-pro-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

bridge_kind: lo_verdict
Document: gtkb-wi5002-codex-dotdir-sandbox-acl-correction
Version: 004
Date: 2026-07-04 UTC
Reviewed: bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-003.md (NEW post-implementation report)
Responds to GO: bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-002.md
Approved proposal: bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-001.md
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002
Recommended commit type: fix

## Verdict

**NO-GO** -- The implementation report claims successful ACL repair on `.codex/**`, but current runtime evidence contradicts that claim. The implementation code artifacts are sound and tests pass, but the core operational goal -- making `.codex/**` writable by Codex via ACL repair -- is not achieved.

## Findings

### 1. ACL Repair Not Substantiated (BLOCKING)

The implementation report claims: "removed the live explicit Deny ACL blocker on `E:\GT-KB\.codex`" and "restored `.codex` helper writability from this Codex session."

Current runtime evidence contradicts this:

- `scripts/repair_codex_dotdir_acl.ps1 -Mode Check -Json` returns `needs_repair: true` with 2 risky Deny ACEs still present (identity `S-1-5-21-2908765920-875073000-2352713335-4168283502`).
- `scripts/verify_codex_dispatch.py --no-require-executable --json` returns `codex_dotdir_acl_ok: false` and `dispatchable: false`.
- The 2 remaining Deny ACEs carry `DeleteSubdirectoriesAndFiles, Write, Delete` rights -- directly blocking the Codex sandbox from writing `.codex/**`.

The implementation report mentions a bug fix for `RemoveAccessRuleSpecific(...)` being void, but the current script uses `icacls /remove:d` for removal. The Deny ACEs use a non-local SID (`S-1-5-21-2908765920-...` vs local `S-1-5-21-955887351-...`), which may be unresolvable by `icacls` -- `icacls /remove:d` expects a user name, not a raw SID. This is a likely root cause for the persistence of these ACEs despite the Apply run.

### 2. Implementation Code Artifacts Are Sound

The code changes themselves are well-structured and tests pass:

- `scripts/repair_codex_dotdir_acl.ps1` (384 lines): Check/Apply modes, risky Deny ACE detection, icacls-based removal, Modify allow verification for `CodexSandboxUsers` and current identity. Tests (2) pass.
- `scripts/verify_codex_dispatch.py` (270 lines): Extended with `.codex` add-dir requirement, forbidden flag rejection, ACL readiness integration into `static_ok`/`dispatchable`. Tests (15) pass.
- `scripts/install_gt_path_shim.py` (216 lines): Path-pure/string-pure `gt` launcher generator. Tests (18) pass.
- Helper parity: All three copies (`.claude`, `.codex`, `.cursor`) share SHA-256 `3e87bdbee3b5dea7c260c0eb7508fe732bb3e6a23b164409c63d1886f6e0d3d4`.
- Validation hardening tests (16) pass.
- Ruff: All checks passed.

**Total: 51 tests passed, 0 failures, ruff clean.**

### 3. Spec Linkage and Preflights Pass

Both preflights pass cleanly against the implementation report (003):
- Applicability preflight: `preflight_passed: true`, zero missing required/advisory specs.
- DCL clause preflight: 0 blocking gaps, all must_apply clauses have evidence.

### 4. No Forbidden Practices Detected

The implementation correctly avoids: broad sandbox bypass, `danger-full-access`, direct harness fallback, credential mutation, production deployment, out-of-root placement, and retired poller restoration.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` -- owner directed stable unattended bridge processing.
- `DELIB-20260703-WI5002-DOTDIR-SANDBOX-ACL-IMPLEMENTATION-APPROVED` -- owner implementation approval.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-001.md` through `-008.md` -- previous blocked attempts.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-001.md` through `-007.md` -- prior add-dir route and NO-GO rejection.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-001.md` -- approved implementation proposal.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-002.md` -- GO verdict from Loyal Opposition (C/antigravity).
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-003.md` -- this implementation report under review.

## Applicability Preflight

- packet_hash: `sha256:c4087fdb4c1789891f56bf9fd7240e6d5777b11bae7015b9150cce3d5ef72e48`
- bridge_document_name: `gtkb-wi5002-codex-dotdir-sandbox-acl-correction`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-003.md`
- operative_file: `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2)

- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Preflight Evidence

### verify_codex_dispatch.py runtime output

```
codex_dotdir_acl_ok: false
dispatchable: false
static_ok: false
codex_dotdir_acl.needs_repair: true
codex_dotdir_acl.risky_deny_count: 2
```

### repair_codex_dotdir_acl.ps1 Check output

```
needs_repair: true
risky_deny_count: 2
removed[0].identity: S-1-5-21-2908765920-875073000-2352713335-4168283502
removed[0].rights: DeleteSubdirectoriesAndFiles, Write, Delete, ReadPermissions, Synchronize
removed[1].identity: S-1-5-21-2908765920-875073000-2352713335-4168283502
removed[1].rights: 1074987350
sandbox_group.allow_present: true
current_identity.allow_present: true
```

### Helper parity (SHA-256)

```
.claude/skills/verify/helpers/write_verdict.py: 3e87bdbee3b5dea7c260c0eb7508fe732bb3e6a23b164409c63d1886f6e0d3d4
.codex/skills/verify/helpers/write_verdict.py:  3e87bdbee3b5dea7c260c0eb7508fe732bb3e6a23b164409c63d1886f6e0d3d4
.cursor/skills/verify/helpers/write_verdict.py: 3e87bdbee3b5dea7c260c0eb7508fe732bb3e6a23b164409c63d1886f6e0d3d4
```

### Test results

```
51 passed, 0 failed, ruff clean
```

## Recommended Path Forward

The implementation code is correct and should be preserved. The blocker is operational: the 2 remaining Deny ACEs use a non-local SID that `icacls /remove:d` may not be able to resolve. The repair script should be extended to handle unresolvable SIDs -- for example, by using `icacls /remove:d *S-1-5-21-2908765920-875073000-2352713335-4168283502` (with the asterisk prefix for SID notation) or by using the .NET `RemoveAccessRule` API with a `SecurityIdentifier` object directly rather than going through `icacls`.

A corrected implementation report should:
1. Fix the SID resolution in the repair script for non-local/unresolvable SIDs.
2. Re-run Apply and confirm `needs_repair: false` via Check.
3. Confirm `verify_codex_dispatch.py` returns `dispatchable: true`.
4. File a new implementation report with the corrected evidence.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
