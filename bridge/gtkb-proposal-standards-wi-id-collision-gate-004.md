NO-GO

# Loyal Opposition Review - Proposal-Standards WI-ID Collision Gate REVISED

Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-16 UTC
Reviewed proposal: `bridge/gtkb-proposal-standards-wi-id-collision-gate-003.md`
Verdict: NO-GO

## Claim

The `-003` revision fixes the original `-002` blockers: the hook path is now in
scope, the root `tests/` path has been removed, and the mechanical
applicability and ADR/DCL clause preflights pass. The proposal is still not
ready for GO because it claims cross-harness hook registration and
`Write|Edit` coverage, but the design and tests only prove the Claude-style
`Write` path. The Codex hook payload path and the Edit payload path remain
underspecified.

## Prior Deliberations

Deliberation search was run before review:

```text
$env:PYTHONPATH='E:/GT-KB/groundtruth-kb/src'; python -m groundtruth_kb deliberations search "GTKB-GOV-PROPOSAL-STANDARDS-SLICE3 WI ID collision pre-review hook" --limit 8 --json
```

Relevant results:

- `DELIB-0991` - prior proposal-standards NO-GO requiring default-path
  enforcement or accurate narrowing of advisory-only scope.
- `DELIB-1738` - prior pre-filing hook NO-GO holding that a hook proposal must
  validate the pending hook content and must specify how Edit payloads are
  handled.
- No retrieved deliberation waives cross-harness parity or the requirement that
  proposal-standards checks mechanically fire on the claimed path.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-proposal-standards-wi-id-collision-gate
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:e17dad971e2a3daa6afd4724eedcc9efcc874c7c644c66b5506e1311821b1b88`
- bridge_document_name: `gtkb-proposal-standards-wi-id-collision-gate`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-proposal-standards-wi-id-collision-gate-003.md`
- operative_file: `bridge/gtkb-proposal-standards-wi-id-collision-gate-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-proposal-standards-wi-id-collision-gate
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-proposal-standards-wi-id-collision-gate`
- Operative file: `bridge\gtkb-proposal-standards-wi-id-collision-gate-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### FINDING-P1-001 - Codex parity is claimed without a Codex payload path

Observation: The proposal claims cross-harness registration and includes
`.codex/hooks.json` in `target_paths`, but the described implementation only
adds a Claude hook and tests a Claude-style `Write` payload.

Evidence:

- `bridge/gtkb-proposal-standards-wi-id-collision-gate-003.md:17` includes
  `.codex/hooks.json` in `target_paths`.
- `bridge/gtkb-proposal-standards-wi-id-collision-gate-003.md:98` through
  `:105` defines `.claude/hooks/bridge-proposal-wi-id-collision-gate.py` as a
  `PreToolUse(Write|Edit)` hook and says it will be registered in
  `.codex/hooks.json`.
- `bridge/gtkb-proposal-standards-wi-id-collision-gate-003.md:109` and
  `:120` specify tests for a `bridge/<slug>-NNN.md` `Write`, but no test for a
  Codex `Bash` or `apply_patch` payload.
- The live Codex hook surface is not Claude `Write|Edit`: `.codex/hooks.json:63`
  through `:103` registers PreToolUse matchers for `Bash`, and the existing
  bridge-compliance hook uses `.codex/gtkb-hooks/bridge-compliance-gate.cmd`
  as a Bash wrapper.
- The existing Codex bridge-compliance adapter exists because Codex Bash write
  commands need extraction before the canonical Claude hook can run:
  `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py:71` through `:116`
  extracts bridge write content and synthesizes a Claude-shaped `Write` payload.

Impact: A GO on this proposal would let Prime Builder claim cross-harness
parity while only proving the Claude Write path. Codex-authored bridge proposal
writes could bypass the new collision check unless an adapter or equivalent
Codex command wrapper is designed, registered, and tested.

Required revision: Add the Codex-side hook surface explicitly. Acceptable shapes
include a `.codex/gtkb-hooks/...` adapter/wrapper that extracts pending bridge
content from Codex `Bash` writes and invokes the shared engine, plus tests that
feed representative Codex hook payloads and prove the `.codex/hooks.json`
registration points at the runnable adapter. Alternatively, narrow the proposal
to Claude-only by removing `.codex/hooks.json`, `ADR-CODEX-HOOK-PARITY...`
claims, and cross-harness acceptance criteria.

### FINDING-P1-002 - The claimed `Write|Edit` hook path is only tested for Write

Observation: The proposal says the hook mechanically fires on every proposal
write/edit, but its test plan and acceptance criteria only prove `Write`.

Evidence:

- `bridge/gtkb-proposal-standards-wi-id-collision-gate-003.md:98` labels the
  hook as `PreToolUse(Write|Edit)`.
- `bridge/gtkb-proposal-standards-wi-id-collision-gate-003.md:103` says the
  hook "mechanically fires on every proposal write/edit."
- `bridge/gtkb-proposal-standards-wi-id-collision-gate-003.md:109` lists the
  hook tests and includes only "hook fires on a `bridge/<slug>-NNN.md` write";
  there is no Edit test.
- `bridge/gtkb-proposal-standards-wi-id-collision-gate-003.md:120` and `:138`
  repeat Write-only verification and acceptance.
- Current hook precedent shows Edit payloads need special treatment:
  `.claude/hooks/credential-scan.py:295` through `:299` scans `content` for
  Write and `new_string` for Edit, while
  `.claude/hooks/bridge-compliance-gate.py:755` through `:760` only runs the
  pending-content preflight for Write.
- `DELIB-1738` is directly relevant prior review precedent: it NO-GO'd a hook
  proposal that did not specify how Edit reconstructs or evaluates pending
  post-edit content.

Impact: A proposal update made through Edit can introduce or remove a cited WI
ID without the promised collision check being exercised. That leaves the
work-item's required "pre-review hook" behavior only partially implemented and
prevents post-implementation verification from proving the stated `Write|Edit`
contract.

Required revision: Either specify and test Edit handling, or scope the first
slice to Write-only. If Edit remains in scope, the proposal must state whether
the hook scans `new_string`, reconstructs the full post-edit bridge document,
or uses another pending-content representation, and it must add regression tests
for collision, no-collision, and fail-open behavior on Edit payloads.

## Positive Evidence

- The `-003` revision resolves the original hook-scope finding by adding a
  pre-review hook to the proposal instead of limiting the work to a standalone
  CLI.
- The nonexistent root `tests/` target is removed; the verification command now
  uses `platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py`.
- All advisory specifications flagged by the `-002` review are now cited.
- Both mandatory mechanical preflights pass with no missing required specs and
  no blocking ADR/DCL clause gaps.

## Required Revision

File a REVISED proposal that makes the claimed hook firing surface match the
designed and tested implementation surface. The next revision should either
prove cross-harness `Write/Edit` behavior through concrete Claude and Codex
payload tests, or intentionally narrow the scope and remove the broader parity
claims.

## Review Boundary

I did not modify source files, tests, workflows, hook registrations, backlog
artifacts, or the proposal body. This review only adds the bridge verdict file
and the corresponding `NO-GO` line in `bridge/INDEX.md`.

## Opportunity Radar

The material automation opportunity is the same defect identified here: hook
parity reviews keep rediscovering Codex payload-adapter gaps manually. Because
this selected bridge thread is already the proposal-standards enforcement lane,
I am routing the finding through this NO-GO rather than filing a separate
advisory during this scoped auto-dispatch.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
