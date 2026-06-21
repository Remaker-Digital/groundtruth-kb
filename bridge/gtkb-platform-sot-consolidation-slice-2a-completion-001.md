NEW

# Platform SoT Consolidation — Slice 2A read-discipline narrative completion (WI-4345, WI-4350)

bridge_kind: prime_proposal
Document: gtkb-platform-sot-consolidation-slice-2a-completion
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-21 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: f8a1abee-94b2-4e6c-a9c7-795a8e7c7dae
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI explanatory output style, interactive session

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-SLICE-2A-NARRATIVE-COMPLETION
Project: PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION
Work Item: WI-4345

target_paths: [".claude/rules/prime-builder-role.md", ".claude/rules/canonical-terminology.md", "platform_tests/scripts/test_sot_read_discipline_narrative_completion.py"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal closes the two remaining un-delivered narrative deliverables of the
already-VERIFIED Slice 2A read-discipline work
(`bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-009.md`
VERIFIED). The Slice 2A implementation (commit `ed5da3650`) delivered the
PreToolUse Read hook, the Codex Bash adapter, the doctor check, the spec
extensions/inserts, the registry seeds, and tests — but two narrative items
were never delivered and fell outside the enumerated deliverable list of the
original Slice 2A PAUTH:

- **WI-4345** — Extend `.claude/rules/prime-builder-role.md`'s interrogative-default
  with a SoT-read-discipline clause: when verifying owner factual claims or
  deriving any state claim, Prime Builder routes reads through canonical reader
  entrypoints and avoids registered `forbidden_substitutes` paths, so state
  claims derive from fresh canonical reads. This makes `prime-builder-role.md`
  reciprocate the pointer that `.claude/rules/sot-read-discipline.md` already
  carries toward it (§ "Relationship to Other Rules" → prime-builder-role.md
  clause (a)).
- **WI-4350** — Add two glossary entries to `.claude/rules/canonical-terminology.md`
  for the load-bearing SoT-read-discipline concepts that currently have no
  glossary surface: **"SoT read discipline"** and **"forbidden substitute"**.
  (`canonical reader entrypoint` already exists in the glossary; these two do
  not.)

Both are non-destructive, additive narrative changes plus one guard test. No
source logic, config, or KB schema changes are in scope.

This proposal is filed under the gap-closure authorization captured this session
(`DELIB-20265458`) and the bounded PAUTH minted from it. Per the owner's
session directive, implementation and VERIFIED remain gated on Loyal Opposition
GO (cross-harness dispatch is currently failing; owner is handling Codex
separately) and on per-protected-file narrative-artifact-approval packets at
write time.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed as the next status-bearing numbered
  bridge file with dispatcher/TAFE publication; numbered file chain is canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section cites
  every governing spec; tests derive from the linked specs (below).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — proposal cites Project,
  Project Authorization, and Work Item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Spec-Derived
  Verification Plan maps each linked specification to an executed test.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (v2) — the parent governance principle for
  read discipline; WI-4345 operationalizes its clause (a) in the Prime Builder
  behavior contract.
- `DCL-SOT-READ-HOOK-CONTRACT-001` (v1) — the read-discipline hook contract whose
  concepts the glossary entries (WI-4350) define.
- `DCL-CONCEPT-ON-CONTACT-001` — touching the load-bearing SoT-read-discipline
  concepts triggers glossary promotion (the WI-4350 trigger).
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` — the glossary is the agent-side DA read
  surface; new canonical concepts must have glossary entries with DA-cited
  sources.
- `GOV-ARTIFACT-APPROVAL-001` — protected narrative edits to `.claude/rules/*.md`
  require narrative-artifact-approval packets at write time (implementation
  phase).
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` /
  `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — covered by
  `PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-SLICE-2A-NARRATIVE-COMPLETION`
  (cites `DELIB-20265458`).
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — the PAUTH cites
  `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` and `DCL-SOT-READ-HOOK-CONTRACT-001`.
- `GOV-STANDING-BACKLOG-001` — WI-4345 and WI-4350 are tracked work items in
  `PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION`; this proposal advances them.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — narrative completion
  preserves the SoT-read-discipline decisions as durable rule + glossary
  artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the work reorganizes/
  completes governance artifacts rather than transient state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — touching the
  SoT-read-discipline concepts triggers the glossary-promotion lifecycle event.

## Prior Deliberations

- `DELIB-20260671` — owner 7-AUQ pass authorizing the Platform SoT consolidation
  umbrella. This proposal completes Slice 2A under that umbrella.
- `DELIB-20260672` — owner 16-AUQ pass defining Slice 2A read-discipline scope
  (WI-4345 and WI-4350 originate here).
- `DELIB-20260673` — parallel-session fragmentation evidence; the motivation for
  routing reads through canonical readers (the WI-4345 clause).
- `DELIB-20260879` — Slice 2A read-discipline implementation envelope (the
  original PAUTH whose enumerated deliverables omitted these two narrative items).
- `DELIB-20265458` — owner AUQ this session (2026-06-21) authorizing this
  gap-closure PAUTH + proposal queuing. Owner-decision evidence for this filing.
- `DELIB-S324-PB-INTERROGATION-DIRECTIVE` — origin of the interrogative-default
  in `prime-builder-role.md`; WI-4345 extends that section with the SoT-read
  clause.
- `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-009.md` —
  Slice 2A VERIFIED verdict; this proposal completes the narrative remainder of
  that slice without reopening it.

## Owner Decisions / Input

This proposal depends on owner approval and cites it here:

- **AUQ (2026-06-21, this interactive PB session), recorded as `DELIB-20265458`**
  (`source_type=owner_conversation`, `outcome=owner_decision`,
  `presented_to_user=true`, `transcript_captured=true`).
  - Question: authorize a bounded PAUTH for WI-4345 + WI-4350 and file a NEW
    proposal to queue for Codex.
  - Owner answer: **"Authorize + queue proposal."**
- The owner separately directed (same session, prior AUQ) that I "proceed
  autonomously and queue GO/VERIFIED-dependent items for Codex" while the owner
  repairs/runs the failing Loyal Opposition dispatch.

No further owner decision is required to file this NEW proposal. Implementation
will additionally require per-protected-file narrative-artifact-approval packets
(`GOV-ARTIFACT-APPROVAL-001`) at write time for the two `.claude/rules/*.md`
targets.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing requirements
(`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v2, `DCL-SOT-READ-HOOK-CONTRACT-001`,
`DCL-CONCEPT-ON-CONTACT-001`, `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`) plus the
WI-4345/WI-4350 scope already define the intended behavior. This proposal is the
narrative completion of an already-VERIFIED slice; no new or revised requirement
is needed.

## Planned Changes

### WI-4345 — `.claude/rules/prime-builder-role.md`

Add a SoT-read-discipline bullet to the operational-implications list adjacent to
the existing interrogative-default clause, in substance:

> **SoT-read discipline** (per `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v2 clause (a)
> and `.claude/rules/sot-read-discipline.md`): when verifying owner factual
> claims or deriving any state claim, Prime Builder routes reads through the
> canonical reader entrypoint for each source-of-truth artifact and does not
> consult registered `forbidden_substitutes` paths. State claims derive from
> fresh canonical reads, not cached substitutes, stale mirrors, or generated
> summaries. The mechanical floor is the `.claude/hooks/sot-read-discipline.py`
> PreToolUse hook; its bypass (the owner-authorized `GTKB_SOT_READ_DISCIPLINE_BYPASS`
> environment override) is owner-authorized-only and must be logged with rationale.

### WI-4350 — `.claude/rules/canonical-terminology.md`

Add two glossary entries (following the file's Definition / Canonical alias /
Not-to-be-confused-with / Source / Implementation-pointer convention):

- **SoT read discipline** — the PreToolUse enforcement layer that blocks reads
  against registered forbidden-substitute paths so state claims derive from
  fresh canonical reads; operationalizes `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v2;
  implemented by `.claude/hooks/sot-read-discipline.py` (+ the Codex Bash
  adapter) per `DCL-SOT-READ-HOOK-CONTRACT-001`; narrative authority
  `.claude/rules/sot-read-discipline.md`.
- **forbidden substitute** — a non-canonical alias path for a source-of-truth
  artifact that the SoT read discipline blocks; registered in the
  `forbidden_substitutes` column of `config/registry/sot-artifacts.toml` per
  `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v2; source motivation `DELIB-20260673`
  (parallel-session fragmentation). Not to be confused with an
  archived/historical copy readable for audit via the owner-authorized bypass.

### Verification guard — `platform_tests/scripts/test_sot_read_discipline_narrative_completion.py`

New pytest asserting both narrative additions are present (and reference their
governing specs), so the completion cannot silently regress.

## Spec-Derived Verification Plan

| Specification | Test / Command | Expected |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v2 (WI-4345 clause) | `test_prime_builder_role_has_sot_read_clause` (asserts `prime-builder-role.md` contains the SoT-read clause referencing `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` + `sot-read-discipline.md` + `forbidden_substitutes`) | PASS |
| `DCL-SOT-READ-HOOK-CONTRACT-001` / `DCL-CONCEPT-ON-CONTACT-001` / `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` (WI-4350) | `test_canonical_terminology_has_sot_read_discipline_entry` + `test_canonical_terminology_has_forbidden_substitute_entry` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | the pytest suite above, run with the repo venv | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | live numbered-file chain shows this thread `NEW`; applicability + clause preflights | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-platform-sot-consolidation-slice-2a-completion` | `preflight_passed: true`, `missing_required_specs: []` |

Execution interpreter (repo venv):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_sot_read_discipline_narrative_completion.py -q --no-header
```

## Risk / Rollback

Low risk: additive narrative text + one new test file; no source logic, config,
or schema change. The VERIFIED finalization stages only the three `target_paths`.
Rollback = revert the single VERIFIED commit (or re-edit the two narrative files
to remove the additions). No data migration, no runtime behavior change beyond
the (already-shipped) hook the clause documents.

Note on contamination: `.claude/rules/canonical-terminology.md` currently carries
unrelated uncommitted hunks (ollama-routing terminology) from a different work
stream. The WI-4350 edit must be staged so the VERIFIED commit does not bundle
those hunks; if the tree is not clean at implementation time, implementation of
the WI-4350 portion waits on that file being committed by its owning thread.
WI-4345 (`prime-builder-role.md`) is on a clean path.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-platform-sot-consolidation-slice-2a-completion`; no prior
version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the
numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`docs` — narrative governance additions (a Prime Builder behavior clause and two
glossary entries) plus a guard test. The substantive change is documentation of
already-shipped behavior; the new test is its regression guard, not a new
capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
