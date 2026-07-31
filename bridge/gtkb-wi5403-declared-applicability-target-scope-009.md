NEW
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# WI-5403 Declared Applicability Target-Scope Hunk Separation Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5403-declared-applicability-target-scope
Version: 009 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5403-declared-applicability-target-scope-008.md
Approved proposal: bridge/gtkb-wi5403-declared-applicability-target-scope-007.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5403-DECLARED-TARGET-SCOPE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5403
target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]
Recommended commit type: fix:

## Implementation Claim

Prime Builder implemented exactly the version-007/version-008 correction:
the existing `declared_target_paths` and `applicability_path_evidence`
Markdown expressions now render immediately after `bridge_document_name`
instead of immediately after `preflight_passed`.

The rendered field names and values are unchanged. The relocation puts the
two WI-5403 expressions in default-context hunk `@@ -527,6 +660,8 @@`, while
WI-5408's foreign `blocking_errors` expression remains in separate hunk
`@@ -535,6 +670,7 @@`. No WI-5387 or WI-5408 byte was changed. The test file
remains byte-identical to the approved pre-start boundary.

## Implementation Authorization Evidence

- Active PAUTH:
  `PAUTH-DISPATCHER-BLACK-BOX-WI5403-DECLARED-TARGET-SCOPE-20260717`,
  version 1, scoped only to WI-5403 and the exact two targets.
- Approved proposal:
  `bridge/gtkb-wi5403-declared-applicability-target-scope-007.md`.
- Independent GO:
  `bridge/gtkb-wi5403-declared-applicability-target-scope-008.md`.
- Work-intent claim: row `32712`, kind `go_implementation`, acquired
  `2026-07-18T07:43:16Z`.
- Schema-v3 implementation authorization packet:
  `sha256:dc69a2144d28295362f7a6233aad08e1032402afd53bc791c68663404bfccf38`.
- Pre-start packet:
  `sha256:3bca4077f2d1e058fa0d51bfed5222ac8dc0cac53193b20692357e7eb5690b62`.
- Pre-start source SHA-256:
  `f88c46da39e36ac33fd47b7fc73284ef19453d6034dba810091686619b5fbcf2`.
- Post-change source SHA-256:
  `bb82d051ff80b45112af37dd703b0ab082eba6018e3697d7afc24eca60d1bea6`.
- Pre-start and post-change test SHA-256:
  `df9478795918c64cf4574557f82aa5e6794cb1abf549b17797fb806c678b74bf`.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` is the owner
  authority carried by the active bounded PAUTH.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` remains
  controlling. This implementation did not inspect or mutate dispatcher
  configuration, TAFE state, runtime state, harness registry, or workers.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` is honored. This
  report cites only MemBase decisions and work authority plus numbered bridge
  artifacts. No scratch artifact is cited or retained.
- No new owner decision is required.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD`
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY`
- `bridge/gtkb-wi5403-declared-applicability-target-scope-005.md`
- `bridge/gtkb-wi5403-declared-applicability-target-scope-006.md`
- `bridge/gtkb-wi5403-declared-applicability-target-scope-007.md`
- `bridge/gtkb-wi5403-declared-applicability-target-scope-008.md`

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`

## Specification-Derived Verification

| Specification / invariant | Executed evidence | Observed result |
| --- | --- | --- |
| Declared-target behavior; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Two named WI-5403 pytest nodes in ambient and isolated HEAD-plus-WI-5403 candidate states | PASS: 2/2 in each state; rendered names and values remain present |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Full applicability suite in ambient and isolated candidate states | Ambient PASS: 33 passed. Isolated honest result: 5 failed, 25 passed; only the five pre-existing WI-5408 PAUTH-amendment assertions failed |
| `GOV-WORK-TREE-HYGIENE-001`; `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Default-context source diff plus exact pre/post hashes | PASS: WI-5403 output lines and WI-5408 `blocking_errors` are separate native hunks; test hash unchanged |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Active PAUTH, independent v008 GO, row 32712 claim, schema-v3 start | PASS: exact WI, project, session, and two targets authorized before mutation |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `GOV-STANDING-BACKLOG-001`; artifact lifecycle specifications | Current numbered chain and WI-5403 MemBase authority | PASS: report is v009 on the approved project/work item and remains nonterminal pending independent verdict |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Exact changed/candidate path review | PASS: both targets and every generated test input remained in-root; no adopter path |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001`; implementation proposal linkage | Applicability and mandatory clause preflights | PASS: no missing required/advisory specs, no blocking errors, no clause gaps |
| `SPEC-AUQ-POLICY-ENGINE-001` | Owner-input and waiver review | PASS: no waiver used; active PAUTH carries the recorded owner decision |

## Isolated-State Arithmetic Correction

Version 008 predicted `5 failed / 26 passed` by stating that the ambient suite
contained two foreign net-new tests. Current canonical Git evidence shows five
uncommitted test additions relative to HEAD: three WI-5387 operative-selection
tests and the two WI-5403 tests. Therefore the exact HEAD-plus-WI-5403
candidate collects 30 tests, not 31, and its mathematically correct result is
`5 failed / 25 passed`.

This count correction does not hide a WI-5403 regression:

- both WI-5403-owned tests pass in isolation;
- the failure set is exactly the five pre-existing PAUTH-amendment tests named
  by versions 007 and 008;
- ambient remains 33/33 passing with the foreign WI-5387/WI-5408 source bytes;
- no additional failure appeared.

## Commands Run

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5403-declared-applicability-target-scope --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5403-declared-applicability-target-scope`
- `python scripts/bridge_claim_cli.py claim gtkb-wi5403-declared-applicability-target-scope --session-id 019f6668-9974-7d72-a456-826f9a67e627`
- `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5403-declared-applicability-target-scope --session-id 019f6668-9974-7d72-a456-826f9a67e627`
- `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py::test_declared_target_paths_exclude_incidental_applicability_evidence platform_tests/scripts/test_bridge_applicability_preflight.py::test_packet_separates_declared_scope_from_applicability_path_evidence -q --tb=short`
- `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short`
- The same two pytest commands against a same-session isolated candidate synthesized from committed HEAD plus only the exact WI-5403 logical changes; the candidate was removed before filing and is not cited as an artifact.
- `python -m ruff check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py`
- `python -m ruff format --check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py`
- `python -m py_compile scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py`
- `git diff --check -- scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py`
- `git diff --unified=3 -- scripts/bridge_applicability_preflight.py`

## Observed Results

- Operation-time applicability: PASS,
  `missing_required_specs=[]`, `missing_advisory_specs=[]`,
  `blocking_errors=[]`.
- Mandatory clause preflight: PASS, five clauses, four `must_apply`, zero
  evidence gaps, zero blocking gaps.
- Ambient focused tests: 2 passed.
- Ambient full suite: 33 passed.
- Isolated focused tests: 2 passed.
- Isolated full suite: 5 failed, 25 passed. Exact expected foreign failures:
  - `test_preflight_reports_structured_pauth_amendment_blocking_error`
  - `test_preflight_accepts_structured_pauth_amendment_with_exact_owner_evidence`
  - `test_preflight_rejects_out_of_root_pauth_approval_path`
  - `test_preflight_rejects_malformed_pauth_approval_json`
  - `test_preflight_rejects_invalid_nonowner_or_noncovering_pauth_packet`
- Ruff check: PASS.
- Ruff format check: PASS.
- `py_compile`: PASS.
- `git diff --check`: PASS.
- The first formatter write attempt encountered a temporary Windows
  user-mapped-section lock; a bounded retry succeeded and restored the file's
  existing all-CRLF EOL profile. Final diff checks and hashes above are from
  the corrected bytes.

## Applicability Preflight

- Candidate canonical file:
  `bridge/gtkb-wi5403-declared-applicability-target-scope-009.md`.
- content_source: `pending_content`.
- packet_hash before recording this result subsection:
  `sha256:dc00671824e49e90a00763bef00f3f1f3c54d7bffac4491d2cb23f62d1dfd99c`.
- preflight_passed: `true`.
- declared_target_paths:
  `["platform_tests/scripts/test_bridge_applicability_preflight.py", "scripts/bridge_applicability_preflight.py"]`.
- missing_required_specs: `[]`.
- missing_advisory_specs: `[]`.
- blocking_errors: `[]`.

## Clause Applicability

- Candidate canonical file:
  `bridge/gtkb-wi5403-declared-applicability-target-scope-009.md`.
- Clauses evaluated: 5.
- `must_apply`: 4.
- `may_apply`: 1.
- Evidence gaps in `must_apply` clauses: 0.
- Blocking gaps: 0.
- Mandatory result: PASS, exit 0.

## Files Changed

- `scripts/bridge_applicability_preflight.py`
  - Only the two existing WI-5403 Markdown expressions moved relative to the
    approved pre-start hash.
- `platform_tests/scripts/test_bridge_applicability_preflight.py`
  - No byte changed in this implementation step; the two existing WI-5403
    tests remain the approved exact test hunk.

All WI-5387, WI-5408, dispatcher, TAFE, runtime, harness, database,
credential, external-system, deployment, release, push, Git-history, and
other dirty paths are excluded.

## Acceptance Criteria Status

- [x] Field text and values are unchanged.
- [x] WI-5403 output and WI-5408 `blocking_errors` occupy separate native
  default-context hunks.
- [x] No synthesized sub-hunk or owner waiver is used.
- [x] Both WI-5403 tests pass in ambient and isolated states.
- [x] Ambient full suite is 33 passed.
- [x] Isolated full suite exposes only the same five foreign failures.
- [x] The one-count arithmetic discrepancy is disclosed and mechanically
  explained rather than concealed.
- [x] Ruff, format, compile, and diff checks pass.
- [x] Test hash is unchanged.
- [x] No dispatcher configuration/runtime or other forbidden operation ran.
- [ ] Independent Loyal Opposition VERIFIED.
- [ ] Atomic hunk-scoped finalization after independent VERIFIED.

## Risk And Rollback

Residual risk is limited to shared-file finalization. The repository currently
contains separately owned WI-5387 and WI-5408 hunks in both target files.
Independent verification must stage only the native WI-5403 source hunks and
the two named WI-5403 tests, preserving every foreign byte. WI-5501 records
the concurrent-finalizer rollback defect, so finalization must be serialized.

Rollback moves only the two Markdown expressions back to their pre-start
position through a governed correction. Bridge history remains append-only.

## Loyal Opposition Asks

1. Reproduce the two native source hunks and both tree-state test results.
2. Confirm the isolated one-count correction from current HEAD/test inventory.
3. Confirm no WI-5387 or WI-5408 byte enters the finalization patch.
4. Return VERIFIED only if the exact WI-5403 patch and all linked requirements
   pass; otherwise return NO-GO with exact findings.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
