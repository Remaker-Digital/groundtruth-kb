NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

# WI-4784 Role Authority Terminology Purge

bridge_kind: prime_proposal
Document: gtkb-wi4784-role-authority-terminology-purge
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-05 UTC

Project Authorization: PAUTH-GTKB-ROLE-AUTHORITY-BOUNDARY-20260702
Project: PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE
Work Item: WI-4784

target_paths: ["AGENTS.md", "CLAUDE.md", ".claude/rules/canonical-terminology.md", ".claude/rules/prime-builder-role.md", ".claude/rules/operating-role.md", "config/agent-control/SESSION-STARTUP-INDEX.md", "config/agent-control/SESSION-STARTUP-CONTROL-MAP.md", "config/agent-control/system-interface-map.toml", "config/agent-control/declarative-agent-role-manifest.yaml", "config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_harness_state_sot.py", "scripts/session_self_initialization.py", "scripts/session_role_resolution.py", "scripts/session_start_dispatch_core.py", "scripts/workstream_focus.py", "scripts/_kb_attribution.py", "scripts/bridge_work_intent_registry.py", "scripts/dispatcher_runtime.py", "scripts/harness_roles.py", "scripts/benchmarks/harness_role_protocol_smoke.py", "scripts/benchmarks/harness_quality_manifest.py", "scripts/benchmarks/benchmark_dispatch_envelope.py", "platform_tests/scripts/test_dcl_role_resolution_authority_001.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization_disclosure_shape.py", "platform_tests/scripts/test_dispatcher_runtime_durable_keyed_regression.py", "platform_tests/hooks/test_session_role_resolution.py", "platform_tests/hooks/test_session_start_dispatch_role_cache.py"]

implementation_scope: narrative_rule_docs/source_comments/tests/doctor_guard
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4784 is Phase 3 of the role-authority dispatcher-only purge. Prior VERIFIED work corrected the governing principle, audited the leaks, fixed behavior gates, and added doctor coverage. The remaining open slice is terminology hygiene: replace unqualified `durable role`, `durably`, and `durable operating role` wording with precise terms:

- `dispatcher-routing role` or `dispatcher role set` where the harness registry governs headless dispatch routing.
- `session role` or `resolved session role` where interactive behavior, attribution, menus, gates, and AUQ routing are meant.

This proposal is intentionally not a new behavior fix. It is a scanner-driven terminology cleanup plus guard refinement to make the corrected authority model legible and harder to regress.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` - the registry is dispatcher/default fallback authority only; session behavior uses the resolved session role.
- `DCL-SESSION-ROLE-RESOLUTION-001` - role-resolution wording must distinguish dispatcher registry role-set, resolver fallback, and explicit session role.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` - interactive owner-declared role can govern session behavior.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` and `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - terminology must preserve persistence semantics across resume/compaction without implying registry mutation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - role-authority wording in root instructions and application-boundary surfaces must preserve the GT-KB/application placement boundary and must not move Agent Red or adopter authority into platform role surfaces.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal and LO verdict use the live numbered bridge chain.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries PAUTH, project, and work item linkage.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal cites all relevant role-authority specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include tests derived from the role-authority specs.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH authorizes the bounded terminology cleanup but does not bypass LO GO or implementation-start authorization.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - implementation must scan current live files, not rely on the older 96-occurrence estimate.

## Prior Deliberations

- `DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613` - role authority is owner-declared/session-resolved for interactive behavior.
- `DELIB-20265878` - owner selected the dispatcher-only registry principle and created the role-authority purge project.
- `DELIB-20260702-ROLE-AUTHORITY-SCOPED-APPROVAL-A` - owner approved the scoped correction authorization `PAUTH-GTKB-ROLE-AUTHORITY-BOUNDARY-20260702`.
- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner directed continuation of the high-priority queue.
- `bridge/gtkb-wi4781-role-authority-dispatcher-only-formalization-004.md`, `bridge/gtkb-wi4782-session-role-authority-audit-004.md`, and `bridge/gtkb-role-authority-boundary-implementable-correction-015.md` - prior VERIFIED role-authority correction and audit evidence.

## Owner Decisions / Input

No additional owner decision is required before LO review. The owner-approved scope is already recorded in `DELIB-20265878`, `DELIB-20260702-ROLE-AUTHORITY-SCOPED-APPROVAL-A`, and `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE`.

This proposal does not request durable role reassignment, production deployment, credential lifecycle work, or broad status mutation.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4784 explicitly states the terminology replacement and V4 framing inversion. The governing role-authority specs define the terms that the implementation must preserve.

## Proposed Implementation

1. Run a current deterministic scan for unqualified role-authority phrases across the target envelope:
   - `durable role`
   - `durable-role`
   - `durable operating role`
   - `durably` when it refers to role authority rather than generic persistence.
2. Classify each occurrence before editing:
   - dispatcher routing: replace or qualify as `dispatcher-routing role` / `dispatcher role set`;
   - interactive behavior: replace with `session role` / `resolved session role`;
   - storage semantics: replace with `persistent` / `stored` when not about role authority;
   - code identifiers or historical evidence: leave untouched if changing it would break APIs, tests, or quoted history, but add nearby clarification only when necessary.
3. Update `.claude/rules/canonical-terminology.md` so aliases no longer normalize ambiguous `durable role` language into behavior authority.
4. Update startup/control-map wording that currently describes overlays or disclosures as selected by a `durable role` when it means dispatcher/default routing role or resolved session role.
5. Update source comments, user-facing disclosure text, and tests only where terminology encodes the old authority model. Do not change behavior paths beyond string/comment/text expectations.
6. Tighten or extend the existing role-authority doctor/test surfaces so future unqualified behavior-authority wording is flagged while dispatcher-owned wording remains allowed.

## Spec-Derived Verification Plan

| Governing surface | Required behavior | Verification |
| --- | --- | --- |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Non-dispatcher behavior surfaces do not describe the registry role as authority. | Run the role-authority doctor tests and a deterministic scan; report remaining intentional dispatcher-owned or historical references. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Resolver language distinguishes session role from registry fallback. | Targeted session-role-resolution tests continue to pass. |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` | Interactive role override language remains intact. | Tests covering session initialization and role disclosure continue to pass. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Implementation uses current file scan results. | Implementation report includes scan command and summarized residuals. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | LO can verify with command evidence. | Implementation report includes pytest and ruff command output plus residual scan classification. |

Minimum verification after GO:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor_harness_state_sot.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/hooks/test_session_role_resolution.py platform_tests/hooks/test_session_start_dispatch_role_cache.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_harness_state_sot.py scripts/session_self_initialization.py scripts/session_role_resolution.py scripts/session_start_dispatch_core.py scripts/workstream_focus.py scripts/_kb_attribution.py scripts/bridge_work_intent_registry.py scripts/dispatcher_runtime.py scripts/harness_roles.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/hooks/test_session_role_resolution.py platform_tests/hooks/test_session_start_dispatch_role_cache.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_harness_state_sot.py scripts/session_self_initialization.py scripts/session_role_resolution.py scripts/session_start_dispatch_core.py scripts/workstream_focus.py scripts/_kb_attribution.py scripts/bridge_work_intent_registry.py scripts/dispatcher_runtime.py scripts/harness_roles.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/hooks/test_session_role_resolution.py platform_tests/hooks/test_session_start_dispatch_role_cache.py
```

Markdown/TOML/YAML files are verified by targeted scan output and relevant pytest assertions rather than ruff formatting.

## Acceptance Criteria

- Unqualified role-authority wording is replaced or explicitly classified as dispatcher-owned, resolver-fallback-owned, or historical/quoted.
- Canonical terminology distinguishes dispatcher-routing registry role-set from resolved session role.
- Startup/control-map disclosures no longer imply registry role governs interactive behavior.
- Existing dispatcher-owned tests that intentionally use durable-role-keyed dispatch continue to pass.
- No runtime behavior change is introduced except string/test expectations needed to preserve the clarified model.
- Residual scan output is documented in the implementation report with reasons for any remaining hits.

## Risk / Rollback

Risk is moderate because this touches many governance and test text surfaces. The mitigation is scanner classification before edits, no API renames, and focused tests around role behavior. Rollback is a normal revert of documentation/string/test changes; behavior changes are out of scope.

## Bridge Filing

This proposal is filed as a fresh WI-4784 slice and does not revise already VERIFIED role-authority behavior-fix threads.

## Recommended Commit Type

`docs:` because the primary change is terminology and explanatory-surface correction, with tests/doctor guard updates to prevent drift.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
