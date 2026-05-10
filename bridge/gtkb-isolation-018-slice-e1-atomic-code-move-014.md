NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-018 18.E.1 Atomic Code Cluster Move REVISED-6

Reviewed: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-013.md`
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-10
Verdict: NO-GO

## Claim

REVISED-6 fixes the immediate branch-ordering defect from `-012`: the proposed
Phase 3 cleanup now performs a containment check before both `unlink()` and
`rmtree()`. The live mechanical bridge preflights pass.

It is still not ready for GO because the proposed containment check is not
portable on the Windows host that runs this project. The algorithm converts the
write-set string through `Path(p)` and then checks
`str(path).startswith('applications/Agent_Red/')`. On Windows, valid in-scope
paths stringify with backslashes, so the helper rejects legitimate
`applications/Agent_Red/...` destination cleanup paths before it can complete
rollback.

## Prior Deliberations

Deliberation Archive checks were run before review using semantic search and
exact `get` lookups.

Search query:

- `GTKB-ISOLATION-018 E.1 atomic code cluster move Agent Red applications Agent_Red rollback containment parent traversal write-set`

Relevant results and exact checks:

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` remains the owner-decision
  authority for nesting Agent Red under `applications/Agent_Red/`.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` remains the active
  migration-window waiver and requires sub-slices to constrain commits to their
  scope.
- `DELIB-S334-OQ-E3-OPTION-A` remains relevant for file-level platform-test
  disposition and dual pytest discovery.
- Semantic search also surfaced older isolation-contract/rehearsal records
  (`DELIB-0878`, `DELIB-1119`, `DELIB-1327`, `DELIB-1328`, `DELIB-1329`,
  `DELIB-1330`, `DELIB-1337`), but no prior deliberation found in this review
  rejects the approved 18.E.1 direction.

The blocker below is a remaining rollback-helper containment defect, not an
objection to the atomic code-cluster move itself.

## Findings

### FINDING-P1-001 - Windows path normalization makes the rollback containment check reject valid destinations

Observation:
REVISED-6 proposes this containment check:

```python
for p in destinations_to_clean:
    path = Path(p)
    if not str(path).startswith('applications/Agent_Red/'):
        raise AssertionError(f'Refusing to remove out-of-scope destination path: {path}')
```

The write-set stores repository-relative destination paths with forward slashes,
but the proposal immediately wraps each string in `Path(p)`. On Windows,
`str(Path(...))` normalizes separators to backslashes. A valid destination such
as `applications/Agent_Red/tests/a.txt` therefore becomes
`applications\Agent_Red\tests\a.txt` and fails the forward-slash prefix check.

Evidence:

- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-013.md:116-121` shows
  the proposed `Path(p)` plus forward-slash `startswith(...)` check.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-013.md:122-125` performs
  the destructive cleanup only after that check, so a false negative aborts all
  valid cleanup.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-013.md:138-141` expands
  tests only for outside file/directory destinations; it does not include an
  in-scope Windows-path regression test.
- Review-time probe from `E:\GT-KB`:

```text
input=applications/Agent_Red/src
str=applications\Agent_Red\src
startswith_forward=False
input=applications/Agent_Red/tests/a.txt
str=applications\Agent_Red\tests\a.txt
startswith_forward=False
input=applications/Agent_Red/config/stripe_product_ids.json
str=applications\Agent_Red\config\stripe_product_ids.json
startswith_forward=False
```

Impact:
The rollback helper is the safety mechanism for a 1,400+ file move. As written,
it would hard-fail on normal in-scope destination cleanup paths on this
Windows/PowerShell environment. That means a partial `git mv` failure can still
leave destination-side artifacts behind, because the safety helper cannot get
past its own containment check. It also means the proposed M5/M6 mutation tests
are incomplete: they prove outside paths fail, but not that legitimate in-scope
paths pass on the host platform.

Required revision:
Replace the lexical `str(Path(...)).startswith('applications/Agent_Red/')`
check with a cross-platform containment helper and test both pass and fail
cases. The helper should either:

1. Treat write-set paths as POSIX-style repository-relative strings, reject
   absolute paths and `..` path parts, then compare normalized parts against
   `('applications', 'Agent_Red')`; or
2. Resolve against the repository root and use a real relative-to check against
   the resolved `applications/Agent_Red` root.

The revised proposal should explicitly cover:

- valid in-scope file and directory destinations pass on Windows and POSIX;
- outside file and directory destinations fail before `unlink()` or `rmtree()`;
- parent traversal such as `applications/Agent_Red/../outside.txt` fails;
- absolute destinations fail unless they resolve under the repository's
  `applications/Agent_Red` root by an explicitly justified rule.

No owner decision is needed. This is a Prime Builder revision task.

## Applicability Preflight

- packet_hash: `sha256:43373cea11bdde60a1da7be02b0e315305b0e257d2f25b1ef823a4754d0e8adf`
- bridge_document_name: `gtkb-isolation-018-slice-e1-atomic-code-move`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-013.md`
- operative_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-013.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-isolation-018-slice-e1-atomic-code-move`
- Operative file: `bridge\gtkb-isolation-018-slice-e1-atomic-code-move-013.md`
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

## Prime Builder Implementation Context

The next revision should remain narrow. Keep the four-phase rollback design and
the pre-branch containment placement, but make the containment predicate
cross-platform and bidirectional: legitimate generated destinations must pass,
and malformed/generated-outside destinations must fail before deletion.

Expected proposal updates:

1. Define a small helper such as `validate_agent_red_destination(path_text,
   repo_root)` and use it before both `unlink()` and `rmtree()`.
2. State whether the helper validates lexical repository-relative strings or
   resolved filesystem paths.
3. Add positive tests for valid in-scope file and directory destinations on
   Windows-style paths, not only negative tests for outside paths.
4. Add negative tests for parent traversal and absolute paths.

No owner input is needed.

## Result

NO-GO. Revise and re-file as
`bridge/gtkb-isolation-018-slice-e1-atomic-code-move-015.md`.

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
