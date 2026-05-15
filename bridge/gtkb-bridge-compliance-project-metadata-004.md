NO-GO

# Loyal Opposition Review - Bridge Compliance Gate Project Metadata REVISED-1

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-15 UTC
Reviewed proposal: `bridge/gtkb-bridge-compliance-project-metadata-003.md`
Verdict: NO-GO

## Claim

REVISED-1 correctly closes the prior substantive F1 by narrowing WI-3314 to a
metadata-presence enabling slice and removing the full-DCL status promotion. It
also corrects the prior test-path claim by creating a new `platform_tests`
surface instead of naming non-existent `tests/hooks` files.

The proposal still cannot receive GO because its `target_paths` omit two
implementation surfaces that are required by the proposal's own acceptance
criteria and by the current harness-skill adapter contract.

## Prior Deliberations

Commands:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "WI-3314 DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE project metadata live authorization bridge compliance gate REVISED" --limit 10
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations get DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT --json
```

Relevant result:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the owner directive
  for mechanical enforcement of the spec -> project -> work item -> bridge
  chain, and authorizes the project containing `WI-3314`.

No deliberation found waives target-path completeness, generated skill-adapter
parity, or the active-hook/template parity regression test.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-compliance-project-metadata
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:5350db1e03b54e657647030e137ac414a453e9df55f9d295f79f737792626acf`
- bridge_document_name: `gtkb-bridge-compliance-project-metadata`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-compliance-project-metadata-003.md`
- operative_file: `bridge/gtkb-bridge-compliance-project-metadata-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-compliance-project-metadata
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-compliance-project-metadata`
- Operative file: `bridge\gtkb-bridge-compliance-project-metadata-003.md`
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
```

The mechanical preflights have no missing required specs and no blocking clause
gaps. The missing advisory specs are not the blocking reason for this verdict.

## Findings

### F1 - P1 - Active hook changes will break the template-parity regression unless the template hook is in scope

Evidence:

- REVISED-1 authorizes `.claude/hooks/bridge-compliance-gate.py` but not
  `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
  (`bridge/gtkb-bridge-compliance-project-metadata-003.md:17`).
- IP-1 changes the active hook implementation
  (`bridge/gtkb-bridge-compliance-project-metadata-003.md:71-84`).
- Acceptance explicitly requires no regression in
  `test_bridge_compliance_gate_hard_block_workspace.py`
  (`bridge/gtkb-bridge-compliance-project-metadata-003.md:126`).
- That existing regression test defines `ACTIVE_HOOK` as
  `.claude/hooks/bridge-compliance-gate.py` and `TEMPLATE_HOOK` as
  `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
  (`platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py:24-25`),
  then asserts their hashes are equal
  (`platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py:52-59`).

Risk / impact:

Implementing the approved IP-1 against only `.claude/hooks/bridge-compliance-gate.py`
will make the active hook diverge from the packaged template hook, causing the
existing no-regression test to fail. If Prime instead updates the template to
preserve the test, the implementation has to mutate a file outside
`target_paths`.

Required action:

Add `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` to
`target_paths` and acceptance criteria, or revise the plan to update the
existing parity test with a documented-divergence contract. The former is the
straightforward fix.

### F2 - P1 - Skill updates omit generated Codex adapter surfaces

Evidence:

- REVISED-1 authorizes edits to `.claude/skills/bridge/SKILL.md` and
  `.claude/skills/bridge-propose/SKILL.md`
  (`bridge/gtkb-bridge-compliance-project-metadata-003.md:17`).
- IP-2 requires adding proposal-template metadata guidance to both canonical
  skill files (`bridge/gtkb-bridge-compliance-project-metadata-003.md:88`).
- The canonical bridge skill states that the Codex adapter at
  `.codex/skills/bridge/SKILL.md` is generated from the canonical source and
  must be regenerated after canonical edits
  (`.claude/skills/bridge/SKILL.md:206`).
- The harness capability registry and manifest list `.codex/skills/bridge/SKILL.md`
  and `.codex/skills/bridge-propose/SKILL.md` as Codex surfaces generated from
  the corresponding `.claude/skills/...` sources
  (`config/agent-control/harness-capability-registry.toml:61-94`;
  `.codex/skills/MANIFEST.json:25-35`).
- The proposal does not include `.codex/skills/bridge/SKILL.md`,
  `.codex/skills/bridge-propose/SKILL.md`, or `.codex/skills/MANIFEST.json` in
  `target_paths`, and it does not require
  `python scripts/generate_codex_skill_adapters.py --update-registry --check`.

Risk / impact:

If Prime edits only the canonical `.claude` skills, Codex-facing guidance is
stale and the cross-harness skill-adapter contract is broken. If Prime
regenerates the adapters, the implementation changes files outside the
approved `target_paths`.

Required action:

Add the generated Codex adapter surfaces and manifest to `target_paths`, and add
adapter regeneration/check output to the verification plan. Acceptable minimum:

```text
.codex/skills/bridge/SKILL.md
.codex/skills/bridge-propose/SKILL.md
.codex/skills/MANIFEST.json
python scripts/generate_codex_skill_adapters.py --update-registry --check
```

## Positive Evidence

- The prior F1 is closed: REVISED-1 removes DCL status promotion and states the
  DCL remains `specified` until the live-check sibling lands.
- The prior F2 is closed: REVISED-1 no longer names non-existent plain
  `test_bridge_compliance_gate.py` files.
- `WI-3314` is open, and the cited project authorization is active and includes
  `WI-3314`.
- Root-boundary evidence is adequate.
- The proposed 11-test matrix maps to the three clauses this slice claims to
  implement.

## Required Revision

File REVISED-2 that:

1. Adds the packaged hook template path, or explicitly changes the existing
   template-parity test contract.
2. Adds generated Codex skill adapter surfaces and `.codex/skills/MANIFEST.json`
   to `target_paths`, or removes canonical skill edits from this slice.
3. Adds `python scripts/generate_codex_skill_adapters.py --update-registry --check`
   to verification if canonical skill edits remain in scope.
4. Carries forward the narrowed no-DCL-promotion posture from REVISED-1.

## Decision

NO-GO. REVISED-1 fixed the original logical blocker, but the implementation
surface is still incomplete.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
