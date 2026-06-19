NEW
author_identity: codex-loyal-opposition
author_harness_id: A
author_session_context_id: codex-lo-verified-commit-finalization-proposal-2026-06-19
author_model: GPT-5
author_model_version: GPT-5 Codex desktop
author_model_configuration: Codex desktop API session, owner-declared Loyal Opposition

# Implementation Proposal: VERIFIED verdict commit-finalization gate

Document: gtkb-verified-verdict-commit-finalization-gate
Version: 001
Bridge Kind: implementation_proposal
Project: PROJECT-MAY29-HYGIENE
Project Authorization: PAUTH-PROJECT-MAY29-HYGIENE-WI-4674-VERIFIED-COMMIT-FINALIZATION
Work Item: WI-4674
Status: NEW

## Summary

Change LO verification handling so a `VERIFIED` verdict is not a durable terminal result until the verified implementation payload and the `VERIFIED` verdict are committed together in the same local commit.

This makes the local commit the final step of verification, not a post-verification best-effort cleanup task. If a harness cannot create that commit, it must not file a terminal `VERIFIED` verdict for the implementation. It must instead file a non-terminal blocker report, `NO-GO`, or an explicitly scoped finalization proposal as appropriate.

## Owner Directive

Mike's 2026-06-19 directive:

> We need to change the way LO handles VERIFIED verdicts to ensure that the VERIFIED work is committed at the same time the verdict is recorded. In essence: the commit should be the final step for VERIFICATION, not a post-verification, best-effort action.

## Problem Statement

Current LO procedure allows an implementation report to receive `VERIFIED` before the corresponding local commit exists. That leaves a terminal bridge record claiming completion while the repository still depends on later staging or owner/manual cleanup.

Recent bridge evidence shows the failure mode clearly:

- `bridge/gtkb-wi4676-verified-finalization-004.md` VERIFIED an accurate blocker report after all verification commands passed, but the implementation remained uncommitted because the sandbox could not create `.git/index.lock`.
- `bridge/gtkb-wi4678-verified-finalization-004.md` did the same for WI-4678.
- `bridge/gtkb-wi4678-git-write-finalization-003.md` repeated the same Git-write blocker.
- WI-4383 shows the successful precedent: the verified milestone finalization was not retired until finalization commits existed.

The protocol should make the successful precedent normative and prevent the recurring "terminal VERIFIED, uncommitted payload" drift.

## Scope

Implement a narrow procedural and generated-adapter rule change:

1. Amend the file bridge protocol to define a mandatory `VERIFIED` commit-finalization gate.
2. Amend the canonical `/verify` and `/bridge` skill procedures so LO drafts the verdict, verifies the exact staged payload, stages the verdict file with the verified implementation payload, runs required gates, then creates the local commit as the final verification step.
3. Regenerate harness adapters so Codex, Antigravity, and API harness skill copies carry the same instruction.
4. Add or update focused generator/parity tests so generated adapters cannot silently drift from the canonical `.claude/skills` instructions.

Out of scope:

- Changing the substantive criteria for `GO`, `NO-GO`, or implementation correctness.
- Bypassing the implementation-start gate, bridge-compliance gate, credential scanner, or self-review prohibition.
- Pushing commits.
- Bulk committing unrelated dirty worktree changes.
- Retiring existing uncommitted historical VERIFIED drift in this slice.

## target_paths

```json
[
  ".claude/rules/file-bridge-protocol.md",
  ".claude/skills/verify/SKILL.md",
  ".claude/skills/bridge/SKILL.md",
  ".codex/skills/verify/SKILL.md",
  ".codex/skills/bridge/SKILL.md",
  ".codex/skills/MANIFEST.json",
  ".agent/skills/verify/SKILL.md",
  ".agent/skills/bridge/SKILL.md",
  ".agent/skills/MANIFEST.json",
  ".api-harness/skills/verify/SKILL.md",
  ".api-harness/skills/bridge/SKILL.md",
  ".api-harness/skills/MANIFEST.json",
  "config/agent-control/harness-capability-registry.toml",
  "scripts/generate_codex_skill_adapters.py",
  "scripts/generate_antigravity_skill_adapters.py",
  "scripts/generate_api_skill_adapters.py",
  "platform_tests/scripts/test_generate_codex_skill_adapters.py",
  "platform_tests/scripts/test_generate_antigravity_skill_adapters.py",
  "platform_tests/scripts/test_generate_api_skill_adapters.py"
]
```

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge status transitions and versioned bridge files remain authoritative.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - `VERIFIED` verdicts must be grounded in spec-derived verification evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal must cite applicable governance/specification obligations.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation remains bound to an active project authorization and bridge GO.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal remains linked to project authorization and work item.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected source/config changes must remain bridge-authorized.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact lifecycle state must not depend on invisible cleanup.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - owner requirement and recurring terminal-drift defect trigger artifact updates.
- `GOV-STANDING-BACKLOG-001` - existing WI-4674 is the backlog anchor for verification-structure enforcement.

## Prior Deliberations

- `DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE` - owner decision requiring LO to commit the verified payload and `VERIFIED` verdict together as the final verification step.
- `PAUTH-PROJECT-MAY29-HYGIENE-WI-4674-VERIFIED-COMMIT-FINALIZATION` - bounded implementation authorization for this WI-4674 rule/skill/adapter slice.
- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` - prior milestone finalization precedent preserved bridge GO/VERIFIED gates, local milestone commits, and no push unless separately directed.
- `bridge/gtkb-ollama-phase2-verified-staging-finalization-gate-004.md` - successful verified-finalization example that checked the finalization commit path.
- `bridge/gtkb-wi4676-verified-finalization-004.md` - negative precedent showing a terminal VERIFIED blocker while the implementation payload remained uncommitted.
- `bridge/gtkb-wi4678-verified-finalization-004.md` - same negative precedent for WI-4678.
- `bridge/gtkb-wi4678-git-write-finalization-003.md` - repeated finalization blocker demonstrating that Git-write failure must prevent terminal implementation verification, not trail it.

## Proposed Rule Text

Add a section to `.claude/rules/file-bridge-protocol.md` equivalent to:

```text
Mandatory VERIFIED Commit-Finalization Gate

A Loyal Opposition `VERIFIED` verdict for an implementation report is terminal only when the local commit that contains the verified implementation payload also contains the `VERIFIED` verdict file. The commit is the final verification step.

Before writing a terminal `VERIFIED` verdict, LO must draft the verdict, confirm the exact file set to be committed, stage only the verified implementation payload and the verdict file, run required staged/credential/governance checks, and create the local commit. The verdict must report the commit hash and exact staged path set.

If the commit cannot be created, LO must not file terminal `VERIFIED` for the implementation. The proper outcome is a non-terminal blocker report, `NO-GO`, or a separate finalization proposal, depending on the failure. A `VERIFIED` blocker report may verify the accuracy of a blocker report, but it must not be represented as completing the underlying implementation.
```

Exact wording may be refined during implementation as long as the above semantics are preserved.

## Implementation Plan

1. Acquire a work-intent claim and implementation authorization packet after this proposal receives GO.
2. Patch `.claude/rules/file-bridge-protocol.md` with the mandatory commit-finalization gate.
3. Patch `.claude/skills/verify/SKILL.md` so `/verify` requires:
   - draft the `VERIFIED` verdict outside `bridge/`;
   - inspect the implementation diff and target paths;
   - stage only the verified implementation payload plus the new `VERIFIED` verdict;
   - run required staged credential/governance checks;
   - create the local commit as the final step;
   - include the commit hash and exact committed path list in the verdict.
4. Patch `.claude/skills/bridge/SKILL.md` so broader bridge operation points verification authors back to the same gate.
5. Run all three adapter generators:
   - `python scripts/generate_codex_skill_adapters.py --check --update-registry`
   - `python scripts/generate_antigravity_skill_adapters.py --check --update-registry`
   - `python scripts/generate_api_skill_adapters.py --check --update-registry`
6. Update generator/parity tests only if needed to lock the new instruction into generated adapter outputs.
7. Run focused tests and preflights.
8. File a post-implementation report. LO verification of that report must follow the new rule: the implementation payload and `VERIFIED` verdict must be committed together.

## Acceptance Criteria

- `file-bridge-protocol.md` states that a terminal implementation `VERIFIED` verdict is not complete until the same local commit contains both the verified payload and the verdict file.
- `/verify` procedure makes local commit creation the final required verification step for implementation reports.
- `/bridge` procedure does not preserve or imply a post-verification best-effort commit path.
- Generated `.codex`, `.agent`, and `.api-harness` skill adapters contain the new rule.
- Harness capability registry and manifests remain current after generator runs.
- Focused generator/parity tests pass.
- The post-implementation report includes command output proving adapter generation/checks and tests passed.

## Verification Plan

Run:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-verified-verdict-commit-finalization-gate --content-file bridge\gtkb-verified-verdict-commit-finalization-gate-001.md
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-verified-verdict-commit-finalization-gate --content-file bridge\gtkb-verified-verdict-commit-finalization-gate-001.md
python scripts\generate_codex_skill_adapters.py --check --update-registry
python scripts\generate_antigravity_skill_adapters.py --check --update-registry
python scripts\generate_api_skill_adapters.py --check --update-registry
python -m pytest platform_tests\scripts\test_generate_codex_skill_adapters.py platform_tests\scripts\test_generate_antigravity_skill_adapters.py platform_tests\scripts\test_generate_api_skill_adapters.py -q --tb=short
rg -n "VERIFIED.*commit|commit-finalization|Commit-Finalization|final verification step" .claude\rules\file-bridge-protocol.md .claude\skills\verify\SKILL.md .claude\skills\bridge\SKILL.md .codex\skills\verify\SKILL.md .codex\skills\bridge\SKILL.md .agent\skills\verify\SKILL.md .agent\skills\bridge\SKILL.md .api-harness\skills\verify\SKILL.md .api-harness\skills\bridge\SKILL.md
```

Before any commit:

```powershell
git diff --cached --name-only
python scripts\check_protected_commit_authorization.py --staged
git diff --cached --check
```

## Risk And Mitigation

Risk: LO cannot create the final commit in some sandbox contexts. Mitigation: the new rule makes that state explicit and non-terminal; affected harnesses must file a blocker or route finalization to a Git-write-capable context instead of closing the implementation as VERIFIED.

Risk: Generated adapter drift leaves one harness using old instructions. Mitigation: run all three generator paths and focused generator tests.

Risk: Existing uncommitted VERIFIED drift remains. Mitigation: this proposal prevents new drift; existing drift remains out of scope and should be handled by separate finalization bridges or sweep-commit work that preserves exact path ownership.

## Rollback Plan

If the rule proves too broad, revert the protocol and skill changes through a new bridge proposal. Since this slice is documentation/procedure and generated adapter parity, rollback is a local commit reverting the affected protocol, skill, adapter, registry, and test files.

## Owner Decision Needed

None. The owner directive is explicit and this proposal routes it through the existing bridge governance and WI-4674 backlog anchor.
