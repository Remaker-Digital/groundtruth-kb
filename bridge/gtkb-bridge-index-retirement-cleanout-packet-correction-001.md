NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-keep-working-20260616-bridge-index-revision
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop automation; Prime Builder

# Bridge Index Retirement Cleanout Packet Correction Proposal

bridge_kind: prime_proposal
Document: gtkb-bridge-index-retirement-cleanout-packet-correction
Version: 001
Source-Thread: bridge/gtkb-bridge-index-retirement-cleanout
Author: Prime Builder (Codex, harness A)
Date: 2026-06-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: ["groundtruth.db", "AGENTS.md", "CLAUDE.md", "README.md", "CONTRIBUTING.md", "CHANGELOG.md", ".agent/skills/**", ".api-harness/skills/**", ".claude/rules/**", ".claude/skills/**", ".claude/hooks/**", ".claude/settings.json", ".codex/skills/**", ".codex/hooks.json", "config/agent-control/**", "config/dispatcher/**", "config/governance/**", "config/registry/**", "docs/**", "applications/Agent_Red/docs/**", "scripts/**", "groundtruth-kb/docs/**", "groundtruth-kb/src/**", "groundtruth-kb/templates/**", "groundtruth-kb/tests/**", "platform_tests/**", "harness-state/harness-registry.json", "harness-state/harness-identities.json", "bridge/gtkb-bridge-index-retirement-cleanout-*.md", "bridge/gtkb-bridge-index-retirement-cleanout-packet-correction-*.md", "bridge/gtkb-lo-review-dispatch-reliability-*.md", "bridge/INDEX.md"]

implementation_scope: implementation_start_packet_correction, no_index_cutover_cleanup, source, config, cli, tests, skills, hooks, templates, protected_narrative, historical_classification, harness_dispatch_reliability
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This revision corrects the latest operative proposal for
`gtkb-bridge-index-retirement-cleanout` after the independent Antigravity GO in
`bridge/gtkb-bridge-index-retirement-cleanout-006.md` proved impossible to
activate through the implementation-start gate.

The GO is directionally valid, but the latest reviewed proposal addendum
(`005`) does not contain parser-recognized `## Specification Links` or
`## Requirement Sufficiency` sections, and it names
`PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE` while citing the
`PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI`
authorization. The project mismatch correctly causes
`scripts/implementation_authorization.py begin` to fail closed.

This revision does not change the owner's no-index direction. It makes the
approved cleanout proposal machine-valid for a future implementation-start
packet by:

- retaining the no-backward-compatibility invariant;
- using project metadata that matches the cited PAUTH;
- carrying forward the required specification links;
- adding the exact required requirement-sufficiency state; and
- clarifying that TAFE remains a related subsystem, not the machine-readable
  project authorization for this WI-4578 implementation lane.

## Specification Links

- `DELIB-20263438` - owner decision that bridge dispatch is rule-based and
  independent from operating role assignment; old bridge-index behavior must not
  confuse the corrected dispatcher architecture.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher state, target
  resolution, audit recording, and status belong to the centralized dispatch
  path rather than a generated index file.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - bridge work routing depends on
  harness, role, topic, prompt, and envelope data.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - declarative dispatch rules are routing
  authority.
- `SPEC-TOPIC-ENVELOPE-ROUTER-001` - `::open <activity>` participates in
  dispatch eligibility.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - session state must be read from
  durable session-envelope surfaces.
- `SPEC-TAFE-R4`, `SPEC-TAFE-R5`, and `SPEC-TAFE-R6` - dispatcher hard gates,
  health, and telemetry must replace index-derived actionability where TAFE
  participates in bridge queue state.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - current index-canonical clauses must be
  revised, retired, or superseded so they no longer require `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  carries concrete governing links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision includes
  machine-readable project authorization, project, and work-item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must
  carry forward the verification mapping and observed commands.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the owner correction is durable
  architecture/process authority and cleanup findings must remain traceable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all active GT-KB work must remain
  under `E:\GT-KB`, with Agent Red paths touched only as explicitly in-root
  adopter documentation/tests.

## Prior Deliberations

- `DELIB-20263438` - owner decision for corrected role/dispatch architecture.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D13-20260612` - dispatch hard gates before
  calibrated selection.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-V1-DISPATCH-POLICY-20260612` - conservative
  deterministic v1 dispatch routing.
- `DELIB-20260635` and `DELIB-20260637` - session/topic envelope containment.
- `DELIB-20263305` - TAFE dual-write INDEX parity review; relevant as
  superseded context because the current owner direction rejects generated
  compatibility output.
- `DELIB-20263190` - earlier bridge-index guard work admitted to bridge
  reliability scope; relevant as historical predecessor work.
- `bridge/gtkb-bridge-index-retirement-cleanout-003.md` - corrected NO-GO
  identifying mandatory preflight dependence on `bridge/INDEX.md`.
- `bridge/gtkb-bridge-index-retirement-cleanout-004.md` and
  `bridge/gtkb-bridge-index-retirement-cleanout-005.md` - full revised
  inventory and final sweep addendum carried forward here.
- `bridge/gtkb-bridge-index-retirement-cleanout-006.md` - independent
  Antigravity GO approving the cleanup direction.

## Owner Decisions / Input

No new owner decision is required for this proposal correction. Existing owner
direction already selected:

- no `bridge/INDEX.md` file;
- no backward-compatibility bridge index output;
- preservation of versioned bridge files as historical audit artifacts; and
- normal bridge protocol for every mutating cleanup task.

This revision does not request production deployment, credential changes,
destructive repository history edits, or an owner waiver.

## Requirement Sufficiency

Existing requirements sufficient. The owner decision in `DELIB-20263438`, the
dispatch/envelope specifications, the TAFE dispatch requirements, and the
standing no-index owner direction provide enough authority to implement the
cleanup. The implementation may need to revise or retire formal artifacts whose
current text still declares `bridge/INDEX.md` authoritative, but those
mutations are cleanup deliverables under the already approved direction and
must use their required approval packets before becoming canonical.

## Project And PAUTH Correction

The previous revised proposal versions correctly identified TAFE as a related
subsystem, but their machine-readable `Project:` field was incompatible with
the cited project authorization. This revision sets:

- `Project Authorization:
  PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI`
- `Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH`
- `Work Item: WI-4578`

TAFE remains in scope as related implementation substrate and verification
surface. It is not the project named by this PAUTH.

## Implementation Plan

1. **Bootstrap no-index governance gates.** Update applicability preflight,
   clause preflight, bridge compliance gates, implementation authorization, and
   bridge proposal/revision/report helpers so versioned bridge files can be
   discovered and reviewed without any index entry.

2. **Remove active index authority clauses.** Revise, retire, or supersede
   active governance/configuration clauses such as
   `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` that still
   describe `bridge/INDEX.md` as live authority.

3. **Make dispatcher/TAFE queue state complete.** Ensure new versioned bridge
   files become pending flow/stage work without `bridge/INDEX.md`. Dispatch
   status and health must report queue/actionability, selected targets, last
   launch, exit code, stale state, and reset guidance.

4. **Harden LO review delivery.** Fix or contain the observed Ollama
   max-turn/no-output behavior, OpenRouter timeout/no-output behavior, and
   Antigravity metadata/evidence quality issues before relying on cheap LO
   review as the only verification gate for this cleanup family.

5. **Rewrite active agent guidance.** Update active startup, rules, skills,
   system maps, and dashboard/status guidance to state that `bridge/INDEX.md`
   must not exist and that dispatcher/TAFE-backed bridge state plus versioned
   bridge files are the live surfaces.

6. **Remove runtime index paths.** Retire or replace index parsers, writers,
   serializers, repair scripts, CLI groups, MCP surfaces, doctor checks, TAFE
   preview/generator references, and helper paths whose sole purpose is reading
   or writing `bridge/INDEX.md`.

7. **Update templates and fixtures.** Stop scaffolding `bridge/INDEX.md`, update
   golden fixtures, and keep old-format fixtures only when explicitly labeled
   historical import/audit inputs.

8. **Retire obsolete backlog work.** Retire or supersede `WI-4508`, reframe or
   retire `WI-4577`, and replace the TAFE Phase 6 compatibility-view language
   with no-compatibility cleanup/cutover language.

9. **Preserve historical audit.** Keep prior versioned `bridge/*.md` audit
   files. Do not rewrite old bridge history while removing active runtime
   dependencies.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Search and rewrite active bridge text without exposing credential-bearing files. | Credential scan and changed-file review. | |
| CQ-PATHS-001 | Yes | Keep cleanup inside `E:\GT-KB` and the target paths above. | Root-boundary review. | |
| CQ-COMPLEXITY-001 | Yes | Remove index-only code paths rather than adding compatibility shims. | Old-symbol search and source review. | |
| CQ-CONSTANTS-001 | Yes | Replace index constants with dispatcher/TAFE constants or remove them. | Ruff and targeted tests. | |
| CQ-SECURITY-001 | Yes | Keep production/cloud mutation oversight independent from bridge health. | Prompt/rule review. | |
| CQ-DOCS-001 | Yes | Rewrite active guidance to no-index dispatcher/TAFE operation. | `rg` search with historical-only allowlist. | |
| CQ-TESTS-001 | Yes | Update tests to prove no index creation and no index dependency. | Targeted pytest commands below. | |
| CQ-LOGGING-001 | Yes | Health must report real work-delivery evidence, not only config presence. | Dispatch-health JSON assertions. | |
| CQ-VERIFICATION-001 | Yes | Treat every missing-index failure as a defect until explicitly classified historical. | Search, CLI, and pytest verification. | |

## Spec-Derived Verification Plan

```text
Test-Path bridge/INDEX.md
```

Expected: `False`.

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-index-retirement-cleanout
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-index-retirement-cleanout
```

Expected: pass without `bridge/INDEX.md` and resolve the latest versioned
bridge file from dispatcher/TAFE state or direct versioned-file discovery.

```text
python -m groundtruth_kb bridge dispatch config --json
python -m groundtruth_kb bridge dispatch status --json
python -m groundtruth_kb bridge dispatch health --json
```

Expected: report topology, queue completeness, selected targets, launch/output
evidence, stale state, and reset guidance without reading or recreating
`bridge/INDEX.md`.

```text
python scripts/cross_harness_bridge_trigger.py --diagnose
python scripts/single_harness_bridge_dispatcher.py --diagnose
```

Expected: help text and diagnose output contain no claim that the dispatcher
reads `bridge/INDEX.md`; diagnose distinguishes topology health from actual
work-delivery health.

```text
rg -n "bridge/INDEX[.]md|bridge\\INDEX[.]md|INDEX[.]md|compatibility view|compatibility output|INDEX_FILENAME|index_path" AGENTS.md config/registry config/governance groundtruth-kb/src/groundtruth_kb/project groundtruth-kb/src/groundtruth_kb/session groundtruth-kb/templates platform_tests --glob "!archive/**" --glob "!**/__pycache__/**"
```

Expected: no active references except historical/audit/import fixtures that are
explicitly labeled historical and cannot be used as live authority.

```text
python -m pytest platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py -q --tb=short
python -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_startup_index.py platform_tests/hooks/test_workstream_focus.py -q --tb=short
python -m pytest groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_project_artifacts.py groundtruth-kb/tests/test_doctor.py groundtruth-kb/tests/test_cli_bridge_index.py groundtruth-kb/tests/test_bridge_status_driver.py -q --tb=short
python -m pytest groundtruth-kb/tests/test_doctor.py groundtruth-kb/tests/test_scaffold_smoke.py platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py -q --tb=short
python -m ruff check groundtruth-kb/src scripts platform_tests
python -m ruff format --check groundtruth-kb/src scripts platform_tests
```

Expected: all updated tests pass; tests that retain old index expectations are
removed, reframed as historical import tests, or fail the cleanup.

## Risk / Rollback

The largest risk is that mandatory governance gates still embed the old bridge
index. That is the first implementation slice, because future bridge work must
not depend on the retired file.

The second risk is weak automated LO review. This revision carries forward the
need to harden cheap LO delivery or use a separately reviewed temporary
topology before relying on it.

Rollback must not recreate `bridge/INDEX.md`. If a slice fails, revert the
specific source/config/doc/test changes or pause dispatch; do not restore the
retired index or compatibility generator.
