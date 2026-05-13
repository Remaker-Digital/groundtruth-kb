REVISED

# Formal Artifact Approval Hook False Positive Fix

target_paths: [".claude/hooks/formal-artifact-approval-gate.py", "platform_tests/hooks/test_formal_artifact_approval_gate.py"]
Recommended commit type: fix:

## Revision Notes

Revision 2 is metadata-only. It changes the `Requirement Sufficiency` operative phrase to the exact machine-readable form required by `scripts/implementation_authorization.py`: `Existing requirements sufficient`.

## Claim

Correct the formal-artifact approval PreToolUse hook so it gates actual formal artifact mutation commands without blocking read-only harvester help/dry-run inspection or unrelated session-prompt handoff text that merely mentions a gated script name.

The current hook overmatches raw command text. It treats any command containing `scripts/harvest_session_deliberations.py` as a formal mutation, even when the command is `--help`, and it also blocks a `KnowledgeDB.insert_session_prompt(...)` handoff when the prompt text mentions that script path. This prevents normal wrap-up and diagnostic work without protecting an actual formal artifact write.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` - the hook must preserve strict approval evidence for formal GOV/SPEC/PB/ADR/DCL/DELIB mutations.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - the hook is the enforcement surface for native-format approval evidence before canonical formal-artifact persistence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - this correction preserves artifact-oriented development by preventing governance tooling from blocking unrelated supporting-record work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the fix affects blocked/supporting lifecycle behavior around session wrap-up and verification handoff.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner-visible artifact governance remains intact while the false-positive supporting-record path is narrowed.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is governed by live `bridge/INDEX.md` and the append-only bridge protocol.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this implementation proposal cites the governing specifications before implementation approval.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must execute tests derived from the linked specifications.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001` require strict gating of formal artifact mutations; they do not require blocking read-only help, dry-run diagnostics, or supporting-record handoff text that contains a script name. No new or revised requirement is needed before this implementation.

## Owner Decisions / Input

- Owner directive in current session: "This hook needs to be corrected."
- Scope interpretation: correct the false-positive behavior while preserving formal artifact mutation blocking. No owner decision is needed for broader policy change because this proposal does not weaken the canonical formal-artifact approval rule.

## Prior Deliberations

- `DELIB-0835` - owner decision for strict formal artifact approval and audit trail behavior; this fix preserves that strictness for actual formal mutations.
- `DELIB-1476` - prior Loyal Opposition review observed that the hook path-matches `scripts/harvest_session_deliberations.py` regardless of dry-run versus apply; relevant evidence that the overmatch existed before this incident.
- `DELIB-1475` - subsequent GO for DA harvest catch-up worked around the same broad path-match with packet sequencing; relevant precedent but not a reason to retain the overmatch for help/dry-run diagnostics.
- `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` - owner decision requiring full visibility for formal artifact capture; this fix preserves formal artifact visibility while preventing unrelated supporting-record operations from being blocked by text mentions.

## Problem Statement

The hook's mutation detector currently uses a broad `FORMAL_MUTATION_PATTERNS` entry for the harvester script name. That makes the hook fail closed on any shell command whose text contains the script name, independent of whether the command can mutate formal artifacts. In this session, that blocked `--help` inspection and blocked session-prompt insertion because the handoff text mentioned the blocked help command.

## Proposed Implementation

1. Replace the unconditional harvester-script regex with command-aware detection for known formal-artifact mutation modes.
2. Keep blocking lower-level formal mutation paths: `gt deliberations add/upsert/link`, `python -m groundtruth_kb deliberations add/upsert/link`, direct `insert_spec(...)`, `update_spec(...)`, `insert_deliberation(...)`, `upsert_deliberation_source(...)`, direct deliberation/spec SQL writes, archive record scripts, and harvester apply modes that can persist DA rows.
3. Explicitly allow read-only or diagnostic commands such as `scripts/harvest_session_deliberations.py --help` and default dry-run commands without `--apply` unless another formal mutation pattern is present.
4. Ensure a command that calls `KnowledgeDB.insert_session_prompt(...)` and merely includes `scripts/harvest_session_deliberations.py` inside prompt text is not treated as a formal artifact mutation by this hook. Session prompts are supporting records, not formal GOV/SPEC/PB/ADR/DCL/DELIB artifacts.

## Files Expected To Change

- `.claude/hooks/formal-artifact-approval-gate.py`
- `platform_tests/hooks/test_formal_artifact_approval_gate.py`

## Specification-Derived Verification Plan

- `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001`: extend `platform_tests/hooks/test_formal_artifact_approval_gate.py` to prove actual formal mutation commands still block without a packet and still allow valid manual/scoped-auto approval packets.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: prove session handoff/supporting-record text that references a formal-artifact script does not get misclassified as a formal-artifact mutation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: prove blocked diagnostic lifecycle behavior is corrected while apply-mode mutation remains blocked.
- False-positive regression: add tests proving `python scripts/harvest_session_deliberations.py --help` is not hook-blocked and a `KnowledgeDB.insert_session_prompt(...)` command whose prompt text mentions `scripts/harvest_session_deliberations.py --help` is not hook-blocked.
- Harvester mutation regression: add or preserve a test proving `python scripts/harvest_session_deliberations.py --apply` remains hook-blocked without an approval packet.
- Run `python -m pytest platform_tests/hooks/test_formal_artifact_approval_gate.py -q --tb=short`.
- Run `python -m ruff check .claude/hooks/formal-artifact-approval-gate.py platform_tests/hooks/test_formal_artifact_approval_gate.py`.
- Run `python -m ruff format --check .claude/hooks/formal-artifact-approval-gate.py platform_tests/hooks/test_formal_artifact_approval_gate.py`.

## Acceptance Criteria

- `--help` on the harvester script is not treated as a formal artifact mutation.
- Default read-only/dry-run harvester invocation without `--apply` is not blocked by the formal-artifact gate solely because of the script path.
- Harvester `--apply` remains blocked without a valid formal approval packet.
- A session-prompt insertion command that mentions the harvester script in prompt text is not blocked by this hook solely because of that mention.
- Existing direct formal artifact mutation blocking remains intact.

## Pre-Filing Preflight Self-Check

The revised `-002` proposal passed applicability preflight with no missing required or advisory specs:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-formal-artifact-approval-hook-false-positive-fix-001
```

Observed on `-002`:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `packet_hash: sha256:0a3eaca5bb4bad384ee74ff064da09f67818b5e4b9f623e1248bf7acb7d2a904`

The same substantive scope is carried forward in this metadata-only revision.

## Risk / Rollback

Risk is under-blocking a real formal artifact mutation. Mitigation is to make the allow-list narrow and only exempt explicit read-only modes while retaining existing direct mutation and apply-mode coverage. Rollback is reverting `.claude/hooks/formal-artifact-approval-gate.py` and `platform_tests/hooks/test_formal_artifact_approval_gate.py` to the previous broad path-match behavior.

## Out of Scope

- Changing formal artifact approval packet schema.
- Changing Deliberation Archive write APIs.
- Changing session prompt schema or lifecycle.
- Changing narrative-artifact approval behavior.
