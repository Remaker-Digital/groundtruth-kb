NEW
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-05T17-03-48Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;build activity
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: prime_proposal
Document: gtkb-wi5942-bridge-helper-publication-capability
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5942
Related Work Items: ["WI-5314", "WI-5368"]

target_paths: [".goose/skills/gtkb-bridge-propose/helpers/write_bridge.py"]

implementation_scope: source + focused test (bridge publication capability integration)
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: fix

# Implementation Proposal - Systemic fix: bridge-filing helper must mint/consume publication capabilities

## Problem Statement

WI-5942 (P0, defect) is a systemic stranding defect. The bridge-filing helper
`propose_bridge_codex_non_bypass` in
`.goose/skills/gtkb-bridge-propose/helpers/write_bridge.py` writes a status-bearing
numbered bridge file but does **not** mint and consume a bridge publication
capability, unlike the governed writer `scripts/gtkb_bridge_writer.py`
`write_bridge_file`. As a result, every helper-written REVISED/NEW
implementation report is missing the exact publication-capability evidence that
`check_protected_commit_authorization._bridge_publication_capability_clearance`
requires, so atomic VERIFIED finalization fails closed (WI-5825-class stranding).

Confirmed affected files (missing capability rows):
- WI-5314 `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-015.md` (no capability).
- WI-5368 `bridge/gtkb-wi5368-codex-git-window-command-family-023.md`, `-027.md` (no capability), `-028.md` (`recovery_required`).

Root cause: the helper writes through `target.open("x", ...)` without the
`mint_bridge_publication_capability` -> write -> `consume_bridge_publication_capability`
transaction that `write_bridge_file` performs (gtkb_bridge_writer.py ~1212-1334).

## Proposed Fix

Modify `propose_bridge_codex_non_bypass` in the helper to mirror the governed
writer's typed-publication transaction when the registry publication is enabled:

1. Before writing the bridge file, call
   `groundtruth_kb.project.registry_control_plane.mint_bridge_publication_capability`
   with the exact `document_name`, `version`, `status`, `target_path`, `content`
   bytes, author `session_id`, and a compliance digest (mirroring
   `_publication_compliance_digest`), recording a pending-publication token.
2. After a verified byte-exact write, call
   `consume_bridge_publication_capability` to mark the capability `consumed` with
   revision linkage.
3. On any write failure (exclusive-create race, OSError, post-write byte
   mismatch), compensate the pending publication (mirroring
   `_compensate_publication`) and fail closed.
4. Add focused tests asserting that a helper-written bridge file gains a
   `consumed` publication capability with matching content digest, and that a
   failed write compensates without stranding.

This change prevents future WI-5825-class stranding for all helper-written
bridge filings. It does NOT retroactively recover already-stranded files
(WI-5314 -015, WI-5368 -023/-027/-028); those require the separately directed
owner-authorized exceptional recovery.

## Scope

- Modify `.goose/skills/gtkb-bridge-propose/helpers/write_bridge.py`
  `propose_bridge_codex_non_bypass` to mint+consume a publication capability.
- Add a focused test (e.g., `platform_tests/scripts/test_bridge_helper_publication_capability.py`)
  covering the mint-write-consume and compensation paths.

## Out Of Scope

- Retroactive recovery of already-stranded files (WI-5314 -015, WI-5368
  -023/-027/-028) - a separate owner-directed exceptional recovery.
- Any change to `scripts/gtkb_bridge_writer.py` or the governed writer.
- Git mutation, cleanup, retirement, deployment, release, or MemBase mutation.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` requires
numbered-file chain authority and publication-capability evidence;
`DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`,
`GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, and
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` govern the transaction. No new owner
decision is needed to file this proposal.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | After the helper writes a bridge file, `check_protected_commit_authorization` accepts the path (exact consumed publication capability). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused test passes; `python -m pytest platform_tests/scripts/test_bridge_helper_publication_capability.py -q --tb=short`. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | All existing bridge/helper behavior preserved; fail-closed compensation on write failure. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | The mint/consume transaction uses the author session and correct operation type. |

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5942; WI-5314/WI-5368 stranding evidence; GOV-FILE-BRIDGE-AUTHORITY-001",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001; DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
  "primary_route": "helper mints+consumes publication capability on every bridge write, mirroring the governed writer",
  "before_behavior": "helper-written bridge files lack publication capability; atomic VERIFIED finalization strands (WI-5825-class)",
  "after_behavior": "every helper-written bridge file gains an exact consumed publication capability and can reach durable VERIFIED",
  "self_descriptive_naming": "propose_bridge_codex_non_bypass gains the governed mint-write-consume transaction",
  "obsolete_guidance_disposition": "None; the helper now conforms to the governed writer contract",
  "history_preservation": "Append-only bridge writes preserved; no prior file rewritten; compensation only on failed writes",
  "baseline": {
    "affected_files": ["gtkb-wi5314-...-015.md", "gtkb-wi5368-...-023.md", "gtkb-wi5368-...-027.md", "gtkb-wi5368-...-028.md"],
    "helper_mint_import": "absent",
    "governed_writer_mint_import": "present (write_bridge_file)"
  },
  "expected_result": {
    "helper_publication_capability": "minted + consumed on every write",
    "future_stranding": "prevented (WI-5825-class)",
    "existing_stranded_files": "unchanged (separate exceptional recovery)"
  },
  "hard_invariants": [
    "no retroactive change to already-stranded files",
    "no change to scripts/gtkb_bridge_writer.py or the governed writer",
    "append-only bridge history preserved",
    "compensation fails closed on any write failure"
  ],
  "fail_closed_conditions": [
    "mint failure before write - no file written",
    "exclusive-create race - compensate and refuse",
    "post-write byte mismatch - compensate and fail",
    "consume failure - compensate"
  ],
  "rollback": {
    "instructions": "revert the helper change under separately authorized Git mechanics; restore the pre-fix propose_bridge_codex_non_bypass if a regression appears",
    "test": "rerun the focused test and confirm the helper writes bridge files without publication capability stranding"
  },
  "essential_context_preservation": "All governed writer behavior, bridge chain authority, and existing helper filing behavior are preserved except for the added publication-capability transaction."
}
```

## Acceptance Criteria

- `propose_bridge_codex_non_bypass` mints+consumes a publication capability on
  every bridge write when registry publication is enabled.
- A helper-written bridge file gains an exact `consumed` publication capability
  with matching content digest (verifiable by
  `check_protected_commit_authorization`).
- Write failures compensate and fail closed without stranding.
- Focused test passes; ruff check/format pass.
- No already-stranded file is retroactively modified.

## Prior Deliberations

- `DELIB-202667722` - protected-commit timer/TTL invariant discipline; prior
  WI-5368 stranding lineage.
- Owner decision A (2026-08-05) - file systemic fix for helper
  publication-capability stranding.
- `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-016.md`,
  `bridge/gtkb-wi5368-codex-git-window-command-family-030.md` - the NO-GOs that
  surfaced the stranding.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Note On Required PAUTH / GO / Claim / Start

This proposal is filed under the active project-scope PAUTH
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`.
No implementation may begin until an independent bridge `GO`, a matching
work-intent claim, and a successful implementation-start packet exist. The
already-stranded files (WI-5314 -015, WI-5368 -023/-027/-028) are out of scope
and require separate owner-authorized exceptional recovery.

## Request

Request independent Loyal Opposition review (GO/NO-GO). If GO, Prime Builder
will acquire a claim, pass implementation-start, implement the helper mint/consume
integration + focused test, run spec-derived verification, and file an
implementation report requesting VERIFIED.

---
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
