GO

bridge_kind: loyal_opposition_advisory
Document: gtkb-startup-refractor-slice-d-sessionstart-hook-dedup
Version: 002
Responds to: bridge/gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-001.md
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-03 UTC
Reviewer: Loyal Opposition
Recommended commit type: docs

# Startup Slice D SessionStart Hook De-Duplication - GO Verdict

## Verdict

GO, with implementation-start conditions.

The proposal is sufficiently scoped for a behavior-preserving extraction of the duplicated Claude/Codex SessionStart dispatch logic into `scripts/session_start_dispatch_core.py`. It cites the controlling SessionStart, role-resolution, init-keyword, parity, bridge, backlog, and root-boundary specifications; the target path glob is permitted by the file-bridge protocol; and the verification plan maps the high-risk invariants to focused dispatcher tests, stdlib import checks, and Ruff checks.

This GO does not waive the proposal's own sequencing guard. Prime Builder must not start implementation until the surrounding startup-refactor workstream is quiet enough to make this the last hook-area slice in practice.

## Implementation-Start Conditions

Before running `python scripts/implementation_authorization.py begin --bridge-id gtkb-startup-refractor-slice-d-sessionstart-hook-dedup`, Prime Builder must confirm and record in the implementation report:

1. Startup-refactor Slices B, C, and E are no longer actively editing overlapping startup/session surfaces, or the implementation report explains why their current latest bridge states cannot conflict with the SessionStart hook extraction.
2. `git status --short -- .claude/hooks/session_start_dispatch.py .codex/gtkb-hooks/session_start_dispatch.py scripts/session_start_dispatch_core.py platform_tests/scripts/test_*session_start*.py` is reviewed before implementation begins, so unrelated in-flight hook/test edits are not bundled or overwritten.
3. The implementation remains behavior-preserving: no change to role resolution, init-keyword parsing/assertion, bridge dispatch strict-drop behavior, startup disclosure relay semantics, or ephemeral session-role marker invalidation.
4. The shared module remains stdlib-light. The implementation report must include test evidence proving the module does not import `groundtruth_kb`, database APIs, third-party packages, or other slow startup dependencies.
5. Parity tests are rewritten, not removed: the verification evidence must show both wrappers delegate to the shared module and continue to produce equivalent decisions for equivalent inputs.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-startup-refractor-slice-d-sessionstart-hook-dedup
```

Observed result:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
packet_hash: sha256:368363d3f55ce89c5e41f57118f7aa796aa566db18f2a20bf30b9ab3ea79aa9e
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-startup-refractor-slice-d-sessionstart-hook-dedup
```

Observed result:

```text
Clauses evaluated: 5
must_apply: 3
may_apply: 2
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
```

## Project / PAUTH Check

Live MemBase state confirms:

- `PROJECT-GTKB-STARTUP-REFRACTOR-001` exists and is active.
- `PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-GTKB-STARTUP-REFRACTOR-001-SLICES-A-E-IMPLEMENTATION-AUTHORIZATION` is active.
- The PAUTH includes `WI-4272` and permits `source`, `test`, and `hook` mutation classes.
- The PAUTH owner-decision record is `DELIB-20260622`.

The implementation authorization dry-run correctly refused before this verdict because the live latest status was still `NEW`, not `GO`.

## Target Path Check

The proposal target paths are:

- `.claude/hooks/session_start_dispatch.py`
- `.codex/gtkb-hooks/session_start_dispatch.py`
- `scripts/session_start_dispatch_core.py`
- `platform_tests/scripts/test_*session_start*.py`

`.claude/rules/file-bridge-protocol.md` allows concrete files or globs in `target_paths`. The test glob currently matches five in-root session-start test files and is appropriate for preserving the full SessionStart regression floor.

## Prior Deliberations

- `DELIB-20260622` - owner PAUTH decision covering WI-4272.
- `DELIB-2078` - owner approval for the init-keyword startup-disclosure relay contract.
- `bridge/gtkb-startup-refractor-scoping-002.md` - GO for the umbrella scoping plan that sequenced Slice D last.
- `bridge/gtkb-startup-refractor-slice-a-startup-control-inventory-004.md` - VERIFIED inventory confirming the two SessionStart dispatch hooks as active de-duplication targets.

## Specifications Carried Forward

- `GOV-SESSION-SELF-INITIALIZATION-001`
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Residual Risk

This is the highest-blast-radius startup-refactor slice because it touches SessionStart hook code. The residual risk is acceptable only if the implementation report proves the conditions above with focused dispatcher tests and current dirty-state evidence.

## Owner Action Required

None.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
