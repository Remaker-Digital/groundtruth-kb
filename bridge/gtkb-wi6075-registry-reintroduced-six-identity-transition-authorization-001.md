NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=not-exposed-by-host; thread_source=codex-desktop-interactive
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: prime_proposal
Document: gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization
Version: 001
Date: 2026-08-10 UTC
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project Authorization Version: 2
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6075
Related Work Items: WI-5441, WI-5702, WI-5925, WI-6078
target_paths: ["config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth.db"]
implementation_scope: registry_reintroduced_six_identity_transition_apply_authorization
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
dispatcher_or_tafe_mutation_in_scope: false

# WI-6075 — Fresh Single-Use Authorization For Six Reintroduced WI-5441 Registry Identities

## Summary

Authorize one fresh, generation-bound `membership_set` registry transition that
removes exactly six absent pre-rename WI-5441 template identities that were
reintroduced after the original WI-6075 transition had completed. This is a
new incident and a new single-use authorization carrier. It does not reuse the
consumed request, journal, or `GO` from
`gtkb-wi6075-registry-transition-apply-authorization` versions 001-003.

The current registry surfaces are coherent but invalid: the canonical and
packaged declarations contain 1,451 records and agree with the MemBase
projection, while six registered backing paths are absent. The six rows were
re-added at `2026-08-10T15:57:18Z` by `loyal-opposition/goose/G` with the
recorded reason `Owner-directed registry parity repair (2026-08-10): re-declare
72 projection-only wi5441 records and sync projection`. That parity repair
restored byte agreement but also restored six identities that the owner had
already authorized WI-6075 to retire.

No raw TOML or SQLite mutation is proposed. After independent review, the
implementation must use only the governed `gt registry transition request`
and `gt registry transition apply` control surface with a fresh exact claim,
schema-v3 implementation-start packet, active PAUTH, independent apply `GO`,
and exact OPS envelope.

## Current Authoritative Baseline

- Git HEAD at proposal preparation:
  `bde0203557dcc395777ec2ca31b9faa32f0fea42`.
- Current canonical/packaged declaration digest:
  `sha256:8b1045403cca37495ad5871186c48925f0bee68c8ae5ebbccbfb090dc7033461`.
- Current projection digest:
  `sha256:b1283a32a20db8df97d443f54456aa571ad6f2c1c623076670f83fc4bd8ee791`.
- Current generation digest:
  `sha256:af78d18d997be53ffc44cca8b7620f9845c5fad66bd26b211256f7a84420e6c5`.
- Current record count: `1451`.
- Fresh `gt registry diff`, `validate`, and `inspect --no-census` evidence:
  declaration/projection coherence is true; `invalid_unknown=6`;
  `unregistered_load_bearing=0`; membership completeness is false.
- The latest committed registry transaction journal remains row 15,
  `SOTTXN-FD98A21071F549B69DB74E360AB15EC2`, at 1,445 records. The current
  1,451-record generation is coherent but is not that journal generation.

These baseline digests are observation evidence, not a reusable request. The
request step must re-read the live generation. Any drift before request or
apply fails closed and requires a fresh reviewed proposal or reviewer-confirmed
rebaseline; it must not be silently widened.

## Exact Six-Identity Scope

The only authorized removals are:

1. `wi5441-member-groundtruth-kb-templates-skills-baseline-audit-s-cc59361240`
2. `wi5441-groundtruth-kb-templates-skills-bridge-helpers-impl-report-bridge-py`
3. `wi5441-groundtruth-kb-templates-skills-bridge-helpers-revise-bridge-py`
4. `wi5441-member-groundtruth-kb-templates-skills-bridge-helpers-s-7c1442288e`
5. `wi5441-member-groundtruth-kb-templates-skills-bridge-helpers-s-9ddc7316a2`
6. `wi5441-member-groundtruth-kb-templates-skills-bridge-skill-md-0424b16bb6`

Immediately before requesting the transition, the implementer must prove each
legacy backing path is still absent and each canonical renamed destination is
present at the current bytes:

| Absent legacy path | Current destination | Current destination SHA-256 |
| --- | --- | --- |
| `groundtruth-kb/templates/skills/baseline-audit/SKILL.md` | `groundtruth-kb/templates/skills/gtkb-baseline-audit/SKILL.md` | `6AAC4B8756207C1F45F17572A1DDB36849312459F5F974BE6D04DF1575DD1991` |
| `groundtruth-kb/templates/skills/bridge/SKILL.md` | `groundtruth-kb/templates/skills/gtkb-bridge/SKILL.md` | `9854463BCCE83D61F51A4E88D12524D974FCA7FAA821DE93AC4803BEB3B18278` |
| `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py` | `groundtruth-kb/templates/skills/gtkb-bridge/helpers/impl_report_bridge.py` | `5A7BB5C105D8C3C0C645C8576EACEF8896CF0BE5A8B7D914818687525B5F94EF` |
| `groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py` | `groundtruth-kb/templates/skills/gtkb-bridge/helpers/revise_bridge.py` | `650C5E4A4A79127AB5CCEF69FD35D3FB724EDEB2617C915D8C8594B9663550B4` |
| `groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py` | `groundtruth-kb/templates/skills/gtkb-bridge/helpers/scan_bridge.py` | `7F1E6EE3D0BBE69A049C419367A8DF6B888AFF3A715458F35E3C2C39BF25A367` |
| `groundtruth-kb/templates/skills/bridge/helpers/show_thread_bridge.py` | `groundtruth-kb/templates/skills/gtkb-bridge/helpers/show_thread_bridge.py` | `1C0F1F6D61C130A02AD9BA4892097CD6E2DB972FED356E41B02A522809DB8C6B` |

If any legacy path exists, any destination is absent, any destination digest
has drifted without reviewed disposition, or the exact six identity records do
not retain the observed absent-backing-path condition, stop without requesting
or applying a transition.

## Governed Implementation Sequence

1. Revalidate the project, active list-free PAUTH v2, current WI-6075
   membership, exact target collision state, exact bridge `GO`, exact
   go-implementation claim, and fresh schema-v3 implementation-start packet.
2. Open a fresh operation-scoped session envelope for the acting Prime Builder.
3. Run registry inspect, validate, diff, and reconciliation readbacks and bind
   the exact live generation and exact six-identity set.
4. Run `gt registry transition request` once with
   `operation=membership_set`, exactly six `removal` values, no additions, no
   coverage changes, `DELIB-20260808012018`, this bridge thread, the exact
   session/start packet/PAUTH evidence, and a narrowly descriptive change
   reason.
5. Inspect the request and require an exact generation-bound, unexpired,
   unused request whose removal set is byte-for-byte equal to this proposal.
6. Run the transition apply dry-run and preserve its exact receipt.
7. Run `gt registry transition apply` once with this thread's independent
   `GO`, exact OPS envelope, exact request, session, packet, PAUTH, changed-by,
   change reason, and dry-run receipt.
8. Read back the consumed request, committed journal transaction, receipt, both
   declarations, MemBase projection, registry validation, registry identity,
   and reconciliation results.
9. File a truthful implementation report on this thread with exact hashes,
   transaction/request/receipt identifiers, command results, and collision
   evidence for independent verification.

No second apply is authorized. If the request becomes stale or the operation
enters a recoverable journal state, stop and use only the typed registry
recovery surface under its own current authority. Never repeat the apply,
delete a sidecar, edit a journal row, or restore files manually.

## Required Postconditions

- Both registry TOMLs are byte-identical and match the authoritative projected
  generation.
- Registry identity is current and `missing=[]`.
- `invalid_unknown=0`, `unregistered_load_bearing=0`, and
  `membership_complete=true`.
- Exactly the six listed identities are removed; all other record identities,
  paths, coverage modes, notes, and artifact hashes are unchanged.
- The request is consumed once and the journal/receipt is committed and bound
  to the exact generation, operation, authorization, session, and six-ID set.
- If there is no concurrent legitimate registry change, the resulting record
  count is 1,445. The authoritative acceptance condition is the exact six-ID
  delta and coherent receipt-bound postimage, not an unguarded count alone.
- No backing artifact, source, test, dispatcher, TAFE, Git index, credential,
  external system, deployment, or release state changes.

## Explicit Exclusions

- No reuse of request `REGTXNREQ-35314F896AE4436A9A25DF5EBE02FF75`, journal
  `SOTTXN-168C5979328445B6828F2DC393269A5B`, or the consumed v002 `GO` on the
  former authorization thread.
- No raw TOML, SQLite, or projection-table edit.
- No file deletion, move, rename, restoration, or content edit.
- No addition, amendment, coverage change, or removal beyond the six exact IDs.
- No absorption of WI-5925, WI-6078, WI-5702, or foreign worktree changes.
- No emergency-bootstrap bypass while the ordinary governed publication and
  transition route remains available.
- No dispatcher, TAFE, daemon, provider, credential, Git history, push,
  deployment, release, or external-system mutation.

## Requirement Sufficiency

Existing requirements are sufficient. `DELIB-20260808012018` already selects
governed retirement of the exact six stale identities. This proposal does not
create a new requirement or change owner intent; it restores the one-use
governed transition route after a later parity repair reintroduced the six
records. No waiver is requested.

## Specification Links

- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `ADR-REGISTRY-AUTHORITATIVE-ARTIFACT-LIFECYCLE-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Specification-Derived Verification Plan

| Requirement | Verification evidence | Acceptance |
| --- | --- | --- |
| Independent mutation authority | Canonical bridge readback, role/session metadata, and publication receipt | Fresh independent `GO` binds this exact carrier and six-ID scope |
| Operation-time authority | Claim, schema-v3 packet, PAUTH evaluation, OPS envelope, and request/apply audit fields | All current and exact at request and apply |
| Exact removal set | Pre/post canonical record snapshots and request digest | Six listed IDs removed; zero other identity or field changes |
| Generation atomicity | Dry-run receipt, consumed request, committed journal, final receipt, declaration/projection digests | One coherent generation and one consumed apply |
| Registry identity | `gt registry inspect`, `validate`, `diff`, and `reconcile` readbacks | No missing identities; invalid unknown zero; membership complete |
| Rename boundary | Direct existence/hash checks for six legacy/current pairs | Legacy absent; reviewed current destinations present at accepted bytes |
| Scope containment | Exact target status, Git diff, dispatcher/TAFE status | Only governed registry transaction surfaces change |
| Failure behavior | Stale-generation/request and mismatch negative checks | Fail closed without widening, retry, or manual repair |

Independent Loyal Opposition verification must reproduce these readbacks and
must not rely solely on the Prime Builder's report.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260808012018, WI-6075, and the current coherent 1451-record registry generation",
  "canonical_authority": "the governed registry transition control plane, exact owner decision, current PAUTH, independent bridge GO, claim, schema-v3 start packet, and receipt-bound journal",
  "primary_route": "one fresh generation-bound membership_set request and one independently authorized apply for exactly six identities",
  "before_behavior": "six absent pre-rename WI-5441 template identities are registered, so the coherent registry still reports six invalid unknown records and incomplete membership",
  "after_behavior": "the same registry generation minus exactly those six identities is coherent, receipt-bound, identity-current, and membership-complete",
  "self_descriptive_naming": "the carrier name states WI-6075, the reintroduced-six incident, identity transition, and authorization purpose",
  "obsolete_guidance_disposition": "the former one-use authorization is preserved as consumed history and is explicitly prohibited from reuse",
  "history_preservation": "all former requests, journals, receipts, bridge versions, owner decisions, and reintroduction evidence remain append-only",
  "baseline": {
    "record_count": 1451,
    "invalid_unknown": 6,
    "unregistered_load_bearing": 0,
    "membership_complete": false
  },
  "expected_result": {
    "removed_identity_count": 6,
    "other_record_changes": 0,
    "invalid_unknown": 0,
    "unregistered_load_bearing": 0,
    "membership_complete": true
  },
  "rollback": {
    "instructions": "do not perform a raw inverse; an unused or denied request changes nothing, and any post-prepare failure uses only typed registry recovery under current authority",
    "verification": "re-read the request, journal, receipts, declarations, projection, identity, and reconciliation state before any further action"
  },
  "hard_invariants": [
    "exactly six named identities and no other registry record are removed",
    "no backing file content or path is mutated",
    "canonical declaration, packaged declaration, and MemBase projection remain one coherent generation",
    "the old request, journal, and GO are never reused",
    "all foreign worktree and runtime state remains unabsorbed"
  ],
  "fail_closed_conditions": [
    "missing or stale GO, claim, packet, PAUTH, OPS envelope, or request",
    "generation or exact identity-set drift",
    "legacy path reappearance or current destination loss",
    "unexpected target or claim collision",
    "dry-run/live receipt mismatch",
    "journal or projection incoherence"
  ],
  "essential_context_preservation": "the proposal preserves the original owner-selected WI-6075 retirement, the consumed first transition, the later reintroduction evidence, and the registry's governed single-writer transaction semantics"
}
```

## Risk And Recovery

The material risk is accidental removal beyond the six identities or replay of
consumed authority. Exact ID binding, generation CAS, request expiry, distinct
independent `GO`, claim/start/PAUTH/OPS evidence, dry-run receipt binding, and
one-use consumption mitigate that risk. A pre-apply mismatch changes nothing.
A post-prepare failure is recoverable only through the typed registry recovery
surface; this proposal authorizes no manual rollback.

## Prior Deliberations And Governed History

- `DELIB-20260807012015` — earned registration and closure-before-sweep.
- `DELIB-20260808012018` — controlling owner disposition for the exact six
  stale-identity retirements.
- `DELIB-20260808-WI6077-WI6081-LEAD-PRIME-COMPLETION-DIRECTIVE` — directs
  governed reliability-program completion without bypassing review gates.
- `bridge/gtkb-wi6075-registry-membership-closure-001.md` through `-005.md` —
  parent implementation and later evidence/finalization history.
- `bridge/gtkb-wi6075-registry-transition-apply-authorization-001.md` through
  `-003.md` — prior one-use authorization, consumed request, and NO-ACTION
  closure; authoritative history but not current mutation authority.
- `bridge/gtkb-wi6075-registry-transition-apply-authorization-002.md` — the
  consumed independent `GO`; explicitly not reusable.
- `WI-6078` — identifies WI-6075 as the single lawful membership-repair carrier
  and forbids a competing repair lane.

## Files Changed

This proposal publication changes only the append-only bridge artifact and its
governed publication bookkeeping. A later independently approved implementation
may mutate only the three declared registry transaction targets through the
control plane.

## Owner Action Required

None. The existing owner decision is exact. Independent Loyal Opposition review
is required before any registry mutation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
