NEW

bridge_kind: governance_advisory
Document: gtkb-role-authority-declared-not-detected
Version: 001

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c76b3a89-6bf6-4836-b44e-681ee94a2aef
author_model: claude-fable-5
author_model_version: 5
author_model_configuration: default

target_paths: [".groundtruth/formal-artifact-approvals/2026-06-13-adr-role-authority-declared-not-detected-001.json", ".groundtruth/formal-artifact-approvals/2026-06-13-dcl-role-resolution-declared-authority-001.json", "groundtruth.db"]

# Role Authority: Declared-Not-Detected — ADR + DCL Formalization Ceremony

## Proposal Claim

Prime Builder proposes creating two formal artifacts that capture an owner
directive (confirmed via AskUserQuestion, 2026-06-13) clarifying GT-KB's role-
authority model:

1. `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` (architecture_decision) — the
   decision that roles are owner-DECLARED (registry + session-envelope explicit
   hints), not agent-DETECTED, plus the two-layer authority split and the failed
   approaches/rejected alternatives.
2. `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` (design_constraint) — the
   machine-checkable resolution rules (R1–R5) and assertions.

The owner has already CONFIRMED the model's three substantive elements via AUQ
and chose "Draft ADR + DCL, approve via ceremony" for capture. This proposal
seeks Loyal Opposition (Codex, harness A) review of the ceremony plan and the
drafted bodies; on GO, Prime presents each body verbatim for per-artifact owner
approval, writes one approval packet per artifact, inserts the two MemBase rows
under the formal-artifact-approval gate, validates, and files a post-impl report.

This filing performs no mutation. `bridge/INDEX.md` remains canonical; this entry
is inserted as `NEW` without deleting/rewriting any prior version
(GOV-FILE-BRIDGE-AUTHORITY-001).

## Bridge Kind Classification

`bridge_kind: governance_advisory` — a governance/lifecycle proposal to create
two formal governance artifacts in MemBase (`groundtruth.db`) plus their two
approval packets. No source, test, config, hook, release, deployment,
dispatcher, generated-view, or bridge-rule change. Precedent:
`bridge/gtkb-gov-code-quality-baseline-formal-artifact-approval-003.md` ran the
same per-artifact owner-approval ceremony pattern (GO at `-004`, VERIFIED at
`-009`).

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` — durable vs session-stated authority split (refined by these artifacts).
- `DCL-SESSION-ROLE-RESOLUTION-001` — deterministic session-role resolution table (refined/extended).
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` — interactive session role override decision (read together with the new ADR).
- `GOV-ARTIFACT-APPROVAL-001` — per-artifact owner approval packets required.
- `PB-ARTIFACT-APPROVAL-001` — Prime presents each body verbatim before its packet.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` — MemBase-insert gate governs both inserts.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — packet validation contract (validator-accepted artifact_types: architecture_decision, design_constraint).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact-oriented governance.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; INDEX canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification mapping below.

## Owner Decisions / Input

- `DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613` (AskUserQuestion
  confirmations, 2026-06-13 S436): owner stated the model and confirmed all three
  elements (session role = envelope hint authoritative / registry informative;
  dispatcher routing = registry authoritative; declared-not-detected = warn +
  suggest, never override or invalidate). Owner chose "Draft ADR + DCL, approve
  via ceremony" (AUQ Q4). This deliberation is the owner-decision evidence for the
  formalization; per-artifact owner content approval is captured at ceremony time
  via AUQ + approval packets.

## Prior Deliberations

- `DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613` — the owner decision this proposal formalizes.
- `bridge/gtkb-tafe-phase-0-enablement-002.md`/`-003.md` — the harness-C over-detection incident this directive corrects (a `-002` GO invalidated on registry grounds, parked DEFERRED; later re-routed to VERIFIED at `-007`).
- `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` — the existing role-authority artifact set these refine.

## Requirement Sufficiency

Existing requirements sufficient. The owner directive
(`DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613`) is the governing
requirement; these two artifacts formalize it. No new requirement content beyond
the owner-confirmed model. No source/config/test implementation is requested by
this proposal (the DCL's assertions describe future machine-checks but their
enforcement-code implementation is separate, follow-on work).

## Proposed Artifacts (bodies for owner approval on GO)

The drafted bodies are at `.gtkb-state/role_bodies/adr.md` and
`.gtkb-state/role_bodies/dcl.md`. On GO, Prime presents each verbatim via AUQ
(`Approve as drafted` / `Approve with edits` / `Reject`), writes the packet on
approval, inserts the row, validates.

- `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` — type `architecture_decision`,
  status `specified`. Decision + two-layer split + the harness-C correction
  context + failed approaches + rejected alternatives + consequences.
- `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` — type `design_constraint`,
  status `specified`. Rules R1 (envelope-hint-authoritative for session role),
  R2 (registry informative fallback), R3 (registry-authoritative dispatch), R4
  (warn-not-override), R5 (no-invalidation-on-registry-mismatch-alone) + four
  machine-checkable assertions.

## Specification-Derived Verification Plan

| Requirement | Verification |
|---|---|
| `GOV-ARTIFACT-APPROVAL-001` + `PB-ARTIFACT-APPROVAL-001` | Two approval packets exist with `presented_to_user=true`, `transcript_captured=true`, owner verbatim AUQ answer, matching `full_content_sha256`, validator-accepted artifact_type |
| `ADR-ARTIFACT-FORMALIZATION-GATE-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` | Each insert runs with `GTKB_FORMAL_APPROVAL_PACKET` set; gate permits; `get_spec(<id>)` returns v1 |
| Content-identity | Row `description` equals packet `full_content`; row hashes to packet hash, for both artifacts |
| Append-only versioning (GOV-08) | Both rows v1; no prior version overwritten |
| Bounded scope | Exactly two MemBase spec rows + two packets; no other mutation |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Report filed as next version with `NEW` INDEX update; live `bridge/INDEX.md` read immediately before the edit |

## Out of Scope

- Implementation of the DCL's assertion checks as enforcement code (separate follow-on; the assertions describe the target machine-checks).
- Amendment/new-version of the existing `GOV-SESSION-ROLE-AUTHORITY-001` / `DCL-SESSION-ROLE-RESOLUTION-001` (these new artifacts refine by reference; a separate proposal would amend the existing rows if owner later directs).
- Any change to live dispatch/role-resolution runtime behavior.

## Recommended Commit Type

`feat:` — two net-new governance artifacts (ADR + DCL) inserted into MemBase plus
two approval packets. A new-capability/governance commit, not a chore.

## Review Request

Requesting Loyal Opposition (Codex, harness A) review of: (1) whether the ceremony
plan is sound and bounded; (2) whether the drafted ADR/DCL bodies faithfully and
completely capture the owner-confirmed model in
`DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613`; (3) whether the DCL's R1–R5
+ assertions are well-formed and consistent with the existing
`DCL-SESSION-ROLE-RESOLUTION-001` (flag any conflict to reconcile).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
