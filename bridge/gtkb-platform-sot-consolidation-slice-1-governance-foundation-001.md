NEW

# Slice 1: Governance Foundation — 3 new specs + registry mechanism + doctor check (covers umbrella's full Slice 1 scope)

bridge_kind: implementation_proposal
Document: gtkb-platform-sot-consolidation-slice-1-governance-foundation
Version: 001
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-04 UTC
Recipient: Loyal Opposition (Codex, harness A)
Parent umbrella: bridge/gtkb-platform-sot-consolidation-umbrella-008.md (GO)
Project: PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-UMBRELLA-SLICE-1-GOVERNANCE-ENVELOPE
Work Item: WI-4349

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 52868963-6210-4aa4-8add-d5b3751a3544
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, interactive session

target_paths:
- groundtruth.db
- .groundtruth/formal-artifact-approvals/2026-06-04-GOV-PLATFORM-SOT-REGISTRY-001.json
- .groundtruth/formal-artifact-approvals/2026-06-04-DCL-SOT-REGISTRY-PROJECTION-PARITY-001.json
- .groundtruth/formal-artifact-approvals/2026-06-04-DCL-SOT-REGISTRY-RECORD-SCHEMA-001.json
- config/registry/sot-artifacts.toml
- groundtruth-kb/src/groundtruth_kb/project/sot_registry.py
- groundtruth-kb/src/groundtruth_kb/cli.py
- groundtruth-kb/src/groundtruth_kb/project/doctor.py
- groundtruth-kb/src/groundtruth_kb/db.py
- groundtruth-kb/tests/test_sot_registry.py
- platform_tests/scripts/test_check_sot_registry_completeness.py

requires_verification: true
implementation_scope: implementation

## Why this proposal

The umbrella `gtkb-platform-sot-consolidation-umbrella` GO at -008 authorizes the 9-slice sequence. This is the first child bridge — Slice 1 governance foundation — covering: 3 new governance specs (1 GOV + 2 DCLs), the registry TOML scaffold + Python loader + MemBase projection table + `gt registry` CLI subcommand, and the `_check_sot_registry_completeness` doctor check at WARN severity.

Primary tracking work item is WI-4349 (assertions); the work also delivers components that future child slices reference. If Codex prefers Slice 1 to be split into smaller proposals (foundation specs / mechanism / doctor), NO-GO with rationale and Prime files them separately; no prejudice.

## Summary

The 3 new specs establish the registry's governance contract:

- **`GOV-PLATFORM-SOT-REGISTRY-001`** — every SoT class MUST be registered; un-registered SoT is a defect (initially WARN; promoted to ERROR via downstream owner decision per umbrella Decision 6).
- **`DCL-SOT-REGISTRY-PROJECTION-PARITY-001`** — TOML edit-surface and MemBase projection must match; drift is assertion-failing.
- **`DCL-SOT-REGISTRY-RECORD-SCHEMA-001`** — per-record schema including optional `forbidden_substitutes` column (populated by Slice 2A).

The mechanism implements them:

- **`config/registry/sot-artifacts.toml`** — TOML human-edit surface scaffolded with all 22 SoT classes from the umbrella research file (`memory/research_sot_consolidation_2026_06_04.md` §2).
- **`groundtruth_kb.project.sot_registry`** — Python loader analogous to `groundtruth_kb.project.managed_registry`, with dataclasses for `SoTArtifact`, validation exceptions (`InvalidSoTRecord`, `UnknownDomain`), and projection helpers.
- **MemBase `sot_artifacts` table** — append-only versioned canonical projection; mirror of `harness-state/harness-registry.json` ↔ MemBase pattern.
- **`gt registry` CLI subcommand** — list, show, validate, sync (TOML → MemBase projection regeneration), diff.

The doctor enforces:

- **`_check_sot_registry_completeness`** — runs at SessionStart; reports any SoT class detected on disk but absent from the registry; reports any registry entry whose `storage_path` doesn't resolve. Severity WARN initially; owner decision promotes to ERROR.

## Specification Links

| Spec | Severity | Trigger | How this proposal complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via bridge/INDEX.md as NEW versioned bridge file. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section exists with comprehensive citation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification, spec-to-test | See §Specification-Derived Verification Plan; spec-to-test mapping for all 3 new specs. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | path:groundtruth-kb/src/groundtruth_kb/project/** | All Python source mutations stay within `groundtruth-kb/src/groundtruth_kb/project/` and `groundtruth-kb/src/groundtruth_kb/cli.py`; all config additions stay under `config/registry/`; no out-of-root paths. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | blocking | content:source of truth, cited paths | New `GOV-PLATFORM-SOT-REGISTRY-001` extends this as parent authority. |
| `GOV-08` (KB is truth) | blocking | foundational | Registry inventory resolves against MemBase as canonical. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:ADR/DCL/GOV/spec inserts | 3 formal-artifact-approval packets target paths listed; per-packet owner approval required before MemBase insert. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH, path:project authorization | Umbrella PAUTH `PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-UMBRELLA-SLICE-1-GOVERNANCE-ENVELOPE` cited; covers Slice 1 mutation classes (governance_artifact_insert, source_addition, config_addition, test_addition, cli_extension). |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH cites `DELIB-20260671` as owner-decision; this proposal stays within Slice 1 scope. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 framing specs; this proposal cites them + the 3 new specs being created. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items inserts | Primary tracking WI declared; project membership preserved. |
| `GOV-12` (WI triggers tests) | blocking | path:work_items, test creation | 2 new test files included in target_paths; each new spec gets at least one assertion. |
| `GOV-09` (owner input classification) | blocking | content:owner directive | Owner directive `DELIB-20260671` already classified as specification-language; this proposal IS the spec-first response. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, ADR, DCL, work item, owner decision | 3 new specs + concrete implementation plan + verification plan — fully artifact-routed. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | Slice 1 establishes the artifact-registry pattern for cross-domain SoT inventory. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:verified, retired | Slice 1 establishes the 4 lifecycle states (active/deprecated/archive/generated) per `SESSION-STARTUP-CONTROL-MAP.md` precedent. |
| `DCL-CONCEPT-ON-CONTACT-001` | advisory | content:new concepts | "sot_artifacts table", "registry projection parity", "registry record schema", "forbidden_substitutes column" — new concepts; glossary updates included in implementation plan. |
| `.claude/rules/project-root-boundary.md` | blocking | path:groundtruth-kb/**, path:config/**, content:E:\GT-KB | All target_paths are within `E:\GT-KB`; no out-of-root paths cited. |

## Requirement Sufficiency

**Existing requirements sufficient.** Umbrella owner-decision evidence (`DELIB-20260671` 7-AUQ + `DELIB-20260672` 16-AUQ adopted + `DELIB-20260673` parallel-session evidence + `DELIB-20260670` triage survey + `DELIB-20260868` work-item disposition AUQ + `DELIB-20260869` work-item text alignment AUQ) resolves all material requirement-disambiguation questions for Slice 1.

## Prior Deliberations

- `bridge/gtkb-platform-sot-consolidation-umbrella-001..008` — umbrella thread; GO at -008.
- `DELIB-20260671` — owner 7-AUQ for the platform SoT consolidation umbrella.
- `DELIB-20260672` — peer's 16-AUQ adopted via S408 reconciliation.
- `DELIB-20260673` — parallel-session fragmentation evidence.
- `DELIB-20260670` — manual-triage survey identifying 8 forbidden-substitute candidates (Slice 2A scope foundation).
- `DELIB-20260868` — owner AUQ resolving work-item disposition.
- `DELIB-20260869` — owner AUQ aligning work-item text with umbrella schema decision.
- `memory/research_sot_consolidation_2026_06_04.md` — research file with 22 SoT classes (§2) used for the registry's initial population.
- `bridge/gtkb-managed-artifact-registry-008.md` — precedent registry pattern (managed-artifacts.toml + Python loader + doctor check).
- `bridge/gtkb-startup-refractor-slice-a-startup-control-inventory-002.md` — precedent inventory pattern (SESSION-STARTUP-CONTROL-MAP.md with 4 lifecycle states).
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-008.md` — precedent TOML↔MemBase projection pattern (harness-registry.json).

No previously rejected approach is being revisited.

## Owner Decisions / Input

The 7+16+2+2 owner decisions captured in the umbrella thread fully authorize Slice 1 scope. No new AUQ required for THIS proposal; per-spec formal-artifact-approval packets require owner per-packet approval at packet-generation time per `GOV-ARTIFACT-APPROVAL-001`.

Authority cross-reference:

| Umbrella decision | How it shapes Slice 1 |
|---|---|
| Q1 (Umbrella) | This proposal files as a child of the umbrella |
| Q2 (Hybrid C: TOML + MemBase projection) | Mechanism is TOML at `config/registry/sot-artifacts.toml` + MemBase projection |
| Q3 (`config/registry/`) | TOML lives at `config/registry/sot-artifacts.toml` |
| Q6 (WARN severity) | `_check_sot_registry_completeness` ships at WARN; ERROR promotion is a downstream owner decision |
| Peer's AUQ#5 (Hybrid TOML+MemBase) | Confirms Hybrid choice |
| Peer's AUQ#11 (Extend GOV-SOURCE-OF-TRUTH-FRESHNESS-001) | `GOV-PLATFORM-SOT-REGISTRY-001` cites it as parent |

## Proposed Specifications (inline drafts)

### Spec 1 of 3 — GOV-PLATFORM-SOT-REGISTRY-001

```yaml
id: GOV-PLATFORM-SOT-REGISTRY-001
type: governance
title: Platform-wide SoT Artifact Registry
status: specified
priority: P1
parents: [GOV-SOURCE-OF-TRUTH-FRESHNESS-001, GOV-08]
description: |
  Every SoT (source-of-truth) class in the GroundTruth-KB platform MUST be
  registered in the platform artifact registry. Un-registered SoT is a defect.

  Scope: applies to all SoT classes including but not limited to MemBase
  tables (specs/work-items/tests/procedures/DA/projects/PAUTHs), narrative
  authority files (CLAUDE.md, AGENTS.md, .claude/rules/*.md), bridge
  protocol state (bridge/INDEX.md, bridge/*.md), harness state
  (harness-state/*.json), config/registry surfaces, control surfaces
  (config/agent-control/*), governance policy registries
  (config/governance/*.toml), runtime state surfaces (.gtkb-state/*,
  .claude/session/*).

  Authority chain: this GOV extends GOV-SOURCE-OF-TRUTH-FRESHNESS-001
  (cross-cutting SoT freshness) which extends GOV-08 (KB is truth). The
  registry is the canonical inventory; MemBase is the canonical store.

  Mechanism (per DCL-SOT-REGISTRY-PROJECTION-PARITY-001 +
  DCL-SOT-REGISTRY-RECORD-SCHEMA-001): hybrid TOML edit-surface at
  config/registry/sot-artifacts.toml + MemBase sot_artifacts projection
  table. Doctor check _check_sot_registry_completeness asserts
  (a) TOML/MemBase parity and (b) registry-to-disk reality alignment.

  Initial severity for the doctor check is WARN per owner decision Q6 of
  DELIB-20260671. Promotion to ERROR (release-blocking) is a separate
  downstream owner decision.

  Bootstrap: registry row 1 IS the registry itself
  (config/registry/sot-artifacts.toml).
acceptance_summary: |
  - config/registry/sot-artifacts.toml exists and loads without InvalidSoTRecord
  - MemBase sot_artifacts table exists and is queryable via
    groundtruth_kb.project.sot_registry
  - gt registry list returns the bootstrap inventory (22+ entries)
  - _check_sot_registry_completeness runs at SessionStart and reports drift
    accurately
  - Doctor severity is WARN; promotion to ERROR via downstream owner decision
assertions:
  - kind: file_exists
    path: config/registry/sot-artifacts.toml
  - kind: python_loadable
    module: groundtruth_kb.project.sot_registry
  - kind: cli_subcommand_exists
    invocation: python -m groundtruth_kb registry list
changed_by: claude-prime-builder/harness-B/52868963
change_reason: New GOV spec authorizing platform-wide SoT artifact registry per umbrella DELIB-20260671 Q1+Q2+Q3+Q6
```

### Spec 2 of 3 — DCL-SOT-REGISTRY-PROJECTION-PARITY-001

```yaml
id: DCL-SOT-REGISTRY-PROJECTION-PARITY-001
type: design_constraint
title: SoT Registry TOML/MemBase Projection Parity
status: specified
priority: P1
parents: [GOV-PLATFORM-SOT-REGISTRY-001]
description: |
  The TOML edit-surface at config/registry/sot-artifacts.toml and the
  MemBase sot_artifacts projection table MUST match exactly. Drift between
  them is assertion-failing.

  Mutation flow:
    1. Author edits config/registry/sot-artifacts.toml.
    2. Pre-commit hook (or explicit `gt registry sync`) regenerates MemBase
       projection from TOML.
    3. _check_sot_registry_completeness on next SessionStart confirms parity.

  Drift detection mechanism: _check_sot_registry_completeness compares
  TOML records (parsed via groundtruth_kb.project.sot_registry loader)
  against MemBase sot_artifacts rows. Any divergence in declared fields
  is reported as drift.

  Drift severity escalation: initially WARN for backward compatibility
  with records added before parity enforcement. Promotion to ERROR is a
  downstream owner decision per umbrella Decision 6.

  Bootstrap guarantee: the registry's row 1
  (config/registry/sot-artifacts.toml itself) ensures the registry is
  self-described. Removing row 1 from the TOML causes both
  ERROR-severity drift AND a self-consistency failure detectable by the
  loader.
acceptance_summary: |
  - groundtruth_kb.project.sot_registry.load_toml() and load_projection()
    return structurally equivalent records
  - gt registry sync regenerates projection from TOML deterministically
  - _check_sot_registry_completeness reports zero drift after sync
  - Row 1 (self-reference) cannot be removed without parity failure
assertions:
  - kind: python_function_exists
    module: groundtruth_kb.project.sot_registry
    function: validate_projection_parity
  - kind: cli_subcommand_exists
    invocation: python -m groundtruth_kb registry sync
changed_by: claude-prime-builder/harness-B/52868963
change_reason: New DCL constraining TOML/MemBase parity for SoT registry per umbrella DELIB-20260671 Q2
```

### Spec 3 of 3 — DCL-SOT-REGISTRY-RECORD-SCHEMA-001

```yaml
id: DCL-SOT-REGISTRY-RECORD-SCHEMA-001
type: design_constraint
title: SoT Registry Per-Record Schema
status: specified
priority: P1
parents: [GOV-PLATFORM-SOT-REGISTRY-001]
description: |
  Every record in config/registry/sot-artifacts.toml MUST conform to the
  following schema. The loader (groundtruth_kb.project.sot_registry)
  rejects non-conforming records with InvalidSoTRecord.

  Required fields (all records):
    - id: string, unique. Format: lowercase-kebab-case.
    - domain: string, enum. One of: specifications, narrative_authority,
      bridge_protocol, harness_state, control_surface, governance_policy,
      runtime_state, scaffold_lifecycle, operational_notepad, retired.
    - lifecycle: string, enum. One of: active, deprecated, archive,
      generated.
    - storage_path: string. Path relative to project root, OR MemBase
      table name prefixed with "membase:" (e.g., "membase:specifications").
    - authority_spec_id: string. The GOV/DCL/ADR/PB spec that grants this
      artifact its SoT status.
    - mutation_api: string. The CLI command, Python API, or rule citation
      describing the canonical mutation surface.
    - versioning_policy: string, enum. One of: append_only_versioned,
      overwrite_single_writer, regenerated_from_source, git_tracked,
      immutable_archive.
    - backup_policy: string, enum. One of: git_tracked, membase_export,
      regenerable_from_source, gitignored_runtime, external_backup.
    - health_check_function: string OR null. The doctor check function
      name (e.g., "_check_role_set_topology_consistency") OR null if no
      automated health check exists yet.
    - owner_role: string, enum. One of: prime_builder, loyal_opposition,
      owner_only, shared, automated_only.

  Optional fields:
    - depends_on: string list. Other SoT registry IDs this artifact
      depends on at runtime.
    - forbidden_substitutes: string list. Paths or artifact IDs that
      MUST NOT be substituted for this SoT when answering current-state
      queries. Populated by Slice 2A read-discipline work; defaults to
      empty list.
    - notes: string. Free-form prose for context.

  Lifecycle invariants:
    - lifecycle=archive records: loader does NOT load these for active
      use; they remain in registry for provenance only.
    - lifecycle=deprecated records: loader loads with deprecation
      warning; readers MUST emit warning when querying.
    - lifecycle=generated records: storage_path MUST have a corresponding
      generator pointer in mutation_api field.

  Schema extension process (DCL-CONCEPT-ON-CONTACT-001 mirror):
    - Adding optional fields: bridge proposal + formal-artifact-approval
      packet for a new version of DCL-SOT-REGISTRY-RECORD-SCHEMA-001.
    - Adding required fields: same + migration plan for existing records.
    - Removing fields: same + supersession evidence.
    - Adding enum values: same + per-value rationale.
acceptance_summary: |
  - groundtruth_kb.project.sot_registry loader rejects non-conforming
    records with InvalidSoTRecord
  - All 22+ bootstrap records in config/registry/sot-artifacts.toml
    conform
  - Schema test in groundtruth-kb/tests/test_sot_registry.py validates
    field types, enum membership, and invariants for every record
assertions:
  - kind: python_class_exists
    module: groundtruth_kb.project.sot_registry
    class: SoTArtifact
  - kind: python_class_exists
    module: groundtruth_kb.project.sot_registry
    class: InvalidSoTRecord
changed_by: claude-prime-builder/harness-B/52868963
change_reason: New DCL constraining per-record schema for SoT registry per umbrella DELIB-20260671 Q2 + DELIB-20260672 AUQ#5
```

## Implementation Plan

Per-target-path:

1. **3 approval packets** — generated via `python -m groundtruth_kb generate-approval-packet --kind formal --artifact-type spec` for each of the 3 new specs. Owner reviews and approves each packet (per `GOV-ARTIFACT-APPROVAL-001`).

2. **`config/registry/sot-artifacts.toml`** — TOML file with bootstrap inventory drawn from `memory/research_sot_consolidation_2026_06_04.md` §2 (22 SoT classes). Includes self-reference row (registry-itself).

3. **`groundtruth_kb.project.sot_registry`** — new Python module modeled on `groundtruth_kb.project.managed_registry`. Exposes:
    - `class SoTArtifact` (dataclass with all required + optional fields)
    - `class InvalidSoTRecord(ValueError)`
    - `class UnknownDomain(ValueError)`
    - `def load_toml(path: Path) -> list[SoTArtifact]`
    - `def load_projection(db: KnowledgeDB) -> list[SoTArtifact]`
    - `def validate_projection_parity(toml_records, projection_records) -> ParityReport`
    - `def sync_projection(toml_records, db: KnowledgeDB) -> SyncReport`

4. **MemBase `sot_artifacts` table** — added via `groundtruth_kb/db.py` schema extension (append-only versioned per existing table pattern). Columns mirror the SoTArtifact dataclass.

5. **`gt registry` CLI subcommand** — added to `groundtruth_kb/cli.py` analogous to `gt projects` / `gt deliberations`. Subcommands: `list`, `show <id>`, `validate`, `sync`, `diff`.

6. **`_check_sot_registry_completeness` doctor check** — added to `groundtruth_kb/project/doctor.py`. Returns ToolCheck with severity WARN. Two sub-checks:
    - TOML/MemBase parity (load both, compare).
    - Registry/reality (every active record's storage_path resolves; every storage_path that "looks like an SoT class" is registered — heuristic based on path glob patterns).

7. **`groundtruth-kb/tests/test_sot_registry.py`** — pytest tests for loader, schema validation, parity verification.

8. **`platform_tests/scripts/test_check_sot_registry_completeness.py`** — pytest test for the doctor check.

Execution order: 1 (packets) → owner approvals → MemBase spec inserts → 4 (table) → 3 (loader) → 2 (TOML scaffold) → 5 (CLI) → 6 (doctor) → 7+8 (tests). Tests passing is acceptance.

## Specification-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Spec | Test |
|---|---|
| `GOV-PLATFORM-SOT-REGISTRY-001` | `test_sot_registry.py::test_bootstrap_inventory_loads` (loads TOML, asserts >=22 records, asserts row 1 is self-reference); `test_check_sot_registry_completeness.py::test_check_runs_at_warn_severity` |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | `test_sot_registry.py::test_toml_membase_parity_after_sync` (load TOML, sync, reload from MemBase, assert structural equivalence); `test_sot_registry.py::test_drift_detection_reports_divergence` (mutate one field, assert validate_projection_parity reports it) |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | `test_sot_registry.py::test_loader_rejects_invalid_records` (test each invariant: missing required field, invalid enum, lifecycle=generated without mutation_api generator, etc.); `test_sot_registry.py::test_all_bootstrap_records_conform` |

Verification commands LO can run post-implementation:

```text
python -m pytest groundtruth-kb/tests/test_sot_registry.py -v
python -m pytest platform_tests/scripts/test_check_sot_registry_completeness.py -v
python -m groundtruth_kb registry list
python -m groundtruth_kb registry validate
python -m groundtruth_kb project doctor --check _check_sot_registry_completeness
```

## Risk and Rollback

**Risk** is moderate. New module + new MemBase table + new CLI subcommand + new doctor check. Each piece has a precedent (managed_registry pattern). Specific risks:

- **Bootstrap correctness:** the 22 SoT classes in the research file may have inaccurate metadata. Mitigated by per-record validation at loader time; owner can adjust TOML before sync.
- **Doctor false positives:** the registry/reality heuristic may flag legitimate SoT classes as unregistered. Mitigated by WARN severity initially; refine heuristic via downstream work.
- **MemBase schema migration:** adding `sot_artifacts` table requires careful schema version handling. Mitigated by existing append-only pattern (no schema downgrade needed).
- **Drift between TOML and MemBase:** the parity check catches this, but the initial sync must succeed. Mitigated by `gt registry sync` being idempotent and pre-commit-hookable.

**Rollback** is straightforward at the proposal level. If LO NO-GOs, no source changes have been made. If LO GOs and implementation hits a wall, `git revert` reverts the source/test/config additions; MemBase mutations (spec inserts + sot_artifacts table) require explicit retire-spec + table-drop operations (separate bridge if needed).

## Project Root Boundary Compliance

All target_paths are within `E:\GT-KB` per `.claude/rules/project-root-boundary.md`. No path escapes the root. No application-application crossover (all paths are platform-scope, not Agent Red application-scope).

## Pre-Filing Preflight Subsection

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-platform-sot-consolidation-slice-1-governance-foundation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-platform-sot-consolidation-slice-1-governance-foundation
```

Both will be run after INDEX entry insertion; expected to pass cleanly (spec set is complete, target_paths are concrete).

## Recommended Commit Type

`feat`: adds net-new capability (3 new specs, registry mechanism, doctor check). Will be cited in post-impl report.

## Recommended Outcome

**GO** for the Slice 1 governance foundation proposal.

LO is asked to verify:

1. The 3 inline spec drafts are well-formed and ready for formal-artifact-approval-packet generation.
2. Target paths are concrete, in-root, and align with the umbrella PAUTH's allowed mutation classes (governance_artifact_insert, source_addition, config_addition, test_addition, cli_extension).
3. Implementation plan covers all 7 mechanism components (TOML + loader + MemBase table + CLI subcommand + doctor check + 2 test files).
4. Spec-to-test mapping is complete (every new spec has at least one test).
5. Slice 1 as ONE proposal is acceptable; if split is preferred, NO-GO with split recommendation and Prime files smaller proposals separately.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
