REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; substantive post-NO-GO revision; dispatcher and TAFE deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5542-ollama-publisher-envelope-recovery
Version: 007
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5542-ollama-publisher-envelope-recovery-006.md
Revises: bridge/gtkb-wi5542-ollama-publisher-envelope-recovery-001.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5542-OLLAMA-PUBLISHER-ENVELOPE-RECOVERY-20260718
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5542

target_paths: ["scripts/ollama_harness.py", "platform_tests/scripts/test_ollama_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
approval_evidence_work_in_scope: false

KB Mutation: This proposal performs no MemBase or `groundtruth.db` mutation,
write, insert, change, or edit.

# Revised Implementation Proposal — WI-5542 Ollama Publisher-Envelope Recovery

## Revision Response To Version 006

Prime Builder accepts the version-006 NO-GO in full. Versions 003 and 005
incorrectly treated the absence of a live claim as terminal disposition
evidence. Prime Builder withdraws that disposition-close premise. Version 004
did not implement, verify, withdraw, or supersede the bounded design approved
in version 002, and `NO-ACTION` cannot close the review lane.

This revision restores the still-required WI-5542 implementation as pending,
rebinds it to the now-executable version-2 project authorization, records the
current exact target baselines, and narrows the activation statement to the
remaining predecessor. It does not claim implementation and authorizes no
source or test mutation by itself.

## Summary

After an Ollama D reviewer has authored a substantive review but has not
successfully published its governed verdict, replace dependence on provider
tool-selection enforcement with a D-specific publisher-envelope recovery turn.
The recovery turn requests exactly one JSON verdict envelope without exposing
tools, validates the envelope locally against the trusted assigned-document
state and canonical publisher contract, and invokes the existing
`PublishBridgeVerdict` execution path only for one valid assigned target.

Malformed JSON, mixed prose, missing or extra fields, role-invalid status,
incomplete verdict body, duplicate target, unassigned target, or an extra
action fails closed. Such failures consume the existing bounded recovery
policy and produce a bounded, credential-redacted diagnostic; they never count
as publication or completion.

## Claim

Prime Builder proposes only the bounded two-target implementation originally
reviewed at version 002, updated for current authority and dependency state.
Protected implementation remains held until WI-5545 is terminal, this revised
proposal receives a fresh independent `GO`, a fresh matching
`go_implementation` claim is acquired, and a schema-v3 implementation-start
packet is issued from then-current bytes.

## Requirement Sufficiency

Existing requirements sufficient. The linked specifications, WI-5542, the
original technical review, the version-006 correction, and the active
version-2 PAUTH fully define this bounded recovery slice. No new or revised
formal requirement is needed before implementation. The remaining WI-5545
condition is a sequencing and exact-target ownership hold, not a requirement
gap or owner-decision gap.

## In-Root Placement Evidence

Both targets resolve inside `E:\GT-KB`:

- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

No out-of-root source, test, runtime, configuration, or scratchpad artifact is
a live dependency.

## Active Authorization And Approval Evidence

`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5542-OLLAMA-PUBLISHER-ENVELOPE-RECOVERY-20260718`
is active at version 2. It includes WI-5542, allows `bridge`, `metadata`,
`source`, and `test`, and uses only registered forbidden-operation tokens:
`credential_lifecycle`, `destructive_cleanup`, `dispatcher_mutation`,
`external_system_mutation`, `git_history_rewrite`, `git_push`,
`production_deployment`, and `release`.

The version-2 scope preserves the narrower non-mutation boundaries: no secret
value disclosure, direct harness-to-harness invocation, provider request,
dispatcher configuration/role/identity/selection/ranking/routing change,
automatic turn-budget change, or automatic production-dispatch selection
change. The owner decision remains
`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`; the version-2
normalization did not change the included work item, linked-spec sets,
mutation classes, or substantive scope.

## Current Target Baseline

The two exact targets are tracked, unstaged, staged, and worktree clean at
candidate authoring time.

| Target | Raw SHA-256 | Size | Current behavior |
|---|---|---:|---|
| `scripts/ollama_harness.py` | `B13F453C29B99C5CB5919649B8BC11BC160F94CDF94E8E3FEE1FEEFA8A442EF1` | 68,954 bytes | Publisher-only recovery still offers only `PublishBridgeVerdict` and rejects a provider-selected nonpublisher tool; no no-tools exact-envelope validator exists. |
| `platform_tests/scripts/test_ollama_harness.py` | `47A713DA83D6E6C366989DF5094905529204C872FA49CCA28FD769E8EE7A88EF` | 63,707 bytes | Current regressions assert the legacy four-attempt rejection/exhaustion path; no exact-envelope success/failure matrix exists. |

The source baseline corresponds to Git blob
`c8e970a8b426c102c16e6366ad685825ce236eff`; the test baseline corresponds to
Git blob `8d989ca17be59cc1741ea60f47f62e991955ffc9`. A future implementation-start
must fail closed and return for review if either raw hash, blob identity,
cleanliness state, PAUTH decision, claim state, or predecessor state changes.

## Dependency And Exact-Target Ownership

- WI-5495 is resolved and its thread is terminal `VERIFIED` at version 011.
- WI-5471 is resolved and its thread is terminal `VERIFIED` at version 006.
- WI-5545 remains open; `gtkb-wi5545-per-document-provider-completion` is
  current `NO-GO` at version 006. Its approved design owns both exact WI-5542
  targets and supplies the trusted per-assigned-document state needed for a
  two-item D batch.
- No live WI-5542 claim exists, and no current exact-target claim collision was
  present at candidate authoring time.

WI-5545 is therefore the sole remaining exact-target and design predecessor.
No WI-5542 source or test mutation, claim acquisition, or implementation-start
packet is permitted until WI-5545 reaches a genuine terminal state and the two
targets are freshly reconciled clean. Terminalization alone is not authority:
fresh independent `GO`, claim, and schema-v3 start remain mandatory afterward.

## Proposed Scope

1. Add a D-specific recovery state entered only when a governed verdict is
   required, substantive provider work has occurred, and canonical publication
   has not advanced the trusted assigned-document state.
2. In that state, make a provider turn whose payload exposes no tools and whose
   prompt requests exactly one JSON object containing the canonical publisher
   arguments for one still-pending assigned document.
3. Parse one object only. Reject blank content, malformed JSON, arrays, fenced
   payloads, prose prefixes/suffixes, duplicate keys, unknown keys, extra
   actions, or non-string fields where strings are required.
4. Validate the document slug against WI-5545's trusted per-assigned-document
   state, reject already-advanced, duplicate, or unassigned slugs, and validate
   verdict/status/body and any status-specific finalization arguments against
   the existing canonical `PublishBridgeVerdict` contract.
5. Dispatch the existing canonical publisher path only after all local checks
   pass. Do not write bridge bytes directly, relax the publisher guard, infer a
   substantive verdict, or silently rewrite the provider's GO/NO-GO/VERIFIED
   choice.
6. Treat a valid nonblank canonical `verdict_path` as publication success only
   after the trusted assigned-document state advances. Otherwise return the
   existing bounded, credential-redacted diagnostic and continue only within
   the existing recovery policy.
7. Preserve ordinary Ollama tool turns, model route, D eligibility and LO role,
   current max-items, worker/model/operation/session allowances, claim and
   lease rules, TAFE state, dispatcher topology, and canonical finalization.

## Explicit Exclusions

- No cloud-harness, dispatcher, TAFE, routing, registry, lease, role, identity,
  max-items, model-route, provider-account, environment, or credential change.
- No direct provider request is part of implementation or deterministic test
  verification; provider calls in tests are local fakes.
- No bridge writer, publisher, finalizer, claim, or PAUTH behavior change.
- No direct bridge-file mutation, database mutation, Git commit/push/history
  operation, deployment, release, or destructive cleanup.
- No implementation before WI-5545 terminal and no expansion into WI-5545's
  per-document state design.

## Timer, Retry, Threshold, And Concurrency Disposition

This slice introduces no hard-coded timeout, TTL, interval, retry, throttle,
threshold, fan-out, or concurrency literal and does not retune an existing
value. The existing `MAX_BRIDGE_VERDICT_RECOVERY_TURNS = 3` remains unchanged
in this slice. The motivating four failures repeated a deterministic provider
capability mismatch; they do not establish that the recovery count is too
short, and increasing it would only prolong the same invalid mechanism.

WI-5804 owns deterministic inventory and evidence classification for this
existing retry count. WI-5806 owns its later externalization through the
centralized timer/retry/threshold/concurrency source of truth with a
relaxed-first, data-driven default. WI-5542 neither duplicates nor preempts
those work items. Tests refer to the resolved configured/current policy rather
than adding a second numeric literal.

## Cross-Harness Disposition

- **A / Codex:** Prime Builder governance and implementation lane remains
  unchanged; no provider behavior is added to A.
- **D / Ollama:** Sole runtime behavior target. Recovery becomes a no-tools,
  locally validated envelope route after normal canonical publication fails to
  advance an assigned document.
- **F / OpenRouter:** No source or test target in this slice; shared
  per-document semantics remain owned by WI-5545.
- **B, C, E, G, H:** No eligibility, role, routing, model, cap, prompt,
  publisher, or runtime change.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — preserve the active harness role,
  route, execution, provenance, and governed publication contract.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — preserve dispatcher selection,
  assigned-document, lease, completion, and topology semantics.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` — meet the common governed publisher
  outcome without claiming unsupported provider tool-selection capability.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — require numbered append-only review,
  independent GO, claim, implementation-start authority, report, and VERIFIED.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — bind the exact mutation to
  the active project authorization and listed two-target cohort.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — re-evaluate
  version-2 PAUTH for packet creation and implementation start before effects.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — preserve the PAUTH,
  project, work-item, and inline-JSON target metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — carry all
  applicable requirements into the proposal and report.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — require independent
  execution of every mapped test before VERIFIED.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — preserve legitimate ordinary
  tool turns, fail-closed publication, topology, and unrelated harnesses.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — retain durable WI, proposal,
  review, authority, test, report, and verdict relationships.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — keep traceability between the
  defect, authority, source, tests, and review evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — represent pending, held, approved,
  implemented, and verified states without treating inactivity as closure.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — keep platform harness behavior
  and tests inside the GT-KB root, outside adopter application scope.
- `GOV-STANDING-BACKLOG-001` — retain timer externalization and tuning work in
  WI-5804/WI-5806 without silently implementing it here.
- `SPEC-AUQ-POLICY-ENGINE-001` — no owner question is necessary because the
  requirements, project approval, and active bounded PAUTH are sufficient.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — preserve self-enforced bridge,
  claim, start, scope, and verification boundaries in Codex sessions.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` — owner-approved
  fleet defect-repair authority carried by PAUTH version 2.
- `DELIB-202666850` — selected graceful Ollama publisher recovery rather than
  a transport switch.
- `DELIB-202666257` — Loyal Opposition review of the WI-5253 recovery lineage.
- `DELIB-202666204` — owner authorization for the WI-5253 recovery lineage.
- `DELIB-202666256` — independent verification of WI-5253 recovery.
- `DELIB-202666410` — review of bounded abrupt-exit diagnostics.
- `DELIB-202667722` — timer and throttle governance; no new hard-coded value.
- `DELIB-202667748` — centralized timers, retries, thresholds, fan-out, and
  per-harness concurrency with evidence-triggered, data-driven tuning.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` supplies the
  owner decision for this bounded project-authorized repair.
- The owner's project-level approval rule applies to WI-5542 through its active
  project membership and the active WI-specific PAUTH version 2.
- The timer/concurrency direction is already captured by `DELIB-202667722` and
  `DELIB-202667748`; this proposal introduces no competing configuration
  decision.
- No additional owner decision is required. The WI-5545 hold must be resolved
  through its governed bridge lifecycle, not by an AUQ bypass.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5542, bridge versions 001 through 006, DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION, DELIB-202667722, and DELIB-202667748",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; GOV-HARNESS-ONBOARDING-CONTRACT-001; SPEC-CENTRALIZED-DISPATCH-SERVICE-001; DCL-OLLAMA-TOOL-PARITY-GATE-001",
  "primary_route": "scripts/ollama_harness.py run_tool_loop publisher-recovery branch after WI-5545 trusted per-assigned-document state is terminally available",
  "before_behavior": "Ollama publisher-only recovery keeps exposing one publisher tool, but a provider that does not honor tool selection can return Bash or another call and exhaust four repeated failures without a governed verdict.",
  "after_behavior": "Ollama publisher recovery requests one exact no-tools JSON envelope, validates it locally for one pending assigned document, and invokes the unchanged canonical publisher only after validation.",
  "self_descriptive_naming": "Envelope parsing, validation, assigned-target checks, and bounded recovery diagnostics use publisher-verdict and assigned-document terminology rather than provider-specific guesses.",
  "obsolete_guidance_disposition": "Versions 003 and 005 remain historical evidence but their disposition-close premise is explicitly withdrawn; no prior bridge byte is rewritten or deleted.",
  "history_preservation": "The numbered bridge chain, PAUTH versions, WI lineage, target baselines, timer-governance ownership, and future implementation report remain append-only and independently reviewable.",
  "baseline": {
    "source_sha256": "B13F453C29B99C5CB5919649B8BC11BC160F94CDF94E8E3FEE1FEEFA8A442EF1",
    "test_sha256": "47A713DA83D6E6C366989DF5094905529204C872FA49CCA28FD769E8EE7A88EF",
    "target_state": "both exact targets clean",
    "legacy_recovery_attempts": 4,
    "remaining_predecessor": "WI-5545 current NO-GO version 006"
  },
  "expected_result": {
    "valid_assigned_envelope": "exactly one canonical publisher invocation and trusted assigned-document advancement",
    "invalid_envelope": "bounded redacted diagnostic, zero publisher invocation, and zero completion credit",
    "ordinary_tool_turns": "unchanged",
    "other_harnesses": "unchanged",
    "timer_policy": "no new literal or retuning; WI-5804 and WI-5806 remain owners"
  },
  "rollback": {
    "instructions": "Revert only the independently reviewed WI-5542 source and focused-test hunks after preserving the report and verdict chain.",
    "test": "python -m pytest platform_tests/scripts/test_ollama_harness.py -q --tb=short"
  },
  "hard_invariants": [
    "no direct bridge write",
    "no provider-authored envelope counts as publication before canonical publisher success",
    "no unassigned or duplicate target can publish",
    "no substantive verdict status is inferred or silently rewritten",
    "no dispatcher, TAFE, route, role, cap, lease, credential, or provider-account mutation",
    "no implementation before WI-5545 terminal plus fresh GO, claim, and schema-v3 start",
    "no new timer, retry, threshold, fan-out, throttle, or concurrency literal"
  ],
  "fail_closed_conditions": [
    "WI-5545 nonterminal or target ownership uncertain",
    "target hash or cleanliness drift",
    "PAUTH, claim, or schema-v3 packet invalid",
    "assigned-document context unavailable or inconsistent",
    "envelope malformed, mixed, incomplete, duplicated, unassigned, role-invalid, or action-bearing",
    "canonical publisher returns no nonblank verdict path or trusted state does not advance"
  ],
  "essential_context_preservation": "Diagnostics retain the assigned slug and bounded redacted failure class; the complete target-authored substantive body reaches only the canonical publisher and is never treated as completion in prose form."
}
```

## Specification-Derived Verification Plan

| Specification | Required verification and expected result |
|---|---|
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Focused tests prove D remains LO, ordinary tool exposure and metadata remain unchanged, and recovery cannot bypass canonical publication. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Tests use trusted assigned-document context, reject unassigned/duplicate/already-advanced slugs, and require state advancement before completion. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | A deterministic fake provider ignores tool selection in the motivating legacy case, then succeeds through the no-tools envelope route without claiming tool-choice support. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Before edits, verify WI-5545 terminal, latest v007 `GO`, fresh claim, and valid schema-v3 start; after edits, file a numbered report and require independent VERIFIED. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Operation-time preflight selects active PAUTH v2 and permits only the exact source/test cohort. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Candidate applicability and implementation-start evaluations report `allowed` for packet creation/start with no unknown taxonomy token. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Compliance audit confirms the exact PAUTH/project/WI and inline-JSON target metadata. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate applicability preflight reports no missing required or advisory specifications and no blocking error. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO reruns every command below and maps observed results to every linked specification before VERIFIED. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Full focused Ollama suite remains green; ordinary tool turns, canonical publisher failures, final prose gating, telemetry, and redaction behavior remain unchanged outside the new branch. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Report carries forward WI, PAUTH, predecessor, target hashes, test evidence, risks, and timer-program disposition. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Exact diff and report evidence preserve traceability from incident to source/test cases. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Tests and bridge state distinguish held, approved, implemented, failed, and verified outcomes without inactivity closure. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only` contains only the two declared in-root platform targets. |
| `GOV-STANDING-BACKLOG-001` | Diff inspection proves no WI-5804/WI-5806-owned timer/configuration implementation is absorbed. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Authority and requirements remain sufficient; no new owner decision is synthesized. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Prime Builder self-enforces latest GO, exact claim, schema-v3 packet, target scope, and independent review even if native hooks do not run. |

### Required Commands After Authorized Implementation

```powershell
python -m pytest platform_tests/scripts/test_ollama_harness.py -q --tb=short
python -m ruff check scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py
python -m ruff format --check scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py
python -m py_compile scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py
git diff --check -- scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py
git diff --name-only -- scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py
python scripts/bridge_applicability_preflight.py --content-file <completed-report-candidate> --json
python scripts/adr_dcl_clause_preflight.py --content-file <completed-report-candidate>
```

The implementation report must record exact observed results rather than
promising future execution. Diff review must additionally prove that
`MAX_BRIDGE_VERDICT_RECOVERY_TURNS` is unchanged and that no new numeric timer,
retry, interval, threshold, throttle, fan-out, or concurrency literal appears.

## Focused Regression Matrix

1. A valid exact GO envelope for one pending assigned slug invokes the
   canonical publisher exactly once and advances that slug.
2. A valid exact NO-GO envelope preserves the target-authored body and status.
3. A VERIFIED envelope missing status-specific finalization arguments fails
   closed without publisher invocation.
4. Malformed JSON, array roots, duplicate keys, fenced JSON, mixed prose,
   unknown fields, extra actions, blank body, status/body mismatch, wrong role,
   unassigned slug, duplicate slug, and already-advanced slug each fail closed.
5. A canonical publisher denial or blank `verdict_path` remains bounded,
   credential-redacted, and non-completing.
6. The recovery provider payload exposes no tool schema; ordinary non-recovery
   turns retain the existing allowed-tool schemas.
7. The existing motivating nonpublisher recovery fixture no longer dispatches
   Bash or loops on forced publisher selection once envelope recovery begins.
8. WI-5545 per-document state remains authoritative when two documents are
   assigned; one success cannot complete the second.
9. Existing telemetry stop reasons, repeated-signature protection, final-prose
   gate, tool-argument recovery, timeouts, and session allowances remain green.

## Acceptance Criteria

1. WI-5545 is terminal and both targets are freshly clean before a fresh GO,
   claim, or schema-v3 start is used.
2. A valid assigned target-authored envelope produces exactly one canonical
   `PublishBridgeVerdict` invocation and counts as complete only after a
   nonblank verdict path and trusted assigned-document advancement.
3. Every malformed, mixed, incomplete, duplicate, unassigned, already-
   advanced, role-invalid, or extra-action envelope produces zero publisher
   invocation and zero completion credit.
4. No direct bridge mutation, inferred verdict, guard weakening, or unvalidated
   envelope can count as success.
5. Ordinary Ollama tool turns, D route/role/cap, TAFE, dispatcher, leases,
   allowances, publisher/finalizer gates, and all unrelated harnesses remain
   unchanged.
6. The complete focused regression matrix, Ruff check, Ruff format check,
   compilation, diff check, candidate applicability, mandatory clause, and
   compliance audits pass with exact observed evidence in the report.
7. No new hard-coded timer, retry, interval, threshold, throttle, fan-out, or
   concurrency literal is introduced, and the existing recovery count is not
   retuned under WI-5542.
8. Independent Loyal Opposition verification is required before terminal
   closure; a later live D dispatch proof, if desired, requires separately
   authorized provider execution and is not fabricated by deterministic tests.

## Pre-Filing Preflight

- Exact candidate applicability command:
  `python scripts/bridge_applicability_preflight.py --content-file .tmp-wi5542-v007.md --json`
- Observed and required result: `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`,
  `blocking_errors: []`, and PAUTH v2 operation-time decisions allowed for
  `implementation_packet_create` and `implementation_start`.
- Mandatory clause command:
  `python scripts/adr_dcl_clause_preflight.py --content-file .tmp-wi5542-v007.md`
- Expected and required result: exit 0 with no blocking gap.
- Compliance audits evaluated these candidate bytes as the proposed
  `bridge/gtkb-wi5542-ollama-publisher-envelope-recovery-007.md`; both the
  canonical config hook and active Claude hook returned no deny or ask reason.

## Risks / Rollback

Primary risk is accepting provider-authored structure as authority. The design
contains that risk by accepting only one strict local envelope, validating it
against trusted assigned-document and publisher contracts, and preserving the
canonical publisher as the only state-changing path.

Secondary risk is collision with WI-5545 or stale target assumptions. The hard
hold, fresh hashes, clean-path check, fresh independent GO, exact claim, and
schema-v3 packet fail closed before any edit.

Another risk is masking a deterministic invalid envelope with excessive
retries. This revision does not change the existing count and leaves
externalization/tuning to WI-5804/WI-5806; stable invalid input remains a
bounded actionable failure.

Rollback is a focused revert of only the independently reviewed WI-5542 hunks
in the two declared targets, followed by the focused Ollama suite and a new
append-only implementation report. Bridge files, PAUTH history, deliberations,
and verification evidence are audit records and are not deleted or rewritten.

## Files Expected To Change

- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
