NO-ACTION
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; governed NO-ACTION correction
author_metadata_source: explicit_interactive_session_metadata

# Prime Builder NO-ACTION - WI-5495 Ollama Protocol Mismatch

bridge_kind: operational_state_change
Document: gtkb-wi5495-publisher-recovery-tool-choice-forcing
Version: 003
Responds to: bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-002.md
Approved proposal: bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5495
target_paths: []

implementation_scope: bridge-disposition only
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## First-Line Role Eligibility Check

PASS. Session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a` is transcript-defined
Prime Builder for harness A and holds the exact `no_action_correction` claim
for this latest-`GO` thread. `NO-ACTION` is the role-correct status for
rejecting a governance-defective Loyal Opposition verdict and grants no
implementation authority.

## Reason

Prime Builder rejects version 002 because it approves an Ollama mechanism that
does not exist on the protocol used by the declared implementation target.

The canonical current source in `scripts/ollama_harness.py` sends chat requests
to Ollama's native `/api/chat` endpoint. The native chat request contract
accepts `tools` but has no `tool_choice` request field. Forced function
selection is available on a different, OpenAI-compatible chat-completions
protocol with a different endpoint and response envelope. Adding
`payload["tool_choice"]` while continuing to call native `/api/chat`, as
versions 001 and 002 require, therefore does not mechanically force
`PublishBridgeVerdict`. The D/Ollama publisher-recovery defect remains.

Implementation began only after the version 002 GO, an exact
`go_implementation` claim, and a schema-v3 implementation-start packet.
Protocol validation before the implementation report then exposed this
mismatch:

- The F/OpenRouter candidate correctly adds forced function selection to its
  actual OpenAI-compatible request.
- The D/Ollama candidate added the same field to the native request and a
  mocked unit assertion that only proved the Python dictionary contained the
  field.
- The ineffective D source and test hunks were removed under the still-live
  implementation claim. Both D target paths are clean relative to HEAD.
- The valid F candidate remains unstaged, uncommitted, and unreported. It is
  quarantined candidate evidence until a revised proposal receives a fresh
  independent GO.
- The implementation claim was released before this correction claim was
  acquired. No implementation report was filed.

No bridge predecessor was deleted or rewritten. No dispatcher configuration,
TAFE state, harness eligibility, lease, database, credential, Git staging,
commit, push, deployment, or release operation occurred.

## Required Corrected Loyal Opposition Action

Process this entry through `review_no_action` and issue `NO-GO` against the
version 001 implementation proposal. The corrected verdict must require Prime
Builder to file a `REVISED` proposal that:

1. preserves the bounded F/OpenRouter forced-function correction;
2. replaces the unsupported native Ollama field with an enforcement mechanism
   that is actually supported by the selected Ollama protocol;
3. if the OpenAI-compatible Ollama endpoint is selected for publisher-only
   recovery, explicitly governs endpoint selection and response-envelope
   normalization while leaving ordinary native turns unchanged;
4. adds tests that prove the actual D request endpoint, request dialect,
   forced-function field, response normalization, and negative controls before
   and after recovery;
5. requires a fresh claim and implementation-start packet before adopting the
   quarantined F candidate or changing either D target; and
6. replaces direct Prime-to-harness smoke language with a genuine,
   dispatcher-produced TAFE/bridge D and F smoke that respects the owner's
   no-direct-harness-contact boundary.

Do not reissue `GO` on the unchanged version 001 proposal. Its D half cannot
satisfy its own mechanical-enforcement claim or live-smoke acceptance
criterion.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5495 remains a bounded reliability
defect under the active standing project authorization. The failure is in the
approved implementation mechanism and test fidelity, not a missing owner
requirement. No new owner decision is required before a corrected `NO-GO` and
Prime `REVISED` proposal.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`

## Prior Deliberations

- `DELIB-202666257` - prior governed Ollama publisher-failure recovery review.
- `DELIB-202666256` - prior governed Ollama publisher-recovery verification.
- `DELIB-202666227` - provider-verdict completion contract verification.
- `DELIB-202666174` - governed verdict-publication parity review.
- `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-001.md` - the
  proposal whose Ollama protocol assumption requires correction.
- `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-002.md` - the
  rejected GO.

## Owner Decisions / Input

No new owner decision is requested or inferred. Existing owner direction
requires genuine governed dispatcher-produced harness work and prohibits
direct harness contact. This correction preserves that boundary and authorizes
no implementation.

## Specification-Derived Verification

| Specification / invariant | Evidence | Result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-NO-ACTION-STATUS-SEMANTICS-001` | Exact thread read plus dedicated `no_action_correction` claim | PASS: latest version is LO-authored GO; Prime correction routes back to LO without implementation authority. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Current `scripts/ollama_harness.py` request path and protocol contract | FAIL for version 002: the declared D implementation sends native `/api/chat`, whose request contract has no forced-function-selection field. |
| `GOV-RELIABILITY-FAST-LANE-001` | Candidate diff and targeted tests | PARTIAL: F is mechanically valid; D mocked payload shape does not establish provider enforcement. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Version 001 test plan and acceptance criteria | FAIL for D: the planned unit test can pass while the provider ignores the unsupported field, and no genuine D smoke can prove the proposed mechanism. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve the four original targets and this numbered bridge target | PASS: all paths remain inside `E:/GT-KB`; no adopter or external project path is involved. |

## Pre-Filing Preflight Subsection

Both mandatory preflights were run against the completed candidate:

- Applicability: PASS with `preflight_passed: true`, no missing required or
  advisory specifications, no blocking errors, and an empty declared target
  set appropriate to this non-implementation correction.
- Clause applicability: PASS with five clauses evaluated, four `must_apply`,
  one `may_apply`, zero required evidence gaps, and zero blocking gaps.

The governed writer reruns the bridge compliance gate before creating the
numbered file.

## Authority Boundary

This `NO-ACTION` authorizes no source, test, configuration, runtime, database,
dispatcher, TAFE, harness, lease, credential, Git, external-system, release,
deployment, or destructive-cleanup operation. The surviving F diff is not
adopted by this bridge disposition.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
