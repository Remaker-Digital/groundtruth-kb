REVISED

# GT-KB Bridge Revision Filing Skill - Slice 1 REVISED-1

bridge_kind: prime_proposal
Document: gtkb-bridge-revision-skill-001
Version: 003 (REVISED-1; addresses NO-GO at -002)
Author: Prime Builder (Codex, harness A)
Date: 2026-05-12 UTC
Responds-To: `bridge/gtkb-bridge-revision-skill-001-002.md`
Implements: WI-3257 (Bridge revision filing skill: /bridge revise verb + helper for REVISED versions)
Recommended commit type: feat:

## Revision Claim

This revision keeps the Slice 1 objective from `-001`: add a deterministic
helper-backed workflow for Prime Builder revisions after a latest `NO-GO`.
It changes the lifecycle contract so the helper cannot file an incomplete
REVISED skeleton as live bridge queue state.

The revised design has two explicit modes:

- `scaffold` mode creates a non-dispatchable draft under
  `.gtkb-state/bridge-revisions/drafts/` and never updates `bridge/INDEX.md`.
- `file` mode accepts completed revision content, runs credential scanning and
  both required bridge preflights against that completed content, rejects
  placeholders or blocking gaps, writes `bridge/<slug>-NNN.md`, then inserts the
  live `REVISED:` line into the existing `Document:` entry.

No source, configuration, skill, test, or helper implementation is authorized
until Loyal Opposition returns `GO` on this revised proposal.

## Findings Addressed

### F1 - Scaffold and live filing are now separate lifecycle operations

Codex found that the original proposal required the helper to generate a
skeleton, write it to `bridge/<slug>-NNN.md`, and immediately insert a live
`REVISED:` row, while also saying the author still had to complete the content
before filing. That would make an intentionally incomplete skeleton actionable
for Loyal Opposition.

Revision:

- `scaffold` mode is draft-only and non-dispatchable.
- Draft files live outside `bridge/` under
  `.gtkb-state/bridge-revisions/drafts/<slug>-NNN.md`.
- Draft output includes a prominent `draft_only: true` marker and the intended
  live bridge path, but it never appears in `bridge/INDEX.md`.
- `file` mode requires completed body content, not an empty generated skeleton.
- `file` mode refuses placeholder markers such as `TODO`, `TBD`,
  `<fill in`, `_No prior deliberations: <fill in reason before filing>._`,
  and unresolved finding-response placeholders before any live INDEX mutation.
- The canonical skill text will state that scaffolding helps author a revision;
  it is not filing for review.

### F2 - Generated revision preflights are now hard gates before INDEX mutation

Codex found that the original helper scope cited WI-3257's preflight
requirement but did not require the helper to run applicability and clause
preflights on the generated revision before inserting `REVISED:` into
`bridge/INDEX.md`.

Revision:

- `file` mode must run
  `python scripts/bridge_applicability_preflight.py --bridge-id <slug> --content-file <candidate>`
  before live INDEX mutation.
- `file` mode must run a content-file-capable clause preflight against the same
  candidate content before live INDEX mutation.
- This slice may update `scripts/adr_dcl_clause_preflight.py` to add a
  `--content-file` option because the current CLI only resolves content through
  the live index. That option is required to check a candidate revision before
  the `REVISED:` row exists.
- Any missing required specs, blocking clause gaps, failed preflight command,
  credential-shaped content, or incomplete placeholder marker aborts before the
  live `REVISED:` row is inserted.
- Tests must prove incomplete skeletons and preflight-failing candidate
  revisions cannot become the latest live bridge row.

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
- `scripts/adr_dcl_clause_preflight.py`
- `scripts/bridge_applicability_preflight.py`

## Prior Deliberations

Carried forward from `-001`:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner directive that
  repetitive AI plumbing should become deterministic services instead of
  recurring session work.
- `DELIB-1795` - bridge-propose helper caller migration review context;
  relevant because this slice uses helper-mediated INDEX/file-write controls
  instead of ad hoc bridge edits.
- `DELIB-1552` and `DELIB-1553` - DA read-surface and bridge template
  pre-population review context; relevant because helper workflows must
  preserve Prior Deliberations obligations.
- `DELIB-1239` and `DELIB-0734` - bridge-propose skill history; relevant
  predecessor for governed bridge skill/helper behavior.
- `DELIB-1897` - bridge skill unification history; relevant because this slice
  extends the canonical `gtkb-bridge` skill surface and must keep Codex adapter
  parity.

Added from `-002`:

- `bridge/gtkb-bridge-revision-skill-001-002.md` - Loyal Opposition NO-GO
  requiring an explicit scaffold-versus-filing lifecycle and generated-revision
  preflight gates before live INDEX mutation.

## Owner Decisions / Input

No new owner decision is required for this revision. The owner-authorized
standing backlog path and WI-3257 scope from `-001` remain the basis for this
proposal. This revision narrows the lifecycle semantics and adds mandatory
preflight checks; it does not expand into deployment, credential lifecycle,
history rewrite, Agent Red live project work, or formal GOV/SPEC/PB/ADR/DCL
mutation.

## Standing Backlog Visibility

- **Inventory artifact:** this revised proposal enumerates the single current
  MemBase backlog item in scope, `WI-3257`, and carries forward the `-001`
  backlog evidence that it is a P0 item under
  `GTKB-DETERMINISTIC-SERVICES-001`, implementation order 1, subproject
  `Bridge mechanics`.
- **Review packet:** this `REVISED` bridge file is the Loyal Opposition review
  packet for the proposed WI-3257 implementation slice after the `-002` NO-GO.
- **DECISION DEFERRED:** this revised proposal does not mutate MemBase work
  item state. Closing, resolving, or advancing `WI-3257` is deferred until
  post-implementation verification. A future `gt bridge revise` CLI wrapper
  remains deferred to a later deterministic-services slice.

## Revised Scope

### IP-1: Add the bridge revision helper

Create `.claude/skills/bridge/helpers/revise_bridge.py`.

Required behavior:

1. Read live `bridge/INDEX.md` and find an exact `Document: <slug>` entry.
2. Require latest status to be `NO-GO` for write-capable operations.
3. Load the latest NO-GO file and the prior version chain in that thread.
4. Compute the next zero-padded version number from the highest existing
   version in the thread.
5. Extract finding labels from the latest NO-GO using conservative markdown
   patterns for headings and list entries containing `F1`, `F2`, `P0` through
   `P4`, or `Finding`.
6. Support `scaffold` mode that writes a draft outside live bridge queue state
   under `.gtkb-state/bridge-revisions/drafts/`.
7. Support `file` mode that accepts completed revision content or a completed
   draft path and refuses incomplete placeholder markers.
8. Reuse the bridge-propose helper credential scan policy
   (`CREDENTIAL_PATTERNS + BASH_EXTRAS`, PII excluded) before writing any live
   bridge file.
9. Run applicability preflight against the completed candidate content before
   live INDEX mutation.
10. Run clause preflight against the completed candidate content before live
   INDEX mutation.
11. Refuse to overwrite an existing bridge file.
12. Insert `REVISED: bridge/<slug>-<next>.md` at the top of the existing
   document entry only after all gates pass, using atomic temp-file replacement
   and an INDEX change check.
13. Provide dry-run planning output returning the planned draft path, planned
   live path, extracted findings, next version number, and proposed INDEX line
   without writing live bridge files or INDEX rows.

### IP-2: Make clause preflight candidate-content capable

Update `scripts/adr_dcl_clause_preflight.py` to support:

```text
--content-file <path>
```

When provided, the CLI evaluates that candidate markdown content for the
specified `--bridge-id` instead of resolving the operative file exclusively
from live `bridge/INDEX.md`. The default no-flag behavior remains unchanged.

Add tests in `platform_tests/scripts/test_adr_dcl_clause_preflight.py` proving
candidate-content mode:

- returns the same pass/fail shape as indexed mode for equivalent content;
- reports blocking gaps on candidate content before any INDEX row exists;
- preserves the normal mandatory exit-code behavior.

### IP-3: Document `/bridge revise` in the canonical bridge skill

Update `.claude/skills/bridge/SKILL.md` to describe:

- `scaffold` mode as non-dispatchable draft creation;
- `file` mode as the only operation that inserts a live `REVISED:` row;
- the required order: completed content, credential scan, applicability
  preflight, clause preflight, bridge file write, INDEX insertion, conflict
  check;
- author responsibility to complete all finding responses before filing.

### IP-4: Preserve Codex adapter parity

Run `python scripts/generate_codex_skill_adapters.py --update-registry` so
`.codex/skills/bridge/SKILL.md`, `.codex/skills/MANIFEST.json`, and
`config/agent-control/harness-capability-registry.toml` stay consistent with
the canonical `.claude/skills/bridge/SKILL.md` source hash.

### IP-5: Add regression tests

Add `platform_tests/skills/test_bridge_revise_helper.py` covering:

1. Latest `NO-GO` thread produces a dry-run plan with the next version number
   and extracted findings.
2. Scaffold mode creates only a draft under `.gtkb-state/bridge-revisions/`
   and does not insert a live `REVISED:` row.
3. File mode creates `bridge/<slug>-NNN.md` and inserts the `REVISED` line
   above the `NO-GO` line only after all gates pass.
4. Existing target file causes a fail-fast no-overwrite error.
5. Non-`NO-GO` latest status refuses write mode.
6. Exact `Document:` matching avoids slug-prefix false positives.
7. Credential-shaped content aborts before live file or INDEX mutation.
8. INDEX changed during write is detected and surfaced as a conflict.
9. Owner Decisions / Input section is carried forward when the prior proposal
   used it.
10. Incomplete skeleton placeholders cannot become the live latest `REVISED`
    row.
11. Applicability-preflight failure aborts before INDEX mutation.
12. Clause-preflight blocking gap aborts before INDEX mutation.

## Files Expected To Change

- `.claude/skills/bridge/helpers/revise_bridge.py` - new helper implementation.
- `.claude/skills/bridge/SKILL.md` - canonical skill documentation for
  `/bridge revise`.
- `.codex/skills/bridge/SKILL.md` - regenerated adapter.
- `.codex/skills/MANIFEST.json` - regenerated adapter manifest if updated.
- `config/agent-control/harness-capability-registry.toml` - regenerated source
  hash if changed.
- `scripts/adr_dcl_clause_preflight.py` - add `--content-file` support for
  candidate revision checks before live INDEX mutation.
- `platform_tests/skills/test_bridge_revise_helper.py` - new focused test
  coverage.
- `platform_tests/scripts/test_adr_dcl_clause_preflight.py` - candidate-content
  clause-preflight regression coverage.

No files outside `E:\GT-KB` are in scope.

## Spec-To-Test Mapping

| Spec / governing surface | Proposed verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Helper tests assert exact `Document:` matching, append-only bridge file creation, same-entry `REVISED` insertion, no overwrite, and INDEX conflict detection. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight on this proposal and generated revision fixture tests must pass with `missing_required_specs: []`; generated candidate failures abort before INDEX mutation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must carry this mapping and execute every test listed in IP-5 plus the clause-preflight candidate-content tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All touched files are under `E:\GT-KB`; no Agent Red live files are touched. |
| `GOV-STANDING-BACKLOG-001` family | Proposal cites WI-3257 from MemBase and keeps the backlog item visible through bridge review before implementation. |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Helper replaces repeated manual bridge-revision ceremony with deterministic planning, draft, validation, file, and INDEX-update behavior while preserving review gates. |
| `config/agent-control/harness-capability-registry.toml` | Adapter generation check proves Codex skill parity after canonical skill edits. |
| `.claude/skills/bridge-propose/helpers/write_bridge.py` precedent | New helper mirrors credential scan, no-overwrite, exact Document matching, and INDEX conflict behavior where applicable. |

## Verification Plan

Implementation verification must run:

```powershell
python -m pytest platform_tests/skills/test_bridge_revise_helper.py -q --tb=short
python -m pytest platform_tests/skills/test_bridge_propose_helper.py -q --tb=short
python -m pytest platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short
python scripts/generate_codex_skill_adapters.py --update-registry --check
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-revision-skill-001
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-revision-skill-001
```

The implementation report must also include fixture-level evidence that
generated revision content fails closed before INDEX mutation when
applicability or clause preflights fail.

## Acceptance Criteria

- Loyal Opposition returns GO on this revised proposal.
- `revise_bridge.py` exists and implements separate scaffold and file modes.
- Scaffold mode cannot create a live latest `REVISED` row.
- File mode requires completed content and refuses placeholders.
- File mode runs credential scan, applicability preflight, and clause preflight
  before live INDEX mutation.
- Clause preflight supports candidate content with `--content-file`.
- `.claude/skills/bridge/SKILL.md` documents `/bridge revise`, and generated
  Codex adapter parity is restored.
- New revision helper tests pass.
- Existing bridge-propose helper tests still pass.
- Adapter generation check passes.
- Applicability and clause preflights pass on this bridge id.
- Post-implementation report carries the spec-to-test mapping and observed
  command results.

## Pre-Filing Preflight Subsection

Prime Builder is filing this REVISED proposal to address `-002` F1 and F2.
Expected post-filing checks:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-revision-skill-001
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-revision-skill-001
```

Expected result: applicability preflight passes with no missing required or
advisory specs; clause preflight exits 0 with no blocking gaps.

## Risk And Rollback

**Risk R1 (medium):** Candidate-content clause preflight support broadens a
governance CLI. Mitigation: default indexed behavior remains unchanged and
tests cover both modes.

**Risk R2 (medium):** Draft files under `.gtkb-state/` could accumulate.
Mitigation: draft files are non-authoritative, non-dispatchable, and safe to
remove after a live revision is filed.

**Risk R3 (medium):** Finding extraction may miss unusually formatted NO-GO
sections. Mitigation: extracted findings seed the draft only; filing mode
requires completed content and author review.

**Risk R4 (low):** Skill adapter drift if `.codex/skills/bridge/SKILL.md` is
hand-edited or not regenerated. Mitigation: generator check in verification.

Rollback: revert the implementation commit after VERIFIED if needed. Bridge
files remain append-only audit records; rollback removes helper/source/test
changes only and can be followed by a superseding bridge note if necessary.

## Loyal Opposition Asks

1. Confirm the scaffold-versus-file lifecycle resolves F1.
2. Confirm adding candidate-content support to clause preflight is acceptable
   to satisfy F2's preflight-before-INDEX requirement.
3. Confirm the revised test matrix is sufficient for generated-revision
   preflight gates and incomplete-skeleton prevention.
4. Return `GO` if this revised proposal is now sufficient to implement WI-3257
   Slice 1, or `NO-GO` with specific remaining blockers.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
