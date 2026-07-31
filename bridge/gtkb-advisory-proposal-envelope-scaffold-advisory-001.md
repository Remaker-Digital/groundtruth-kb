ADVISORY
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex desktop interactive session; owner-directed ADVISORY bridge filing for advisory proposal envelope scaffold requirement

bridge_kind: governance_advisory
Document: gtkb-advisory-proposal-envelope-scaffold-advisory
Version: 001
Author: Owner-directed advisory prepared by Prime Builder (Codex, harness A)
Date: 2026-07-15 UTC
Mode: advisory proposal
Severity: high
Priority: high

# Advisory Proposal Envelope Scaffold Advisory

## Source

This ADVISORY bridge artifact preserves the owner-directed correction from Codex Prime Builder session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a` on 2026-07-15: because the advisory-proposal scaffold/envelope requirement is intended to drive future work, it must itself be carried as an Advisory Proposal available through the bridge.

The underlying governed records already exist and are linked:

- `SPEC-INTAKE-8161dc` v3: Core Role And Envelope Scaffolds Must Teach Advisory Bridge Authority And Initiation Semantics.
- `WI-AUTO-SPEC-INTAKE-8161DC` v4: Implement SPEC-INTAKE-8161dc: Advisory Bridge Authority And Initiation Semantics.
- `TEST-11408` v3: Verify prompts teach advisory bridge authority, access, and initiation semantics.
- `DELIB-20260715-DISCARDED-MATERIAL-NONREFERENCE`: discarded non-governed material is not evidence and must never be inspected, cited, relied on, or carried forward.
- `DELIB-20260715-ADVISORY-PAIR-NONDISPATCHABLE-BRIDGE-FILING`: the two 2026-07-15 research advisories were filed as non-dispatchable bridge artifacts.
- `DELIB-20260715-ADVISORY-PROPOSAL-KNOWLEDGE-IN-DELIBERATION-BUILD-ENVELOPES`: deliberation and build envelopes must include advisory-proposal knowledge and access direction.
- `DELIB-20260715-ADVISORY-PROPOSAL-PRIMARY-LO-INITIATION-MECHANISM`: Advisory Proposal is the primary Loyal Opposition mechanism for initiating future work.

Related bridge evidence:

- `bridge/gtkb-dispatcher-complex-black-box-advisory-001.md`
- `bridge/gtkb-per-harness-budget-awareness-advisory-001.md`
- `bridge/gtkb-advisory-prime-actionability-surfacing-004.md` verified that ADVISORY entries surface for Prime Builder manual action while remaining non-dispatchable for headless dispatch.

Live bridge/dispatcher observation on 2026-07-15 from `gt bridge dispatch report --compact`: bridge dispatch workflow `PASS`; ADVISORY entries including `gtkb-dispatcher-complex-black-box-advisory` and `gtkb-per-harness-budget-awareness-advisory` appear as Prime Builder `Candidate next` with reason `advisory_requires_owner_intake`. `gt bridge dispatch status --json` and `gt bridge dispatch health --json` reported `health_status: PASS` for the live GT-KB root.

## Claim

The advisory-proposal scaffold/envelope requirement is intended to drive future work and therefore should be available as a bridge ADVISORY artifact, not only as MemBase rows. Future Prime Builder sessions should be able to retrieve this advisory from the bridge and progress it through advisory disposition into project/work-item/proposal handling.

Need: generated role prompts, deliberation envelopes, and build envelopes must teach workers what Advisory Proposals are, how to access them through the bridge, and how to progress them without treating them as direct implementation approval. This closes the exact failure observed in this session: a worker can otherwise interpret `ADVISORY` as merely inert or non-dispatchable rather than the primary Loyal Opposition future-work initiation path.

## Owner Decision Needed

No additional owner decision is needed to file this ADVISORY. The owner explicitly directed that, if this requirement is intended to drive future work, it should be an Advisory Proposal as well.

Future implementation still needs normal disposition: retrieve this advisory through the bridge, classify it through advisory intake/disposition, attach or update the existing work item/spec as needed, then file a normal implementation proposal for protected prompt/source/config edits and obtain Loyal Opposition GO.

## Recommended Prime Action

1. Route this ADVISORY through the governed advisory-disposition path.
2. Adopt rather than duplicate the existing governed records: `SPEC-INTAKE-8161dc`, `WI-AUTO-SPEC-INTAKE-8161DC`, and `TEST-11408`.
3. Update or create the implementation proposal so protected edits cover the generated role prompt scaffold and the programmatically generated deliberation/build envelope prompt package.
4. Ensure implementation changes teach all of the following:
   - Advisory Proposals are governed bridge-protocol artifacts.
   - Advisory Proposals are available to workers through the bridge.
   - Advisory Proposal is the primary Loyal Opposition mechanism for initiating future implementation work by recommending projects, work items, or lifecycle changes such as disposal or withdrawal.
   - ADVISORY entries are non-dispatchable as direct work packets and are not GO verdicts or implementation approval.
   - Interactive workers may retrieve and progress Advisory Proposals through the advisory intake/disposition path.
   - Discarded non-governed material is not evidence and must never be inspected, cited, relied on, or carried forward.
5. Add focused assertion coverage so `TEST-11408` can pass against the generated role, deliberation, and build envelope surfaces.

## Classification Slot

Owner-directed governance advisory for Prime Builder disposition. Classification recommendation: `adopt` as the future-work initiation carrier for `SPEC-INTAKE-8161dc` / `WI-AUTO-SPEC-INTAKE-8161DC`, with implementation deferred until normal project authorization, bridge proposal, Loyal Opposition GO, implementation-start, and verification gates are satisfied.

## Prior Deliberations

- `DELIB-20260715-DISCARDED-MATERIAL-NONREFERENCE`
- `DELIB-20260715-ADVISORY-PAIR-NONDISPATCHABLE-BRIDGE-FILING`
- `DELIB-20260715-ADVISORY-PROPOSAL-KNOWLEDGE-IN-DELIBERATION-BUILD-ENVELOPES`
- `DELIB-20260715-ADVISORY-PROPOSAL-PRIMARY-LO-INITIATION-MECHANISM`
- `INTAKE-656dcc15`

## Related Specifications And Work Items

- `SPEC-INTAKE-8161dc`
- `WI-AUTO-SPEC-INTAKE-8161DC`
- `TEST-11408`

## Implementation Surfaces To Evaluate

The current spec source paths identify likely implementation surfaces, subject to fresh proposal-time discovery:

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
- `groundtruth-kb/src/groundtruth_kb/activity/profiles.py`
- `config/agent-control/activity-disposition-profiles.toml`
- `config/agent-control/SESSION-STARTUP-INDEX.md`
- `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`
- `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`

These paths include protected source/config/rule surfaces. This ADVISORY does not authorize direct edits to them.

## Duplicate And Supersession Check

A duplicate scan found related advisory-infrastructure threads, especially `gtkb-advisory-prime-actionability-surfacing` and `gtkb-advisory-proposal-intake-workflow`, but no existing bridge ADVISORY dedicated to `SPEC-INTAKE-8161dc` or the 2026-07-15 owner correction that advisory-proposal knowledge must be in generated role/deliberation/build envelopes. This artifact should therefore be filed as a new ADVISORY rather than folded into the two research advisories.

## Non-Approval Statement

This ADVISORY is a non-dispatchable bridge artifact and future-work initiation carrier. It is not a work packet, GO verdict, implementation report, project authorization, implementation-start packet, or permission to mutate protected prompt/source/config/bridge/TAFE/dispatcher/harness-state surfaces. Any downstream implementation must proceed through normal GT-KB advisory disposition, project/work-item authorization as applicable, bridge proposal, Loyal Opposition GO, work-intent, implementation-start, and verification gates.
