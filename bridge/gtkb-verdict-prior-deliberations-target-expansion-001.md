NEW

# WI-4664 Target Expansion For Verdict Prior-Deliberations Seeding

bridge_kind: prime_proposal
Document: gtkb-verdict-prior-deliberations-target-expansion
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-18 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019edbad-39e6-7b62-a901-430263b702fc
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; Prime Builder; Hygiene PB

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4664

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", ".claude/skills/verify/helpers/write_verdict.py", ".claude/skills/verify/SKILL.md", ".claude/skills/bridge/SKILL.md", ".claude/skills/proposal-review/SKILL.md", ".codex/skills/verify/SKILL.md", ".codex/skills/bridge/SKILL.md", ".codex/skills/proposal-review/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/skills/test_verify_prior_deliberations_pre_population.py", "groundtruth-kb/tests/fixtures/scaffold_golden/**"]

implementation_scope: verdict_prior_deliberations_target_expansion
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
protected_source_mutation_in_scope: true

---

## Summary

The latest GO for `gtkb-verdict-prior-deliberations-seeding` authorizes the
core WI-4639 implementation paths, but a focused implementation attempt found
that the required adapter parity checks also require generated updates to
`.codex/skills/MANIFEST.json` and
`config/agent-control/harness-capability-registry.toml`. Those generated
metadata paths are outside the current GO packet, so Prime Builder cannot
complete WI-4639 without either changing the design to avoid the parity update
or obtaining an expanded target-path envelope.

This proposal requests that expanded envelope under the explicit follow-up work
item `WI-4664`. It does not bypass the original WI-4639 review. It carries
forward the approved WI-4639 design and adds the two missing generated metadata
targets so the implementation can be finished, verified, and reported as one
coherent bridge cycle.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — Protected source/config/skill-adapter work
  must proceed through the numbered bridge chain and must not be completed from
  an under-scoped GO packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — The expanded
  proposal must carry concrete specification links rather than relying on the
  prior GO by implication.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — The proposal carries
  explicit project, work item, and project authorization metadata for
  `PROJECT-GTKB-MAY29-HYGIENE` / `WI-4664`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — The implementation report
  must map the expanded target scope to tests proving the verdict-seeding
  behavior and adapter/registry parity.
- `GOV-STANDING-BACKLOG-001` — `WI-4664` is the durable backlog record for the
  discovered target-path omission, preventing repeated unsafe attempts to
  consume the current WI-4639 GO.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — The active May29 Hygiene project
  authorization permits proposing implementation for unimplemented project work
  items but remains additive to bridge GO and implementation-start packets.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`,
  `ADR-DA-READ-SURFACE-PLACEMENT-001`, and
  `DCL-CONCEPT-ON-CONTACT-001` — These remain the governing requirements for
  WI-4639's verdict-side Prior-Deliberations seeding behavior.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` and
  `.claude/rules/sot-read-discipline.md` — The shared seeding primitive must
  remain a single canonical implementation with generated adapter metadata kept
  fresh.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
  `.claude/rules/project-root-boundary.md` — All targets are in-root GT-KB
  platform files; no Agent Red or out-of-root path is in scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — The work-item/bridge/evidence graph
  should reflect the discovered target-path gap rather than leaving it as chat
  memory.

## Prior Deliberations

- `INTAKE-b4928376` — Intake: Bridge review eligibility is harness-agnostic; durable role is a fallback, not a review/verdict gate
- `INTAKE-5a61f299` — Intake: Claim-gated implementation-start: holding the GO-implementation claim is required before editing a GO'd thread's target paths
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — S382 owner decisions: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS completion scope (Slice 1 + Slice 4)
- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` — Owner/governance
  authorization for proposing implementation for unimplemented May29 Hygiene
  work items.
- `bridge/gtkb-verdict-prior-deliberations-seeding-001.md` and
  `bridge/gtkb-verdict-prior-deliberations-seeding-002.md` — The original
  WI-4639 proposal and GO verdict. This proposal preserves that design and
  expands the implementation envelope only where verification showed the target
  set was incomplete.
- `WI-4664` — Captures the discovered omission: generated adapter metadata
  paths are required by parity tests but absent from the current WI-4639 GO.
- `bridge/gtkb-target-paths-coverage-preflight-001.md` — Establishes the class
  of generator-output target-path coverage this proposal is correcting.

## Owner Decisions / Input

No new owner decision is required for this proposal. The active May29 Hygiene
authorization `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`
is backed by `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` and covers
proposal filing for unimplemented project work items, including `WI-4664`.
Implementation still requires LO GO and a fresh implementation-start packet.

## Requirement Sufficiency

Existing requirements sufficient. The required behavior and verification
discipline are already governed by the WI-4639 specification links plus the
bridge, source-of-truth, and project-authorization records cited above. The
defect is an under-scoped target-path envelope, not a missing product
requirement.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | No credentials or credential-shaped values are introduced. | Credential scan in the bridge writer and commit hooks. | |
| CQ-PATHS-001 | Yes | Keep all implementation paths in-root and limited to the inline `target_paths`. | Target-path JSON parse, implementation-start packet, and final `git diff --name-only`. | |
| CQ-COMPLEXITY-001 | Yes | Keep the implementation to shared primitive extraction, a thin helper, skill docs, generated adapter metadata, and tests. | Source review plus focused helper tests. | |
| CQ-CONSTANTS-001 | Yes | Preserve one canonical prior-deliberations primitive and avoid duplicated constants. | Propose/verdict seeding parity tests. | |
| CQ-SECURITY-001 | Yes | Do not bypass bridge GO or implementation-start authorization for protected config and skill surfaces. | Implementation-start packet and bridge report evidence. | |
| CQ-DOCS-001 | Yes | Document the verdict-side seeding step in all three interactive verdict skill surfaces and generated Codex adapters. | Skill adapter parity checks and source review. | |
| CQ-TESTS-001 | Yes | Run focused prior-deliberations, bridge helper, adapter, and golden fixture tests. | Commands listed in the spec-derived verification plan. | |
| CQ-LOGGING-001 | Yes | Keep verdict-side helper audit logs namespaced away from propose-side helper logs. | Test asserts `.gtkb-state/bridge-verify-helper/` output. | |
| CQ-VERIFICATION-001 | Yes | Run separate ruff lint and format gates for changed Python files. | `ruff check` and `ruff format --check`. | |

## Spec-Derived Verification Plan

Spec-to-test mapping for the expanded scope:

- `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: run
  `python scripts/bridge_applicability_preflight.py --bridge-id
  gtkb-verdict-prior-deliberations-target-expansion --json` and
  `python scripts/adr_dcl_clause_preflight.py --bridge-id
  gtkb-verdict-prior-deliberations-target-expansion`. Expected: no missing
  required specs and no blocking gaps.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`,
  `ADR-DA-READ-SURFACE-PLACEMENT-001`, and `DCL-CONCEPT-ON-CONTACT-001`: run
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest
  platform_tests/skills/test_verify_prior_deliberations_pre_population.py -q
  --tb=short`. Expected: verdict-body Prior-Deliberations seeding uses the
  shared primitive, places content in the correct section, and writes the
  verify-namespaced audit log.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` and adapter parity: run
  `groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py
  --check --update-registry` before and after the implementation write mode as
  appropriate. Expected after implementation: the three touched Codex skill
  adapters, `.codex/skills/MANIFEST.json`, and
  `config/agent-control/harness-capability-registry.toml` are fresh.
- Path-load and helper-regression coverage: run
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest
  platform_tests/skills/test_bridge_propose_helper.py
  platform_tests/skills/test_bridge_revise_helper.py
  platform_tests/skills/test_bridge_impl_report_helper.py
  platform_tests/skills/test_verify_prior_deliberations_pre_population.py -q
  --tb=short`. Expected: existing proposal/revision/report helpers still load
  the re-exported shared prior-deliberations primitive.
- Scaffold/golden parity: run
  `groundtruth-kb/.venv/Scripts/python.exe scripts/_capture_scaffold_golden.py`
  and then
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest
  groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py -q
  --tb=short`. Expected: scaffold golden files are updated only as generated
  consequences of the approved target paths.
- Code quality: run `groundtruth-kb/.venv/Scripts/python.exe -m ruff check` and
  `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check` over the
  changed Python paths. Expected: both separate gates pass.

## Risk / Rollback

Primary risk is scope creep: this expansion must not become a broad skill
registry cleanup or LLM-harness `.lo-verdict.md` repair. The implementation is
limited to completing the already-approved WI-4639 interactive-verdict path and
the generated Codex manifest/registry metadata required to make that path pass
parity tests. `WI-4648` remains the follow-on for LLM-harness verdict files.

Rollback is a normal revert of the implementation commit plus any generated
adapter/registry outputs from that commit. No MemBase mutation, deployment,
credential change, or out-of-root artifact is in scope.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-verdict-prior-deliberations-target-expansion`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — this proposal repairs the incomplete target-path envelope that blocks
completion of the already-approved WI-4639 feature implementation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
