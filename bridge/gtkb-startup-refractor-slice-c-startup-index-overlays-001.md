NEW

# GTKB-STARTUP-REFRACTOR-001 Slice C — Role-Neutral Startup Index + Role Overlays

bridge_kind: implementation_proposal
Document: gtkb-startup-refractor-slice-c-startup-index-overlays
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC

author_identity: Claude Code Prime Builder (PAUTH-authorized implementation)
author_harness_id: B
author_session_context_id: 2026-06-03-gtkb-startup-refractor-slice-c
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-GTKB-STARTUP-REFRACTOR-001-SLICES-A-E-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-STARTUP-REFRACTOR-001
Work Item: WI-4271

target_paths: ["config/agent-control/SESSION-STARTUP-INDEX.md", "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md", "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md", "CLAUDE.md", "AGENTS.md", "platform_tests/scripts/test_session_startup_index.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Slice C of GTKB-STARTUP-REFRACTOR-001 (WI-4271), covering advisory findings **F4**
(startup content duplicated across too many loaded documents) and **F7** (Prime
Builder lacks a compact startup load list comparable to Loyal Opposition's). It
collapses the duplicated startup procedure into a short role-neutral index plus
two compact role overlays, then repoints the protected narrative to the index
instead of restating the procedure:

1. Create `config/agent-control/SESSION-STARTUP-INDEX.md` — the role-neutral
   canonical startup load order (role record → role overlay → canonical
   terminology → bridge index → dashboard/backlog summary → selected task),
   referencing the Slice A `SESSION-STARTUP-CONTROL-MAP.md` for the surface
   inventory.
2. Create `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md` and
   `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md` — compact
   role-specific overlays.
3. Repoint `CLAUDE.md` and `AGENTS.md` to cite the index + overlays instead of
   restating the full startup procedure (reduces duplication and token load;
   for `CLAUDE.md` this trends LINE COUNT DOWN, helping the GOV-01 ≤300-line cap).

Both `CLAUDE.md` and `AGENTS.md` are protected narrative artifacts; each edit
lands through its own formal narrative-artifact-approval packet (PAUTH
`narrative` mutation class). The index + overlays are additive docs under
`config/agent-control/`. This slice depends on the Slice A inventory (VERIFIED).

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` — governs the startup load order this index codifies. PAUTH-linked.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — de-duplication directly serves the startup token-budget constraint. PAUTH-linked.
- `GOV-ARTIFACT-APPROVAL-001` — governs the protected `CLAUDE.md` + `AGENTS.md` narrative edits (per-artifact packets).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol for this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-linkage compliance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + WI + PAUTH linkage.
- `GOV-STANDING-BACKLOG-001` — WI-4271 linkage.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; all target paths in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory); `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory); `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).

## Prior Deliberations

- `DELIB-20260622` — owner PAUTH decision (covers WI-4271).
- `bridge/gtkb-startup-refractor-scoping-002.md` — scoping GO defining Slice C.
- `bridge/gtkb-startup-refractor-slice-a-startup-control-inventory-004.md` — Slice A VERIFIED; the index references the control-map this slice depends on.
- `DELIB-2078` — init-keyword startup-disclosure relay; the repoint must preserve the disclosure-relay contract.

## Owner Decisions / Input

- Implementation authority: project PAUTH (active), owner decision `DELIB-20260622`,
  allowed mutation classes include `documentation`, `narrative`, `test`. No
  embedded owner choice for this slice (the protected-narrative edits are gated
  per-artifact by the narrative-approval packet path, not an owner content
  decision here).

## Requirement Sufficiency

**Existing requirements sufficient.** Governing requirements are advisory F4/F7,
`GOV-SESSION-SELF-INITIALIZATION-001`, and `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`.
The index/overlays consolidate existing content; no new behavior contract, so no
new specification is required.

## Spec-Derived Verification Plan

| Specification / Finding | Spec-to-test mapping | Command | Expected |
|---|---|---|---|
| F4/F7 / `GOV-SESSION-SELF-INITIALIZATION-001` | `test_session_startup_index.py` asserts the index exists, declares the canonical load order, and that CLAUDE.md + AGENTS.md reference the index/overlays | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_startup_index.py -q --no-header -p no:cacheprovider` | PASS |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | same test asserts both role overlays exist and are bounded (compact); de-duplication check | (same pytest) | PASS |
| GOV-01 (CLAUDE.md cap) | assert CLAUDE.md line count remains ≤300 after the repoint | (same pytest) | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | lint + format on the new test | `ruff check` / `ruff format --check` on changed Python | clean |

The implementation report will carry observed pytest + ruff results and the
`CLAUDE.md` + `AGENTS.md` narrative-approval packet references.

## Risk / Rollback

Moderate: two protected-narrative repoints (packet-gated, must preserve the
init-keyword disclosure-relay contract and the GOV-01 cap) plus three additive
docs and a test. No control-flow change. Rollback is a single-commit revert; the
narrative packets make each protected edit independently auditable.

## Recommended Commit Type

`refactor` — restructures startup documentation (consolidate to index + overlays,
repoint narrative) without changing runtime behavior; net effect is reduced
duplication, not a new capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
