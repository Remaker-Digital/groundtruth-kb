NEW

# GT-KB MCP Stable Harness Surface Conversion Proposal - NEW

bridge_kind: prime_proposal
Document: gtkb-mcp-stable-harness-surface-conversion
Version: 001 (NEW; Slice 0 scoping)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Source advisory: `bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md` (filed as NO-GO@001 transport per legacy convention).

## Claim

The advisory recommends a narrow MCP adapter as the stable harness-facing contract for GT-KB services, wrapping existing GT-KB APIs, CLI, and governed service paths without replacing MemBase, Deliberation Archive, dashboard, or bridge implementation. Prime proposes to convert this advisory into a Slice 0 scoping-only bridge that defines the MCP authority model and read-only surface contract.

Implementation is deferred to per-slice work. The MCP adapter should not become the source of truth; core GT-KB remains package/service/CLI/API plus the new MCP convenience surface.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/operating-model.md`
- `.claude/rules/project-root-boundary.md`
- `config/agent-control/system-interface-map.toml`

## Prior Deliberations

- `bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md` - source LO advisory.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` - LO insight reports informing the advisory.

## Owner Decisions / Input

Per S341 autonomous-execution directive, Prime authorizes this scoping-only bridge.

Owner position: do not change GT-KB service implementation. Adding MCP as a stable convenience surface between harness and application may be beneficial. MCP should not be authoritative or replace existing MemBase/bridge/governance mutation rules.

## Scope (Scoping)

Slice 0 authorizes specification and design work only:

1. Design read-only MCP tool/resource interface for status, MemBase lookup, deliberation search, spec lookup, backlog list, bridge index, and dashboard summary. No SQLite writes; no broad filesystem mutation tools.
2. Authority labels specification: every MCP response must carry lifecycle/authority labels (authoritative, generated-summary, advisory, allowed, denied, owner-approval-required).
3. Boundary enforcement design: MCP root boundary is `E:\GT-KB`; MCP must reject reads/requests outside this boundary.
4. Role-aware behavior design for Prime Builder and Loyal Opposition harnesses. Define how MCP routing differs by role.
5. Plugin boundary specification: if GT-KB is packaged as a plugin, the plugin is an onboarding bundle (skills, hooks, startup context, MCP registration, dashboard/doc affordances). Core GT-KB remains the package/service/CLI/API boundary.

Slice 0 explicitly excludes: MCP mutation tools; SQLite writes; dashboard/startup integration code; registration of MCP into harness configuration.

This Slice 0 GO, if granted, authorizes ONLY per-slice bridge filings.

## Test Plan (Scoping)

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-conversion` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-conversion` - exit 0 expected.
3. Specification review confirming MCP authority labels match system-interface-map.toml lifecycle distinctions.
4. Design review confirming boundary enforcement prevents read access outside `E:\GT-KB`.
5. Owner validation that role-aware behavior matches harness role assignments (prime-builder, loyal-opposition).

### Spec-to-test mapping

| Spec | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This NEW + Codex VERIFIED (pending). |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + this mapping. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Step 4 (MCP root boundary). |

## Acceptance Criteria

- [ ] Applicability + clause preflights PASS.
- [ ] MCP tool/resource specification documenting read-only interfaces, authority labels, and role behavior.
- [ ] Boundary enforcement design specification confirming `E:\GT-KB` root constraint.
- [ ] Plugin boundary specification (if applicable) confirming plugin is onboarding bundle, not source of truth.
- [ ] Decision artifact (proposal, rebuttal, or defer) regarding MCP placement: convenience surface vs authoritative boundary.
- [ ] Codex VERIFIED on this scoping proposal.

## Risk + Rollback

Risk: adding MCP as a new harness boundary may create expectation that MCP is authoritative for GT-KB services. Mitigation: scoping-only phase explicitly defines MCP as a convenience surface and confirms existing service APIs remain authoritative.

Rollback: `git revert <commit-sha>`. No implementation code lands in Slice 0.

## Recommended Commit Type

`docs:` - scoping bridge artifact only.

## Loyal Opposition Asks

1. Confirm read-only-only scope (no mutation tools) is the right Slice 0 boundary.
2. Confirm authority labels (authoritative, generated-summary, advisory, etc.) cover the spectrum needed for MCP responses.
3. Confirm boundary enforcement design is sufficient to prevent accidental reads outside `E:\GT-KB`.
4. Confirm plugin-vs-core split is correctly framed (plugin = onboarding bundle; core = service/API).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
