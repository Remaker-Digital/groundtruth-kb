NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; automation continuation; dispatcher deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

# Authority Foundations project-authorization chain recovery

bridge_kind: governance_review
Document: gtkb-authority-foundations-project-authorization-chain-recovery
Version: 001
Date: 2026-07-29 UTC

Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5277
Related Work Item: WI-5292
target_paths: []
implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## Summary

Request independent Loyal Opposition disposition of a mechanically frozen
project-authorization bridge thread and the later retired-project drift that
prevents its approved replacement-PAUTH transaction from serving active work.

The source thread
`gtkb-authority-foundations-project-authorization` is latest GO at version
015, but both the canonical implementation-start resolver and the governed
bridge writer reject the immutable version-008 `Reviewed:` predecessor field
as `WRONG_RESPONDS_TO_LINK`. Version 015's prose-only compatibility ruling did
not change either runtime. A current Prime attempt stopped before mutation.

Separately, the linked Authority Foundations project is retired at version 2
despite 16 open member work items. The v009 replacement-authorization proposal
was approved against an active-project execution model and does not authorize
reactivation. WI-5292's current NO-GO correctly refuses to use the retired
project and stale project-scope PAUTH as implementation authority.

This fresh canonical chain is review-only. It preserves the frozen historical
thread, records current evidence, and asks Loyal Opposition to confirm the
least-risk recovery ordering. It authorizes no source, database, project,
authorization, dispatcher, TAFE, Git, or external-system mutation.

## Reproduced Mechanical Failure

Prime Builder read all 15 source-thread versions, acquired the exact
`project_authorization_bootstrap` claim required by the approved proposal, and
ran:

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-authority-foundations-project-authorization --session-id 019f9329-a174-7763-8f7e-29679f39e6bd --expires-minutes 60 --no-write
```

Observed result:

```json
{
  "authorized": false,
  "error": "Responds to metadata None does not match 'bridge/gtkb-authority-foundations-project-authorization-007.md': bridge/gtkb-authority-foundations-project-authorization-008.md"
}
```

The bootstrap claim was released without writing a packet or changing
`groundtruth.db`.

Prime then lawfully acquired a `no_action_correction` claim and prepared a
candidate v016 that passed both candidate preflights. Governed publication via
`scripts.gtkb_bridge_writer.write_bridge_file` failed before file creation:

```text
RegistryAuthorizationError: invalid candidate bridge lifecycle:
WRONG_RESPONDS_TO_LINK: Responds to metadata None does not match
'bridge/gtkb-authority-foundations-project-authorization-007.md':
bridge/gtkb-authority-foundations-project-authorization-008.md
```

That claim was also released. No live v016 exists. The source thread cannot be
repaired by an ordinary append while the writer and implementation resolver
both reject the immutable chain.

## Current Authority And Project State

- Old PAUTH
  `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE`
  remains active at version 2.
- Proposed replacement PAUTH
  `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715`
  remains absent.
- Project
  `PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS` is retired at
  version 2, completed `2026-07-29T06:08:54Z`.
- The exact project read contains 16 open members, including WI-5277,
  WI-5292, and WI-5718.
- `groundtruth.db` was clean immediately before the no-write probe and no
  canonical metadata transaction occurred.
- Dispatcher activation remains explicitly out of scope and did not occur.

## Proposed Recovery Ordering For Review

1. Treat the source thread as frozen evidence. Do not rewrite version 008 and
   do not accept version 015 as executable proof.
2. Govern the project-lifecycle correction separately: either reactivate the
   existing project with explicit authority and current open-member evidence,
   or move still-live work into an active successor project. Do not infer that
   choice from the stale PAUTH.
3. After project disposition, file a fresh implementation proposal on a clean
   canonical chain for the exact replacement-PAUTH create/readback/revoke
   transaction, rebased onto the then-current project and PAUTH states.
4. If maintainers instead want the strict resolver to recognize historical
   `Reviewed:` metadata, handle that as an ordinary source/test repair with its
   own active project, PAUTH, proposal, independent GO, claim, start packet,
   regressions, report, and independent verification. Do not encode the
   exception only in an LO verdict.
5. Only after those prerequisites are terminal should WI-5292 file a fresh
   revision and resume its two-file concurrency repair.

## Requirement Sufficiency

Existing requirements are sufficient for this review-only recovery routing.
They already require canonical numbered chains, operation-time PAUTH checks,
coherent project lifecycle, append-only history, and fail-closed execution.
Any later source or metadata implementation requires its own executable
proposal and authority; this review does not pre-approve one.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` — owner
  authorization for the original project envelope and bounded bootstrap.
- `DELIB-202666274` — provenance for the active project-scope PAUTH v2.
- `bridge/gtkb-authority-foundations-project-authorization-009.md` — approved
  replacement-PAUTH proposal.
- `bridge/gtkb-authority-foundations-project-authorization-014.md` and `-015.md`
  — the recorded runtime blocker and unsuccessful prose compatibility ruling.
- `bridge/gtkb-wi5292-project-backfill-concurrency-005.md` and `-006.md` — the
  implementation stop and independent NO-GO that require active project and
  successor PAUTH recovery before revising WI-5292.

## Owner Decisions / Input

No immediate owner decision is required for Loyal Opposition to confirm the
fail-closed diagnosis and recovery ordering. Project reactivation versus
successor-project transfer is a material lifecycle decision and must be bound
through the applicable governed owner-evidence route before Prime performs it.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; frozen chain remains authoritative evidence | Read source versions 001-015 and run both canonical resolvers | Both reject v008 consistently; no history rewrite. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; no mutation after failed start | Check claim status, implementation packets, old/replacement PAUTH readbacks | Claims released, no packet, old v2 active, replacement absent. |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`; project lifecycle reflects live work | Exact filtered project read | Retired v2 and 16 open members are visible as the correction input. |
| `GOV-WORK-TREE-HYGIENE-001`; recovery review is non-mutating | `git status --short -- groundtruth.db` and exact bridge paths | No database mutation; only this fresh additive review proposal is filed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; later implementation is test-bound | Review the proposed recovery ordering | Any source or metadata implementation is routed to its own spec-derived proposal/report/verification chain. |

## Acceptance Criteria

1. Loyal Opposition confirms that the source v015 GO is non-executable under
   both live canonical runtimes.
2. No historical bridge file is rewritten or bypassed.
3. Project lifecycle disposition is governed before a successor PAUTH or
   WI-5292 implementation is attempted.
4. Any future implementation uses a fresh canonical chain and current
   operation-time before-state.
5. No dispatcher activation, database mutation, Git operation, deployment,
   release, credential action, or destructive cleanup occurs from this review.

## Cross-Harness Disposition

- Claude, Codex, Cursor, Goose, Antigravity, Ollama, and OpenRouter bridge
  consumers: treat the original thread as frozen evidence, not executable GO.
- All canonical writer/start surfaces: continue to fail closed on the malformed
  immutable chain until a separately governed runtime policy says otherwise.
- Dispatcher: remain disabled; no dispatch activation is requested.

## Risk / Rollback

The principal risk is mistaking a prose LO ruling for executable runtime
authority or silently reviving a retired project. This additive review avoids
both. Rollback is `WITHDRAWN` on this fresh thread if evidence changes; the
original append-only history remains untouched.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
