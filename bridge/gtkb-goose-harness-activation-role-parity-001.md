NEW
author_identity: goose
author_harness_id: G
author_session_context_id: goose-interactive-20260720-goose-activation-pb
author_model: goose-default
author_model_version: goose-desktop-1.43.0
author_model_configuration: Goose Desktop interactive; session-stated role prime-builder via ::init gtkb pb

# Goose Harness Activation & Role Parity

Work Item: (new — fast-track owner directive)
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION (existing)
target_paths: [
  "harness-state/harness-registry.json",
  "harness-state/harness-identities.json",
]

## Summary

Activate Goose harness (identity G) from `retired`/LO-only to `active`/dual-role (prime-builder + loyal-opposition) with dispatch capability enabled. This is a fast-track, minimal-surface owner-directed activation — the Goose Desktop harness is already functioning interactively (this proposal is authored from it) and has a working headless dispatch script (`scripts/goose_harness.py`). The registry is the only blocking artifact: it currently marks Goose as retired, LO-only, non-dispatchable.

## Background

- **Slice 1 ADR** (`bridge/gtkb-goose-harness-adoption-slice1-adr-001` through `-003`) was WITHDRAWN pre-implementation because the framing shifted from GUI-centric (Goose desktop) to model-centric (Alibaba DeepSeek non-GUI). Owner has now returned with explicit direction to activate the Goose Desktop harness itself.
- **Current state**: Goose (G) is `retired`, role `["loyal-opposition"]`, `can_receive_dispatch: false`, `reviewer_precedence: null`, `dispatch_quality: 80.0`, `dispatch_cost: 40.0`.
- **Evidence of viability**: This proposal is authored from an interactive Goose Desktop session with session-stated Prime Builder role. The Goose CLI (`goose.exe` v1.43.0 at `E:\goose-dist-windows\resources\bin\goose.exe`) supports `run`, `session`, and `serve` commands. The `scripts/goose_harness.py` wrapper already supports `bridge-review`, `verification`, and `implementation` skill routing for headless dispatch.
- **What this slice does NOT do**: capability-registry population, full harness-parity evaluation, hook-surface auditing, or skill-adapter generation. Those are deferred to follow-on slices. This slice is strictly registry activation.

## Changes

### 1. `harness-state/harness-registry.json` — Harness G entry

| Field | Current | Target | Rationale |
|-------|---------|--------|-----------|
| `status` | `"retired"` | `"active"` | Harness is live and functioning |
| `role` | `["loyal-opposition"]` | `["prime-builder", "loyal-opposition"]` | Owner directive; interactive PB already demonstrated |
| `can_receive_dispatch` (root) | `false` | `true` | Enable headless dispatch |
| `can_receive_dispatch` (invocation_surfaces.dispatch) | `false` | `true` | Enable headless dispatch (surface-level) |
| `reviewer_precedence` | `null` | `20` | Match Codex (A) and Claude (B) |
| `dispatch_quality` | `80.0` | `85.0` | Conservative bump; real score TBD by follow-on evaluation |
| `dispatch_max_items` (root) | `1` | `2` | Match Ollama/OpenRouter capacity; conservative for initial activation |
| `invocation_surfaces.dispatch.dispatch_max_items` | `1` | `2` | Surface-level match |
| `harness_type` | `"goose-desktop"` | `"goose"` | Normalize to simple type; desktop is the surface kind, not the type |

### 2. `harness-state/harness-identities.json` — No changes needed

Goose is already registered with ID `G`, `status: "active"`, `assigned_at: "2026-07-08T14:08:00Z"`. The identities file is correct.

### 3. Out of scope (deferred to follow-on)

- Capability registry entries for goose in `config/agent-control/harness-capability-registry.toml`
- Dispatcher rules in `config/dispatcher/rules.toml` (goose not currently referenced; adding dispatch eligibility may require a rules entry)
- Hook-surface parity audit
- `goose_harness.py` modifications (already functional)
- Skill adapter generation for goose (goose reads `.claude/` rules natively per current behavior)

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — harness activation must record owner decision, role assignment, and dispatch topology
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail and GO/NO-GO discipline
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing specification
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — activation recorded as durable artifact
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability preserved
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — Goose transitions from retired → active
- `REQ-HARNESS-REGISTRY-001` — registry is the canonical role/dispatch authority
- `DCL-SESSION-ROLE-RESOLUTION-001` — session-stated role override already functional for Goose
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below derives tests from linked specifications

## Requirement Sufficiency

**Existing requirements sufficient.** The harness registry schema and governance contracts already cover activation. No new specifications are required for a registry field update.

## Specification-Derived Verification

| Spec | Verification |
|------|-------------|
| REQ-HARNESS-REGISTRY-001 | `gt harness roles` returns G with both roles, active status |
| GOV-HARNESS-ONBOARDING-CONTRACT-001 | Registry JSON validates; dispatch fields set correctly |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | G status transitions from retired→active with audit trail |
| GOV-FILE-BRIDGE-AUTHORITY-001 | This proposal filed via governed bridge writer; GO required before implementation |

## Acceptance Criteria

1. `gt harness roles` shows harness G as `active` with roles `prime-builder` and `loyal-opposition`
2. `harness-state/harness-registry.json` validates as well-formed JSON with the updated G entry
3. `can_receive_dispatch: true` at both root and invocation_surfaces.dispatch levels
4. No other harness entries are modified (minimal surface)

## Owner Decisions / Input

- Mike directed this activation in the current session (2026-07-19) via explicit governance-bypass authorization, then selected option A (fast-track bridge proposal) for execution.
- The prior WITHDRAWN Slice 1 ADR was superseded by model-centric reframing; this proposal returns to harness-centric activation per renewed owner direction.
- AUQ evidence: owner selected option A from the three-path choice (fast-track bridge proposal).

## Recommended Commit Type

`feat:` — net-new activation of a previously retired harness identity.