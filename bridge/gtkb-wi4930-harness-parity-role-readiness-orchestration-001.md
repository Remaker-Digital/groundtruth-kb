NEW

# WI-4930 Harness Parity Role-Readiness Orchestration

bridge_kind: prime_proposal
Document: gtkb-wi4930-harness-parity-role-readiness-orchestration
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-30 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f170a-27c3-75c3-971b-2e329ebba25a
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION
Project: PROJECT-GTKB-CROSS-HARNESS-PARITY
Work Item: WI-4930
Related Work Items: WI-4928

target_paths: ["scripts/session_self_initialization.py", "scripts/check_harness_parity.py", "scripts/harness_parity_phase2.py", "scripts/parity_discovery_diff.py", "platform_tests/scripts/test_check_harness_parity.py", "platform_tests/scripts/test_cross_harness_protocol_parity.py", "platform_tests/scripts/test_session_self_initialization.py", ".claude/skills/harness-parity-review/SKILL.md", ".codex/skills/harness-parity-review/SKILL.md", ".cursor/skills/harness-parity-review/SKILL.md", ".agent/skills/harness-parity-review/SKILL.md", ".api-harness/skills/harness-parity-review/SKILL.md", ".codex/skills/MANIFEST.json", ".cursor/skills/MANIFEST.json", ".agent/skills/MANIFEST.json", ".api-harness/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml"]

implementation_scope: source, tests, skill, registry
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal implements WI-4930, the Slice B follow-up to the verified WI-4928
phase-1 checker repair. WI-4928 corrected static catalog parity false positives;
WI-4930 wires the corrected semantics into startup disclosure, role-readiness
coverage, phase-2 review workflow, and operator-facing terminology so a green
or warning catalog check is not mistaken for proof that a harness can fill a
Prime Builder or Loyal Opposition role.

The previous bridge thread
`gtkb-wi4928-wi4930-harness-parity-role-readiness` is terminal VERIFIED for
Slice A only. This proposal opens a fresh bridge thread for the remaining
Slice B orchestration work. No protected source, test, skill, config, or
registry mutation is performed before Loyal Opposition review and GO.

## Backlog and Bridge Coverage

Live Auto-builder coverage before filing found 55 open/backlogged P0/P1/P2
work items (`P0=1`, `P1=12`, `P2=42`) and 37 active projects. The selected
candidate is WI-4930 because it is P1, attached to active
`PROJECT-GTKB-CROSS-HARNESS-PARITY` memberships, covered by active
membership-based `PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION`,
and its WI-4928 prerequisite has terminal bridge verification at
`bridge/gtkb-wi4928-wi4930-harness-parity-role-readiness-004.md`.

Other live Prime bridge work was not taken over in this filing:
`gtkb-wi4783-session-role-gate-fallback-purge` is latest GO but has an active
go-implementation claim held by session
`019f09c9-2db0-7b00-a337-40f998b07e56` until 2026-06-30T06:29:44Z.
The canonical Prime scan surfaced no unclaimed dispatchable GO/NO-GO work.

## Specification Links

- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - governs applicability-aware parity populations, waiver handling, discovery-diff behavior, and cross-harness parity evidence.
- `ADR-CROSS-HARNESS-PARITY-001` - parity means semantic capability equivalence, not file presence or registry row presence alone.
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` - governs role/harness parity surfaces and Codex-baseline comparison.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source, test, skill, and config changes require bridge GO, implementation-start authorization, report, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries PAUTH, project, work item, and inline JSON target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links governing requirements before implementation and maps them to verification commands.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must carry forward the spec-to-test mapping and executed command evidence.
- `GOV-STANDING-BACKLOG-001` - WI-4930 is the standing-backlog authority for this orchestration slice.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - active project authorization covers WI-4930 by active project membership.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - this proposal preserves the work item, prior verification, bridge state, tests, and review workflow as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the implementation must update the artifact graph and generated adapters instead of leaving parity semantics in transient session notes.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the verified Slice A state and remaining Slice B work trigger a fresh implementation proposal rather than informal continuation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain inside the GT-KB root and outside adopter application scope.

## Prior Deliberations

- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` - owner authorization for the cross-harness parity program and active membership-based PAUTH.
- `bridge/gtkb-wi4928-wi4930-harness-parity-role-readiness-001.md` - original combined proposal, including Slice B orchestration scope.
- `bridge/gtkb-wi4928-wi4930-harness-parity-role-readiness-002.md` - Loyal Opposition GO approving sequential Slice A first, then Slice B after verification.
- `bridge/gtkb-wi4928-wi4930-harness-parity-role-readiness-003.md` - Slice A implementation report explicitly deferring WI-4930.
- `bridge/gtkb-wi4928-wi4930-harness-parity-role-readiness-004.md` - Slice A VERIFIED verdict; prerequisite evidence for this proposal.
- `bridge/gtkb-harness-parity-phase-2-baseline-evaluator-001.md` - phase-2 operational evaluator context complementary to this work.
- `bridge/gtkb-cross-harness-parity-slice-3-discovery-diff-004.md` - existing discovery-diff scope and hook-surface boundary.

## Owner Decisions / Input

No new owner decision is required before filing this proposal. The required
owner authority is already recorded in `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION`,
and active project authorization
`PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION` covers WI-4930 by
active project membership. This proposal does not request credential changes,
provider key rotation, production deployment, or GitHub settings mutation.

## Requirement Sufficiency

Existing requirements sufficient.

WI-4930 states the required orchestration behavior directly: startup parity
uses assigned harness scope, a fleet role-coverage gate exists, phase-2
evaluator output is on the review skill path, discovery-diff or documented
equivalent covers non-Claude/Codex harnesses, and operator documentation
distinguishes catalog parity from role readiness. The linked cross-harness
parity ADR/DCL and verified WI-4928 Slice A work provide enough governing
requirements for implementation.

## Proposed Scope

1. Update `scripts/session_self_initialization.py` so `_harness_parity_status`
   evaluates the resolved harness when one is available instead of collapsing
   Cursor, Antigravity, Ollama, and OpenRouter to `harness=all`. Startup text
   must disclose whether the result is catalog parity or operational readiness.
2. Add a fleet role-coverage check to `scripts/check_harness_parity.py` or a
   closely related function so GT-KB can prove each operating role has at least
   one active harness covering required capabilities after waivers and
   applicability rules are applied.
3. Consume `resolve_applicability()` consistently when selecting harness
   populations: role-relative capabilities should check harnesses assigned that
   role; universal capabilities should check the applicable active population.
4. Update the canonical `harness-parity-review` skill and generated adapters so
   the required workflow includes both phase-1 catalog parity and phase-2
   operational readiness, plus discovery-diff where hook configs exist.
5. Keep `scripts/parity_discovery_diff.py` honest about its current Claude/Codex
   hook-config scope. If expanding discovery-diff beyond hook-config harnesses
   is not feasible in this slice, document the non-applicability/deferral in
   the skill and implementation report rather than implying coverage.
6. Add or update focused tests for startup harness scoping, role-coverage
   behavior, applicability-aware populations, and the skill command path.

## Non-Scope

- No MemBase status mutation or bridge-verified backlog reconciliation.
- No credential lifecycle, provider key rotation, production deployment, or
  GitHub settings mutation.
- No dispatcher topology flip, durable role reassignment, or harness activation
  change.
- No implementation of the full benchmark fixture/runner/scoring program from
  WI-4580, WI-4581, or WI-4583.
- No claim that phase-1 catalog parity alone proves operational role fitness.

## Cross-Harness Disposition

| Harness | Disposition |
| --- | --- |
| Codex | Primary baseline and active Prime Builder surface; startup and skill paths must remain truthful. |
| Claude Code | Phase-1 catalog and discovery-diff hook-config coverage remains applicable where `.claude/settings.json` exists. |
| Cursor | Startup scoping must stop collapsing Cursor to `all`; role-readiness reporting should reflect Cursor's actual assigned role and capability rows. |
| Antigravity | Startup/reporting should distinguish supported role-readiness surfaces from missing native hooks or documented fallbacks. |
| Ollama / OpenRouter | API/provider harnesses must not pass on Claude/Codex hook files they do not invoke; phase-2/provider readiness evidence remains the truthful operational surface. |

## Spec-Derived Verification Plan

| Specification | Test or verification command | Expected result |
| --- | --- | --- |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`; `ADR-CROSS-HARNESS-PARITY-001` | `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q --tb=short` | Role coverage, applicability-aware populations, and waiver/classification behavior are covered by focused tests. |
| `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001`; `GOV-STANDING-BACKLOG-001` | `python -m pytest platform_tests/scripts/test_cross_harness_protocol_parity.py -q --tb=short` | Cross-harness parity expectations remain consistent with active role and capability surfaces. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4930-harness-parity-role-readiness-orchestration` before implementation, then targeted validation of changed files | Implementation occurs only after GO and within target paths. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4930-harness-parity-role-readiness-orchestration` | `preflight_passed: true`; no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/check_harness_parity.py --validate-schema`; `python scripts/check_harness_parity.py --all --markdown`; `python scripts/harness_parity_phase2.py --project-root . --format markdown`; `python scripts/parity_discovery_diff.py --project-root . --markdown` | The report carries exact command output and distinguishes catalog parity, operational readiness, and hook discovery-diff scope. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `python scripts/generate_codex_skill_adapters.py --update-registry`; `python scripts/generate_antigravity_skill_adapters.py --update-registry`; `python scripts/generate_api_skill_adapters.py` when the canonical skill changes | Generated adapters and manifests are refreshed rather than left stale. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Bridge applicability and target-path review | All target paths stay in `E:\GT-KB` platform scope. |

## Risk / Rollback

Risk: stricter role-readiness checks may turn previously hidden false positives
into WARN or FAIL rows. That is intended if the evidence is honest; the
implementation report must separate real blockers from accepted typed waivers.

Risk: startup disclosure could become noisier if it includes both catalog and
operational readiness. Mitigation: keep compact text precise and reserve
detailed matrices for command/report output.

Rollback: revert the single implementation commit and regenerate skill adapters
from the prior canonical skill if necessary. Bridge files remain append-only
audit artifacts and are not deleted by rollback.

## Pre-Filing Preflight Subsection

Applicability preflight was run against this candidate content before filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4930-harness-parity-role-readiness-orchestration --content-file .gtkb-state/propose-drafts/gtkb-wi4930-harness-parity-role-readiness-orchestration-001.md --json
```

Result: `preflight_passed=true`, `missing_required_specs=[]`,
`missing_advisory_specs=[]`, packet hash
`sha256:6949fc71e90f5e349aeb6f2e6a7005476eaddc0e0d8b2c630e8b2cec3e64d8ed`.

Clause preflight was run against this candidate content before filing:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4930-harness-parity-role-readiness-orchestration --content-file .gtkb-state/propose-drafts/gtkb-wi4930-harness-parity-role-readiness-orchestration-001.md
```

Result: clauses evaluated `5`, `must_apply=4`, blocking gaps `0`, exit `0`.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered
bridge file for `gtkb-wi4930-harness-parity-role-readiness-orchestration`;
no prior bridge file is deleted or rewritten. Dispatcher/TAFE state plus the
numbered file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix:

This is a defect repair for misleading role-readiness and startup parity
orchestration after the WI-4928 checker-correctness fix. It may add small
helper modes, but the user-visible purpose is to remove false confidence and
stale workflow reporting.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
