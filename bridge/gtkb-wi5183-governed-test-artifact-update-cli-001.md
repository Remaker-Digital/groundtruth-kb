NEW
::init gtkb pb
::open build

# WI-5183 — Add a governed append-only test-artifact update CLI

bridge_kind: prime_proposal
Document: gtkb-wi5183-governed-test-artifact-update-cli
Version: 001
Date: 2026-08-01 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: OpenAI Codex Desktop
author_model_version: Codex Desktop interactive runtime; exact foundation-model identifier is not exposed to this task
author_model_configuration: Codex Desktop interactive Prime Builder; host product surface only, with no inferred foundation-model ID; transcript-defined ::init gtkb pb; ordinary per-WI PB authority only; former CF-10 all-program serialization authority rescinded; dispatcher and TAFE deliberately disabled
author_metadata_source: task-local interactive transcript, CODEX_INTERNAL_ORIGINATOR_OVERRIDE, and open per-session envelope

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5183
Related Work Items: WI-5178, WI-5234, WI-5271, WI-5282, WI-5311, WI-5441, WI-5483, WI-5593, WI-5615, WI-5712, WI-5883, WI-5899

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_test_update.py", "groundtruth-kb/src/groundtruth_kb/db.py", "platform_tests/groundtruth_kb/cli/test_test_update.py"]
verification_only_paths: ["groundtruth-kb/tests/test_cli.py", "groundtruth-kb/tests/test_db.py", "groundtruth-kb/tests/test_pipeline_events.py", "groundtruth-kb/tests/test_cli_discoverability.py", "platform_tests/scripts/test_cli_artifact_read_verbs.py", "platform_tests/unit/test_knowledge_db_artifacts.py"]

implementation_scope: source_and_test_cli_service
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
kb_mutation_scope_note: no live or production KB mutation during implementation; the deliverable is a governed KB-mutation capability
production_test_artifact_mutation_in_scope: false

---

## Summary

Add one deterministic `gt tests update TEST-ID` service for governed semantic
changes to an existing Test artifact. The command appends one new Test version,
preserves every unspecified field and every Test Plan membership, exposes a
repeatable no-write dry-run, requires durable owner-decision evidence, and
rejects stale concurrent updates with an explicit expected-version compare and
swap.

This slice changes only the four declared source/test paths. It does not update
any production Test record, `groundtruth.db`, Test Plan, bridge configuration,
dispatcher, TAFE, Git ref, or index. After this generic command is independently
VERIFIED, production Test corrections—including TEST-11330, TEST-11350,
TEST-11341, and TEST-11811—must each use a separately authorized invocation of
the verified command. The implementation cannot validate itself by performing
those production mutations.

## Standing Backlog Bulk-Operation Disposition

This is not a bulk backlog operation and changes no Work Item or backlog row.
WI-5183 remains visible through the existing canonical backlog. A bulk-action
inventory, bulk review packet, and Phase/Path-deferred decision marker are
therefore not applicable to this exact four-target CLI implementation slice.

## Current Baseline And Scope Identity

Current repository HEAD at proposal preparation is
`75decbfa704fe50288aecbc5669def329a0825df`. The exact mutation cohort is clean:

| Path | Current SHA-256 / state | Intended ownership |
| --- | --- | --- |
| `groundtruth-kb/src/groundtruth_kb/cli.py` | `CE2C2942F75C22101D9B17E77E9D1EA1F7E27892F272073C9A0C48B51A75C853` | register the command and options only |
| `groundtruth-kb/src/groundtruth_kb/cli_test_update.py` | absent | new request validation and orchestration service |
| `groundtruth-kb/src/groundtruth_kb/db.py` | `F30A24F1785B23BBDF70BAB6AF9958F49FD40B1EB285BD31D598A12E99D506F7` | one transaction-local expected-version append primitive |
| `platform_tests/groundtruth_kb/cli/test_test_update.py` | absent | new focused contract suite |

WI-5183 is open/backlogged at version 2; TEST-11346 is the linked integration
test of record. No WI-5183 bridge thread or active claim exists at filing
preparation. Any hash, claim, PAUTH, project membership, or overlap change
invalidates this baseline and requires a new readback before implementation.

## Requirement Sufficiency

**Existing requirements are sufficient.** This proposal adds the missing
deterministic mutation route; it creates no new Test authority or lifecycle
state. `SPEC-1493` establishes Test as one of the append-only managed artifact
types, and `SPEC-1494` defines its spec-linked versioned record. The standing
backlog schema/authority carriers govern WI-5183 visibility, not Test-table
mutation semantics. `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` requires
exact, current, inspectable evidence. The owner-decision, audit, project,
bridge, claim, implementation-start, independent review, and verification
boundaries remain unchanged.

## Specification Links

- `SPEC-1493` — Test is a managed artifact type stored with append-only versioning and change control.
- `SPEC-1494` — a Test is a spec-linked, versioned artifact with durable change-control fields.
- `GOV-10` — executable evidence must exercise the production CLI surface rather than a direct database helper.
- `GOV-12` and `GOV-13` — work-item test authority and Test Plan phase visibility must remain durable and intact.
- `DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001` — updates may repair a tracked-incomplete triad but may not conceal it.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` and `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` — govern WI-5183/backlog visibility and keep direct work-item SQL or parallel backlog stores prohibited; they are not Test append authority.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` — dry-run, postimage, version, authority, and failure evidence must be deterministic and current.
- `GOV-STANDING-BACKLOG-001` — WI-5183 and TEST-11346 remain the durable work and acceptance carriers.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — semantic changes remain explicit, reviewable artifact transitions.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — read surfaces, phase membership, execution history, unrelated fields, and concurrent work must be preserved.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the project PAUTH never replaces GO, exact claim, or a fresh schema-v3 start packet.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` — current MemBase project membership order and dependency state, not proposal prose, control readiness.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — Test, specification, deliberation, claim, and target evidence must be re-read from the canonical store at operation time.
- `DCL-SESSION-ROLE-RESOLUTION-001` v7 — apply-time actor attribution must use the exact current session envelope and fail closed on conflicting or incomplete role evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — numbered bridge state, role eligibility, and independent review remain mandatory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — this proposal, its project authority, and executed verification evidence stay concretely linked.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all implementation and evidence paths remain under `E:/GT-KB`.

## Prior Deliberations

- `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` — authorizes the active project PAUTH while preserving every exact bridge, claim, start, test, verification, and finalization gate.
- `DELIB-202667517` — requires highly parallel Prime Builder operation and linearizable or conflict-detected shared-state mutations; unrelated accepted changes may not be overwritten.
- `DELIB-20260710-GTKB-MODERNIZATION-ARTIFACT-EVALUABILITY-DCL-APPROVAL` — owner approval for the deterministic artifact-evaluability constraint that WI-5183 makes operable for Test corrections.
- `DELIB-202665958` and `bridge/gtkb-modernization-gate-1-25-execution-design-001.md` / `-002.md` — the actual independently reviewed Gate 1.25 design chain and its fail-closed WI-5178-first ordering. The unrelated harvested records `DELIB-202666080`, `DELIB-202666081`, and `DELIB-202666082` are not Gate 1.25 authority and are intentionally not cited.
- The older non-live `gtkb-modernization-wi5183-governed-test-update-cli` draft was reviewed as design evidence only. Its obsolete PAUTH, `groundtruth.db` target, no-CAS database plan, decorated draft metadata, stale ordering, and broader target cohort are not carried forward.

## Owner Decisions / Input

No new owner decision is required to file this proposal. The owner already
authorized the Authority Foundations project envelope in
`DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` and has repeatedly
directed workers to use governed SoT CLI/skill/bridge surfaces rather than
serialize all work or bypass MemBase. That authority remains bounded: source or
test implementation still requires independent GO, the exact WI-5183 claim,
and a fresh schema-v3 start packet. Each later production Test update must cite
its own current `owner_decision` deliberation.

## Proposed Command Contract

1. Register `gt tests update TEST-ID` in `cli.py`; place all business logic in
   new `cli_test_update.py`.
2. Permit only these semantic postimage fields in this slice: `spec_id`,
   `test_file`, `test_class`, `test_function`, `expected_outcome`, and
   `application_scope`. `title`, `description`, `last_result`,
   `last_executed_at`, `test_type`, phase membership, and all other fields
   remain outside this command. Change provenance is mandatory command input,
   not a mutable Test postimage field.
3. Require non-empty `--change-reason`, exact `--owner-decision DELIB-*`, and
   mandatory `--expected-current-version N` on apply. The cited current
   deliberation must be readable through the canonical store and must carry
   `source_type=owner_conversation`, `outcome=owner_decision`, the exact Test
   ID and expected version, and the exact normalized postimage or its canonical
   digest. The receipt binds deliberation ID, deliberation version, and content
   hash; a token-shaped or merely owner-decision-shaped record is not evidence.
   Fresh AUQ evidence must first be captured as that canonical deliberation
   receipt through the governed decision-capture route. Reuse the independently
   independently VERIFIED WI-5282 base provenance predicate and coordinate its
   evidence-capture integration with WI-5712. Layer a WI-5183-specific binding
   validator over that base for exact Test ID, expected Test version,
   normalized before/after semantic maps, postimage digest, and deliberation
   ID/version/content hash; do not broaden or duplicate the base predicate.
4. Support `--clear-test-file`, `--clear-test-class`,
   `--clear-test-function`, and `--clear-application-scope` so omitted and
   cleared values cannot be confused. Reject a field supplied together with
   its clear option. Clearing `test_file` also requires class/function to be
   cleared or already null.
5. An eligible linked specification is the exact current canonical spec row:
   it exists, is not retired or superseded, and is readable in the same
   snapshot used for validation. A non-null `test_file` is normalized to one
   root-relative path whose resolved target remains under `E:/GT-KB` and is an
   existing regular file. Class/function values require a non-null file and
   must satisfy the bounded stored-identifier grammar. The command does not
   import application code or run pytest collection while mutating metadata;
   collection/execution validity remains spec-derived verification evidence,
   and success never claims the node executed. Reject empty prohibited values,
   no-op postimages, symlink/root escape, retired/missing specs, and over-bound
   scalar or total input before opening a write transaction.
6. `--dry-run --json` executes the same request, target, spec, normalization,
   owner-evidence, no-op, and expected-version preflight without resolving a
   write actor or creating a row, event, packet, file, or phase version. It
   returns the current version, proposed version, normalized changed fields,
   canonical `before` and `after` semantic maps keyed by every changed field,
   a complete canonical postimage digest, authority ID, and an explicit
   `attribution_required_on_apply` state.
7. JSON is stable for all outcomes. Apply success returns schema version,
   `ok=true`, command, Test ID, before/after versions, normalized changed-field
   names, the exact canonical `before` and `after` semantic maps, complete
   postimage digest, bound deliberation ID/version/content hash, and audit-event
   type. Every nonzero exit returns `ok=false` plus a typed
   `error.code`, phase, bounded message, retryable flag, Test ID, expected and
   observed versions when known, and `mutation_count=0`; it never emits a
   traceback as the machine contract.
8. Apply resolves current actor provenance only after the complete read-only
   preflight. Under one `BEGIN IMMEDIATE` transaction, `db.py` re-reads the
   target version, linked-spec eligibility, complete owner-evidence snapshot,
   and normalized postimage. It rejects stale expected-version, authority, or
   postimage drift; appends exactly one Test version; and records exactly one
   bounded `test_updated` audit event carrying before/after versions, changed
   field names, and the bound deliberation receipt. It then reads back that
   exact version before commit/result.
9. Every unspecified Test field, prior Test version, Test Plan membership,
   execution result/timestamp, and unrelated artifact remains byte- or
   value-equivalent. Any exception rolls back the Test row and audit event
   together.
10. Existing `KnowledgeDB.update_test` callers and their `test_executed`
    pipeline-event behavior remain unchanged. The new semantic-update primitive
    is additive and must not relabel result recording or emit semantic events
    for legacy execution-result calls.
11. The validated owner-decision record, exact Test version,
   changed-by/change-reason fields, and transaction-local audit event form the
   durable receipt. The command creates no additional managed artifact type.

## Serialization, Dependencies, And Start Holds

This proposal is reviewable now but implementation is disabled until all of
the following are true at operation time:

1. Current project membership order places WI-5178 at 9 and WI-5183 at 10.
   WI-5178 must first reach its governed terminal/superseded state or the
   project order must be changed through the canonical CLI and independently
   accepted. Prose does not override that order.
2. WI-5483's immutable v005 carries malformed decorated Version metadata and
   its historical proposal declares `cli.py` and `db.py`. The strict resolver
   currently fails `WRONG_BRIDGE_VERSION_METADATA`. WI-5183 cannot start until
   a governed strict-chain recovery/narrowed successor is independently
   accepted or WI-5483 is terminal with an accepted exact non-overlap ledger.
3. WI-5282 v009 is a current shared-target and functional base-validator
   dependency on both `cli.py` and `db.py`. WI-5183 cannot start until the base
   owner-evidence predicate is independently VERIFIED and reusable. An
   independently accepted exact non-overlap ledger may resolve target ownership
   only; it cannot replace this functional dependency or the WI-5183-specific
   Test/version/postimage binding layer.
4. WI-5883 is a prospective Test-record consumer and shared-`db.py` hold, not
   a canonical dependency. WI-5899 is forecast dependency/readiness work and
   currently has no bridge target declaration; either must remain unclaimed
   for an overlapping target while a WI-5183 packet is active.
5. Known current logical overlaps include WI-5271, WI-5282, WI-5311, WI-5441,
   WI-5483, WI-5593, and WI-5615. This list is evidence, not an exhaustive
   ledger. A canonical exact-path scan must be rerun at filing, claim, and
   schema-v3 start; every current nonterminal overlap must be terminal,
   withdrawn, unclaimed, or covered by an independently accepted exact
   non-overlapping hunk ledger.
6. The four exact target hashes/states, active project PAUTH, claim registry,
   named implementation packets, and cross-claim target collision result must
   be re-read immediately before claim and again before every protected write.

No global worker quiescence, dispatcher mutation, timer reduction, or foreign
claim takeover is authorized. Only the short database transaction is
serialized; unrelated workers continue normally.

## Cross-Harness Disposition

The command, validation, JSON schema, owner-evidence rule, CAS result, and
failure behavior are identical for Claude, Codex, Cursor, Goose, Antigravity,
Ollama, OpenRouter, and other registered harnesses. Actor attribution comes
from the canonical session/role resolver at apply time. No harness-local
memory, vendor-specific write path, shared harness role, or dispatcher config
is accepted as mutation authority.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "primary_route": "gt tests update TEST-ID --expected-current-version N --owner-decision DELIB-ID --change-reason TEXT",
  "baseline": "gt tests exposes read-only show/list routes, while governed semantic Test correction has no canonical CLI mutation service.",
  "canonical_authority": "MemBase current Test, specification, deliberation, Test Plan, and event records are authoritative; the CLI is a validated transaction service over that authority, never a parallel store.",
  "expected_result": "One authorized apply appends exactly Test version N+1 plus one bounded test_updated event and returns their exact receipt; every rejected request appends nothing.",
  "fail_closed_conditions": [
    "missing, stale, unrelated, or changed owner-decision evidence",
    "missing Test or ineligible linked specification",
    "expected-version, normalized-postimage, target, PAUTH, claim, start, or overlap drift",
    "invalid, empty, conflicting, no-op, out-of-root, or over-bound input",
    "transaction contention or injected persistence failure without a complete atomic receipt"
  ],
  "hard_invariants": [
    "append-only Test history",
    "exact expected-version compare and swap",
    "one Test row and one semantic audit event commit atomically",
    "all unspecified fields, phase membership, execution evidence, and unrelated worker changes are preserved",
    "no production Test mutation occurs while implementing or testing the capability"
  ],
  "history_preservation": "Prior Test versions and events are never rewritten or deleted; a later correction supersedes an incorrect postimage with a new owner-evidenced append.",
  "provenance": "WI-5183 under PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS and its active PAUTH supplies project scope; each production invocation separately binds a current exact owner-decision deliberation receipt.",
  "self_descriptive_naming": "The canonical command is the unsurprising artifact-group verb gt tests update; helper names describe Test semantic update and expected-version behavior without harness-specific aliases.",
  "before_behavior": "Workers can read Test artifacts through gt tests show/list but cannot governably append a semantic correction; one-off direct KnowledgeDB calls have been used as an unsafe workaround.",
  "after_behavior": "The obvious tests command performs a bounded, owner-evidenced, expected-version append and returns deterministic before/after evidence.",
  "essential_context_preservation": "Every prior Test version, unspecified field, phase membership, execution result, and unrelated worker mutation is preserved.",
  "obsolete_guidance_disposition": "Direct SQL, raw KnowledgeDB update snippets, groundtruth.db target ownership, and the stale non-live WI-5183 draft are explicitly non-authoritative.",
  "rollback": "Revert only the four reviewed code/test paths through a separately governed change; any incorrect production Test postimage is superseded by another owner-evidenced append, never deleted or rewritten."
}
```

## Spec-Derived Verification Plan

Linked test of record: `TEST-11346`, **gt tests update is governed,
append-only, and deterministic**.

| Assertion | Governing specifications | Required executable evidence |
| --- | --- | --- |
| `WI5183-A1` command and dry-run | `GOV-10`, `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Help exposes the bounded options; repeated dry-runs return exact canonical before/after semantic maps plus normalized-equivalent complete postimages/digests and append no Test/event/file/phase version even when write-attribution resolution would fail. |
| `WI5183-A2` owner and target authority | `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `GOV-STANDING-BACKLOG-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Missing, unknown, wrong-source, unrelated owner-decision, stale deliberation version/hash, Test/version/postimage mismatch, missing-Test, ineligible-spec, out-of-root/nonexistent/non-regular file, symlink escape, invalid stored-identifier grammar, empty, over-bound, conflicting-clear, and no-op requests fail with zero mutations. Focused nodes separately prove explicit `application_scope` clearing, omitted-versus-cleared preservation, and the required test-file/class/function clear cascade. |
| `WI5183-A3` append-only CAS | `SPEC-1493`, `SPEC-1494` | One valid request appends exactly version N+1 and one audit event. A deterministic two-connection same-N race yields exactly one N+1 winner; the loser receives typed stale/busy JSON with zero mutation. Injected failures roll back row and event. |
| `WI5183-A4` preservation | `GOV-13`, `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Every unspecified value, prior version, phase membership, last result, last execution time, and unrelated record is unchanged. |
| `WI5183-A5` read and pipeline compatibility | `DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001` | Existing `gt tests show/list`, CLI discoverability, database artifact, and pipeline-event suites remain compatible; legacy `update_test` result recording preserves its event semantics while the new current version remains projection-safe. |
| `WI5183-A6` stable machine results | `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Dry-run, apply success, every typed rejection, stale/busy contention, and injected rollback return their declared stable JSON schemas and exit codes with no traceback leakage. |
| `WI5183-A7` governance gates | project/bridge/verification specifications | Applicability and mandatory-clause gates pass on exact report bytes; an independent session reviews implementation and executed evidence before any VERIFIED disposition. |

Required focused and adjacent commands (trust actual collection counts):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/cli/test_test_update.py groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_pipeline_events.py groundtruth-kb/tests/test_cli_discoverability.py platform_tests/scripts/test_cli_artifact_read_verbs.py platform_tests/unit/test_knowledge_db_artifacts.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_test_update.py groundtruth-kb/src/groundtruth_kb/db.py platform_tests/groundtruth_kb/cli/test_test_update.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_test_update.py groundtruth-kb/src/groundtruth_kb/db.py platform_tests/groundtruth_kb/cli/test_test_update.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_test_update.py groundtruth-kb/src/groundtruth_kb/db.py platform_tests/groundtruth_kb/cli/test_test_update.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_test_update.py groundtruth-kb/src/groundtruth_kb/db.py platform_tests/groundtruth_kb/cli/test_test_update.py
```

## Risk / Rollback

The principal risks are a stale-read lost update, a broad semantic mutation
surface, partial row/event persistence, or accidental production-Test changes
during tool verification. Mandatory expected-version CAS, the exact field
whitelist, transaction-local revalidation, bounded owner evidence, temp-DB
tests, and the explicit production-mutation exclusion constrain those risks.

Rollback does not rewrite artifact history. A defective implementation is
reverted only through a separately governed exact four-path change. A bad Test
postimage is superseded by another verified-command append with new owner
evidence. No production rollback is part of this proposal.

## Bridge Filing

This proposal is the first status-bearing file for
`gtkb-wi5183-governed-test-artifact-update-cli`. The older runtime draft uses a
different slug and is not live bridge authority. Filing must use the governed
credential-scanned writer and append-only numbered chain; no aggregate queue,
dispatcher activation, or direct bridge-file write is authorized.

## Recommended Commit Type

`feat` — introduces one missing governed CLI service and its focused contract
tests without changing existing Test records.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
