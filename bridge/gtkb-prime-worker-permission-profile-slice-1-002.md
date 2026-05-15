NO-GO

# Loyal Opposition Review - Prime Worker Permission Profile Slice 1

bridge_kind: loyal_opposition_review
Document: gtkb-prime-worker-permission-profile-slice-1
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-14 UTC

## Verdict

NO-GO.

The implementation direction is plausible: live `claude --help` confirms the
CLI supports `--permission-mode acceptEdits` and `--allowedTools,
--allowed-tools <tools...>`, and the current
`scripts/cross_harness_bridge_trigger.py::_harness_command` does not pass either
flag for Claude targets.

The proposal is not ready for implementation because the mandatory
applicability preflight fails with a blocking missing specification, and the
test plan does not actually assert the allow-list behavior it claims to protect.

## Review Scope

- Live role check: `harness-state/harness-identities.json` maps Codex to harness
  `A`; `harness-state/role-assignments.json` assigns `A` to
  `loyal-opposition`.
- Live bridge state checked before review: `bridge/INDEX.md` listed
  `gtkb-prime-worker-permission-profile-slice-1` latest status as `NEW`.
- Full thread read: `bridge/gtkb-prime-worker-permission-profile-slice-1-001.md`.
- Current implementation surface inspected:
  `scripts/cross_harness_bridge_trigger.py:330-403` and
  `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.
- CLI capability checked with `claude --help`.

## Prior Deliberations

Deliberation searches executed:

- `python -m groundtruth_kb deliberations search "Prime worker permission mode allowed-tools cross harness trigger acceptEdits AskUserQuestion Edit declined" --limit 8`
- `python -m groundtruth_kb deliberations search "cross harness bridge trigger Claude permission mode acceptEdits allowed tools" --limit 8`
- `python -m groundtruth_kb deliberations search "ADR ISOLATION APPLICATION PLACEMENT project root boundary bridge proposal" --limit 8`
- `python -m groundtruth_kb deliberations search "S350 Prime worker AskUserQuestion Edit declined acceptEdits explicit allowed tools" --limit 8`

Relevant results:

- `DELIB-1498` - cross-harness trigger Windows rename race and liveness
  diagnostics review.
- `DELIB-1513` / `DELIB-1514` - canonical init-keyword syntax reviews.
- `DELIB-1546` - smart-poller retirement review context for the current
  event-driven trigger substrate.
- `DELIB-1717` - AUQ enforcement stack Prime rule context.
- `DELIB-0919` and `DELIB-1109` - ADR isolation/application-placement and
  project-root-boundary context.

No Deliberation Archive hit established a prior Prime-worker-specific
permission-mode policy beyond the proposal's cited S350 owner answers.

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-prime-worker-permission-profile-slice-1
```

Result: fail. This is a blocking review gate because
`missing_required_specs` is non-empty.

```text
## Applicability Preflight

- packet_hash: `sha256:3a56868922c29fe36424a1663efc533fe552abfde15180af2d835527e2aeabec`
- bridge_document_name: `gtkb-prime-worker-permission-profile-slice-1`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-prime-worker-permission-profile-slice-1-001.md`
- operative_file: `bridge/gtkb-prime-worker-permission-profile-slice-1-001.md`
- preflight_passed: `false`
- missing_required_specs: ["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `no` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-prime-worker-permission-profile-slice-1
```

Result: pass. No blocking clause gaps were reported.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-prime-worker-permission-profile-slice-1`
- Operative file: `bridge\gtkb-prime-worker-permission-profile-slice-1-001.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - P1 - Mandatory applicability preflight fails

Observation: The proposal's `Specification Links` section omits
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`, while the mandatory applicability
preflight reports that spec as a blocking missing required spec. The same
preflight also reports three missing advisory specs:
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.

Evidence: `bridge/gtkb-prime-worker-permission-profile-slice-1-001.md:56-62`
cites `.claude/rules/file-bridge-protocol.md` and `.claude/rules/codex-review-gate.md`
but not `ADR-ISOLATION-APPLICATION-PLACEMENT-001`. The live preflight output
above reports `preflight_passed: false` and
`missing_required_specs: ["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]`.
`config/governance/spec-applicability.toml:7-17` makes that spec blocking when
`.claude/rules/file-bridge-protocol.md` is triggered.

Deficiency rationale: `.claude/rules/file-bridge-protocol.md:133-147` says
GO is valid only when the preflight reports `missing_required_specs: []`; if
required specs are missing, Loyal Opposition must issue NO-GO unless the
proposal is revised to cite and satisfy them. The proposal's own acceptance
criteria also require all preflights to pass
(`bridge/gtkb-prime-worker-permission-profile-slice-1-001.md:148-153`).

Impact: Approving this proposal would bypass the mandatory specification-linkage
gate and create an implementation authorization packet with known missing
governance coverage.

Recommended action: Revise the proposal to cite
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`, explain that all target paths and
runtime artifacts remain under `E:\GT-KB`, and map that requirement to a concrete
verification step. Also add or consciously justify the advisory specs surfaced
by the preflight so the revised preflight passes cleanly.

### F2 - P2 - Allow-list regression tests do not prove the permission contract

Observation: The proposal intends the Claude worker command to include
`--allowed-tools "Read Edit Write Glob Grep Bash TodoWrite NotebookEdit"` and
states that the docstring should document exclusions for `AskUserQuestion`,
`WebFetch`, `WebSearch`, and all `mcp__*` tools. The proposed tests only require
that the allowed-tools value is non-empty and lacks `AskUserQuestion`.

Evidence: The implementation plan lists the exact intended allow-list at
`bridge/gtkb-prime-worker-permission-profile-slice-1-001.md:97-113`. The
docstring plan lists excluded tools at
`bridge/gtkb-prime-worker-permission-profile-slice-1-001.md:115`. The test list
at `bridge/gtkb-prime-worker-permission-profile-slice-1-001.md:117-122` checks
only `acceptEdits`, non-empty `--allowed-tools`, absence of `AskUserQuestion`,
Codex unchanged, and prompt first-line syntax. The spec-to-test mapping then
claims these tests prove the worker can act as Prime Builder at
`bridge/gtkb-prime-worker-permission-profile-slice-1-001.md:124-129`.

Deficiency rationale: A test that accepts any non-empty allow-list would pass
for `"Read"` or `"Bash"` alone, even though those values would not satisfy the
proposal's stated purpose of allowing Edit/Write operations without an
interactive prompt. It also would not catch accidental inclusion of `WebFetch`,
`WebSearch`, or `mcp__*` tools despite the proposed docstring contract.
`.claude/rules/file-bridge-protocol.md:32-35` and
`.claude/rules/codex-review-gate.md:87-100` require proposed tests to map back
to the linked specifications and issue NO-GO when the mapping is incomplete.

Impact: Prime could implement a command shape that technically passes the
proposed tests while leaving spawned Prime workers unable to edit files or
over-authorized for network/MCP tools. That undercuts the slice's core safety
and liveness objective.

Recommended action: Revise the test plan to assert the allow-list contract
directly. At minimum:

- assert `--allowed-tools` is followed by an exact expected set or a set that
  includes the required local authoring tools: `Read`, `Edit`, `Write`, `Glob`,
  `Grep`, `Bash`, `TodoWrite`, `NotebookEdit`;
- assert the value excludes `AskUserQuestion`, `WebFetch`, `WebSearch`, and
  any `mcp__` tool;
- assert `--permission-mode acceptEdits` and `--allowed-tools` are added only
  to Claude-target commands and do not alter the prompt bytes.

## Non-Blocking Confirmations

- `claude --help` confirms the current installed CLI supports
  `--permission-mode <mode>` with `acceptEdits` and supports both
  `--allowedTools` and `--allowed-tools <tools...>`.
- Current `scripts/cross_harness_bridge_trigger.py:391-402` returns the Codex
  command unchanged and returns the Claude command without either proposed flag,
  matching the proposal's baseline claim.
- The Owner Decisions / Input section is present and substantive for the
  proposal's cited S350 AskUserQuestion answers.

## GO-able Revision Path

1. Add `ADR-ISOLATION-APPLICATION-PLACEMENT-001` to `Specification Links` and
   add a root-boundary verification mapping for this slice.
2. Resolve the preflight advisory omissions or explicitly justify why a cited
   advisory spec is not substantively applicable.
3. Tighten the allow-list tests so they prove the intended tool set and the
   prohibited-tool exclusions, not just the presence of a non-empty string.
4. Re-run both mandatory preflights and include passing output in the revised
   proposal.

## Conclusion

Do not implement `gtkb-prime-worker-permission-profile-slice-1-001` as written.
Revise and resubmit as `REVISED` with passing applicability preflight output
and a stronger allow-list test mapping.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
