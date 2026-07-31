NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

# Implementation Proposal - Route provider-backed LO bridge verdicts through governed writer

bridge_kind: prime_proposal
Document: gtkb-wi5210-provider-lo-governed-verdict-publication
Version: 001
Date: 2026-07-12 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5210-PROVIDER-VERDICT-PUBLICATION-20260712
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5210

target_paths: ["scripts/gtkb_bridge_writer.py", "scripts/cloud_harness_base.py", "scripts/alibaba_cloud_studio_harness.py", ".api-harness/routing.toml", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair the missing provider-backed Loyal Opposition publication capability exposed by genuine H dispatch 2026-07-12T11-03-20Z-loyal-opposition-H-92f409. H completed 74 turns and 139 governed tool calls but raw Write correctly hit controlled-artifact/implementation-start protections. Add a high-level governed tool instead of weakening those protections.

Work item description: A genuine dispatcher-produced Alibaba H Loyal Opposition review completed 74 provider turns and 139 governed tool calls, but its verdict publication failed: cloud_harness_base routed Write of the next numbered bridge verdict through raw protected-target guards, implementation-start-gate saw an unknown mutating target, and no governed bridge helper path was available. Add a provider-backed verdict-publication route that validates tool arguments before hooks, requires a next-numbered append-only LO status, delegates bridge content to the canonical governed writer, preserves author/session/model metadata and compliance/evidence checks, and leaves non-bridge protected writes fail-closed.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5210` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/gtkb_bridge_writer.py`, `scripts/cloud_harness_base.py`, `scripts/alibaba_cloud_studio_harness.py`, `.api-harness/routing.toml`, `platform_tests/scripts/test_gtkb_bridge_writer.py`, `platform_tests/scripts/test_cloud_harness_base.py`, `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`, `platform_tests/scripts/test_implementation_start_gate.py`, `platform_tests/scripts/test_lo_verified_commit_atomicity.py`.

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
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` - auto-linked governing or work-item specification.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666172` - Authorize WI-5199 plus H functional proof
- `DELIB-20263264` - Loyal Opposition Review: WI-4509 Cutover Evidence Gathering
- `DELIB-20261280` - Loyal Opposition Verdict: VERIFIED — Envelope Init-Keyword Amendment - Current-State Evidence Capture (WI-4291)
- `DELIB-20261584` - Loyal Opposition Verification - Legacy GOV WI Cleanup
- `DELIB-20260706` - Loyal Opposition Verdict: VERIFIED — Envelope Init-Keyword Amendment - Current-State Evidence Capture (WI-4291)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5210-PROVIDER-VERDICT-PUBLICATION-20260712` - active project authorization covering `WI-5210`.

## Proposed Scope

- Add a dedicated PublishBridgeVerdict provider tool accepting slug, verdict, content, and VERIFIED-only finalization inputs; the provider never chooses a path or version.
- Resolve document-authoritative worker role from the actual session envelope, require loyal-opposition and a live same-session claim for the exact thread, compute max(version)+1, validate the current latest transition and response reference, and fail closed on metadata conflicts.
- Run scanner-safe credential protection, bridge compliance, evidence-anchor, author-provenance, review-independence, and exclusive append checks before GO/NO-GO; delegate VERIFIED via stdin to the existing atomic finalizer with explicit include paths, optional hunk patches, and commit message.
- Expose PublishBridgeVerdict only to H bridge-review/verification routes; leave raw Write/Edit/Bash and production implementation-start/controlled-artifact guards unchanged. Preserve H and all D/F/H generous numeric allowances exactly.
- Keep all pre-existing foreign hunks in approved dirty files excluded from the focused patch.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Writer and cloud tests prove exact-chain next-version publication, exclusive append, and raw direct-write denial. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Atomicity tests prove VERIFIED uses the canonical finalizer and rolls back on commit failure. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Tests prove session-document LO authority, same-session claim ownership, independent context, and trusted H model metadata. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Alibaba route tests and a genuine dispatcher H review prove substantive governed verdict publication. |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | Shared cloud runtime owns the provider tool while the Alibaba adapter supplies only route/prompt wiring. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Tests prove ordinary mutating tools retain their full fail-closed guard floor. |

## Acceptance Criteria

- The provider supplies no path/version authority; valid GO/NO-GO appends exactly the computed next version through the canonical writer and cannot overwrite, skip, race, or recreate a historical version.
- Valid VERIFIED invokes the canonical atomic finalizer and either commits exactly the reviewed include/hunk set plus verdict or leaves no verdict/partial commit on failure.
- Prime-only statuses, wrong-role or missing session documents, absent/wrong/expired claims, stale responses, metadata conflicts, malformed arguments, self-review, fabricated anchors, and compliance/credential failures deny before mutation; claims release only after successful publication.
- Direct Write using path or file_path remains bridge_status_file_direct_mutation; no general exemption is added.
- H sees PublishBridgeVerdict only for LO review skills, generous H settings remain 600/900/28800/29400, focused tests pass, and a genuine dispatcher H review publishes a substantive canonical verdict.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/gtkb_bridge_writer.py`
- `scripts/cloud_harness_base.py`
- `scripts/alibaba_cloud_studio_harness.py`
- `.api-harness/routing.toml`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`

## Recommended Commit Type

`feat`
