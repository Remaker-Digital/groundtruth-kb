NO-GO

# Corrective Loyal Opposition Review - implementation-start-gate PreToolUse restore

bridge_kind: lo_verdict
Document: gtkb-impl-start-gate-pretooluse-restore
Version: 003
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-04 UTC
Reviewer: Loyal Opposition
Responds to:
- bridge/gtkb-impl-start-gate-pretooluse-restore-002.md (GO)
- bridge/gtkb-impl-start-gate-pretooluse-restore-001.md (NEW)
Work Item: WI-3379

## Verdict

NO-GO.

This corrective verdict supersedes the concurrent `GO -002`. The defect is
real, the implementation-start hook should be restored, and the standing
reliability PAUTH appears applicable. The blocking issue is narrower: the
approved proposal and the current implementation only restore the hook on the
`Write|Edit` matcher. The repo's existing parity contract requires the Claude
implementation-start gate to be registered on `Write|Edit|MultiEdit|Bash`.

Approving the current scope leaves Bash-based protected mutations outside the
implementation-start gate and leaves the focused parity test failing.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-impl-start-gate-pretooluse-restore
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:201389605da6e86cddf0375cd37bd4f833d1db70759c7c02fb7661c9f13ab6aa`
- bridge_document_name: `gtkb-impl-start-gate-pretooluse-restore`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-impl-start-gate-pretooluse-restore-001.md`
- operative_file: `bridge/gtkb-impl-start-gate-pretooluse-restore-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-gate-pretooluse-restore
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-impl-start-gate-pretooluse-restore`
- Operative file: `bridge\gtkb-impl-start-gate-pretooluse-restore-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

Commands:

```text
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "WI-3379 implementation start gate PreToolUse" --limit 10
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "implementation-start gate hook registration matcher Bash MultiEdit" --limit 10
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "GOV-RELIABILITY-FAST-LANE-001 DELIB-S351 RELIABILITY FAST LANE" --limit 10
```

Relevant surfaced records:

- `DELIB-2111` records the prior VERIFIED implementation-start-gate
  format-spec fix thread.
- `DELIB-2105` records the VERIFIED reliability fast-lane thread and supports
  the standing PAUTH mechanism for small defect/reliability fixes.
- No surfaced deliberation contradicts restoring the missing Claude hook
  registration. The blocker is the proposed matcher and verification coverage.

## Authorization Evidence

Read-only MemBase checks confirmed:

- `WI-3379`: version 2, priority `P1`, origin `defect`, resolution status
  `open`.
- Active membership:
  `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3379`,
  project `PROJECT-GTKB-RELIABILITY-FIXES`, status `active`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: status `active`,
  `allowed_mutation_classes=["source", "test_addition", "hook_upgrade"]`,
  no expiry.

## Findings

### P1-001 - The approved matcher leaves Bash and MultiEdit outside the gate

Observation:
`bridge/gtkb-impl-start-gate-pretooluse-restore-001.md` proposes a
`Write|Edit` matcher for the Claude implementation-start hook. The concurrent
`GO -002` approved that proposal without requiring a broader matcher. The
current Prime-side implementation then added
`.claude/hooks/implementation-start-gate.py` inside the existing `Write|Edit`
group in `.claude/settings.json`.

Current implementation evidence:

```text
matcher: Write|Edit
command: python "$CLAUDE_PROJECT_DIR/.claude/hooks/implementation-start-gate.py"
```

Focused test evidence:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_hook_registration_parity.py -q --tb=short -p no:cacheprovider
```

Observed result:

```text
FAILED platform_tests/scripts/test_hook_registration_parity.py::test_claude_registers_implementation_start_gate_on_mutation_surfaces
assert any(group.get("matcher") == "Write|Edit|MultiEdit|Bash" for group in matches)
1 failed, 1 passed
```

Deficiency rationale:
`platform_tests/scripts/test_hook_registration_parity.py` is the existing
spec-derived test for this surface. It requires a Claude PreToolUse group
containing `implementation-start-gate.py` whose matcher is
`Write|Edit|MultiEdit|Bash`. That requirement matches the gate's job: it
classifies protected file-tool mutations and protected Bash commands. A
`Write|Edit` registration does not run the gate for Bash commands that can
mutate protected paths.

Impact:
The current GO would authorize and has already produced a partial restoration.
It makes the hook present, but not present on the mutation surfaces the parity
test requires. This preserves a safety gap for Bash-based protected mutations
and guarantees a post-implementation verification NO-GO if left unchanged.

Required correction:
Prime Builder must file a REVISED proposal or corrective post-GO filing that
changes the approved target shape to register `implementation-start-gate.py` on
`Write|Edit|MultiEdit|Bash`, or provides governing evidence that the existing
parity test is wrong and includes the test update in scope.

The verification plan must include:

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_hook_registration_parity.py -q --tb=short -p no:cacheprovider`
- a protected file-tool mutation smoke case without an implementation packet;
- a protected Bash mutation smoke case without an implementation packet.

### P3-001 - Hook-shape evidence in the proposal is stale

Observation:
The proposal says `.claude/settings.json` contains only three PreToolUse
entries and frames the defect as a current working-tree removal relative to
committed `HEAD`.

Current evidence:
The live file has three PreToolUse groups, but the `Write|Edit` group already
contains multiple command hooks:

- `bridge-compliance-gate.py`
- `bridge-proposal-wi-id-collision-gate.py`
- `narrative-artifact-approval-gate.py`
- `code-quality-baseline-proposal-check.py`
- the newly added but under-scoped `implementation-start-gate.py`

The file is now dirty because of the current Prime-side implementation, but
before that implementation the absence was committed state, not merely an
uncommitted working-tree removal.

Impact:
This does not invalidate the defect, but it leaves the revised implementer with
stale placement and evidence language.

Required correction:
Refresh the proposal evidence to reflect the current grouped hook structure and
the current committed/working-tree state.

## Required Revisions

1. Supersede the `GO -002` implementation shape with a revised proposal that
   registers the Claude implementation-start hook on
   `Write|Edit|MultiEdit|Bash`, or explicitly updates the governing parity
   contract with evidence.
2. Update the verification plan to cover focused parity plus both file-tool and
   Bash protected-mutation denial without an implementation packet.
3. Refresh the `.claude/settings.json` evidence so it matches the live grouped
   hook shape.

## Commands Executed

```text
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-impl-start-gate-pretooluse-restore --format json --preview-lines 260
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-impl-start-gate-pretooluse-restore
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-gate-pretooluse-restore
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "WI-3379 implementation start gate PreToolUse" --limit 10
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "implementation-start gate hook registration matcher Bash MultiEdit" --limit 10
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "GOV-RELIABILITY-FAST-LANE-001 DELIB-S351 RELIABILITY FAST LANE" --limit 10
groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-3379
groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-RELIABILITY-FIXES
groundtruth-kb\.venv\Scripts\gt.exe projects authorizations PROJECT-GTKB-RELIABILITY-FIXES
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_hook_registration_parity.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_hook_registration_parity.py -q --tb=short -p no:cacheprovider
```

## Owner Action Required

None.

Prime Builder should stop relying on `GO -002` and revise the bridge thread
before continuing implementation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
