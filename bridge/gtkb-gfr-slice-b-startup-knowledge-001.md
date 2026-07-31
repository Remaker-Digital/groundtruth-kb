NEW
::init gtkb lo
::open build

# Implementation Proposal — GFR Slice B: Startup & knowledge surfacing

bridge_kind: prime_proposal
Document: gtkb-gfr-slice-b-startup-knowledge
Version: 001
Date: 2026-07-21 UTC
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-07-21T08-15-00Z
author_model: GLM-5.2
author_model_version: GLM-5.2-2026
author_model_configuration: standard

Project Authorization: PAUTH-GFR-PROGRAM-20260721
Project: PROJECT-GTKB-GOVERNANCE-FRICTION-REDUCTION
Work Item: WI-5643

target_paths: ["config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md", "config/agent-control/SESSION-STARTUP-INDEX.md", "config/agent-control/activity-disposition-profiles.toml", ".claude/rules/canonical-terminology.md", ".claude/skills/gtkb-work-item/SKILL.md", ".claude/skills/gtkb-bridge/SKILL.md"]

Implementation proposal for governance friction reduction — Slice B (startup & knowledge surfacing).

## Claim

Slice B of the Governance Friction Reduction program (per GO'd advisory `bridge/gtkb-governance-friction-reduction-002.md`) reduces avoidable tool-call cost by surfacing knowledge at the point of need rather than requiring agents to discover it by failing first. The advisory documented that the dominant session cost was staggered, reactive discovery of rules and knowledge that exist in the codebase but are not surfaced at the point of need.

This slice implements six findings from the advisory:

1. **Finding 1.1 — Session-envelope provenance pre-flight line**: Add a one-line pre-flight to the Prime Builder startup overlay and SESSION-STARTUP-INDEX that says: *"Worker-role provenance requires an open session envelope; open one with `python -m groundtruth_kb session envelope open --harness-name <name> --harness-id <id> --init-keyword "::init gtkb pb" --subject gtkb --role prime-builder` before any KB-write or bridge claim."* This prevents the 10+ tool-call provenance-discovery loop documented in the advisory.

2. **Finding 1.3 — Auto-load `gtkb-work-item` at `::open build`**: The `gtkb-work-item` skill already exists with an `argument-hint` listing all required flags for `backlog add-work-item`, but the builder in the advisory session had not loaded it. Add `gtkb-work-item` to the build activity's `skills` list in `activity-disposition-profiles.toml` so it loads automatically when the build envelope opens.

3. **Finding 1.6 — Per-harness skill-adapter generator discovery**: Add a note to the `gtkb-bridge` skill (or a companion reference) listing which harnesses have skill-adapter generators and which do not, so a builder does not have to discover this by failing parity checks. This is a documentation/reference addition, not a new generator.

4. **Finding 3.1 — Session-ID vs worker-role provenance terminology**: Add a glossary entry to `canonical-terminology.md` binding "worker-role provenance" to "the validated role attestation an open session envelope provides" — clarifying that provenance is a property of an open session envelope, not an env var. This addresses the central procedural error of the advisory session.

5. **Finding 3.2 — `unclassified` mutation class**: Add a glossary entry for the `unclassified` mutation class, explaining that `target_paths` matching no classifier rule are treated as `unclassified` and may cause `begin` to fail if they fall into a protected scope. This prevents the trial-and-error glob refinement documented in Finding 2.4.

6. **Finding 3.3 — `Responds to` chain semantics**: Add a one-line note to the `gtkb-bridge` skill: *"`Responds to` for `begin` must resolve to the GO document, not a NO-GO or VERIFIED."* This prevents the `Responds to` pointing at a NO-GO rejection documented in the advisory.

## Requirement Sufficiency

Existing requirements are sufficient for this slice. The advisory's findings are all documentation/terminology/surfacing changes — no new specifications or requirement changes are needed. The governing specifications cited below provide the authority and linkage requirements; this slice implements within their scope.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:
- `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md` ✅
- `config/agent-control/SESSION-STARTUP-INDEX.md` ✅
- `config/agent-control/activity-disposition-profiles.toml` ✅ (added for auto-load)
- `.claude/rules/canonical-terminology.md` ✅
- `.claude/skills/gtkb-work-item/SKILL.md` ✅ (verify name reference)
- `.claude/skills/gtkb-bridge/SKILL.md` ✅

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant governing specifications; implementation does not proceed without LO GO.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — defines who may author which status tokens; this proposal is authored by Prime Builder (prime-builder/goose).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance is the default interpretation stance; these findings preserve durable artifacts (glossary entries, startup overlay lines).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification will require spec-to-test mapping; the linked test (TEST-11688) verifies that all existing tests pass and ruff is clean after the changes.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal includes the three mandatory header lines (Project Authorization, Project, Work Item).
- `SPEC-AUQ-POLICY-ENGINE-001` — owner decision DELIB-202667078 provides the AUQ evidence for this program.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are within the GT-KB root boundary.
- `GOV-STANDING-BACKLOG-001` — the GFR program was added to the standing backlog via WIs WI-5643 through WI-5646.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — skill adapter parity is relevant to the auto-load addition (Finding 1.3).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — these changes convert informal session-discovered knowledge into durable records.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the glossary entries and startup overlay lines are durable artifacts triggered by the advisory's threshold crossing.

## Prior Deliberations

- `DELIB-202667078` — Owner approval: Governance Friction Reduction program. Owner approved proceeding with the 4-slice program per GO'd advisory `gtkb-governance-friction-reduction-002`.
- `DELIB-20263490` — Loyal Opposition Progress & Verification Report — Terminology & Bridge Reconciliation. Relevant to terminology additions (Findings 3.1-3.3).
- `DELIB-202665594` — Loyal Opposition Review — WI-4840 Advisory Disposition Skill Scaffold. Relevant to skill auto-load pattern (Finding 1.3).
- `DELIB-20265747` — Loyal Opposition GO verdict: WI-4716 bridge-propose semantic-search doc sync. Relevant to bridge skill documentation (Finding 3.3).


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- `DELIB-202667078` (AUQ GFR-PAUTH-001) — Owner answer: "1 - Yes, proceed". Authorizes creating the GFR project, 4 per-slice WIs, PAUTH, and filing per-slice implementation proposals.
- `PAUTH-GFR-PROGRAM-20260721` — Active project authorization covering WI-5643 through WI-5646 with source/test/config mutation classes.

## Cross-Harness Disposition

This proposal touches `.claude/skills/gtkb-bridge/SKILL.md` and `.claude/skills/gtkb-work-item/SKILL.md`, which are harness-surface files.

| Harness | Surface | Parity Status | Disposition |
|---|---|---|---|
| Claude Code | `.claude/skills/` (canonical source) | N/A — canonical | Changes made here are the canonical source. |
| Codex | `.codex/skills/` (generated adapter) | **Requires adapter regeneration** | After implementation, run `python scripts/generate_codex_skill_adapters.py --update-registry` to regenerate the Codex adapter from the canonical source. The adapter carries a `<!-- GTKB-CODEX-SKILL-ADAPTER -->` marker. |
| Antigravity | No skill adapter | N/A — no adapter surface | No action required; Antigravity uses inline loading. |
| Cursor | No skill adapter | N/A — no adapter surface | No action required; Cursor uses Claude-compatible loading. |
| Goose | No skill adapter | N/A — no adapter surface | No action required; Goose uses inline loading. |
| OpenRouter | No skill adapter | N/A — no adapter surface | No action required; OpenRouter uses inline loading. |

**No typed waiver required.** The only downstream action is regenerating the Codex skill adapter after implementation, which is the standard post-edit step per `ADR-CROSS-HARNESS-PARITY-001`.

## Proposed Scope

### Finding 1.1 — Envelope-open pre-flight line

Add to `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md` (Phase B, after step 1):

> **Pre-flight (before any KB-write or bridge claim):** Worker-role provenance requires an open session envelope. Open one with:
> `python -m groundtruth_kb session envelope open --harness-name <name> --harness-id <id> --init-keyword "::init gtkb pb" --subject gtkb --role prime-builder`
> before any `gt backlog`, `gt bridge`, or `implementation_authorization.py begin` command.

Add a corresponding line to `config/agent-control/SESSION-STARTUP-INDEX.md` Phase B step 1.5 (between identity resolution and canonical terminology load).

### Finding 1.3 — Auto-load `gtkb-work-item` at `::open build`

Add `"gtkb-work-item"` to the `skills` list for the `build` activity in `config/agent-control/activity-disposition-profiles.toml`:

```toml
[activities.build]
skills = [
    "bridge",
    "bridge-propose",
    "verify",
    "kb-work-item",       # ← keep for backward compat
    "gtkb-work-item",     # ← add (canonical name post-rename)
    "kb-spec",
    "advisory-intake",
]
```

Also add `target_paths` entry for `config/agent-control/activity-disposition-profiles.toml`.

### Finding 1.6 — Per-harness skill-adapter generator discovery

Add a reference note to `.claude/skills/gtkb-bridge/SKILL.md` under the "Cross-harness implementation notes" section:

> **Per-harness generator inventory:**
> - Claude Code: `scripts/generate_codex_skill_adapters.py` (generates `.codex/skills/`)
> - Codex: generated by the above; no separate generator
> - Antigravity, Cursor, Goose, OpenRouter: **no generator** — these harnesses use inline skill loading or Claude-compatible adapters
> 
> When adding or renaming skills, run `python scripts/generate_codex_skill_adapters.py --update-registry` after editing the canonical at `.claude/skills/`.

### Finding 3.1 — Session-ID vs worker-role provenance glossary entry

Add to `.claude/rules/canonical-terminology.md`:

> ### Worker-role provenance
> **Source:** `scripts/_kb_attribution.py`; `groundtruth-kb/src/groundtruth_kb/session/envelope.py` L424-464; WI-5010; DELIB-202667078.
> 
> Worker-role provenance is the validated role attestation that an **open session envelope** provides. It is not an environment variable, a harness registry role, or a marker file. The `changed_by` field on MemBase writes (e.g., `backlog add-work-item`) resolves worker-role provenance by reading the open session envelope's `worker_role_provenance` block, which is populated at envelope-open time from the init keyword's resolved role.
> 
> An env var like `GTKB_SESSION_ID` tells the CLI *which* session envelope to read, but it does not *provide* provenance — only the open envelope document does. If `resolve_changed_by` fails with "current session id is missing" or "does not match," the fix is to open a session envelope, not to set more env vars.

### Finding 3.2 — `unclassified` mutation class glossary entry

Add to `.claude/rules/canonical-terminology.md`:

> ### Unclassified mutation class
> **Source:** `scripts/bridge_applicability_preflight.py` L64 (`TARGET_PATH_RE`); `scripts/implementation_authorization.py` target-path classification.
> 
> When a `target_paths` entry matches no classifier rule in `bridge_applicability_preflight.py`, it is classified as `unclassified`. This means the path is not recognized as a protected mutation target. Paths classified as `unclassified` may cause `implementation_authorization.py begin` to fail if they fall into a protected scope that the classifier did not match. To resolve, refine the glob pattern to match a known classified sub-pattern (e.g., `.../**/*.md` → `governance_evidence` rather than `.../**`).

### Finding 3.3 — `Responds to` chain semantics note

Add to `.claude/skills/gtkb-bridge/SKILL.md` under the "Revise" operation:

> **`Responds to` for `begin`:** The `Responds to` field must resolve to the **GO** document, not a NO-GO or VERIFIED. A REVISED proposal responds to the prior NO-GO, but the `begin` validator traces the chain to find a GO. If the chain points at a NO-GO or VERIFIED, `begin` will reject with a provenance error.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "documentation and configuration surfacing changes",
  "provenance": "GO'd advisory gtkb-governance-friction-reduction-002; owner decision DELIB-202667078",
  "canonical_authority": "canonical-terminology.md; PRIME-BUILDER-STARTUP-OVERLAY.md; SESSION-STARTUP-INDEX.md",
  "primary_route": "additive: new glossary entries, new startup overlay lines, new skill auto-load entry",
  "before_behavior": "agents discover provenance, terminology, and skill availability by failing first",
  "after_behavior": "agents find provenance, terminology, and skill availability in startup/skill surfaces at the point of need",
  "self_descriptive_naming": "glossary entries use canonical heading format; startup overlay uses existing pre-flight pattern",
  "obsolete_guidance_disposition": "no existing guidance is superseded; all changes are additive",
  "history_preservation": "no existing artifacts are deleted or rewritten",
  "baseline": "existing tests + ruff check + ruff format --check",
  "expected_result": "all tests pass, ruff clean, new glossary entries present, startup overlay updated, skill auto-loads",
  "rollback": "revert the commit; no data migration or state change to roll back",
  "hard_invariants": "GOV-12/GOV-13 chain intact; bridge protocol unchanged; no gate weakened",
  "fail_closed_conditions": "missing glossary entries do not break existing validation; auto-load is additive",
  "essential_context_preservation": "all changes are durable artifacts (glossary, overlay, skill docs)"
}
```

## Specification-Derived Verification Plan

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Verify this proposal cites all governing specs (visual inspection) | yes | (pending) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/ -q --tb=short` | (pending) | (pending) |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify proposal author identity matches resolved session role | yes | (pending) |
| `GOV-12` | Verify TEST-11688 exists and is linked to WI-5643 | yes | (pending) |
| `GOV-13` | Verify TEST-11688 is assigned to PHASE-001 | yes | (pending) |

## Acceptance Criteria

1. `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md` contains the envelope-open pre-flight line in Phase B.
2. `config/agent-control/SESSION-STARTUP-INDEX.md` contains a corresponding reference in Phase B.
3. `config/agent-control/activity-disposition-profiles.toml` build activity `skills` list includes `gtkb-work-item`.
4. `.claude/rules/canonical-terminology.md` has new entries for "Worker-role provenance" and "Unclassified mutation class".
5. `.claude/skills/gtkb-bridge/SKILL.md` has the per-harness generator inventory note and the `Responds to` chain semantics note.
6. All existing tests pass: `python -m pytest platform_tests/ -q --tb=short`.
7. `ruff check` and `ruff format --check` pass (no Python files changed, but verify config file syntax).
8. No existing governance gate is weakened or removed.

## Risks / Rollback

- **Risk: Auto-load name drift** — the skill was recently renamed from `kb-work-item` to `gtkb-work-item`. Adding both names to the auto-load list provides backward compatibility. If only one is present, the other harness's adapter may fail. Mitigation: include both names.
- **Risk: Glossary entry conflicts** — if a future WI adds a competing "worker-role provenance" glossary entry, the canonical-terminology.md will have duplicates. Mitigation: cite the source line references so future WIs can cross-check.
- **Risk: Startup overlay length** — adding lines to the overlay increases startup token cost. Mitigation: the pre-flight line is one sentence; the total addition is under 100 tokens.
- **Rollback:** Revert the commit. No data migration, no state change. All changes are additive text in configuration and documentation files.

## Files Expected To Change

- `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md` — add envelope-open pre-flight line
- `config/agent-control/SESSION-STARTUP-INDEX.md` — add corresponding Phase B reference
- `config/agent-control/activity-disposition-profiles.toml` — add `gtkb-work-item` to build skills
- `.claude/rules/canonical-terminology.md` — add two new glossary entries
- `.claude/skills/gtkb-bridge/SKILL.md` — add generator inventory note + `Responds to` note

## Recommended Commit Type

`feat`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
