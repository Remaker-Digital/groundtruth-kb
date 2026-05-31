ADVISORY

author_identity: Antigravity Loyal Opposition
author_harness_id: C
author_model: Gemini 3.5 Flash (High)
author_model_configuration: Antigravity sdk, scoped owner-action advisory review

bridge_kind: loyal_opposition_advisory
Document: gtkb-antigravity-implements-link-ambiguity-advisory
Version: 001
Author: Antigravity Loyal Opposition
Date: 2026-05-30 UTC
Source advisory reviewed: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-30-05-04.md

Specs: GOV-FILE-BRIDGE-AUTHORITY-001, SPEC-AUQ-POLICY-ENGINE-001, DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001, GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001
WIs: WI-3462, WI-3398, WI-3423

# Advisory - Scoped Resolution for Ambiguous Implements-Links Mappings

## Summary

This advisory establishes a clear, sequential path to resolve the remaining `implements-link` ambiguities for the Platform Developer Platform.

1. **WI-3462 Clean Backfill is Terminal Closed**: The Phase-2 implements-link backfill (WI-3462) has been fully implemented, formatted cleanly, and VERIFIED on the live bridge in `bridge/gtkb-implements-link-backfill-phase2-implementation-006.md`. No duplicate formatting or backfill work is needed.
2. **Ambiguity Resolution is Highly Scoped**: Four of the five originally flagged ambiguous projects have already been cleanly linked during the Phase-2 `--apply` run. Only one project—`PROJECT-PROJECT-GTKB-RELIABILITY-FIXES`—remains unlinked due to competing candidate threads.
3. **One-at-a-Time Owner Decisions**: To respect the owner-action protocol and avoid user-burden, this advisory breaks down the two remaining ambiguous work items into sequential, one-at-a-time choices for Mike.

Recommended Prime Builder disposition: Acknowledge this advisory. Sequence and resolve the two decisions below one-at-a-time, allowing a final scoped `--apply` execution to link the project and arm the v4 completion gates.

---

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`

---

## Technical Audit: Current Implements-Link Status

A live audit of the `groundtruth.db` database and the `backfill_implements_links.py` classification shows that the platform's arming state has reached high readiness:

- **CLEAN Projects Backfilled**: 24 projects are cleanly resolved and have active `implements` links recorded in `project_artifact_links` (totaling 39 active links). This includes the successful resolution of projects such as `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`, `PROJECT-GTKB-GOVERNANCE-HARDENING`, and `PROJECT-GTKB-LO-ADVISORY-INTAKE`.
- **UNADDRESSED Projects Paused**: 11 projects have work items with no candidate addressing threads and remain untouched.
- **SINGLE AMBIGUOUS Project Left**: Only `PROJECT-PROJECT-GTKB-RELIABILITY-FIXES` (PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING) is flagged as `AMBIGUOUS` because two of its gating work items (`WI-3398` and `WI-3423`) resolve to multiple candidate threads.

---

## Sequential Owner Decisions

Per the Way of Working protocol (`independent-progress-assessments/CODEX-WAY-OF-WORKING.md`), Mike's inputs must be requested one item at a time. Therefore, we present **Decision 1** as the active, blocking decision. Once Mike selects an option for Decision 1, the Prime Builder should present Decision 2.

### OWNER ACTION REQUIRED (Decision 1 of 2)

> [!IMPORTANT]
> **Select the Canonical Bridge Thread for WI-3398 (PROJECT-PROJECT-GTKB-RELIABILITY-FIXES)**
>
> **Ambiguous Work Item:** `WI-3398`  
> **Gating Project:** `PROJECT-PROJECT-GTKB-RELIABILITY-FIXES`  
>
> The backfill tool found two competing candidate threads for `WI-3398`. Please designate which thread is the authoritative implementation thread:
>
> - **Option A:** `gtkb-prime-worker-context-aware-auq-slice-2` (Slice 2 context-aware AUQ implementation)
> - **Option B:** `gtkb-prime-worker-post-stop-dispatch-retry-slice-3` (Slice 3 post-stop retry implementation)
>
> **Why this matters:** Designating the canonical thread allows the backfill tool to associate `WI-3398` with its verified bridge history, paving the way for `PROJECT-PROJECT-GTKB-RELIABILITY-FIXES` to auto-complete once all its work items are verified.
>
> **Expected Reply Shape:**  
> Please respond with your choice:  
> `PROJECT-PROJECT-GTKB-RELIABILITY-FIXES / WI-3398 -> [Option A | Option B]`

---

### OWNER ACTION REQUIRED (Decision 2 of 2 - Queued)

> [!NOTE]
> **This decision is currently queued and will be activated immediately after Decision 1 is resolved.**
>
> **Ambiguous Work Item:** `WI-3423`  
> **Gating Project:** `PROJECT-PROJECT-GTKB-RELIABILITY-FIXES`  
>
> - **Option A:** `gtkb-platform-tests-ruff-cleanup` (Ruff platform test cleanup implementation)
> - **Option B:** `gtkb-wi-3423-pauth-creation` (PAUTH registry and auth envelope creation)
>
> **Expected Reply Shape:** (To be provided once Decision 1 is resolved).

---

## Prime Builder Implementation Context

Objective: Provide a clean path for the Prime Builder to ingest these owner choices and execute a final, scoped implements-link backfill.

Preconditions and constraints:
- `bridge/INDEX.md` remains the sole coordinator for bridge queue state.
- Once Mike provides the decision for `WI-3398`, the Prime Builder should draft a normal follow-on implementation proposal (e.g., `bridge/gtkb-project-reliability-fixes-implements-link-backfill-001.md`) that documents the approved link mapping.
- The backfill script `scripts/backfill_implements_links.py` should NOT be modified. Instead, the resolved links can be applied cleanly using the deterministic database APIs or via a small, focused patch script if required.

Open decisions required from owner now: **Decision 1 of 2**.

---

## Commands Executed

```text
python scripts/backfill_implements_links.py --report
Get-Content -Raw bridge/gtkb-implements-link-backfill-phase2-implementation-006.md
Get-Content -Raw independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-30-05-04.md
```

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
