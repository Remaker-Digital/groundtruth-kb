REVISED

bridge_kind: prime_proposal
Document: gtkb-role-rule-orthogonality-cleanup-claude-pb-switch
Version: 009
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-03 UTC
Responds to: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-008.md (NO-GO)

Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4214
Project Authorization: PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-PY-DOC-SURFACES

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: c3ccabea-0273-4e0e-af3f-0ca48b607c1e
author_model: Claude Opus 4.8 (1M context)
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

# Revised Implementation Proposal — Residual stale-mirror-authority cleanup in dispatch/operator surfaces

## Revision Claim

This `REVISED` converts the post-implementation-report loop
(`-003` → `-004` NO-GO → `-005` → `-006` NO-GO → `-007` → `-008` NO-GO) into a
**scope-expansion implementation proposal** that adds the two Python source
files Codex `-008` FINDING-F1 named as still carrying
`role-assignments.json`-as-authority guidance:

- `scripts/cross_harness_bridge_trigger.py` (authority-chain comment, line 887)
- `scripts/workstream_focus.py` (two operator-facing warning strings, lines 952 and 957)

The original GO at `-002` scoped target_paths to the rule files
(`.claude/rules/operating-role.md`, `.claude/rules/canonical-terminology.md`)
plus registry/mirror state. The impl-start gate correctly blocked Prime from
editing these two `.py` files against `-002`. Codex `-008`'s NO-GO is therefore
a **scope-expansion request** requiring a fresh GO authorizing the expanded
target_paths.

**Work-item / authorization correction.** Earlier framing in this session
tentatively cited `WI-3509`; that work item is `resolved` and scoped to the
status-aware dispatch resolver, not doc-surface cleanup. The accurate home is
`WI-4214` ("Retire orphaned role-assignments.json legacy mirror"), whose own
description enumerates this exact doc-drift defect class (code/docs still
naming `role-assignments.json` as the single source of truth). This proposal is
authorized by the dedicated envelope
`PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-PY-DOC-SURFACES`
(owner decision `DELIB-2799`, re-confirmed by owner AskUserQuestion on
2026-06-03), which includes `WI-4214` and allows the `source` mutation class for
exactly these two `.py` files.

On Codex GO of `-009`, Prime mints an implementation-authorization packet from
the expanded target_paths and applies the three edits below. Next bridge round:
`-010` (Codex GO/NO-GO) → `-011` (Prime post-impl report) → `-012` (VERIFIED).

## Specification Links

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — operator/dispatch surfaces must point at the canonical store, not the orphan mirror (core motivation; included in the PAUTH).
- `DCL-REPORTING-SURFACE-FRESH-READ-001` — operator-facing reports (the workstream_focus warning strings) must cite the canonical registry (included in the PAUTH).
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — orthogonality model declaring `harness-registry.json` canonical and `role-assignments.json` an orphan compatibility mirror (included in the PAUTH).
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — PAUTH envelope authority for this bounded scope.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — the PAUTH satisfies the envelope constraint.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the PAUTH does not bypass bridge review; this REVISED is the explicit demonstration.
- `GOV-ARTIFACT-APPROVAL-001`; `PB-ARTIFACT-APPROVAL-001`; `DCL-ARTIFACT-APPROVAL-HOOK-001` — no protected-narrative or canonical-artifact mutation in this slice; only source-code comments and string literals.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge filing canonicality.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the spec-derived verification plan below maps each spec to a concrete check.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project linkage cited in the header metadata block.
- `GOV-STANDING-BACKLOG-001` — WI-4214 is the durable backlog record for the retire-mirror program.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target_paths are in-root under `E:\GT-KB`.

## Prior Deliberations

- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-001.md` — original NEW proposal; § Project Linkage already noted "downstream role-assignment language to update in later slices."
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-002.md` — Antigravity LO GO on the original rule-file target_paths.
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-006.md` — Codex NO-GO requiring a broader scan covering dispatcher/hook code.
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-007.md` — Prime REVISED post-impl report; closed `cross_harness_bridge_trigger.py:964` but missed `:887` and the `workstream_focus.py:952/957` warning strings.
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-008.md` — Codex NO-GO FINDING-F1 enumerating the three lines this `-009` addresses.
- `DELIB-2799` — owner decision authorizing the WI-4214 retire-role-assignments-mirror program (the PAUTH's owner-decision basis).
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — owner directive establishing the canonical orthogonality model.
- `DELIB-2521` — owner-decision capture establishing `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (S376), under which the residual mirror-authority guidance is a freshness defect.
- WI-4214 backlog record — enumerates the doc-drift defect class these edits close.

## Owner Decisions / Input

- **Owner AskUserQuestion (2026-06-03, interactive check-in)** — the owner selected "Authorize role-rule PAUTH," authorizing a scope-expansion project authorization covering `scripts/cross_harness_bridge_trigger.py` and `scripts/workstream_focus.py` so the residual stale-mirror-authority cleanup can land. This is the durable owner-decision evidence for this REVISED. The authorization was minted as `PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-PY-DOC-SURFACES` (owner-decision `DELIB-2799`; source mutation class; includes WI-4214).
- **Owner Action Required for this REVISED:** None. The PAUTH is active; Codex review proceeds normally.

## Requirement Sufficiency

Existing requirements sufficient. The cleanup is bounded by
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `DCL-REPORTING-SURFACE-FRESH-READ-001`, and
`ADR-SINGLE-HARNESS-OPERATING-MODE-001` (all included in the PAUTH). No new
requirement or policy is introduced; the three lines are stale mirror-authority
guidance that must be repointed at the canonical registry.

## Target Paths

```json
[
  "scripts/cross_harness_bridge_trigger.py",
  "scripts/workstream_focus.py",
  "bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-009.md",
  "bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-010.md",
  "bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-011.md",
  "bridge/INDEX.md"
]
```

No protected-narrative `.md` is touched in this slice; no MemBase mutation is in
scope. The PAUTH's `source` mutation class covers the two `.py` files.

## Implementation Plan

### Edit 1 — `scripts/cross_harness_bridge_trigger.py:887`

Current (line 887, within the authority-chain comment block at 883–895):

```python
#   1. role-assignments.json: needed_role_label -> harness_id  (role authority)
```

Replacement:

```python
#   1. harness-registry.json: needed_role_label -> harness_id  (canonical role authority)
```

### Edit 2 — `scripts/workstream_focus.py:952`

Current:

```python
                    "— counterpart bridge roles may collide; verify harness-state/role-assignments.json."
```

Replacement:

```python
                    "— counterpart bridge roles may collide; verify harness-state/harness-registry.json (canonical role registry)."
```

### Edit 3 — `scripts/workstream_focus.py:957`

Current:

```python
                    "Treat bridge message authority per harness-state/role-assignments.json."
```

Replacement:

```python
                    "Treat bridge message authority per harness-state/harness-registry.json (canonical role registry)."
```

### Implementation order

1. `python scripts/implementation_authorization.py begin --bridge-id gtkb-role-rule-orthogonality-cleanup-claude-pb-switch` (against this `-009` GO once issued).
2. Apply Edit 1 to `scripts/cross_harness_bridge_trigger.py`.
3. Apply Edits 2 and 3 to `scripts/workstream_focus.py`.
4. Run the spec-derived verification plan below.
5. File the post-impl report at `-011`.

## Spec-Derived Verification Plan

| Specification | Verification Command | Expected |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — no stale-authority guidance remains | `rg -n "role-assignments\.json.*(authority\|role authority\|Treat bridge message authority\|verify harness-state)" scripts/cross_harness_bridge_trigger.py scripts/workstream_focus.py` | zero matches |
| `DCL-REPORTING-SURFACE-FRESH-READ-001` — operator reports cite canonical registry | `rg -n "harness-registry\.json" scripts/workstream_focus.py scripts/cross_harness_bridge_trigger.py` | three new matches (Edits 1–3) |
| `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — canonical-registry framing present | `rg -n "canonical role registry\|canonical role authority" scripts/cross_harness_bridge_trigger.py scripts/workstream_focus.py` | new matches present |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — lint/format gates pass | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cross_harness_bridge_trigger.py scripts/workstream_focus.py`; `... -m ruff format --check ...` | `All checks passed!`; both files already formatted |
| (regression) — workstream_focus warning tests still pass | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_workstream_focus.py -q` | pass (string-content assertions, if any, updated in lockstep) |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` — INDEX evidence in report | post-impl `-011` includes a `Bridge INDEX Self-Check` subsection naming `bridge/INDEX.md` | section present in `-011` |

Post-edit re-run of the Codex `-008` broader scan must show no `role-assignments.json` match acting as authority/operator-instruction; remaining matches are orphan/compat/provenance references only.

## Project Linkage

Project: `PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH`.
Work Item: `WI-4214` (Retire orphaned role-assignments.json legacy mirror — the accurate home for role-assignments.json reference cleanup).
Project Authorization: `PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-PY-DOC-SURFACES` — active; owner-decision `DELIB-2799`; includes WI-4214; `source` mutation class; specs `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `ADR-SINGLE-HARNESS-OPERATING-MODE-001`, `DCL-REPORTING-SURFACE-FRESH-READ-001`.

## Risk & Rollback

Low. Three single-line string substitutions: Edit 1 is a code comment (zero
runtime effect); Edits 2–3 change operator-facing warning strings (same code
path fires; only the cited file name changes). No control-flow, API, MemBase, or
protected-narrative change. Rollback: `git revert` the implementation commit.

## Applicability Preflight

Codex re-runs both mandatory preflights against this operative `-009` file:

```
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-rule-orthogonality-cleanup-claude-pb-switch
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-rule-orthogonality-cleanup-claude-pb-switch
```

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause-preflight zero blocking gaps.

## Bridge INDEX Self-Check

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`, this REVISED is
filed canonically under `bridge/` as
`bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-009.md`, and the
`bridge/INDEX.md` entry for this Document receives a new
`REVISED: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-009.md`
line inserted at the top of the Document's version list, above the existing
`NO-GO: ...-008.md` line. All prior versions (`-001` … `-008`) remain on disk
byte-for-byte; no version is deleted, renamed, or rewritten; the append-only
audit chain is intact and monotonic.

Expected INDEX entry shape after this filing:

```
Document: gtkb-role-rule-orthogonality-cleanup-claude-pb-switch
REVISED: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-009.md
NO-GO: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-008.md
REVISED: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-007.md
NO-GO: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-006.md
NEW: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-005.md
GO: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-004.md
REVISED: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-003.md
GO: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-002.md
NEW: bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-001.md
```

`Recommended commit type:` `refactor` (string repointings; no behavior change). The bridge file itself is `docs`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
