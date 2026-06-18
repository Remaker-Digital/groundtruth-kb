GO

# Loyal Opposition Review - Dot-Prefixed Protected Path Normalization

bridge_kind: lo_verdict
Document: gtkb-dot-prefixed-protected-path-normalization
Version: 002
Author: Loyal Opposition (Codex automation)
Date: 2026-06-18 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-dot-prefixed-protected-path-normalization-001.md
Recommended commit type: fix

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: keep-working-lo-20260618
author_model: GPT-5 Codex
author_model_version: 2026-06-18
author_model_configuration: Keep Working LO automation; fresh session context

## Verdict

GO.

The proposal is a narrow P1 governance-gate defect repair. The live source
matches the defect claim: `scripts/implementation_start_gate.py:211` and
`scripts/protected_mutation_guard.py:74` normalize candidate paths with
`lstrip("./")`, which strips real leading dots before protected exact-path and
prefix checks run. Focused read-only probing confirmed both classifiers
currently return `False` for `.claude/hooks/h.py`, `.claude/rules/x.md`,
`.codex/gtkb-hooks/a.py`, `.github/workflows/ci.yml`,
`.claude/settings.json`, `.codex/hooks.json`, and `.env`, while continuing to
return `True` for `scripts/foo.py` and `config/x.toml`.

Prime Builder may implement only the target paths in the proposal:

- `scripts/implementation_start_gate.py`
- `scripts/protected_mutation_guard.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `platform_tests/scripts/test_protected_mutation_guard.py`

Implementation must preserve the proposal's key constraint: replace
character-set trimming with explicit leading `./` prefix removal after separator
normalization, without weakening the existing `bridge/` and diagnostic allowed
write exceptions.

## Same-Session Guard

The reviewed artifact was authored by Prime Builder session
`keep-working-20260618T0210Z`. This verdict is authored by a separate headless
Loyal Opposition automation session. The owner clarified that session-context
separation, not shared Codex harness identity alone, controls review eligibility
for separately launched headless runs.

## Applicability Preflight

- packet_hash: `sha256:01021fa5368cf7389d43ea798edf4d09f1aa8ff3e535382ddd13ef077bf64586`
- bridge_document_name: `gtkb-dot-prefixed-protected-path-normalization`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-dot-prefixed-protected-path-normalization-001.md`
- operative_file: `bridge/gtkb-dot-prefixed-protected-path-normalization-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-dot-prefixed-protected-path-normalization`
- Operative file: `bridge\gtkb-dot-prefixed-protected-path-normalization-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate when evidence is absent and no owner
waiver line is cited. No blocking gap exists for this proposal.

## Prior Deliberations

The verdict helper was run before filing. Its broad semantic candidates were
reviewed and pruned as non-controlling search noise for this narrow classifier
defect.

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` - owner authorization
  basis for `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`.
- `INTAKE-5a61f299` - claim-gated implementation-start intake; this proposal
  repairs a classifier used to decide whether protected mutations must pass
  that authorization path.
- `bridge/gtkb-governance-hook-worktree-root-resolution-*` - related prior
  path-normalization repair on the implementation-start gate. This proposal is
  narrower and fixes dot-prefixed relative paths, not worktree root resolution.
- `bridge/gtkb-protected-commit-authorization-gate-001.md` - adjacent May29
  thread that explicitly left this shared `is_protected_path` defect to
  `WI-4642`.

## Backlog And Authorization Check

Live MemBase query confirmed `WI-4642` is open, P1, defect-origin, and attached
to `PROJECT-GTKB-MAY29-HYGIENE`. Its description names the same
`lstrip("./")` defect and the same unprotected dot-prefixed surfaces.

Live project-authorization query confirmed
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` is active
for `PROJECT-GTKB-MAY29-HYGIENE`, with owner-decision deliberation
`DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` and scope "Propose
implementation for all unimplemented work items linked to
PROJECT-GTKB-MAY29-HYGIENE." No duplicate or precedence conflict blocked this
proposal; sibling work around the protected commit gate explicitly excluded
this source-gate classifier repair.

## Positive Confirmations

- Full bridge thread read: the thread has a single current `NEW` version,
  `bridge/gtkb-dot-prefixed-protected-path-normalization-001.md`, with no drift
  reported by `show_thread_bridge.py`.
- Mandatory applicability preflight passed with no missing required or advisory
  specs.
- Mandatory clause preflight passed with zero blocking gaps.
- The proposal contains concrete `Project Authorization`, `Project`, `Work
  Item`, and `target_paths` metadata.
- The proposal includes Requirement Sufficiency and a spec-derived verification
  plan.
- Current target source/test files are clean in the worktree, so this GO does
  not mask pre-existing local edits in the proposed target paths.
- `python scripts/implementation_authorization.py begin --bridge-id
  gtkb-dot-prefixed-protected-path-normalization --no-write` currently fails
  closed because no GO/work-intent claim exists, which is the expected
  pre-implementation state before this verdict is consumed by Prime Builder.

## Implementation Notes

Prime Builder should include regression assertions for exact dot-prefixed paths,
dot-prefixed prefixes, and `.env`/`.env.*` credential-path classification in
both duplicated classifiers. The implementation should also assert that
existing allowed write paths such as `bridge/` remain allowed, so the fix does
not over-tighten normal bridge filing.

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dot-prefixed-protected-path-normalization
```

Observed: preflight passed, `missing_required_specs: []`,
`missing_advisory_specs: []`.

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dot-prefixed-protected-path-normalization
```

Observed: exit 0, 4 must-apply clauses with evidence, 0 blocking gaps.

```text
rg -n 'lstrip\("\./"\)|lstrip\(' scripts/implementation_start_gate.py scripts/protected_mutation_guard.py
```

Observed: unsafe protected-path normalization at
`scripts/protected_mutation_guard.py:74`,
`scripts/implementation_start_gate.py:211`, and
`scripts/implementation_start_gate.py:222`.

```text
python -m groundtruth_kb.cli backlog list --id WI-4642 --json
python -m groundtruth_kb.cli projects authorizations PROJECT-GTKB-MAY29-HYGIENE --json --all
python -m groundtruth_kb.cli deliberations search "WI-4642 dot-prefixed protected path implementation_start_gate protected_mutation_guard" --limit 10 --json
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-dot-prefixed-protected-path-normalization --format json
python scripts/implementation_authorization.py begin --bridge-id gtkb-dot-prefixed-protected-path-normalization --no-write
python .claude/skills/verify/helpers/write_verdict.py --slug gtkb-dot-prefixed-protected-path-normalization
```

Observed: work item and PAUTH present; show-thread drift `[]`; implementation
authorization fails closed before GO/claim; verdict helper returned broad
semantic candidates that were reviewed and pruned.

Read-only classifier probe:

```text
implementation_start_gate
  .claude/hooks/h.py: False
  .claude/rules/x.md: False
  .codex/gtkb-hooks/a.py: False
  .github/workflows/ci.yml: False
  .claude/settings.json: False
  .codex/hooks.json: False
  .env: False
  scripts/foo.py: True
  config/x.toml: True
  bridge/foo-001.md: False
protected_mutation_guard
  .claude/hooks/h.py: False
  .claude/rules/x.md: False
  .codex/gtkb-hooks/a.py: False
  .github/workflows/ci.yml: False
  .claude/settings.json: False
  .codex/hooks.json: False
  .env: False
  scripts/foo.py: True
  config/x.toml: True
  bridge/foo-001.md: False
```

## Owner Action Required

None.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
