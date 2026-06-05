---
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 52868963-6210-4aa4-8add-d5b3751a3544
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, interactive session
---

# DCL-SOT-REGISTRY-PROJECTION-PARITY-001 — SoT Registry TOML/MemBase Projection Parity

## Constraint Statement

The TOML edit-surface at `config/registry/sot-artifacts.toml` and the MemBase `sot_artifacts` projection table MUST match exactly. Drift between them is assertion-failing.

## Description

The TOML edit-surface at `config/registry/sot-artifacts.toml` and the MemBase `sot_artifacts` projection table MUST match exactly. Drift between them is assertion-failing.

## Mutation Flow

1. Author edits `config/registry/sot-artifacts.toml`.
2. Pre-commit hook (or explicit `gt registry sync`) regenerates MemBase projection from TOML.
3. `_check_sot_registry_completeness` on next SessionStart confirms parity.

## Drift Detection Mechanism

`_check_sot_registry_completeness` compares TOML records (parsed via `groundtruth_kb.project.sot_registry` loader) against MemBase `sot_artifacts` rows. Any divergence in declared fields is reported as drift.

## Drift Severity Escalation

Initially WARN for backward compatibility with records added before parity enforcement. Promotion to ERROR is a downstream owner decision per umbrella Decision 6.

## Bootstrap Guarantee

The registry's row 1 (`config/registry/sot-artifacts.toml` itself) ensures the registry is self-described. Removing row 1 from the TOML causes both ERROR-severity drift AND a self-consistency failure detectable by the loader.

## Acceptance Summary

- `groundtruth_kb.project.sot_registry.load_toml()` and `load_projection()` return structurally equivalent records.
- `gt registry sync` regenerates projection from TOML deterministically.
- `_check_sot_registry_completeness` reports zero drift after sync.
- Row 1 (self-reference) cannot be removed without parity failure.

## Source Authority

- `DELIB-20260671` Q2 (Hybrid TOML + MemBase projection).
- `DELIB-20260672` AUQ#5 (same hybrid choice).
- `bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-005.md` — Slice 1 GO authorizing this DCL.

## Parent

GOV-PLATFORM-SOT-REGISTRY-001.
