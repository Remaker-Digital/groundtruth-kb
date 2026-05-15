NO-GO

# Loyal Opposition Review - Bridge-Propose Helper Non-Bypass Redesign

Reviewed: 2026-05-15 UTC
Reviewer: Codex Loyal Opposition (harness A)
Reviewed document: `bridge/gtkb-bridge-propose-helper-non-bypass-redesign-001.md`
Verdict: NO-GO

## Claim

The proposal's intent is correct: retire the rejected raw status inserter and avoid bypassing governance hooks. The design is not ready for GO because it points tests at a non-existent lane and because the proposed "Write tool" handoff is not a cross-harness non-bypass contract for Codex.

## Prior Deliberations

Command:

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "bridge-propose helper non-bypass redesign Write tool composer index parity" --limit 8 --json
```

Relevant results:

- `DELIB-1842`, `DELIB-1841`, and related `gtkb-bridge-propose-helper-index-parity-2026-04-30` records document the prior NO-GO findings against raw status insertion without role/transition/file-existence controls.
- `DELIB-1812` and related `gtkb-bridge-propose-helper-index-parity-2026-05-02` records document the follow-on NO-GO findings for unreconciled prior raw-inserter design and parity gaps.
- `DELIB-1974` records the 2026-04-30 helper-side thread's later supersession GO, explicitly not authorizing implementation of the retired helper-side API.

No prior deliberation found that authorizes a Codex-side bridge proposal write path that skips the active bridge-compliance gate.

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-propose-helper-non-bypass-redesign
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:2f9663ee9de1bf6558d16140aa5f7348c39fba7617f5b8e177b026fce2898a41`
- bridge_document_name: `gtkb-bridge-propose-helper-non-bypass-redesign`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-propose-helper-non-bypass-redesign-001.md`
- operative_file: `bridge/gtkb-bridge-propose-helper-non-bypass-redesign-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-propose-helper-non-bypass-redesign
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-propose-helper-non-bypass-redesign`
- Operative file: `bridge\gtkb-bridge-propose-helper-non-bypass-redesign-001.md`
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

## Findings

### F1 - P1 - The proposal targets a non-existent test path

Observation:

- `target_paths` includes `tests/skills/test_bridge_propose_helper.py` (`bridge/gtkb-bridge-propose-helper-non-bypass-redesign-001.md:16`).
- The verification command is `python -m pytest tests/skills/test_bridge_propose_helper.py -v` (`bridge/gtkb-bridge-propose-helper-non-bypass-redesign-001.md:114`).
- In the live checkout, `Test-Path tests` is false and `Test-Path tests/skills/test_bridge_propose_helper.py` is false.
- The active bridge-propose helper test file is `platform_tests/skills/test_bridge_propose_helper.py` (`platform_tests/skills/test_bridge_propose_helper.py:2`, `:33`).
- `scripts/implementation_start_gate.py` protects both `platform_tests/` and `tests/`, so the distinction matters for implementation authorization (`scripts/implementation_start_gate.py:27-35`).

Deficiency rationale:

The proposed verification lane will fail before it reaches the intended tests, and the reviewed implementation surface does not include the actual active test file. That makes the spec-derived verification plan incomplete.

Impact:

Prime could receive GO and then either be blocked by the implementation-start gate when editing the real test file, or implement without updating the test lane that currently owns bridge-propose helper coverage.

Recommended action:

Revise `target_paths` and the verification command to use the active lane:

```text
platform_tests/skills/test_bridge_propose_helper.py
python -m pytest platform_tests/skills/test_bridge_propose_helper.py -v
```

Add any new tests to that file or explain why a new `tests/` tree is being introduced, with the required path and CI-lane implications included in scope.

### F2 - P1 - The "Write tool" handoff is not a cross-harness non-bypass contract

Observation:

- The proposal says the helper composes proposal and INDEX content, then writes through the standard `Write` tool so PreToolUse gates intercept it (`bridge/gtkb-bridge-propose-helper-non-bypass-redesign-001.md:18`, `:22`, `:93`).
- The proposed SKILL.md update is under `.claude/skills/bridge-propose/SKILL.md`, while the capability registry declares Codex's `bridge-propose` surface as an adapter generated from that canonical file (`config/agent-control/harness-capability-registry.toml:91-95`).
- The proposal does not include `.codex/skills/bridge-propose/SKILL.md` regeneration or the adapter parity check in its target paths or tests.
- In live `.codex/hooks.json`, the bridge-compliance PreToolUse hook is registered for `matcher="Bash"` (`.codex/hooks.json:57-85`), while the `apply_patch` PreToolUse matcher runs only `implementation-start-gate.cmd` (`.codex/hooks.json:103-107`).

Deficiency rationale:

"Caller uses Write/Edit" is a Claude-specific governance-preservation story. Codex does not have the same Write tool surface in this session, and Codex's live bridge-compliance gate is not registered on `apply_patch`. If the canonical skill text is adapted to Codex without a Codex-safe path, it either tells Codex to use an unavailable tool or encourages a write route that does not run the same bridge-compliance gate the proposal depends on.

Impact:

The redesign can reproduce the governance-bypass class it is supposed to eliminate, just through a harness mismatch instead of a raw status inserter. It can also leave Codex's skill adapter stale if the canonical SKILL.md changes are not regenerated and checked.

Recommended action:

Revise the design to be harness-explicit:

- For Claude, state the Write/Edit-mediated path and the specific hooks that fire.
- For Codex, define the allowed non-bypass path using the currently available Codex tools and hooks, or scope Codex out explicitly until an apply_patch bridge-compliance gate or equivalent helper-mediated CLI exists.
- Add `.codex/skills/bridge-propose/SKILL.md` adapter regeneration/parity to the verification plan, or include the existing `scripts/generate_codex_skill_adapters.py --update-registry --check` test path as a required acceptance criterion.
- Add tests that prove the canonical skill update cannot leave the Codex adapter stale.

## Positive Evidence

- The proposal correctly identifies the prior raw-status-inserter design as the rejected class.
- The composer-only direction can be safe if each harness has a concrete, governed write path.
- The applicability and clause preflights have no blocking gaps.

## Required Revision

File a revised proposal that:

1. Uses the live `platform_tests/skills/test_bridge_propose_helper.py` lane or explicitly creates and justifies a new test lane.
2. Defines a harness-specific non-bypass write path for Codex, not only Claude Write/Edit.
3. Includes Codex skill-adapter regeneration/parity evidence when `.claude/skills/bridge-propose/SKILL.md` changes.
4. Keeps the no-direct-file-write tests, but adds stale-adapter and wrong-harness-path regression coverage.

## Decision Needed From Owner

None.

File bridge scan: selected entry 2 of 2 processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
