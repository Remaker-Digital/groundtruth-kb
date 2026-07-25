REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; Codex Desktop interactive Prime Builder; role_source=transcript_init_keyword
author_metadata_source: explicit current-session filing metadata and live draft work-intent claim

# Revised Stage A Proposal: Advance semantic reference and generator ownership closure

bridge_kind: prime_proposal
Document: gtkb-file-move-rename-canonicalization-v4
Version: 005
Responds to: bridge/gtkb-file-move-rename-canonicalization-v4-004.md
Revises implementation report: bridge/gtkb-file-move-rename-canonicalization-v4-003.md
Approved Stage A proposal: bridge/gtkb-file-move-rename-canonicalization-v4-001.md
Date: 2026-07-22 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

target_paths: ["scripts/gtkb_file_reference_migration.py", "scripts/generate_rule_compatibility_projections.py", "scripts/generate_cursor_skill_adapters.py", "config/file-reference-migration/wi5640.toml", "platform_tests/scripts/test_gtkb_file_reference_migration.py", "platform_tests/scripts/test_generate_rule_compatibility_projections.py", "platform_tests/scripts/test_generate_cursor_skill_adapters.py", "platform_tests/fixtures/file_reference_migration/**", ".gtkb-state/file-reference-migration/wi5640/**"]

implementation_scope: source | test | configuration | runtime_state | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

This revision accepts all five findings in
`bridge/gtkb-file-move-rename-canonicalization-v4-004.md`. It seeks a fresh GO
for a second Stage A correction pass limited to the same nine implementation
targets. This pass will close findings F1 through F3 in the engine and model the
interfaces for F4, but it does not claim that planner code alone repairs the
live structured/domain objects. F4 requires separately reviewed target authority
and F5 remains a separate WI-5648 dependency. Both remain hard blockers to
terminal Stage A verification and the exact-plan child.

The retained-source and stage boundaries do not change. Stage A may observe the
entire `E:\GT-KB` root and may simulate exact consumer postimages and domain
operations, but it may not mutate any live repository consumer, SQLite database,
dashboard projection, old source, Git index, dispatcher surface, or file outside
the nine declared implementation targets. Stage B remains impossible until a
separate exact-plan child receives independent GO and its own claim and packet.

## First-Line Role Eligibility Check

PASS. This session context
`019f863a-acd3-7320-80c0-1831f0936cc0` is Prime Builder by the controlling
transcript role assignment. `REVISED` is a Prime Builder status. The latest
strict v4 state is `NO-GO` at v4-004, this draft directly responds to that
immediate predecessor, and a draft work-intent claim was acquired before
substantive drafting.

## Finding Responses

### F1: Typed live-reference classification

Accepted. The existing scanner correctly fails closed but overstates
load-bearing evidence because 1,377 of 1,666 unresolved records are unqualified
bare filenames.

The revised engine will emit source spans and one typed syntactic context for
each occurrence:

1. `executable_path` for component-resolved loader/config/subprocess/import path
   values;
2. `python_path_expression` for statically evaluable `Path`, `/`, `joinpath`,
   `os.path.join`, and adjacent literal constructions;
3. `powershell_path_expression` for statically evaluable `Join-Path`, `-f`,
   interpolation, array join, and path-provider expressions;
4. `structured_scalar` for JSON, TOML, YAML, and configured SQLite text nodes;
5. `markdown_target` for link/image/autolink destinations, separate from prose
   and fenced/inline code;
6. `test_expectation` for test fixture and assertion literals whose old spelling
   is either the behavior under test or an intended expected canonical value;
7. `compatibility_reference` for retained native loader/projection contracts;
8. `diagnostic_prose` and `historical_quotation` for nonexecuting narrative
   evidence; and
9. `ambiguous_basename` when no deterministic loader root and syntactic role can
   be proved.

Each reference record will bind `span_start`, `span_end`, `semantic_type`,
`parser`, `semantic_locator`, and `classification_reason`. Discovery remains a
lexical superset: every basename span must classify exactly once. Parser failure,
overlapping classifications, or a non-unique mapping remains blocking. This is
especially important for `sot-read-discipline.py`, which exists in both hook and
rule mapping families and cannot be selected from basename alone.

Only typed load-bearing spans enter automatic postimage rendering. Rendering
will consume the scanner's collision-checked, non-overlapping spans rather than
rerunning a looser regular expression. Directory aliases may have path suffixes;
JSON-escaped delimiters terminate a token correctly. An ambiguous basename
remains a blocker as `AMBIGUOUS_BASENAME_REFERENCE`; it is never silently
treated as prose and never globally replaced.

Every non-load-bearing exception will bind path, typed context, source location,
token, mapping/alias id, disposition, and preimage hash. A hash mismatch or
location disappearance invalidates the exception.

### F2: Set-equal inferred-alias disposition ledger

Accepted. `wi5640.toml` will declare one exact ledger row for every inferred
candidate id using only `candidate_id`, an identity digest over the inferred
id/source/canonical/inference-basis tuple, and one decision:

- `rewrite-if-present`
- `assert-absent`

The source and canonical literals will not be repeated in the policy row,
because the full-root scanner observes the policy itself and such literals
would make every absence assertion self-invalidating. A separate class-to-
occurrence-disposition table will map mutable/canonical text to `rewrite`,
generated text and native compatibility projections to
`generator-regenerate`, audit/input/worktree evidence to `immutable-audit`,
runtime and retained sources to `retained-compatibility`, and application
boundaries to `application-boundary`.

Startup validation will require casefold/NFC set equality between the 43
deterministically inferred candidates and the policy ledger. Duplicate,
missing, extra, identity-drifted, or ambiguous rows block preflight.
`assert-absent` is valid only when the full observation contains zero matching
occurrences; any occurrence turns it into a blocker. Every occurrence of the 24
currently live candidate families must therefore receive a reviewed rewrite or
typed exception disposition, while the 19 currently absent families are
absence assertions rather than implicit skips.

The 19 observed absence decisions are the `CAND-GTKB_` candidates for ADR,
ASSERT, BATCH, BENCHMARKS, BRIDGE_CONFIG, GRILL_ME_FOR_CLARIFICATION,
HYGIENE_INVESTIGATION, HYGIENE_RECLAIM, HYGIENE_SWEEP,
LO_HYGIENE_ASSESSMENT, LOYAL_OPPOSITION_REPORT, PROMOTE, PROPOSE, QUERY,
SESSION_WRAP, SESSION_WRAP_SCAN, SPEC, SWEEP_COMMIT, and WORK_ITEM. The other
24 current candidates are `rewrite-if-present`; candidate-set drift invalidates
these decisions rather than silently changing their meaning.

### F3: Isolated multi-generator projection graph

Accepted. Planning will build two independent disposable projection roots under
`.gtkb-state/file-reference-migration/wi5640/**`. Each root will be seeded from
the same observed preimage set and exact proposed canonical postimages. No
generator will run against the live consumer tree.

The policy will declare generator id, owner, inputs, owned output patterns,
execution order, environment, policy-bound clock, source snapshot, and check command. The engine will enforce exact
single ownership for every generated path and reject undeclared output,
multiply-owned output, orphan deletion, access outside the projection root, and
network/subprocess behavior not explicitly declared by the owner.

The deterministic order is:

1. reconstruct and parse planned canonical configuration/TOML postimages;
2. rule compatibility projections;
3. canonical Codex adapters and resource mirrors;
4. Antigravity adapters;
5. API adapters;
6. API-to-Goose adapters excluding the shared manifest;
7. `generate_goose_manifest.py` as sole owner of
   `.goose/skills/MANIFEST.json`;
8. Cursor adapters and manifest;
9. harness-capability registry hash projections;
10. dashboard JSON/report projections through their authoritative renderer;
11. harness parity and every generator's check-only command against the
    simulated postimage root.

All changed outputs will be harvested as content-addressed plan payloads.
Projection A and B must have byte-identical output path sets, modes, bytes,
owner ledgers, and semantic structured fingerprints. Existing generated-prefix
classification will be narrowed to exact owner-declared files; unmanaged Goose
helpers/drafts become ordinary mutable text or exact hash-bound retained
artifacts rather than generator-owned by directory prefix.

### F4: Structured TOML, dashboard SQLite, and live domain operation

Accepted as a required independently authorized dependency. This nine-target
revision will model and test the exact operations, but it will not edit these
live objects and does not claim F4 resolved by simulation alone.

The malformed staged source and untracked canonical activity-envelope TOMLs
will be reconstructed in memory from the clean tracked `HEAD` blob for
`config/agent-control/activity-envelope-sharding.toml`, with the observed
corrupt preimages, HEAD commit, clean-blob hash, transforms, and resulting
postimages bound into the plan. Both projected TOMLs must parse and agree on the
canonical deferred-surface set. Their future exact writes belong only to the
Stage B child target list.

The mojibake currently present in
`config/agent-control/gtkb-harness-capability-registry.toml` is not accepted as
content authority. Its postimage will continue to be reconstructed from the
clean retained source with all manifest transforms applied, preserving valid
Unicode and binding both corrupt preimage and clean postimage hashes.

`.groundtruth/dashboard/gtkb-dashboard.sqlite` will be queried read-only during
Stage A. A disposable dashboard database will be regenerated through
`groundtruth_kb.dashboard.refresh_dashboard_db` against a projected source
database and projection root. Because volatile capture time and SQLite page
layout are not byte authorities, the plan will bind an ordered schema/table/row
semantic fingerprint, declared volatile-field exclusions, source DB semantic
preconditions, and the official regeneration operation. Stage B must execute
the official API and verify the semantic fingerprint; it may not byte-edit or
raw-replace the live SQLite file.

The one current `groundtruth.db` residual for harness `H`, version `59`, will be
represented as a separately authorized append-only harness-domain operation,
never raw SQL. The exact operation will assert the current version and full
preimage row, append a new harness version preserving every field except
`capabilities_ref`, set that field to
`config/agent-control/gtkb-harness-capability-registry.toml`, regenerate
`harness-state/harness-registry.json` through
`groundtruth_kb.harness_projection.generate_harness_projection`, and verify the
new current row and projection. Historical harness rows remain immutable.

These consumer/database paths will be enumerated in the exact Stage B child
proposal after their prerequisite authorities exist. Before terminal Stage A
verification, separate reviewed bridge work must provide:

1. exact restoration authority for
   `config/agent-control/activity-envelope-sharding.toml` and
   `config/agent-control/gtkb-activity-envelope-sharding.toml`, using the clean
   tracked blob and bundled registry copy as evidence rather than a third target;
2. a public append-only `set-capabilities-ref` harness-domain operation and CLI
   with exact-version precondition, field preservation, projection regeneration,
   and tests, targeting
   `groundtruth-kb/src/groundtruth_kb/harness_ops.py`,
   `groundtruth-kb/src/groundtruth_kb/cli.py`,
   `groundtruth-kb/tests/test_harness_ops.py`,
   `platform_tests/groundtruth_kb/cli/test_harness_cli.py`, and the relevant
   harness-projection test; and
3. Stage B operation authority for `groundtruth.db`,
   `harness-state/harness-registry.json`, and
   `.groundtruth/dashboard/gtkb-dashboard.sqlite`, with dashboard regeneration
   routed through the existing `gt dashboard refresh` /
   `groundtruth_kb.dashboard.refresh_dashboard_db` API after repository and
   harness-domain changes.

Those paths are observations and dependency targets, not an expansion of this
Stage A write envelope. The Prime Builder will create or link the derived work
items and bridge proposals rather than silently absorbing them under WI-5640.

### F5: Governance suite dependency

Accepted. WI-5648 remains a separate bridge-protocol-reliability dependency and
is not absorbed into WI-5640. Stage A may reproduce and report its frozen
baseline exactly; it may not repair WI-5648 files under this proposal.

The exact governance suite is the eight-module 460-node composition recorded in
the prior evidence: 222 core nodes, 215 start-gate nodes, and 23 project-
authorization nodes. The 41 failures are not one uniform Version-metadata cause:
37 are stale strict-chain fixture failures, while four expose missing/incorrect
operation-time authorization enforcement in work-intent acquire, extend,
renew, and reclassify behavior. The correction requires an independently
authorized narrow WI-5648 child including at least
`platform_tests/scripts/test_implementation_start_gate.py`,
`scripts/bridge_work_intent_registry.py`, and a durable exact-suite manifest;
the evaluator/taxonomy joins that target set only if existing public APIs cannot
express the four operations.

No exact-plan child proposal will be filed until the independently authorized
WI-5648 correction is implemented and the complete governance/authorization
suite identified by the v4-001 contract passes with zero failures, timeouts,
collection errors, unexpected skips, or xfails. The rerun must record the exact
collected node count and sorted LF node-id hash so the historical 460-node claim
and the currently observed 205-node subset cannot be conflated.

## Bounded Target Set And Dependencies

The nine Stage A targets remain sufficient because this pass changes only the
migration engine, policy, two pure generators, focused tests/fixtures, and
non-authoritative runtime evidence. All live consumers identified by the plan
remain prohibited until the exact child lifecycle. If implementation discovers
that an authoritative dashboard, harness-domain, or generator API itself must
change, Prime Builder will stop and file a separately reviewed target expansion
instead of editing it under this GO.

This is intentionally a bounded correction proposal, not a claim that v4-004 is
fully resolved in one implementation turn. A later implementation report may
show F1-F3 complete while carrying F4-F5 as explicit dependencies; Loyal
Opposition must not record terminal VERIFIED until the separate structured,
domain-operation, dashboard, and governance evidence is complete.

## Requirement Sufficiency

Existing requirements sufficient.

The linked WI-5640 and governing specifications are sufficient for the bounded
F1-F3 Stage A implementation requested here. This state applies only to the nine
declared targets and does not convert the separately authorized F4 and F5
dependencies into this proposal's implementation scope.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5640; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE; bridge/gtkb-file-move-rename-canonicalization-v4-001.md through -004.md; DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, the governed 90-row CSV manifest, numbered bridge history, and independently reviewed implementation packets",
  "primary_route": "Deterministic full-root lexical discovery, typed parser classification, exact disposition ledger, isolated generator projection, independent LO review, and a later separately authorized exact-plan apply",
  "before_behavior": "Stage A finds every obsolete spelling but leaves 1666 live-reference records unresolved because bare filenames and structured contexts are not yet typed precisely enough for safe rendering.",
  "after_behavior": "Every observed obsolete spelling has one hash-bound typed context and disposition; only proved load-bearing spans become proposed writes, while ambiguity and unmet F4-F5 dependencies remain explicit blockers.",
  "self_descriptive_naming": "Reference semantic types, blocker codes, generator owners, candidate ids, operation records, and evidence hashes identify their purpose and authority directly.",
  "obsolete_guidance_disposition": "Mutable live consumers are proposed for canonicalization by typed span or authoritative regeneration; bridge and other canonical audit history is observed but never rewritten; retained old sources remain compatibility evidence until separately authorized deletion.",
  "history_preservation": "All numbered bridge files and deliberations remain append-only, all 90 obsolete sources remain present, and Stage A changes only the nine declared implementation and runtime-evidence targets.",
  "baseline": {
    "manifest_rows": 90,
    "inferred_alias_candidates": 43,
    "unresolved_live_references": 1666,
    "generated_outputs_not_materialized": 277,
    "old_sources_present": 90
  },
  "expected_result": {
    "f1_f3_blockers": 0,
    "alias_ledger": "casefold/NFC set-equal to all 43 inferred candidates",
    "generator_projection": "two isolated roots with identical owner, path, mode, byte, and semantic fingerprints",
    "f4_f5": "preserved as explicit independently authorized dependency gates",
    "old_sources_present": 90
  },
  "rollback": {
    "instructions": "Revert only the nine Stage A implementation targets to the v4-003 baseline and regenerate disposable evidence; do not alter consumer files, old sources, bridge history, databases, or the Git index.",
    "verification": "Rerun focused tests, Ruff checks, two clean-process preflights, source-presence checks, and strict bridge lifecycle resolution."
  },
  "hard_invariants": [
    "No live consumer, SQLite database, dashboard projection, Git index, dispatcher surface, application tree, or old source is mutated in this Stage A pass.",
    "No automatic rewrite occurs without one unique typed source span and preimage hash.",
    "No generated output has zero owners or multiple owners.",
    "Stage B requires a separate exact-plan proposal, independent GO, claim, and implementation packet."
  ],
  "fail_closed_conditions": [
    "Any lexical occurrence is unclassified, multiply classified, or no longer matches its bound preimage.",
    "The inferred candidate set differs from the exact policy ledger.",
    "The two isolated generator projections differ or a generator escapes its declared root.",
    "F4 or F5 is hidden as an exception or represented as completed without separate reviewed authority."
  ],
  "essential_context_preservation": [
    "Retain all 90 obsolete sources throughout migration and repeated verification.",
    "Preserve bridge and other canonical audit trails byte-for-byte.",
    "Inventory applications and in-root worktrees without admitting them to the write set.",
    "Carry source, parser, semantic locator, disposition, and preimage hash in every reference record."
  ]
}
```

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

`DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` remains controlling. All old
sources must remain present through Stage A, Stage B apply, and repeated
post-apply verification. Any later deletion requires a separate owner-approved
proposal. No additional owner decision is required for this bounded Stage A
correction.

## Prior Deliberations And Evidence

- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - temporary old-source retention and separate deletion authorization.
- `DELIB-202666274` - project authorization and independent-review controls.
- `bridge/gtkb-wi5648-file-move-false-verification-incident-001.md` and `-002.md` - fail-closed lifecycle and evidence requirements.
- `bridge/gtkb-file-move-rename-canonicalization-v4-001.md` through `-004.md` - operative Stage A proposal, GO, implementation evidence, and correction findings.

## Specification-Derived Verification Plan

### Focused deterministic tests

Add positive and negative tests for:

- typed Python, PowerShell, structured, Markdown, test-expectation,
  compatibility, prose, quotation, and ambiguous-basename occurrences;
- exact source-span rendering for directory suffixes and JSON escapes;
- duplicate-basename mappings that remain ambiguous until parser context proves
  one source family;
- exact set equality for 43 inferred candidate dispositions, including
  identity-digest drift, policy self-observation, and `assert-absent` violations;
- identical two-root generator projections and rejection of undeclared,
  multiply-owned, orphaned, or live-root output;
- Goose adapter/manifest single ownership;
- exact owner classification for generated skill artifacts versus unmanaged
  helper/draft resources;
- clean-HEAD TOML reconstruction, corrupt-preimage binding, and projected parse;
- dashboard SQLite read-only scan, official regeneration, stable semantic
  fingerprint, and volatile-field exclusion rejection;
- clean harness-registry Unicode reconstruction with every path transform and
  rejection of the mojibake destination as authority;
- append-only harness-domain operation precondition, version conflict,
  field-preservation, projection regeneration, and historical immutability;
- in-root registered-worktree observation bound to each worktree HEAD without
  following external worktrees;
- two clean-process plans with identical plan, write-set, exception, generator,
  structured-operation, and expected-final closure hashes.

The implementation will use the current declared dependency set. If a portable
span-preserving YAML or CommonMark parser cannot be implemented with existing
project dependencies, Prime Builder will stop and file a target expansion for
`pyproject.toml` and the applicable dependency/CI surfaces before adding a new
package.

### Required commands

```powershell
python -m pytest platform_tests/scripts/test_gtkb_file_reference_migration.py platform_tests/scripts/test_generate_rule_compatibility_projections.py platform_tests/scripts/test_generate_cursor_skill_adapters.py -q --tb=short
python -m ruff check scripts/gtkb_file_reference_migration.py scripts/generate_rule_compatibility_projections.py scripts/generate_cursor_skill_adapters.py platform_tests/scripts/test_gtkb_file_reference_migration.py platform_tests/scripts/test_generate_rule_compatibility_projections.py platform_tests/scripts/test_generate_cursor_skill_adapters.py
python -m ruff format --check scripts/gtkb_file_reference_migration.py scripts/generate_rule_compatibility_projections.py scripts/generate_cursor_skill_adapters.py platform_tests/scripts/test_gtkb_file_reference_migration.py platform_tests/scripts/test_generate_rule_compatibility_projections.py platform_tests/scripts/test_generate_cursor_skill_adapters.py
python scripts/gtkb_file_reference_migration.py preflight
python scripts/gtkb_file_reference_migration.py preflight
```

The two preflights must run in separate processes and yield identical binding
material. F1-F3 migration blockers must reach zero. F4-F5 must remain explicit
typed dependency gates until their own reviewed implementations close; they may
not be hidden as exceptions or described as completed. All 90 old sources and
all canonical destinations must remain present.

The frozen 209-node cross-harness no-regression suite and the currently observed
governance/authorization baseline will be rerun exactly as declared in
`wi5640.toml`. Any new node/failure/signature is blocking. The exact-plan child
remains prohibited until the independently corrected full governance suite is
completely green.

## Acceptance Criteria

- [ ] Every full-root occurrence has one typed context, disposition, location, and preimage hash.
- [ ] Ambiguous bare filenames remain explicit blockers; no blanket replacement exists.
- [ ] The inferred alias policy ledger is set-equal to all 43 deterministic candidates.
- [ ] Every live alias occurrence is materialized through an exact text span, authoritative generator, structured operation, or typed exception.
- [ ] Two isolated generator roots produce identical owner/path/mode/byte and semantic fingerprints.
- [ ] Goose manifest ownership is singular and generated-prefix overclassification is removed.
- [ ] The planned activity-envelope TOMLs parse from clean-HEAD reconstruction and bind corrupt preimages.
- [ ] Dashboard SQLite and `groundtruth.db` changes are official semantic operations, never byte edits or raw SQL.
- [ ] Every in-root worktree is observed under its own HEAD; external worktrees remain outside the dependency boundary.
- [ ] `applications/**` is inventoried but never enters the write set or a live generator root.
- [ ] Focused tests, Ruff lint, and Ruff format pass.
- [ ] Two clean-process preflights have zero F1-F3 migration blockers, explicit F4-F5 dependency gates, and identical complete bindings.
- [ ] All 90 old sources remain present and no live consumer mutation has occurred.
- [ ] No Stage B child is filed before the independently repaired governance suite is fully green.

## Risk And Rollback

The main risk is converting an over-broad blocker into an under-broad scanner.
Typed parsers therefore add evidence; they do not downgrade unmatched tokens to
prose. Byte probing remains the completeness backstop, and any obsolete byte
without a typed disposition blocks closure.

Generator execution is restricted to disposable roots, with two independent
builds and exact owner/output comparison. A generator escape, undeclared output,
or nondeterministic byte/semantic result blocks the plan. Stage A rollback is
limited to the nine additive implementation targets and runtime evidence; no
consumer rollback exists because no consumer mutation is authorized.

The active PAUTH forbids destructive cleanup, commit, push, release, deployment,
and dispatcher mutation. Nothing in this revision changes those prohibitions.

## Loyal Opposition Request

Review whether the typed scanner, set-equal alias ledger, isolated generator
graph, semantic operation model, unchanged Stage A target boundary, and explicit
F4-F5 dependency partition are sufficient for the next bounded correction pass.
A GO must authorize only the nine Stage A targets and read-only/simulated
observation; it must not represent F4 or F5 as completed and must not authorize
live migration apply or any Stage B consumer operation.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
