REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-16T17-22-46Z-prime-builder-A-b4aaec
author_model: gpt-5-codex
author_model_version: 2026-06-16 runtime
author_model_configuration: Codex bridge auto-dispatch session; Prime Builder

# Revised Scope Proposal - No-Index Skill, Template, And Documentation Cleanout

bridge_kind: prime_proposal
Document: gtkb-no-index-skill-template-doc-cleanout
Version: 007
Responds-To: bridge/gtkb-no-index-skill-template-doc-cleanout-006.md
Prior Report: bridge/gtkb-no-index-skill-template-doc-cleanout-005.md
Prior GO: bridge/gtkb-no-index-skill-template-doc-cleanout-004.md
Prior Proposal: bridge/gtkb-no-index-skill-template-doc-cleanout-003.md
Author: Prime Builder (Codex, harness A)
Date: 2026-06-16 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: [".claude/skills/bridge-propose/**", ".claude/skills/bridge/**", ".claude/skills/bridge-config/**", ".claude/skills/verify/**", ".claude/skills/gtkb-propose/**", ".claude/skills/send-review/**", ".claude/skills/kb-session-wrap/**", ".claude/skills/gtkb-hygiene-investigation/**", ".claude/skills/gtkb-hygiene-sweep/**", ".claude/skills/loyal-opposition-hygiene-assessment/**", ".claude/skills/projects/**", ".codex/skills/**", ".agent/skills/**", ".api-harness/skills/**", "config/agent-control/harness-capability-registry.toml", "scripts/check_skill_health.py", "platform_tests/scripts/test_check_skill_health.py", "platform_tests/scripts/test_check_harness_parity.py", "platform_tests/skills/**", "groundtruth-kb/templates/skills/**", "groundtruth-kb/templates/rules/**", "groundtruth-kb/templates/project/**", "groundtruth-kb/templates/hooks/**", "groundtruth-kb/templates/BRIDGE-INVENTORY.md", "groundtruth-kb/tests/fixtures/scaffold_golden/**", "README.md", "CONTRIBUTING.md", "CHANGELOG.md", "docs/gtkb-systems-and-tools.md", "applications/Agent_Red/docs/gtkb-systems-and-tools.md", "bridge/gtkb-no-index-skill-template-doc-cleanout-*.md"]

implementation_scope: skill_template_doc_no_index_cleanup_revised_parity_scope
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This REVISED entry responds to the Loyal Opposition NO-GO in
`bridge/gtkb-no-index-skill-template-doc-cleanout-006.md` by correcting the
approved scope before any further protected implementation work is attempted.

The NO-GO identified two blockers:

1. An out-of-scope protected registry diff.
2. A required skill/parity verification lane that still failed live.

The first blocker is now resolved by the separate verified bridge thread
`bridge/gtkb-harness-capability-registry-drift-disposition-004.md`: the
registry diff is clean in the current checkout. The second blocker remains
live. A fresh rerun with a workspace temp base completed with `88 passed,
18 failed`:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp=.gtkb-state\pytest-no-index-skill-template-doc-cleanout-20260616T1729 platform_tests\scripts\test_check_harness_parity.py platform_tests\scripts\test_check_skill_health.py platform_tests\skills -q --tb=short --maxfail=30
```

The failures show that the previous target set was insufficient. Passing the
required lane now requires coordinated updates to generated adapter/registry
parity, the skill-health checker/test fixture, and platform skill helper tests
that still encode retired `bridge/INDEX.md` mutation assumptions.

This revision does not claim implementation. It asks Loyal Opposition to
approve the expanded scope needed to make the required verification lane pass
without treating the failures as an implicit follow-on.

## Findings Addressed

### F1 - Out-of-scope protected registry drift remains after implementation

Response: resolved as a dependency before this revised proposal. The dedicated
registry-disposition bridge reached `VERIFIED` at
`bridge/gtkb-harness-capability-registry-drift-disposition-004.md`, and live
inspection now shows no staged or unstaged diff for
`config/agent-control/harness-capability-registry.toml`.

The registry remains in this revised target path set because the required
adapter generator workflow may need to update registry hashes and declare the
`bridge-config` skill. Any such registry change must occur only after this
revised scope receives `GO` and a fresh implementation-start packet.

### F2 - Required platform skill/parity verification still fails

Response: scope is revised so Prime Builder can fix the failing verification
lane rather than deferring it. Current failures fall into four concrete groups:

- `test_repository_registry_covers_project_skills` reports
  `.claude/skills/bridge-config/SKILL.md` as an undeclared project skill.
- `test_codex_skill_adapter_parity_check`,
  `test_codex_adapter_body_matches_canonical_normalized_sha`, and
  `test_manifest_entry_present` report generated adapter/manifest/registry
  drift.
- `test_detects_direct_index_write_instruction` and
  `test_skill_documents_no_index_mutation` still encode retired-index
  expectations that conflict with the no-index direction.
- Bridge revise/implementation-report helper tests still assert index-era
  helper functions such as `insert_index_status` and `validate_transition`.

The expanded target set includes the affected skill sources, generated
adapters/manifests, registry file, skill-health checker, and platform skill
tests needed to bring the verification lane to a clean result.

## Prior Deliberations

- `DELIB-20263438` - owner requirement for corrected bridge-dispatch
  architecture and no role/dispatchability conflation.
- `DELIB-20261030` - GT-KB skills guidance compliance advisory.
- `DELIB-20261027` - GT-KB skill use, coverage, and enforcement advisory.
- `DELIB-2639` - prior LO finding that generated Codex skill adapter metadata
  and registry changes must be in target scope when adapter regeneration can
  touch them.
- `DELIB-1555` - prior LO finding that bridge skill/helper changes must include
  parity/template scope and generator checks.
- `DELIB-1967` and `DELIB-2173` - prior verified bridge-propose helper index
  parity threads; now relevant as historical context being superseded by the
  no-index bridge model.
- `bridge/gtkb-no-index-runtime-tooling-cleanout-006.md` - verified sibling
  thread for runtime tooling no-index cleanup.
- `bridge/gtkb-no-index-dispatcher-trigger-cleanout-007.md` - verified sibling
  thread for dispatcher/trigger no-index cleanup.
- `bridge/gtkb-harness-capability-registry-drift-disposition-004.md` -
  verified dependency resolving the prior protected registry drift.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation must proceed
  through GO plus a live work-intent claim and implementation-start packet.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge lifecycle remains governed by
  proposal/review/report/verification files.
- `GOV-FILE-BRIDGE-PROTOCOL-001` - versioned bridge files and dispatcher/TAFE
  state are the live bridge workflow surfaces; the retired index must not be
  recreated.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision includes
  project authorization, project, work item, and machine-readable target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the revised scope
  links all governing requirements before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map the
  linked requirements to executed tests and observed results.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher/status/health and
  harness registry surfaces are dispatch topology authorities.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - routing and actionability are based on
  role, subject, and activity rules, not an index compatibility file.
- `REQ-HARNESS-REGISTRY-001` - harness capability registry entries and hashes
  must be intentional and consistent with generated adapter surfaces.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - harness capability surfaces must be
  complete and parity-checkable.
- `GOV-AGENT-INSTRUCTION-SURFACE-CONSISTENCY-001` - active agent-facing
  instructions must not teach contradictory current authority.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - cross-harness skill and hook surfaces
  must be corrected consistently.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must self-enforce bridge scope
  and preserve hook/adapter parity evidence when native interception is not
  sufficient by itself.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Agent Red local documentation
  remains in scope only as an in-root adopter documentation surface.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable instruction and test
  artifacts should be corrected rather than leaving stale behavior implicit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - retired-index references and tests are
  lifecycle-triggered stale artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable artifact cleanup and
  historical labeling remain explicit.

## Requirement Sufficiency

Existing requirements are sufficient. Mike's no-backward-compatibility
direction for `bridge/INDEX.md`, WI-4578 project authorization, and the linked
bridge/governance/harness parity requirements are enough to authorize this
revised implementation scope once Loyal Opposition records `GO`.

No new owner decision is required. This auto-dispatched Prime Builder session
cannot interactively request owner input; no waiver is being requested.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI` -
  active project authorization for WI-4578 dispatch orthogonality and
  bridge/config/status CLI work.
- `DELIB-20263438` - owner requirement for corrected bridge-dispatch
  architecture and no role/dispatchability conflation.
- No new owner decision, waiver, deployment approval, credential action, or
  formal artifact mutation is requested by this revision.

## Proposed Implementation After GO

1. Begin a fresh implementation-start packet for
   `gtkb-no-index-skill-template-doc-cleanout` after this REVISED entry receives
   GO.
2. Update active skill instructions and helper tests so no current instruction
   or positive test requires `bridge/INDEX.md`; retain only explicitly
   historical, prohibited, or negative-test references.
3. Update `scripts/check_skill_health.py` and its tests so the checker detects
   direct retired-index mutation instructions while the test fixture no longer
   requires a current skill document to mention the retired file.
4. Update bridge revise and implementation-report helper tests to validate the
   current no-index writer/dispatcher behavior rather than removed
   `insert_index_status` and `validate_transition` internals.
5. Regenerate Codex and Antigravity skill adapters/manifests through the
   established generators and update
   `config/agent-control/harness-capability-registry.toml` only to the extent
   needed for generated adapter/registry parity.
6. If generator output requires files outside the revised `target_paths`, stop
   and file another bridge revision before touching those files.

## Spec-Derived Verification Plan

Run:

```powershell
Test-Path bridge\INDEX.md
git diff --name-only -- config/agent-control/harness-capability-registry.toml
git diff --cached --name-only -- config/agent-control/harness-capability-registry.toml
python scripts\generate_codex_skill_adapters.py --check --update-registry
python scripts\generate_antigravity_skill_adapters.py --check --update-registry
python scripts\check_harness_parity.py --harness codex --all --json
python scripts\check_harness_parity.py --harness antigravity --all --json
groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp=.gtkb-state\pytest-no-index-skill-template-doc-cleanout-verification platform_tests\scripts\test_check_harness_parity.py platform_tests\scripts\test_check_skill_health.py platform_tests\skills -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_scaffold_smoke.py groundtruth-kb\tests\test_scaffold_bridge_index.py groundtruth-kb\tests\test_scaffold_consumes_resolver.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\check_skill_health.py platform_tests\scripts\test_check_skill_health.py platform_tests\scripts\test_check_harness_parity.py platform_tests\skills
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\check_skill_health.py platform_tests\scripts\test_check_skill_health.py platform_tests\scripts\test_check_harness_parity.py platform_tests\skills
```

Expected:

- `Test-Path bridge\INDEX.md` returns `False`.
- Registry staged/unstaged diff is either clean or exactly the intentional
  generator/registry update authorized by this revised scope.
- Codex and Antigravity adapter generator checks pass.
- Codex and Antigravity harness parity checks report no stale generated skill
  adapters and no undeclared `bridge-config` project skill.
- The platform skill/parity pytest lane passes with a workspace `--basetemp`.
- Scaffold tests pass.
- Ruff lint and format checks pass for Python files touched in this revised
  scope.
- Remaining `bridge/INDEX.md` mentions in the target set are explicitly
  historical, prohibited, or negative-test references.

## Risk And Rollback

Risk: the adapter generators may surface stale canonical skill changes from
parallel bridge work. Mitigation: the revised target set includes the currently
staged skill surfaces and generated harness adapters needed for parity; if a
new out-of-scope file appears, stop and revise again before mutation.

Risk: updating broad generated adapter sets can obscure which canonical skill
change caused each generated diff. Mitigation: implementation must report exact
generator output, final changed-file list, and source-to-adapter mapping.

Rollback: revert only files changed under the revised target paths and file the
next bridge report or revision. Do not recreate `bridge/INDEX.md`.

## Pre-Filing Preflight

Commands:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-no-index-skill-template-doc-cleanout --content-file .gtkb-state\bridge-revisions\drafts\gtkb-no-index-skill-template-doc-cleanout-007.md --json
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-no-index-skill-template-doc-cleanout --content-file .gtkb-state\bridge-revisions\drafts\gtkb-no-index-skill-template-doc-cleanout-007.md
```

Applicability preflight observed:

- packet_hash: `sha256:b7edb54260b69ad7d6f288250b36955fd02969cb0e545c625085457c95ad6aaf`
- content_source: `pending_content`
- content_file: `.gtkb-state/bridge-revisions/drafts/gtkb-no-index-skill-template-doc-cleanout-007.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- warnings.missing_parent_dirs: `[]`

ADR/DCL clause preflight observed:

- Clauses evaluated: `5`
- must_apply: `4`
- may_apply: `1`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

The live filing helper must re-run these gates and refuse publication if the
candidate content changes into a blocking state.

## Recommended Commit Type

Recommended commit type: `fix:`

Rationale: this revision repairs a failed verification lane and stale
retired-index behavior in active skill/test/checker surfaces. The work is not a
new feature; it makes the approved no-index bridge behavior testable and
consistent.
