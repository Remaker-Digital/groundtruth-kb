NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb353-97ef-74b1-9310-09761b16938a
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; TAFE deliberately disabled
author_metadata_source: current session metadata

bridge_kind: prime_proposal
Document: gtkb-wi5888-exact-session-authority-cache-repair
Version: 001
Date: 2026-08-01 UTC

# Governed Defect-Fix Proposal — Exact session authority and derived-cache repair

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL
Work Item: WI-5888

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/session/wrap.py", "groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "scripts/session_role_resolution.py", ".claude/hooks/lo-file-safety-gate.py", ".claude/hooks/bridge-axis-2-surface.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_session_envelope_cli_choice.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py", "platform_tests/hooks/test_bridge_axis_2_role_aware.py"]

implementation_scope: source,test,protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

KB Mutation: This proposal performs no MemBase mutation or `groundtruth.db`
write. The database is not an implementation target.

---

## Summary

WI-5888 consolidates three still-reproducible session-role/envelope defects:
session wrap can close the per-harness projection instead of the caller's exact
session, role-gated hooks can trust stale or contradictory cache state, and the
wrap snapshot can disagree with live enforcement for one continuous session.

The proposed architecture makes the unique exact session-id-keyed envelope the
session identity authority. Per-harness envelopes and session-role marker files
become derived caches only. Wrap, role resolution, and the affected hook
consumers must resolve one exact caller session document, validate its identity
and provenance, fail closed on invalid authority, and atomically regenerate
only derived cache surfaces when one uniquely valid authority document exists.

This is proposal and independent-review authority only. It does not authorize
implementation, mutation of any target, claim bypass, Git staging or commit,
dispatcher activation, or terminal verification.

## Current Defect Evidence

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py` already supports
  session-id-keyed documents through `worker_session_envelope_path`,
  `load_worker_session`, and `resolve_worker_role_provenance`, including
  ambiguity and provenance validation. However, `load_current` still reads the
  per-harness `session-envelope.json`, and `close_session` selects that
  projection without an exact caller session ID.
- `groundtruth-kb/src/groundtruth_kb/session/wrap.py` invokes the current-envelope
  path and closes it using only harness identity. The `gt session wrap` surface
  in `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py` does not require
  an exact session ID.
- `scripts/session_role_resolution.py` still accepts per-harness projection and
  marker fallbacks. `.claude/hooks/lo-file-safety-gate.py` treats resolver
  exceptions and durable-only outcomes as fail-open. The AXIS 2 surface consumes
  the same resolver and can therefore disagree with the wrap snapshot.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` v1 currently names the per-harness
  envelope as active authority and tells wrap to read it. That requirement is
  incompatible with the owner's exact-session authority decision and must not
  be stretched by implementation inference.

## Proposed Architecture and Acceptance Criteria

1. The wrap and close APIs require the exact caller session ID. The CLI obtains
   it from an explicit argument or the canonical session-ID resolver; absence
   or ambiguity is a typed, visible failure before any close/archive mutation.
2. The runtime loads exactly
   `harness-state/<harness>/sessions/<session-id>/session-envelope.json`, then
   validates the requested session ID, harness identity, lifecycle status, and
   worker-role provenance. It must not select authority from the per-harness
   current projection, lexical ordering, a durable role registry, or a marker.
3. Wrap archives and closes only that validated exact document. A second close
   is idempotent only when it proves the same completed close; a mismatched or
   conflicting closed state fails closed and cannot mutate another session.
4. Per-harness `session-envelope.json` and session-role markers are documented
   and treated as non-authoritative caches. Given one uniquely valid exact
   document, drift is repaired atomically from that document. Missing,
   malformed, mismatched, or ambiguous authority leaves all caches untouched
   and returns a typed failure.
5. `scripts/session_role_resolution.py` returns one typed resolution result
   based on the exact session document. It does not fall back to the durable
   dispatcher role registry, infer role from a projection, or silently choose
   between contradictory live surfaces.
6. Both affected hook consumers use that typed result. Protected-write
   enforcement fails closed with a visible diagnostic when authority is
   unresolved or contradictory. The AXIS 2 surface reports the same resolved
   role and diagnostic state as the safety gate.
7. Cache repair is narrowly bounded: it may replace only derived session
   envelope/role projections for the same validated session and harness. It
   must use same-directory temporary material plus atomic replacement, retain
   no partial cache set on failure, and never rewrite authoritative history.
8. No new hard-coded timer, retry count, throttle, threshold, fan-out value, or
   per-harness concurrency cap is introduced. Contention-sensitive tests use
   deterministic synchronization rather than short elapsed-time assumptions.
9. Claude and Codex interactive surfaces consume the same session authority
   contract. Unsupported event hooks remain visibly unsupported; parity is not
   simulated by enabling TAFE or any dispatcher.

## Scope Boundaries

This slice does not change bridge routing, dispatcher rules, harness capability
registration, claim schema, work-intent ownership, or formal requirements. It
must never mutate `.api-harness/routing.toml`, `.claude/settings.json`,
`config/dispatcher/rules.toml`, or
`config/agent-control/harness-capability-registry.toml`. TAFE and the native
dispatcher remain deliberately disabled.

The exact document's existing validation and provenance machinery should be
reused. This proposal does not authorize a parallel envelope runtime or an
alternate role authority. It also does not impose an interim wrap pause: the
owner explicitly chose continuation under the current behavior while the
governed repair proceeds.

## Cross-Harness Disposition

- **Claude Code**: the native `lo-file-safety-gate` and AXIS 2 hook surfaces
  consume the same typed exact-session resolver and must fail closed or report
  the same visible diagnostic when authority cannot be established.
- **Codex Desktop/CLI**: there is no claim of native event-hook parity. Session
  wrap, CLI resolution, and mandatory self-enforcement consume the shared exact
  document contract; unsupported event delivery remains disclosed and TAFE is
  not enabled to simulate it.
- **Cursor, Antigravity, Goose, Ollama, OpenRouter, and Alibaba Cloud Studio**:
  no harness-specific configuration or capability registration changes in this
  slice. Any use of the shared resolver receives the same typed authority and
  fail-closed semantics; absent native hooks remain an explicit mechanism
  difference rather than a false parity claim.
- **Parity gate**: independent verification must prove behavioral agreement for
  the shared authority contract and preserve every existing unsupported-hook
  disclosure. No typed waiver is requested.

## Dependency and Overlap Gates

Implementation may not start until all of these conditions are proven in a
fresh proposal-review/claim/start context:

- `WI-5580` is terminal and its current foreign-dirty changes to
  `groundtruth-kb/src/groundtruth_kb/session/envelope.py` are committed or
  otherwise cleanly resolved. This proposal must not hand-stage, rewrite, or
  absorb that cohort.
- `WI-5679` and `WI-5723` are terminal, or an independently approved hunk ledger
  proves non-overlap for every shared source/test target. Their role-keying and
  fallback-removal behavior is consumed rather than duplicated.
- `WI-5812` completes before any shared
  `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py` mutation, or an
  independently approved hunk ledger proves non-overlap.
- `WI-5815` receives an explicit governed disposition. Its per-session envelope
  and claim-isolation ownership remains distinct; WI-5888 owns wrap selection,
  exact-authority validation, derived-cache repair, and hook convergence. Any
  residual overlap must be merged into one reviewed implementation carrier or
  removed from this scope before GO.
- The formal requirement repairs in `## Requirement Sufficiency` are complete.
- All target paths are clean relative to their admitted predecessor commits,
  no other live claim holder exists, the PAUTH remains active, a fresh exact
  work-intent claim is acquired, and a schema-v3 implementation-start packet is
  minted before the first protected mutation.
- `WI-5783` is independently VERIFIED before protected commit finalization is
  attempted. No finalizer may rely on the currently unsafe protected-commit
  checker before that terminal result.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires the append-only bridge proposal,
  independent GO, exact claim, implementation-start authority, report, and
  independent terminal verdict.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this
  proposal to identify the governing requirements and disclose the known
  insufficiency before source mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the explicit
  project, work-item, and PAUTH linkage above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the terminal
  verdict to reproduce specification-derived checks rather than accept a
  generic suite pass.
- `GOV-STANDING-BACKLOG-001` — WI-5888 is the durable work carrier for the
  advisory-derived defect; the owner decision authorizes proposal filing only.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` — governs envelope lifecycle and wrap,
  but v1's per-harness-authority language must be replaced by a fully approved
  revision before implementation.
- `DCL-SESSION-ROLE-RESOLUTION-001` — governs transcript/session role evidence,
  dispatcher-only durable role authority, and fail-closed unresolved identity;
  its formal approval defect must be repaired before it can govern this slice.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` — preserves an owner-declared
  interactive role across compaction and contiguous session boundaries without
  changing the dispatcher/default assignment map.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — requires the repair to preserve
  bridge, dispatcher, harness, and current-work capabilities outside the exact
  defect surface.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — requires the requirement conflict,
  owner choices, source evidence, tests, report, and verdict to remain linked as
  a durable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — keeps WI-5888, its requirement repairs,
  proposal, implementation report, and terminal verdict in explicit lifecycle
  states rather than treating proposal filing as completion.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — governs promotion of the advisory
  findings and owner choices into WI, DELIB, specification, bridge, test, and
  verification artifacts.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — requires a concrete per-harness
  parity disposition for the two `.claude/hooks/` targets and blocks unsupported
  mechanism differences from being reported as native parity.
- `ADR-CROSS-HARNESS-PARITY-001` — establishes behavioral parity with disclosed
  mechanism differences as the required cross-harness architecture.

## Prior Deliberations

- `INTAKE-e71dd673` and `INTAKE-d9d4764d` — establish the durable requirement
  candidate for interactive session-envelope role continuity; WI-5888 narrows
  the unresolved identity and cache-repair contract.
- `INTAKE-e0d49108` — establishes the architecture principle that lifecycle
  events are authoritative records and projections are derived; this proposal
  applies that principle to session documents and caches.
- `DELIB-20260801-WI5888-GOVERNED-PROPOSAL-APPROVAL` — authorizes investigation,
  owner clarification, and a governed proposal, but no implementation.
- `DELIB-20260801-WI5888-EXACT-SESSION-IDENTITY-AUTHORITY` — selects the unique
  exact session-id-keyed document as the canonical session identity authority.
- `DELIB-20260801-WI5888-DERIVED-CACHE-REPAIR-POLICY` — selects atomic repair of
  derived projections only when one valid exact authority document exists.
- `DELIB-20260801-WI5888-INTERIM-WRAP-POLICY` — selects continued current wrap
  operation during governance/implementation rather than an interim pause.

The three source advisories remain evidence, not implementation authority:
`bridge/gtkb-session-wrap-close-mistargets-session-identity-001.md`,
`bridge/gtkb-role-gated-hook-envelope-fragility-advisory-003.md`, and
`bridge/gtkb-session-role-resolution-wrap-vs-live-hook-disagreement-001.md`.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5888; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE; DELIB-20260801-WI5888-GOVERNED-PROPOSAL-APPROVAL; DELIB-20260801-WI5888-EXACT-SESSION-IDENTITY-AUTHORITY; DELIB-20260801-WI5888-DERIVED-CACHE-REPAIR-POLICY; DELIB-20260801-WI5888-INTERIM-WRAP-POLICY",
  "canonical_authority": "The approved future revisions of DCL-SESSION-ENVELOPE-DURABILITY-001 and DCL-SESSION-ROLE-RESOLUTION-001, together with DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001 and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001.",
  "primary_route": "Governed bridge review, predecessor and requirement closure, exact work-intent claim, schema-v3 implementation start, scoped implementation and tests, implementation report, and independent atomic VERIFIED finalization.",
  "before_behavior": "Wrap selects through a per-harness projection, role resolution accepts stale projection or marker fallback, and affected role-gated hooks can disagree with the exact session document or fail open.",
  "after_behavior": "Wrap and role-gated enforcement resolve one validated exact session-id-keyed envelope; derived projections are atomically repaired only from unique valid authority; invalid authority fails closed before mutation.",
  "self_descriptive_naming": "The proposal slug, exact-session runtime functions, derived-cache repair operation, typed resolution results, and focused tests explicitly name authority, cache, wrap, and role-resolution behavior.",
  "obsolete_guidance_disposition": "The per-harness-authority language in DCL-SESSION-ENVELOPE-DURABILITY-001 v1 must be superseded through a formal approved revision before implementation; no historical bridge or requirement version is rewritten or deleted.",
  "history_preservation": "Exact session documents, numbered bridge files, Deliberation Archive decisions, predecessor commits, and MemBase history remain append-only; only non-authoritative cache surfaces may be regenerated.",
  "baseline": {
    "work_item": "WI-5888 is open/backlogged and proposal-authorized only",
    "requirements": "DCL-SESSION-ENVELOPE-DURABILITY-001 v1 conflicts with the owner decision; DCL-SESSION-ROLE-RESOLUTION-001 v7 has an unresolved formal-approval defect",
    "overlap": "WI-5580 owns the foreign-dirty envelope.py cohort; WI-5679, WI-5723, WI-5812, and WI-5815 have disclosed shared surfaces or behavior",
    "dispatch": "TAFE and native dispatcher remain deliberately disabled"
  },
  "expected_result": {
    "authority": "One exact session-id-keyed envelope is the sole live identity authority",
    "wrap": "Only the validated caller session can be closed or archived",
    "cache_repair": "Only derived caches for that validated session and harness are atomically regenerated",
    "hooks": "Protected role-gated surfaces converge on one typed resolver and fail closed on unresolved or contradictory authority"
  },
  "rollback": {
    "instructions": "Revert only the future scoped source and test commit, then regenerate derived caches from immutable exact session documents; never delete authority or bridge history.",
    "verification": "Re-run all focused pytest, ruff, applicability, clause, cleanliness, dispatch-disabled, and forbidden-path checks after rollback."
  },
  "hard_invariants": [
    "No implementation before approved requirement revisions, predecessor clearance, independent GO, exact claim, and schema-v3 start authority",
    "No authority selection from per-harness projection, lexical order, markers, or the durable dispatcher role registry",
    "No mutation of authoritative session history during cache repair or rollback",
    "No TAFE or dispatcher activation and no forbidden routing, settings, dispatcher, or capability-registry mutation",
    "No absorption or hand-staging of the foreign-dirty WI-5580 cohort",
    "No new hard-coded timer, threshold, throttle, retry, fan-out, or concurrency cap"
  ],
  "fail_closed_conditions": [
    "Exact caller session ID is absent, malformed, ambiguous, unknown, or mismatched to the harness",
    "Exact document status or worker-role provenance is malformed, contradictory, or conflicts with the requested operation",
    "Derived cache repair cannot complete atomically or would touch another session or harness",
    "A predecessor, requirement repair, PAUTH, work-intent claim, schema-v3 start, target-cleanliness, or independent-review gate is missing"
  ],
  "essential_context_preservation": "Preserve the four owner DELIB decisions, exact-session authority, derived-only atomic repair, interim continuation policy, all overlap gates, the requirement insufficiency, explicit target cohort, TAFE-disabled state, and spec-derived verification evidence across implementation and review."
}
```

## Owner Decisions / Input

The required owner choices are complete and canonically captured in the four
DELIB records above. No further owner decision is required to review this
proposal. The authorization does not waive requirement repair, predecessor
closure, independent GO, claim/start gates, independent verification, or
atomic commit-finalization evidence.

## Requirement Sufficiency

New or revised requirement required before implementation.

Before GO can authorize implementation, a fully approved formal-artifact packet
must revise `DCL-SESSION-ENVELOPE-DURABILITY-001` so that the exact
session-id-keyed envelope is authority, per-harness/marker surfaces are derived
caches, wrap requires exact identity, and repair/failure semantics match the
owner decisions. The `DCL-SESSION-ROLE-RESOLUTION-001` v7 approval defect must
also be repaired through its governed carrier without citing retired
`GOV-SESSION-ROLE-AUTHORITY-001` as active authority. The implementation report
must identify the exact approved requirement versions used.

## Spec-Derived Verification Plan

The implementation report and independent terminal verdict must record commands,
exit codes, test counts, and expected/actual outcomes for all checks below.

1. Exact wrap selection and lifecycle (`DCL-SESSION-ENVELOPE-DURABILITY-001`):
   add tests proving two concurrent sessions for one harness cannot cause one
   caller to close, archive, or project the other's envelope; explicit unknown,
   duplicate, mismatched-harness, malformed, and conflicting-closed cases fail
   before mutation.
2. CLI binding (`DCL-SESSION-ENVELOPE-DURABILITY-001`): add parser/runtime tests
   proving `gt session wrap` supplies the canonical exact caller session ID and
   never selects a per-harness projection or lexical latest document.
3. Derived-cache repair (`DCL-SESSION-ROLE-RESOLUTION-001`): add tests proving
   one valid exact document atomically repairs stale envelope and marker caches,
   while absent/ambiguous/invalid authority leaves all cache bytes unchanged.
4. Hook convergence (`DCL-SESSION-ROLE-RESOLUTION-001` and
   `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`): add tests proving the safety
   gate fails closed on unresolved/contradictory authority and both affected
   hook surfaces report the same exact-session role and typed diagnostic.
5. Nonimpairment and boundaries (`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`):
   assert normal open/wrap/archive behavior remains valid, TAFE stays disabled,
   and forbidden configuration plus the capability registry remain clean at
   HEAD.

Run at minimum with the explicit repository interpreter:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_envelope_cli_choice.py platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py platform_tests/hooks/test_bridge_axis_2_role_aware.py -q --tb=short
E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe check groundtruth-kb/src/groundtruth_kb/session/envelope.py groundtruth-kb/src/groundtruth_kb/session/wrap.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py scripts/session_role_resolution.py .claude/hooks/lo-file-safety-gate.py .claude/hooks/bridge-axis-2-surface.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_envelope_cli_choice.py platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py platform_tests/hooks/test_bridge_axis_2_role_aware.py
E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe format --check groundtruth-kb/src/groundtruth_kb/session/envelope.py groundtruth-kb/src/groundtruth_kb/session/wrap.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py scripts/session_role_resolution.py .claude/hooks/lo-file-safety-gate.py .claude/hooks/bridge-axis-2-surface.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_envelope_cli_choice.py platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py platform_tests/hooks/test_bridge_axis_2_role_aware.py
```

Independent verification must additionally inspect the admitted commit and
diff by reference, re-run the focused tests, confirm no unrelated or foreign
dirty payload was included, and attach atomic protected-commit finalization
evidence. A short timer expiry, lock wait, or scanner delay is not a defect
verdict without bounded retry and evidence that the configured limit itself is
wrong.

## Risk / Rollback

The highest risks are closing the wrong session, repairing cache state from an
ambiguous document, silently weakening a protected-write gate, or absorbing a
foreign dirty cohort. The dependency gates and fail-closed typed outcomes bound
those risks. The implementation must be one scoped commit after all predecessor
targets are clean; rollback is a revert of that commit plus regeneration of
derived caches from the still-immutable exact documents. Authoritative session
history must never be deleted as rollback.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing version for
`gtkb-wi5888-exact-session-authority-cache-repair`. Dispatcher/TAFE state plus
the numbered file chain remain the live workflow state under
`GOV-FILE-BRIDGE-AUTHORITY-001`; filing does not enable dispatch.

## Recommended Commit Type

`fix` — the future implementation corrects session-selection, cache-consistency,
and fail-closed enforcement defects without adding a new product capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
