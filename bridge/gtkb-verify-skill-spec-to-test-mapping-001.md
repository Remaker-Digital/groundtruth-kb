NEW

# Implementation Proposal - /verify Skill + Spec-to-Test Mapping Helper (WI-3261)

bridge_kind: implementation_proposal
Document: gtkb-verify-skill-spec-to-test-mapping
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3261

target_paths: [".claude/skills/verify/SKILL.md", ".codex/skills/verify/SKILL.md", "scripts/spec_to_test_mapper.py", "tests/scripts/test_spec_to_test_mapper.py", "platform_tests/scripts/test_spec_to_test_mapper.py"]

This NEW proposal lands a `/verify` skill (Codex parity-aware) plus a `spec_to_test_mapper.py` CLI helper. The helper generates the spec-to-test mapping table that every implementation report must include per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

## Claim

Two artifacts: (1) a Claude-side `/verify` skill at `.claude/skills/verify/SKILL.md` (Codex mirror at `.codex/skills/verify/SKILL.md`) that orchestrates verdict-author work; (2) a CLI helper `scripts/spec_to_test_mapper.py` that, given a list of spec IDs, queries `current_tests` for tests linked to those specs and emits a markdown table suitable for paste into implementation reports.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - source spec; mapping helper is its operationalization.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; verify skill operates within it.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - deterministic-services framing.
- `SPEC-AUQ-POLICY-ENGINE-001` - skill is a thin orchestration surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `GOV-STANDING-BACKLOG-001` - WI-3261 tracked.
- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - batch-3 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner directive "Please continue with the next priority project" - authorizes this NEW.

## Requirement Sufficiency

Existing requirements sufficient. WI-3261 description + DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 specify the helper's role.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-DETERMINISTIC-SERVICES-001 per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch3-deterministic-services-authorization.json`. Review-packet inventory: IP-1 (skill) + IP-2 (helper) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed at `bridge/gtkb-verify-skill-spec-to-test-mapping-001.md`; new top entry prepended.

## Proposed Scope

### IP-1: /verify skill scaffold

In `.claude/skills/verify/SKILL.md`:

```markdown
---
name: verify
description: Compose VERIFIED verdict files for bridge thread review. Use when authoring post-implementation verification verdicts.
---

# /verify

When the owner asks to "verify <bridge-id>" or "compose verdict for <bridge-id>":
1. Read the latest version of the bridge thread.
2. Run `python scripts/spec_to_test_mapper.py --bridge-id <id>` to generate the spec-to-test table.
3. Run the cited tests; capture results.
4. Compose a VERIFIED or NO-GO verdict file at the next version number.
5. Update bridge/INDEX.md with the verdict line.

[Detailed workflow ...]
```

Codex mirror at `.codex/skills/verify/SKILL.md`.

### IP-2: spec_to_test_mapper.py

CLI: `python scripts/spec_to_test_mapper.py --bridge-id <id>` (extracts specs from proposal) OR `--spec-id SPEC-X --spec-id SPEC-Y` (explicit).

For each spec, query `current_tests` for rows with `spec_id` matching. Emit markdown table:

```
| Spec | Test ID | Status | Last run |
|---|---|---|---|
| SPEC-1234 | TEST-001 | PASS | 2026-05-14 |
```

Also emit JSON for tooling consumption.

### IP-3: Tests + (no spec promotion - new skill)

Tests cover: mapper output format, missing-spec graceful handling, multi-spec aggregation, bridge-id parsing.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Mapper emits markdown table | `test_mapper_emits_markdown_table` |
| Mapper emits JSON variant | `test_mapper_emits_json_when_requested` |
| Spec with no tests reported as empty | `test_mapper_handles_spec_without_tests` |
| Multiple specs aggregated | `test_mapper_aggregates_multiple_specs` |
| Bridge-id extraction from proposal | `test_mapper_extracts_specs_from_bridge_id` |
| Test status reflects assertion_runs | `test_mapper_status_from_assertion_runs` |

Run: `python -m pytest tests/scripts/test_spec_to_test_mapper.py -v`.

## Acceptance Criteria

- IP-1 skills landed (Claude + Codex mirror).
- IP-2 helper landed; 6 tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: skill recommendation conflicts with existing manual verdict-authoring patterns. Mitigation: skill is opt-in; doesn't replace existing workflow.
- Rollback: remove the skill files + helper script.

## Recommended Commit Type

`feat` - new skill + helper. ~100 LOC (skill markdown + Python + tests).
