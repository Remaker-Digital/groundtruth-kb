# Slice 1: LO Advisory Owner-Grilling Gate — Rule Amendment

**Bridge ID:** `gtkb-lo-advisory-owner-grilling-gate-001`
**Status:** NEW
**Filed by:** Prime Builder (harness B), 2026-05-29 (S364)
**Project:** PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001 (3 WIs: WI-3444, WI-3445, WI-3446)
**Slice scope:** Slice 1 of 3 — rule amendment + advisory template skeleton only. Skills/checklists (Slice 2) and lint script + hook + tests (Slice 3) follow as separate bridge proposals.

## target_paths

- `.claude/rules/peer-solution-advisory-loop.md` — amend with new `## Owner-Grilling Gate` section codifying `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`; include an example `## Required Prime Builder Owner-Grilling Gate` block as documentation skeleton.

## Specification Links

- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` v1 (inserted this turn, S364 2026-05-29) — governance principle that LO advisories classified `adopt`/`adapt` MUST include a Prime Builder owner-grilling gate before any derived implementation proposal exists. **Primary governing spec for Slice 1.**
- `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` v1 (inserted this turn) — machine-checkable contract for advisory-shape detection, gate-presence assertion, gate-content assertion, two-phase enforcement, and owner-waiver path. **Cited; full mechanical test coverage deferred to Slice 3 by scope-reduction.**
- `.claude/rules/peer-solution-advisory-loop.md` — existing rule receiving the amendment.
- `.claude/rules/prime-builder-role.md` § "AskUserQuestion as the Only Valid Owner-Decision Channel" — gate references AUQ-only as the durable decision channel.
- `.claude/rules/file-bridge-protocol.md` § "Mandatory Owner Decisions / Input Section Gate" — downstream bridge proposals derived from gated advisories must populate this section; cited cross-reference, not duplicated.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — chat-derived spec approval pattern.
- `GOV-ARTIFACT-APPROVAL-001` + `PB-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` — formal-artifact-approval governance for the GOV and DCL inserts done this turn.
- `GOV-STANDING-BACKLOG-001` — known-work authority context for WI capture.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal must cite all relevant specs (this section is the satisfaction).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification requires spec-derived tests (test plan below; DCL full coverage scope-reduced to Slice 3 with explicit acknowledgement in this proposal).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority: this proposal is filed under the canonical bridge protocol (`bridge/INDEX.md` is authoritative; verdict workflow is NEW/REVISED → GO/NO-GO; post-impl → VERIFIED).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development pattern: the GOV + DCL inserts this turn (artifacts), the project + WIs (artifacts), and the rule amendment (artifact) all conform to artifact-first delivery.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle triggers: the INTAKE deferred deliberation lifecycle (capture → promotion to GOV/DCL), the bridge proposal NEW lifecycle (toward GO → implementation → VERIFIED), and the project lifecycle (active → terminal) are managed per the artifact-lifecycle-trigger contract.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance: owner decisions are captured via AUQ as durable artifacts; requirements (INTAKE) and specifications (GOV/DCL) are append-only artifacts in MemBase; ADRs and DCLs cited above are governance artifacts; backlog (project + WIs) is the canonical known-work artifact surface.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` and `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` (both inserted v1 this turn under formal-artifact-approval packets) fully specify the principle and machine-checkable contract. No new requirement is needed for Slice 1; Slice 1 transcribes the principle into the cited rule file.

## Prior Deliberations

- `INTAKE-e226b05a` (2026-05-29 S364) — captured owner verbatim rule text via `gtkb-spec-intake` skill; `outcome=deferred`. Promoted to formal GOV + DCL via direct insert path with formal-artifact-approval packets rather than `confirm_intake` (which would have minted `SPEC-INTAKE-xxxxxx` IDs at `type='requirement'`).
- Deliberation Archive search for `owner grilling advisory implementation` (run S364 2026-05-29 pre-evaluation) returned the following adjacent records and no prior owner-grilling-gate work:
  - "GT-KB Self-Measurement and Self-Improvement Advisory" (lo_review)
  - "Peer Solution Advisory Report" (lo_review) — established the peer-solution-advisory-loop pattern; this proposal extends it
  - "Loyal Opposition Wrap-Up - 2026-05-03 23:16" (lo_review)
  - "LO opportunity-radar advisory disposition and SPEC-LO-OPPORTUNITY-RADAR-001 approval" (owner_conversation)
  - "Bridge Advisory Report Message Type Advisory" (lo_review)
- No prior deliberation rejected an owner-grilling-gate approach; this is greenfield design space at the advisory→proposal interface.

## Applicability Preflight

Output of `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-advisory-owner-grilling-gate` (run during proposal filing, S364 2026-05-29):

- packet_hash: `sha256:778adc7c0ab06fd4df38c8a7b020ad2436c064f3e1b49159ba751e0add2dd428`
- content_source: `indexed_operative`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`

| Spec | Severity | Cited |
|------|----------|-------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | yes |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | yes |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | yes |

## Clause Applicability

Output of `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-advisory-owner-grilling-gate` (run during proposal filing, S364 2026-05-29):

- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0

| Clause | Spec | Applicability | Evidence found | Severity |
|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking |

## Implementation Plan

### Slice 1 in this proposal

Amend `.claude/rules/peer-solution-advisory-loop.md` with one new top-level section, inserted between the existing § "Owner-Dialogue Workflow" (§ on workflow step 6) and § "Bridge Integration":

```
## Owner-Grilling Gate (Authority: GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001)

Any LO advisory whose recommended Prime Builder disposition is `adopt` or
`adapt` MUST include a `## Required Prime Builder Owner-Grilling Gate`
section in the advisory body. The gate section enumerates:

1. Whether this advisory implies future implementation work (yes/no with
   brief rationale).
2. What Prime Builder must grill the owner about before drafting any
   implementation proposal derived from this advisory.
3. What owner decisions must be durable, recorded via `AskUserQuestion`
   per `.claude/rules/prime-builder-role.md` § "AskUserQuestion as the
   Only Valid Owner-Decision Channel", before an implementation
   proposal can exist.

Prime Builder must conduct a structured owner clarification/grilling
pass — using the `/grill-me-for-clarification` skill or an equivalent
AUQ-recorded structured interview — and the resulting AUQ evidence
MUST land in the resulting bridge proposal's mandatory `## Owner
Decisions / Input` section (per
`.claude/rules/file-bridge-protocol.md` § "Mandatory Owner Decisions /
Input Section Gate") before the proposal is filed as `NEW`.

Scope: The gate fires for `adopt`/`adapt` classifications only.
`reject`/`monitor` advisories are terminal; `defer` advisories receive
the gate at defer-trigger reactivation, not at original filing.

Mechanical contract: `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001`
specifies advisory-shape detection, gate-presence assertion,
gate-content assertion, two-phase enforcement (warning then blocking
via separate owner approval), and the owner-waiver path. The
deterministic lint that enforces the contract lands in Slice 3 of
PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001 (WI-3446); Slices 1 and 2
are advisory-only until Slice 3 ships the lint.

### Example: Required Prime Builder Owner-Grilling Gate skeleton

The following section template is included as documentation. LO uses
it as the starting point when authoring an advisory classified as
`adopt` or `adapt`:

    ## Required Prime Builder Owner-Grilling Gate

    ### Implementation implied
    Yes — this advisory recommends adopt/adapt of <pattern>, which
    requires <files/specs> to be modified. OR: No — recommendation
    is procedural only, no source mutation expected.

    ### Grill-the-owner questions
    Prime Builder must obtain durable AUQ-recorded answers to:
    1. <question 1 about scope>
    2. <question 2 about rule home / authority>
    3. <question 3 about risks or alternatives>
    ...

    ### Required durable owner decisions
    The following AUQ answers must exist before an implementation
    proposal can be filed:
    - <decision 1>
    - <decision 2>
    ...
```

### Slice 2 (separate future bridge proposal)

`gtkb-lo-advisory-owner-grilling-gate-002-slice-2-skills-checklists.md` will:
- Add `Advisory Report` as 5th output mode in `independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md` (§ "Required Output Modes").
- Add an `Advisory Report Checklist` to `independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md`.
- Amend three skills with gate-emission guidance: `.codex/skills/codex-report/SKILL.md`, `.codex/skills/lo-opportunity-radar/SKILL.md`, `.codex/skills/loyal-opposition-hygiene-assessment/SKILL.md`, plus the Claude-side parity copy `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md`.
- target_paths: 6 files. No new scripts; no hook registration.

### Slice 3 (separate future bridge proposal)

`gtkb-lo-advisory-owner-grilling-gate-003-slice-3-lint-and-hook.md` will:
- Create `scripts/advisory_grilling_gate_lint.py` implementing the DCL's 4 assertions (Phase 1: warning only).
- Register a Stop-mode hook in `.claude/settings.json` and `.codex/hooks.json` invoking the lint.
- Add `tests/scripts/test_advisory_grilling_gate_lint.py` covering all 5 classifications, gate-presence pass/fail, gate-content pass/fail, owner-waiver path, false-positive containment.
- Update `gt platform doctor` to surface lint warnings as a `_check_advisory_grilling_gate` health check.
- target_paths: 5 files. Includes mechanical enforcement promotion to warning phase.

## Spec-to-Test Mapping (Slice 1)

| Linked Spec | Slice 1 Test | Verification Command |
|---|---|---|
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` | T1: rule file contains `## Owner-Grilling Gate` heading and cites both `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` and `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` | `grep -E "^## Owner-Grilling Gate" .claude/rules/peer-solution-advisory-loop.md && grep -E "GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001\|DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001" .claude/rules/peer-solution-advisory-loop.md` |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` | T2: GOV row exists in MemBase at v1, `status='specified'`, `type='governance'` | `python -c "import sys; sys.path.insert(0,'groundtruth-kb/src'); from groundtruth_kb.db import KnowledgeDB; s=KnowledgeDB().get_spec('GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001'); assert s['version']==1 and s['status']=='specified' and s['type']=='governance'"` |
| `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` | T3: DCL row exists in MemBase at v1 with 4 named assertions | `python -c "import sys,json; sys.path.insert(0,'groundtruth-kb/src'); from groundtruth_kb.db import KnowledgeDB; s=KnowledgeDB().get_spec('DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001'); a=s['assertions']; a=json.loads(a) if isinstance(a,str) else a; names={x['name'] for x in a}; assert names=={'advisory_shape_mode_header','classification_section_present','gate_presence_when_adopt_adapt','gate_content_three_enumerations'}"` |
| `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` | T4 (scope-reduced): example skeleton section is present in the rule file as documentation reference | `grep -E "^## Required Prime Builder Owner-Grilling Gate" .claude/rules/peer-solution-advisory-loop.md` (matches the example skeleton heading in the amended rule) |

**Explicit scope-reduction acknowledgement (per `feedback_codex_full_ip_d_test_coverage_strict.md` pattern):** `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001`'s full mechanical assertion coverage (lint script invocation against advisory files) is deferred to Slice 3 (WI-3446). Slice 1 verifies DCL existence + assertion catalog only; runtime lint behavior is verified in Slice 3. This is a deliberate slice boundary, not a coverage gap. Slice 3's post-impl verification will close the DCL coverage.

## Acceptance Criteria

- [ ] `.claude/rules/peer-solution-advisory-loop.md` contains `## Owner-Grilling Gate` section with the body shown in Implementation Plan.
- [ ] Rule file's new section cites both `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` and `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` as authority.
- [ ] Example `## Required Prime Builder Owner-Grilling Gate` skeleton is present in the rule file as documentation reference.
- [ ] T1-T4 above all pass.
- [ ] No other files modified.
- [ ] Bridge applicability preflight passes with `missing_required_specs: []`.
- [ ] Clause preflight passes (or owner waiver documented per blocking gap).
- [ ] No credential-shaped tokens introduced.

## Risk / Rollback

- **Risk level:** LOW. Slice 1 is rule-text amendment only. No source code changes. No hook registrations. No new scripts. No behavior change at runtime — the lint that mechanically enforces the gate arrives in Slice 3. Slice 1 changes are documentation-class.
- **Rollback:** `git revert` the rule file edit. MemBase rows (GOV, DCL, project, WIs) are append-only and remain as inserted; rollback only affects the working-tree rule file. No state corruption risk.
- **Pre-existing-content drift:** The peer-solution-advisory-loop.md file is in current modified-but-uncommitted state per `git status` at session start. Slice 1 implementation will rebase its edit on top of any concurrent modifications; if conflicts emerge, REVISED with conflict resolution.

## Owner Decisions / Input

Owner decisions captured via `AskUserQuestion` in S364 (2026-05-29) before this proposal was filed, per `.claude/rules/prime-builder-role.md` § "AskUserQuestion as the Only Valid Owner-Decision Channel":

1. **Rule home** (AUQ "Where should the LO Advisory Owner-Grilling Gate live"): Owner chose "Extend peer-solution-advisory-loop.md (Recommended)". Confirmed gate composes with existing adopt/adapt/reject/defer/monitor classification rather than being a universal new rule.
2. **Gate scope** (AUQ "Which advisory classifications must include the gate"): Owner chose "adopt + adapt only (Recommended)". Confirmed the gate fires at proposal-imminent classifications only; defer/reject/monitor stay on their existing paths.
3. **Skill targets** (AUQ "Which skill should be updated to enforce the gate"): Owner chose "All three: codex-report, lo-opportunity-radar, loyal-opposition-hygiene-assessment". Confirmed Slice 2 will amend all three skills (informational for this Slice-1 proposal; Slice 1 itself does not touch skills).
4. **Procedural** (AUQ "How should I proceed from the locked scope"): Owner chose "Proceed: capture spec → backlog → file bridge proposal (Recommended)". Authorized the canonical-chain progression that resulted in INTAKE-e226b05a, GOV+DCL inserts, project + 3 WIs, and this bridge proposal.
5. **GOV approval** (AUQ "Approve insertion of GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001"): Owner chose "Approve as drafted (Recommended)". Formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-29-GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001.json`. Insert verified as v1.
6. **DCL approval** (AUQ "Approve insertion of DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001"): Owner chose "Approve as drafted (Recommended)". Formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-29-DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001.json`. Insert verified as v1 with 4 assertions.

## Verification Procedure (For Post-Implementation Report)

When Slice 1 implementation lands:
1. Run T1-T4 from Spec-to-Test Mapping.
2. Re-run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-advisory-owner-grilling-gate-001`; expect `preflight_passed: true`.
3. Run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-advisory-owner-grilling-gate-001`; expect no blocking gaps for cited specs.
4. Confirm `git diff` shows only `.claude/rules/peer-solution-advisory-loop.md` changes; no other path mutations.
5. Document T1-T4 evidence + preflight outputs in the Slice 1 post-implementation report (next version of this bridge thread).

## Notes for Loyal Opposition

- **Two-axis classification reminder:** This proposal itself is AXIS-1 dispatchable work (self-contained review, no owner-AUQ-mid-stream needed). Loyal Opposition should be able to GO/NO-GO this proposal from a headless dispatch without further owner input.
- **The proposal authoring itself was an AXIS-2 surface** (multi-AUQ scope-lock); 6 AUQs were resolved in this session before this proposal existed. Slice 1 implementation post-GO is AXIS-1.
- **Conventional commits type recommendation** (per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B): `feat:` — this slice introduces a new governance principle's documentation surface and the principle itself is net-new behavior contract authored in the rule. Net LOC ~50 lines added to one rule file; classification `feat` rather than `docs` because the section codifies enforceable behavior (even if mechanical enforcement waits for Slice 3).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
