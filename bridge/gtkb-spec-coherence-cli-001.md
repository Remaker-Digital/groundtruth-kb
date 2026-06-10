NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-29-prime-builder-spec-coherence-cli-implementation
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; interactive Prime Builder session

# Implementation Proposal - Deterministic CLI: gt validate spec-coherence (WI-3424, Layer A)

bridge_kind: prime_proposal
Document: gtkb-spec-coherence-cli
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-29 UTC
Builds on: `bridge/gtkb-spec-coherence-cli-scoping-002.md` (GO; scoping approval)

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-LAYER-A-HYGIENE-COHERENCE
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3424

target_paths: ["config/governance/spec-coherence-rules.toml", "groundtruth-kb/src/groundtruth_kb/coherence/__init__.py", "groundtruth-kb/src/groundtruth_kb/coherence/checker.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_spec_coherence_cli.py"]

Recommended commit type: feat

## Implementation Claim

Implement Layer A of `gt validate spec-coherence` per the GO'd scoping proposal at `bridge/gtkb-spec-coherence-cli-scoping-002.md`. The implementation is a read-only deterministic CLI that scans `current_specifications` from `groundtruth.db` for three classes of cross-spec contradictions:

1. **Surface-overlap** - pairs of specs constraining the same surface with opposite-polarity must/must-not language.
2. **Authority-hierarchy** - child DCL/SPEC/PB behavior contradicts parent GOV/ADR constraint.
3. **Status-drift** - child whose parent was amended after child's verification timestamp.

The CLI emits structured findings JSON plus a markdown rollup under `.gtkb-state/spec-coherence/<run-id>/`. Layer B (AI-augmented semantic review) remains out of scope for this slice.

## In-Root Placement Evidence

All target paths are under `E:\GT-KB`:

- `E:\GT-KB\config\governance\spec-coherence-rules.toml`
- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\coherence\__init__.py`
- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\coherence\checker.py`
- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\cli.py`
- `E:\GT-KB\platform_tests\scripts\test_spec_coherence_cli.py`

No `applications/` path; no out-of-root dependency.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the coherence CLI and rule registry are governed artifacts.
- `GOV-08` - MemBase is the canonical specification store; coherence checking is a consequence of that authority.
- `GOV-SESSION-SELF-INITIALIZATION-001` - one of the two motivating specs from S364 (will appear as a known contradiction fixture in tests).
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - the other motivating spec from S364.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant cross-cutting specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps acceptance to verification commands.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, Work Item, and Project Authorization metadata present in header.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation target paths within `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - CLI module + TOML registry are durable artifacts.
- `GOV-ARTIFACT-APPROVAL-001` - the coherence-rule TOML follows formal-artifact-approval-packet flow at write time per the standard config-file gate.
- `GOV-STANDING-BACKLOG-001` - WI-3424 is on the standing backlog under `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - PAUTH `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-LAYER-A-HYGIENE-COHERENCE` is active.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner directive that repetitive AI plumbing belongs in deterministic services; coherence audit is the kind of work this principle targets.
- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - owner authorization for the deterministic-services project batch.
- `DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI` - precedent deterministic CLI design pattern.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner decision that deterministic plumbing belongs in services.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - DB-backed backlog and fresh discovery expectations.
- `DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI` - deterministic CLI/template pattern precedent.
- `DELIB-2496` - Artifact Recorder CLI GO; adjacent deterministic-service precedent.
- `DELIB-2471`, `DELIB-2470`, `DELIB-2469` - Discoverability CLI NO-GO/GO history; relevant precedent for deterministic CLI review cycles.
- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - owner authorization for the deterministic-services project batch.
- `bridge/gtkb-spec-coherence-cli-scoping-001.md` - the scoping proposal.
- `bridge/gtkb-spec-coherence-cli-scoping-002.md` - Codex GO on scoping; this implementation proposal carries forward that approved design.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved `PROJECT-GTKB-DETERMINISTIC-SERVICES-001` project authorization including WI-3424.
- 2026-05-28 UTC, S364: owner stated the systemic-weakness finding that motivated the scoping (recorded in scoping proposal `-001`).
- 2026-05-28 UTC: Codex GO on scoping at `-002`, approving the Layer A design direction.

No new owner AskUserQuestion is required for this implementation. The PAUTH `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-LAYER-A-HYGIENE-COHERENCE` is active and covers this implementation scope. The scoping GO at `-002` approved the architecture; this implementation proposal requests Codex GO on the concrete implementation contract.

The TOML rule registry creation may trigger the formal-artifact-approval-packet gate at write time (if `config/governance/*.toml` is in the protected-artifact list). If gated, implementation will create the corresponding packet at write time per `GOV-ARTIFACT-APPROVAL-001`.

## Requirement Sufficiency

Existing requirements sufficient. The scoping proposal `-001` and its GO at `-002` define the Layer A scope, the three rule classes, the CLI contract, the TOML schema illustrative shape, the output destination, and the test coverage expectations. No new product requirement is introduced by this implementation slice; it implements the approved design.

## Proposed Scope

### IP-1: Coherence-rule TOML registry

Location: `config/governance/spec-coherence-rules.toml`

Schema (matching scoping proposal §"Component 1"):

```toml
[[rules]]
id = "surface-overlap-opposite-polarity"
class = "surface_overlap"
description = "..."
surface_tags = [...]
polarity_pairs = [{positive = "...", negative = "..."}, ...]
classification = "contradiction_candidate"
remediation_hint = "..."

[[rules]]
id = "authority-hierarchy-invariant"
class = "hierarchy_violation"
description = "..."
parent_types = ["governance", "architecture_decision"]
child_types = ["design_constraint", "specification", "protected_behavior"]
classification = "hierarchy_violation_candidate"
remediation_hint = "..."

[[rules]]
id = "status-drift"
class = "status_drift"
description = "..."
classification = "verification_staleness"
remediation_hint = "..."
```

Initial rule set includes one surface-overlap rule keyed to `cached_startup_snapshot_authority` to detect the motivating S364 contradiction (`DCL-SESSION-STARTUP-TOKEN-BUDGET-001` vs `GOV-SESSION-SELF-INITIALIZATION-001`).

### IP-2: Coherence checker module

Locations:

- `groundtruth-kb/src/groundtruth_kb/coherence/__init__.py` - package init.
- `groundtruth-kb/src/groundtruth_kb/coherence/checker.py` - the checker.

Public API:

- `load_rules(toml_path: Path) -> list[Rule]` - read-only TOML load with schema validation.
- `check_surface_overlap(specs: list[dict], rules: list[Rule]) -> list[Finding]`
- `check_authority_hierarchy(specs: list[dict], rules: list[Rule]) -> list[Finding]`
- `check_status_drift(specs: list[dict], rules: list[Rule]) -> list[Finding]`
- `run_all(specs: list[dict], rules: list[Rule]) -> list[Finding]` - orchestrates the three.

`Finding` dataclass fields: `rule_id`, `spec_a`, `spec_b`, `surface`, `evidence_excerpts`, `classification`, `remediation_hint`.

Read-only against MemBase; no write side effects.

### IP-3: CLI surface extension

Location: `groundtruth-kb/src/groundtruth_kb/cli.py`

Add a `validate` subcommand group containing `spec-coherence`:

```
gt validate spec-coherence [--rule-set NAME] [--output PATH] [--format json|md|both] [--fail-on-findings] [--db-path PATH]
```

Behavior:

1. Load named rule set (default: all rules in registry).
2. Query `current_specifications` view from `groundtruth.db` (read-only).
3. Run `run_all(specs, rules)`.
4. Emit findings to `.gtkb-state/spec-coherence/<run-id>/`:
   - `findings.json` - structured inventory per `Finding` dataclass shape.
   - `summary.md` - human-readable rollup grouped by rule class.
5. Default exit 0 (report-only); exit 5 when `--fail-on-findings` and findings exist.

### IP-4: Platform tests

Location: `platform_tests/scripts/test_spec_coherence_cli.py`

Coverage:

1. Rule-set loading from TOML (valid + malformed -> raises).
2. Surface-overlap rule produces the known DCL-SESSION-STARTUP-TOKEN-BUDGET-001 vs GOV-SESSION-SELF-INITIALIZATION-001 contradiction as a regression fixture.
3. Authority-hierarchy rule correctness against synthetic parent/child pairs.
4. Status-drift rule against synthetic verification timestamps.
5. JSON output schema matches the `Finding` dataclass shape.
6. Markdown summary section headings present.
7. `--fail-on-findings` exit-code behavior.
8. CLI runs read-only (no MemBase mutation observed in fixture DB).

Tests use a temporary SQLite DB with the `current_specifications` view shape, not the live `groundtruth.db`.

## Explicitly Out of Scope

- Layer B AI-augmented semantic review skill.
- Remediation child-bridge filing by the CLI itself.
- Modification of any existing spec rows in MemBase.
- Promotion of any spec status.
- Bulk standing-backlog operation (this is one work item).
- Auto-registration with the dashboard or release-gate.

## Specification-Derived Verification Plan

| Behavior / spec obligation | Verification |
|---|---|
| TOML loads valid rule set | `python -m pytest platform_tests/scripts/test_spec_coherence_cli.py -q --tb=short` |
| TOML rejects malformed registry | same |
| Surface-overlap detects DCL/GOV motivating fixture | same |
| Authority-hierarchy correctness on synthetic pairs | same |
| Status-drift correctness on synthetic timestamps | same |
| JSON output schema | same |
| Markdown summary headings | same |
| `--fail-on-findings` exit semantics | same |
| CLI is read-only against MemBase | same (fixture-based read check) |
| Lint + format clean | `python -m ruff check <target_paths>` + `python -m ruff format --check ...` |

## Acceptance Criteria

1. `config/governance/spec-coherence-rules.toml` exists with at least one rule of each class (surface-overlap, authority-hierarchy, status-drift).
2. `groundtruth-kb/src/groundtruth_kb/coherence/{__init__.py, checker.py}` exist with the public API listed in IP-2.
3. `gt validate spec-coherence` command is registered in the CLI and invocable.
4. `platform_tests/scripts/test_spec_coherence_cli.py` covers all 8 behaviors in IP-4.
5. CLI emits `.gtkb-state/spec-coherence/<run-id>/{findings.json, summary.md}`.
6. Surface-overlap rule produces the DCL-SESSION-STARTUP-TOKEN-BUDGET-001 vs GOV-SESSION-SELF-INITIALIZATION-001 contradiction as a regression fixture.
7. Default exit is 0; `--fail-on-findings` exits 5 when findings present.
8. CLI performs no `groundtruth.db` mutation.
9. ruff lint and format pass on changed files.
10. Applicability and clause preflights pass before and after filing.
11. (Pending Codex) GO on this NEW at `-002`.

## Risk And Rollback

Risk: surface-overlap regex pairs may produce false positives on prose mentions that aren't actual constraints. Mitigation: regex matches are evidence excerpts, not authoritative classifications; output uses `classification = "contradiction_candidate"` (non-final); owner review remains the final disposition channel.

Risk: authority-hierarchy rule may over-flag derived child specs that legitimately narrow parent scope. Mitigation: hierarchy rule classifies as `hierarchy_violation_candidate` (not final); rule registry can be tuned with parent/child type filters; Layer B (future) provides semantic review.

Risk: TOML registry creation may be gated by formal-artifact-approval-packet flow. Mitigation: if `config/governance/*.toml` is in the protected-artifact list, implementation creates the packet at write time per `GOV-ARTIFACT-APPROVAL-001`; the proposal target_paths includes the TOML so the packet path can be added to target_paths in REVISED if needed.

Risk: CLI subcommand registration may conflict with existing `gt validate` subcommands. Mitigation: implementation will check current CLI command tree and integrate cleanly; if a name conflict exists, implementation reports it as a NO-GO-worthy defect for owner-directed resolution.

Rollback: delete all five files in target_paths; restore `cli.py` to its pre-implementation state via git. No MemBase or formal-artifact-approval mutation persists.

## Clause Scope Clarification (Not a Bulk Operation)

This is not a bulk operation. It is one implementation proposal for one work item (WI-3424) in one project (`PROJECT-GTKB-DETERMINISTIC-SERVICES-001`). Inventory: TOML registry, coherence package (init + checker), CLI extension, platform-test module, implementation report, and verification evidence. No bulk standing-backlog mutation, batch spec promotion, batch retirement, or multi-item MemBase write is proposed.

Evidence tokens for clause / preflight visibility: inventory, work_item, implementation proposal, specification, ADR, DCL, GOV, verified, lifecycle, deliberation, MemBase.

## Pre-Filing Preflight Subsection

To be executed before submission for review:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-spec-coherence-cli`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-spec-coherence-cli`

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight exit 0.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
