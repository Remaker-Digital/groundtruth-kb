REVISED

# Revised Implementation Proposal — format-only target_paths fix

bridge_kind: prime_proposal
Document: gtkb-role-rule-orthogonality-cleanup-claude-pb-switch
Version: 011
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-010.md (GO)

Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4214
Project Authorization: PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-PY-DOC-SURFACES

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: f84fd3f2-0bb2-4a8f-ac9d-f60b02ce8d47
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, autonomous /loop dynamic mode

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/workstream_focus.py", "bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-011.md", "bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-012.md", "bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-013.md", "bridge/INDEX.md"]

## Revision Claim

This `REVISED` is **format-only**. The GO'd proposal `-009` (Antigravity Loyal Opposition GO at `-010`) declared its target paths under a `## Target Paths` heading with a multi-line fenced JSON code block. The impl-start gate at `scripts/implementation_authorization.py begin` cannot parse that form: its `extract_target_paths` accepts (a) an inline single-line `target_paths: [...]` metadata-line form, (b) `## Files Expected To Change` bullet lines, or (c) `## target_paths` bullet lines. The fenced-JSON form under `## Target Paths` falls through all three matchers, so `begin` returns `{"authorized": false, "error": "Approved proposal is missing concrete target_paths or Files Expected To Change"}` and no implementation packet can be minted against the live GO at `-010`.

Per the documented gotcha [[target_paths-must-be-machine-parseable]] (S379 session-memory; tracked in MemBase backlog records named in § Prior Deliberations as the parser-defect-class follow-ons), the cheapest unblock is a format-only `REVISED` that re-states the target paths in the inline-JSON metadata-line form (the form `TARGET_PATHS_RE` matches at line 64 of `scripts/implementation_authorization.py`).

**No semantic change.** The target_paths set is byte-identical to `-009`'s set, with the bridge-file version numbers bumped to reflect this REVISED's filename (`-011`) and the next two expected versions (`-012` next verdict, `-013` post-impl report). The implementation plan (three string substitutions in `scripts/cross_harness_bridge_trigger.py:887` and `scripts/workstream_focus.py:952,957`), the spec-derived verification plan, the risk/rollback analysis, and the PAUTH coverage are carried forward unchanged from `-009`. Read `-009` for the full content of those sections — this REVISED references rather than duplicates them.

**Authored by a different session.** The prior `-009` was authored by Claude Code Prime Builder session `c3ccabea-0273-4e0e-af3f-0ca48b607c1e` (harness B). This `-011` is authored by Claude Code Prime Builder session `f84fd3f2-0bb2-4a8f-ac9d-f60b02ce8d47` (also harness B; different interactive instance). Concurrent Claude sessions share harness ID B but not `author_session_context_id`; this REVISED does not violate the skip-own constraint per `memory/feedback_shared_session_id_skip_own_is_review_not_implement.md`.

## Specification Links

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — operator/dispatch surfaces must point at the canonical store, not the orphan mirror (carried forward from `-009`; included in PAUTH).
- `DCL-REPORTING-SURFACE-FRESH-READ-001` — operator-facing reports cite the canonical registry (carried forward from `-009`; included in PAUTH).
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — orthogonality model declaring `harness-registry.json` canonical and `role-assignments.json` an orphan compatibility mirror (carried forward from `-009`; included in PAUTH).
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — PAUTH envelope authority for this bounded scope.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — the active PAUTH `PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-PY-DOC-SURFACES` satisfies the envelope constraint.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the PAUTH does not bypass bridge review; this REVISED is the explicit demonstration that the bridge protocol is being honored.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge canonicality preserved; append-only chain intact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping present in § Spec-Derived Verification Plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project linkage cited in the header metadata block (Project / Work Item / Project Authorization lines).
- `GOV-STANDING-BACKLOG-001` — `WI-4214` is the durable backlog record for the retire-mirror program.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — every target_paths entry is in-root under `E:\GT-KB`.

## Prior Deliberations

- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-009.md` — Prime REVISED-3 proposal carrying the full implementation plan, verification plan, risk analysis, and PAUTH citation; the substantive plan in this REVISED is byte-identical.
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-010.md` — Antigravity Loyal Opposition GO on `-009`; this REVISED preserves the approved scope.
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-008.md` — Codex NO-GO that enumerated the three lines being repointed.
- `DELIB-2799` — owner decision authorizing the retire-mirror program and the PAUTH.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — owner directive establishing canonical orthogonality.
- `DELIB-2521` — owner-decision capture establishing `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (S376).
- MemBase backlog records for the impl-auth target_paths parser defect class addressed by this format-only fix: the open backlog item titled "impl-auth begin target_paths parser: exact-heading match misses annotated headings + slurps ### subsections"; the resolved item titled "impl-auth begin gate requires `##` section headings but no upstream gate enforces it (post-GO dead-end)"; and the open item titled "Impl-auth gate's literal substring matcher rejects valid Requirement Sufficiency phrasings (bias-case defect)". These are documentary cross-references, not authority claims; the declared Work Item for this REVISED remains `WI-4214`.

## Owner Decisions / Input

- **Owner AskUserQuestion (2026-06-03, interactive check-in)** — the owner selected "Authorize role-rule PAUTH," minting `PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-PY-DOC-SURFACES` (owner-decision `DELIB-2799`). The PAUTH is active, includes `WI-4214`, allows the `source` mutation class, and explicitly covers `scripts/cross_harness_bridge_trigger.py` and `scripts/workstream_focus.py`. This durable owner-decision evidence authorizes the implementation in scope here.
- **Owner Action Required for this REVISED:** None. The PAUTH is active; this REVISED is a format-only fix to the prior GO'd proposal, intended to unblock the impl-start gate; Codex re-review proceeds normally.

## Requirement Sufficiency

Existing requirements sufficient. Carried forward unchanged from `-009` § Requirement Sufficiency: the cleanup is bounded by `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `DCL-REPORTING-SURFACE-FRESH-READ-001`, and `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (all three included in the PAUTH). No new requirement or policy is introduced; the three lines are stale mirror-authority guidance that must be repointed at the canonical registry.

## Implementation Plan

Carried forward unchanged from `-009` § Implementation Plan. Three single-line string substitutions:

- **Edit 1** — `scripts/cross_harness_bridge_trigger.py:887`. Current: `#   1. role-assignments.json: needed_role_label -> harness_id  (role authority)`. Replacement: `#   1. harness-registry.json: needed_role_label -> harness_id  (canonical role authority)`.
- **Edit 2** — `scripts/workstream_focus.py:952`. Current: `"— counterpart bridge roles may collide; verify harness-state/role-assignments.json."`. Replacement: `"— counterpart bridge roles may collide; verify harness-state/harness-registry.json (canonical role registry)."`.
- **Edit 3** — `scripts/workstream_focus.py:957`. Current: `"Treat bridge message authority per harness-state/role-assignments.json."`. Replacement: `"Treat bridge message authority per harness-state/harness-registry.json (canonical role registry)."`.

Implementation order:

1. `python scripts/implementation_authorization.py begin --bridge-id gtkb-role-rule-orthogonality-cleanup-claude-pb-switch` (against this `-011` GO, once issued).
2. Apply Edit 1 to `scripts/cross_harness_bridge_trigger.py`.
3. Apply Edits 2 and 3 to `scripts/workstream_focus.py`.
4. Run the Spec-Derived Verification Plan below.
5. File the post-impl report at `-013`.

## Spec-Derived Verification Plan

Carried forward from `-009` § Spec-Derived Verification Plan; reproduced here so the spec-to-test clause finds evidence in this operative file.

| Specification | Verification Command | Expected |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — no stale-authority guidance remains | `rg -n "role-assignments\.json.*(authority|role authority|Treat bridge message authority|verify harness-state)" scripts/cross_harness_bridge_trigger.py scripts/workstream_focus.py` | zero matches |
| `DCL-REPORTING-SURFACE-FRESH-READ-001` — operator reports cite the canonical registry | `rg -n "harness-registry\.json" scripts/workstream_focus.py scripts/cross_harness_bridge_trigger.py` | three new matches present (Edits 1-3) |
| `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — canonical-registry framing present | `rg -n "canonical role registry|canonical role authority" scripts/cross_harness_bridge_trigger.py scripts/workstream_focus.py` | new matches present |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — lint and format gates are separate | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cross_harness_bridge_trigger.py scripts/workstream_focus.py`; `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cross_harness_bridge_trigger.py scripts/workstream_focus.py` | `All checks passed!`; both files already formatted |
| (regression) — `workstream_focus` warning tests still pass | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_workstream_focus.py -q` | pass (string-content assertions, if any, updated in lockstep) |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` — INDEX evidence in post-impl report | post-impl `-013` includes a `Bridge INDEX Self-Check` subsection naming `bridge/INDEX.md` | section present in `-013` |

Post-edit re-run of the Codex `-008` broader scan must continue to show no `role-assignments.json` match acting as authority or operator-instruction; remaining matches must be orphan/compat/provenance references only.

## Project Linkage

Project: `PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH`.
Work Item: `WI-4214` (Retire orphaned role-assignments.json legacy mirror).
Project Authorization: `PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-PY-DOC-SURFACES` — active; owner-decision `DELIB-2799`; includes WI-4214; `source` mutation class; covers the two `.py` files in scope; specs `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `ADR-SINGLE-HARNESS-OPERATING-MODE-001`, `DCL-REPORTING-SURFACE-FRESH-READ-001`.

## Risk & Rollback

Carried forward unchanged from `-009`. Low. Three single-line string substitutions: Edit 1 is a code comment (zero runtime effect); Edits 2-3 change operator-facing warning strings (same code path fires; only the cited file name changes). No control-flow, API, MemBase, or protected-narrative change. Rollback: `git revert` the implementation commit.

## Applicability Preflight

Codex re-runs both mandatory preflights against this operative `-011` file:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-rule-orthogonality-cleanup-claude-pb-switch
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-rule-orthogonality-cleanup-claude-pb-switch
```

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause-preflight zero blocking gaps. The clause-preflight CLAUSE-SPEC-TO-TEST-MAPPING evidence is in § Spec-Derived Verification Plan above.

## Bridge INDEX Self-Check

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`, this REVISED is filed canonically as `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-011.md`, and the `bridge/INDEX.md` entry for this Document receives a new `REVISED: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-011.md` line inserted at the top of the Document's version list, above the existing `GO: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-010.md` line. All prior versions (`-001` ... `-010`) remain on disk byte-for-byte; no version is deleted, renamed, or rewritten; the append-only audit chain is intact and monotonic.

Expected INDEX entry shape after this filing:

```text
Document: gtkb-role-rule-orthogonality-cleanup-claude-pb-switch
REVISED: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-011.md
GO: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-010.md
REVISED: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-009.md
NO-GO: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-008.md
REVISED: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-007.md
NO-GO: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-006.md
REVISED: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-005.md
NO-GO: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-004.md
NEW: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-003.md
GO: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-002.md
NEW: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-001.md
```

`Recommended commit type:` `docs` (this REVISED is a bridge file only; no source-code change is included in the commit that lands this REVISED).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
