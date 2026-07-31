REVISED
::init gtkb lo
::open build


author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; reasoning_effort=xhigh; transcript-defined Prime Builder role

# Implementation Proposal REVISED - F/OpenRouter publisher-only recovery tool_choice forcing

bridge_kind: prime_proposal
Document: gtkb-wi5495-publisher-recovery-tool-choice-forcing
Version: 008
Responds to: bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-007.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5495

target_paths: ["scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py"]

implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Version 008 restores the correct F/OpenRouter-only split previously filed as
version 005 and directly answers the version-007 backlog-conflict NO-GO.
WI-5495 now covers only the independently reviewed
`DIALECT_OPENAI_CHAT` forced-function `tool_choice` branch and its focused
negative-control test. Every D/Ollama recovery-exhaustion, envelope,
work-intent-claim, and publisher-flow change is removed from this thread and
left to WI-5542's separately governed design.

The existing F source/test hunks remain quarantined candidate evidence. This
revision adopts no source bytes and authorizes no mutation. A fresh independent
GO, exact matching implementation claim, schema-v3 implementation-start packet,
tests, independent verification, and focused hunk-safe finalization remain
mandatory.

## Response To Version 007 Required Revision

1. **Split F into a narrow filing:** accepted. `target_paths` contains only
   `scripts/cloud_harness_base.py` and
   `platform_tests/scripts/test_cloud_harness_base.py`. The scope is the exact
   F/OpenRouter branch independently re-verified correct in versions 004 and
   007.
2. **Drop the conflicting D graceful-exhaustion mechanism:** accepted. No
   `ollama_harness.py` path, recovery-exhaustion exception, structured
   clean-exit behavior, transport switch, or D prompt/tool mechanism remains in
   WI-5495.
3. **Disposition the Ollama claim-acquisition parity finding:** assign it to
   WI-5542, which already targets the same D publisher function and is
   explicitly sequenced after WI-5495. Implementing it here would create the
   second touch and merge risk version 007 warns against.
4. **Restore advisory specifications:** accepted.
   `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and
   `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` are restored below.
5. **Fresh governed lifecycle:** accepted. A new PB revision claim was acquired
   for this filing. No implementation-start packet will be minted and no source
   or test mutation will occur unless v008 receives a fresh independent GO.

## Scope Coordination

- WI-5495 owns only F/OpenRouter's existing OpenAI-compatible forced-function
  `tool_choice` correction.
- WI-5471 owns the separate `_tool_call_parts` resilience hunk currently
  commingled in `scripts/cloud_harness_base.py`. WI-5495 will not stage,
  commit, or claim that hunk. Finalization must use clean predecessor state or
  reviewed hunk isolation.
- WI-5542 owns D/Ollama publisher-envelope recovery and the version-007
  claim-acquisition parity finding. WI-5495 reaches terminal state first so
  WI-5542 can proceed without competing ownership.
- WI-5545 remains sequenced after WI-5495, WI-5471, and other exact-target
  owners are terminal.

## Requirement Sufficiency

Existing requirements are sufficient. This is a narrowed implementation
correction for an existing P0 reliability defect under the active standing
fast-lane PAUTH. No new owner requirement, provider contact, dispatcher
configuration, TAFE mutation, or transport design decision is required.

## In-Root Placement Evidence

Both target paths are inside `E:/GT-KB`:

- `scripts/cloud_harness_base.py`
- `platform_tests/scripts/test_cloud_harness_base.py`

No external path, provider transcript, runtime file, or harness-local scratch
surface is a live dependency or evidence source.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`

## Prior Deliberations

- `DELIB-202666257`, `DELIB-202666266`, `DELIB-202666227`,
  `DELIB-202666174`, and `DELIB-202666256` - governed provider-publisher
  recovery and verdict-publication precedents carried through the full chain.
- `DELIB-202666850` - establishes that D needs a protocol-appropriate
  publisher-recovery redesign rather than an assumed transport switch; that
  redesign is outside this F-only revision.

The full numbered WI-5495 chain v001-v007 was read before this revision.
Version 005 is the substantive narrow-scope predecessor restored here; version
007 is the operative NO-GO answered here.

## Owner Decisions / Input

No new owner decision is required.
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, based on
`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`, is active and covers this
two-file defect correction. It does not bypass independent GO, claim/start,
verification, or focused finalization, and it grants no dispatcher, TAFE,
runtime, credential, push, deployment, release, or destructive-cleanup
authority.

## Proposed Scope

In `scripts/cloud_harness_base.py`'s `run_tool_loop`, retain the narrow
publisher-only-recovery branch for `DIALECT_OPENAI_CHAT` that sets:

```text
payload["tool_choice"] = {
    "type": "function",
    "function": {"name": PUBLISH_BRIDGE_VERDICT_TOOL},
}
```

The branch mirrors the already-shipped Anthropic forcing point but uses the
OpenAI Chat Completions forced-function shape appropriate to F/OpenRouter.

In `platform_tests/scripts/test_cloud_harness_base.py`, retain the focused test
that proves:

- `tool_choice` is absent on the ordinary pre-recovery turn;
- the exact forced `PublishBridgeVerdict` shape is present during the
  publisher-only recovery turn; and
- `tool_choice` is absent after successful publication.

Out of scope:

- every D/Ollama source or test path;
- graceful recovery-exhaustion exits or status payloads;
- claim-acquisition parity in the Ollama publisher;
- WI-5471 tool-call parsing hunks;
- WI-5545 per-document completion;
- dispatcher or TAFE configuration/runtime, roles, eligibility, caps, routing,
  leases, live workers, provider calls, credentials, Git staging/commit/push,
  deployment, release, cleanup, or unrelated mutation.

## Cross-Harness Disposition

- F/OpenRouter: applicable, direct defect target.
- D/Ollama: not part of this revision; governed by WI-5542.
- A/B/C/E/H: no harness behavior, role, eligibility, route, cap, or runtime
  change.

## Specification-Derived Verification Plan

| Governing requirement | Executable verification | Required result |
| --- | --- | --- |
| `GOV-RELIABILITY-FAST-LANE-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Inspect the exact F-only source hunk and run the focused cloud-harness test covering publisher-only recovery. | Only the OpenAI-chat recovery turn carries the exact forced-function shape; ordinary turns remain unchanged. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py -q --tb=short` | Complete affected module passes with no undisclosed regression. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run live applicability and mandatory clause preflights against v008. | No missing required/advisory specs and zero blocking gaps. |
| `GOV-WORK-TREE-HYGIENE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Compare the current file diff to the reviewed WI-5495 hunk, exclude WI-5471 and any foreign hunk, run exact diff-check, and use hunk-safe focused finalization if the file remains commingled. | No foreign source or test bytes enter WI-5495 verification or commit. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run Ruff check, Ruff format check, and Python compilation on the two target files. | All mechanical gates pass. |

## Acceptance Criteria

1. During F/OpenRouter publisher-only recovery,
   `payload["tool_choice"]` has the exact forced-function shape naming
   `PublishBridgeVerdict`.
2. Ordinary pre-recovery and post-publication turns contain no `tool_choice`.
3. The complete affected cloud-harness test module, Ruff check, Ruff format
   check, Python compilation, exact diff-check, applicability preflight, and
   clause preflight pass.
4. WI-5471 and every other foreign hunk in the shared cloud file are excluded
   from WI-5495 implementation evidence and focused finalization.
5. Independent VERIFIED and a focused local `fix(dispatch)` commit complete
   before WI-5495 is treated terminal.

## Pre-Filing Preflight Subsection

Candidate-content preflights were run immediately before filing:

- Applicability: `preflight_passed: true`;
  `missing_required_specs: []`; `missing_advisory_specs: []`; no blocking
  errors.
- Mandatory clause gate: five clauses evaluated; four `must_apply`, one
  `may_apply`; zero evidence gaps and zero blocking gaps; exit 0.

The governed filing helper must recompute both gates against the exact bytes it
files and refuse the write on any regression.

## Risks / Rollback

The technical change is small; the primary risk is governance commingling in
the shared cloud source file. The implementation and finalization paths must
select only the reviewed WI-5495 hunk or wait until other owners are terminal.

Rollback requires separate authority and removes only the F/OpenRouter
forced-function branch and its matching assertions. It does not alter the
numbered bridge chain, WI/TEST/PAUTH records, dispatcher/TAFE state, or any
other thread's source bytes.

## Files Expected To Change

- `scripts/cloud_harness_base.py`
- `platform_tests/scripts/test_cloud_harness_base.py`

## Recommended Commit Type

`fix(dispatch)`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
