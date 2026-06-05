---
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 52868963-6210-4aa4-8add-d5b3751a3544
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, interactive session
---

# GOV-PLATFORM-SOT-REGISTRY-001 — Platform-wide SoT Artifact Registry

Every SoT (source-of-truth) class in the GroundTruth-KB platform MUST be registered in the platform artifact registry. Un-registered SoT is a defect.

**Scope:** applies to all SoT classes including but not limited to MemBase tables (specs/work-items/tests/procedures/Deliberation Archive/projects/PAUTHs), narrative authority files (CLAUDE.md, AGENTS.md, .claude/rules/*.md), bridge protocol state (bridge/INDEX.md, bridge/*.md), harness state (harness-state/*.json), config/registry surfaces, control surfaces (config/agent-control/*), governance policy registries (config/governance/*.toml), runtime state surfaces (.gtkb-state/*, .claude/session/*).

**Authority chain:** this GOV extends GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (cross-cutting SoT freshness) which extends GOV-08 (KB is truth). The registry is the canonical inventory; MemBase is the canonical store.

**Mechanism** (per DCL-SOT-REGISTRY-PROJECTION-PARITY-001 + DCL-SOT-REGISTRY-RECORD-SCHEMA-001): hybrid TOML edit-surface at `config/registry/sot-artifacts.toml` + MemBase `sot_artifacts` projection table. Doctor check `_check_sot_registry_completeness` asserts (a) TOML/MemBase parity and (b) registry-to-disk reality alignment.

**Initial severity** for the doctor check is WARN per owner decision Q6 of DELIB-20260671. Promotion to ERROR (release-blocking) is a separate downstream owner decision tracked as a follow-on work item.

**Bootstrap:** registry row 1 IS the registry itself (config/registry/sot-artifacts.toml).

## Acceptance Summary

- `config/registry/sot-artifacts.toml` exists and loads without `InvalidSoTRecord`.
- MemBase `sot_artifacts` table exists and is queryable via `groundtruth_kb.project.sot_registry`.
- `gt registry list` returns the bootstrap inventory (22+ entries).
- `_check_sot_registry_completeness` runs at SessionStart and reports drift accurately.
- Doctor severity is WARN; promotion to ERROR via downstream owner decision.

## Source Authority

- `DELIB-20260671` — owner 7-AUQ pass authorizing umbrella + Hybrid C structural option + `config/registry/` location + WARN severity.
- `DELIB-20260672` — peer's 16-AUQ pass (adopted) authorizing the parent extension of GOV-SOURCE-OF-TRUTH-FRESHNESS-001.
- `bridge/gtkb-platform-sot-consolidation-umbrella-008.md` — umbrella GO authorizing this slice.
- `bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-005.md` — Slice 1 GO authorizing this spec insert.

## Parents

- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (cross-cutting SoT freshness; this GOV is its platform-wide extension).
- GOV-08 (KB is truth; foundational).
