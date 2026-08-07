NEW
::init gtkb pb
::open build
author_identity: goose
author_harness_id: G
author_session_context_id: G-2026-08-07T14-51-23Z
author_model: deepseek-v4-flash-0731
author_model_version: 0731
author_model_configuration: gtkb-v4f-goose


# gtkb-narrative-gate-write-crlf-autodiscovery-fix — Normalize proposed Write/Edit content to LF before hash and content comparison in the narrative-artifact approval gate

bridge_kind: prime_proposal
Document: gtkb-narrative-gate-write-crlf-autodiscovery-fix
Version: 001
Date: 2026-08-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-6012

target_paths: [".claude/hooks/narrative-artifact-approval-gate.py", "groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py", "platform_tests/hooks/test_narrative_artifact_approval.py", ".groundtruth/formal-artifact-approvals/**"]

> NOTE: `.groundtruth/formal-artifact-approvals/**` is declared in target_paths solely to satisfy the bridge publication guard's approval-evidence completeness checkpoint (the guard's declaration regex treats the hook filename `narrative-artifact-approval-gate.py` as approval-packet language). This implementation creates, modifies, and regenerates NO file under `.groundtruth/formal-artifact-approvals/`; the envelope is a guard-compliance declaration only, and packet regeneration remains a separate WI-5984 follow-on.

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The narrative-artifact approval gate (`.claude/hooks/narrative-artifact-approval-gate.py`)
lets a session-native Write to a protected narrative path succeed from a matching
on-disk approval packet without an env var the Write tool cannot carry. The matcher
(`_autodiscover_packet`) hashes the proposed content byte-for-byte and compares it to
the packet's declared `full_content_sha256`; the validator (`_validate_packet`) also
compares the proposed content directly against the packet's LF-normalized
`full_content`. On Windows, a session-native Write delivers CRLF-normalized content, so
the byte-for-byte hash and the direct content comparison never match the LF-normalized
packet, and a fully owner-approved, GO-authorized narrative write is hard-blocked.

This change normalizes the proposed Write/Edit content to LF before both the hash in
`_autodiscover_packet` and the content comparison in `_validate_packet`, matching the
packet-generation side (`groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py`),
which already reads and hashes content as LF. **This proposal performs no approval-evidence
work: it creates no approval packet, modifies no `.groundtruth/formal-artifact-approvals`
file, and regenerates no existing packet.** The on-disk WI-5984 packet's hash
inconsistency (its `full_content` hashes to `4bfbcad0...` rather than its declared
`8903abf3...`) is noted as a separate WI-5984 follow-on and is out of scope here.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-6012` that normalizes
proposed Write/Edit content to LF before hash and content comparison in the
narrative-artifact approval gate hook, mirrors the change to the parity template, and
adds a CRLF regression test. Bridge review, implementation-start, and independent
verification gates remain intact.

## Requirement Sufficiency

Existing requirements are sufficient. The work item and the active whole-project
authorization define the implementation boundary; no new requirement is required before
implementation.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/hooks/narrative-artifact-approval-gate.py`,
`groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py`,
`platform_tests/hooks/test_narrative_artifact_approval.py`, and the
`.groundtruth/formal-artifact-approvals/**` guard-compliance envelope (declared only to satisfy the bridge publication guard; no file under it is modified).

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` - governs owner-visible approval packets and their hook-time authorization; this change fixes hook-time matching without altering packet semantics.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - governs the approval gate hook behavior; the LF normalization is a hook-side correction.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the parity template must remain byte-equivalent to the live hook.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge-mediated implementation and verification honor the file bridge authority model.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must be derived from the linked specifications and executed against the implementation; the verification plan above maps each spec to executed tests.

## Prior Deliberations

- `DELIB-202666772` - fix narrative-artifact-approval-gate Edit-autodiscovery gap directly (root cause, not exception); related Edit-path thread is NO-GO v006 (out of scope here).
- `DELIB-20261603` / `DELIB-2410` - Loyal Opposition Review, `gt generate-approval-packet` CLI REVISED-1.
- `DELIB-20261598` / `DELIB-2405` - Loyal Opposition Review, bridge-skill Protected-File Write Helper.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730` - active project authorization covering `WI-6012`.
- Owner directive 2026-08-07: fix `WI-6012` to unblock `WI-5984`; note but do not perform the packet regeneration in this proposal.

## Cross-Harness Disposition

- `codex` - behavioral parity via the byte-equivalent template `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py`; the template is forward-compatible only and is not a live Windows interception boundary per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`.

## Proposed Scope

- Add an LF line-ending normalization helper to `.claude/hooks/narrative-artifact-approval-gate.py` and apply it before hashing the proposed content in `_autodiscover_packet` and before comparing the proposed content against the packet `full_content` in `_validate_packet`, so a CRLF-delivered Write/Edit matches an LF-normalized packet.
- Mirror the resulting hook byte-for-byte into `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py` so the `T-A-codex-template-parity` test stays green.
- Add a CRLF regression test to `platform_tests/hooks/test_narrative_artifact_approval.py` proving a Write whose proposed content differs from the packet LF `full_content` only by CRLF line endings is allowed via packet autodiscovery.
- Do not modify `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py` (already LF-normalized).
- The `.groundtruth/formal-artifact-approvals/**` target path is a guard-compliance declaration only: this implementation creates, modifies, and regenerates NO packet file under that directory. The on-disk WI-5984 packet hash inconsistency (its `full_content` hashes to `4bfbcad0...` rather than its declared `8903abf3...`) is noted as a separate WI-5984 follow-on and is explicitly out of scope.

## Intuitiveness / Non-Impairment Disposition

This change is a narrow, intuitive correction to the narrative-artifact approval gate:
it makes the hook compare the proposed Write/Edit content in the same LF-normalized
form the packet generator uses, restoring the documented autodiscovery purpose for
Windows sessions. It does not alter packet semantics, packet creation, owner-visible
packet display, or the env-var / explicit-hint override paths. No guidance is retired.
The numbered bridge chain remains append-only.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-ARTIFACT-APPROVAL-001` | Add and run a CRLF-autodiscovery regression test in `platform_tests/hooks/test_narrative_artifact_approval.py` proving LF-normalized matching; run the full narrative-gate suite. |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | Run `platform_tests/hooks/test_narrative_artifact_approval.py` in full; all existing and new tests pass. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run the `T-A-codex-template-parity` test; live hook and parity template remain byte-equivalent. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights on the filed proposal and implementation report. |

## Acceptance Criteria

- A session-native Write to a protected narrative path whose proposed content differs from the packet LF `full_content` only by line endings (CRLF vs LF) is allowed via `_autodiscover_packet` when a matching on-disk packet exists.
- The live hook and the `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py` parity template remain byte-equivalent.
- Existing narrative-artifact approval-gate tests (`platform_tests/hooks/test_narrative_artifact_approval.py`, `platform_tests/scripts/test_fab14_narrative_autodiscovery.py`) still pass.
- No `.groundtruth/formal-artifact-approvals/*.json` packet is created, modified, or regenerated by this change.

## Risks / Rollback

Risk is low. The change is confined to the hook's comparison logic and its parity
template plus one test file. The primary risk is that LF normalization could mask a
genuine content difference that happens to differ only by line endings; that is the
intended behavior (line endings are not semantically meaningful in the approved
content). Rollback is a revert of the source and test changes; bridge files and
project authorization records are append-only and must not be deleted by rollback.

## Files Expected To Change

- `.claude/hooks/narrative-artifact-approval-gate.py`
- `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py`
- `platform_tests/hooks/test_narrative_artifact_approval.py`

## Recommended Commit Type

`fix`

---

When you are finished working, close your session envelope by invoking ::wrap.
