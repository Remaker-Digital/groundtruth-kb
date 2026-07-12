NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

# Implementation Proposal - Expose provider Read truncation instead of returning silent partial files

bridge_kind: prime_proposal
Document: gtkb-wi5214-truthful-provider-read-pagination
Version: 001
Date: 2026-07-12 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5214-TRUTHFUL-READ-PAGINATION-20260712
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5214

target_paths: ["scripts/cloud_harness_base.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_ollama_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Make provider Read output truthful under the existing 6,000-character transport ceiling by adding zero-based character offsets and an in-band continuation marker whenever more content remains. Preserve exact short-file output and D/F/H generous allowances.

Work item description: Genuine Alibaba H review 2026-07-12T15-55-02Z-loyal-opposition-H-0584dc read complete 12,115-byte bridge report gtkb-wi5199-fd-evidence-h-functional-proof-003 through the shared provider Read tool. The tool silently capped output at MAX_TOOL_OUTPUT_CHARS, ending mid-token without a truncation marker or continuation contract. H reasonably but incorrectly classified the durable artifact as physically truncated and issued NO-GO. Make bounded Read output explicitly truthful through truncation metadata/marker and a governed continuation or pagination path so provider reviewers cannot mistake partial transport output for file contents.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5214` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/cloud_harness_base.py`, `scripts/ollama_harness.py`, `platform_tests/scripts/test_cloud_harness_base.py`, `platform_tests/scripts/test_ollama_harness.py`.

## Specification Links

- `ADR-CLOUD-HARNESS-TEMPLATE-001` - auto-linked governing or work-item specification.
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
- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20263306` - TAFE Dual-Write INDEX Parity Proposal Review
- `DELIB-20263304` - Verdict
- `DELIB-WI4510-CUTOVER-HOLD-PRE-RECONCILIATION-20260614` - HOLD WI-4510 TAFE governed cutover; reconcile shadow-vs-INDEX divergence first
- `DELIB-20263305` - TAFE Dual-Write INDEX Parity Proposal Review
- `DELIB-20266071` - First-Line Role Eligibility Check

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5214-TRUTHFUL-READ-PAGINATION-20260712` - active project authorization covering `WI-5214`.

## Proposed Scope

- Add an optional nonnegative offset argument to the shared cloud and Ollama Read schemas; keep max_chars positive and interpret both in Unicode-character units.
- Return exact short-file content unchanged at offset zero. For incomplete reads, reserve space inside MAX_TOOL_OUTPUT_CHARS for a marker that reports the returned half-open character range, total character count, and exact next offset.
- Ensure each Read response remains at most 6,000 characters even when max_chars is larger; support repeated continuation reads that reconstruct the complete file without overlap or gaps.
- Keep filesystem confinement, all other tool behavior, telemetry, dispatch routing, bridge authority, and D/F/H 600/900/28800/29400 allowances unchanged.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | Shared-base tests prove exact short-read compatibility, bounded marked long reads, Unicode-character ranges, and lossless continuation. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run both focused files plus Ruff check and format check on all four targets before requesting VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CROSS-HARNESS-PARITY-001` | The same pagination contract and tests cover the dedicated Ollama D path and shared OpenRouter F/Alibaba H path. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Regression reproduces H's 12,115-character review case and proves the model-visible response cannot be mistaken for the complete artifact. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Ollama schema, validation, marker, response bound, and reconstruction behavior match the shared cloud implementation. |

## Acceptance Criteria

- A provider cannot receive silent partial Read content: every incomplete result carries truthful range, total, and continuation-offset metadata inside the existing output ceiling.
- Short UTF-8 files read from offset zero remain byte-for-byte text-equivalent to current output, with no marker.
- First, middle, final, oversized-max_chars, small-max_chars, end-offset, and invalid-offset tests pass for the shared cloud and Ollama paths; paginated chunks reconstruct the original Unicode text exactly.
- Focused suites and Ruff check/format gates pass, followed by an implementation report, independent Loyal Opposition VERIFIED verdict, and focused commit.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/cloud_harness_base.py`
- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Recommended Commit Type

`feat`
