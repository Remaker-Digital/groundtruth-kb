NEW

# gtkb-wi4895-claude-token-outage-dispatch-topology — Temporary dispatcher topology for Claude Code token outage

bridge_kind: prime_proposal
Document: gtkb-wi4895-claude-token-outage-dispatch-topology
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-27T16:22:00Z

author_identity: Prime Builder / Codex
author_harness_id: A
author_session_context_id: codex-prime-20260627-claude-token-outage
author_model: GPT-5 Codex
author_model_version: 2026-06-27 runtime
author_model_configuration: Codex desktop interactive session; approval_policy=never; owner-selected Prime Builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4895-CLAUDE-TOKEN-OUTAGE-TOPOLOGY
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4895

target_paths: ["config/dispatcher/rules.toml", "harness-state/harness-registry.json"]

implementation_scope: config
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Claude Code (harness B) is out of tokens until July 1, 2026. The current dispatcher topology still leaves B active and event-capable, while Codex (A) is not selected as a Prime Builder dispatch target because its durable role is Loyal Opposition and its dispatcher receive flag is false.

This proposal authorizes a temporary, bounded dispatcher-topology change: make Codex A and Cursor E active dispatchable Prime Builder targets; suspend Claude B and disable its dispatcher receive/event eligibility; preserve the active viable Loyal Opposition targets D and F; and leave Antigravity C retired unless a separate owner decision reverses the prior retirement. The implementation must use governed CLI surfaces only: `gt harness set-role`, `gt harness suspend`, and `gt bridge dispatch config set-eligibility`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires Prime Builder to file this implementation proposal, receive an independent GO, and acquire implementation-start authorization before protected config/harness-state mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this proposal to cite the governing dispatcher and bridge-control specifications instead of relying on an uncited operational shortcut.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied by the machine-readable Project Authorization, Project, and Work Item header lines above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the post-implementation report and verification verdict to map checks back to the dispatcher topology requirements below.
- `GOV-STANDING-BACKLOG-001` — satisfied by `WI-4895`, which records this owner-directed operational recovery item in MemBase.
- `ADR-DISPATCHER-ARCHITECTURE-001` — governs dispatcher topology, dispatch target selection, and the requirement to change dispatch behavior through the dispatcher control plane rather than hand-editing runtime state.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — governs the expected dispatcher status/health evidence after topology changes.

## Prior Deliberations

- `DELIB-20266291` — owner decision captured for this exact temporary topology change while Claude Code is token-exhausted until July 1, 2026.
- `DELIB-20266276` — daemon-resilience program scope-lock included topology activation as a dispatcher-reliability concern; this proposal is narrower and supersedes only the immediate outage routing shape, not the broader resilience program.
- `INTAKE-f8bc08a3` — Dispatcher/Bridge CLI as primary mutating UI for GT-KB artifact operations; this proposal follows that rule by requiring governed CLI transactions, not direct config edits.
- `INTAKE-2ce995f2` — bounded parallel cross-harness auto-dispatch; this proposal preserves bounded multi-target dispatch while removing the token-exhausted Claude target.

## Owner Decisions / Input

Owner approval is recorded in `DELIB-20266291`: Mike directed that Claude Code is out of tokens until July 1, 2026, and instructed the dispatcher topology to make Codex and Cursor dispatchable Prime Builder targets, keep viable non-Claude targets as Loyal Opposition, and suspend Claude Code.

Project authorization `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4895-CLAUDE-TOKEN-OUTAGE-TOPOLOGY` is active for `WI-4895`, includes `ADR-DISPATCHER-ARCHITECTURE-001` and `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, allows `config` and `harness-state` mutation classes, and explicitly forbids reactivating Antigravity C.

## Requirement Sufficiency

Existing requirements sufficient — the owner decision in `DELIB-20266291`, `WI-4895` acceptance summary, and active PAUTH define a bounded operational topology change. No new specification is required because this is a temporary dispatcher-control transaction under the existing dispatcher architecture and centralized dispatch-service contracts.

## Specification-Derived Verification Plan

Before mutation:

```text
gt bridge dispatch config set-eligibility A --can-receive-dispatch --can-fire-events --dry-run --json
gt bridge dispatch config set-eligibility B --no-can-receive-dispatch --no-can-fire-events --dry-run --json
```

Expected: dry-runs report only the intended A/B dispatcher eligibility deltas.

Implementation commands after GO and implementation-start packet:

```text
gt harness set-role --harness A --role prime-builder --reason "WI-4895 temporary Claude token-outage topology: Codex dispatchable PB"
gt harness suspend --harness B --cause owner-declared --reason "WI-4895 temporary Claude Code token outage until 2026-07-01"
gt bridge dispatch config set-eligibility A --can-receive-dispatch --can-fire-events --json
gt bridge dispatch config set-eligibility B --no-can-receive-dispatch --no-can-fire-events --json
```

Verification commands:

```text
gt harness show --harness A
gt harness show --harness B
gt bridge dispatch config --json
gt bridge dispatch status --json
gt bridge dispatch health --json
gt bridge dispatch report --json
```

Expected results:

- `GOV-FILE-BRIDGE-AUTHORITY-001`: implementation report cites the GO, work-intent claim, implementation-start packet, exact commands, and post-change status evidence.
- `ADR-DISPATCHER-ARCHITECTURE-001`: `selected_by_role.prime-builder` contains A/Codex and E/Cursor; `selected_by_role.loyal-opposition` contains active viable non-Claude LO targets D/Ollama and F/OpenRouter; C/Antigravity remains retired and absent from selected targets.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`: `gt bridge dispatch status --json` shows B/Claude suspended and not selected; `gt bridge dispatch config --json` shows B cannot receive dispatch and cannot fire events; health is not FAIL due to missing role capacity.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the verification verdict re-runs the same status/config/health checks and confirms the expected topology.

## Risk / Rollback

Risk is operational misrouting: Codex could receive Prime Builder work sooner than intended, or Claude could continue firing events if only role metadata changes and dispatcher eligibility is left untouched. The implementation therefore must change both durable harness lifecycle/role state and dispatcher eligibility, then verify selected targets through the dispatcher CLI.

Rollback is the inverse governed transaction: resume Claude B, restore its dispatcher event eligibility if tokens are available, and set Codex A back to Loyal Opposition or non-receive-eligible according to the owner-selected post-outage topology. Do not reactivate Antigravity C as part of rollback unless a separate owner decision reverses the prior retirement.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4895-claude-token-outage-dispatch-topology`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

chore — temporary operational topology/configuration change, not a source behavior change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
