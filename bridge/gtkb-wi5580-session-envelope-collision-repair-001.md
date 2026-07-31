NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Defect-Fix Proposal - Prevent cross-harness session-envelope collisions from blocking modernization evidence

bridge_kind: prime_proposal
Document: gtkb-wi5580-session-envelope-collision-repair
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5580

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "scripts/collect_modernization_semantic_evidence.py", ".claude/hooks/workstream-focus.py", "platform_tests/scripts/test_collect_modernization_semantic_evidence.py", "platform_tests/scripts/test_kb_attribution_session_role.py", "platform_tests/hooks/test_workstream_focus.py"]

## Claim

The modernization evidence collector must select the active worker's exact canonical session envelope from trusted runtime-specific host markers and durable harness identity, while continuing to derive role authority only from the selected envelope. Existing same-session documents owned by other harnesses must remain immutable, visible as collision diagnostics, and unable to block legitimate evidence acquisition for the acting harness.

## Defect / Reproduction

On current HEAD `7048eaf6e84d7624f100cd77c08e80aae6f0421c`, the active Codex Desktop session id appears in simultaneous open exact-session documents under the `claude`, `codex`, and `cursor` harness directories. `resolve_session_authority()` calls `resolve_worker_role_provenance()` without a harness selector, so the resolver raises `Worker role provenance is ambiguous across session envelopes.` All 26 modernization semantic-evidence receipt plans then stop before measurement. The Codex host exposes `CODEX_THREAD_ID` but no `GTKB_HARNESS_NAME` or `GTKB_HARNESS_ID`, so a generic environment override is neither required nor sufficient as the trust basis.

The Claude interactive hook also accepts `GTKB_HARNESS_NAME` before its adapter-owned identity. A foreign inherited override can therefore make the Claude adapter write an exact-session document under another harness directory. The repair must prevent new foreign writes without deleting or rewriting any existing envelope.

## In-Root Placement Evidence

All implementation and test targets are inside the mandatory `E:\GT-KB` project root. No external or retired artifact is an input, output, dependency, or cited authority.

## Bridge Chain Placement

This artifact is filed with `NEW` status as the next numbered bridge file at `bridge/gtkb-wi5580-session-envelope-collision-repair-001.md`. The versioned bridge file chain is append-only; no prior version is deleted or rewritten.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` - worker role remains document-authoritative; host detection is only a document selector.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - exact-session documents remain durable and existing collision history is not rewritten.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - evidence acquisition must not impair any harness, dispatcher path, or ordinary workflow.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - trust and nonimpairment requirements need executable regression coverage.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation remains bound to the active project PAUTH.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - operation-time PAUTH validation remains mandatory.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the implementation-start packet must bind the selected PAUTH and exact paths.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - WI-5580 remains linked to live specification authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - no protected mutation may start before independent GO, claim, and start packet.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this Prime Builder proposal requests independent Loyal Opposition review.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, PAUTH, and work-item linkage are explicit above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposed behavior is mapped to its governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent verification must execute the specification-derived matrix below.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - each approved hunk must be independently reviewable and mechanically finalizable.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - WI-5256, WI-5353, WI-5396, and WI-5541 overlap is preserved and checked before start/finalization.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the observed defect is carried by WI-5580 and TEST-11627.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - implementation report and terminal verification remain required.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - canonical evidence, not scratch state, governs completion.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ENVELOPE-DURABILITY-001`, and `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` already define the required trust, durability, and nonimpairment outcomes. WI-5580 applies those requirements to a newly reproduced collision path, and the cited specifications fully govern this implementation.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": {
    "work_item": "WI-5580",
    "linked_test": "TEST-11627",
    "reproduced_head": "7048eaf6e84d7624f100cd77c08e80aae6f0421c"
  },
  "canonical_authority": [
    "GOV-SESSION-ROLE-AUTHORITY-001",
    "DCL-SESSION-ENVELOPE-DURABILITY-001",
    "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001"
  ],
  "primary_route": "Prime Builder proposal through governed bridge CLI, deterministic TAFE review, independent GO, exact claim/start, implementation report, and independent VERIFIED",
  "before_behavior": "A same-session document collision across three harness directories blocks all 26 semantic-evidence plans before measurement.",
  "after_behavior": "The acting harness selects and validates only its exact canonical document; foreign documents remain immutable and diagnostic while valid evidence acquisition proceeds.",
  "self_descriptive_naming": "Selector, collision diagnostic, and producer-ownership names state that harness identity selects a document but never grants role authority.",
  "obsolete_guidance_disposition": "No active guidance is retired; inherited foreign harness overrides are rejected by the owning adapter instead of being treated as write authority.",
  "history_preservation": "Every existing exact-session envelope remains byte-for-byte unchanged and queryable; no collision cleanup is an implementation mechanism.",
  "baseline": {
    "semantic_evidence_plans": 26,
    "plans_blocked_before_measurement": 26,
    "same_session_harness_documents": 3
  },
  "expected_result": {
    "plans_blocked_by_valid_acting_harness_collision": 0,
    "foreign_document_mutations": 0,
    "dispatcher_tafe_harness_configuration_mutations": 0
  },
  "rollback": {
    "instructions": "Revert only independently reviewed WI-5580 hunks through a governed successor; do not rewrite runtime envelope history.",
    "test": "Rerun TEST-11627 and the focused collector, provenance, hook, hard-invariant, fresh-worker, harness-parity, and scope-semantic suites."
  },
  "hard_invariants": [
    "Role authority comes only from validated worker_role_provenance in the selected exact-session document.",
    "Ambiguous host families and durable identity mismatches fail closed.",
    "No existing envelope, dispatcher, TAFE, harness role, eligibility, or routing state is mutated."
  ],
  "fail_closed_conditions": [
    "Missing or malformed selected document",
    "Closed or stale selected session",
    "Wrong harness name or durable harness id",
    "Conflicting runtime-specific host markers",
    "Selected document provenance conflicts with its envelope"
  ],
  "essential_context_preservation": "The selected exact-session bytes and hash, foreign-collision diagnostics, durable harness identity, document-authoritative role provenance, current Git HEAD, and all downstream activity-specific evidence outcomes remain explicit."
}
```

## Prior Deliberations

- `DELIB-202666274` - owner-approved project-scoped modernization implementation authority with bridge, claim, start, and independent verification gates preserved.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE` is active, project-scoped, and has no per-work-item inclusion restriction.
- The owner requires all routing to remain deterministic through TAFE/bridge and prohibits direct harness interaction or dispatcher configuration manipulation.

## Cross-Harness Disposition

- Shared parity: `resolve_worker_role_provenance()` and the modernization evidence selector remain harness-neutral after a runtime-specific host family is validated. Codex, Claude, Cursor, Antigravity, Ollama, OpenRouter, and Alibaba documents are all subject to the same exact-session, durable-identity, open-state, and document-role validation.
- Codex: `CODEX_THREAD_ID` or the Codex runtime family selects the Codex document only; role still comes from that document. This is the current acceptance-blocker reproduction.
- Claude: `.claude/hooks/workstream-focus.py` is the only adapter-specific producer target in this slice. It is bound to the Claude durable identity and refuses a conflicting foreign override while preserving fail-soft hook behavior.
- Cursor, Antigravity, Ollama, OpenRouter, and Alibaba: no adapter-specific file is changed in this slice. Their explicit producer calls continue to pass their own harness name/id and receive the shared resolver validation. Focused parity tests must prove no behavioral regression.
- No typed waiver is requested. Any newly discovered harness-specific producer that can write a foreign document is a blocking finding for this proposal, not an implicit exclusion.

## Proposed Scope

### IP-1 - Trusted acting-harness selector

Add a reusable selector that recognizes unambiguous runtime-specific host markers such as a Codex thread marker or Claude Code marker, maps the selected harness name to its durable identity, and rejects conflicting host families or an explicit harness id/name that disagrees with the durable map. The selector must never provide or override a role.

### IP-2 - Collision-tolerant evidence authority

Make modernization evidence authority pass the validated acting-harness selector to `resolve_worker_role_provenance()`. Validate and snapshot only the exact selected document. Preserve fail-closed behavior for missing, closed, malformed, wrong-harness, wrong-session, identity-mismatched, or provenance-conflicting documents. Surface the presence of ignored same-session foreign documents as deterministic diagnostics without deleting or modifying them.

### IP-3 - Producer ownership guard

Bind the Claude workstream-focus adapter to the Claude durable harness identity. Treat a conflicting inherited `GTKB_HARNESS_NAME` or `GTKB_HARNESS_ID` as a fail-soft refusal to persist an envelope, not as permission to write a foreign harness document. Preserve normal hook response behavior and do not contact, disable, reroute, or reconfigure any harness.

### IP-4 - Hunk isolation and coexistence

`groundtruth-kb/src/groundtruth_kb/session/envelope.py` already contains foreign WI-5396 exact-root Git-status bytes. Implementation and finalization must preserve those pre-start bytes and apply only WI-5580 additions. No whole-file attribution is allowed. All other concurrent worktree changes remain excluded.

## Specification-Derived Verification Plan

| Requirement | Deterministic verification |
|---|---|
| Acting Codex collision proceeds | Seed valid `codex`, `claude`, and `cursor` documents for one session, provide only Codex runtime markers, and assert authority resolves and snapshots the valid Codex document. |
| Role remains document-authoritative | Forge ambient role variables and assert the selected envelope's validated role wins; malformed or conflicting selected provenance fails closed. |
| Host trust is unambiguous | Supply conflicting Codex and Claude host markers, unknown host markers, and durable identity mismatch; assert failure before measurement or mutation. |
| Foreign documents are immutable | Hash all colliding documents before and after resolution and assert byte identity; assert deterministic collision diagnostics enumerate paths without treating them as authority. |
| Wrong selected document fails closed | Cover missing, closed, stale-session, wrong-harness, wrong-id, malformed, and provenance-conflicting selected envelopes. |
| Producer cannot write foreign harness state | Exercise the Claude adapter with a Codex override and assert no Codex envelope is created or changed while hook behavior remains fail-soft. |
| Normal producers remain functional | Exercise a valid Claude init-keyword payload and assert the exact Claude envelope is written with durable id B and document-authoritative role provenance. |
| Nonimpairment | Run focused collector, session-role, and hook suites plus modernization hard-invariant, fresh-worker, harness-parity, and scope-semantic acquisition checks; assert no dispatcher, TAFE, role, eligibility, or routing state changes. |
| Hunk isolation | Capture pre-start hashes/diffs for all six targets; prove WI-5396 bytes remain byte-identical and finalization selects only approved WI-5580 hunks plus its complete bridge chain. |

## Acceptance Criteria

1. With one valid acting-harness envelope and any number of same-session foreign envelopes, modernization evidence proceeds to measurement using only the acting envelope.
2. Caller-supplied role values, registry role defaults, and foreign envelopes cannot grant role authority.
3. Ambiguous or contradictory runtime host markers fail closed before evidence mutation.
4. Existing collision documents remain byte-for-byte unchanged, and collision diagnostics are deterministic and in-root.
5. The Claude startup producer cannot write or update a foreign harness document even when foreign override variables are inherited.
6. Missing, malformed, closed, wrong-session, wrong-harness, and durable-identity-mismatched selected documents remain hard failures.
7. All 26 semantic-evidence plans advance past the current issuer-provenance blocker on a valid current Codex session; downstream activity-specific results remain reported independently.
8. Dispatcher availability, TAFE behavior, harness dispatchability, roles, eligibility, routing, credentials, Git index/history, deployments, releases, and live envelope history are unchanged.
9. The WI-5396 pre-start hunk and every unrelated dirty path are preserved and excluded from WI-5580 finalization.

## Risks / Rollback

The primary risk is converting a selector into role authority or silently choosing among conflicting host signals. Tests therefore force selection and role validation into separate stages and fail closed on ambiguous host families. The second risk is absorbing WI-5396's concurrent `session/envelope.py` hunk; applicability and finalization must use stable hunk-level patches. Rollback is limited to the independently reviewed WI-5580 hunks; no runtime envelope history is rewritten as either implementation or rollback.

## Explicit Exclusions

- No deletion, archival, closure, rewrite, merge, or relocation of existing session-envelope documents.
- No dispatcher/TAFE configuration or runtime mutation, routing choice, harness contact, role/eligibility change, quiescence, or disablement.
- No synthetic evidence, receipt backfill, acceptance-result fabrication, or frozen-contract amendment.
- No Git staging, commit, push, history rewrite, release, deployment, credential, database, external-system, or destructive-cleanup operation during implementation.
- No source changes before independent GO plus matching claim/start authority.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
- `scripts/collect_modernization_semantic_evidence.py`
- `.claude/hooks/workstream-focus.py`
- `platform_tests/scripts/test_collect_modernization_semantic_evidence.py`
- `platform_tests/scripts/test_kb_attribution_session_role.py`
- `platform_tests/hooks/test_workstream_focus.py`

## Recommended Commit Type

`fix`
