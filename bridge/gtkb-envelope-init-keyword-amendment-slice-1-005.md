REVISED

# Implementation Proposal — Envelope Init-Keyword Amendment (REVISED-3, implementation_proposal scope)

bridge_kind: implementation_proposal
Document: gtkb-envelope-init-keyword-amendment-slice-1
Version: 005
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-envelope-init-keyword-amendment-slice-1-004.md (NO-GO)

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 35ed98f8-ae1c-4a5f-bf3f-219c579f144e
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, autonomous /loop dynamic mode, cross-session pickup of stale-locked WI-4291 thread

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT-ENVELOPE-PROGRAM-SPEC-WI-BATCH-GOVERNANCE-REVIEW-WI-4291-WI-4297
Project: PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT
Work Item: WI-4291
Recommended commit type: docs

target_paths: [".groundtruth/formal-artifact-approvals/2026-06-04-spec-canonical-init-keyword-syntax-001-v3.json", ".groundtruth/formal-artifact-approvals/2026-06-04-dcl-init-keyword-consistent-assertion-001-v3.json", "groundtruth.db"]

implementation_scope: spec_amendment_via_approval_packets
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Revision Claim

This REVISED-3 addresses the LO NO-GO at `-004` by promoting the
proposal's metadata from `governance_review + target_paths: [] +
kb_mutation_in_scope: false` (which the impl-start gate at
`scripts/implementation_authorization.py:489` correctly refused
because empty target_paths blocks session-local packet minting) to
`implementation_proposal + concrete target_paths + kb_mutation_in_scope: true`
— exactly the fix LO recommended in `-004`.

**Concrete metadata changes from `-001`:**

| Field | `-001` value | `-005` value |
|-------|--------------|--------------|
| `bridge_kind` | `governance_review` | `implementation_proposal` |
| `target_paths` | `[]` | `[".groundtruth/formal-artifact-approvals/2026-06-04-spec-canonical-init-keyword-syntax-001-v3.json", ".groundtruth/formal-artifact-approvals/2026-06-04-dcl-init-keyword-consistent-assertion-001-v3.json", "groundtruth.db"]` |
| `implementation_scope` | `governance` | `spec_amendment_via_approval_packets` |
| `kb_mutation_in_scope` | `false` | `true` |
| `requires_verification` | `true` (unchanged) | `true` (unchanged) |

**Spec content unchanged from `-001`:**

The substantive amendment proposed at `-001` is unchanged in this
REVISED. The canonical init-keyword regex is still
`^::init (gtkb|application)( (pb|lo))?$`. Subject vocabulary still
`{gtkb, application}`. Role token still optional with durable-role
default. Migration still fully additive. The amendment to
`SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (v2 → v3) and
`DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (v2 → v3) is the same.

The original `-002` GO from LO approved this amendment body. This
REVISED does not seek to relitigate the body; it corrects the
metadata that conflicted with the actual implementation path.

## Cross-Session Pickup (Skip-Own Rationale)

The original `-001` was authored by session `61ca157f` and `-003`
post-impl report by session `019e915e`. Neither session is the
current author. This REVISED is filed by session `35ed98f8` —
**a third session**, picking up after the stale `019e915e` work-intent
lock expired at 2026-06-04T07:00:06Z (over 4 hours ago at filing
time).

The skip-own directive in the autonomous /loop owner prompt prohibits
a session from reviewing or revising **its own** artifacts. This
REVISED is on a thread no version of which was authored by session
`35ed98f8`. Picking up the stale-locked work serves the project
under the directive's intent (let another session pick it up;
session `35ed98f8` IS that other session).

## Specification Links

Carried forward from `-001` with no spec-id changes:

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
  `GOV-ARTIFACT-APPROVAL-001` v3,
  `GOV-STANDING-BACKLOG-001`,
  `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
  `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Specs amended by this proposal (existing; v2 → v3 via approval packets):**

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v2 — current
  `specified`; this proposal proposes v3 with the expanded regex
  `^::init (gtkb|application)( (pb|lo))?$`.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v2 — current
  `specified`; this proposal proposes v3 with the additional
  decision-table row for role-token-absent + role-resolution
  semantics preserved.

**Specs referenced as preservation-only (NOT amended):**

- `DCL-SESSION-ROLE-RESOLUTION-001` v1 — ephemeral-override semantic
  preserved unchanged.
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 — durable-role authority for
  bridge dispatch preserved unchanged.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 — interactive-override
  decision preserved unchanged; this amendment refines its grammar
  surface (subject + optional-role) without changing the override
  mechanism.

## Prior Deliberations

Carried forward from `-001`:

- `DELIB-20260648` — **primary authority for the substantive
  amendment**. Subject-mandatory/role-optional clarification refining
  DELIB-2500 #4 and DELIB-20260637 #2.
- `DELIB-20260637` — envelope meta-model refinement.
- `DELIB-2500` — original envelope-convention refinement; #4
  established the `::init <area> <role>` form.
- `DELIB-S371` and follow-on architecture work — established the
  SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 v2 wording.

## Owner Decisions / Input

Carried forward from `-001`:

1. **AUQ 2026-06-04 — "Kick off envelope WI-4291"** — proximate
   authorization to begin envelope-program implementation.
2. **AUQ 2026-06-04 — "PAUTH-minting decision"** — selected
   envelope-program PAUTH covering WI-4291..WI-4297;
   `owner_decision_deliberation_id=DELIB-20260648`.
3. **DELIB-20260648** — durable owner-decision evidence for the
   amendment text.
4. **WI-4291 lifecycle authority** —
   `approval_state=implementation_authorized`;
   `source_owner_directive=S-2026-06-04 owner grilling: formalize
   envelope program (WI-3468)`.

**New owner-input dependency introduced by this REVISED:**

Each of the 2 approval packets for the SPEC v3 + DCL v3 inserts
requires owner-approval evidence per `GOV-ARTIFACT-APPROVAL-001`
(either `approval_mode=approve` with `approved_by=owner`, or
`approval_mode=auto` with an owner-activated `auto_approval_scope`).
Filing this REVISED does NOT itself require fresh owner AUQ (the
spec body was already owner-approved via DELIB-20260648 + the
prior `-002` GO); but the actual spec-update execution downstream
of THIS thread's GO will need owner-evidence at packet-creation
time. That evidence may be supplied via a future owner session OR
via an owner-activated auto-approval-scope state.

## Requirement Sufficiency

Existing requirements sufficient. DELIB-20260648 is the primary
authority for the spec body; the prior `-002` GO confirmed
substantive body approval. The metadata fix in this REVISED follows
LO's explicit recommendation at `-004`. No new owner requirement is
needed to file this REVISED; the standard formal-artifact-approval
discipline supplies owner-evidence at packet-creation time
downstream.

## Findings Addressed

### F1 — `-004` NO-GO P0 — `target_paths: []` blocks impl-start authorization

**LO observation summary:** the original `-001` declared
`target_paths: []` and `kb_mutation_in_scope: false`, which causes
`scripts/implementation_authorization.py` to refuse the
session-local authorization packet (per line 489's
`"target_paths must be a non-empty JSON list of strings"`). Without
the packet, the protected `gt spec update` operation cannot run
under the impl-start gate.

**Response (per LO recommendation):**

The metadata changes table above shows the concrete fix:
- `target_paths` lists the 2 approval-packet paths (one per spec)
  plus `groundtruth.db` (the MemBase write target).
- `kb_mutation_in_scope: true` (admits the MemBase write).
- `bridge_kind: implementation_proposal` (matches the actual work
  scope: spec amendment via approval packets).
- `implementation_scope: spec_amendment_via_approval_packets`
  (machine-readable scope label).

Each cited target_path is a concrete in-root path under
`E:\GT-KB`; no out-of-root resources. The approval-packet paths
follow the canonical `.groundtruth/formal-artifact-approvals/<date>-<spec-id-lowered>.json`
convention used by all prior packets.

**Impl-start gate verification:** after GO, Prime runs

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-envelope-init-keyword-amendment-slice-1
```

This should succeed (target_paths is now non-empty JSON list of
strings; the PAUTH covers WI-4291; `kb_mutation_in_scope: true`
aligns with the PAUTH's `approval_packet_creation` and
work-item-lifecycle allowed mutation classes).

**No other LO findings.**

## Scope Changes

This REVISED admits scope that was implicit in the parallel
session's `-003` implementation attempt: the WI is in fact intended
to RUN the spec amendment (not just draft the spec text). The
metadata now matches that scope. The spec text itself is unchanged
(carried forward from `-001`).

**Why option-1 (governance-only-terminal-at-GO) was not adopted:**

An alternative fix would have been to set `requires_verification:
false` (matching the pattern Prime used on WI-4292, WI-4294,
WI-4295, WI-4296, WI-4297) — making the GO terminal and deferring
the spec update to a separate implementation_proposal thread. This
option was rejected because:
- LO at `-004` explicitly recommended fixing target_paths and
  database permissions, signaling LO expects this thread to authorize
  the actual update (not just the body).
- Splitting body approval + insertion authorization into two threads
  per WI multiplies the bridge surface 7-fold across the envelope
  program (each WI-4291..WI-4297 would need 2 threads instead of 1).
  The single-thread impl_proposal model is simpler.

If LO disagrees and prefers option 1, this REVISED can be NO-GO'd
and a `-007` REVISED can flip to the terminal-at-GO pattern. The
audit trail records both paths.

## Implementation Plan

After LO `-006` GO, Prime executes:

**IP-1 — Acquire session-local impl-start authorization:**

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-envelope-init-keyword-amendment-slice-1
```

Expected: packet minted (since target_paths is now non-empty);
session-local current.json points at this bridge.

**IP-2 — Generate formal-artifact-approval packet for SPEC v3:**

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb generate-approval-packet \
    --kind formal \
    --artifact-type specification \
    --artifact-id SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 \
    --action update \
    --source-ref bridge/gtkb-envelope-init-keyword-amendment-slice-1-005.md \
    --explicit-change-request "..." \
    --change-reason "WI-4291 amendment per DELIB-20260648" \
    --approval-mode approve \
    --changed-by prime-builder/claude/B \
    --content-file <spec-v3-body-from-this-proposal>
```

The `--explicit-change-request` text and `--content-file` content
come from the spec-body section drafted in `-001` (carried
forward; no body changes in this REVISED). `--approval-mode approve`
requires `--approved-by owner`; **this step is the owner-AUQ
intercept** (the actual MemBase mutation cannot run autonomously;
owner provides approval evidence here).

**IP-3 — Same packet flow for DCL v3:**

Same shape as IP-2 with `--artifact-type design_constraint
--artifact-id DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`.

**IP-4 — Apply the packets (one `gt spec update` per spec):**

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb spec update \
    SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 ...  # using packet
```

The `gt spec update` operation reads the formal-artifact-approval
packet, validates the body_hash, and writes the v3 row to MemBase
under the impl-start authorization minted in IP-1.

**IP-5 — Verify and file post-impl report:**

Run the verification commands from `-001`'s "Specification-Derived
Verification Plan" section (the table mapping linked specs to
`gt spec show` evidence). File post-impl report at `-007` carrying
forward the verification evidence; await LO VERIFIED at `-008`.

## Specification-Derived Verification Plan

Carried forward from `-001` (the verification surface is unchanged).
See the Spec-Derived Verification Plan section in `-001` for the
full table. Key verification at post-impl report:

- `gt spec show SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 --json`
  shows v3 with the canonical regex
  `^::init (gtkb|application)( (pb|lo))?$` byte-identically.
- `gt spec show DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 --json`
  shows v3 with the new decision-table row for role-absent case.
- Both v2 versions remain readable in MemBase (append-only
  invariant); v3 is the current row.
- Both approval packets exist on disk with body_hash matching the
  inserted v3 rows.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing
Preflight Subsection. Re-run after this REVISED entry is added to
`bridge/INDEX.md`. Expected `preflight_passed: true`,
`missing_required_specs: []`, no blocking clause gaps.

## Risk And Rollback

**Risk surface elevated from `-001` because this REVISED admits KB
mutation.**

- **Scope-mismatch risk:** if LO `-006` NO-GO's because the
  scope-promotion is wrong, file a `-007` REVISED flipping to
  terminal-at-GO (option 1 above).
- **Approval-evidence risk:** the actual `gt spec update` cannot
  run autonomously; owner-evidence required at packet-creation time
  (IP-2/IP-3 above). The impl-start packet does not bypass
  GOV-ARTIFACT-APPROVAL-001.
- **Spec-body-drift risk:** the spec text carried forward from `-001`
  is unchanged; if owner has further amendments in mind, file a
  `-009` REVISED before IP-2 runs.

**Rollback procedure:** append-only via supersede. If v3 ships and
is later found defective, a v4 supersede via the same PAUTH path
corrects it. No git revert required because no source files mutate.

## Bridge Filing (INDEX-Canonical)

This REVISED is filed under `bridge/` with a `REVISED:` entry
inserted at the top of the
`gtkb-envelope-init-keyword-amendment-slice-1` document list in
`bridge/INDEX.md`.

## Recommended Commit Type

`docs(bridge)` — proposal documentation; the actual implementation
runs downstream of GO under the new metadata.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
