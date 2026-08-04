REVISED
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-03T15-24-47Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb

# WI-5429 Finalized Runtime-Generation Admission Recovery - REVISED (refreshed cohort hashes)

bridge_kind: prime_proposal
Document: gtkb-wi5429-finalized-runtime-generation-admission-recovery
Version: 003
Date: 2026-08-04 UTC
Responds to: bridge/gtkb-wi5429-finalized-runtime-generation-admission-recovery-002.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5429-FINALIZED-GENERATION-ADMISSION-V2-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5429
target_paths: ["scripts/dispatcher_generation_admission.py", "scripts/ensure_dispatcher_daemon.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_generation_admission.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py"]
implementation_scope: finalized_generation_admission_repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation: this proposal performs no MemBase or `groundtruth.db` write or mutation.

## Revision Claim

This REVISED proposal responds to NO-GO v002, which found a single P0 blocking
finding: `scripts/gtkb_dispatcher_daemon.py` SHA-256 drifted from the v001
cohort table (`e9a9dfb9...` declared vs `754ed871...` observed), tripping the
proposal's own any-target-preimage-drift gate. The other four declared targets
matched.

This revision refreshes the Exact Current Evidence hash table with the current
live values and preserves the materializer repair plan unchanged. No source or
test change is proposed in this revision; it re-pins the cohort so
implementation can start from a current, drift-free preimage set.

## Refreshed Exact Current Evidence (current live SHA-256)

| Target | Current SHA-256 | Git status |
| --- | --- | --- |
| `scripts/dispatcher_generation_admission.py` | `a3b9efb3032534f43c4759f64cb22b685e19d3944b979a343e00ce4d55524415` | clean |
| `scripts/ensure_dispatcher_daemon.py` | `5f172ce9a0917532500632e91f37625975d5c4c140524428a27f3aede4b9c317` | clean |
| `scripts/gtkb_dispatcher_daemon.py` | `754ed8719ce141dba048f8cfd770cdcf88fb94d43d5efc792ab34b307d416c32` | clean |
| `platform_tests/scripts/test_dispatcher_generation_admission.py` | `71a2fae7a76939ab3c33cb370ef860535f8c81ac8b92215a8b19ada0bd4fa0e7` | clean |
| `platform_tests/scripts/test_dispatcher_daemon_supervision.py` | `8b50f98738cb396ef2a012afa20d7070c512cd923935c834bc9a0644dfca4975` | clean |

## Response To NO-GO-002 F1 (P0) - gtkb_dispatcher_daemon.py SHA-256 drift

Accepted and corrected. The live file hash is `754ed871...` (not the v001
declared `e9a9dfb9...`). This revision re-pins the cohort with the current
values above, so all five declared targets now match their live preimages.
The other four targets were already matching at v002 review time and remain so.

## Preserved Repair Plan (unchanged from v001, non-authorizing)

The proposed fix for `materialize_generation()` in
`scripts/dispatcher_generation_admission.py` (initialize error accumulator,
single `_compute_generation_hash()` identity, one manifest pass, no live
dispatcher/TAFE mutation) remains the right minimum repair for the reproduced
undefined-name failures. This revision does not implement it; implementation
begins only after an independent GO, exact claim, and schema-v3 start packet.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Requirement Sufficiency

Existing requirements sufficient. The materializer repair (initialize error
accumulator, single `_compute_generation_hash()` identity, one manifest pass)
is fully defined by the existing governing specifications; the NO-GO finding
was a cohort-hash drift, not a requirement gap. No new or revised requirement
is needed before implementation.

## Prior Deliberations

- `bridge/gtkb-wi5429-finalized-runtime-generation-admission-recovery-002.md` - NO-GO this filing responds to (P0 cohort hash drift).
- `bridge/gtkb-wi5429-finalized-runtime-generation-admission-recovery-001.md` - prior NEW proposal (repair plan carried forward).
- `DELIB-20260718-DISPATCHER-HOLD-NARROW-WI5429-FIRST`
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD`
- Historical `gtkb-wi5429-finalized-runtime-generation-admission` v008 NO-GO (substantive defect evidence).

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5429 finalized-runtime-generation-admission-recovery; NO-GO v002 (P0 cohort hash drift); refreshed preimages",
  "baseline": {
    "declared_targets": 5,
    "drifted_target_at_v002": "scripts/gtkb_dispatcher_daemon.py",
    "drifted_hash_at_v002": "754ed8719ce141dba048f8cfd770cdcf88fb94d43d5efc792ab34b307d416c32"
  },
  "essential_context_preservation": "Preserve the materializer repair design, exact cohort preimages, project-only authorization, immutable v001/v002 bridge history, and all independent GO/claim/start/verification gates",
  "canonical_authority": "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "REVISED with refreshed cohort preimages; then independent GO, exact claim, schema-v3 start, repair implementation, report, and independent verification",
  "before_behavior": "One declared target (gtkb_dispatcher_daemon.py) hash drifted from the v001 cohort, tripping the any-target-preimage-drift gate",
  "after_behavior": "All five declared targets re-pinned to their current live preimages; repair plan preserved unchanged",
  "self_descriptive_naming": "Refresh cohort hashes; preserve repair design",
  "obsolete_guidance_disposition": "v001 hash table superseded by current values; repair design retained",
  "history_preservation": "v001 and v002 preserved append-only; this v003 re-pins preimages",
  "expected_result": {
    "cohort_preimages_current": true,
    "repair_plan_preserved": true,
    "live_dispatcher_tafe_mutation": false
  },
  "hard_invariants": [
    "No source/test mutation in this revision",
    "No live dispatcher/TAFE mutation",
    "Implementation begins only after independent GO, exact claim, and schema-v3 start"
  ],
  "fail_closed_conditions": [
    "Any target preimage drift after this revision",
    "Missing GO, claim, or start packet before implementation"
  ],
  "rollback": "No source change in this revision; supersede any incorrect evidence append-only"
}
```

## Specification-Derived Verification

| Specification / governing surface | Executed evidence | Result |
| --- | --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | `git status --short` on all five targets | no output (all clean) |
| Exact cohort preimages | SHA-256 recomputation of all five targets | values in refreshed table above; no drift now |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Append-only chain v001 -> v002 -> v003 | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Active PAUTH covers all five targets | PASS |

## Commands Run

- `python -c "import hashlib; ...sha256 of all five targets..."` -> values in refreshed table.
- `git status --short -- <five targets>` -> no output (clean).

## Files Changed

No source or test file changed by this revision. It refreshes the declared
preimage cohort hashes only.

## Recommended Commit Type

`fix` (for the separately authorized implementation once GO'd).

## Requested Loyal Opposition Action

Return `GO` if the refreshed cohort preimages and the preserved materializer
repair plan are acceptable, or `NO-GO` with concrete corrections.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
