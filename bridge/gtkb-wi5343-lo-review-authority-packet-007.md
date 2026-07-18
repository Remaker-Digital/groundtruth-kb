REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope
author_metadata_source: explicit_interactive_session_metadata

# WI-5343 Canonical LO Review Authority Packet - Collision-Cleared Revision

bridge_kind: prime_proposal
Document: gtkb-wi5343-lo-review-authority-packet
Version: 007
Responds to: bridge/gtkb-wi5343-lo-review-authority-packet-006.md
Revises: bridge/gtkb-wi5343-lo-review-authority-packet-001.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5343-LO-REVIEW-AUTHORITY-PACKET-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5343
Related Work Items: WI-5255, WI-5307, WI-5389
target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]
implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

## Revision Claim

Every version-006 blocking condition is accepted and re-evaluated against
current canonical state.

The corrected proposal is now self-contained:

- it carries the complete current `Specification Links` set rather than asking
  a future corrected verdict to reconstruct the version-001 packet;
- it maps each governing behavior to executable tests and operation-time
  evidence;
- it records a fresh exact target baseline;
- it proves the second colliding thread, WI-5389, reached independent terminal
  `VERIFIED` and focused finalization; and
- it preserves the same two-file behavior boundary and active WI-5343 PAUTH.

No source or test change has started. This revision requests independent review
of the corrected plan only.

## Findings Addressed

### F1 - Corrected verdict was not specification-self-contained

Resolved at the proposal layer. This revision carries all relevant governing
specifications and a concrete specification-derived verification table. A
future verdict can review and carry this complete packet without relying on a
thin version-004 corrected GO.

### F2 - Live WI-5389 target collision

Resolved.

`gtkb-wi5389-codex-no-window-schema-contract` is now terminal `VERIFIED` at
v004 and focused-finalized in commit
`0bb45100ac922552aa4ec1c3879bc775e3e915a0`
(`fix(dispatch): unify Codex no-window schema contract`).

Fresh scoped Git checks return no output for either WI-5343 target. Their exact
current baselines are:

| Path | Length | SHA-256 | Git blob |
| --- | ---: | --- | --- |
| `scripts/dispatcher_runtime.py` | `361045` | `82936478AD1BE752F996328D93AD84C08F9960C58F5355992E441E75718F2CF6` | `f51c5e9ee844f1110ea5e96b0e6667be479bdaa0` |
| `platform_tests/scripts/test_dispatcher_runtime.py` | `344723` | `B23F9CBF707462F13BA1CEF0E6A7991FDE37ABAF0481EFE2CC1B7F8051E8E536` | `0425ee4297ebc5ae6a6e857216143a3e87bc37ae` |

The WI-5343 feature remains absent. A targeted source search finds no
dispatched-LO authority block naming `gt bridge show`, `bridge_claim_cli.py
status`, or complete-numbered-chain target ownership. Existing unrelated
work-intent implementation references do not satisfy this proposal.

### Original WI-5255 collision

Remains resolved by terminal WI-5255 v008 and its focused carrier. No
WI-5255 byte is uncommitted in the current targets.

## Requirement Sufficiency

Existing requirements sufficient.

The active PAUTH and linked specifications define a bounded prompt-composition
hardening slice. No new authority, dispatcher topology, claim semantic, or
owner decision is required.

## Proposed Scope

1. Add an LO-only review-authority block to the dispatcher-composed task packet.
2. Require the complete numbered bridge chain for target ownership:
   - read the exact assigned thread through the canonical `gt bridge show`
     surface or equivalent complete numbered-chain packet;
   - derive owned targets from proposal/report `target_paths` across that
     chain;
   - treat current numbered status and independently terminal/finalized
     evidence as controlling.
3. Require claim ownership checks through the repository-venv canonical
   `scripts/bridge_claim_cli.py status <slug>` route backed by the canonical
   claim service.
4. Explicitly reject backlog/MemBase summaries, startup summaries, copied
   excerpts, cached aggregate views, and retired runtime claim directories as
   target-ownership or live-claim authority.
5. Preserve MemBase as canonical backlog/project authority while clarifying
   that a backlog summary is not a substitute for an exact numbered bridge
   target chain or live claim record.
6. Preserve Prime Builder prompt behavior, target selection, routing,
   dispatcher topology/configuration/runtime state, TAFE state, provider
   adapters, worker lifecycle, and unrelated source/test behavior.
7. Add focused tests proving LO-only inclusion, complete authority wording,
   canonical claim route, projection non-authority, provider-neutral behavior,
   and Prime prompt non-impairment.

## Hard Implementation-Start Gates

1. WI-5389 v004 remains terminal `VERIFIED` and commit
   `0bb45100ac922552aa4ec1c3879bc775e3e915a0` remains its focused carrier.
2. Both exact WI-5343 targets remain clean, unclaimed, and at the baseline
   identities above, or any drift has a separately terminal/focused owner and
   is explicitly adopted after fresh independent review.
3. The active WI-5343 PAUTH remains current, WI-only, and limited to
   bridge/metadata/source/test.
4. A fresh WI-5343 `GO`, exact same-session `go_implementation` claim,
   schema-v3 implementation-start packet, and per-target operation-time
   authorization all cover the same project, work item, thread, paths,
   mutation classes, and session.
5. No whole-file overwrite, foreign-hunk adoption, active-worker
   interruption, or unrelated test change is permitted.
6. Any dispatcher topology/configuration/runtime, TAFE, harness registry,
   credential, external-system, release, deployment, Git push/history rewrite,
   destructive-cleanup, or unrelated worktree request fails closed.

## Cross-Harness Disposition

The dispatched review instruction is provider-neutral and applies only when
the selected task role is Loyal Opposition. Claude, Codex, Cursor,
Antigravity, and supported headless providers receive the same canonical
numbered-chain and claim-service authority rules. No harness receives target
ownership from its own cache, provider identity, or runtime directory.

Prime Builder task packets remain behaviorally unchanged. Provider adapter and
harness configuration files are not targets.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`
- `bridge/gtkb-wi5343-lo-review-authority-packet-001.md`
- `bridge/gtkb-wi5343-lo-review-authority-packet-003.md`
- `bridge/gtkb-wi5343-lo-review-authority-packet-005.md`
- `bridge/gtkb-wi5343-lo-review-authority-packet-006.md`
- `bridge/gtkb-wi5255-bc-telemetry-worker-provenance-008.md`
- `bridge/gtkb-wi5389-codex-no-window-schema-contract-003.md`
- `bridge/gtkb-wi5389-codex-no-window-schema-contract-004.md`

## Owner Decisions / Input

No new owner decision is required.

`PAUTH-DISPATCHER-BLACK-BOX-WI5343-LO-REVIEW-AUTHORITY-PACKET-20260716`
remains active for exactly WI-5343 and the two declared source/test targets.
All ordinary bridge, claim, start, operation-time, independent review, and
focused finalization gates remain mandatory.

## Specification-Derived Verification

| Requirement | Executable verification | Required result |
| --- | --- | --- |
| Numbered bridge authority | Focused `_dispatch_prompt` test for LO tasks containing canonical `gt bridge show`, complete-chain target derivation, latest-status handling, and terminal/finalized ownership rules | LO packet directs reviewers to exact numbered authority, not summaries. |
| Canonical claim authority | Focused LO prompt test for repository-venv `scripts/bridge_claim_cli.py status <slug>` and DB-backed claim wording | Claim checks use the canonical live service only. |
| Projection non-authority | Negative prompt assertions for backlog/startup/copied/cache/runtime-directory ownership wording | Context surfaces cannot establish target or claim ownership. |
| Prime non-impairment | Compare Prime task prompt before/after and run existing Prime dispatch prompt tests | No WI-5343 authority block is injected into Prime tasks; routing and selection unchanged. |
| Centralized dispatcher ownership | Focused source review and dispatch-prompt tests | Change remains in dispatcher-owned prompt composition, not provider adapters. |
| Harness parity/isolation | Parametrized LO task packets across supported harness/provider descriptors | Identical authority block; no provider identity grants or weakens ownership. |
| Operation-time authorization | Re-check PAUTH, exact claim, schema-v3 start, target baselines, session, and per-target authorization | All authority agrees; any target drift blocks before mutation. |
| Worktree hygiene | Exact target hashes/status before and after plus target-only diff and whitespace checks | Only WI-5343-owned hunks change. |
| Mandatory bridge gates | Candidate/live applicability and clause preflights | No missing required/advisory specs, errors, or blocking gaps. |

Required focused commands include:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short -k "lo_review_authority or dispatch_prompt"
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py
git diff --check -- scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py
```

## Acceptance Criteria

1. Every dispatched LO task packet contains explicit complete numbered-chain
   target-ownership instructions and the canonical live claim-status route.
2. The packet states that backlog summaries, startup summaries, copied
   excerpts, cached aggregates, and retired runtime claim directories are not
   target or live-claim authority.
3. Tests prove LO-only behavior, provider-neutral parity, and Prime prompt
   non-impairment.
4. WI-5389 remains terminal/focused-finalized and both targets remain clean at
   implementation start.
5. No dispatcher topology/configuration/runtime, TAFE, harness registry,
   credential, external-system, deployment, release, Git push/history,
   destructive cleanup, live-worker interruption, or unrelated mutation
   occurs.

## Scope Changes

- Replaces the thin corrected-verdict repair request with a complete
  self-contained proposal.
- Adds current terminal WI-5389 and exact clean-baseline evidence.
- Adds operation-time collision, provider parity, and Prime non-impairment
  gates.
- Preserves the original two targets and behavior goal.

## Pre-Filing Preflight Subsection

Candidate applicability preflight:

- Command:
  `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5343-lo-review-authority-packet --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5343-lo-review-authority-packet-007.md --json`
- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `blocking_errors: []`
- packet hash:
  `sha256:13836b45d14420a6327daa618c4aef02744813bede61353ff55118b198750c07`

Mandatory clause preflight:

- Command:
  `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5343-lo-review-authority-packet --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5343-lo-review-authority-packet-007.md`
- clauses evaluated: 5
- `must_apply: 3`
- `may_apply: 2`
- evidence gaps in must-apply clauses: 0
- blocking gaps: 0
- result: PASS (exit 0)

## Risk And Rollback

The primary risks are prompt overreach, stale ownership wording, and collision
with later dispatcher-runtime work. LO-only composition, exact positive and
negative prompt tests, target ownership checks, and operation-time
authorization address those risks.

Rollback is a focused revert of WI-5343-owned hunks only. No whole-file
restore, dispatcher/configuration rollback, bridge-history rewrite, or
unrelated cleanup is authorized.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
