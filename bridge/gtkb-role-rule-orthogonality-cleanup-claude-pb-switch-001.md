NEW

bridge_kind: implementation_proposal

Document: gtkb-role-rule-orthogonality-cleanup-claude-pb-switch
Version: 001
Author: Claude Code (harness B, owner-directed Prime Builder; durable role record `[]` at draft time)
Date: 2026-06-03 UTC
Reviewer: Loyal Opposition (Codex, harness A — current durable PB+LO single-harness role)
Recommended commit type: docs:

author_identity: Claude Code Prime Builder (owner-directed for S385 interactive session)
author_harness_id: B
author_session_context_id: S385-claude-rule-cleanup-and-pb-switch
author_model: Claude Opus 4.7 (1M context)
author_role_authority_basis: Owner directive in S385 interactive session ("Claude Code will now be the active Prime builder and Codex will take the role of Loyal Opposition") plus the AskUserQuestion answer recorded in §Owner Decisions / Input below. The canonical `::init gtkb pb` session-stated override keyword was not typed; this proposal IS the bridge artifact that, once GO'd, will move B's durable role to `[prime-builder]` so subsequent Claude Code work can file as PB without this caveat.
author_metadata_source: explicit S385 owner directive + AUQ answer + observed harness-registry/role-assignments JSON state at draft time

# Implementation Proposal — Orthogonality-Aligned Rule Cleanup + Claude=PB Role Switch

## Implementation Claim

This proposal does two coordinated things:

1. **Rule cleanup.** Remove the obsolete "all OTHER recorded harnesses are demoted to Loyal Opposition" language from `.claude/rules/operating-role.md` and the parallel sentence in `.claude/rules/canonical-terminology.md`'s `role assignment` definition. Replace with orthogonality-aligned language that matches the actual behavior of the canonical CLI (`gt mode set-role` / `gt harness set-role` → `mode_switch.transaction.apply_role_switch`, which already preserves inactive non-targets per the comment at `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py:378-380`) and the `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` owner decision.

2. **Role switch.** Reactivate harness B (Claude Code) from `status: suspended` to `status: active` via `gt harness activate`, then assign B the Prime Builder role via `gt mode set-role`. The canonical CLI will move A (Codex) from the current single-harness role set `[loyal-opposition, prime-builder]` to multi-harness role set `[loyal-opposition]`. C (Antigravity, `status: registered`, `role: [prime-builder]`) is **preserved unchanged** per the orthogonality model and the canonical CLI's "Non-active harness role sets are preserved" semantics.

The role switch is the **validation case** for the rule cleanup: after the edit, the rule text accurately describes what the CLI actually does, and the role switch produces a state that the cleaned-up rule would not have allowed under the old text (C preserved with `role: [prime-builder]` while B becomes active PB).

## Specification Links

- `GOV-HARNESS-ROLE-PORTABILITY-001` — role-portability spec; FR9 (single-active-per-role) remains in force; the obsolete language being removed was the over-broad "demote all OTHER" reading of FR9. This proposal does NOT supersede FR9 itself; it narrows the rule-text claim to match FR9's actual scope (active harnesses only).
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — multi-harness role configuration spec; the multi-harness topology assignment bullet is what this proposal rewrites.
- `GOV-SESSION-ROLE-AUTHORITY-001` — durable / session-stated role authority split; unaffected by this proposal but cited as carry-forward.
- `DCL-SESSION-ROLE-RESOLUTION-001` — deterministic resolver; unchanged.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` — interactive session-stated override; unchanged. Cited as relevant because the author of this proposal is operating under owner-directed PB authority without the canonical init-keyword.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3 (per VERIFIED bridge `gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-009`) — the orthogonality model formalized in MemBase. The rule edits make `.claude/rules/operating-role.md` consistent with the ADR v3 text.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval discipline. The narrative edits require formal-artifact-approval packets.
- `PB-ARTIFACT-APPROVAL-001` — Prime Builder protected-artifact write contract.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — narrative-artifact-approval-gate.py PreToolUse hook gates the rule-file writes on packet presence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs this proposal's `bridge/INDEX.md` routing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section satisfies the linkage requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — see §Specification-Derived Verification Plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — see §Project Linkage below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; this proposal decomposes the model shift into durable governed artifacts (rule edits + approval packets + bridge thread) rather than ad hoc runtime change.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the proposal distinguishes superseded (legacy CLI semantics), unchanged (Single-harness topology assignment bullet), candidate (rule edits), deferred (FR9 spec supersede + legacy CLI cleanup), and future-work (compatibility-mirror retirement) states.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; this proposal preserves the owner-decision, specification, backlog, and verification surfaces by routing the owner direction through bridge review + formal-artifact-approval packets.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — covered by Claude-side narrative-artifact-approval-gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files are under the `E:\GT-KB` project root.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — reporting and decisions in this proposal use fresh reads of the live `harness-state/*.json` artifacts and `bridge/INDEX.md`, not cached snapshots.
- `DCL-REPORTING-SURFACE-FRESH-READ-001` — the §Current State table below is a fresh read.

## Owner Decisions / Input

- **S385 owner directive (interactive prompt):** "Please update the GT-KB configuration: Claude Code will now be the active Prime builder and Codex will take the role of Loyal Opposition."
- **S385 owner follow-up:** "[the multi-harness topology assignment auto-demote rule] is obsolete guidance and should be removed."
- **S385 owner AskUserQuestion answer (sequencing/scope):** "Combined bridge proposal (Recommended)" — selected option from the 4-option AUQ asking how to scope and sequence the obsolete-guidance removal plus the role switch. Selected scope explicitly DEFERS legacy `scripts/harness_roles.py` cleanup and the formal `GOV-HARNESS-ROLE-PORTABILITY-001` FR9 supersede to follow-on bridges; this proposal narrows rule text only and uses the role switch as validation.
- **Implicit owner direction:** B holds the Prime Builder role for the duration of this proposal's drafting and implementation per the interactive directive. The role switch in §Implementation Plan formalizes this in durable state.

No new owner approval is required for the implementation step itself; this proposal IS the artifact through which the owner direction is carried into review.

## Prior Deliberations

- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — owner decision adopting role/status orthogonality with single-ACTIVE-per-role dispatch.
- `DELIB-S378-SLICE1-CLI-PACKET-FORM-WAIVER` — S378 Slice-1 CLI packet-form waiver (cited for context; not invoked here).
- S384 owner clarification (per `memory/MEMORY.md` `Role/Status Orthogonality Dispatch (S378->S379)` project entry): "role and active-status are ORTHOGONAL. C (Antigravity) HOLDS the PB role but is NOT active — 'active' is capability-gated on bridge-event reception, and C has no hook surface (event_driven_hooks=false). So single-ACTIVE-per-role HOLDS (B sole active PB)..." — this proposal applies that model to current state.
- `bridge/gtkb-role-status-orthogonality-dispatch-scoping-005.md` (VERIFIED at -006) — umbrella scoping; this proposal is one of the "downstream role-assignment language to update in later slices" items that scoping deferred.
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-009.md` (VERIFIED at -010) — landed `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3 + companion DCLs that the rule text being edited here is now out of sync with.
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-2-resolver-003.md` (VERIFIED at -004) — landed the resolver + attribution work that uses orthogonality semantics in practice.
- `bridge/gtkb-role-status-orthogonality-dispatch-landing-reconciliation-007.md` (VERIFIED at -008) — landing reconciliation (stale-projection regen) that fixed the dual-PB dispatch break and proved orthogonality preserved across landing operations.
- `bridge/gtkb-active-status-capability-gate-formalization-003.md` (VERIFIED at -004) and three sibling capability-gate threads — formalized "active = event-reception capability" gate.
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-007.md` (VERIFIED at -008) — Slice 1 of compatibility-mirror retirement; relevant because this proposal still writes the mirror via the canonical CLI's mirror path.

## Current State (fresh read of `harness-state/harness-registry.json` at draft time)

| Harness | id | type | status | role (registry) | role (mirror) | event_driven_hooks |
|---|---|---|---|---|---|---|
| codex | A | codex | active | `[loyal-opposition, prime-builder]` | `[loyal-opposition, prime-builder]` | true |
| claude | B | claude | **suspended** | `[]` | `[]` | true |
| antigravity | C | antigravity | registered | `[prime-builder]` | `[]` | false |

Mirror/registry drift for C (registry shows role=[prime-builder]; mirror shows role=[]) is pre-existing; this proposal does NOT attempt to reconcile that — separate concern under `gtkb-retire-role-assignments-mirror-*` follow-on slices.

## Requirement Sufficiency

Existing requirements sufficient. The orthogonality semantics required for this work are formalized in `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3, `DCL-SESSION-ROLE-RESOLUTION-001`, and `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`. No new specification creation or revision is required; this proposal narrows obsolete rule text to match those existing authorities.

## Target Paths

```json
[
  ".claude/rules/operating-role.md",
  ".claude/rules/canonical-terminology.md",
  "bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-001.md",
  "bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-002.md",
  "bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-003.md",
  "bridge/INDEX.md",
  "harness-state/harness-registry.json",
  "harness-state/role-assignments.json",
  "groundtruth.db",
  ".gtkb-state/**",
  ".groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-operating-role-md-orthogonality-cleanup.json",
  ".groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-canonical-terminology-md-role-assignment-orthogonality.json"
]
```

## Project Linkage

Project: `PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH` (per `memory/MEMORY.md` project line citing WI-3509/3511/3512). This proposal is a downstream rule-cleanup slice of that umbrella project per `bridge/gtkb-role-status-orthogonality-dispatch-scoping` umbrella decomposition.

Work Item: this proposal introduces no new work item; the rule cleanup is one of the "downstream role-assignment language to update in later slices" items already scoped under the umbrella project. If Codex requires a specific WI for project-linkage gate, propose `WI-CANDIDATE-RULE-CLEANUP-OPERATING-ROLE-MD-ORTHOGONALITY` for owner AUQ at GO time.

Project Authorization: this proposal does NOT cite a project-scoped implementation authorization. Authorization for this single proposal rests on the S385 owner AUQ + this proposal's GO. A future cleanup slice for the legacy `scripts/harness_roles.py` may benefit from a scoped authorization envelope but is out of scope here.

## Implementation Plan

### Step 1 — Narrative-artifact-approval packets

Generate two packets via the canonical CLI (not the per-amendment builder script pattern; `scripts/_build_narrative_packet_operating_role_md.py` is a historical artifact from S343 and is left untouched):

```text
& python -m groundtruth_kb generate-approval-packet `
  --kind narrative `
  --target .claude/rules/operating-role.md `
  --artifact-id claude-rules-operating-role-md-orthogonality-cleanup `
  --action update `
  --source-ref gtkb-role-rule-orthogonality-cleanup-claude-pb-switch `
  --explicit-change-request "S385 owner directive: remove obsolete 'all OTHER recorded harnesses are demoted' guidance; replace with orthogonality-aligned active-harness role assignment language. Inactive harnesses (registered or suspended) preserved unchanged." `
  --change-reason "S385 owner directive + AUQ; align rule text with ADR-SINGLE-HARNESS-OPERATING-MODE-001 v3 and DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH." `
  --approval-mode approve `
  --changed-by claude-prime-builder/B `
  --out .groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-operating-role-md-orthogonality-cleanup.json `
  --stage
```

Repeat for `.claude/rules/canonical-terminology.md` with `--artifact-id claude-rules-canonical-terminology-md-role-assignment-orthogonality` and corresponding paths.

The packet content is generated from the current working-tree blob sha256 of the post-edit file. Working-tree edit must precede `gt generate-approval-packet` invocation so the packet captures the edited content's hash.

### Step 2 — Edit `.claude/rules/operating-role.md`

Replace the **"Multi-harness topology assignment" bullet** (currently lines 49-52 in the live file; anchor: the bullet whose first line starts `- **Multi-harness topology assignment:**` and whose body says `all OTHER recorded harnesses are demoted to Loyal Opposition`) with:

```
- **Active-harness role assignment:** role assignment via the canonical
  `gt mode set-role` / `gt harness set-role` CLI updates the target ACTIVE
  harness's role set. The complementary role's active assignment is preserved
  on its current holder or atomically reassigned to a different active
  harness, maintaining the single-ACTIVE-per-role invariant (per
  `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` and FR9 of
  `GOV-HARNESS-ROLE-PORTABILITY-001`). **Inactive harnesses (registered or
  suspended) retain their existing role sets unchanged** — role and status
  are orthogonal axes (per the S384 owner clarification and
  `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3). The CLI gates the target on
  `status == "active"`; run `gt harness activate --harness <id>` first if
  needed.
```

The "Single-harness topology assignment" bullet immediately below is unchanged.

### Step 3 — Edit `.claude/rules/canonical-terminology.md`

Replace the **role-record sentence in the `role assignment` definition** (currently lines 708-710 in the live file; anchor: the sentence inside the `role assignment` definition that reads `The role map records one role per harness ID. Switching a harness to Prime Builder demotes all other recorded harnesses to Loyal Opposition in the same update.`) — current text:

```
The role map records one role per
harness ID. Switching a harness to Prime Builder demotes all other recorded
harnesses to Loyal Opposition in the same update.
```

with:

```
The role map records a role SET per harness ID (singleton lists for
multi-harness mode, multi-element lists for single-harness mode). Switching
an ACTIVE harness to Prime Builder updates that harness's role set; another
active harness holding the complementary role is preserved on its current
holder or atomically reassigned to maintain the single-active-per-role
invariant. Inactive harnesses (registered or suspended) retain their
existing role sets unchanged, consistent with the role/status orthogonality
model per `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` and
`ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3.
```

### Step 4 — Reactivate B and assign Prime Builder

```text
& python -m groundtruth_kb harness activate --harness B `
  --reason "S385 owner directive: Claude Code returns to active duty as Prime Builder; reverses S380 suspension."

& python -m groundtruth_kb mode set-role --harness B --role prime-builder `
  --reason "S385 owner directive: Claude Code becomes active Prime Builder; Codex becomes Loyal Opposition. Bridge GO at bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-002.md."
```

The `gt mode set-role` invocation will produce the audit-trail record under `.gtkb-state/mode-switches/`, demote A from `[loyal-opposition, prime-builder]` to `[loyal-opposition]`, and preserve C unchanged.

### Step 5 — Bridge dispatch settles

After the role switch, the cross-harness event-driven trigger sees the next bridge actionable signature change and dispatches to the newly-assigned counterpart harness (A=LO for any subsequent NEW/REVISED; B=PB for any subsequent GO/NO-GO). This proposal's own VERIFIED verdict will be authored by A under the new role assignment.

## Specification-Derived Verification Plan

| Specification / Decision | Verification | Result Criterion |
|---|---|---|
| Rule edit removed FR9-over-broad text from `.claude/rules/operating-role.md` | `python -c "import pathlib; t=pathlib.Path('.claude/rules/operating-role.md').read_text(encoding='utf-8'); assert 'all OTHER recorded harnesses are demoted' not in t; assert 'Active-harness role assignment' in t; print('OK')"` | Prints `OK` (no exception). |
| Rule edit removed FR9-over-broad text from `.claude/rules/canonical-terminology.md` | `python -c "import pathlib; t=pathlib.Path('.claude/rules/canonical-terminology.md').read_text(encoding='utf-8'); assert 'demotes all other recorded' not in t; assert 'role and status are orthogonal' in t or 'orthogonality model' in t; print('OK')"` | Prints `OK`. |
| Narrative-artifact-approval packets exist and validate | `python -m groundtruth_kb generate-approval-packet --validate-after ...` exit 0; both packet files exist under `.groundtruth/formal-artifact-approvals/` | Both packets generated; sha256 matches staged blob. |
| B reactivated to `status: active` | `python -m groundtruth_kb harness show --harness B` | JSON shows `status: active`. |
| B holds Prime Builder role | `python -m groundtruth_kb harness show --harness B` | JSON shows `role: ["prime-builder"]`. |
| A demoted from `[LO, PB]` to `[LO]` | `python -m groundtruth_kb harness show --harness A` | JSON shows `role: ["loyal-opposition"]`. |
| C preserved unchanged | `python -m groundtruth_kb harness show --harness C` | JSON shows `status: registered`, `role: ["prime-builder"]` (registry form; mirror drift pre-existing). |
| Single-active-per-role invariant holds | `python -c "from groundtruth_kb.mode_switch.invariants import verify_active_role_partition; from pathlib import Path; s = verify_active_role_partition(Path('.')); print(s)"` | Prints summary with `prime_builder_id='B'` and `loyal_opposition_id='A'`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | All rows in this table executed against the implemented changes | All criteria met. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `python -c "from pathlib import Path; paths=['.claude/rules/operating-role.md','.claude/rules/canonical-terminology.md','harness-state/harness-registry.json','harness-state/role-assignments.json']; [print(p, Path(p).resolve().relative_to(Path('.').resolve()))  for p in paths]"` | All paths inside `E:\GT-KB`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-role-rule-orthogonality-cleanup-claude-pb-switch --format json --preview-lines 400` | drift=[] |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-rule-orthogonality-cleanup-claude-pb-switch` | `preflight_passed: true`; `missing_required_specs: []`. |
| ADR/DCL clause preflight | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-rule-orthogonality-cleanup-claude-pb-switch` | exit 0; no blocking gaps. |

## Risk & Rollback

**Risk 1 — Codex (A) NO-GOs on author role-authority basis.** B's durable role at draft time is `[]`; this proposal asserts B is owner-directed Prime Builder for filing purposes. Codex may NO-GO with finding "Author role authority insufficient; refile from A or after canonical session-stated override invocation." Mitigation: this author_identity block is fully transparent. If NO-GO on this basis, owner can invoke the canonical `::init gtkb pb` in a follow-on prompt OR have Codex (current durable PB) refile the proposal verbatim.

**Risk 2 — Working-tree drift between rule edit and packet generation.** The narrative-artifact-approval-gate.py hook validates the packet sha256 against the staged blob. If autocrlf converts CRLF->LF between edit and stage, the staged sha differs from working-tree sha and packet validation fails. Mitigation: the recommended `--stage` flag stages the packet AND the target together; verify with `git cat-file -p <staged-sha>` if needed. Per `feedback_s378_narrative_artifact_packet_recipe.md`.

**Risk 3 — Inventory-drift pre-commit gate.** The dev-environment inventory-drift gate blocks protected-file changes unless a `bridge/*.md` is staged in the same commit (`has_bridge_review_evidence` valve). Mitigation: stage `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-*.md` files alongside the rule edits in the implementation commit. Per `feedback_inventory_drift_gate_bridge_evidence_escape_valve.md`.

**Risk 4 — C role/mirror drift exposes a latent bug.** Registry shows C role=[PB]; role-assignments.json mirror shows C role=[]. Pre-existing; not introduced by this proposal. The implementation does NOT touch C. If `verify_active_role_partition` raises on this drift after the role switch, that's a follow-on defect to file under the retire-role-assignments-mirror umbrella, not a regression of this proposal.

**Rollback.** Each step is reversible:
- Rule edits: `git checkout -- .claude/rules/operating-role.md .claude/rules/canonical-terminology.md`.
- Narrative-artifact-approval packets: `rm .groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-*.json`.
- B reactivation: `python -m groundtruth_kb harness suspend --harness B --reason "rollback per S385 abort"`.
- Role switch: `python -m groundtruth_kb mode set-role --harness A --role prime-builder --reason "rollback per S385 abort"` (returns A to PB; B's prior role=[] is lost but recoverable from audit-trail records under `.gtkb-state/mode-switches/`).

## Applicability Preflight

Command:

```text
& python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-rule-orthogonality-cleanup-claude-pb-switch
```

Observed result (live; pre-filing self-check):

```text
## Applicability Preflight

- packet_hash: `sha256:3b9b94bc700f11bafe66ed3212127681941444fbf859f1123ecd0cf6a9da3a07`
- bridge_document_name: `gtkb-role-rule-orthogonality-cleanup-claude-pb-switch`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-001.md`
- operative_file: `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
& python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-rule-orthogonality-cleanup-claude-pb-switch
```

Observed result (live; pre-filing self-check; exit 0):

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-role-rule-orthogonality-cleanup-claude-pb-switch`
- Operative file: `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

## Owner Action Required

None for the proposal-review phase. Codex GO/NO-GO is the next event.

If GO: Prime Builder (whoever holds that role after the switch — initially the implementing Claude Code session under this proposal's authority, then the durable Prime Builder for subsequent slices) implements per §Implementation Plan.

If NO-GO: revise per Codex findings and refile as `-003` (next available version after the GO/NO-GO verdict at `-002`).

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
