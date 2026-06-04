# DELIB-S414-DOCUMENT-AUTHOR-PROVENANCE-PAUTH-AUTHORIZATION

**Source:** Owner AUQ chain in S414 /loop autonomous tick (2026-06-04 UTC) addressing the corrective NO-GO at `bridge/gtkb-document-author-provenance-contract-002.md`.

**Refines:** The standing reliability fast-lane PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` did NOT cover the proposed scope of WI-3399's implementation (new GOV spec + helpers + hook + MemBase mutation; ~500-800 LOC; commit type `feat:`). The NO-GO -002 cited this as P1 findings F1 (fast-lane criteria mismatch) and F2 (mutation classes not enumerated).

## AUQ Chain

1. **Q (S414 turn):** "How should the `gtkb-document-author-provenance-contract` NO-GO -002 be unblocked?"
   **A:** "Authorize new project-scoped PAUTH (Recommended)" — mint a new PAUTH covering the full feature scope; WI-3399 stays as-is; file REVISED citing the new PAUTH.

2. **Q (S414 turn):** "Which project should the new feature-scope PAUTH attach to?"
   **A:** "Mint new PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE (Recommended)" — create a new dedicated project for the provenance contract; cleanest scope boundary.

3. **Q (S414 turn):** "What mutation-class scope should the new PAUTH grant?"
   **A:** "Feature-full (Recommended)" — `allowed_mutation_classes = [source, test_addition, hook_upgrade, config_governance, governance_spec_insertion, formal_artifact_insertion]`; `forbidden_operations = [deploy, git_push_force, spec_deletion]` (standard floor).

## Decision

Authorize implementation work for the document-author-provenance contract under a new project-scoped PAUTH on the new `PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE` project. WI-3399 becomes a member of this project (in addition to its existing memberships in `PROJECT-GTKB-LO-ADVISORY-ROUTING` and `PROJECT-GTKB-RELIABILITY-FIXES`).

The new PAUTH carries the feature-full mutation scope above. Per-artifact formal-artifact-approval packets are still required for GOV-DOCUMENT-AUTHOR-PROVENANCE-001 insertion under `GOV-ARTIFACT-APPROVAL-001` (the PAUTH grants scope; per-artifact owner approval remains intact).

## Lineage

- `bridge/gtkb-document-author-provenance-contract-001.md` — NEW Prime proposal (cites the too-narrow PAUTH).
- `bridge/gtkb-document-author-provenance-contract-002.md` — LO NO-GO -002 (the trigger for this AUQ chain).
- `INSIGHTS-2026-05-27-13-24-DOCUMENT-ARTIFACT-AUTHOR-PROVENANCE-GAP.md` — the LO advisory establishing the provenance gap.
- `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3399` — earlier S414 PWM noting Q1=All 5 surfaces, Q2=Forward-only, Q3=New GOV-DOCUMENT-AUTHOR-PROVENANCE-001, Q4=Adopt.

## Implementation deltas implied

1. New project `PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE` created (this session).
2. WI-3399 added to the new project as `member`.
3. New PAUTH `PAUTH-PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE-WI-3399-FEATURE-FULL` minted (this session).
4. REVISED -003 filed on `bridge/gtkb-document-author-provenance-contract` citing the new PAUTH + scope.
5. LO re-reviews; on GO, implementation proceeds per the now-broader authorization envelope.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
