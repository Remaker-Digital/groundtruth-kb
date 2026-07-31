NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 8e0b4e69-e221-4d23-9bfd-e5d9591e66f2
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - Extend narrative-artifact-approval-gate autodiscovery to Edit tool calls

bridge_kind: prime_proposal
Document: gtkb-narrative-gate-edit-autodiscovery-fix
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5509

target_paths: [".claude/hooks/narrative-artifact-approval-gate.py", "groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py", "groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py", "groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_fab14_narrative_autodiscovery.py", "platform_tests/hooks/test_narrative_artifact_approval.py", "groundtruth-kb/tests/test_cli_approval_packet.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Confirmed this session (WI-5492 impl, bridge GO gtkb-retire-ipa-refs-rules-skills-002): a content-changing Edit to a protected narrative artifact cannot be authorized session-natively. Write already has HYG-047/FAB-14 autodiscovery (matches an on-disk packet by target_path+content-hash); Edit is explicitly excluded because tool_input carries old_string/new_string, not full content, and the only two packet-reference paths (env var, tool_input hint) are both unreachable across separate tool invocations given Edit's additionalProperties:false schema. Two-part fix: (1) hook reconstructs Edit's post-edit content from file_path+old_string+new_string+replace_all (fail-closed to today's behavior whenever ambiguous), then reuses the existing unmodified autodiscovery path; (2) generate-approval-packet --kind narrative gains an optional --content-file override (the flag already exists, wired only for --kind formal) so a packet's content can come from a staged file while target_path still identifies the real, already-existing target -- closing the matching chicken-and-egg for packet generation itself. Related but narrower than WI-5441 (broader 7-leak registry unification, capture-only/not yet approved).

Work item description: The narrative-artifact-approval-gate.py PreToolUse hook's _autodiscover_packet() (HYG-047/FAB-14) matches a pre-generated approval packet against a Write call's full content hash, letting a session-native Write succeed without an env var the tool cannot carry. It explicitly does NOT apply to Edit (new_content is None for Edit tool_input per the hook's own code/docstring), because Edit calls carry old_string/new_string, not full content. Confirmed this session (WI-5492 rules-skills implementation, bridge GO gtkb-retire-ipa-refs-rules-skills-002): with no reachable env var (PowerShell-set vars do not persist to a separate Edit tool invocation) and no way to pass an extra tool_input field (Edit's declared schema has additionalProperties:false), a content-changing Edit to a protected narrative artifact (.claude/rules/*.md, CLAUDE.md, AGENTS.md) cannot be authorized session-natively at all -- a genuine chicken-and-egg gap distinct from Write's already-working path. Fix: the hook already receives file_path, old_string, new_string, and replace_all in tool_input for Edit calls; it can read the current on-disk full content, apply the same replace-once/replace_all logic Edit itself performs to reconstruct the resulting full content, then reuse the EXISTING autodiscovery match (same rel_path + content-hash lookup already implemented for Write) against that reconstructed content. No env var, no tool schema change, no new mechanism -- a narrow, symmetric extension of the existing Write path. Related but distinct from the broader WI-5441 protected-artifact-registry unification (that WI is capture-only/not yet implementation-approved and targets a different, larger unification scope: registry fragmentation across 8 places). Owner explicitly authorized this narrower, immediate fix via AskUserQuestion during WI-5492 implementation (2026-07-18).

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5509` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/hooks/narrative-artifact-approval-gate.py`, `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py`, `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py`, `groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `platform_tests/scripts/test_fab14_narrative_autodiscovery.py`, `platform_tests/hooks/test_narrative_artifact_approval.py`, `groundtruth-kb/tests/test_cli_approval_packet.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - auto-linked governing or work-item specification.
- `GOV-ARTIFACT-APPROVAL-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20264771` - Loyal Opposition Review - Advisory-to-Backlog Router REVISED-2
- `DELIB-20261598` - Loyal Opposition Review - bridge-skill Protected-File Write Helper
- `DELIB-2405` - Loyal Opposition Review - bridge-skill Protected-File Write Helper
- `DELIB-1738` - Loyal Opposition Review - GTKB-PRE-FILING-PREFLIGHT-HOOK
- `DELIB-20264779` - Loyal Opposition Review - Benchmark Suite REVISED-2

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30` - active project authorization covering `WI-5509`.

## Proposed Scope

- Hook fix (byte-identical in both .claude/hooks/ and the Codex template per test_a_codex_template_parity_exists_and_matches): add _reconstruct_edit_content(file_path, tool_input) that reads current on-disk content and applies the same old_string->new_string substitution Edit itself performs (single occurrence, or all occurrences when replace_all); returns None (fail-closed, current behavior preserved) on missing/non-string old_string or new_string, zero occurrences, or ambiguous multi-occurrence without replace_all. main() calls it for tool_name==Edit in place of the current hardcoded None; Write's path is completely unchanged.
- CLI fix: build_narrative_packet() gains an optional content_source: Path|None param; when given, full_content is read from content_source instead of target_path, while target_path (the packet field the hook matches against rel_path) still derives from the target_path argument. _build_narrative_packet() in cli_approval_packet.py threads request.content_file into this new param when present (validated in-root + exists, mirroring the existing formal-kind check); when absent, behavior is 100% unchanged (reads target_path as today). --content-file's cli.py help text updated to reflect the new optional narrative use.
- New tests: unit tests for _reconstruct_edit_content in test_fab14_narrative_autodiscovery.py (single occurrence, replace_all, zero-occurrence fail-closed, ambiguous-occurrence fail-closed, non-string inputs fail-closed); end-to-end Edit-tool_name payload tests in test_narrative_artifact_approval.py mirroring the existing T-A-allow-with-packet Write tests; a --content-file override test in test_cli_approval_packet.py confirming target_path still matches the real path while full_content comes from the separate content file.

## Cross-Harness Disposition

- **codex**: parity: byte-identical template update at groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py per test_a_codex_template_parity_exists_and_matches; forward-compatible only, not a live Windows interception boundary per ADR-CODEX-HOOK-PARITY-FALLBACK-001, unchanged by this fix

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | python -m pytest platform_tests/hooks/test_narrative_artifact_approval.py platform_tests/scripts/test_fab14_narrative_autodiscovery.py -q |
| `GOV-ARTIFACT-APPROVAL-001` | python -m pytest groundtruth-kb/tests/test_cli_approval_packet.py -q |

## Acceptance Criteria

- Existing test_autodiscover_none_for_contentless_edit and all other current tests in both files pass unchanged (autodiscover's own contract is untouched; only main()'s new_content derivation for Edit changes).
- A new Edit-tool_name payload with a matching on-disk packet (content computed via content-file-override packet generation) allows; a mismatched or ambiguous Edit still blocks with the existing error message.
- Codex template remains byte-identical to the Claude hook (test_a_codex_template_parity_exists_and_matches stays green).
- generate-approval-packet --kind narrative with no --content-file behaves exactly as before (regression-covered by the existing CRLF test).

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/hooks/narrative-artifact-approval-gate.py`
- `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py`
- `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py`
- `groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_fab14_narrative_autodiscovery.py`
- `platform_tests/hooks/test_narrative_artifact_approval.py`
- `groundtruth-kb/tests/test_cli_approval_packet.py`

## Recommended Commit Type

`feat`
