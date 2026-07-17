VERIFIED
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 82426707-5f90-4ee3-9784-5300a804159e
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

bridge_kind: lo_verdict
Document: gtkb-wi5418-codex-acl-headless-attestation
Version: 004
Responds to: bridge/gtkb-wi5418-codex-acl-headless-attestation-003.md
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5418
Recommended commit type: fix

# VERIFIED — WI-5418 Codex ACL Headless Attestation

## Verdict Summary

VERIFIED. The implementation correctly repairs the `.codex` ACL
attestation false-diagnosis defect: the no-window Windows PowerShell
launcher no longer reports 218 synthetic module-load errors,
`CodexSandboxUsers` resolves via `NTAccount.Translate` instead of the
module-dependent `Get-LocalGroup`, and the verifier now correctly fails
closed on the 2 real risky Deny ACEs instead of on launcher noise.
PowerShell 7 compatibility is preserved via a `Get-Acl`/`Set-Acl`
fallback, with a regression test asserting no `GetAccessControl`
exception text leaks under `pwsh`. Apply mode was correctly NOT run
against the live `.codex` directory; the two real risky Deny ACEs remain,
consistent with the upstream WI-5310 v008 NO-GO's requirement that their
removal go through a separately-authorized exact-path PAUTH/bridge.

## Independently Re-Verified Evidence

1. **Tests re-run — matches exactly.** `pytest
   platform_tests/scripts/test_codex_dotdir_acl_repair.py
   platform_tests/scripts/test_repair_codex_dotdir_acl.py
   platform_tests/scripts/test_verify_codex_dispatch.py -q --tb=short` →
   31 passed, 0 skipped.

2. **Both ruff gates re-run separately — both pass.**

3. **Live ACL state reproduced three independent ways** —
   `verify_codex_dispatch.py --json`, direct `powershell.exe` (5.1), and
   direct `pwsh` (7) all returned identical `checked_count=218,
   risky_deny_count=2, errors=[]`, `sandbox_group.present=true`,
   `current_identity.allow_present=true`. The two remaining risky Deny
   ACEs are real, structurally valid ACEs against the same foreign SID
   documented in the WI-5065 fixture — not fabricated.

4. **Hash proof.** SHA-256 of all three changed files matched the
   SHA-256 values independently recorded in WI-5418's MemBase status
   detail exactly.

5. **Isolation confirmed.** `git status --porcelain` on all 5 target
   paths shows only the 3 claimed files modified. Full `git diff` read
   of all 3 changed files shows every hunk is on-topic ACL/detection
   logic — no commingled unrelated changes despite the heavily dirty
   working tree.

6. **No deleted predecessor files.** All three thread versions show
   untracked/new (`??`), no `D` markers.

7. **Governance chain verified live.** PAUTH
   `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE`
   active, correctly scoped, citing owner decision `DELIB-202666274`.

8. **Cross-reference to upstream WI-5310 v008 NO-GO confirms honest
   framing.** WI-5418 fixes the detection/attestation mechanism only
   (Check mode never mutated live `.codex`); it correctly does not claim
   to have removed the 2 real risky Deny ACEs, which requires a separate
   exact-path PAUTH/bridge per WI-5310's own D1 finding.

9. **Both mandatory preflights pass clean.**

10. **Review independence confirmed.** Report author session
    `A-2026-07-17T10-20-39Z` (Codex/A) differs from this reviewer's
    session context.

## Non-Blocking Finding — Diff-stat table in report is inaccurate

The report's "Diff stat" table claims `3 files changed, 99
insertions(+), 30 deletions(-)`; independent `git diff --numstat` shows
`155 insertions(+), 62 deletions(-)`. Root cause: a ~60-line descendant-
scan block was wrapped in a new `if` guard, re-indenting every contained
line, which git's line-based diff counts as both a deletion and
insertion. Full line-by-line diff read confirms no unrelated or
undisclosed content — every hunk is on-topic. SHA-256 hash of the live
file matches the audit-trail record exactly, so this is a supplementary-
evidence computation error, not evidence of incomplete reporting. No
linked specification depends on diff-stat accuracy. No action required;
noted for future report-generation methodology.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `GOV-HARNESS-ISOLATION-001`

## Spec-to-Test Mapping

| Specification | Test | Executed | Result |
| --- | --- | --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Focused ACL/verifier pytest suite (31 tests) | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Full independent re-execution of this mapping | yes | PASS |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | 3 independent live invocations (Python wrapper, WinPS 5.1, pwsh 7) | yes | PASS — all agree exactly |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `test_acl_check_preserves_no_window_launcher` + re-run of verify_codex_dispatch.py | yes | PASS — no-window disposition preserved |
| Code quality gates | ruff check + ruff format --check on 4 files | yes | PASS |

## Commands Executed

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_codex_dotdir_acl_repair.py platform_tests/scripts/test_repair_codex_dotdir_acl.py platform_tests/scripts/test_verify_codex_dispatch.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/repair_codex_dotdir_acl.ps1 scripts/verify_codex_dispatch.py platform_tests/scripts/test_codex_dotdir_acl_repair.py platform_tests/scripts/test_repair_codex_dotdir_acl.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/repair_codex_dotdir_acl.ps1 scripts/verify_codex_dispatch.py platform_tests/scripts/test_codex_dotdir_acl_repair.py platform_tests/scripts/test_repair_codex_dotdir_acl.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\verify_codex_dispatch.py --json`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\repair_codex_dotdir_acl.ps1 -ProjectRoot E:\GT-KB -Mode Check -Json`
- `pwsh -NoProfile -File scripts\repair_codex_dotdir_acl.ps1 -ProjectRoot E:\GT-KB -Mode Check -Json`
- `Get-FileHash -Algorithm SHA256` on all 3 changed files
- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5418-codex-acl-headless-attestation`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5418-codex-acl-headless-attestation`
- `gt bridge show gtkb-wi5418-codex-acl-headless-attestation --json --compact`

## Prior Deliberations

- `bridge/gtkb-wi5418-codex-acl-headless-attestation-001.md` / `-002.md` —
  approved proposal and GO.
- `bridge/gtkb-wi5310-codex-effective-workspace-profile-008.md` —
  upstream NO-GO naming this repair as dependency D1; confirmed this
  thread does not overclaim D1 closure.
- `DELIB-202666274` — owner authorization underlying the active PAUTH.

## Applicability Preflight

- packet_hash: `sha256:c0a7d27cc5cad69363848aebc1093a264a9b9f810b52c51136869aba927075a6`
- operative_file: `bridge/gtkb-wi5418-codex-acl-headless-attestation-003.md`
- preflight_passed: `true`
- missing_required_specs: `[]`

## Clause Applicability

- Clauses evaluated: 5; must_apply: 4, may_apply: 1
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit code: `0` (pass)

## Methodology Trail

Read all 3 bridge version files. Ran full test suite and both ruff gates
independently. Re-ran the ACL checker three separate ways (Python
wrapper, WinPS 5.1, pwsh 7) confirming byte-for-byte agreement. Verified
SHA-256 hashes against MemBase-recorded values. Full line-by-line diff
read of all 3 changed files confirming no commingled content. Confirmed
no deleted predecessor files. Cross-referenced upstream WI-5310 NO-GO to
confirm honest scope framing. Ran both mandatory preflights. Re-ran `gt
bridge show --json --compact` immediately before filing to confirm
thread currency (unchanged: NEW, version 3).

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Intended commit subject: `fix(bridge): WI-5418 codex ACL headless attestation VERIFIED`
- Same-transaction path set:
- `bridge/gtkb-wi5418-codex-acl-headless-attestation-001.md`
- `bridge/gtkb-wi5418-codex-acl-headless-attestation-002.md`
- `bridge/gtkb-wi5418-codex-acl-headless-attestation-003.md`
- `scripts/repair_codex_dotdir_acl.ps1`
- `platform_tests/scripts/test_codex_dotdir_acl_repair.py`
- `platform_tests/scripts/test_repair_codex_dotdir_acl.py`
- `scripts/verify_codex_dispatch.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`
- `bridge/gtkb-wi5418-codex-acl-headless-attestation-004.md`
- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.
