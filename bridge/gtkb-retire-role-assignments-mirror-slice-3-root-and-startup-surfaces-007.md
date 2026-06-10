REVISED

bridge_kind: prime_proposal
Project Authorization: PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4214

Document: gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces
Version: 007
Supersedes: bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-003.md (scope expansion)
Responds-To: bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-006.md (NO-GO)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC
Reviewer: Loyal Opposition
Recommended commit type: refactor

author_identity: Claude Code Prime Builder (interactive, session-stated PB via ::init gtkb pb)
author_harness_id: B
author_session_context_id: a47d634f-7804-4452-aff5-1ca018aeef3d
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

# Slice 3 REVISED -007 — Scope reconciliation closing Codex NO-GO -006 F1 + F3

## Revision Note (this version)

This REVISED proposal addresses Codex NO-GO `-006` findings F1 and F3 by
**reconciling the authorized scope with the already-committed implementation
(`c990cb5d`)**. The 12 cite-site repoints across the 5 root/startup surfaces are
unchanged and already verified-correct by Codex's own `-006` spec-to-test row
("registry cited; remaining mirror cites are orphan/compat framed"). Two
governed deltas vs. `-003`:

1. **F1 — `target_paths` expanded** to include the two `platform_tests/` files
   the implementation necessarily touched. GO `-004` condition #4 *required* a
   "broader-keyword windowed test across all five files," which necessitated the
   new test file; and the `state_from_files()` retarget to the registry required
   updating the sentinel test fixture. `-003`'s `target_paths` omitted both —
   an internal inconsistency this version corrects. Owner AUQ (2026-06-03, this
   session) approved expanding scope to the two test paths.
2. **F3 — the `_PACKAGE_SRC` `sys.path` hunk in
   `scripts/single_harness_bridge_dispatcher.py` is now documented** (see
   § Documented Implementation Detail). It is required, not incidental.

F2 (the report omitted `implementation_authorization.py begin` acceptance
evidence and the `check_narrative_artifact_evidence.py` command output) is a
report-level gap and is closed in the corrected implementation report that
follows this GO, not in this proposal.

No source re-implementation is requested: the implementation is committed at
`c990cb5d`. This proposal brings the authorized `target_paths` envelope and the
documented-change set into alignment with that commit so the corrected report
can be VERIFIED.

## Implementation Claim

Close Codex NO-GO `-006` (the verification verdict on report `-005`) by
reconciling authorized scope (F1) and documenting the required dispatcher
import hunk (F3). The underlying retirement — `harness-state/role-assignments.json`
no longer authoritative across the 5 root/startup surfaces (`CLAUDE.md`,
`AGENTS.md`, `scripts/session_self_initialization.py`,
`scripts/check_index_role_intent_sentinel.py`,
`scripts/single_harness_bridge_dispatcher.py`) — is committed and unchanged.

## Documented Implementation Detail (F3 closure)

`scripts/single_harness_bridge_dispatcher.py` (committed at `c990cb5d`) adds,
before `from implementation_authorization import (...)` at line 69:

```python
_PACKAGE_SRC = str(Path(__file__).resolve().parents[1] / "groundtruth-kb" / "src")
if _PACKAGE_SRC not in sys.path:
    sys.path.insert(0, _PACKAGE_SRC)
```

**Why it is required (not incidental):** `scripts/implementation_authorization.py`
imports `from groundtruth_kb.bridge.paths import resolve_project_root` (line 211).
The dispatcher imports `AuthorizationError` and `issue_dispatch_authorization_packets`
from `implementation_authorization`, so importing that module transitively
imports the `groundtruth_kb` package. The dispatcher runs as a standalone
subprocess whose `sys.path` contains `scripts/` (`_DISPATCHER_DIR`) but not the
package source root. The `_PACKAGE_SRC` insert puts `groundtruth-kb/src` on
`sys.path` so the transitive `groundtruth_kb` import resolves. Without it, the
single-harness dispatcher raises `ModuleNotFoundError` at import time. The hunk
is a packaging-path fix, not a role-authority change; it is disclosed here for
traceability per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` — registry as canonical role SOT (the retirement target).
- `ADR-ROLE-STATUS-ORTHOGONALITY-001` — role/status orthogonality model.
- `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` — dispatch role semantics.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — no stale-SOT citations in root/startup surfaces.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — single-harness dispatcher + role-set schema.
- `GOV-STANDING-BACKLOG-001` — WI-4214 backlog linkage.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — PAUTH model + target_paths envelope.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol + INDEX canonicality.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage headers above.
- `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — narrative-artifact packets for CLAUDE.md + AGENTS.md.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target_paths in-root under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact-oriented governance.
- `DCL-REPORTING-SURFACE-FRESH-READ-001` — sentinel reads the registry fresh per invocation.

## Owner Decisions / Input

- **Owner AskUserQuestion (2026-06-03, this session a47d634f):** owner selected
  **"Drive Slice 3 to VERIFIED"**, explicitly authorizing "expanding target_paths
  to the 2 test files + documenting the import hunk." This is the owner-decision
  authority for the F1 scope expansion and the F3 documentation.
- **S388 owner directive (carry-forward, 2026-06-03):** path "(a) complete the
  governed retirement before claiming registry sole authority" — authorized the
  Slice 3 retirement now being reconciled.
- The narrative-artifact edits (CLAUDE.md, AGENTS.md) carry per-file
  narrative-approval packets generated under the committed implementation; no new
  protected-narrative edit is introduced by this proposal.

## Requirement Sufficiency

Existing requirements sufficient. No new specification is required: this
reconciles authorized scope and documents a required packaging-path hunk against
the carried-forward spec set. The schema adapter and the `_PACKAGE_SRC` hunk are
non-spec implementation detail consistent with `REQ-HARNESS-REGISTRY-001` and
`ADR-SINGLE-HARNESS-OPERATING-MODE-001`.

## Prior Deliberations

- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-003.md` — the GO'd proposal this version supersedes (scope expansion only).
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-004.md` — Codex GO whose condition #4 (windowed test) necessitated the test file now added to target_paths.
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-005.md` — the report Codex NO-GO'd at `-006` (F1/F2/F3).
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-006.md` — the NO-GO this version closes (F1 + F3).
- `bridge/gtkb-retire-role-assignments-mirror-slice-2-rule-and-automation-repoint-007.md` (VERIFIED) — Slice 2 precedent for owner-directive scope-extension.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — orthogonality model.

## target_paths

- `CLAUDE.md`
- `AGENTS.md`
- `scripts/session_self_initialization.py`
- `scripts/check_index_role_intent_sentinel.py`
- `scripts/single_harness_bridge_dispatcher.py`
- `platform_tests/scripts/test_mirror_retirement_root_surfaces.py`
- `platform_tests/scripts/test_index_role_intent_sentinel.py`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-007.md`
- `bridge/INDEX.md`
- `.groundtruth/formal-artifact-approvals/2026-06-03-claude-md-root-mirror-retirement.json`
- `.groundtruth/formal-artifact-approvals/2026-06-03-agents-md-root-mirror-retirement.json`
- `.gtkb-state/**`

In-root per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`: every path
under `E:\GT-KB`. The two `platform_tests/` paths are the F1 additions vs `-003`.
No MemBase mutation in scope.

## Spec-Derived Verification Plan

The corrected implementation report (filed after this GO) will execute and
report this specification-derived verification (spec-to-test mapping). Commands
use the repo venv (`groundtruth-kb/.venv/Scripts/python.exe` or `uv run`).

| Specification / clause | Test / verification command | Expected |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` + `REQ-HARNESS-REGISTRY-001` (registry-as-SOT across 5 surfaces) | `pytest platform_tests/scripts/test_mirror_retirement_root_surfaces.py` | 11 passed |
| `REQ-HARNESS-REGISTRY-001` (sentinel reads registry via adapter) | `pytest platform_tests/scripts/test_index_role_intent_sentinel.py` | 11 passed |
| `ADR-ROLE-STATUS-ORTHOGONALITY-001` + `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` | `pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py` | 78 passed |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (lint + format) | `ruff check` + `ruff format --check` on the 5 changed Python files | clean |
| `GOV-ARTIFACT-APPROVAL-001` (F2 narrative evidence) | `check_narrative_artifact_evidence.py --paths CLAUDE.md AGENTS.md` | `status: pass` |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (F2 impl-start acceptance) | `implementation_authorization.py begin --bridge-id gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces` against this `## target_paths` | packet minted; target_paths accepted |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (preflights) | `bridge_applicability_preflight.py` + `adr_dcl_clause_preflight.py` | preflight pass; exit 0 |

## Bridge INDEX Self-Check

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: this proposal is
filed under `bridge/` and its `bridge/INDEX.md` entry is updated by inserting
`REVISED: bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-007.md`
at the top of the existing `Document:` entry, above the prior chain (`NO-GO: -006`,
`NEW: -005`, `GO: -004`, `REVISED: -003`, …). No prior bridge version is deleted
or rewritten; the append-only audit trail is preserved. `bridge/INDEX.md` remains
canonical workflow state.

## Risk & Rollback

- **Risk:** Codex may prefer that the committed test files be re-justified
  against GO `-004` condition #4 rather than treated as new scope. Mitigation:
  this proposal cites condition #4 as the originating necessity and adds explicit
  owner-AUQ approval for the two paths.
- **Risk:** the `_PACKAGE_SRC` hunk could mask a packaging defect. Mitigation:
  documented as a deliberate path fix; the 78-test dispatcher suite passes with
  it. A future packaging cleanup (proper editable install) could remove the need;
  tracked as a candidate follow-on.
- **Rollback:** `git revert c990cb5d` restores all 5 surfaces + removes the test
  files and the hunk; bridge files remain (append-only).

## Applicability Preflight

To be populated post-INDEX-entry. Expected `preflight_passed: true`,
`missing_required_specs: []`. Proposal text includes the cross-cutting trigger
vocabulary (Specification Links / verification / spec-to-test / artifact /
deliberation / MemBase / work item / backlog / owner decision / requirement /
ADR / DCL / verified / retired / superseded).

## Clause Applicability

To be populated post-INDEX-entry. Expected exit 0, no blocking gaps:
`CLAUSE-IN-ROOT` (target_paths in-root), `CLAUSE-INDEX-IS-CANONICAL` (INDEX
self-check above), `CLAUSE-CONCRETE-LINKS` (concrete Specification Links),
`CLAUSE-SPEC-TO-TEST-MAPPING` (Spec-Derived Verification Plan above).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
