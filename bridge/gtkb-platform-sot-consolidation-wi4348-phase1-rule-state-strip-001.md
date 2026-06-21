NEW

# Platform SoT Consolidation — WI-4348 Phase-1: rule-file role-state pointer-swaps

bridge_kind: prime_proposal
Document: gtkb-platform-sot-consolidation-wi4348-phase1-rule-state-strip
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-21 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: f8a1abee-94b2-4e6c-a9c7-795a8e7c7dae
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI explanatory output style, interactive session

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-WI-4348-PHASE1-RULE-STATE-STRIP
Project: PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION
Work Item: WI-4348

target_paths: [".claude/rules/operating-role.md", ".claude/rules/prime-builder-role.md", ".claude/rules/acting-prime-builder.md", "platform_tests/scripts/test_wi4348_rule_state_strip_phase1.py"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4348 ("Strip role-state and current-state prose from `.claude/rules/*.md`")
was split out of Slice 8 for an audit-first pass. The read-only audit
(`.gtkb-state/wi4348/audit-findings.md`) found that several behavior-contract
rule files bake current role/harness *state* into prose, duplicating the
canonical durable map. The live SoT read-discipline hook
(`DCL-SOT-READ-HOOK-CONTRACT-001`) already registers
`.claude/rules/operating-role.md` as a *forbidden substitute* for
`harness-state/harness-registry.json` — the mechanical proof that rule files
carrying role-state become forbidden state-substitutes.

This **Phase-1** proposal addresses the three clean-tree Category-A findings by
replacing the baked state with canonical-source pointers (the
canonical-terminology.md findings A4/A5 are deferred to Phase-1b to avoid the
contamination/sequencing collision with the queued WI-4350 glossary additions
and the uncommitted ollama hunk):

1. **A1 — `.claude/rules/operating-role.md`** (§ Harness Identity): relabel the
   baked `Codex = harness ID A` / `Claude Code = harness ID B` mapping as a
   non-authoritative illustration and keep the authority statement ("identity is
   resolved from `harness-state/harness-identities.json`").
2. **A2 — `.claude/rules/prime-builder-role.md`**: replace the baked assignment
   "Mike designates the active AI harness as **Prime Builder until further
   notice**" with a pointer to the durable role record
   (`harness-state/harness-registry.json`), preserving the behavior contract.
3. **A3 — `.claude/rules/acting-prime-builder.md`** (§ Current GroundTruth-KB
   Mapping): convert the current-assignment snapshot into a behavior rule that
   defers to the durable role map.

The role-resolution authority is unchanged — Phase-1 removes duplicated *prose*
state, not the durable map. No source logic, config, or KB schema changes.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed as the next status-bearing numbered
  bridge file; numbered file chain + dispatcher/TAFE state are canonical.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched paths
  (`.claude/rules/**`, `platform_tests/**`, the bridge file) are in-root under
  `E:\GT-KB`; placement/root-boundary contract satisfied.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section cites
  every governing spec; tests derive from them.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Project
  Authorization / Work Item metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Verification
  Plan maps each spec to an executed test.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — rule files must not be read as
  current-state substitutes for canonical SoT; removing baked role-state stops
  these files from being forbidden substitutes.
- `DCL-SOT-READ-HOOK-CONTRACT-001` — the hook that registers
  `operating-role.md` as a forbidden substitute for `harness-registry`; this
  Phase-1 directly reduces the substitute surface.
- `GOV-SESSION-ROLE-AUTHORITY-001` / `DCL-SESSION-ROLE-RESOLUTION-001` — the
  durable map is the role authority and rule files are explanatory guidance;
  Phase-1 aligns the prose to that split (rule files defer, do not assert state).
- `GOV-ARTIFACT-APPROVAL-001` — the three targets are protected narrative files;
  per-file narrative-artifact-approval packets are required at write time.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` /
  `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — covered by
  `PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-WI-4348-PHASE1-RULE-STATE-STRIP`
  (cites `DELIB-20265508`; mutations `documentation`, `test_addition`).
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — PAUTH cites
  `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` + `DCL-SOT-READ-HOOK-CONTRACT-001`.
- `GOV-STANDING-BACKLOG-001` — WI-4348 is a tracked work item; this advances it.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — preserves the role model as
  durable artifacts (the registry) and removes drift-prone prose duplication.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — durable artifacts over
  transient state baked in prose.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — touching the role-state
  surfaces triggers the alignment lifecycle event.

## Prior Deliberations

- `DELIB-20260672` — owner 16-AUQ SoT-read-discipline scope (the parent program).
- `DELIB-20265460` — Slice 8 / WI-4348 split-out decision (audit-first).
- `DELIB-20265508` — owner AUQ this session (2026-06-21) authorizing this
  Phase-1 filing. Owner-decision evidence.
- `DELIB-20261000` — Phase-1 Rule-Files Implementation VERIFIED (the separate
  harness-state SoT project's rule-file work; precedent for careful rule-file
  edits under the same SoT program).
- `bridge/gtkb-platform-sot-consolidation-umbrella-008.md` — umbrella GO.
- `GOV-SESSION-ROLE-AUTHORITY-001` / `DCL-SESSION-ROLE-RESOLUTION-001` — the
  authority-split decisions this Phase-1 aligns the prose to.

## Owner Decisions / Input

This proposal depends on owner approval and cites it here:

- **AUQ (2026-06-21, this interactive PB session), recorded as `DELIB-20265508`**
  (`source_type=owner_conversation`, `outcome=owner_decision`,
  `presented_to_user=true`, `transcript_captured=true`).
  - Question: file the WI-4348 Phase-1 proposal now (Category-A pointer-swaps),
    or hold?
  - Owner answer: **"File WI-4348 Phase-1 now."**
- Prior same-session AUQs authorized the audit-first pass and the broader
  "proceed autonomously + queue for Codex" stance.

No further owner decision is required to file this NEW proposal.

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-SESSION-ROLE-AUTHORITY-001`,
`DCL-SESSION-ROLE-RESOLUTION-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, and
`DCL-SOT-READ-HOOK-CONTRACT-001` already define that the durable map is
authoritative and rule files are explanatory. Phase-1 aligns the prose; no
new/revised requirement is needed.

## Planned Changes

### A1 — `.claude/rules/operating-role.md`

In § "Harness Identity", keep "Harness identity is installation-stable and
resolved from `harness-state/harness-identities.json`" as the authority, and
reframe the `A`/`B` list as an *illustrative example of current assignments
(non-authoritative; the file is the authority)* rather than a bare fact list —
so the file is not a state substitute for the identity map.

### A2 — `.claude/rules/prime-builder-role.md`

Replace the opening baked assignment ("Mike designates the active AI harness as
**Prime Builder until further notice** …") with a statement that the active
Prime Builder is the harness whose role record in
`harness-state/harness-registry.json` resolves to `prime-builder` (read via
`groundtruth_kb.harness_projection.read_roles` / `gt harness roles`), with the
session-resolved-role override per `DCL-SESSION-ROLE-RESOLUTION-001`. The
behavior contract (everything below the header) is preserved.

### A3 — `.claude/rules/acting-prime-builder.md`

In § "Current GroundTruth-KB Mapping", convert the current-assignment snapshot
("The owner-assigned active AI harness assumes the Prime Builder role until …")
into a behavior rule that defers to the durable role map for the live
assignment, retaining the compatibility/provenance narrative.

### Verification guard — `platform_tests/scripts/test_wi4348_rule_state_strip_phase1.py`

New pytest asserting each file defers to the canonical source and no longer
asserts baked role/harness state.

## Spec-Derived Verification Plan

| Specification | Test / Command | Expected |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` + `DCL-SOT-READ-HOOK-CONTRACT-001` (A1) | `test_operating_role_defers_identity` — asserts `operating-role.md` cites `harness-identities.json` as authority and frames the A/B mapping as illustrative (not a bare authoritative fact list) | PASS |
| `GOV-SESSION-ROLE-AUTHORITY-001` (A2) | `test_prime_builder_role_defers_assignment` — asserts `prime-builder-role.md` points to `harness-registry.json` for the active role and no longer carries the baked "until further notice" assignment as authority | PASS |
| `DCL-SESSION-ROLE-RESOLUTION-001` (A3) | `test_acting_prime_builder_defers_mapping` — asserts `acting-prime-builder.md` § Current Mapping defers to the durable role map | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | the pytest suite, run with the repo venv | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | applicability + clause preflights on this file | PASS |

Execution interpreter (repo venv):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_wi4348_rule_state_strip_phase1.py -q --no-header
```

## Risk / Rollback

Sensitivity note: these three files are role-contract files loaded at session
start, so the rewordings are behavior-relevant. Mitigations: (a) the durable
role authority (`harness-registry.json` / `harness-identities.json`) and the
role-resolution code path are unchanged — only duplicated *prose* state is
removed; (b) each edit is a protected-narrative change requiring an
owner-approval packet and Codex GO; (c) the guard test pins the
defer-to-canonical behavior. Rollback = `git revert` the single VERIFIED commit.

Sequencing: canonical-terminology.md findings (A4/A5) are intentionally NOT in
this proposal — they collide with the queued WI-4350 glossary additions
(`gtkb-platform-sot-consolidation-slice-2a-completion`) and the uncommitted
ollama hunk; they are deferred to a Phase-1b filed after WI-4350 lands.

## Bridge Filing

Filed under `bridge/` as the next status-bearing numbered bridge file for
`gtkb-platform-sot-consolidation-wi4348-phase1-rule-state-strip` (append-only).
Dispatcher/TAFE state + the numbered file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`docs` — governance/rule-file edits that realign role-state prose to the durable
map; the guard test is the regression boundary. No source/behavior change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
