ADVISORY
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role; build activity
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: governance_advisory
Document: gtkb-lo-wi5368-legacy-chain-verdict-publication-blocker-advisory
Version: 001
Date: 2026-07-29 UTC
Author: Loyal Opposition (Codex A)

# Advisory Proposal — WI-5368 invalid legacy chain blocks a required review verdict

## Source

Direct Loyal Opposition review of `gtkb-wi5368-codex-git-window-command-family` v005, including a governed writer attempt for the required v006 NO-GO and a duplicate/ownership check of the live WI-5298 containment-repair thread.

## Claim

The current WI-5368 v005 proposal must be rejected for its live WI-5298 target collision, but the governed bridge writer cannot publish the required NO-GO because immutable WI-5368 v002 is an operative GO with missing author provenance. The strict lifecycle resolver therefore blocks every ordinary append to the thread, leaving the invalid REVISED item LO-actionable without a governed same-thread verdict route.

## Evidence

- Live `gt bridge show gtkb-wi5368-codex-git-window-command-family --json --compact` resolves the historical v002 GO in the ordinary chain.
- The governed writer rejects a v006 NO-GO with `OPERATIVE_VERSION_MISSING_PROVENANCE` for `bridge/gtkb-wi5368-codex-git-window-command-family-002.md` before it can publish the verdict.
- Independent review found a separate live `GO` thread, `gtkb-wi5298-codex-git-window-family-containment-repair` v002, declaring the exact same source/test targets under a different matcher scope. The desired NO-GO evidence is retained in this advisory because the immutable chain cannot receive it.
- Duplicate search found related legacy-resolution work in `gtkb-wi5670-legacy-init-role-evidence-v2`, which deliberately preserves fail-closed behavior for an operative legacy proposal/GO; it does not provide a disposition channel for a blocked review verdict on an already-invalid thread.

## Risk

The recurring LO drain will rediscover WI-5368 v005 indefinitely, while Prime Builder receives no durable same-thread review verdict explaining the live target collision. A reviewer may also be tempted to bypass the governed writer or overwrite historical files, violating append-only provenance and fail-closed behavior.

## Recommended Prime Action

Prime Builder should create a fresh, new clean-chain implementation proposal that:

1. cites this advisory and preserves the unmodifiable WI-5368 v001–v005 chain as historical evidence;
2. resolves or explicitly incorporates the active WI-5298 containment-repair GO before requesting new ownership of either shared target; and
3. uses a fully provenance-complete proposal/GO lifecycle, preserving all current no-window, hide-only, and terminal-authorization gates.

Alternatively, a separately approved bridge-protocol design change may add a governed quarantine/correction route for invalid legacy operative chains. It must not weaken `OPERATIVE_VERSION_MISSING_PROVENANCE` for implementation authorization or allow review self-approval.

## Prior Deliberations

- `DELIB-202666274` — project work remains subject to independent review and implementation-start gates.
- `DELIB-202667132` — live WI-5298 containment-repair GO evidence.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` — retain the nonimpairing console-containment objective.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decision Needed

None to record this advisory. The owner’s standing LO drain instruction directs Loyal Opposition to file an Advisory Proposal for an out-of-scope GT-KB defect or poor design choice. Any repair still requires normal Prime Builder disposition, owner decision where applicable, a new proposal, LO GO, and an implementation-start packet.

## Classification Slot

Classification: **adapt**.

The clean-chain recovery route is immediately available without weakening the lifecycle resolver. A broader protocol change, if desired, needs a separate owner-grilled decision because it would alter how malformed historical operative artifacts are quarantined while preserving fail-closed implementation authorization.

## Non-Approval Statement

This ADVISORY is evidence and a future-work recommendation only. It neither authorizes source/test changes nor replaces project authorization, bridge review, implementation-start, terminal-finalization, or owner-decision gates.
