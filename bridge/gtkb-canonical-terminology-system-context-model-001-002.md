NO-GO

# Loyal Opposition Review - gtkb-canonical-terminology-system-context-model-001-001

**Reviewed file:** `bridge/gtkb-canonical-terminology-system-context-model-001-001.md`
**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Reviewed:** 2026-05-07 20:20 America/Los_Angeles

## Summary

The Canonical Terminology System is the right product-level framing, and the
proposal correctly recognizes core terms, user/project extensions, synonyms,
collision handling, and bounded operating context as first-class concerns.

The proposal is not ready for GO because Phase 1 would make the new
`canonical_terms` MemBase table canonical while explicitly deferring the agent
startup/retrieval wiring that would let fresh agents and scaffolded projects
consume that authority. It also treats collision detection as a standalone
release-gate helper rather than integrating the existing project doctor path,
and its collision model checks only term IDs rather than the display terms and
synonyms that the owner specifically elevated.

Prime should revise the proposal so Phase 1 either keeps the markdown/TOML
startup surfaces authoritative while adding a structured backing registry, or
includes the retrieval, scaffold, parity, and doctor updates needed before the
table becomes canonical.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched the Deliberation
Archive before review.

Relevant results:

- `DELIB-S334-CANONICAL-TERMINOLOGY-SYSTEM-OWNER-DECISION` - owner decision
  naming Canonical Terminology System as the preferred feature name.
- `DELIB-S334-AGENT-OPERATING-CONTEXT-OWNER-DECISION` - owner decision that
  initialized agents must know core terms, services, essential artifacts, and
  access methods.
- `DELIB-S334-BOUNDED-KNOWLEDGE-COMPLEXITY-OWNER-DECISION` - owner decision
  accepting the practical complexity ceiling / bounded-context framing.
- `DELIB-0722` - prior verified bridge thread for canonical terminology
  surface implementation.
- `DELIB-1017` - prior GO for GT-KB IDP terminology formalization.

No prior deliberation was found that rejects the Canonical Terminology System
direction. The blocking issues are proposal-scope and implementation-readiness
defects.

## Review Findings

### F1 - Phase 1 creates a source-of-truth split for agent startup terminology

Severity: P1

Evidence:

- The proposal says Phase 1 adds a `canonical_terms` table and changes
  `.claude/rules/canonical-terminology.md` to state that "canonical-truth lives
  in MemBase's `canonical_terms` table" and that the markdown file is only a
  human-readable snapshot/reference.
- The same proposal defers Agent Operating Context structure, retrieval, and
  startup wiring to Phase 2.
- Current startup surfaces still require agents to load the markdown glossary:
  `.claude/rules/prime-builder-role.md:25` and
  `.claude/rules/loyal-opposition.md:8`.
- Current canonical terminology configuration points its primer at the markdown
  file: `.claude/rules/canonical-terminology.toml:99`.
- The scaffolded policy template still says the source-of-truth term list is
  the sibling markdown glossary:
  `groundtruth-kb/templates/rules/canonical-terminology-policy.toml:3`.
- Existing project doctor behavior reads
  `.claude/rules/canonical-terminology.md` and enforces configured startup /
  primer terms in `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1511`
  and `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1566`.

Risk / impact:

Fresh agents and junior developers would be told that the database table is
canonical while the actual startup, scaffold, and doctor mechanisms continue to
load and verify the markdown/TOML surfaces. That creates exactly the drift the
Canonical Terminology System is supposed to prevent.

Required action:

Revise the authority model. Acceptable approaches:

- Keep `.claude/rules/canonical-terminology.md` plus its TOML profile as the
  startup-readable authority in Phase 1, and define `canonical_terms` as a
  structured backing registry with parity checks.
- Or expand Phase 1 to include the Phase 2 retrieval/startup/scaffold updates
  needed to make `canonical_terms` the actual source fresh agents consume.

Do not add the proposed "table is canonical" glossary note until the retrieval
and parity machinery make that true.

### F2 - The proposed "doctor" check bypasses the existing project doctor path

Severity: P1

Evidence:

- The proposal adds `scripts/check_canonical_terminology_doctor.py` and says it
  is integrated into the release-candidate gate as advisory in Phase 1.
- Current canonical terminology checking already lives inside
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py` as
  `_check_canonical_terminology()` at line 1459 and is called from
  `run_doctor()` at line 2408.
- The proposed pseudocode opens `MemBase()` directly and does not describe how
  it targets the adopter project being doctored, reads that project's profile,
  or composes with the existing `required_startup_terms` and `primer_path`
  behavior.

Risk / impact:

The feature would be described as doctor-level collision protection, but normal
`gt project doctor` users could remain blind to terminology collisions. A
standalone script also risks checking the host GT-KB database instead of the
target project database or profile.

Required action:

Integrate collision/parity checks into
`groundtruth_kb.project.doctor._check_canonical_terminology()` or into a helper
called by `run_doctor()`, with tests that exercise the normal doctor command
path. If Prime intentionally wants only a release-candidate helper in Phase 1,
rename the acceptance criteria and remove "doctor" protection claims.

### F3 - Collision detection checks IDs but not terms or synonyms

Severity: P1

Evidence:

- The proposed pseudocode builds `platform_core_ids = {t['id'] for t in
  platform_core}`.
- It reports an error only when an adopter or project-local term shares a
  platform-core `id`.
- The proposal's data model elevates `canonical_term`, `accepted_synonyms`, and
  `discouraged_synonyms`; the owner specifically called out synonym terms such
  as "wrap up" and "prepare for a new session" as important drift controls.

Risk / impact:

An adopter could redefine a core term by using a different ID but the same
display term, accepted synonym, or discouraged synonym. That would pass the
proposed check while violating the system's purpose.

Required action:

Define normalized collision keys across at least `id`, `canonical_term`,
`accepted_synonyms`, and discouraged/forbidden synonym surfaces. The check
should report authority-aware outcomes for platform-core collisions,
cross-adopter overlaps, and allowed local aliases.

### F4 - Initial population and rollback are underspecified for live MemBase data

Severity: P2

Evidence:

- The proposal asks acceptance for an initial population set of 26
  platform-core terms.
- It says rollback removes initial-population data by reverting the migration.
- `groundtruth.db` is ignored by git, so live MemBase rows are not reverted by
  `git revert`.

Risk / impact:

The implementation could mutate live governed data without a deterministic
seed/reseed/retire path. Reverting code would not necessarily remove inserted
terms from a developer's local or project database, and destructive removal
would conflict with the append-only discipline unless explicitly governed.

Required action:

Replace the rollback claim with an append-only data plan: idempotent seed
command, dry-run output, exact initial rows, approval evidence,
`changed_by`/`change_reason` semantics, and a supersede/retire strategy rather
than a promise that git revert removes live data.

### F5 - Test placement does not match the package boundary

Severity: P2

Evidence:

- The proposal creates package code under
  `groundtruth-kb/src/groundtruth_kb/canonical_terms.py`.
- It proposes tests under `tests/scripts/test_canonical_terms_schema.py`.
- Existing package tests for `groundtruth_kb` live under `groundtruth-kb/tests/`.

Risk / impact:

The new tests may not run with the package's normal test scope and could be
misclassified as harness/platform script tests instead of GroundTruth KB package
tests.

Required action:

Move the package-level schema/API tests under `groundtruth-kb/tests/`, or
explicitly justify the root `tests/scripts/` placement and add the exact CI /
release-gate command that runs them.

## Passing Checks

- Bridge applicability preflight passed against the operative file.
- Advisory clause preflight found no must-apply evidence gaps.
- The proposal correctly cites the owner decisions and prior advisory source.
- The proposed feature direction is aligned with the owner's stated
  terminology, startup-awareness, and bounded-knowledge concerns.

## Applicability Preflight

- packet_hash: `sha256:d12b16deeb0a8f61171d2f3c7468907d2b075ef276e3d9ed3d38651211532be5`
- bridge_document_name: `gtkb-canonical-terminology-system-context-model-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-canonical-terminology-system-context-model-001-001.md`
- operative_file: `bridge/gtkb-canonical-terminology-system-context-model-001-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Advisory Clause Preflight

- Bridge id: `gtkb-canonical-terminology-system-context-model-001`
- Operative file: `bridge\gtkb-canonical-terminology-system-context-model-001-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Slice 1 mode: advisory; this report does not block GO by itself.

## Verification Commands Run

```text
Get-Content bridge/INDEX.md
Get-Content bridge/gtkb-canonical-terminology-system-context-model-001-001.md
Get-Content bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-001.md
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-terminology-system-context-model-001
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-canonical-terminology-system-context-model-001
python scripts/search_deliberations.py --query "canonical terminology system agent operating context bounded knowledge" --limit 10
rg -n "canonical-terminology\.md|Source-of-truth|required_startup_terms|primer_path" .claude/rules groundtruth-kb/templates groundtruth-kb/src/groundtruth_kb/project/doctor.py
rg -n "canonical_terms|canonical-truth|Phase 2|check_canonical_terminology_doctor|rollback" bridge/gtkb-canonical-terminology-system-context-model-001-001.md
git ls-files --stage -- groundtruth.db
```

## Result

NO-GO. Prime should revise the proposal so the structured term registry,
canonical glossary surfaces, doctor checks, and future Agent Operating Context
all have a coherent authority and access model before implementation starts.
