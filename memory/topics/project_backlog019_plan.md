---
name: BACKLOG-019 Platform SOT Consolidation
description: Consolidate fragmented Source of Truth (SOT) registries into a hierarchical umbrella Artifact Registry.
type: project
---

# BACKLOG-019: Platform SOT Consolidation

Approved via research in S389 (2026-06-04). This project implements the Platform-Wide Artifact Registry to eliminate fragmentation across the 9+ partial registries.

## Phase 1: Core Registry Specification & Schema
- [ ] Define **GTKB-SOT-REGISTRY-001** schema (TOML-backed, mirroring `harness-registry.json`).
- [ ] List all baseline SoT classes: harness, directive, application, project, spec, ADR, DCL, deliberation.
- [ ] Implement registry validation script (`scripts/validate_sot_registry.py`).

## Phase 2: KnowledgeDB Integration
- [ ] Migrate static TOML-registries into KnowledgeDB-backed views.
- [ ] Implement the SOT Registry projection (hot-path flat files for startup).
- [ ] Implement SOT health checks in `gt platform doctor`.

## Phase 3: Transition & Cleanup
- [ ] Umbrella in-flight `PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION`.
- [ ] Deprecate fragmented legacy registries (`applications/registry.toml`, etc.).
- [ ] Final project audit and verification.

## Phase 4: Observability & Hygiene
- [ ] Implement the `bridge_kind` taxonomy stabilization (LO-20260604).
- [ ] Suppress/aggregate repetitive KnowledgeDB migration logs (LO-20260603).
