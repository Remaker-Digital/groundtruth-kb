NO-GO

bridge_kind: lo_verdict
Document: gtkb-gov-08-permitted-markdown-amendment-scoping
Version: 002
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-28 UTC
Responds to: `bridge/gtkb-gov-08-permitted-markdown-amendment-scoping-001.md`
Verdict: NO-GO

# Loyal Opposition Review - GOV-08 Permitted Markdown Amendment Scoping

## Verdict

NO-GO for revision. The proposal addresses a real governance gap around `bridge/INDEX.md` and narrows markdown memory scope in the right general direction, but it needs two corrections before GO:

- Add the lifecycle-trigger DCL that the applicability preflight surfaced.
- Reconcile the proposed `MEMORY.md at project root` replacement text with GT-KB's actual `memory/MEMORY.md` harness-memory profile and the generic adopter-project root convention.

## Prior Deliberations

Deliberation Archive search was run before review:

```text
python -m groundtruth_kb deliberations search "GOV 08 permitted markdown amendment scoping narrative artifact markdown governance" --limit 8
```

Relevant returned records included:

- `DELIB-1582` - backlog work list retirement directive, relevant precedent for retiring historical markdown/list surfaces.
- `DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE` - standing self-improvement directive.
- `DELIB-S337-CODEX-HOOK-PARITY...` - adjacent harness/governance context.
- `DELIB-1563`, `DELIB-1570`, and `DELIB-1573` - historical Deliberation Archive and read-surface context.

No returned deliberation authorized omitting lifecycle verification for a GOV supersession, or relocating GT-KB's MEMORY surface without reconciling the harness-memory profile.

## Findings

### P2-001 - Lifecycle-trigger DCL is omitted from a GOV supersession and markdown-retirement proposal

Observation: The proposal would retire `GOV-08`, create a replacement GOV row, and later migrate topic-specific markdown files into governed storage. That is lifecycle work, but the proposal omits `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` from both the specification links and the spec-derived verification plan.

Evidence:

- `bridge/gtkb-gov-08-permitted-markdown-amendment-scoping-001.md:155-165` specifies retiring `GOV-08`, setting `superseded_by`, and inserting a replacement GOV.
- `bridge/gtkb-gov-08-permitted-markdown-amendment-scoping-001.md:173-251` lists specification links without `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.
- `bridge/gtkb-gov-08-permitted-markdown-amendment-scoping-001.md:275-286` maps specification-derived verification without a row for `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.
- `bridge/gtkb-gov-08-permitted-markdown-amendment-scoping-001.md:320-334` describes follow-on MemBase changes and lifecycle state for the retired and replacement GOV rows.
- Applicability preflight reports `missing_advisory_specs: ["DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]`, triggered by lifecycle terms including `candidate`, `deferred`, `superseded`, `verified`, and `retired`.

Risk/impact: A follow-on mutation slice could change GOV lifecycle state and migrate markdown topic files without an explicit check that retirement, successor links, and durable artifact state are preserved consistently.

Required revision: Add `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` to `## Specification Links` and `## Specification-Derived Verification Plan`. The verification plan should require that `GOV-08` is retired with a correct `superseded_by` successor, the replacement GOV is current, markdown-topic migrations have explicit lifecycle outcomes, and no retired markdown class remains ambiguous.

### P2-002 - Replacement text misstates the GT-KB MEMORY.md location

Observation: The proposed replacement text says `MEMORY.md` is at the project root. In the GT-KB checkout, the active harness-memory profile uses `memory/MEMORY.md`; root `MEMORY.md` is the standard scaffold/adopter convention, not the GT-KB local surface.

Evidence:

- `bridge/gtkb-gov-08-permitted-markdown-amendment-scoping-001.md:127-132` proposes allowlist text for `CLAUDE.md`, `bridge/INDEX.md`, and `MEMORY.md` "at project root".
- `AGENTS.md:12` states that in the GT-KB checkout `MEMORY.md` lives at `memory/MEMORY.md` under the harness-memory profile, while standard scaffolded adopter projects use project-root `MEMORY.md`.
- `.claude/rules/operating-model.md:83` distinguishes `memory/MEMORY.md` from MemBase and states it is session state, not canonical knowledge.

Risk/impact: If the replacement GOV is intended to govern GT-KB locally, the root-path wording is wrong. If it is intended to govern generic adopter scaffolds, the GT-KB harness-memory exception needs to be explicit. Without that distinction, future doctor checks and governance reviews can disagree about whether `memory/MEMORY.md` is allowed, disallowed, or merely exempt from a root-file content check.

Required revision: State whether the amended GOV text is GT-KB-local, generic scaffold/adopter guidance, or both. If both, explicitly encode the standard scaffold root `MEMORY.md` convention and the GT-KB harness-memory exception: `memory/MEMORY.md` is the GT-KB operational notepad, while root `MEMORY.md` remains the standard scaffold/adopter location.

## Applicability Preflight

- packet_hash: `sha256:df4a38fb2a4c1d300dd7a70defce7f465353f384cb4e119ae55f23f6be5ef6e9`
- content_file: `bridge/gtkb-gov-08-permitted-markdown-amendment-scoping-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: [`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`]

| Spec | Severity | Cited |
|------|----------|-------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | yes |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | no |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | yes |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | yes |
| `GOV-BASELINE-GOVERNANCE-CONTRACT-001` | blocking | yes |
| `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` | blocking | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | yes |

## Clause Applicability

- Bridge id: `gtkb-gov-08-permitted-markdown-amendment-scoping`
- Operative file: `bridge\gtkb-gov-08-permitted-markdown-amendment-scoping-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0

| Clause | Spec | Applicability | Evidence found | Enforcement |
|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking |

## Verification Performed

- Read live `bridge/INDEX.md`; latest status for `gtkb-gov-08-permitted-markdown-amendment-scoping` was `NEW: bridge/gtkb-gov-08-permitted-markdown-amendment-scoping-001.md`.
- Read the full proposal file.
- Ran `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-08-permitted-markdown-amendment-scoping`.
- Ran `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-08-permitted-markdown-amendment-scoping`.
- Ran the Deliberation Archive search quoted above.
- Checked GT-KB MEMORY.md terminology in `AGENTS.md` and `.claude/rules/operating-model.md`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
