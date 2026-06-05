---
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 52868963-6210-4aa4-8add-d5b3751a3544
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, interactive session
---

# DCL-SOT-REGISTRY-RECORD-SCHEMA-001 — SoT Registry Per-Record Schema

## Constraint Statement

Every record in `config/registry/sot-artifacts.toml` MUST conform to the per-record schema defined below. The loader (`groundtruth_kb.project.sot_registry`) rejects non-conforming records with `InvalidSoTRecord`.

## Description

Every record in `config/registry/sot-artifacts.toml` MUST conform to the following schema. The loader (`groundtruth_kb.project.sot_registry`) rejects non-conforming records with `InvalidSoTRecord`.

## Required Fields (All Records)

- `id`: string, unique. Format: lowercase-kebab-case.
- `domain`: string, enum. One of: `specifications`, `narrative_authority`, `bridge_protocol`, `harness_state`, `control_surface`, `governance_policy`, `runtime_state`, `scaffold_lifecycle`, `operational_notepad`, `retired`.
- `lifecycle`: string, enum. One of: `active`, `deprecated`, `archive`, `generated`.
- `storage_path`: string. Path relative to project root, OR MemBase table name prefixed with `membase:` (e.g., `membase:specifications`).
- `authority_spec_id`: string. The GOV/DCL/ADR/PB spec that grants this artifact its SoT status.
- `mutation_api`: string. The CLI command, Python API, or rule citation describing the canonical mutation surface.
- `versioning_policy`: string, enum. One of: `append_only_versioned`, `overwrite_single_writer`, `regenerated_from_source`, `git_tracked`, `immutable_archive`.
- `backup_policy`: string, enum. One of: `git_tracked`, `membase_export`, `regenerable_from_source`, `gitignored_runtime`, `external_backup`.
- `health_check_function`: string OR null. The doctor check function name (e.g., `_check_role_set_topology_consistency`) OR null if no automated health check exists yet.
- `owner_role`: string, enum. One of: `prime_builder`, `loyal_opposition`, `owner_only`, `shared`, `automated_only`.

## Optional Fields

- `depends_on`: string list. Other SoT registry IDs this artifact depends on at runtime.
- `forbidden_substitutes`: string list. Paths or artifact IDs that MUST NOT be substituted for this SoT when answering current-state queries. Populated by Slice 2A read-discipline work; defaults to empty list.
- `notes`: string. Free-form prose for context.

## Lifecycle Invariants

- `lifecycle=archive` records: loader does NOT load these for active use; they remain in registry for provenance only.
- `lifecycle=deprecated` records: loader loads with deprecation warning; readers MUST emit warning when querying.
- `lifecycle=generated` records: `storage_path` MUST have a corresponding generator pointer in `mutation_api` field.

## Schema Extension Process

(DCL-CONCEPT-ON-CONTACT-001 mirror)

- Adding optional fields: bridge proposal + formal-artifact-approval packet for a new version of DCL-SOT-REGISTRY-RECORD-SCHEMA-001.
- Adding required fields: same + migration plan for existing records.
- Removing fields: same + supersession evidence.
- Adding enum values: same + per-value rationale.

## Acceptance Summary

- `groundtruth_kb.project.sot_registry` loader rejects non-conforming records with `InvalidSoTRecord`.
- All 22+ bootstrap records in `config/registry/sot-artifacts.toml` conform.
- Schema test in `groundtruth-kb/tests/test_sot_registry.py` validates field types, enum membership, and invariants for every record.

## Source Authority

- `DELIB-20260671` Q2 (Hybrid choice; record schema is part of the mechanism).
- `DELIB-20260672` AUQ#5 + AUQ#11 (registry schema definition).
- `bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-005.md` — Slice 1 GO authorizing this DCL.

## Parent

GOV-PLATFORM-SOT-REGISTRY-001.

## Schema Reference Implementation

The Python loader exposes:

- `class SoTArtifact` (dataclass with all required + optional fields).
- `class InvalidSoTRecord(ValueError)`.
- `class UnknownDomain(ValueError)`.

The TOML file structure is one `[[artifacts]]` table per record.
