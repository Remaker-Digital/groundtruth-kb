REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc9e-ca08-7b40-8eb2-23994cc2029d
author_model: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder

# Harness C Governance Gate Parity and Cloud Config Protection

bridge_kind: prime_proposal
Document: gtkb-harness-c-governance-gate-parity-gap
Version: 005
Revises: bridge/gtkb-harness-c-governance-gate-parity-gap-003.md
Responds-To: bridge/gtkb-harness-c-governance-gate-parity-gap-004.md
Author: Prime Builder (Codex, harness A)
Date: 2026-06-16 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4543

target_paths: ["scripts/implementation_start_gate.py", "scripts/session_self_initialization.py", "scripts/sync_antigravity_rules.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_sync_antigravity_rules.py", ".githooks/pre-commit", ".agent/rules/**", "AGENTS.md", "bridge/gtkb-harness-c-governance-gate-parity-gap-*.md"]

implementation_scope: protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## NO-GO Response

This revision addresses the NO-GO in
`bridge/gtkb-harness-c-governance-gate-parity-gap-004.md` by fixing the
machine-readable target scope, declaring in-root output paths, and removing
stale retired-index filing language. This revision does not recreate or
require `bridge/INDEX.md`.

## Summary

This proposal addresses a governance-gate parity gap on Harness C
(Antigravity) and other hook-limited harnesses where a harness may not execute
the same PreToolUse checks as Claude Code or Codex. It adds harness-agnostic
mechanical enforcement around the already-required bridge GO plus work-intent
implementation boundary and extends the start gate to cloud/deployment
configuration paths that are already protected.

## Prior Deliberations

- `INTAKE-5a61f299` - Claim-gated implementation-start: holding the
  GO-implementation claim is required before editing a GO'd thread's target
  paths.
- `DELIB-20260614-ANTIGRAVITY-ADVISORY-REROUTE-AUTH` - owner approved
  reverting unreviewed Antigravity auto-implementations and re-routing them
  through the bridge protocol.
- Current owner directive - no agent should alter cloud service or
  deployed-application configuration without oversight/review before action and
  auditability after.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected implementation
  work requires a bridge GO and live implementation-start authorization.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge files govern proposal, review,
  implementation report, and verification transitions.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision includes
  explicit project/work authorization and machine-readable target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision
  cites the governing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification is mapped
  from requirements to concrete tests and diagnostics.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - cross-harness gate parity matters when
  some harnesses cannot rely on the same native hook substrate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all generated and mutated
  artifacts remain under the GT-KB root at `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this proposal preserves owner
  governance requirements as durable implementation artifacts.
- `GOV-STANDING-BACKLOG-001` - the work is tied to a tracked project/work item
  and must remain visible in backlog-driven execution.

## Requirement Sufficiency

Existing requirements are sufficient for the revised scope. All generated and
mutated artifacts are in-root outputs under `E:\GT-KB`:

- `E:\GT-KB\scripts\implementation_start_gate.py`
- `E:\GT-KB\scripts\session_self_initialization.py`
- `E:\GT-KB\scripts\sync_antigravity_rules.py`
- `E:\GT-KB\platform_tests\scripts\test_implementation_start_gate.py`
- `E:\GT-KB\platform_tests\scripts\test_sync_antigravity_rules.py`
- `E:\GT-KB\.githooks\pre-commit`
- `E:\GT-KB\.agent\rules\`
- `E:\GT-KB\AGENTS.md`
- `E:\GT-KB\bridge\gtkb-harness-c-governance-gate-parity-gap-005.md`

## Proposed Implementation

1. Update `scripts/implementation_start_gate.py` so unauthorized attempts to
   mutate `Dockerfile`, `Dockerfile.test`, `Dockerfile.ui`, `.dockerignore`,
   `docker-compose.yml`, `shopify.app.toml`, `.env`, `env.local`, and
   `env.staging` are classified as protected cloud/deployment configuration
   edits and blocked unless the active implementation packet authorizes them.
2. Add `.githooks/pre-commit` as the tracked hook template. The hook should run
   the implementation start gate against staged protected paths and fail closed
   when no valid GO/work-intent packet exists.
3. Update `scripts/session_self_initialization.py` to install or refresh the
   local `.git/hooks/pre-commit` hook from `.githooks/pre-commit` during GT-KB
   startup when the workspace is writable.
4. Add `scripts/sync_antigravity_rules.py` to copy essential GT-KB operating
   rules into `.agent/rules/` for Antigravity startup without relying on the
   retired index or hand-maintained duplicate instructions.
5. Update `AGENTS.md` to describe the self-enforcement and pre-commit safety
   boundary for harnesses whose native hooks are incomplete or unsupported.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | No credentials or secret values are introduced; cloud/env paths are classification targets only. | Run credential scan hook and review diffs for secret-shaped values. | |
| CQ-PATHS-001 | Yes | Use only in-root paths under `E:\GT-KB` and the explicit target_paths list. | Applicability and clause preflights; `Test-Path bridge\INDEX.md`. | |
| CQ-COMPLEXITY-001 | Yes | Keep gate and sync logic small, deterministic, and covered by focused tests. | Focused pytest for implementation start gate and sync script. | |
| CQ-CONSTANTS-001 | Yes | Centralize protected path patterns in the gate logic or a nearby constant list. | Focused pytest asserts all protected cloud/config examples. | |
| CQ-SECURITY-001 | Yes | Fail closed for unauthorized protected cloud/deployment edits. | Diagnostic start-gate tests for unauthorized and authorized cases. | |
| CQ-DOCS-001 | Yes | Update AGENTS.md only for the self-enforcement/pre-commit boundary and avoid retired-index instructions. | Fixed-string search for `bridge/INDEX.md` references in changed text. | |
| CQ-TESTS-001 | Yes | Add or update targeted tests for start gate, pre-commit behavior, and Antigravity rule sync. | `python -m pytest platform_tests\scripts\test_implementation_start_gate.py platform_tests\scripts\test_sync_antigravity_rules.py -q --tb=short` | |
| CQ-LOGGING-001 | Yes | Ensure diagnostics explain blocked protected paths without exposing secrets. | Focused tests assert diagnostic classification output. | |
| CQ-VERIFICATION-001 | Yes | Carry command evidence into the post-implementation report. | Ruff, focused pytest, preflights, and `Test-Path bridge\INDEX.md`. | |

## Spec-Derived Verification Plan

Run:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-harness-c-governance-gate-parity-gap --content-file bridge\gtkb-harness-c-governance-gate-parity-gap-005.md
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-harness-c-governance-gate-parity-gap --content-file bridge\gtkb-harness-c-governance-gate-parity-gap-005.md
python -m pytest platform_tests\scripts\test_implementation_start_gate.py platform_tests\scripts\test_sync_antigravity_rules.py -q --tb=short
python -m ruff check scripts\implementation_start_gate.py scripts\session_self_initialization.py scripts\sync_antigravity_rules.py platform_tests\scripts\test_implementation_start_gate.py platform_tests\scripts\test_sync_antigravity_rules.py
python -m ruff format --check scripts\implementation_start_gate.py scripts\session_self_initialization.py scripts\sync_antigravity_rules.py platform_tests\scripts\test_implementation_start_gate.py platform_tests\scripts\test_sync_antigravity_rules.py
Test-Path bridge\INDEX.md
```

Expected:

- Applicability and clause preflights pass with no blocking gaps.
- Start-gate tests prove unauthorized cloud/deployment config mutations are
  blocked and authorized GO/work-intent edits still pass.
- Antigravity rule-sync tests prove essential rules are copied deterministically
  into `.agent/rules/`.
- Ruff check and format pass for touched Python files.
- `bridge\INDEX.md` remains absent.

## Risks

- A pre-commit hook is a last-resort enforcement layer, not a replacement for
  bridge preconditions. Agents must still self-enforce before editing.
- Installing `.git/hooks/pre-commit` is local workspace state; the tracked
  source of truth is `.githooks/pre-commit`, and session startup should refresh
  the local hook.
- Over-broad cloud/config classification could block legitimate platform work.
  The tests must cover authorized packets as well as unauthorized edits.

## Rollback

Revert edits to the listed target paths and remove the local `.git/hooks/pre-commit`
if it was installed from `.githooks/pre-commit`. Do not recreate the retired
`bridge/INDEX.md` surface.
