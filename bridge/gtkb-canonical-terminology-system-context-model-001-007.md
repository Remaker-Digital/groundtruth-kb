NEW

# Implementation Report — GTKB-CANONICAL-TERMINOLOGY-SYSTEM-CONTEXT-MODEL-001 (Phase 1)

**Author:** Prime Builder (Claude, harness B)
**Filed:** 2026-05-08
**Bridge thread:** `gtkb-canonical-terminology-system-context-model-001`
**Prior GO:** `bridge/gtkb-canonical-terminology-system-context-model-001-006.md` (on `-005` REVISED)
**Implementation status:** Phase 1 complete; awaiting Loyal Opposition VERIFIED.

## Claim

Phase 1 of `GTKB-CANONICAL-TERMINOLOGY-SYSTEM-CONTEXT-MODEL-001` is implemented per `-005`'s scope:

- `canonical_terms` table added to MemBase schema (append-only, versioned, with check constraints) — `groundtruth-kb/src/groundtruth_kb/db.py`.
- `groundtruth_kb.canonical_terms` module exposes `insert_term`, `get_term`, `list_terms`, `list_versions`, `find_collisions`, `parse_markdown_glossary`, `parity_check`, `seed_from_markdown` — implementing the unified text-surface collision-key model and the idempotent append-only seed.
- `_check_canonical_terms_registry()` extends the project doctor; `gt project doctor` surfaces parity drift and collision findings natively.
- `gt canonical-terms` CLI subcommand group: `seed --dry-run`/`--apply`, `list`, `history`.
- Markdown content is **unchanged** (T-no-markdown-edit ✓): `.claude/rules/canonical-terminology.md` retains its Phase-1-authoritative role.
- Live seed against `.claude/rules/canonical-terminology.md` populates 27 platform_core terms; second `--apply` produces 27 `unchanged` operations (idempotent).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge proposals/reports are governed through `bridge/INDEX.md`; this report is delivered via that protocol.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation report carries forward the proposal's spec links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived tests executed against the implementation; mapping below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application files under `applications/`; this implementation touches platform code only (no `applications/Agent_Red/` content; verified by `git diff --stat`).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifact-oriented governance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — durable artifacts, lifecycle states, traceable evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — append-only versioning + supersede-via-retire.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — owner-visible confirmation for chat-derived specs.
- `SPEC-TERMINOLOGY-DOCTOR-CHECK` — existing doctor-check; the new `_check_canonical_terms_registry` is added as an adjacent check, not a replacement.
- `SPEC-TERMINOLOGY-PROFILE-MATRIX` — profile-aware required-term spec; unchanged.
- `.claude/rules/canonical-terminology.md` — markdown source-of-truth (Phase-1-authoritative; **no content changes** in this implementation).
- `.claude/rules/canonical-terminology.toml` — profile config (unchanged).
- `.claude/rules/operating-model.md` §2 — canonical-terms vocabulary baseline.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol root contract.
- `.claude/rules/codex-review-gate.md` — review-gate constraints.
- `.claude/rules/project-root-boundary.md` — root-boundary contract.
- `bridge/gtkb-canonical-terminology-system-context-model-001-005.md` — proposal addressed by this implementation.
- `bridge/gtkb-canonical-terminology-system-context-model-001-006.md` — Codex GO authorizing this implementation.

## Owner Decisions / Input

The four 2026-05-07 owner agreements (advisory `-001` source) are preserved unchanged as the scope basis. The S336 owner directive ("Please proceed with Item 1's Phase 1 implementation") authorized this round under the standing "work independently" scope. No new owner decision was required to complete Phase 1.

## Files Changed

### Schema

- `groundtruth-kb/src/groundtruth_kb/db.py` — added `canonical_terms` table CREATE, three indexes, and `current_canonical_terms` view to `SCHEMA_SQL`. Existing tables and views are unchanged.

### Package code

- `groundtruth-kb/src/groundtruth_kb/canonical_terms.py` (new, 631 lines, ruff-formatted) — module exposing the public API plus internal helpers `_normalized_text_keys`, `_text_surface_origin`, `_slugify`, `_extract_definition`, `_markdown_hash`. The collision detector uses the unified `("text", value)` namespace per `-005`'s F1 fix; lexical surfaces include `canonical_term`, `accepted_synonyms`, `discouraged_synonyms`, and `forbidden_uses`; field-of-origin metadata is preserved for the classifier.
- `groundtruth-kb/src/groundtruth_kb/cli.py` — added `gt canonical-terms` group with `seed`, `list`, `history` subcommands.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — added `_check_canonical_terms_registry()` and registered it in `run_doctor()` immediately after `_check_canonical_terminology()`. The existing `_check_canonical_terminology()` is unchanged; the new registry check is additive.

### Tests

- `groundtruth-kb/tests/test_canonical_terms_schema.py` (new, 13 tests) — schema/round-trip/append-only/constraint/UNIQUE/retire-filter coverage.
- `groundtruth-kb/tests/test_canonical_terms_collisions.py` (new, 10 tests) — covers T-collision-1 through T-collision-5 plus negative cases and case/whitespace normalization.
- `groundtruth-kb/tests/test_canonical_terms_seed.py` (new, 8 tests) — covers T-seed-1, T-seed-2, T-seed-3, T-population-1; includes parser-behavior, dry-run vs apply parity, supersede-via-retire, and revival-after-retire paths.
- `tests/scripts/test_check_canonical_terminology_doctor_integration.py` (new, 9 tests) — covers T-doctor-1, T-doctor-2 integration paths plus skip cases (table not provisioned / db not present / glossary not present).

### Markdown (T-no-markdown-edit)

- `.claude/rules/canonical-terminology.md` — **content unchanged**; verified by `git diff --stat .claude/rules/canonical-terminology.md` returning empty output.

## Spec-To-Test Mapping

| Test ID | Spec/Requirement | Test location | Result |
|---|---|---|---|
| T-bridge-1 | `GOV-FILE-BRIDGE-AUTHORITY-001` | INDEX entry | Present |
| T-spec-1 | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-terminology-system-context-model-001` | preflight_passed: true |
| T-spec-2 | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report | Section present |
| T-schema-1 | DDL constant matches schema | `test_schema_ddl_constant_matches_table_ddl` | PASS |
| T-schema-2 | Append-only versioning | `test_append_only_two_versions`, `test_append_only_view_returns_only_latest` | PASS |
| T-schema-3 | authority_level constraint | `test_authority_level_constraint_blocks_invalid`, `test_authority_level_db_constraint_blocks_raw_invalid` | PASS |
| T-schema-4 | lifecycle_status constraint | `test_lifecycle_status_constraint_blocks_invalid`, `test_lifecycle_status_db_constraint_blocks_raw_invalid` | PASS |
| T-seed-1 | Idempotent seed | `test_seed_idempotent`; live `gt canonical-terms seed --apply` repeated produces all `unchanged` | PASS |
| T-seed-2 | Dry-run vs apply parity | `test_seed_dry_run_and_apply_produce_same_operations` | PASS |
| T-seed-3 | Supersede via retire | `test_seed_supersede_via_retire`, `test_seed_revival_after_retire` | PASS |
| T-collision-1 | id collision across authority levels = ERROR | `test_id_collision_across_authority_levels_errors` | PASS |
| T-collision-2 | display-term collision across authority levels = ERROR | `test_display_term_collision_across_authority_levels_errors` | PASS |
| T-collision-3 | accepted vs discouraged cross-field = WARN | `test_cross_field_text_reuse_accepted_vs_discouraged_warns` | PASS (executable for the first time per `-005`'s unified-key model) |
| T-collision-4 | accepted vs forbidden cross-field = WARN | `test_cross_field_text_reuse_accepted_vs_forbidden_warns` | PASS |
| T-collision-5 | platform-core vs adopter-extension synonym overlap = ERROR | `test_cross_authority_synonym_overlap_errors` | PASS |
| T-doctor-1 | Doctor integration surfaces collisions | `test_pass_when_seeded_clean`, `test_fail_on_platform_core_redefinition`, `test_warning_on_cross_field_text_reuse` | PASS |
| T-doctor-2 | Doctor parity check | `test_warning_on_parity_missing_in_table`, `test_fail_on_parity_missing_in_markdown` | PASS |
| T-population-1 | ≥ 26 platform_core terms after seed | `test_seed_against_live_glossary`; live `gt canonical-terms list --authority-level platform_core` returns 27 | PASS |
| T-no-markdown-edit | `.claude/rules/canonical-terminology.md` content unchanged | `git diff --stat .claude/rules/canonical-terminology.md` | PASS (empty diff) |
| T-isolation-1 | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All Phase-1 changes touch only `groundtruth-kb/`, `tests/scripts/`; no `applications/Agent_Red/` paths | PASS |
| T-secrets-1 | Credential safety | `python -m groundtruth_kb secrets scan --paths <8 changed files> --json --fail-on=` returns `finding_count: 0` | PASS |

## Verification Commands and Results

### Test suites

```text
python -m pytest groundtruth-kb/tests/test_canonical_terms_schema.py groundtruth-kb/tests/test_canonical_terms_collisions.py groundtruth-kb/tests/test_canonical_terms_seed.py -q --tb=line
  -> 31 passed, 1 warning in 2.66s

python -m pytest tests/scripts/test_check_canonical_terminology_doctor_integration.py -q --tb=line
  -> 9 passed, 1 warning in 1.83s
```

(Run separately because the two trees have sibling `tests/conftest.py` files; pytest's default rootdir discovery cannot collect both in one invocation.)

### Live seed flow against `.claude/rules/canonical-terminology.md`

Executed against a scratch copy of `groundtruth.db` to avoid mutating the live KB during this verification:

```text
cp groundtruth.db /tmp/canonical-terms-seed-trial.db

GT_DB_PATH=/tmp/canonical-terms-seed-trial.db python -m groundtruth_kb canonical-terms seed --dry-run
  -> canonical-terms seed [DRY-RUN]
     source: .claude/rules/canonical-terminology.md
     hash:   sha256:e9ed5e69b2959bd0156154d7fad7d9522d03e6437c9ff81aaacdde741bc480df
     summary: insert=27

GT_DB_PATH=/tmp/canonical-terms-seed-trial.db python -m groundtruth_kb canonical-terms seed --apply
  -> summary: insert=27

GT_DB_PATH=/tmp/canonical-terms-seed-trial.db python -m groundtruth_kb canonical-terms seed --apply
  -> summary: unchanged=27   (T-seed-1 idempotency verified)

GT_DB_PATH=/tmp/canonical-terms-seed-trial.db python -m groundtruth_kb canonical-terms list --authority-level platform_core --json | python -c "import json, sys; print(len(json.load(sys.stdin)))"
  -> 27   (T-population-1: ≥ 26 verified)
```

The scratch DB was removed after the verification (`rm /tmp/canonical-terms-seed-trial.db`).

The live `groundtruth.db` was **not** mutated by this implementation. The seed applies against any GT-KB project's MemBase via the standard `gt canonical-terms seed --apply` path; project-by-project seed runs are governed by their respective bridge approvals.

### Lint / format / secrets / markdown invariance

```text
python -m ruff check groundtruth-kb/src/groundtruth_kb/canonical_terms.py groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_canonical_terms_schema.py groundtruth-kb/tests/test_canonical_terms_collisions.py groundtruth-kb/tests/test_canonical_terms_seed.py tests/scripts/test_check_canonical_terminology_doctor_integration.py
  -> All checks passed!

python -m ruff format --check groundtruth-kb/src/groundtruth_kb/canonical_terms.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_canonical_terms_schema.py groundtruth-kb/tests/test_canonical_terms_collisions.py groundtruth-kb/tests/test_canonical_terms_seed.py tests/scripts/test_check_canonical_terminology_doctor_integration.py
  -> 7 files already formatted

python -m groundtruth_kb secrets scan --paths <same 8 files> --json --fail-on=
  -> finding_count: 0; paths_scanned: 8

git diff --stat .claude/rules/canonical-terminology.md
  -> (empty output — content unchanged)
```

### CLI smoke test

```text
python -m groundtruth_kb canonical-terms --help
  -> Lists `seed`, `list`, `history` subcommands.
```

## Notable Implementation Details

### Markdown parser dedup (slug collisions)

`.claude/rules/canonical-terminology.md` includes two distinct entries that slug to the same id (e.g., "GroundTruth KB" vs "GroundTruth-KB" both produce `GROUNDTRUTH_KB` after slugification). To preserve append-only idempotency, `parse_markdown_glossary` deduplicates by suffixing later occurrences (`GROUNDTRUTH_KB_2`, etc.) so each markdown entry maps to a stable unique id across runs. Without this, repeated seed-apply runs produced one spurious `update` op per duplicate-slug pair.

This dedup is internal to the parser and produces stable ids; it does not modify the markdown source or the headings displayed to users.

### Authority-model preservation

The Phase 1 contract per Codex `-002` F1 (acknowledged-resolved in `-006`) is: markdown stays canonical for fresh-agent consumption; the table is a backing registry. This implementation respects that:

- No "table is canonical" edit was added to the markdown.
- `.claude/rules/prime-builder-role.md`, `.claude/rules/loyal-opposition.md`, `.claude/rules/canonical-terminology.toml`, and `groundtruth-kb/templates/rules/canonical-terminology-policy.toml` are untouched.
- The new `_check_canonical_terms_registry()` doctor check passes when the table is empty (Phase-1-authoritative-only mode) and only blocks on parity/collision findings once the table has been populated.

### Append-only data semantics (per Codex `-002` F4)

- `seed_from_markdown` never DELETEs; supersede uses `lifecycle_status='retired'` (an appended row).
- `gt canonical-terms history <id>` exposes the full audit trail.
- The live `groundtruth.db` was not mutated by this verification; the scratch-DB pattern (`cp groundtruth.db /tmp/...`) was used instead.

## Conditions From `-006` GO Discharged

- ✅ T-collision-3 executable and passing.
- ✅ T-collision-4 executable and passing.
- ✅ T-collision-5 platform-core redefinition path passing.
- ✅ T-no-markdown-edit: empty diff for `.claude/rules/canonical-terminology.md`.
- ✅ T-secrets-1: `finding_count: 0` over all 8 changed files.

## Recommended Commit Type

`feat`. The change adds a new functional component to GT-KB (Canonical Terminology System backing registry: schema, module API, CLI subcommand group, doctor integration). 40 new tests are added; 0 existing tests are modified. No behavior change to existing surfaces. Per the Conventional Commits Type Discipline section of `.claude/rules/file-bridge-protocol.md`, `feat` is the appropriate type for a net-new module + CLI surface + doctor check.

## Out Of Scope (carried forward from `-005`)

- Phase 2: Agent Operating Context retrieval/startup wiring — separate bridge thread.
- Phase 3: Bounded Knowledge Principle implementation — separate bridge thread.
- Phase 4: Junior-developer / fresh-agent documentation — separate bridge thread.
- Live seed of GT-KB's own `groundtruth.db` — owner can run `gt canonical-terms seed --apply` at their convenience under standard governance.
- Adopter / project-local term seeding — adopter projects own this in their own bridge threads.

## Residual Risk

- Two markdown entries colliding on slug ("GroundTruth KB" vs "GroundTruth-KB") get suffixed to `GROUNDTRUTH_KB_2`. This is a pragmatic dedup; if owner prefers an explicit alternative slug strategy (e.g., distinguishing alias forms), Phase 2's terminology design can adopt one. The current behavior is stable and idempotent.
- Doctor parity-check classification of `missing_in_markdown` as ERROR is intentionally strict: a `platform_core` row in the table without a markdown counterpart implies someone hand-wrote the table. Test `test_fail_on_parity_missing_in_markdown` documents this. If the strictness needs softening, that's a Phase-2-or-later refinement.

## Requested Loyal Opposition Review

Review this implementation report for verification. Specific question for Codex: with all 5 GO conditions discharged (T-collision-3/4/5 executable+passing, T-no-markdown-edit, T-secrets-1), 40 tests passing across 4 test files, ruff clean, secrets-scan clean, and the live seed flow verified for idempotency on a scratch DB, does Phase 1 of `gtkb-canonical-terminology-system-context-model-001` qualify for `VERIFIED`?
