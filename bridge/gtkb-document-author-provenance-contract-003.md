REVISED

# Implementation Proposal REVISED — Document Artifact Author Provenance Contract (WI-3399)

bridge_kind: prime_proposal
Document: gtkb-document-author-provenance-contract
Version: 003
Author: Prime Builder (Claude Opus 4.7, harness B)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-document-author-provenance-contract-002.md (NO-GO)
Session: S414 /loop autonomous tick

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 65ea0a52-0609-49c4-86fc-fdf62b6239df
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, /loop autonomous tick

Source advisory: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-27-13-24-DOCUMENT-ARTIFACT-AUTHOR-PROVENANCE-GAP.md (Codex Prime Builder, harness A, 2026-05-27)

Project: PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE
Project Authorization: PAUTH-PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE-PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE-WI-3399-FEATURE-FULL-AUTHORIZATION
Work Item: WI-3399
work_item_ids: [WI-3399]
target_paths: ["scripts/document_author_metadata.py", "scripts/check_document_author_metadata.py", "platform_tests/scripts/test_document_author_metadata.py", ".claude/hooks/document_author_provenance_gate.py", ".codex/gtkb-hooks/document_author_provenance_gate.py", ".claude/settings.json", ".codex/hooks.json", "config/governance/document-author-provenance.toml", "groundtruth.db"]
spec_ids: ["GOV-DOCUMENT-AUTHOR-PROVENANCE-001"]

Recommended commit type: feat

---

## Revision Claim

The prior NEW `-001` was NO-GO'd at `-002` on two P1 findings:

- **F1:** Scope mismatch with `GOV-RELIABILITY-FAST-LANE-001` eligibility (the proposal is a feature, not a small defect fix; ~500-800 LOC; commit type `feat`).
- **F2:** The cited `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` allowed_mutation_classes (`source/test_addition/hook_upgrade`) does not enumerate governance-spec insertion, generic config governance changes, or MemBase formal-artifact mutation.

This REVISED supersedes the prior PAUTH citation with a new project-scoped PAUTH minted in this session per owner AUQ S414 (DELIB-20260666). Substantive scope is unchanged; the authorization envelope is now scope-appropriate.

## Findings Addressed

### F1 — Fast-lane criteria mismatch

**Resolution:** Removed `GOV-RELIABILITY-FAST-LANE-001` from the authorizing spec scope. The new authorization basis is `PAUTH-PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE-...-FEATURE-FULL-AUTHORIZATION`, a standard project-scoped PAUTH covering the full feature scope. No fast-lane eligibility is claimed.

### F2 — PAUTH mutation classes don't enumerate proposed scope

**Resolution:** New PAUTH `PAUTH-PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE-PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE-WI-3399-FEATURE-FULL-AUTHORIZATION` carries `allowed_mutation_classes = [source, test_addition, hook_upgrade, config_governance, governance_spec_insertion, formal_artifact_insertion]`. This explicitly enumerates the proposed mutation surfaces, including governance-spec insertion (`GOV-DOCUMENT-AUTHOR-PROVENANCE-001`) and `groundtruth.db` formal-artifact mutation. Forbidden operations remain `[deploy, git_push_force, spec_deletion]` (standard floor).

Per-artifact formal-artifact-approval packets for `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` insertion are still required under `GOV-ARTIFACT-APPROVAL-001`; the PAUTH grants the implementation-scope authorization, not formal-artifact-approval substitution.

### Notes on NO-GO -002 § "Required revisions"

The NO-GO offered two paths: (1) refile under standard project authorization, or (2) split into fast-lane source/test/hook bridge + separate formal-artifact bridge. Owner AUQ S414 picked **Path 1** (single bridge, new project-scoped PAUTH). This REVISED implements Path 1.

## Owner Decisions / Input

Owner-grilling-gate AUQ from NEW -001 (2026-06-04 UTC) carried forward:

| Q | Topic | Owner answer |
|---|-------|--------------|
| Q1 | Scope: which markdown surfaces? | **All 5 surfaces** (bridge/, .claude/rules/, independent-progress-assessments/, memory/, docs/). |
| Q2 | Backfill posture for existing files? | **Out of scope (forward-only)**. Contract applies to files written AFTER implementation; existing files grandfathered. |
| Q3 | Rule home / authority? | **New GOV-DOCUMENT-AUTHOR-PROVENANCE-001**. Dedicated governance spec, cross-linked to `GOV-ARTIFACT-APPROVAL-001`. |
| Q4 | Disposition? | **Adopt** — file impl proposal with captured scope. |

Additional AUQ decisions captured in S414 /loop autonomous tick (this session; archived as `DELIB-20260666`):

| Q | Topic | Owner answer |
|---|-------|--------------|
| Q5 | Unblock strategy for NO-GO -002? | **Authorize new project-scoped PAUTH** (Path 1 of NO-GO's two paths). |
| Q6 | Which project for the new PAUTH? | **Mint new `PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE`**. |
| Q7 | Mutation-class scope for the new PAUTH? | **Feature-full**: `[source, test_addition, hook_upgrade, config_governance, governance_spec_insertion, formal_artifact_insertion]`; forbid `[deploy, git_push_force, spec_deletion]`. |

Adopt at Q4 + the S414 PAUTH-authorization AUQ chain are the operative owner-approval evidence required by `.claude/rules/peer-solution-advisory-loop.md` § Approval-Gate + bridge-cycle revision protocol.

## Specification Links

Carried forward + updated per NO-GO findings:

- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval packets required for `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` insertion (per-artifact packet generated at impl time; not a PAUTH substitute).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance umbrella; provenance is a fundamental artifact-orientation discipline.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; provenance contract extends the existing bridge-author-metadata enforcement to non-bridge document surfaces.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project authorization mandate; the new project-scoped PAUTH covers this WI via active membership in `PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE`.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — PAUTH envelope structure.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — PAUTH does not bypass bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec linkage mandate.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived testing mandate.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle trigger chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development; provenance is a tier-zero artifact property.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — root-boundary; all work stays inside `E:\GT-KB` and outside `applications/`.

**Removed at revision:** `GOV-RELIABILITY-FAST-LANE-001` — no longer the authorizing scope rule per NO-GO -002 F1. The work is feature-scope, not fast-lane-scope.

**New specifications drafted by this proposal:** `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — the new governance contract per owner Q3.

## Prior Deliberations

- `DELIB-20260666` (S414 /loop autonomous tick, 2026-06-04) — owner AUQ chain authorizing the new project + PAUTH. This is the operative owner-decision evidence for this REVISED.
- `DELIB-2720` (per NO-GO -002 § Prior Deliberations) — adjacent in-source provenance anchors thread.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — relevant to the proposed deterministic checker/hook shape.
- `bridge/gtkb-document-author-provenance-contract-001.md` — original NEW proposal (substantive scope is carried forward unchanged).
- `bridge/gtkb-document-author-provenance-contract-002.md` — corrective NO-GO surfacing the PAUTH scope mismatch.

## Authorization Evidence

- **WI-3399:** version ≥2, priority `P1`, origin `hygiene`, stage `created`.
- **Project memberships (active):**
  - `PWM-PROJECT-GTKB-LO-ADVISORY-ROUTING-WI-3399` (S366 routing).
  - `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3399` (S414 earlier adoption; remains for routing visibility).
  - `PWM-PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE-WI-3399` (this session; new dedicated project).
- **PAUTH** (active, no expiry): `PAUTH-PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE-PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE-WI-3399-FEATURE-FULL-AUTHORIZATION`, owner_decision_deliberation_id `DELIB-20260666`, `allowed_mutation_classes = [source, test_addition, hook_upgrade, config_governance, governance_spec_insertion, formal_artifact_insertion]`, `forbidden_operations = [deploy, git_push_force, spec_deletion]`.

## Requirement Sufficiency

Existing requirements sufficient. The substantive scope is unchanged from NEW `-001`; the revision concerns the authorization envelope (PAUTH), not the requirements being implemented.

## Proposed Scope

Substantive scope unchanged from NEW `-001`. Briefly:

1. Create `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` (new governance spec, per-artifact formal-approval packet generated at impl time).
2. Build reusable helper `scripts/document_author_metadata.py` (promoting the six-field pattern from `scripts/bridge_author_metadata.py`).
3. Build audit checker `scripts/check_document_author_metadata.py`.
4. Wire PreToolUse Write hook `document_author_provenance_gate.py` on Claude Code (`.claude/hooks/`) + Codex (`.codex/gtkb-hooks/`) parity.
5. Tests under `platform_tests/scripts/test_document_author_metadata.py`.
6. Config at `config/governance/document-author-provenance.toml` (governed surfaces, exclusions).

Forward-only posture per owner Q2.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight Subsection, will re-run after INDEX update:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-document-author-provenance-contract
```

Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

## Specification-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, the substantive verification plan is unchanged from NEW `-001`. Each linked spec maps to:

- Helper-behavior tests (`platform_tests/scripts/test_document_author_metadata.py`) covering the six-field provenance shape, deterministic emission, surface coverage.
- Checker-behavior tests covering the audit-mode scan over the 5 governed surfaces with forward-only exclusion of grandfathered files.
- Hook tests (Claude + Codex parity) confirming PreToolUse Write of a new governed-surface markdown without provenance is BLOCKED.
- Linting/formatting under repo conventions (`ruff check` + `ruff format --check`).
- MemBase verification: `gt spec get GOV-DOCUMENT-AUTHOR-PROVENANCE-001` returns the inserted v1.

Detailed test inventory is in NEW `-001` § "Specification-Derived Verification Plan" (unchanged).

## Risk / Rollback

Risk and rollback unchanged from NEW `-001`. Briefly:

- **Risk:** forward-only enforcement could surprise authors of new bridge files. Mitigation: rolled out behind an explicit governed-surface allowlist; clear error message points to the helper script and the GOV spec.
- **Rollback:** revert the hook registration in `.claude/settings.json` + `.codex/hooks.json`; the helper script and config file are inert without the hook.

## Bridge Filing

Will insert at top of the `gtkb-document-author-provenance-contract` entry in `bridge/INDEX.md`:

```text
Document: gtkb-document-author-provenance-contract
REVISED: bridge/gtkb-document-author-provenance-contract-003.md
NO-GO: bridge/gtkb-document-author-provenance-contract-002.md
NEW: bridge/gtkb-document-author-provenance-contract-001.md
```

## Recommended Commit Type

`feat:` — net-new cross-document governance + enforcement capability. Same as NEW `-001`; the corrective fast-lane mismatch did not change the commit-type recommendation, only the authorization basis.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
