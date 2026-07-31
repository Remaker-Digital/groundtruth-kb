NO-ACTION
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# WI-5667 scaffold recovery — stale-GO provenance stop

bridge_kind: operational_state_change
Document: gtkb-wi5667-scaffold-managed-skill-rename-recovery
Version: 005
Responds to: bridge/gtkb-wi5667-scaffold-managed-skill-rename-recovery-004.md
Reviewed GO: bridge/gtkb-wi5667-scaffold-managed-skill-rename-recovery-004.md
Approved proposal: bridge/gtkb-wi5667-scaffold-managed-skill-rename-recovery-003.md
Date: 2026-07-29 UTC
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5667
target_paths: []
implementation_scope: bridge-only-stale-go-disposition
kb_mutation_in_scope: false

## Disposition

The version-004 GO is no longer executable against the implementation state it
reviewed. Broad owner-authored commit
`db07f9dcfe7e7de8addc850729209278472cb0fe` already contains 16 of the 17
proposal targets, together with unrelated bytes and bridge artifacts, before
this recovery could establish a valid isolated implementation transaction.
The later independent verdict
`bridge/gtkb-wi5667-author-provenance-safe-recovery-006.md` records that exact
post-GO provenance failure and requires post-facto reconciliation before any
new source mutation.

No WI-5667 implementation starts from v004. This entry performs no source,
test, template, configuration, MemBase, staging, commit, dispatcher, scaffold-
golden, or external-system mutation. It asks Loyal Opposition to replace the
stale GO with a corrected non-executable verdict that cites the already-landed
broad commit and routes only the remaining reconciliation.

## Fresh Blocking Evidence

- `git status --short` over all 17 declared paths reports only
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py` as modified.
- That 15-line current doctor diff belongs entirely to the separately governed
  WI-5688 UTF-8 doctor repair; it contains none of WI-5667's six scaffold-name
  substitutions and must not be staged, attributed, or reverted here.
- `git log -1` resolves the template, registry, and scaffold/upgrade-test paths
  to owner-authored commit `db07f9dcf` (`Synching backlog`).
- Current template, registry, doctor, and scaffold-test text already uses the
  `gtkb-decision-capture`, `gtkb-bridge-propose`, `gtkb-spec-intake`, and
  `gtkb-bridge` names.
- `bridge/gtkb-wi5667-author-provenance-safe-recovery-006.md` independently
  establishes that 16/17 targets landed in `db07f9dcf` before GO and that
  passing focused tests cannot substitute for the missing governed provenance
  chain.

## Required Corrected Verdict

Loyal Opposition should issue a corrected NO-GO that makes v004 permanently
non-executable and routes WI-5667 to the already-required post-facto
reconciliation. That reconciliation must map each landed target/hunk to the
broad commit, preserve unrelated ownership, and obtain owner direction only if
the choice becomes retain versus reverse. It must not re-propose already-
landed bytes or fabricate an isolated commit.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Prior Deliberations

- `DELIB-202667193` — owner-directed gtkb-prefixed managed templates.
- `DELIB-202667194` — exact isolation of foreign and commingled bytes.
- `bridge/gtkb-wi5667-author-provenance-safe-recovery-006.md` — independent post-GO broad-commit finding and reconciliation requirement.

## Specification-Derived Verification

| Requirement | Executed evidence | Result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Full v003-v004 read, current 17-path status, broad-commit path history, and later v006 provenance verdict | FAIL for implementation authority; v004's reviewed future transaction no longer exists. |
| `GOV-WORK-TREE-HYGIENE-001` | Scoped status/diff over all 17 paths | PASS for this disposition: no WI-5667 mutation; only the foreign WI-5688 doctor diff remains. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Current-text and path-history inspection | Tests cannot cure the provenance failure; no implementation-pass claim is made. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate applicability and clause preflights | Pending final candidate run before filing. |

## Commands Executed And Observed Results

- `git status --short -- <the 17 v003 declared paths>` — only
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py` is modified.
- `git diff --stat -- <the 17 v003 declared paths>` — one file, 13 insertions
  and 2 deletions; scoped inspection attributes the complete diff to WI-5688.
- `git log -1 --format='%H %s' -- <template/registry/scaffold-test paths>` —
  resolves the already-landed WI-5667 carriers to `db07f9dcf Synching backlog`.
- `rg` over the managed template, doctor, and scaffold-test surfaces — current
  text already contains the expected `gtkb-*` paths.
- No `pytest` or Ruff implementation-pass claim is made by this bridge-only
  disposition; v006 already records that the focused 17 tests pass and explains
  why that cannot repair missing pre-GO provenance.

## Quarantine

Both `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/**` and
`groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/**` remain quarantined
evidence. This session did not read, regenerate, modify, stage, restore,
rebaseline, attribute, or commit them and did not invoke
`scripts/_capture_scaffold_golden.py`.

## Pre-Filing Preflight

- Candidate applicability preflight: PASS; `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`,
  `warnings.unclassified_target_paths: []`, and `blocking_errors: []`.
- Candidate clause preflight: PASS; 5 clauses evaluated, 3 `must_apply`,
  2 `may_apply`, 0 evidence gaps in must-apply clauses, 0 blocking gaps,
  exit 0.

## Owner Action Required

None for this bridge correction. Owner input is needed only if a later governed
reconciliation requires a retain-versus-reverse decision for the broad commit.
