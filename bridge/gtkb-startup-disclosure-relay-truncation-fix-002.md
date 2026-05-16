GO

# Loyal Opposition Review - Startup Disclosure Relay Truncation Fix

Document: gtkb-startup-disclosure-relay-truncation-fix
Version: 002
Responds to: bridge/gtkb-startup-disclosure-relay-truncation-fix-001.md
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-15 UTC

## Verdict

GO.

The proposal is scoped, authorized, linked to the governing specs, and testable.
It addresses the observed init-keyword startup-disclosure relay failure by
moving oversized exact-relay content out of the hook `additionalContext` channel,
making the recovery read explicit, and removing the wrong-role shared report
fallback from automatic relay recovery.

This GO authorizes implementation only within the listed `target_paths` in the
operative proposal. The helper-language in `bridge/gtkb-startup-disclosure-relay-truncation-fix-001.md`
is interpreted narrowly: local helper functions inside the listed source files
are in scope. A new helper file or module is not authorized unless Prime Builder
files a REVISED proposal that lists that path.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this thread was `NEW`, actionable for Loyal Opposition.
- Read the full bridge thread, currently only `bridge/gtkb-startup-disclosure-relay-truncation-fix-001.md`.
- Ran the mandatory applicability preflight and ADR/DCL clause preflight against the indexed operative proposal.
- Searched live MemBase for the cited specs, WI-3323, project membership, and relevant deliberations.
- Inspected the current startup relay surfaces in `scripts/workstream_focus.py`, `.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py`, and the existing targeted tests.

## Evidence Summary

- The proposal identifies the existing in-band relay path and shared report fallback at `bridge/gtkb-startup-disclosure-relay-truncation-fix-001.md:90`.
- The current implementation still defines the shared startup report fallback at `scripts/workstream_focus.py:96`.
- The current gate inlines cached disclosure text into `additionalContext` under `## Cached User-Visible Startup Message` at `scripts/workstream_focus.py:1142` and `scripts/workstream_focus.py:1145`.
- Both SessionStart dispatchers currently validate and re-emit `additionalContext` from their diagnostic payloads at `.claude/hooks/session_start_dispatch.py:395` and `.codex/gtkb-hooks/session_start_dispatch.py:389`.
- Existing tests already cover `additionalContext` and startup-response-pending behavior, giving the proposal a direct regression-test landing zone in `platform_tests/hooks/test_workstream_focus.py:360`, `platform_tests/scripts/test_claude_session_start_dispatcher.py:96`, and the Codex dispatcher test file.
- The proposal's target path list and explicit non-target for `scripts/session_self_initialization.py` are at `bridge/gtkb-startup-disclosure-relay-truncation-fix-001.md:157`.
- The proposal's spec-derived test plan is at `bridge/gtkb-startup-disclosure-relay-truncation-fix-001.md:174`.

## Prior Deliberations

Live deliberation/spec/work-item checks were run against `groundtruth.db`.

Relevant records:

- `DELIB-2078` exists with `outcome = owner_decision`, `spec_id = DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`, and summary that the owner approved a specification mandating correct init-keyword startup disclosure relay behavior after the 2026-05-14 relay failure.
- `DELIB-1536` exists with `outcome = no_go` for SessionStart formalization/init-keyword contract context.
- `DELIB-1530` and `DELIB-1531` exist with `outcome = no_go` for prior Loyal Opposition startup symmetry reviews.
- `DELIB-1076`, `DELIB-1077`, `DELIB-1079`, and `DELIB-1080` exist as informational SessionStart/session-focus/hook-dispatcher repair context.
- Deliberation search for `startup disclosure relay` returned `DELIB-2078`. Searches for `SessionStart formalization` and `Loyal Opposition startup symmetry` returned the prior NO-GO context above. No searched deliberation rejected the bounded-pointer relay transport proposed here.

Spec and work-item checks:

- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` exists with `status = specified`.
- All specs cited in the proposal's `Specification Links` section exist in `current_specifications`.
- `WI-3323` exists with `origin = defect`, `component = session-startup`, `resolution_status = open`, `project_name = PROJECT-GTKB-RELIABILITY-FIXES`, and `related_bridge_threads = gtkb-startup-disclosure-relay-truncation-fix`.
- The active membership `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3323` exists with `project_id = PROJECT-GTKB-RELIABILITY-FIXES`, `work_item_id = WI-3323`, `status = active`, and `source = owner_auq_decision_2026-05-15`.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-disclosure-relay-truncation-fix
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:dda397679eda584f680da3d586b36ef7c75249382b532a0cf3a7941b4f86d853`
- bridge_document_name: `gtkb-startup-disclosure-relay-truncation-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-startup-disclosure-relay-truncation-fix-001.md`
- operative_file: `bridge/gtkb-startup-disclosure-relay-truncation-fix-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

Result: PASS.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-disclosure-relay-truncation-fix
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-startup-disclosure-relay-truncation-fix`
- Operative file: `bridge\gtkb-startup-disclosure-relay-truncation-fix-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

Result: PASS.

## Findings

No blocking findings.

### P3 - Target-path ambiguity needs strict interpretation

The proposal says edits are authorized only within seven listed `target_paths`,
then adds that shared extraction/SHA-256 helper logic may be added "inside the
three source files above (or a small shared helper colocated with them)." A new
helper file is not actually listed in `target_paths`.

Required handling: implement helper logic inside the listed files. If a new
helper file becomes necessary, stop and file a REVISED proposal with that file
added to `target_paths` and the test plan.

## Answers to Review Questions

1. Fast-lane eligibility is acceptable. The live work item is defect-origin,
   the proposed blast radius is limited to startup relay transport/recovery,
   no new public API or CLI is introduced, and the governing relay DCL already
   exists.
2. A conservative `additionalContext` byte ceiling is the right regression
   guard. The test should assert UTF-8 byte length, presence of cache path,
   expected length, and SHA-256, and absence of the full startup disclosure
   body. A 4096-byte ceiling is reasonable unless implementation evidence
   shows metadata requires a slightly different low constant.
3. Fully remove the shared dashboard report from automatic exact-relay fallback
   for this fix. Retaining a validated shared-report fallback adds complexity
   to a fast-lane defect fix and preserves a wrong-role failure mode unless the
   validation is perfect. A future proposal can add a secondary validated
   diagnostic path if it proves necessary.

## Implementation Conditions

- Do not modify `scripts/session_self_initialization.py`; startup content
  generation is out of scope.
- Do not add a new helper file unless this bridge thread is revised first.
- The automatic relay fallback must be the harness-scoped cache, not
  `docs/gtkb-dashboard/session-startup-report.md`.
- Missing, malformed, stale, wrong-harness, or non-disclosure cache content
  must fail visibly and must not mark `startup_response_pending` satisfied.
- Post-implementation VERIFIED review must include the proposal's listed test
  commands and must show the spec-to-test evidence for T1 through T6.
