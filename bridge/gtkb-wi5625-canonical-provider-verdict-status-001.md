NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f77f8-0931-75e2-a78d-7dea7037f743
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Canonicalize provider verdict status lines

bridge_kind: prime_proposal
Document: gtkb-wi5625-canonical-provider-verdict-status
Version: 001
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5625

target_paths: ["scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

Normalize provider-authored verdict content to the explicit `verdict` argument
before author metadata, envelope, compliance, and disk-write processing. The
published artifact must place the exact ASCII status token alone on line 1
even when model-authored content decorates that line with a title.

The repair is deliberately confined to the provider publication boundary and
its existing focused test module. It does not relax canonical readers to
accept malformed status lines. Invalid content that does not begin with the
requested status token continues to fail closed.

## Requirement Sufficiency

Existing requirements sufficient.

`GOV-FILE-BRIDGE-AUTHORITY-001`,
`GOV-DOCUMENT-AUTHOR-PROVENANCE-001`, and
`DCL-NO-ACTION-STATUS-SEMANTICS-001` already require one canonical numbered
bridge chain, trustworthy provider publication, and a deterministic correction
route. The owner-authorized Dispatcher Next program records this defect as
`WI-5625` / `TEST-11670`; no new formal requirement is needed for this bounded
compatibility repair.

## In-Root Placement Evidence

Both targets are inside `E:\GT-KB`: `scripts/gtkb_bridge_writer.py` and
`platform_tests/scripts/test_gtkb_bridge_writer.py`.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION; WI-5625; bridge/gtkb-dispatcher-next-foundation-spike-003.md",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001, GOV-DOCUMENT-AUTHOR-PROVENANCE-001, DCL-NO-ACTION-STATUS-SEMANTICS-001, and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Provider PublishBridgeVerdict normalization, bridge compliance guards, numbered bridge write, canonical readers, implementation-start gate, implementation report, and independent Loyal Opposition VERIFIED.",
  "before_behavior": "Provider verdict content may persist a decorated first line such as GO plus a title. Tolerant scanners classify it as GO while exact claim and implementation-start readers reject it, so one artifact projects conflicting lifecycle states.",
  "after_behavior": "Provider verdict publication replaces a semantically matching decorated first line with the exact explicit ASCII verdict token before guards and write. Every canonical downstream reader sees the same lifecycle status.",
  "self_descriptive_naming": "The helper, test, bridge slug, work item, and test ID all name canonical provider verdict status normalization.",
  "obsolete_guidance_disposition": "No historical bridge file is rewritten and no reader is relaxed. Version 003 NO-ACTION remains the correction route for the already-published malformed verdict; future provider verdicts are canonicalized at publication.",
  "history_preservation": "Existing numbered bridge artifacts, deliberations, work-item versions, and project authorization versions remain append-only.",
  "baseline": {
    "foundation_thread": "version 003 NO-ACTION pending corrected LO verdict",
    "provider_writer": "accepts first-token match and preserves decorated first line",
    "implementation_targets": "two clean files"
  },
  "expected_result": {
    "provider_writer": "writes the exact explicit verdict token alone on line 1",
    "reader_agreement": "thread reader, claim registry, and implementation-start validator return the same status",
    "runtime_effect": "no dispatcher restart, configuration, route, cap, lease, TAFE, credential, deployment, release, or Git mutation"
  },
  "rollback": {
    "instructions": "Before VERIFIED, revert only the two scoped files and file a revised implementation report. After VERIFIED, use a governed follow-on correction rather than rewriting bridge history.",
    "verification": "Rerun the focused writer pytest module, ruff checks, bridge preflights, and live dispatcher health read."
  },
  "hard_invariants": [
    "The explicit verdict argument remains independently validated.",
    "Wrong-status or missing-status model content fails before write.",
    "Trusted provider author metadata is unchanged.",
    "No historical bridge artifact is rewritten.",
    "No implementation occurs without independent GO, exact claim, and implementation-start authorization."
  ],
  "fail_closed_conditions": [
    "Model first status token differs from the explicit verdict.",
    "Model content contains no status token.",
    "Provider worker role or claim provenance is invalid.",
    "Bridge compliance or evidence-anchor guard denies publication.",
    "Post-write readback differs from normalized content."
  ],
  "essential_context_preservation": "Preserve WI-5625, TEST-11670, the owner program deliberation, version 003 NO-ACTION evidence, provider provenance, and the exact six-target boundary of the foundation spike."
}
```

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - one numbered artifact must project one lifecycle status across all consumers.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - provider verdict publication must preserve trusted worker metadata while normalizing only the status envelope.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - malformed LO verdicts must be correctable through an explicit Prime NO-ACTION route.
- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` - provider verdicts remain `lo_verdict`; no new bridge kind is introduced.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal cites exact PAUTH, project, work item, and targets.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal and tests carry concrete governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent VERIFIED requires executed spec-derived tests.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the repair must not restart or reconfigure the live dispatcher.
- `GOV-WORK-TREE-HYGIENE-001` - preserve unrelated dirty files and modify only the two clean targets.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex self-enforces GO, claim, and implementation-start gates.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the observed failure, work item, test, NO-ACTION, repair, and verification remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the derived defect follows an explicit proposal through VERIFIED terminal state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect is preserved in MemBase rather than treated as transient chat context.
- `GOV-STANDING-BACKLOG-001` - any further parser discrepancy becomes governed derived work.

## Owner Decisions / Input

`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` directs the Master
Prime Builder to implement the isolated program and drive constituent,
derived, and upstream-dependent work to VERIFIED or another governed terminal
state. It also preserves independent bridge review and implementation-start
gates. No additional owner input is required for this bounded repair.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - owner approval and terminal-closure mandate for Dispatcher Next and derived defects.

## Proposed Scope

1. Add one private provider-publication normalizer in
   `scripts/gtkb_bridge_writer.py`.
2. Require the first non-empty model-authored line to begin with the explicit
   provider verdict token already validated by `publish_lo_verdict`.
3. Replace that complete decorated line with the exact normalized verdict
   token before trusted metadata injection, envelope normalization, compliance
   guards, and write.
4. Preserve the remainder of model-authored content byte-for-byte apart from
   existing metadata and envelope normalization.
5. Keep wrong-status and missing-status content fail closed.
6. Add focused regression coverage to
   `platform_tests/scripts/test_gtkb_bridge_writer.py`.

## Specification-Derived Verification

| Requirement | Test or command | Acceptance predicate |
| --- | --- | --- |
| Canonical ASCII status | New provider-publication unit test with model content `GO \u2014 Proposal Approved` and verdict argument `GO` | Written file begins exactly `GO\n::init gtkb pb\n::open test\n`; no decorated first line remains. |
| Reader agreement | Same test passes the written path to `scripts.bridge_thread_files.status_from_bridge_file`, `scripts.bridge_work_intent_registry._bridge_file_status`, and `scripts.implementation_authorization._bridge_file_status` | All three return `GO`. |
| Correct transition | Existing `publish_lo_verdict` next-version and claim-release tests | Existing valid `NEW -> GO`, `REVISED -> GO/NO-GO`, `NO-ACTION -> GO/NO-GO`, and report `NEW -> VERIFIED/NO-GO` behavior remains green. |
| Fail closed | New tests for content beginning with `NO-GO` while argument is `GO`, and for content with no status | `BridgePublicationError`; no bridge file written and claim not released as success. |
| Metadata integrity | Existing trusted runtime model metadata and provenance tests | All pass unchanged; normalization does not alter trusted author fields. |
| Focused regression | `python -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=short` | Exit 0. |
| Static quality | `python -m ruff check scripts/gtkb_bridge_writer.py platform_tests/scripts/test_gtkb_bridge_writer.py` | Exit 0. |
| Formatting | `python -m ruff format --check scripts/gtkb_bridge_writer.py platform_tests/scripts/test_gtkb_bridge_writer.py` | Exit 0. |
| Live nonimpairment | `gt bridge dispatch health --json` before and after | Daemon remains running; no restart, config, cap, route, lease, or TAFE mutation. |

## Acceptance Criteria

- Provider publication always writes an exact canonical status token alone on
  line 1.
- A decorated but semantically matching model line is normalized, not
  persisted.
- A wrong or absent model status is rejected before write.
- Writer, canonical thread reader, work-intent registry, and
  implementation-start validator agree on the generated file's status.
- Existing provider metadata, transition, claim, guard, and envelope tests
  remain green.
- Only the two declared target files change.
- The live dispatcher is not restarted, reconfigured, or cut over.

## Risks and Rollback

- Risk: over-normalization could hide a model choosing a different verdict.
  Mitigation: normalize only after the first token exactly matches the
  separately validated verdict argument; mismatches remain errors.
- Risk: newline handling could change the body. Mitigation: preserve existing
  newline semantics and test the complete written head.
- Risk: provider publication is shared by F and D. Mitigation: run the full
  focused writer suite and retain all provenance/guard tests.
- Rollback: revert the two scoped files. Existing version 003 NO-ACTION
  remains the append-only recovery path for the already-published malformed
  artifact.
