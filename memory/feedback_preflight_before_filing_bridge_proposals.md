---
name: Run preflight before filing bridge proposals
description: Before writing any bridge proposal, run scripts/bridge_applicability_preflight.py against the intended bridge-id; if INDEX entry doesn't exist yet, manually check the spec-applicability.toml regex matrix against the draft text. Voluntary compliance has failed twice in S331 (umbrella -002 NO-GO + waiver -002 NO-GO, both for missing cross-cutting spec citations).
type: feedback
---

Before drafting a bridge proposal: read `config/governance/spec-applicability.toml` and KB-search for cross-cutting governance specs governing the *artifact type itself* (not just the topic). Cite every triggered required + advisory spec in the Specification Links section. Run `python scripts/bridge_applicability_preflight.py --bridge-id <intended-id>` to verify.

**Why:** S331 incident chain — two consecutive Codex NO-GOs on the same class of defect:
1. `bridge/gtkb-isolation-018-agent-red-file-migration-002.md` F1: missed `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`. The proposal cited topic-specific GOVs/DCLs (about Agent Red migration) but missed the cross-cutting GOVs/DCLs that govern bridge proposals as an artifact type.
2. `bridge/gtkb-isolation-018-pending-migration-waiver-002.md` F1: missed `GOV-ARTIFACT-APPROVAL-001` (the formal-artifact-approval gate that governs DELIB inserts as an artifact-type mutation). The test plan referenced it; the Specification Links section didn't.

Root cause: deliberation search was scoped to the *topic* of the proposal, not to the *artifact type* the proposal would create. The cross-cutting governance specs are a different axis from the topic governance specs.

**How to apply:** Two axes of governance to search before drafting any bridge proposal:
- **Topic axis** — already-mandated by `deliberation-protocol.md`; KB-search for prior reviews on the spec/WI/component the proposal addresses.
- **Artifact-type axis** — read `config/governance/spec-applicability.toml`; for each trigger that fires on the draft (path, content match, doc match), cite the listed spec.

If filing a bridge proposal that creates/modifies a formal artifact (DELIB, GOV, SPEC, ADR, DCL, PB), additionally cite `GOV-ARTIFACT-APPROVAL-001` v2 (the formal-artifact-approval gate). This is not currently in `spec-applicability.toml` as a trigger but is required by Codex review per the artifact-approval principle.

After drafting and before filing: run `python scripts/bridge_applicability_preflight.py --bridge-id <intended-id>`. If INDEX entry doesn't yet exist (catch-22), manually grep the draft text against the spec-applicability.toml content patterns. Then file with INDEX entry; the preflight will run cleanly on first review.

Permanent mechanical fix in flight (S331 owner directive "all three"):
- This memory record (in-session recall; project-tracked at `memory/`)
- Rule update bridge thread (extends `.claude/rules/file-bridge-protocol.md` to mandate pre-filing preflight; survives session boundaries)
- Hook upgrade bridge thread (extends `.claude/hooks/bridge-compliance-gate.py` to actually run the preflight at write-time and hard-block on missing required specs; mechanical enforcement)
