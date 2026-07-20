REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f77f8-0931-75e2-a78d-7dea7037f743
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Revised Implementation Proposal - Canonicalize provider verdict status lines

bridge_kind: prime_proposal
Document: gtkb-wi5625-canonical-provider-verdict-status
Version: 003
Responds to: bridge/gtkb-wi5625-canonical-provider-verdict-status-002.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5625

target_paths: ["scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
predecessor: WI-5578 must be VERIFIED, its implementation claim released, and its final scoped hunk established as the implementation baseline

## Revision Claim

Normalize semantically matching, decorated provider verdict status lines to the
explicit `verdict` argument at the provider-publication boundary. The published
artifact must place the exact ASCII status token alone on line 1 before any
canonical reader, claim gate, or implementation-start gate consumes it.

This revision does not authorize concurrent changes to the shared writer.
WI-5578 is a hard predecessor. WI-5625 implementation may begin only after the
WI-5578 bridge thread is `VERIFIED`, its implementation claim is released, and
the operation-time target baseline has been captured. Wrong or missing status
content continues to fail closed.

## Finding Responses

### F1 - Active WI-5578 ownership conflicts with the clean-target baseline

Accepted and corrected. `scripts/gtkb_bridge_writer.py` is currently modified
by the authorized WI-5578 candidate at the same `publish_lo_verdict` boundary.
`platform_tests/scripts/test_gtkb_bridge_writer.py` is currently clean.
The v001 phrase "two clean files" is withdrawn.

WI-5578 is now an explicit predecessor rather than a concurrent implementation:

1. The latest WI-5578 bridge status must be exact `VERIFIED`.
2. Its `go_implementation` claim must be absent.
3. Prime Builder must record operation-time SHA-256 hashes and `git diff`
   attribution for both WI-5625 targets before acquiring the WI-5625 claim.
4. The WI-5625 implementation must preserve WI-5578's stable mismatch code,
   no-publication behavior, one-correction contract, and independently verified
   final hunk.
5. If either target changes between that capture and mutation, implementation
   stops and returns for a revised proposal.

This sequence removes overlapping ownership. It also makes WI-5578's verified
writer state the canonical WI-5625 baseline.

### F2 - TEST-11670 end-to-end authorization outcome is unmapped

Accepted and corrected. The verification plan now includes one isolated-root
integration test that exercises the complete sequence:

`decorated provider content -> exact ASCII publication -> every canonical
reader -> implementation claim -> finalized implementation-start packet`.

The test must simulate a non-UTF-8 Windows preferred locale and prove that
explicit UTF-8 bridge reads remain correct. A successful helper-level reader
assertion alone is insufficient.

### F3 - One linked requirement is not a live MemBase specification

Accepted and corrected. `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` is removed. The
proposal relies on the code-enforced `lo_verdict` bridge kind and cites WI-5455
only as the separate tracking record for the missing taxonomy specification.
WI-5455 is not treated as a governing specification or implementation
dependency for this bounded repair.

## Requirement Sufficiency

Existing live requirements are sufficient. The change preserves the existing
exact-reader contract and repairs provider publication before bytes become a
governed artifact. No reader is relaxed and no historical bridge file is
rewritten.

## In-Root Placement Evidence

Both targets are within `E:\GT-KB`:

- `scripts/gtkb_bridge_writer.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - one numbered artifact must expose one
  lifecycle status to every canonical consumer.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - provider publication must preserve
  trusted runtime provenance.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - malformed LO verdicts use the explicit
  correction route and are not silently reinterpreted.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - exact PAUTH, project,
  work item, and target paths are declared.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal and
  test mapping cite concrete governing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent verification
  must execute the complete specification-derived path.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - implementation must not restart
  or reconfigure the live dispatcher.
- `GOV-WORK-TREE-HYGIENE-001` - WI-5578 and all unrelated dirty bytes must be
  preserved and attributed.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex self-enforces GO, claim, and
  implementation-start gates.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`

Code-enforced invariant: provider verdict files retain bridge kind
`lo_verdict`. WI-5455 separately tracks the absent formal taxonomy
specification and is not cited as live requirement authority here.

## Owner Decisions / Input

`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` directs the Master
Prime Builder to carry the isolated Dispatcher Next program and its derived
defects to governed terminal states while preserving independent bridge and
implementation-start gates. No additional owner decision is required.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - owner approval and
  terminal-closure mandate for Dispatcher Next and derived defects.

## Revised Scope

After WI-5578 is VERIFIED and its claim is released:

1. Capture target hashes and exact diff attribution.
2. Add one private provider-publication normalizer in
   `scripts/gtkb_bridge_writer.py`.
3. Require the first non-empty provider-authored line to begin with the
   explicit verdict token already validated by `publish_lo_verdict`.
4. Replace that complete decorated line with the exact normalized ASCII
   verdict token before trusted metadata injection, envelope normalization,
   compliance guards, and disk write.
5. Preserve the remaining model-authored content apart from existing metadata
   and envelope normalization.
6. Keep wrong-status and missing-status content fail closed.
7. Add focused and isolated-root integration coverage to
   `platform_tests/scripts/test_gtkb_bridge_writer.py`.

No dispatcher route, cap, lease, TAFE state, credential, deployment, release,
or historical bridge artifact is in scope.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION; WI-5625; TEST-11670; bridge/gtkb-wi5625-canonical-provider-verdict-status-002.md",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001, GOV-DOCUMENT-AUTHOR-PROVENANCE-001, DCL-NO-ACTION-STATUS-SEMANTICS-001, GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Provider publication normalization, exact numbered bridge artifact, canonical readers, claim, implementation-start packet, implementation report, independent VERIFIED.",
  "before_behavior": "A decorated first line can be classified differently by tolerant and exact readers.",
  "after_behavior": "Publication emits the explicit ASCII verdict token alone on line 1, so every downstream reader and gate sees the same lifecycle state.",
  "self_descriptive_naming": "The private normalizer, focused tests, bridge slug, WI-5625, and TEST-11670 all name canonical provider verdict status normalization.",
  "obsolete_guidance_disposition": "Version 001's clean-target claim is withdrawn. No historical bridge file is rewritten and no exact reader is relaxed.",
  "predecessor": "WI-5578 exact VERIFIED plus released implementation claim",
  "baseline": {
    "predecessor_thread": "WI-5578 is currently implemented but not yet VERIFIED and retains an active implementation claim",
    "provider_writer": "currently contains the authorized WI-5578 candidate; its final VERIFIED state becomes the WI-5625 baseline",
    "focused_writer_test": "currently clean; recapture its operation-time hash before mutation"
  },
  "target_baseline": {
    "scripts/gtkb_bridge_writer.py": "currently modified only as the active WI-5578 candidate; operation-time baseline is the final VERIFIED WI-5578 state",
    "platform_tests/scripts/test_gtkb_bridge_writer.py": "currently clean; recapture at operation time"
  },
  "expected_result": {
    "provider_writer": "writes the exact explicit ASCII verdict token alone on line 1",
    "reader_and_gate_agreement": "all canonical readers, claim acquisition, and finalized implementation-start authorization accept the same artifact",
    "runtime_effect": "no dispatcher restart, reconfiguration, lease mutation, cutover, credential operation, deployment, or release"
  },
  "history_preservation": "All bridge files, deliberations, work-item versions, and project-authorization versions remain append-only.",
  "rollback": "Before VERIFIED, restore only the WI-5625 operation-time hunk to the captured WI-5578 baseline and file a revised report. After VERIFIED, use a governed follow-on correction.",
  "fail_closed_conditions": [
    "WI-5578 is not exact VERIFIED or still has an active implementation claim.",
    "Either target changes after the operation-time baseline capture.",
    "Provider content selects a different verdict or contains no status.",
    "Any bridge compliance, claim, implementation-start, or evidence-anchor gate denies the operation."
  ],
  "essential_context_preservation": "Preserve WI-5578's exact final hunk and verification evidence, WI-5625, TEST-11670, the owner program deliberation, provider provenance, append-only bridge history, and both operation-time target hashes.",
  "hard_invariants": [
    "WI-5625 never owns the shared writer concurrently with WI-5578.",
    "The explicit verdict argument remains independently validated.",
    "Wrong or missing provider status fails before publication.",
    "WI-5578 mismatch diagnostics, no-publication behavior, and one-correction contract remain intact.",
    "No implementation occurs without independent GO, exact claim, and implementation-start authorization."
  ]
}
```

## Specification-Derived Verification

| Requirement | Test or command | Acceptance predicate |
| --- | --- | --- |
| Sequenced target ownership | Operation-time status, hash, claim-status, and bridge-status capture | WI-5578 is exact `VERIFIED`; its claim is absent; both WI-5625 targets have recorded hashes and attributable baselines before mutation. |
| Canonical ASCII status | Provider-publication test with content beginning `GO` plus an em-dash title and explicit verdict `GO` | Persisted bytes begin exactly `47 4f 0a`; the decorated line is absent. |
| Canonical reader agreement | Read the published path with `scripts.bridge_thread_files.status_from_bridge_file`, `scripts.bridge_work_intent_registry._bridge_file_status`, and `scripts.implementation_authorization._bridge_file_status` | Every reader returns exact `GO`. |
| Complete authorization path | New isolated-root integration test seeds the minimum project authorization and bridge chain, publishes decorated provider content, reads it through all three readers, acquires the implementation claim, prepares and finalizes the implementation-start packet | Claim acquisition succeeds and finalized packet authorizes the declared protected target without bypass or test-only status injection. |
| Locale-independent UTF-8 | In that integration test, patch the process preferred locale to a cp1252-like value while the decorated content contains UTF-8 bytes not representable as ASCII | Publication and all readers still succeed through explicit UTF-8 decoding; persisted first-line bytes remain exact ASCII. |
| Fail closed | Tests with a different first status and with no status | `BridgePublicationError`; no artifact is written and no claim is released as successful publication. |
| WI-5578 preservation | Full WI-5578 provider-status suite plus focused writer suite | Stable mismatch code, sanitized no-publication diagnostic, one correction, and bounded second mismatch all remain green. |
| Focused regression | `python -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_provider_verdict_status_consistency.py -q --tb=short` | Exit 0. |
| Claim/start regression | `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization.py -q --tb=short` | Exit 0. |
| Static quality | `python -m ruff check scripts/gtkb_bridge_writer.py platform_tests/scripts/test_gtkb_bridge_writer.py` | Exit 0. |
| Formatting | `python -m ruff format --check scripts/gtkb_bridge_writer.py platform_tests/scripts/test_gtkb_bridge_writer.py` | Exit 0. |
| Live nonimpairment | `gt bridge dispatch health --json` before and after | Daemon remains running; no restart, config, route, cap, lease, or TAFE mutation. |

## Acceptance Criteria

- WI-5578 is VERIFIED and unclaimed before WI-5625 implementation begins.
- Provider publication writes an exact canonical ASCII status alone on line 1.
- Decorated but semantically matching status is normalized before all guards and
  readers.
- Wrong or missing status remains fail closed.
- All canonical readers agree.
- The full isolated-root claim and finalized implementation-start path succeeds
  under a simulated non-UTF-8 Windows locale.
- WI-5578 behavior remains intact.
- Only the two declared targets change for WI-5625.
- The live dispatcher is not restarted or reconfigured.

## Pre-Filing Preflight Subsection

The governed revision helper must pass candidate-content applicability and
clause preflights before it creates version 003. Any blocking or missing
evidence result stops filing.

## Risks and Rollback

- Risk: normalization could conceal a model selecting another verdict.
  Mitigation: normalize only when the first status token matches the separately
  validated explicit verdict; mismatch remains a stable error.
- Risk: implementation could absorb WI-5578 changes.
  Mitigation: hard predecessor, released-claim check, operation-time hashes, and
  diff attribution.
- Risk: a helper-only test could miss a gate disagreement.
  Mitigation: TEST-11670 now requires the actual claim and finalized
  implementation-start packet in an isolated root.
- Rollback: before WI-5625 VERIFIED, restore only its hash-pinned hunk to the
  captured WI-5578 baseline and file a revised implementation report. After
  VERIFIED, use a governed follow-on proposal rather than rewriting history.
