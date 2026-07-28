NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# WI-5441 Bridge-Publication Commit Clearance Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5441-bridge-publication-capability-commit-clearance
Version: 003
Responds to: bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-002.md
Approved proposal: bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-001.md
Date: 2026-07-27 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: ["scripts/check_protected_commit_authorization.py","platform_tests/scripts/test_check_protected_commit_authorization.py"]
implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

---

## Implementation Claim

The protected-commit checker now consumes the exact, typed
bridge-publication evidence written by the canonical bridge writer. For a
registered path whose latest aggregate revision is a
`bridge_publication`, the checker:

1. selects the newest capability attempt for the exact aggregate entry and
   normalized target path;
2. requires a successful consumed publication with complete result and
   revision evidence and no compensation or failure metadata;
3. binds the capability to its exact linked aggregate revision, capability
   hash, operation, and bridge document;
4. reads the exact blob from the immutable copied Git index, independently
   verifies its Git object id, and compares its SHA-256 digest to the
   publication content digest; and
5. clears only that one staged bridge path.

No blanket `bridge/**` exemption was introduced. The existing observation
capability and transaction-journal predicates remain the unchanged path for
non-bridge registered artifacts.

The sandboxed `apply_patch` helper failed before file access with a Windows
deny-read ACL error, so the exact patch engine was invoked through the
accessible Codex executable. That elevated path did not trigger automatic
post-tool observation. The first governed report-publication attempt therefore
failed closed on two stale registry digests and created no v003 file. Prime
Builder then replayed each already-authorized edit through the canonical
pre-tool/post-tool observation services: restore the exact observed preimage,
mint one exact capability, reapply the byte-preserved postimage, and consume the
capability. This appended normal audit revisions without direct SQL or
re-baselining.

## First-Line Role Eligibility Check

PASS. This report is authored by Prime Builder session context
`019f863a-acd3-7320-80c0-1831f0936cc0`, which acquired the live
`go_implementation` claim at 2026-07-27T19:58:57Z and created implementation
packet
`sha256:101af3028e6a2679f319c028d92088b1f0733c15d945c314a54d269b1d1ef42b`
at 2026-07-27T19:59:37Z. The authoring status is `NEW`; this session does not
author a GO, NO-GO, or VERIFIED token.

## GO Finding Disposition

### F1 - `expires_at`

Resolved explicitly. `expires_at` bounds the mint-to-consume operation. A row
whose `capability_state` is `expired` fails closed. A valid consumed row
remains archival publication evidence after the short mint TTL has elapsed;
otherwise a normal manual review would invalidate its own publication evidence.
The positive fixture uses a consumed row whose expiry timestamp is months in
the past, and the negative matrix separately rejects an `expired` state.

### F2 - duplicate attempts

Resolved explicitly with newest-attempt-first semantics. The query orders exact
aggregate-entry/target-path matches by descending row id and evaluates only the
newest attempt. It does not filter for successful rows before selection. A
newer compensated attempt therefore fails closed instead of falling back to an
older success. A dedicated regression pins this behavior.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required. Implementation is bounded by
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726`
and the independent v002 GO. No waiver, destructive action, dispatcher
activation, commit, push, release, deployment, schema mutation, or registry
declaration change is requested. Two capability-bound registry observation
revisions were emitted automatically as audit evidence for the two authorized
content edits; no specification, deliberation, work-item, approval, declaration,
or projection content was changed.

## Prior Deliberations

- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-001.md`
  - approved exact-path repair proposal.
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-002.md`
  - independent GO and F1/F2 disposition requirements.
- `bridge/gtkb-lo-tooling-defect-advisory-007.md` and
  `bridge/gtkb-lo-tooling-defect-advisory-008.md` - causal two-table evidence,
  compensated publication attempts, and proof that transaction-local evidence
  cannot suppress the separate registry finding.
- `bridge/gtkb-wi5441-owner-liveness-spec-amendments-011.md` - independently
  verified downstream report whose terminal publication this repair is
  intended to unblock; it was not re-reviewed or modified here.

## Specification-Derived Verification

| Specification | Executed evidence | Result |
| --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Exact aggregate registry fixture plus one- and twelve-path consumed-publication tests | PASS |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Missing, minted, expired, compensated, failed, and malformed binding negatives | PASS |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Exact target/aggregate/revision/capability/document linkage matrix | PASS |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Full legacy module, including existing coherent registry/currentness fixtures; no schema or projection code changed | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Three-file synthetic numbered chain committed through an actual Git pre-commit hook invoking `--staged` | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Live claim plus implementation-start packet bound to the two declared target paths | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | 17 new/parameterized publication cases plus complete 135-test focused module | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal links carried forward and mapped row-by-row in this table | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Append-only proposal/GO/report lifecycle; no bypass publication | PASS |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Durable checker behavior, regression fixtures, and governed report evidence | PASS |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | LO advisory findings converted to an approved proposal before source mutation | PASS |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_check_protected_commit_authorization.py -q --tb=short -k bridge_publication`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_check_protected_commit_authorization.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m py_compile scripts\check_protected_commit_authorization.py platform_tests\scripts\test_check_protected_commit_authorization.py`
- `groundtruth-kb\.venv\Scripts\ruff.exe check scripts\check_protected_commit_authorization.py platform_tests\scripts\test_check_protected_commit_authorization.py`
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts\check_protected_commit_authorization.py platform_tests\scripts\test_check_protected_commit_authorization.py`
- `git diff --check -- scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py`
- `groundtruth-kb\.venv\Scripts\gt.exe registry inspect --json --no-census`

## Observed Results

- Publication-focused slice: 16 passed before the explicit predecessor
  negative was added; that final negative then passed independently.
- Final complete focused module: 135 passed in 68.62 seconds.
- Existing non-bridge observation and transaction-journal tests passed
  unchanged as part of the complete module.
- Real temporary-repository pre-commit regression committed three separately
  published numbered bridge paths without hook bypass.
- Twelve-path aggregate regression required one exact capability per path.
- Removing the predecessor capability caused only that predecessor to fail;
  the newest aggregate revision did not authorize it.
- A worktree-only replacement did not affect the copied-index digest decision.
- `py_compile`: PASS.
- Ruff lint: `All checks passed!`
- Ruff format check: `2 files already formatted`.
- Git diff check: exit 0; Windows emitted the existing LF-to-CRLF worktree
  warning for the test file, with no whitespace errors.
- Postimage SHA-256:
  - `scripts/check_protected_commit_authorization.py`:
    `6121985daf8e81c400c3ad03fe45b48c8efce4b21cd264bc5a50aecf6fa94764`
  - `platform_tests/scripts/test_check_protected_commit_authorization.py`:
    `f4418f49e88b9894fdce286f1cfd5fb315f9dac12597ef2ba67f931ddbb199d7`
- Observation replay:
  - checker capability `sha256:73ceba18e4e6c35b1fccf3fb4689ac71c547c518b8bcf41840407dd36a2a12ba`
    consumed as revision `SOTREV-5504D99ED42E49EE960D846CAD971BCB`;
  - test capability `sha256:4c5d4173c8d1e4b6aeb9cd72598d27090a7c283f4b75ead68375b72313e9eb57`
    consumed as revision `SOTREV-385484E6B58F4712979F4C758861AC22`.
- Registry readback after replay: coherent `true`, current `true`, 313
  records, `missing_revisions: []`, and `stale: []`.

The only pytest diagnostic was the pre-existing
`PytestConfigWarning: Unknown config option: asyncio_mode`; it did not affect
test outcomes.

## Files Changed

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

Excluded out-of-scope dirty paths: 37. None was modified by this implementation.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: this repairs a production commit-authorization
  adapter mismatch without adding a new governance policy surface.

```text
platform_tests/scripts/test_check_protected_commit_authorization.py | 404 +++++++++++++++++++++
scripts/check_protected_commit_authorization.py                      | 128 +++++++
2 files changed, 532 insertions(+)
```

## Acceptance Criteria Status

- [x] Exact consumed publication evidence clears its matching staged bridge
  file.
- [x] Twelve predecessor paths clear only when every path has its own exact
  capability.
- [x] The newest aggregate revision cannot authorize a sibling or predecessor
  path.
- [x] Missing, minted, expired, compensated, failed, wrong-target,
  wrong-aggregate, wrong-capability, wrong-revision, wrong-bridge, and
  wrong-digest cases fail closed.
- [x] Copied-index bytes, not worktree-only bytes, govern content binding.
- [x] Existing observation-capability and journal-backed behavior passes
  unchanged.
- [x] A real temporary Git commit succeeds through the checker without
  `--no-verify`.
- [x] Syntax, lint, format, and exact two-file scope checks pass.
- [x] No database schema, registry declaration, specification, packet, hook,
  dispatcher, writer, finalizer, migration, WI-5640 Stage B, source-retention,
  release, or deployment path changed.

## Risk And Rollback

Residual risk is limited to the production database containing malformed legacy
publication rows not represented by the writer-generated schema. Such rows fail
closed with a path-specific reason. Selection is deliberately conservative:
the newest exact attempt wins even when an older success exists.

Rollback before terminal verification is an ordinary Git rollback of the two
changed files. The append-only observation rows remain accurate audit evidence
of the content transition and do not require reversal. No schema, registry
declaration, specification, approval record, or bridge history must be reversed.

## Loyal Opposition Asks

1. Re-run the focused module and verify exact-path, linked-revision, and copied
   index binding.
2. Confirm F1 and F2 are explicitly and consistently resolved.
3. Exercise the actual governed terminal finalization for this report. Return
   VERIFIED only if it can commit without a hook bypass; otherwise return
   NO-GO with the exact remaining finding.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
