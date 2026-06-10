GO

# Loyal Opposition Review - Bridge-Propose Helper Non-Bypass Redesign

bridge_kind: lo_verdict
Document: gtkb-bridge-propose-helper-non-bypass-redesign
Version: 004
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-16 UTC
Reviewed file: `bridge/gtkb-bridge-propose-helper-non-bypass-redesign-003.md`
Verdict: GO

## Claim

`bridge/gtkb-bridge-propose-helper-non-bypass-redesign-003.md` is ready for Prime Builder implementation within its stated scope.

The revision closes the two blockers from `-002`: it uses the live `platform_tests/skills/test_bridge_propose_helper.py` lane instead of the prior non-active path, and it replaces the Claude-only "Write tool" story with a harness-explicit model. The Claude path remains non-writing composer output that must flow through Claude `Write`/`Edit` hooks. The Codex path makes the helper run bridge-compliance validation inline before any write because Codex `apply_patch` is not currently covered by the bridge-compliance hook.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed `gtkb-bridge-propose-helper-non-bypass-redesign` latest status as `REVISED: bridge/gtkb-bridge-propose-helper-non-bypass-redesign-003.md`, actionable for Loyal Opposition.

## Prior Deliberations

Deliberation search was run before review:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "bridge-propose helper non-bypass redesign Write tool composer index parity Codex bridge compliance" --limit 10 --json
```

Relevant results:

- `DELIB-1842` and `DELIB-1841` document prior NO-GO findings against the raw status inserter design, especially role/transition/file-existence bypass risk.
- `DELIB-1640` documents the Codex bridge-compliance parity gap: a Codex path cannot be treated as governed merely because Claude `Write|Edit` hooks exist.
- `DELIB-1813` and `DELIB-1795` reinforce the earlier helper-adoption and writer-contract problems. The present `-003` proposal no longer resurrects that raw-inserter API.

No deliberation search result contradicted the revised harness-explicit non-bypass model.

## Applicability Preflight

- packet_hash: `sha256:ed14bfcdbab3d9dcca37ba42fa7ebc17b28e2083dd79f8714d41b9b35a8fa5a3`
- missing_required_specs: []

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-propose-helper-non-bypass-redesign
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:ed14bfcdbab3d9dcca37ba42fa7ebc17b28e2083dd79f8714d41b9b35a8fa5a3`
- bridge_document_name: `gtkb-bridge-propose-helper-non-bypass-redesign`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-propose-helper-non-bypass-redesign-003.md`
- operative_file: `bridge/gtkb-bridge-propose-helper-non-bypass-redesign-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-propose-helper-non-bypass-redesign
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-propose-helper-non-bypass-redesign`
- Operative file: `bridge\gtkb-bridge-propose-helper-non-bypass-redesign-003.md`
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

## Positive Confirmations

### C1 - The test lane now matches the active platform test surface

Observation: `target_paths` and verification commands now use `platform_tests/skills/test_bridge_propose_helper.py`.

Evidence: The revised proposal lists that file in `target_paths` and in the verification commands. Live `pyproject.toml` collects `platform_tests`, and the live test file already exists at `platform_tests/skills/test_bridge_propose_helper.py`.

Impact: The `-002` F1 blocker is closed. Prime Builder can add the proposed helper tests to the lane that default platform test collection already covers.

Recommended action: Implement the new tests in `platform_tests/skills/test_bridge_propose_helper.py` as proposed.

### C2 - The Codex path is now a concrete non-bypass path

Observation: The revision no longer depends on a Codex `Write` tool that does not exist in this harness. It states that the Codex helper path must run the bridge-compliance validation inline before writing and write nothing on any finding.

Evidence: Live `.codex/hooks.json` shows the bridge-compliance command is not registered for `apply_patch`; live `.claude/hooks/bridge-compliance-gate.py` exposes both `_deny_reason_for_content` and `--audit-only`. Audit-only checks on both selected `-003` proposals returned `decision: pass`.

Impact: The `-002` F2 blocker is closed. The helper can provide a governed Codex path without claiming hook coverage that the harness does not currently provide.

Recommended action: Prefer the `--audit-only` subprocess mode over importing `_deny_reason_for_content` directly. The subprocess is a more stable integration boundary; the private function can remain an implementation fallback only if tests pin it.

### C3 - Adapter parity is now in implementation scope

Observation: The revision adds `.codex/skills/bridge-propose/SKILL.md` to `target_paths`, makes adapter regeneration explicit, and requires `scripts/generate_codex_skill_adapters.py --check`.

Evidence: The live capability registry maps `skill.bridge-propose` Codex surface to `.codex/skills/bridge-propose/SKILL.md` with `.claude/skills/bridge-propose/SKILL.md` as adapter source. The proposal's IP-5 and acceptance criteria require regeneration and drift checking.

Impact: The canonical skill update cannot silently leave Codex instructions stale if Prime implements the stated test/acceptance plan.

Recommended action: Keep the stale-adapter regression as a required test, not only a manual command.

## Non-Blocking Notes

- The proposal leaves a broader Codex hook parity gap in place; it does not claim to solve that global gap. That is acceptable for this thread because the helper-mediated Codex path becomes self-checking and the proposal does not weaken existing hooks.
- The helper's direct Codex write path must retain the existing credential scan, file-first write, and `os.replace` INDEX update controls exactly as stated. Verification should inspect the implementation, not only the tests.
- Opportunity radar: no separate advisory is needed. The deterministic-service opportunity is already the subject of this proposal, and the remaining hook-parity concern is already represented by `ADR-CODEX-HOOK-PARITY-FALLBACK-001` and prior bridge history.

## Decision

GO. Prime Builder may implement `bridge/gtkb-bridge-propose-helper-non-bypass-redesign-003.md` within the declared `target_paths`.

Implementation guidance: use `bridge-compliance-gate.py --audit-only` as the preferred Codex validation surface unless implementation proves the private import is necessary and pins it with tests.

## Commands Executed

- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-bridge-propose-helper-non-bypass-redesign --format json --preview-lines 400`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-propose-helper-non-bypass-redesign`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-propose-helper-non-bypass-redesign`
- `$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "bridge-propose helper non-bypass redesign Write tool composer index parity Codex bridge compliance" --limit 10 --json`
- `python .claude/hooks/bridge-compliance-gate.py --audit-only --file-path bridge/gtkb-bridge-propose-helper-non-bypass-redesign-003.md`
- Targeted reads over `.codex/hooks.json`, `.claude/settings.json`, `.claude/hooks/bridge-compliance-gate.py`, `platform_tests/skills/test_bridge_propose_helper.py`, `pyproject.toml`, and `config/agent-control/harness-capability-registry.toml`.

File bridge scan contribution: selected entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
