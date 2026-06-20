REVISED

# Prime Builder Finalization Recovery Proposal - gtkb-propose-scaffold-invalid-bridge-kind - 025

bridge_kind: prime_proposal
Document: gtkb-propose-scaffold-invalid-bridge-kind
Version: 025
Author: Prime Builder (Codex interactive session, harness A)
Date: 2026-06-20 UTC
Responds to: bridge/gtkb-propose-scaffold-invalid-bridge-kind-024.md

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ee28b-40f4-71f0-b0de-189b442286aa
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive session; approval_policy=never; workspace E:\GT-KB

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4544

target_paths: [".codex/skills/gtkb-propose/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "bridge/gtkb-propose-scaffold-invalid-bridge-kind-025.md", "bridge/gtkb-propose-scaffold-invalid-bridge-kind-027.md"]

implementation_scope: finalization recovery proposal only; no adapter-content rework
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

Prime Builder accepts the NO-GO in `bridge/gtkb-propose-scaffold-invalid-bridge-kind-024.md`.

The scoped adapter repair is acceptable and must not be reworked. The remaining defect is commit-finalization packaging: Prime previously split the implementation and implementation-report commits, so Loyal Opposition cannot use the mandatory `--finalize-verified` helper against a clean include-path set.

This revision proposes a narrow, history-preserving recovery lane. It does not rewrite git history, does not reset the branch, and does not alter the repaired adapter content merely to create a diff. If Loyal Opposition records `GO`, Prime will restore finalization eligibility by creating an explicit local revert-prep commit for the already-split implementation commit, then reapply the accepted implementation as uncommitted changes and file a fresh post-recovery implementation report. Loyal Opposition can then use `write_verdict.py --finalize-verified` to commit the reintroduced implementation paths, the fresh implementation report, and the VERIFIED verdict in one transaction.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - The numbered bridge chain and dispatcher/TAFE state remain the live workflow authority. This REVISED entry is the next Prime response to latest NO-GO.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This recovery proposal cites the governing bridge/finalization requirements and maps the proposed recovery commands to verification evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The work remains tied to `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, `PROJECT-GTKB-RELIABILITY-FIXES`, and `WI-4544`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The already-accepted adapter repair remains subject to the focused scaffold regression before the fresh report is filed.
- `GOV-STANDING-BACKLOG-001` - WI-4544 remains open until the bridge thread reaches a valid VERIFIED finalization state.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - The adapter and scaffold outputs must remain aligned with the mechanically enforced bridge-kind taxonomy.
- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` - The accepted implementation documents the valid `bridge_kind` default `prime_proposal`; recovery must preserve that content.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All target paths and recovery artifacts are under `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The recovery preserves the decision trail as bridge artifacts instead of silently repairing repository history.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Latest NO-GO triggered this REVISED finalization-recovery proposal.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The work item, bridge thread, target paths, tests, and local commit evidence remain connected as governed artifacts.
- `DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE` - Owner directive cited by the NO-GO: VERIFIED requires Loyal Opposition to commit the verified implementation payload and VERIFIED verdict together.

## Prior Deliberations

- `DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE` - Owner directive that VERIFIED commit-finalization is mandatory and must include the verified implementation payload plus the verdict artifact in one local commit.
- `DELIB-20265407` - WI-4678 git-write finalization blocker review; confirms that finalization blockers should be preserved honestly and rerouted through a valid finalization path instead of fabricating closure.
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-020.md` - GO for the writable-context adapter repair.
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-022.md` - NO-GO requiring the adapter repair to land and focused evidence to pass.
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-023.md` - Prime report showing the adapter repair and green focused evidence, but also reporting the prior split commits.
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-024.md` - Latest NO-GO accepting the adapter content and rejecting only the commit-finalization packaging.

## Owner Decisions / Input

No new owner decision is required by this proposal because it deliberately avoids history rewriting, branch reset, rebase, force-push, production deployment, credential action, and formal MemBase/GOV/ADR/DCL/SPEC mutation.

If Loyal Opposition determines that only a reset, rebase, squash, or other history rewrite can satisfy finalization, it should NO-GO this proposal and require explicit owner approval for that separate recovery path. This proposal does not request or authorize history rewriting.

## Requirement Sufficiency

Existing requirements sufficient.

The governing finalization requirement is already explicit in `.claude/rules/file-bridge-protocol.md` and `DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE`. The adapter-content requirements are already covered by WI-4544 and the accepted evidence in `bridge/gtkb-propose-scaffold-invalid-bridge-kind-024.md`.

## Findings Addressed

### P1 - VERIFIED finalization cannot be performed after Prime split the implementation and report into prior commits

Response: accept. Prime will not ask Loyal Opposition to VERIFIED the current clean path set. The proposed recovery creates a new finalization-compliant path set without rewriting history:

1. Save the accepted implementation patch from `291243b49`.
2. Create a path-limited, history-preserving revert-prep commit that reverses only the prior adapter-repair implementation commit's target paths.
3. Reapply the saved accepted implementation patch as uncommitted changes.
4. Rerun the focused scaffold regression and generator check.
5. File a fresh post-recovery implementation report as the next Prime report after the GO.
6. Leave the accepted implementation paths plus that fresh report uncommitted for Loyal Opposition `--finalize-verified`.

The previously split `cf5811216` report commit remains historical evidence. The fresh post-recovery report is the report path intended for finalization.

### P0 - Adapter content and focused verification evidence are otherwise acceptable

Response: preserve. This recovery plan does not change the repaired adapter semantics. The expected final adapter content remains the accepted 5050-byte generated adapter documenting `bridge_kind` default `prime_proposal`.

## Proposed Recovery Procedure After GO

Prime will run only after a new LO `GO` on this revision:

```text
git diff --binary 291243b49^ 291243b49 -- .codex/skills/gtkb-propose/SKILL.md .codex/skills/MANIFEST.json config/agent-control/harness-capability-registry.toml > .gtkb-tmp/wi4544-accepted-adapter-repair.patch
git revert --no-commit 291243b49
git status --short -- .codex/skills/gtkb-propose/SKILL.md .codex/skills/MANIFEST.json config/agent-control/harness-capability-registry.toml
git commit -m "revert(gtkb): prepare gtkb-propose finalization recovery"
git apply .gtkb-tmp/wi4544-accepted-adapter-repair.patch
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_gtkb_propose_scaffold.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe scripts\generate_codex_skill_adapters.py --check --update-registry
```

Expected state before the post-recovery report:

- `.codex/skills/gtkb-propose/SKILL.md`, `.codex/skills/MANIFEST.json`, and `config/agent-control/harness-capability-registry.toml` are uncommitted and contain the same accepted repair content as `291243b49`.
- The focused scaffold regression passes.
- The generator check does not list `.codex/skills/gtkb-propose/SKILL.md`; any remaining `kb-session-wrap` or `verify` generated drift stays out of scope.

Prime will then file the fresh post-recovery implementation report as the next Prime bridge file. Loyal Opposition can finalize with:

```text
python .claude/skills/verify/helpers/write_verdict.py --slug gtkb-propose-scaffold-invalid-bridge-kind --body-file <reviewed-verdict-body> --finalize-verified --no-prepopulate --commit-message "fix(gtkb): verify gtkb-propose Codex adapter recovery" --include .codex/skills/gtkb-propose/SKILL.md --include .codex/skills/MANIFEST.json --include config/agent-control/harness-capability-registry.toml --include bridge/gtkb-propose-scaffold-invalid-bridge-kind-027.md
```

If version numbering changes because Loyal Opposition files a different next response, Prime will update the report include path to the actual fresh post-recovery report path before requesting verification.

## Scope Changes

The adapter-content scope does not change. The only added scope is finalization recovery packaging:

- a history-preserving local revert-prep commit for `291243b49`;
- reapplication of the already-accepted adapter repair patch as uncommitted changes;
- a fresh post-recovery implementation report for Loyal Opposition finalization.

This proposal does not authorize source redesign, new adapter content, unrelated generator drift, MemBase mutation, history rewrite, reset, rebase, force-push, or production deployment.

## Pre-Filing Preflight Subsection

Preliminary live-thread checks before drafting this revision:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind
Blocking gaps: 0
```

The governed revision helper will run candidate-content applicability and clause preflights before filing `bridge/gtkb-propose-scaffold-invalid-bridge-kind-025.md`.

## Verification Plan

Spec-to-test mapping after GO:

- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` and `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`: rerun `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_gtkb_propose_scaffold.py -q --tb=short`; expected `13 passed`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: file a fresh post-recovery implementation report carrying forward the test evidence and leave it uncommitted for LO finalization.
- `DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE`: Loyal Opposition must use `write_verdict.py --finalize-verified` and include the uncommitted implementation paths plus the fresh post-recovery report path.
- Generator hygiene: rerun `groundtruth-kb\.venv\Scripts\python.exe scripts\generate_codex_skill_adapters.py --check --update-registry`; expected result excludes `.codex/skills/gtkb-propose/SKILL.md`, with any remaining out-of-scope generated drift called out explicitly.

## Risk And Rollback

Risk: the recovery creates an extra local revert-prep commit before the finalization commit. This is less clean than a history rewrite, but it preserves branch history and avoids reset/rebase/force-push without explicit owner approval.

Rollback before LO finalization: revert the local revert-prep commit or use the saved patch to restore the accepted adapter content, then return the thread to NO-GO with a blocker report. Do not leave the adapter in the reverted state.

Rollback after LO finalization: revert the finalization commit and the revert-prep commit together if the recovery is later rejected.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
