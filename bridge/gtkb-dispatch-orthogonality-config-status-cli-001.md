NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-wi-4578-implementation-proposal-20260615
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; Prime Builder

# Bridge Dispatch Orthogonality, Configuration, and Status CLI Implementation Proposal

bridge_kind: prime_proposal
Document: gtkb-dispatch-orthogonality-config-status-cli
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: ["groundtruth.db", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/harness_projection.py", "groundtruth-kb/src/groundtruth_kb/harness_ops.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py", "scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/_kb_attribution.py", "scripts/bridge_author_metadata.py", "config/dispatcher/rules.toml", "harness-state/harness-registry.json", "AGENTS.md", "CLAUDE.md", ".claude/rules/operating-role.md", ".claude/rules/canonical-terminology.md", ".codex/skills/bridge-config/SKILL.md", ".claude/skills/bridge-config/SKILL.md", "platform_tests/groundtruth_kb/test_mode_switch_invariants.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py", "platform_tests/groundtruth_kb/cli/test_harness_cli.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_single_harness_bridge_dispatcher.py", "platform_tests/scripts/test_bridge_author_metadata.py", "platform_tests/scripts/test_kb_attribution.py", "platform_tests/scripts/test_fab01_dispatch_substrate_revival.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

implementation_scope: membase, source, config, cli, tests, skill, protected_narrative
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Implement `WI-4578`, the bridge-dispatch correction approved for governance direction at `bridge/gtkb-dispatch-architecture-canonicalization-002.md`.

The implementation makes the requested topology durable:

- Codex: Prime Builder, dispatchable.
- Claude Code: Prime Builder, not dispatchable.
- Ollama, OpenRouter, Antigravity: Loyal Opposition, dispatchable.

It also removes the stale model in which active role assignment and dispatchability are coupled, or in which the dispatcher assumes exactly one active Prime Builder and exactly one active Loyal Opposition.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` - harness role, status, invocation surfaces, and generated projection are registry-backed. This implementation adds explicit dispatchability metadata to that path.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all live GT-KB implementation, verification, and generated skill files remain inside the `E:\GT-KB` root boundary; this work does not target Agent Red or any separate application repository.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatch target resolution and audit state come from a centralized dispatcher service path.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatch targets may be harness, role, topic, or prompt; the implementation uses role plus subject/topic rules rather than a single role label only.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatch eligibility rules are declarative and must be read by the dispatcher.
- `SPEC-TOPIC-ENVELOPE-ROUTER-001` - `::open <type>` is the topic/activity declaration surface.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - session subject and payload state must be read through authoritative session-envelope surfaces.
- `SPEC-TAFE-R4` - hard eligibility gates precede calibrated precedence and cost/quality tie-breaks.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` remains the live queue authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this proposal includes project linkage, target paths, and a spec-derived verification plan.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the owner clarification is now a formal work item, PAUTH, and bridge-reviewed implementation lane.

## Prior Deliberations

- `DELIB-20263438` - owner decision for role/dispatchability orthogonality, rule-based dispatch, and availability/cost/quality selection.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D13-20260612` - hard eligibility gates followed by calibrated precedence tiers.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-V1-DISPATCH-POLICY-20260612` - conservative deterministic v1 routing.
- `DELIB-20260635` and `DELIB-20260637` - dispatch/session/topic envelope containment and `::open <type>` routing intent.
- `bridge/gtkb-dispatch-architecture-canonicalization-002.md` - Loyal Opposition GO on the canonical interpretation and `WI-4578` implementation lane.

## Owner Decisions / Input

No new owner decision is required. `DELIB-20263438` captures the owner directive, and `PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI` authorizes this bounded work item. Formal artifact and protected narrative mutations still require approval packets; implementation source edits still require a matching implementation-start packet after this proposal receives GO.

## Requirement Sufficiency

Existing requirements sufficient. The specified registry, dispatch service, dispatch-envelope, topic-envelope, session-envelope, TAFE R4, and bridge-governance specs plus `DELIB-20263438` provide enough authority to implement this corrective slice. Any new ADR/DCL/SPEC rows created during implementation are canonicalization deliverables that make the already-approved owner decision visible to future agents; they do not introduce a different requirement.

## Implementation Plan

1. **Canonical artifact updates.** Insert or update formal MemBase artifacts for role-dispatchability orthogonality, dispatch rule eligibility, and the bridge configuration/status CLI. Keep the retired single-active-per-role artifacts retired.

2. **Registry/projection updates.** Store explicit dispatchability in registry metadata and update `harness_projection` so `can_receive_dispatch` is not inferred solely from `harness_type`. Keep `event_driven_hooks` as a deprecated compatibility alias.

3. **CLI and health reporting.** Add bridge configuration/status/health commands that report role, status, dispatchability, headless launchability, rule eligibility, last dispatch result, readiness, and selected/blocked reasons. The commands must offer JSON output and compact human output.

4. **Dispatcher updates.** Update cross-harness and single-harness dispatch to apply independent dispatchability filtering plus require/block rules over role, session subject, and topic/activity when present. Multiple eligible same-role harnesses remain valid; final selection follows hard gates, availability, precedence, and cost/quality tie-breaks.

5. **Contradiction cleanup.** Replace stale source docstrings, tests, and narrative text that still imply exactly one active Prime Builder and one active Loyal Opposition. Attribution helpers must not fail when more than one Prime Builder exists.

6. **Skill.** Add a `bridge-config` skill for Codex and Claude explaining how to inspect, change, and verify bridge dispatch configuration through the CLI.

## Spec-Derived Verification Plan

```text
python -m pytest platform_tests/groundtruth_kb/test_mode_switch_invariants.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/groundtruth_kb/cli/test_harness_cli.py -q --tb=short
```

Expected: pass. Proves multi-PB with one dispatchable PB is allowed, multi-LO dispatch pool is allowed, and role assignment is independent from dispatchability.

```text
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
```

Expected: pass. Proves explicit dispatchability filtering, rule eligibility, fallback, and cross/single dispatcher parity.

```text
python -m pytest platform_tests/scripts/test_bridge_author_metadata.py platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_fab01_dispatch_substrate_revival.py -q --tb=short
```

Expected: pass. Proves attribution under multiple Prime Builders and compatibility for `can_receive_dispatch` / `event_driven_hooks`.

```text
python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/harness_projection.py groundtruth-kb/src/groundtruth_kb/harness_ops.py groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py groundtruth-kb/src/groundtruth_kb/project/doctor.py scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py scripts/_kb_attribution.py scripts/bridge_author_metadata.py
```

Expected: pass.

```text
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/harness_projection.py groundtruth-kb/src/groundtruth_kb/harness_ops.py groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py groundtruth-kb/src/groundtruth_kb/project/doctor.py scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py scripts/_kb_attribution.py scripts/bridge_author_metadata.py
```

Expected: pass.

```text
python -m groundtruth_kb harness roles
python -m groundtruth_kb bridge health --json
python -m groundtruth_kb status
```

Expected: roles show Codex and Claude as Prime Builder role holders with only Codex dispatchable for PB; bridge health reports Ollama/OpenRouter/Antigravity as eligible LO targets; `gt status` remains PASS for bridge and bridge-dispatch, aside from unrelated existing WARN components.

```text
rg -n "exactly one active|single active|single-ACTIVE-per-role|one active Prime Builder|one active Loyal Opposition" AGENTS.md CLAUDE.md .claude/rules groundtruth-kb/src scripts platform_tests -g "!groundtruth-kb/.venv/**" -g "!archive/**"
```

Expected: no live contradictory guidance remains except explicitly retired historical references.

## Risk / Rollback

Primary risk is coupling this bridge-dispatch fix to the larger TAFE cutover. Mitigation: this proposal does not make TAFE authoritative and does not replace `bridge/INDEX.md`.

Second risk is breaking legacy readers of `event_driven_hooks`. Mitigation: preserve it as a deprecated alias while tests lock the compatibility behavior.

Rollback is append-only for MemBase artifacts and a normal revert for source/config/skill/narrative files. If the dispatcher selection change is flawed, revert the dispatcher/CLI source while leaving the owner-decision and WI/PAUTH evidence intact.
