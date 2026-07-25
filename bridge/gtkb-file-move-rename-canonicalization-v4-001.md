NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user; role_source=transcript_init_keyword
author_metadata_source: explicit current-session Codex bridge filing metadata

# Implementation Proposal: Recover and harden deterministic file-reference migration Stage A

bridge_kind: prime_proposal
Document: gtkb-file-move-rename-canonicalization-v4
Version: 001
Date: 2026-07-22 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

target_paths: ["scripts/gtkb_file_reference_migration.py", "scripts/generate_rule_compatibility_projections.py", "scripts/generate_cursor_skill_adapters.py", "config/file-reference-migration/wi5640.toml", "platform_tests/scripts/test_gtkb_file_reference_migration.py", "platform_tests/scripts/test_generate_rule_compatibility_projections.py", "platform_tests/scripts/test_generate_cursor_skill_adapters.py", "platform_tests/fixtures/file_reference_migration/**", ".gtkb-state/file-reference-migration/wi5640/**"]

implementation_scope: source | test | configuration | documentation | metadata | runtime_state | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

observation_scope: every filesystem entry beneath E:\GT-KB, every configured
current SQLite text field, every registered nested worktree, and every
application/reparse boundary. Observation does not grant mutation authority.

---

## Summary And Claim

This fresh thread replaces the structurally irreparable v3 Stage A report
chain. It authorizes only correction and verification of the deterministic
migration engine, policy, generators, fixtures, tests, and non-authoritative
runtime evidence listed in `target_paths`. It does not authorize migration
apply, repository-consumer mutation, database mutation, source deletion,
staging, commit, push, release, deployment, dispatcher mutation, or mutation of
the preserved v3 evidence.

The corrected Stage A must produce a complete, deterministic, exact-write plan
for all load-bearing obsolete references under the repository root. Coverage
must include the 90 CSV mappings and obsolete aliases outside that CSV, such as
retired skill paths. It must also close the transaction-safety, final-state
verification, generated-output, structured-container, and test-evidence gaps
found after v3. All 90 old source paths remain present. Apply remains impossible
until a separately reviewed exact-plan child thread receives GO and an exact
claim and implementation-start packet.

## First-Line Role Eligibility Check

PASS. This interactive Codex session context
`019f863a-acd3-7320-80c0-1831f0936cc0` was initialized by the owner as
`::init gtkb pb`; its in-root session envelope resolves `prime-builder` from
the transcript init keyword and the durable registry agrees. `NEW` is a Prime
Builder status. The owner assigned all Prime Builder work for this program to
this session and reserved formal LO review for an unrelated interactive Codex
session.

## Recovery And Incident Disposition

1. Preserve `gtkb-file-move-rename-canonicalization-v3` versions 001 through
   006 unchanged as incident evidence. Do not file v3-007.
2. v3-005 has decorated `Version` metadata. The strict resolver parses every
   contiguous version before resolving status, so no appended v3 artifact can
   repair the chain.
3. The implementation-report helper also emits `Responds to GO:` instead of
   the strict immediate-predecessor `Responds to:` field. Both helper defects
   are WI-5648 bridge-protocol-reliability scope and are not silently absorbed
   into WI-5640.
4. Any later v4 implementation report must be composed with exact undecorated
   metadata, strict-prevalidated as a candidate, and published through the
   governed writer path. The defective report helper may not be used until it
   is separately repaired and verified.
5. This v4-001 has no `Responds to:` field because it is a new version-001
   lifecycle. v3 is cited only as evidence, never as authority.

## Requirement Sufficiency

Existing requirements are sufficient for this bounded Stage A correction. The
operative owner requirements are: deterministic programmatic full-root
discovery and replacement; no agent-driven recursive manual find/replace;
correction of every load-bearing obsolete reference except explicitly
classified immutable audit history; temporary retention of every obsolete
source; repeated independent verification before any later deletion; and
independent LO review at each governed stage.

No owner decision authorizes deletion, blind copying, raw database mutation,
or use of the invalid v3 chain. Newly discovered requirements outside WI-5640
must be preserved as backlog work instead of being implemented under this GO.

## Current-State Evidence

- The CSV has 90 unique non-no-op rows: 33 hooks, 38 rules, and 19
  agent-control mappings. All 90 source paths and all 90 destinations exist.
- The latest v3 Stage A evidence is blocked: 4,069 reference hits, 1,676
  unresolved residuals, 479 proposed writes, and 1,994 blockers. The recorded
  plan hash is
  `sha256:575053236f13e2a6b456f0b1ec0e7e9d19369138cdb99f52112385976bbb3855`.
- The focused Stage A suite passes 31 tests and Ruff is clean.
- The required 209-test cross-harness suite currently has a reproducible
  baseline of 203 pass and 6 fail at HEAD
  `ef6ba79c7527190606e41267bd45e6732c405e43`. One failure is the
  already-committed, undeclared `gtkb-skill-rollout` skill introduced under
  WI-5646. Five failures are the exact unimplemented WI-5364 Codex hook batch,
  whose latest bridge verdict is NO-GO; successor WI-5428 tracks restoration
  after the false backlog closure. Those targets are outside this Stage A
  write set.
- The governance/authorization suite was rerun in bounded groups with a
  120-second per-test timeout. The resolver/authorization core group passed
  222/222 in 1,042.03 seconds and the project-authorization group passed 23/23.
  The start-gate group passed 174/215 and failed 41/215 because its synthetic
  bridge fixtures omit strict `Version` metadata. The sorted failing-node list
  has LF hash
  `sha256:31cd76c57a3d6070965aebda83e31ea66a4a0d2a0e9454ffd36f51db6ced3338`.
  This is a real baseline defect aligned with WI-5648, not a timeout and not a
  pass.
- An independent deterministic alias inventory found 28 active files requiring
  rewrite, 14 generated/projection files requiring regeneration, 300
  historical/audit files requiring byte-preserved typed exclusions, and 548
  accessible runtime copies for the retired `bridge-propose` path family. It
  also found two physically old-named managed-template files. The old canonical
  skill path is absent and the `gtkb-bridge-propose` path is present. These
  point-in-time counts are reconnaissance that Stage A must reproduce; they
  prove both content and physical-path coverage are missing from the current
  90-row-only scanner.
- The current plan also reports 277 generated outputs not materialized, 33
  undecoded-container byte hits, failed or ownership-blocked generators, one
  live SQLite current-state residual, and an unreadable runtime directory.
- No apply has run. No old source has been deleted. There is no active v3 or v4
  implementation claim or implementation-start packet.

## Authorized Stage A Corrections

### 1. Deterministic obsolete-alias coverage

Extend the policy and engine so the migration universe is not limited to the
90 CSV rows. The engine must build one collision-checked obsolete-token catalog
from these deterministic sources:

1. all CSV source/destination pairs;
2. canonical skill inventories and governed rename metadata;
3. path-like references to absent non-prefixed skill directories when the
   corresponding present `gtkb-*` canonical directory exists;
4. explicit reviewed alias rows for legacy spellings that cannot be inferred
   without ambiguity; and
5. family-level loader, registry, template, generator, and import-root forms.

Inferred aliases are evidence candidates, not automatic rewrite authority.
Each candidate must be emitted into the plan with source, canonical target,
inference basis, every occurrence, and one disposition: rewrite,
generator-regenerate, immutable-audit, retained-compatibility, external or
application boundary, or unresolved. Ambiguous, multiply-targeted, or
undispositioned aliases block the plan.

The scanner must cover direct POSIX/Windows/mixed/absolute/escaped/URI forms,
referrer-relative paths, Python and PowerShell segmented constructions, TOML,
JSON and YAML structured strings, globs, regular expressions, bare filenames
resolved against loader roots, generated manifests, and configured SQLite text
fields. Matching must be component-aware, Unicode-NFC normalized, and Windows
case-insensitive without rewriting unrelated prose substrings.

The scanner must also inventory path components themselves. Content scanning
cannot discover a physically old-named file or directory when its bytes contain
no old token. Every physical alias is recorded with object type, source path,
candidate canonical path, existence/collision state, tracking state, hash or
directory inventory hash, and disposition. Stage A observes and plans such
operations; it does not move, rename, delete, or create the live object.

Lexical overlap is not path authority. Stable capability IDs such as
`skill.bridge-propose`, runtime namespaces such as
`.gtkb-state/bridge-propose-*`, Python identifiers, and plain prose receive
typed compatibility or semantic-review dispositions and are never changed by a
global substring replacement.

Unknown extensions and undecodable files may not disappear. The engine must
run byte-level token probes for every obsolete catalog entry, inspect supported
containers through structured readers such as `zipfile` and read-only SQLite,
and emit a blocking or explicit immutable-fixture disposition for every hit.

### 2. Full-root inventory and exclusions

Every enumerable entry under `E:\GT-KB` must receive exactly one classification
record. The full observation includes ignored files and excluded roots. The
stable closure fingerprint may replace volatile excluded subtrees with fixed
root records only when the full observation separately records their entries,
counts, bytes, errors, and inventory hash.

`bridge/**` and equivalent governed audit history are immutable and excluded
from correction, but remain inventoried. Registered nested worktrees,
`applications/**`, reparse targets, runtime/cache trees, database files, binary
containers, generated output, retained sources, canonical destinations, and
unreadable paths require distinct classifications. The scanner must not follow
reparse points or external worktree roots. An unreadable entry blocks closure
until a separate authorized resolution makes it enumerable or an independently
reviewed evidence standard explicitly dispositions it; no excluded ancestor may
silently hide it.

### 3. Complete mutation manifest

The plan must declare every durable side effect, not only repository-consumer
postimages. It must distinguish:

- exact repository file writes;
- generated files materialized from isolated generator runs;
- structured domain operations, which require separate API authority;
- created parent directories and restored metadata;
- runtime lock, write-ahead journal, transaction report, payload, and recovery
  files; and
- implementation-packet binding evidence.

Only the exact repository write set belongs in the later child proposal's
mutation target list. Operational runtime and governance side effects must be
separately enumerated and covered by the PAUTH and packet rather than omitted
from the mutation model. No generator may mutate the live repository during
planning.

### 4. Reparse-resistant path safety

Replace path-string-only ancestor checks with a platform adapter that proves
root and ancestor identity immediately before and throughout mutation. On
Windows, open root and every existing write ancestor with Win32 no-reparse
semantics, record volume/file identities and reparse tags, and hold handles that
deny delete/rename sharing for the transaction. Resolve final paths through the
handles and require every identity to remain beneath the original root before
and after each replace. Literal Windows names must never be interpreted as
devices, options, globs, or expressions.

Tests must inject root, ancestor, and target junction/symlink swaps at every
validation boundary and prove zero out-of-root or wrong-object writes. A safety
adapter unsupported on the active platform must fail apply closed, not degrade
to lexical checks.

### 5. Durable write-ahead transaction and recovery

Before the first repository mutation, fsync a canonical journal containing the
plan hash, session, authority hash, complete operation list, preimages,
postimages, attributes, parent-directory actions, and recovery state. For each
operation, persist and fsync an intent record before replacement and an applied
record only after postimage verification. The operation lock must identify the
journal and must never be silently removed after a crash.

Every apply, rollback, and recovery entry point must detect an incomplete
transaction before doing other work. Recovery is explicit, idempotent, and
compare-and-swap guarded. It may restore a preimage only when the current bytes
equal the recorded postimage, and may restore absence only when the created
object identity is the recorded one. Concurrent drift stops recovery with
durable evidence.

Rollback must prevalidate every target, payload, identity, and current
postimage before its first reversal. Each rollback mutation also receives a
write-ahead intent and completion record. Fault-injection tests must cover
termination before first write, between replace and journal update, during
rollback, during compensation, during directory creation, and during final
verification.

### 6. Independent final-state verification

Planning must compute both reviewed pre-apply binding material and an expected
final-state closure fingerprint from the exact postimage simulation. Apply may
not report success from its write log. After all writes, it must re-open every
target through the safety adapter, re-run the complete scanner and structured
readers from disk, re-run generator checks in check-only mode, and require:

- every postimage and attribute matches the plan;
- the Git index and staged-path set are unchanged;
- no pending proposed write remains;
- no unexplained live obsolete reference remains;
- all 90 old sources remain present;
- all retained sources have the planned inert or compatibility disposition;
- no unreadable or unclassified path remains; and
- the observed final fingerprint equals the reviewed expected final-state
  fingerprint.

Only then may the journal become `applied`. Two additional clean-process verify
passes, followed by a third after the complete generator/test suite, must yield
the same final closure fingerprint before an implementation report is filed.

### 7. Generator and structured-data closure

Run generators only against an isolated projection root during planning,
capture every output as a plan payload, and fail if an output is undeclared.
The live apply performs only plan-listed atomic writes; post-apply commands are
check-only. Shared-manifest ownership conflicts must receive one explicit
canonical owner and test before plan approval.

SQLite is always queried structurally in read-only mode during Stage A. A live
current-state residual must become a separately authorized, named public domain
operation with transactional tests and an exact semantic precondition in the
child plan. Historical rows are immutable audit evidence. Raw SQL, binary
database replacement, and direct generated-projection editing remain forbidden.

### 8. Test-gate accounting

Stage A must distinguish scoped regression from unrelated baseline debt without
calling failures passes.

- The migration-focused suite and Ruff must pass completely.
- The 209-test cross-harness suite must either pass completely or reproduce
  only the same six baseline failures by exact node ID and normalized failure
  signature. The policy must contain a machine-readable
  `allowed_baseline_failures` table bound to HEAD
  `ef6ba79c7527190606e41267bd45e6732c405e43`, the owning WI/project, and the
  latest numbered bridge evidence. Candidate failure IDs and normalized
  checker findings must be subsets of that frozen baseline. Any new or changed
  failure is blocking. This is a bounded no-regression contract, not a parity
  waiver and not authority to repair those out-of-scope targets.
- The 460-test governance/authorization suite must complete in bounded groups.
  During Stage A it may reproduce only the same 41 stale-fixture failures, with
  the exact sorted node-list hash above and normalized root cause `missing
  Version metadata`; the other 419 tests must pass and any changed failure is
  blocking. The policy must carry all 41 exact node IDs and the WI-5648 owner.
  A timeout is a failure, not an acceptable baseline.
- Stage B plan approval and apply remain blocked until the 41 strict-fixture
  failures are repaired under WI-5648 or another explicitly authorized bridge
  and the complete 460-test suite passes. Stage A no-regression evidence cannot
  be reused as apply-safety authority.
- Add positive and negative tests for authorized apply, proposal/GO/packet
  tampering, session mismatch, claim drift, packet extension drift, Windows
  literal paths, reparse swaps, crash recovery, rollback fault injection,
  final-state mismatch, unknown-extension hits, alias inference, and generated
  output ownership.

The six allowed baseline node IDs are exactly:

```text
platform_tests/scripts/test_check_harness_parity.py::test_repository_registry_covers_project_skills
platform_tests/scripts/test_codex_hook_parity.py::test_codex_hook_parity_passes_for_repository_configuration
platform_tests/scripts/test_codex_hook_parity.py::test_codex_userpromptsubmit_wrapup_hook_has_headroom_timeout
platform_tests/scripts/test_codex_hook_parity.py::test_codex_hook_parity_requires_session_lifecycle_hook_intent
platform_tests/scripts/test_codex_hook_parity.py::test_codex_hook_commands_avoid_shell_specific_command_substitution
platform_tests/scripts/test_codex_hook_parity.py::test_codex_parity_repository_configuration_wires_bridge_compliance
```

The allowed normalized Codex checker findings are exactly: `hooks=false`;
missing formal-artifact PreToolUse; missing workstream-focus PreToolUse; missing
Bash matcher; missing `apply_patch` matcher; missing workstream-focus
UserPromptSubmit; missing session-lifecycle UserPromptSubmit; and wrap-up
dispatcher forces a role profile. The verifier must also require exactly 209
collected nodes, no new skip/xfail/collection state, no new parity
EXTRA/MISSING/error, current hashes for the relevant baseline files, and three
identical normalized reruns.

## Stage Boundary And Exact-Plan Child

A GO on this v4-001, followed by a matching v4 claim and implementation-start
packet, authorizes only the Stage A target paths listed in this proposal and
read-only `preflight`, `plan`, and `verify` observations. It authorizes no
migration apply or repository-consumer change.

When Stage A is complete, Prime Builder must file a strict-valid v4
implementation report using exact metadata and release the Stage A claim. A
separate child thread named
`gtkb-file-move-rename-canonicalization-v4-plan-approval` must then carry the
complete sorted plan, all reconciliation and alias dispositions, exact write
paths, pre-apply binding, expected final-state binding, generator payloads,
structured domain operations, runtime side effects, and residual/exception
ledger. Its target coverage preflight must be clean for every repository write.

Apply requires an independent child GO that echoes the exact binding, a fresh
non-overlapping child claim, and a child implementation-start packet whose
normalized exact targets equal the repository write set. Engine, policy, CSV,
plan, proposal, GO, packet, claim, Git index, preimages, inventory,
classification, exceptions, generated inputs, and expected final-state hashes
must all match at operation time. Any change requires a new child revision and
independent GO.

No old source deletion belongs to either stage. Deletion remains a later,
separately owner-authorized program after repeated closure checks.

## Cross-Harness Disposition

The scanner and plan cover Claude, Codex, Cursor, Antigravity, Goose, API,
Ollama, OpenRouter, and configured Alibaba surfaces. Native delivery mechanisms
remain harness-specific, but every live consumer must resolve the same canonical
artifact. Generated adapters must be regenerated from canonical sources and
verified, not hand-patched. `applications/**` remains a report-only independent
lifecycle boundary unless a later proposal grants application mutation.

No new parity waiver is requested. The exact six-test repository baseline is
handled only as scoped no-regression evidence for Stage A. WI-5364 and its
latest NO-GO bridge file are direct evidence for the five Codex failures;
WI-5428 is the open restoration owner. WI-5646 and its VERIFIED bridge chain
are direct evidence for the registry omission.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "owner full-root deterministic-scan and obsolete-source-retention directives plus WI-5640 and current advisory evidence",
  "canonical_authority": "config/hooks and config/agent-control gtkb-prefixed destinations, with generated native compatibility projections where declared",
  "primary_route": "v4 Stage A deterministic engine correction followed by a separately GO-approved exact-plan child",
  "before_behavior": "the current 90-row-only scanner misses out-of-manifest and physical aliases and cannot prove crash-safe final-state closure",
  "after_behavior": "one bound catalog inventories and dispositions every obsolete path reference while retained sources remain present and apply stays separately gated",
  "self_descriptive_naming": "gtkb_file_reference_migration and wi5640 policy identify program, scope, and authority",
  "obsolete_guidance_disposition": "live obsolete guidance is planned for correction; immutable audit history and stable lexical compatibility IDs are typed and preserved",
  "history_preservation": "v3, bridge history, database history, Git history, audit records, and all 90 old source files remain present and unmodified in Stage A",
  "baseline": "90 CSV mappings; 28 active alias rewrites; 14 generated alias outputs; 300 audit exclusions; 548 accessible runtime copies; 31 focused passes; 6 cross-harness and 41 governance baseline failures",
  "expected_result": "deterministic exact plan with complete alias and physical-path coverage, durable transaction proof, expected-final-state binding, and no new test failure",
  "rollback": "restore only declared Stage A files to recorded preimages; no broad Git, deletion, or history operation",
  "hard_invariants": [
    "no apply under the v4 Stage A GO",
    "no obsolete-source deletion",
    "no audit-history mutation",
    "no raw database mutation",
    "no Git index mutation",
    "Stage B blocked until the governance suite passes 460/460"
  ],
  "fail_closed_conditions": [
    "unreadable or unclassified path",
    "undispositioned or ambiguous alias",
    "reparse or object-identity uncertainty",
    "journal or recovery ambiguity",
    "plan, packet, claim, preimage, generator, or inventory drift",
    "new or changed test failure"
  ],
  "essential_context_preservation": "native rule compatibility, harness-specific delivery mechanisms, retained safety copies, and immutable evidence remain available while canonical consumers move"
}
```

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - all supported harness projections and
  fallback paths must resolve equivalent canonical control surfaces.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - deterministic coverage must include
  every governed harness delivery mechanism.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - generated adapters and parity
  assertions require generator-first verification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex paths must remain functional
  without absorbing WI-5428 under this proposal.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - retained safety copies,
  transactional recovery, and final-state scanning prevent functional loss.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - v4 requires independent GO, exact claim,
  packet, report, and verification; v3 is not authority.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - active PAUTH, project,
  WI, and bounded targets are declared above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing specs
  are mapped before review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - all verification derives
  from the stated requirements and must use current executed evidence.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - Stage A and
  child apply must revalidate PAUTH, lifecycle, claim, packet, and targets at
  operation time.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - every proposal, plan, report, and
  verdict retains real session and model attribution.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - traversal remains in-root and
  application boundaries are not silently mutated.
- `GOV-WORK-TREE-HYGIENE-001` - the live index and unrelated dirty work remain
  untouched.
- `GOV-STANDING-BACKLOG-001` - WI-5648, WI-5428, and other out-of-scope defects
  remain separately tracked.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - plans, dispositions, recovery state,
  reports, and later deletion remain durable lifecycle artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - manifest, plan, implementation,
  and verification evidence retain traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - retained, blocked, migrated,
  verified, and deletion-candidate states remain explicit.

## Spec-Derived Verification Plan

| Requirement | Required Stage A evidence |
| --- | --- |
| Manifest integrity | Run preflight and prove 90 rows, 33/38/19 categories, unique paths, no no-ops, all sources/destinations present, and stable CSV hash. |
| Alias completeness | Enumerate explicit and inferred obsolete aliases; independently compare against a full-root path-token inventory; require every hit to have one disposition and zero undispositioned candidates. |
| Full-root classification | Prove every enumerable entry has exactly one class; report counts, bytes, errors, full-observation hash, and closure hash; fail on unreadable or unclassified entries. |
| Transaction safety | Unit and fault-injection tests prove handle-bound no-reparse ancestry, durable WAL, stale-lock recovery, prevalidated CAS rollback, compensation, and no out-of-root writes. |
| Final-state proof | Simulate reviewed postimages, then test an authorized apply in fixtures and require a full independent disk rescan to equal the expected final-state fingerprint before success. |
| Authorization binding | Test child lifecycle, unrelated reviewer, exact claim/session, packet hash/expiry/extension, exact targets, proposal/GO hashes, plan binding, and all tamper cases. |
| Generator closure | Run every policy generator against an isolated root; materialize all outputs; verify live checks are side-effect-free and shared-output ownership is unique. |
| Structured data | Exercise read-only SQLite and container readers; require current/history distinctions and fail raw database write attempts. |
| Source retention | Require all 90 old sources before and after fixture apply/rollback; prove no deletion operation is emitted. |
| Focused tests | Run `python -m pytest platform_tests/scripts/test_gtkb_file_reference_migration.py platform_tests/scripts/test_generate_rule_compatibility_projections.py platform_tests/scripts/test_generate_cursor_skill_adapters.py -q --tb=short`; require all pass. |
| Static quality | Run `python -m ruff check scripts/gtkb_file_reference_migration.py scripts/generate_rule_compatibility_projections.py scripts/generate_cursor_skill_adapters.py platform_tests/scripts/test_gtkb_file_reference_migration.py platform_tests/scripts/test_generate_rule_compatibility_projections.py platform_tests/scripts/test_generate_cursor_skill_adapters.py`; require clean. |
| Cross-harness no-regression | Run the exact 209-test command from v3; require 209 pass or only the same six baseline node IDs and signatures with WI ownership evidence. |
| Governance behavior | Run all 460 tests in bounded groups. Stage A may reproduce only the exact 41-node stale-fixture baseline with LF hash `sha256:31cd76c57a3d6070965aebda83e31ea66a4a0d2a0e9454ffd36f51db6ced3338`; require the other 419 pass and no timeout. Stage B requires 460/460 pass. |
| Idempotency | Run plan twice in clean processes; require byte-identical plan and binding. Run verify twice, then after generators/tests; require identical closure fingerprint. |

## Acceptance Criteria

1. v4 resolves strictly as a fresh `NEW` followed only by a valid independent
   LO transition. No v3 file is altered or appended.
2. Stage A changes only the declared target paths and runtime evidence. No live
   migration apply, consumer mutation, database mutation, or source deletion
   occurs.
3. The deterministic obsolete-token catalog covers the 90 CSV mappings and
   out-of-manifest aliases; every full-root occurrence receives one auditable
   disposition.
4. Unknown extensions, undecoded data, containers, generated outputs,
   worktrees, applications, reparse points, runtime roots, and SQLite are
   explicitly observed and classified.
5. The exact plan declares every repository write and every operational side
   effect, with no live generator mutation during planning.
6. Apply and rollback safety are proven by platform-specific no-reparse handle
   checks, durable write-ahead recovery, compare-and-swap, and fault injection.
7. Success requires an independent full disk rescan matching the reviewed
   expected final-state fingerprint; write-log success is insufficient.
8. Focused tests pass. Cross-harness evidence introduces no failure beyond the
   exact six-test baseline. Stage A governance evidence introduces no failure
   beyond the exact 41-node WI-5648 fixture baseline; Stage B remains blocked
   until governance reaches 460/460 pass.
9. All 90 old paths remain present. No deletion, cleanup, broad Git command,
   staging, commit, push, release, deployment, credentials, dispatcher change,
   or external-system mutation occurs.
10. The Stage A report uses exact strict metadata and names all remaining
    blockers. It requests LO review of Stage A only and cannot authorize apply.

## Files Expected To Change

Only the nine `target_paths` entries declared in the header may change or be
created during Stage A. Existing untracked Stage A files are treated as
preexisting candidates, not as authorization. Any edit after GO requires an
exact v4 claim and implementation-start packet.

All other repository paths named in this proposal are observation evidence or
prospective child-plan writes. They are not Stage A mutation authority.

## Risk / Rollback

- Incomplete discovery is controlled by deterministic alias inference,
  full-root inventory, byte/container probes, and undispositioned-hit blockers.
- Reparse and concurrent-path attacks are controlled by held platform handles,
  identity checks, literal paths, and fail-closed unsupported-platform behavior.
- Crash and partial-write loss are controlled by fsynced write-ahead intent,
  explicit recovery, CAS rollback, and fault-injection tests.
- False closure is controlled by expected-final-state binding and independent
  disk rescans after apply and after all generators/tests.
- Scope creep is controlled by Stage A exact targets, separate child plan/GO,
  and separate WIs for bridge helpers and Codex hook parity.

Stage A rollback is file-scoped restoration of only its declared files to their
recorded preimages. It must not use `git reset`, `git checkout`, `git clean`,
stash operations, broad staging, deletion of retained sources, or history
rewrite.

## Owner Decisions / Input

- `DELIB-202666274` authorizes the active Harness Parity project PAUTH while
  preserving independent review, exact claim, packet, nonimpairment, and no
  commit/destructive-cleanup boundaries.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` requires temporary retention
  of obsolete sources, repeated deterministic scans, and a later separately
  authorized deletion phase.
- The owner directed deterministic scanning of the entire `E:\GT-KB` root and
  prohibited manual recursive find/replace.
- The owner assigned all Prime Builder work to this Codex session and will use
  unrelated interactive Codex sessions for formal LO review.

## Prior Deliberations And Evidence

- `DELIB-202666274` - active project authorization owner decision.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - controlling retention and
  deletion-phase decision.
- `DELIB-202667106` - prior LO review of the canonical skill rename rollout.
- `bridge/gtkb-wi5648-file-move-false-verification-incident-001.md` and `-002.md`
  - incident and quarantine evidence; not WI-5640 implementation authority.
- `bridge/gtkb-file-move-rename-canonicalization-v3-001.md` through `-006.md`
  - preserved invalid Stage A chain and review evidence only.
- `bridge/gtkb-wi5364-codex-hook-batch-parity-004.md` - latest NO-GO evidence
  for the exact five Codex hook failures.
- `bridge/gtkb-gfr-slice-d-drift-generator-hygiene-004.md` - terminal WI-5646
  evidence whose delivered skill lacks a registry row.
- WI-5428 - open successor restoring the missing WI-5364 implementation after
  false backlog closure.
- WI-5648 - bridge lifecycle and writer-helper reliability owner.

## Pre-Filing Preflight

The following checks were executed against this exact non-dispatchable draft:

- Strict candidate parse: `strict`, `NEW`, `prime-builder`, document
  `gtkb-file-move-rename-canonicalization-v4`, version `001`, and no
  `Responds to:` value. Ordinary transition validation passed.
- Applicability preflight: `preflight_passed: true`, no blocking errors, no
  missing required/advisory specs, no unclassified targets, and no author
  metadata warning.
- Clause preflight: five clauses evaluated, four `must_apply`, one `may_apply`,
  zero must-apply evidence gaps, and zero blocking gaps.
- Strict target coverage: `verdict: clean`; all nine declared Stage A targets
  covered and no implied generator, integration, prose, verification, or
  out-of-root path remained uncovered.
- Phantom-spec sweep: all 17 cited ADR/DCL/GOV IDs exist in current MemBase.
- Credential scan: zero canonical credential-pattern hits.
- Role eligibility: the in-root current-session envelope resolves this session
  as Prime Builder from `::init gtkb pb`.
- PAUTH: current project authorization is active, has no per-WI inclusion
  restriction, covers the declared Stage A mutation classes, and forbids
  destructive cleanup, commit, push, release, deployment, dispatcher mutation,
  credentials, external-system mutation, and history rewrite.
- Bridge/claim state: no v4 bridge file existed before filing and v4 claim
  status was `null`.
- Test baseline: focused Stage A 31 pass; cross-harness 203 pass/6 fail with
  frozen exact baseline; governance/authorization 419 pass/41 stale-fixture
  fail with the frozen exact node-list hash; no timeout at 120 seconds per test.

The governed Codex writer must repeat credential and bridge-compliance checks,
acquire and release its short drafting claim, preserve the exact author
metadata above, normalize the LO dispatch envelope, and refuse overwrite.

## Explicit Non-Authority

This `NEW` proposal does not authorize implementation. Prime Builder must wait
for an unrelated LO GO on this exact v4-001, then acquire a matching Stage A
claim and implementation-start packet before editing any Stage A target. A v4
GO cannot authorize migration apply. Apply requires the separate exact-plan
child GO, child claim, child packet, and matching reviewed final-state binding.

## Recommended Commit Type

`fix(migration):` after separate commit authorization and independent terminal
verification. The active PAUTH currently forbids commit.

---

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
