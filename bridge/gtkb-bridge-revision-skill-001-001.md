NEW

# GT-KB Bridge Revision Filing Skill - Slice 1 NEW

bridge_kind: implementation_proposal
Document: gtkb-bridge-revision-skill-001
Version: 001 (NEW; Slice 1 - /bridge revise helper and tests)
Author: Prime Builder (Codex, harness A)
Date: 2026-05-12 UTC
Implements: WI-3257 (Bridge revision filing skill: /bridge revise verb + helper for REVISED versions)
Recommended commit type: feat:

## Claim

This proposal implements WI-3257 by adding a deterministic bridge revision filing helper for the repeated Prime Builder task of responding to Loyal Opposition NO-GO findings. Today each revision requires manual reconstruction of the thread chain, next version number, finding checklist, preflight reminders, and INDEX update. That is exactly the repetitive plumbing targeted by the Deterministic Services Principle.

The slice creates a helper-backed `/bridge revise <slug>` workflow that reads the live `bridge/INDEX.md` entry for a thread, loads the latest NO-GO plus the prior proposal chain, computes the next version, generates a finding-by-finding REVISED skeleton, writes the new bridge file without overwriting existing versions, and inserts the REVISED line at the top of the same INDEX entry. Implementation is not authorized until Loyal Opposition returns GO on this proposal.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `PB-STANDING-BACKLOG-CONTINUITY-001`
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`
- `DCL-STANDING-BACKLOG-SCHEMA-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/acting-prime-builder.md`
- `.claude/rules/operating-model.md`
- `config/agent-control/harness-capability-registry.toml`
- `scripts/generate_codex_skill_adapters.py`
- `.claude/skills/bridge/SKILL.md`
- `.claude/skills/bridge-propose/helpers/write_bridge.py`

## Prior Deliberations

Manual Deliberation Archive search was run before filing with queries for `bridge revision filing skill WI-3257 deterministic services`, `DELIB-S312 deterministic services bridge helper`, and `gtkb bridge revision skill`.

Relevant results and source artifacts:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner directive that repetitive AI plumbing should become deterministic services instead of recurring session work.
- `.claude/rules/acting-prime-builder.md` section `Deterministic Services Principle` - live rule surface carrying the S312 mandate and preserving the boundary that formal approval evidence is still required.
- `DELIB-1795` - bridge-propose helper caller migration review context; relevant because this slice uses the same helper-mediated INDEX/file-write pattern instead of ad hoc bridge edits.
- `DELIB-1552` and `DELIB-1553` - DA read-surface / bridge template pre-population review context; relevant because bridge helper workflows must preserve Prior Deliberations obligations rather than bury them.
- `DELIB-1239` and `DELIB-0734` - bridge-propose skill history; relevant predecessor for governed bridge-file helper behavior.
- `DELIB-1897` - bridge skill unification history; relevant because this slice extends the canonical `gtkb-bridge` skill surface and must keep Codex adapter parity.
- WI-3257 in MemBase `current_work_items` - current authoritative backlog row for this proposal.

No cited deliberation authorizes bypassing the bridge, specification-linkage, credential-scan, or approval-packet gates.

## Owner Decisions / Input

- The owner selected `Pick From Standing Backlog` for this Prime Builder session and then confirmed `proceed with Pick From Standing Backlog` after the startup input gate blocked tool use.
- Standing backlog governance authorizes Prime Builder to advance backlog items through the bridge protocol, not to skip review.
- WI-3257 is a P0 MemBase backlog item under `GTKB-DETERMINISTIC-SERVICES-001`, implementation order 1, subproject `Bridge mechanics`.

Outstanding owner decisions before GO: none. This slice changes project-local skill/helper/test surfaces only. No deployment, history rewrite, credential lifecycle action, production operation, Agent Red live artifact mutation, or formal GOV/SPEC/PB/ADR/DCL mutation is in scope.

## Backlog Evidence

MemBase `current_work_items` row `WI-3257` states:

- Title: `Bridge revision filing skill: /bridge revise verb + helper for REVISED versions`.
- Priority: `P0`.
- Acceptance summary: `/bridge revise <slug>` reads latest NO-GO findings and prior NEW/REVISED, bumps version number, atomically inserts REVISED line at top of INDEX entry, runs pre-filing applicability and clause preflights against the new file, and pre-populates a finding-by-finding response shell.
- Intended future bridge thread slug: `gtkb-bridge-revision-skill-001`.

Live `bridge/INDEX.md` had no existing `Document: gtkb-bridge-revision-skill-001` entry before this proposal was filed.

## Standing Backlog Visibility

- **Inventory artifact:** this proposal enumerates the single current MemBase backlog item in scope, `WI-3257`, including its priority, implementation order, project grouping, acceptance summary, and intended bridge thread slug.
- **Review packet:** this bridge file is the Loyal Opposition review packet for the proposed WI-3257 implementation slice.
- **DECISION DEFERRED:** this proposal does not mutate MemBase work item state. Closing or advancing `WI-3257` is deferred until post-implementation verification, and any future `gt bridge revise` CLI wrapper is deferred to a later bridge slice.

## Scope

### IP-1: Add the bridge revision helper

Create `.claude/skills/bridge/helpers/revise_bridge.py`.

Required behavior:

1. Read live `bridge/INDEX.md` and find an exact `Document: <slug>` entry.
2. Require latest status to be `NO-GO` by default; optional dry-run may inspect other statuses but must refuse writes unless latest is `NO-GO`.
3. Load the latest NO-GO file and the prior version chain in that thread.
4. Compute the next zero-padded version number from the highest existing version in the thread.
5. Extract finding labels from the latest NO-GO using conservative markdown patterns for headings and list entries containing `F1`, `F2`, `P0` through `P4`, or `Finding`.
6. Generate a REVISED skeleton with required sections:
   - status line `REVISED`
   - metadata block
   - `## Revision Claim`
   - `## Specification Links`
   - `## Prior Deliberations`
   - `## Owner Decisions / Input` when the prior proposal contained that section or owner-decision language
   - `## Findings Addressed` with one subsection per extracted finding
   - `## Scope Changes`
   - `## Pre-Filing Preflight Subsection`
   - `## Verification Plan`
   - `## Risk And Rollback`
7. Reuse the bridge-propose helper credential scan policy (`CREDENTIAL_PATTERNS + BASH_EXTRAS`, PII excluded) before writing the REVISED file.
8. Refuse to overwrite an existing bridge file.
9. Insert `REVISED: bridge/<slug>-<next>.md` at the top of the existing document entry using atomic temp-file replacement and an INDEX change check.
10. Provide a `--dry-run` or equivalent callable mode returning the planned path, extracted findings, and proposed INDEX line without writing files.

### IP-2: Add a documented `/bridge revise` workflow to the canonical bridge skill

Update `.claude/skills/bridge/SKILL.md` to describe the Prime Builder revise operation and its helper path. The new text must make clear that the helper creates a skeleton, not a final substantive revision; the author still must fill in concrete fixes and then run required preflights before filing for review.

### IP-3: Preserve Codex adapter parity

Run `python scripts/generate_codex_skill_adapters.py --update-registry` so `.codex/skills/bridge/SKILL.md`, `.codex/skills/MANIFEST.json`, and `config/agent-control/harness-capability-registry.toml` remain consistent with the canonical `.claude/skills/bridge/SKILL.md` source hash.

### IP-4: Add regression tests

Add `platform_tests/skills/test_bridge_revise_helper.py` covering:

1. Latest `NO-GO` thread produces a dry-run plan with the next version number and extracted findings.
2. Write mode creates `bridge/<slug>-NNN.md` and inserts the REVISED line above the NO-GO line in the same INDEX entry.
3. Existing target file causes a fail-fast no-overwrite error.
4. Non-`NO-GO` latest status refuses write mode.
5. Exact `Document:` matching avoids slug-prefix false positives.
6. Credential-shaped content in generated or supplied revision text aborts before file or INDEX mutation.
7. INDEX changed during write is detected and surfaced as a conflict.
8. Owner Decisions / Input section is carried forward when the prior proposal used it.

### IP-5: Add focused parity checks to verification

Implementation verification must run:

- `python -m pytest platform_tests/skills/test_bridge_revise_helper.py -q --tb=short`
- `python -m pytest platform_tests/skills/test_bridge_propose_helper.py -q --tb=short`
- `python scripts/generate_codex_skill_adapters.py --update-registry --check`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-revision-skill-001`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-revision-skill-001`

## Out Of Scope

- Implementing any active NO-GO revision with the new helper in this same slice.
- Changing bridge status semantics or adding a new bridge status.
- Replacing `bridge/INDEX.md` as the authoritative bridge queue.
- Creating a `gt bridge revise` CLI surface. This slice is skill-helper scope only; a CLI wrapper can be a later deterministic-services slice.
- Editing `.codex/skills/bridge/SKILL.md` manually. It must be regenerated from the canonical Claude skill.
- Mutating MemBase work item state, formal specs, release gates, deployment configuration, Git history, or external services.
- Touching Agent Red live project files.

## Files Expected To Change

- `.claude/skills/bridge/helpers/revise_bridge.py` - new helper implementation.
- `.claude/skills/bridge/SKILL.md` - canonical skill documentation for `/bridge revise`.
- `.codex/skills/bridge/SKILL.md` - regenerated adapter.
- `.codex/skills/MANIFEST.json` - regenerated adapter manifest if the generator updates it.
- `config/agent-control/harness-capability-registry.toml` - regenerated source hash if changed.
- `platform_tests/skills/test_bridge_revise_helper.py` - new focused test coverage.

No files outside `E:\GT-KB` are in scope.

## Spec-To-Test Mapping

| Spec / governing surface | Proposed verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This proposal and later implementation report use append-only bridge files and live `bridge/INDEX.md`; helper tests assert same-entry REVISED insertion. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight on this bridge id must pass with `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must carry this mapping and execute the tests listed in IP-5. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All touched files are under `E:\GT-KB`; no Agent Red live files are touched. |
| `GOV-STANDING-BACKLOG-001` family | Proposal cites WI-3257 from MemBase and keeps the backlog item visible through bridge review before implementation. |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Helper replaces repeated manual bridge-revision ceremony with deterministic planning, write, and INDEX-update behavior while preserving review gates. |
| `config/agent-control/harness-capability-registry.toml` | Adapter generation check proves Codex skill parity after canonical skill edits. |
| `.claude/skills/bridge-propose/helpers/write_bridge.py` precedent | New helper mirrors file-first, no-overwrite, credential-scan, exact Document matching, and INDEX conflict behavior where applicable. |

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `revise_bridge.py` exists and implements IP-1.
- [ ] `.claude/skills/bridge/SKILL.md` documents `/bridge revise` and generated Codex adapter parity is restored.
- [ ] New tests in `platform_tests/skills/test_bridge_revise_helper.py` pass.
- [ ] Existing bridge-propose helper tests still pass.
- [ ] Adapter generation check passes.
- [ ] Applicability and clause preflights pass on this bridge id.
- [ ] Post-implementation report carries the spec-to-test mapping and observed command results.
- [ ] Loyal Opposition returns VERIFIED before any commit packages this work.

## Pre-Filing Preflight Subsection

Before filing, Prime Builder checked the intended bridge id and confirmed there was no existing `Document: gtkb-bridge-revision-skill-001` entry. The normal applicability preflight returned `ERR_NO_INDEX_ENTRY`, which is expected before the first INDEX entry exists. Clause preflight could not evaluate without an operative file, also expected before filing.

After this file is written and `bridge/INDEX.md` is updated, Prime Builder will run:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-revision-skill-001
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-revision-skill-001
```

Expected result: applicability preflight passes with no missing required or advisory specs; clause preflight exits 0 with no blocking gaps.

## Risk And Rollback

**Risk R1 (medium):** A helper that writes bridge files could amplify authoring mistakes. Mitigation: generated file is only a skeleton; tests enforce no-overwrite, exact Document matching, credential-scan abort, and INDEX conflict detection.

**Risk R2 (medium):** Finding extraction may miss unusually formatted NO-GO sections. Mitigation: the helper should include the raw latest NO-GO path and require author review; missed findings become visible in the generated skeleton and can be filled manually.

**Risk R3 (low):** Skill adapter drift if `.codex/skills/bridge/SKILL.md` is hand-edited or not regenerated. Mitigation: generator check in IP-5 and registry hash update in IP-3.

**Risk R4 (low):** This helper overlaps with the existing bridge-propose helper. Mitigation: shared behavior is intentionally mirrored, not redefined; this slice does not modify bridge-propose semantics.

Rollback: revert the implementation commit after VERIFIED. Since bridge files are append-only audit records, rollback does not delete this proposal; it only removes helper/source/test changes and can be followed by a superseding bridge note if needed.

## Loyal Opposition Asks

1. Confirm that WI-3257 is correctly scoped as a bridge-helper implementation proposal rather than a direct source edit.
2. Confirm the helper may write REVISED files and INDEX lines when invoked by Prime Builder after a latest NO-GO, provided it preserves no-overwrite, credential-scan, and INDEX conflict gates.
3. Confirm the first slice should stop at project-local skill-helper scope, leaving a future `gt bridge revise` CLI wrapper out of scope.
4. Confirm the proposed test matrix is sufficient for GO, or identify any missing failure mode before implementation begins.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
