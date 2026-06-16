NEW

author_identity: Antigravity Prime Builder
author_harness_id: C
author_session_context_id: S375-gtkb-skill-generator-registry-formatting
author_model: Gemini 3.1 Pro High
author_model_version: gemini-3.1-pro-high
author_model_configuration: Antigravity desktop session environment

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-WI-4611-AND-WI-4612-DEFECT-FIXES
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4612

# Implementation Proposal - Codex and Antigravity skill adapter generators should converge registry formatting

## Claim

This proposal implements the fix for WI-4612 by converging the TOML formatting behavior of `scripts/generate_codex_skill_adapters.py` and `scripts/generate_antigravity_skill_adapters.py` when writing to `config/agent-control/harness-capability-registry.toml`. Currently, the Codex generator inserts separator formatting which the Antigravity generator then strips, causing them to fight over the layout and producing drift. This implementation will ensure both generators use a unified TOML formatting rule.

## Defect / Reproduction

During no-index skill-template verification, `scripts/generate_codex_skill_adapters.py --check --update-registry` passed only after inserting separator formatting. The Antigravity generator then strips that formatting. This causes constant false-positive changes and conflicts in `harness-capability-registry.toml`.

## Target Paths

```json
{
  "target_paths": [
    "scripts/generate_codex_skill_adapters.py",
    "scripts/generate_antigravity_skill_adapters.py",
    "platform_tests/scripts/test_generate_codex_skill_adapters.py",
    "platform_tests/scripts/test_generate_antigravity_skill_adapters.py"
  ]
}
```

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Proposal filed on the file bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This section explicitly links specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Tests derived from specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project linkage in the header block.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All target paths are within root.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (Advisory) - Modifying canonical skill representation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (Advisory) - Generation updates for skill adapters.

## Prior Deliberations

<!-- Pre-populated by helper; review and prune. -->
- No prior deliberations related directly to TOML formatting convergence in skill adapter generation.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-20260606-SWEEP-COMMIT-SKILL-PARITY-REGISTRATION` — seed=search; owner_conversation; Proceed with sweep-commit skill parity registration
- DA: `DELIB-1211` — seed=search; bridge_thread; Bridge thread: gtkb-operational-skills-tier-a (8 versions, ORPHAN)
- DA: `DELIB-20261030` — seed=search; lo_review; GT-KB Skills Guidance Compliance Advisory
- DA: `DELIB-20261872` — seed=search; bridge_thread; Bridge thread: gtkb-skill-modernization-slice-0-skill-health-checker (4 versions
- DA: `DELIB-0739` — seed=search; bridge_thread; Bridge thread: gtkb-operational-skills-tier-a (8 versions, VERIFIED)

## Owner Decisions / Input

- `DELIB-20260616-MAY29-HYGIENE-AUTHORIZATION` - Owner decision authorizing the defect fix for `WI-4612` under project authorization.

## Proposed Scope

### 1. Converge TOML Formatting

Update both scripts to use a unified `tomli_w` or `toml` library dumping approach or string formatting that preserves consistent blank lines between sections. Ensure neither script introduces a formatting change that the other would undo.

### 2. Update Tests

Update the respective `platform_tests` to verify that repeated sequential executions of both generators against the registry do not produce any uncommitted diffs in the registry file.

## Specification-Derived Verification Plan

| Specification | Target Test / Manual Verification |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Protocol path: NEW proposal -> LO Review -> GO -> Implementation -> Post-Impl -> VERIFIED |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute both generators with `--update-registry` in sequence. Verify `git diff` on the registry file is empty after the second run. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify `git diff --cached --name-only` shows changes only inside root directory. |

## Acceptance Criteria

1. Running `generate_codex_skill_adapters.py --update-registry` followed by `generate_antigravity_skill_adapters.py --update-registry` produces no formatting-only changes in the registry.
2. The Pytest test suites for both generator scripts pass cleanly.
3. The registry file `harness-capability-registry.toml` remains syntactically valid TOML.

## Risks / Rollback

- **Risk**: Very low risk. The change only affects formatting of a configuration file.
- **Rollback**: `git checkout HEAD -- scripts/`

## Recommended Commit Type

`fix`
