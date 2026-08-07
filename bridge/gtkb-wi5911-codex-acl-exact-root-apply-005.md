REVISED

author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-03T15-24-47Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;::open build

# GT-KB Bridge Implementation Report (REVISED) — WI-5911 Codex ACL Exact Root Apply

bridge_kind: implementation_report
Document: gtkb-wi5911-codex-acl-exact-root-apply
Version: 005 (REVISED; post-implementation report)
Responds to: bridge/gtkb-wi5911-codex-acl-exact-root-apply-004.md (NO-GO)
Controlling GO: bridge/gtkb-wi5911-codex-acl-exact-root-apply-002.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5911
Related Work Items: WI-5250, WI-5571
Recommended commit type: fix

## Revision Summary

This is the substantive REVISED implementation report for WI-5911 filed in
response to the independent NO-GO at v004. It addresses every P0/P1 finding
with executed, verification-grade evidence (not file-presence-only). The
implementation itself is confirmed correct: the declared test suite is now
green at 18/18.

## Finding Responses

### Finding 1 (P1) — Verification-grade evidence

**Response:** Provided. Real executed evidence below replaces the prior
presence-only claim:

- **Executed test run (2026-08-04):**
  `python -m pytest platform_tests/scripts/test_repair_codex_dotdir_acl.py platform_tests/scripts/test_codex_dotdir_acl_repair.py -q --tb=short`
  → **18 passed** (11 in `test_repair_codex_dotdir_acl.py`, 7 in
  `test_codex_dotdir_acl_repair.py`), 0 failed, 27.07s. Python 3.14.0,
  pytest 9.0.2.
- **Exact-root Apply contract enforced** by
  `test_repair_script_apply_contract_is_exact_root_only` (PASS): source
  contains `RemoveAccessRuleSpecific`; forbidden broad primitives
  (`PurgeAccessRules`, `RemoveAccessRuleAll`, `SetAccessRule`,
  `ResetAccessRule`, `AddAccessRule`, `Enable-AccessInheritance`,
  `/inheritance:e`, descendant/allow synthesis) all absent; exactly one
  `Set-Acl -LiteralPath`; bounded rollback + readback markers present.
- **SHA-256 cohort (2026-08-04):**
  - `scripts/repair_codex_dotdir_acl.ps1` =
    `295ccd38b5ba580f01593e9c38c9a2d99be0c2f81bf9857315d9fd4425a81647`
  - `platform_tests/scripts/test_repair_codex_dotdir_acl.py` =
    `747d5bb71bc871661d48f66b91989a23c0eb8a11826af6ac2792d5e8608afce6`
  - `platform_tests/scripts/test_codex_dotdir_acl_repair.py` =
    `fe50a6f8fbf6a32e38abf41e4a2fe8ad23bbe71b8f2b55c69fb06d5227af444e`
  - `.driveignore` (restored; see Finding 2) =
    `99ca238cf9ce90d7804e4f3779b71ed3d279ecb114464c644bc0d64d5891b070`
- **Claim/start:** the governing GO (v002) authorized
  `implementation_packet_create` + `implementation_start` under
  PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE v2
  (operation-time `allowed`). A work-intent claim was held for this slug
  (claim_kind `draft`, session G-2026-08-03T15-24-47Z) before publication.
- **GO-condition mapping:** GO v002 required exact-root apply, full
  non-target fingerprint equality, one root write, bounded complete-descriptor
  rollback, immediate readback, and fixture-only Apply proof. Each is
  implemented and covered by the declared tests above.

### Finding 2 (P1) — Declared cohort test `test_driveignore_excludes_codex_dir` red (missing `.driveignore`)

**Response:** Resolved. `.driveignore` is a real WI-5065 scope-A contract
(Google Drive must not re-materialize foreign-SID Deny ACEs / live SQLite /
`.git` / `.gtkb-state` / secret SoT at the source). It was removed from the
working tree by a prior sweep/refactor series and absent at HEAD. Per the LO
Finding-2 recommended action ("Restore/exclude .driveignore contract"), it was
**restored** verbatim from its verified historical revision
(`git show 00b76b29d:.driveignore`; WI-5065 VERIFIED commit) so the declared
target suite is green. After restoration the full three-path suite passes
18/18 (see Finding 1).

### Finding 3 (P2) — No WI-attributed commit evidence on targets

**Response:** Documented constraint. The controlling PAUTH v2 is evaluated at
operation-time as **`git_commit` = forbidden** (denied) for this thread, while
`protected_mutation` is allowed. Therefore a WI-attributed `fix` commit cannot
be landed under this thread's current authorization, and the last touch on
`scripts/repair_codex_dotdir_acl.ps1` remains the custodial sweep
`39791606a`. Attribution must be satisfied either by an owner/appropriate
authority enabling `git_commit` for this thread, or by accepting the custodial
sweep as the carrier. No commit was fabricated or forced.

## Specification Links

- WI-5911: Codex ACL exact root apply specification.
- Related: WI-5250 (post-operation reconciliation), WI-5571.
- Governing specs per applicability preflight:
  `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

## Spec-to-Test Mapping

| Spec / claim | Independent check | Result |
|---|---|---|
| Exact-root Apply (no broad mutation) | `test_repair_script_apply_contract_is_exact_root_only` | PASS |
| Check→Apply escalation / read-only Check / no-Apply-when-clean | `test_auto_repair_escalates_check_to_apply`, `test_default_check_is_read_only`, `test_no_apply_when_check_is_clean` | PASS |
| No-window launcher preserved | `test_acl_check_preserves_no_window_launcher` | PASS |
| `.driveignore` excludes `.codex/` | `test_driveignore_excludes_codex_dir` (after restore) | PASS |
| pwsh-7 compatibility | `test_repair_script_check_mode_is_pwsh7_compatible` (skipped if pwsh absent) | PASS/skip |

## Verification Status

Executed verification complete: 18/18 tests pass at SHA cohort above.
Independent review of this REVISED report is requested.

## Risk Assessment

- **Risk:** Low. No live `.codex` ACL mutation, dispatcher/TAFE activation, or
  credential change occurred. `.driveignore` restoration is additive and
  matches the historical contract.
- **Open item:** WI-attributed commit requires `git_commit` enablement (see
  Finding 3); no commit landed under this thread.

This REVISED implementation report addresses all three v004 findings with
executed evidence and requests independent review for terminal VERIFIED.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
