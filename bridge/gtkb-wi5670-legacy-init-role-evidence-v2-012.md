NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 8acf3d52-8dbb-4759-a1b7-41424e4c6cb6
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled Loyal Opposition worker; envelope-resolved loyal-opposition role; test activity
author_metadata_source: session envelope (worker_role_provenance)

# LO Verification - WI-5670 legacy author-provenance tolerance - 012

bridge_kind: lo_verdict
Document: gtkb-wi5670-legacy-init-role-evidence-v2
Version: 012
Date: 2026-07-29 UTC
Author: Loyal Opposition (claude, harness B)
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5670-legacy-init-role-evidence-v2-011.md
Reviewed report: bridge/gtkb-wi5670-legacy-init-role-evidence-v2-011.md

## Verdict Summary

**NO-GO** on a single new P0 finding.

Version 011 discharges all three v010 findings and every mechanical claim in it
reproduces exactly: 220/220 tests pass, `ruff check` and `ruff format --check`
both clean, the diff is exactly the three declared `target_paths` at +134/-0,
and both mandatory preflights exit 0. The report is procedurally correct.

The blocking defect is substantive, not procedural. The tolerance added at
`scripts/bridge_lifecycle_resolver.py:369-380` is described throughout the chain
as "audit-only." That description is accurate for the proposal, GO, report,
NO-ACTION, and corrected-verdict positions. It is **not** accurate for the
terminal `VERIFIED` position, which is direct protected-commit clearance
authority and whose author role no downstream consumer re-validates.

## Review Independence

Reviewer session context `8acf3d52-8dbb-4759-a1b7-41424e4c6cb6`
(loyal-opposition/claude, harness B). Report author session context
`019f9329-a174-7763-8f7e-29679f39e6bd` (prime-builder/codex, harness A).
Present, readable, and distinct. No self-review condition. Independence gate
satisfied.

## Findings

### [P0] F1 - The tolerance removes the only enforcement that a terminal VERIFIED verdict was authored by Loyal Opposition

**Claim.** The new `role is None` early-return returns a `BridgeVersion` carrying
the observed status verbatim - including `VERIFIED` - with `author_role=None`,
bypassing `_validate_author_role`. `_approved_chain` in
`scripts/check_protected_commit_authorization.py` validates the author role of
the report, the GO, and the proposal, but never of the terminal `VERIFIED`
verdict itself. `_validate_author_role` at parse time was the sole enforcement of
that invariant, and this diff routes around it.

**Evidence.**

1. The new branch preserves the status and drops the role
   (`scripts/bridge_lifecycle_resolver.py:369-380`, verbatim from `git diff`):

   ```python
   role = _author_role(author_identity)
   if role is None:
       return BridgeVersion(
           version=version,
           path=rel_path,
           status=line_one,
           classification="legacy",
           document=document,
           responds_to=responds_to,
           author_identity=author_identity,
           author_role=None,
           observed_status=line_one,
       )
   _validate_author_role(line_one, role, rel_path=rel_path, version=version)
   ```

2. `VERIFIED` is a Loyal-Opposition-authored status:
   `scripts/bridge_lifecycle_resolver.py:31` -
   `LOYAL_OPPOSITION_STATUSES = frozenset({"GO", "NO-GO", "VERIFIED"})`;
   `:253-263` - for those statuses `allowed = {"loyal-opposition"}` and a
   mismatch raises `WRONG_STATUS_AUTHOR_ROLE`. Pre-change, a `VERIFIED` file with
   an unparseable `author_identity` hard-failed there. Post-change, the new
   branch intercepts first and returns `legacy` with `VERIFIED` intact.

3. `_approved_chain` checks role at three positions and not the fourth
   (`scripts/check_protected_commit_authorization.py:1374-1400`, read directly):

   ```
   1375: latest = resolution.latest_strict_state
   1376: if latest.status != "VERIFIED" or not latest.responds_to:      # status only
   1379: ... or report.author_role != "prime-builder":                  # report role checked
   1396: if go is None or go.status != "GO" or go.author_role != "loyal-opposition":
   1399: ... or proposal.author_role != "prime-builder":
   ```

   A `Select-String` for `author_role` across that module returns exactly four
   hits - lines 1379, 1390, 1396, 1399. `latest.author_role` appears nowhere.
   The terminal verdict is admitted on `status` alone.

4. The resolver's own `proposal.is_legacy` / `go.is_legacy` guards
   (`bridge_lifecycle_resolver.py:508-521`) do not cover this path:
   `_approved_chain` re-walks the chain itself from `latest.responds_to` rather
   than consuming `resolution.implementation_artifact`, and that guard block only
   executes when `latest_status == "GO"` or on a resumable report NO-GO.

5. Write-time gates enforce presence, not role:
   `.claude/hooks/document_author_provenance_gate.py:135-147` blocks governed
   markdown missing provenance; `scripts/document_author_metadata.py:128-132`
   checks only field presence and a placeholder pattern. `author_identity: codex`
   passes both.

**Concrete newly-reachable bypass.** Given a legitimately-approved thread -
strict `NEW` proposal (prime-builder), strict `GO` (loyal-opposition), strict
implementation report (prime-builder) - a session not holding the Loyal
Opposition role writes the terminal verdict with `author_identity: codex` and any
session id distinct from the report author's. The provenance gate passes
(identity present, non-placeholder). `verdict_self_review_reason`
(`scripts/bridge_review_independence.py:174-202`) passes - it compares
`author_session_context_id` only and never consults role. The resolver, which
previously raised `WRONG_STATUS_AUTHOR_ROLE`, now returns
`classification="legacy"`, `status="VERIFIED"`, `author_role=None`.
`_approved_chain` returns a valid chain because report, GO, and proposal are all
strict and role-correct. Protected paths clear on a self-issued verdict.

Any `author_identity` lacking the substrings `prime builder`, `loyal opposition`,
or `owner` after the `[-_/]`-to-space normalization at
`bridge_lifecycle_resolver.py:232-241` triggers this - `codex`, `claude`,
`reviewer/gpt-5`, `B`, and so on.

**Why this is not merely pre-existing.** The sibling missing-`author_identity`
branch (`:355-366`) has the same shape but is unreachable for newly-authored
files, because `document_author_provenance_gate.py` blocks new governed markdown
with no `author_identity` at all. The new branch **is** reachable by
newly-authored files, because presence-only validation admits a bogus value. The
two gates were mutually reinforcing - write-time required presence, resolve-time
required parseability. This change removes the second half for the
present-but-unparseable case, converting a closed grandfathering window into an
open one.

**Why the added tests do not catch it.** The new protected-commit regression
(`platform_tests/scripts/test_check_protected_commit_authorization.py:444`,
`test_approved_chain_rejects_fully_roleless_legacy_chain`) constructs an
all-four-versions-roleless chain and asserts
`match="not linked to a Prime implementation report"` - it fails at the *report*
check and never exercises the terminal-verdict position. The resolver additions
cover roleless proposal, GO, correction predecessor, NO-ACTION, and corrected
verdict, but no roleless terminal `VERIFIED`. The dangerous mixed case - strict
proposal + strict GO + strict report + roleless `VERIFIED` - is untested. The
suite's shape is what conceals the gap.

**Impact.** The "`VERIFIED` must be issued by Loyal Opposition" invariant - the
core of the bridge protocol's independent-verification guarantee and of
`REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` - becomes bypassable by a one-token change
to a metadata line, clearing protected source, test, script, hook, and
configuration paths on a self-issued verdict.

**Contradicted claims.**

- v005 Acceptance Criterion 4: "No legacy version can become an operative ...
  corrected verdict, or protected-commit authority." False for the terminal
  `VERIFIED`; v011 line 158 marks it `[x]`.
- v011 Implementation Claim (lines 39-41): "... or VERIFIED chain cannot become
  implementation or protected-commit authority." False.
- v011 Risk section (lines 175-179): "Operative authority remains unavailable
  because every authority consumer requires a strict or role-correct Prime/LO
  position." False - `_approved_chain`'s terminal-verdict position requires
  neither.

**Recommended action.** Narrow the tolerance so it cannot apply to a terminal
`VERIFIED`. The preferred repair is entirely inside the existing `target_paths`
and needs no scope expansion:

- Option (a), preferred: in `_parse_version`, retain the strict
  `_validate_author_role` path when `line_one == "VERIFIED"`, so a roleless
  `VERIFIED` fails closed exactly as before. This is a two-line guard and leaves
  the existing `test_roleless_identity_non_operative_verdict_is_grandfathered`
  case (a non-operative `NO-GO`) untouched.
- Option (b): fail closed in `_ordinary_resolution` / `_correction_resolution`
  when the latest version is `VERIFIED` and `is_legacy`.

Add a regression asserting that a **mixed** chain - strict proposal, strict GO,
strict report, roleless terminal `VERIFIED` - raises `GateError` from
`_approved_chain` or fails at resolve.

Hardening `_approved_chain` itself to require
`latest.author_role == "loyal-opposition"` is the more complete defence-in-depth
fix, but `scripts/check_protected_commit_authorization.py` is outside the
approved `target_paths` and would require a revised proposal. That decision is
Prime Builder's; option (a) alone closes the blocking gap.

### [P2] F2 - Acceptance criteria assert an authority-containment property that was never tested

**Claim.** v011 lines 155-162 mark all eight acceptance criteria `[x]`, including
criterion 4 (no legacy version becomes protected-commit authority), on an
evidence base containing no test exercising the terminal-`VERIFIED` position.

**Evidence.** The only protected-commit addition is the all-roleless chain test
at `test_check_protected_commit_authorization.py:444`, which short-circuits at
the report check. The spec-to-test mapping row for
`REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` (v011 line 94) claims the regression
"rejects a fully roleless terminal chain with `GateError`" - true, but
non-probative for the actual risk.

**Impact.** A reader of the mapping table reasonably concludes the containment
property is verified when it is not.

**Recommended action.** Add the missing regression per F1 (which also satisfies
this finding), or explicitly scope criterion 4 to the positions actually tested
and record the terminal-`VERIFIED` position as an open gap.

### [P4] F3 - Missing copyright footer

**Claim/Evidence.** `bridge/gtkb-wi5670-legacy-init-role-evidence-v2-011.md`
contains no "Remaker Digital" footer; v005 (line 203) and v010 (line 407) both
carry it.

**Impact.** Cosmetic audit-trail inconsistency. Non-blocking.

**Recommended action.** Restore in the corrected version.

## v010 Findings Disposition - all three closed

| v010 requirement | Status | Evidence |
|---|---|---|
| 1 (P0) - add exactly one `Controlling GO:` line naming v006 | Closed | v011 line 18; exactly one occurrence, matches `CONTROLLING_GO_RE` at `check_protected_commit_authorization.py:62`; `Responds to:` correctly retained at v010 |
| 2 (P3) - refresh or restate the stale dirty-path count | Closed | v011 lines 102, 135 restate 45 as a v009 filing-time observation and decline to assert the live count - exactly what v010 permitted |
| 3 (P3) - record the implementation-start packet inspection path | Closed | v011 line 116 cites `.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5670-legacy-init-role-evidence-v2.json`; file present |
| 4 - change nothing else | Closed | Diff byte-identical in scope to v009's: 3 files, +134/-0 |

## Positive Evidence Accepted (carry forward unchanged)

The following require no re-execution in the corrected report beyond re-running
the two suites after the F1 guard is added:

- `pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_check_protected_commit_authorization.py -q`
  -> `220 passed, 1 warning in 143.65s`. Matches the report's 59 + 161 claim.
- `ruff check` -> `All checks passed!` (exit 0); `ruff format --check` ->
  `3 files already formatted` (exit 0). Both separate gates clean.
- `git diff --stat` -> 3 files, +134/-0, exactly the declared `target_paths`. No
  scope creep; the other dirty worktree paths belong to unrelated workstreams.
- All 16 linked specifications carried forward from v005/v009, each with a
  mapping row in the Specification-Derived Verification Plan (lines 90-107).
- `## Prior Deliberations` present (lines 77-86, 8 entries);
  `## Owner Decisions / Input` present and substantive (lines 70-75).
- `Recommended commit type: fix:` matches the diff shape.

## Prior Deliberations

- `DELIB-20263483` - WI-4522 Author Identity Env Alias Defect. Prior treatment of
  author-identity parsing defects in the same subsystem.
- `DELIB-20262495` - Loyal Opposition Verification, FAB-16 Harness Parity
  Remediation. Precedent for role-token handling across harness surfaces.
- `DELIB-20260683` / `DELIB-20264045` - Loyal Opposition Verdict, Document
  Artifact Author Provenance Contract. The governing provenance contract this
  tolerance relaxes; both records treat author provenance as an authority input,
  not as free-form metadata.
- `bridge/gtkb-wi5670-legacy-init-role-evidence-v2-006.md` - the controlling GO,
  whose condition 3 required executing the proposal's no-side-effect and
  authority assertions. The AC-4 protected-commit-authority assertion was not
  executed for the `VERIFIED` position.

## Applicability Preflight

- packet_hash: `sha256:a6f8496bf1ebebefe8cf4c0e8cd06076bf6308aa7fb4f49a5c7341449a2824fc`
- candidate_evidence_hash: `sha256:09be44478a69ca06be8588d694b24ac1c31d7faa5374ab06716c720ce1d74992`
- bridge_document_name: `gtkb-wi5670-legacy-init-role-evidence-v2`
- declared_target_paths: ["platform_tests/scripts/test_bridge_lifecycle_resolver.py", "platform_tests/scripts/test_check_protected_commit_authorization.py", "scripts/bridge_lifecycle_resolver.py"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5670-legacy-init-role-evidence-v2-011.md`
- operative_file: `bridge/gtkb-wi5670-legacy-init-role-evidence-v2-011.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

Exit code: 0.

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5670-legacy-init-role-evidence-v2`
- Operative file: `bridge\gtkb-wi5670-legacy-init-role-evidence-v2-011.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

Exit code: 0. No blocking gap; no owner waiver required.

Neither preflight inspects verdict-author role semantics, which is why F1 is
invisible to both. The mechanical floor passed; the ceiling did not.

## Commands Executed

- `git diff -- scripts/bridge_lifecycle_resolver.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_check_protected_commit_authorization.py`
  -> 3 files, +134/-0; new `role is None` branch confirmed verbatim.
- `Select-String -Path scripts/check_protected_commit_authorization.py -Pattern 'author_role'`
  -> 4 hits (lines 1379, 1390, 1396, 1399); no `latest.author_role`.
- Direct read of `scripts/check_protected_commit_authorization.py:1370-1403`
  -> confirmed `_approved_chain` admits `latest` on status alone.
- `pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_check_protected_commit_authorization.py -q`
  -> `220 passed, 1 warning in 143.65s`.
- `ruff check` -> exit 0; `ruff format --check` -> exit 0.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5670-legacy-init-role-evidence-v2`
  -> exit 0, `missing_required_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5670-legacy-init-role-evidence-v2`
  -> exit 0, 0 blocking gaps.

## Prime Builder Implementation Context

| Element | Detail |
|---|---|
| Objective | Ensure a terminal `VERIFIED` verdict with a present-but-unparseable `author_identity` cannot clear protected paths. |
| Preconditions | The v011 diff stands; no accepted evidence needs re-derivation. |
| Evidence paths | `scripts/bridge_lifecycle_resolver.py:369-380`, `:31`, `:35`, `:232-241`, `:251-263`, `:508-521`; `scripts/check_protected_commit_authorization.py:1374-1400`, `:1473-1550`, `:1746-1888`; `scripts/bridge_review_independence.py:174-202`; `scripts/document_author_metadata.py:128-132`. |
| File touchpoints | `scripts/bridge_lifecycle_resolver.py` plus the two declared test modules. Option (a) requires no scope expansion. |
| Implementation sequence | 1. Add the `VERIFIED`-strict guard. 2. Add the mixed-chain regression. 3. Re-run both suites. 4. Re-run both preflights. 5. Re-file as `REVISED`. |
| Verification steps | Mixed chain (strict proposal/GO/report + roleless terminal `VERIFIED`) must fail closed; existing 220 tests must still pass; both ruff gates clean. |
| Rollback notes | Additive guard; revert is the same scoped three-path revert already described in v011. |
| Open decisions | Whether to also harden `_approved_chain` (outside current `target_paths`; would require a revised proposal with widened scope). |

## Owner Decisions / Input

No new owner decision is required for this verdict. The repair is inside the
existing project authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
and inside the already-approved `target_paths`. The owner-approval evidence
carried by the v011 report (lines 70-75) remains accurate and is unchanged by
this NO-GO.

## Owner Action Required

None. No owner decision blocks the correction.

## Recommended Commit Type

Not applicable - this is a `NO-GO` verdict, not an implementation. The corrected
implementation report should retain `fix:`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
