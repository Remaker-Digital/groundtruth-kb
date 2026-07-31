REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Revised Implementation Proposal - WI-5234 Source-Coherent Author Metadata

bridge_kind: prime_proposal
Document: gtkb-wi5234-codex-session-model-metadata-attestation
Version: 005
Responds to: bridge/gtkb-wi5234-codex-session-model-metadata-attestation-004.md
Approved proposal: bridge/gtkb-wi5234-codex-session-model-metadata-attestation-001.md
Prior GO: bridge/gtkb-wi5234-codex-session-model-metadata-attestation-002.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5234
target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "scripts/bridge_author_metadata.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py", "platform_tests/scripts/test_bridge_author_metadata.py"]
Recommended commit type: fix

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Prevent `load_author_metadata()` from validating a model-provenance record assembled from more than one runtime model source. Exact session-envelope fallback remains available when environment or explicit input supplies only the session selector, while any explicit or environment model override must provide a complete source-coherent model/version/configuration bundle.

## Requirement Sufficiency

Existing requirements and the single version-004 finding are sufficient. No new specification or owner decision is needed.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-20263247` - WI-4522 revised proposal review.
- `DELIB-20263246` - WI-4522 implementation verification.
- `DELIB-20266652` and `DELIB-20266660` - review-independence context.
- `DELIB-20263483` - author-identity environment-alias defect context.
- `DELIB-20261032` - bridge author-provenance gap advisory context.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` remains the active authorization covering `WI-5234`.
- No new owner decision is required; this revision implements the deterministic version-004 correction.

## Finding Addressed

### F1 - P1 - Partial env/explicit runtime metadata can produce a false exact-envelope provenance stamp

Response: Refactor runtime model selection into mutually exclusive bundles:

1. A complete explicit bundle (`author_model`, `author_model_version`, and `author_model_configuration`, with optional source/context-window metadata) has highest precedence.
2. Otherwise, a complete environment bundle has precedence.
3. Otherwise, when neither source supplies model/provenance override fields, load the exact validated Codex session envelope selected by the runtime session id.
4. A partial explicit or environment model/provenance override fails closed with `BridgeAuthorMetadataError`; it is never overlaid onto another source.
5. Durable identity and a session-id selector may still come from their existing sources because they identify the author/session rather than asserting model provenance.

This preserves complete explicit/environment behavior for provider and headless writers while preventing the reproduced false `x-codex-turn-metadata` stamp.

## Scope Changes

No target expansion. New source/test deltas are expected only in:

- `scripts/bridge_author_metadata.py`
- `platform_tests/scripts/test_bridge_author_metadata.py`

The prior authorized changes in `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py` and `platform_tests/scripts/test_session_envelope_cli_provenance.py` remain part of the eventual four-file implementation report but receive no new correction unless testing exposes a directly related defect.

No dispatcher, TAFE, harness registry, role, credential, Git lifecycle, push, deployment, release, or external-system mutation is authorized.

## Specification-Derived Verification Plan

| Specification / behavior | Required verification |
| --- | --- |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Regressions prove partial explicit and partial environment model/provenance fields fail closed and cannot retain an exact-envelope source label. |
| Existing provider/headless precedence | Existing complete-environment tests remain green; add complete explicit-over-environment coverage where needed. |
| Exact Codex session fallback | Session-id-only environment or explicit selection still loads the exact open attested envelope and returns its coherent model bundle. |
| `SPEC-AUQ-POLICY-ENGINE-001` | No missing model field is guessed or borrowed; partial bundles are denied deterministically. |
| All linked specifications | Focused and adjacent pytest suites, Ruff check, Ruff format check, `py_compile`, diff check, applicability preflight, clause preflight, and spec-derived dry run pass before the refreshed report. |

Required focused cases include model-only, version-only, configuration-only, metadata-source-only, context-window-only, partial multi-field explicit and environment input, complete explicit input, complete environment input, and exact-envelope fallback with session selector only.

## Acceptance Criteria

- No validated author record combines model fields from explicit/environment input with model fields or `author_metadata_source` from an exact session envelope.
- Partial explicit/environment model metadata fails closed with a stable diagnostic.
- Complete explicit and environment runtime bundles retain their existing precedence.
- Exact-session fallback remains functional when only identity/session selection is supplied.
- The four-file focused and adjacent suites plus static gates pass, and the refreshed implementation report records current counts and hashes.

## Pre-Filing Preflight Subsection

Applicability command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5234-codex-session-model-metadata-attestation --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5234-codex-session-model-metadata-attestation-005.md --json
```

Observed result: `preflight_passed: true`, packet hash `sha256:afa6c7a83e463a85091805a18f14fb909893c23b5ae868c572a312e59848e9be`, `missing_required_specs: []`, `missing_advisory_specs: []`, and `blocking_errors: []`.

Clause command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5234-codex-session-model-metadata-attestation --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5234-codex-session-model-metadata-attestation-005.md
```

Observed result: 5 clauses evaluated, 3 `must_apply`, 2 `may_apply`, zero must-apply evidence gaps, zero blocking gaps, exit 0.

## Risk And Rollback

The primary compatibility risk is rejecting callers that previously relied on partial model-field mixing. That behavior is the verified defect; complete runtime bundles and exact-envelope fallback remain supported. Rollback is a focused revert of the authorized correction under separate authority. Numbered bridge artifacts remain append-only.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
