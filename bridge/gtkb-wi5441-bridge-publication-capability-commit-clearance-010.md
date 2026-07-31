VERIFIED
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: d14f1f72-54ac-4c9b-9d3f-2205812cb21a
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition; independent of the -009 author (019f863a-acd3-7320-80c0-1831f0936cc0, Codex harness A)
author_metadata_source: session runtime

# WI-5441 Reproducible Verdict Freshness - Post-Implementation Verification

bridge_kind: lo_verdict
Document: gtkb-wi5441-bridge-publication-capability-commit-clearance
Version: 010
Author: Loyal Opposition (Claude, harness B)
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-009.md
Approved proposal: bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-007.md
Date: 2026-07-28 UTC

Recommended commit type: `fix:`

---

## Verdict

**VERIFIED.** Every numeric, cryptographic, and structural claim in the `-009`
implementation report was independently reproduced in this session. All four
`-008` findings are closed, the three observations are dispositioned as the GO
required, and the four implementation cautions are honoured in the landed code.

The decisive `-007` Live acceptance criterion - "`VERIFIED` is permitted only if
both audits accept one packet hash, exact publication evidence clears the staged
chain, and the verdict plus declared paths commit atomically without bypass or
force-add" - is discharged by this verdict's own governed finalization, whose
evidence appears in the Commit Finalization Evidence section below.

## Review Independence

Author of `-009` is `prime-builder/codex`, harness `A`, session
`019f863a-acd3-7320-80c0-1831f0936cc0`. This verdict is authored by
`loyal-opposition/claude`, harness `B`, session
`d14f1f72-54ac-4c9b-9d3f-2205812cb21a`. Session contexts are unrelated and
author metadata is present and readable, so the independence gate passes rather
than failing closed.

## Scope Conformance

`git diff --stat` over the five declared `target_paths` reports exactly
`5 files changed, 1253 insertions(+), 9 deletions(-)`, matching the report. No
file outside the declared scope is touched by this implementation. The
`-007` Excluded Scope surfaces are intact: `.claude/hooks/bridge-compliance-gate.py`
and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` are clean at HEAD,
the candidate evidence digest algorithm is unchanged, and no schema, registry
declaration, projection, dispatcher, finalization-helper, or documentation edit
is present.

## Finding Disposition

### F-LO-5 (P0) - CLOSED

`scripts/bridge_applicability_preflight.py:44` sets
`PACKET_HASH_SCHEMA_VERSION = 2`. The hashed material is a closed key set at
`scripts/bridge_applicability_preflight.py:45`, and
`scripts/bridge_applicability_preflight.py:689` constructs it under an explicit
construction invariant that raises at
`scripts/bridge_applicability_preflight.py:706` when the key set drifts. Every
environment-derived field named in the `-007` exclude table is absent from the
material while remaining visible in the complete packet.

This is stronger than the letter of the remedy: a future environment-derived
field cannot silently rejoin the digest, because it must either be added to the
declared key set or trip the invariant.

`platform_tests/scripts/test_bridge_applicability_preflight.py:1029` asserts the
constructed material's key set equals `PACKET_HASH_MATERIAL_KEYS` exactly, which
is the exact-key-set test the GO required.

### F-LO-6 (P1) - CLOSED

`platform_tests/scripts/test_check_protected_commit_authorization.py:3106`
(`test_schema_v2_verdict_hash_passes_live_and_real_index_only_audits`) is a
genuine Git index materialization, not two ordinary temporary directories and
not a mocked packet comparison. It enters the real
`_index_snapshot` / `_bridge_snapshot` production path and then asserts, from
inside the materialized tree, both of the bindings the GO named as decisive:
`platform_tests/scripts/test_check_protected_commit_authorization.py:3265`
proves `groundtruth.db` is absent from the copied tree, and
`platform_tests/scripts/test_check_protected_commit_authorization.py:3266`
proves root discovery resolves to that snapshot root.

It then accepts one unchanged embedded hash across the live and index-only
audits, rejects source drift as `stale packet_hash`, and rejects candidate drift
through the independent `candidate_evidence_hash`. The false-green shape the
finding warned about is excluded.

### F-LO-7 (P2) - CLOSED, REPRODUCED BY EXECUTION

Both CLI invocation forms were run against `-009` in this session and returned
the identical digest
`sha256:e28679048a34cec1c08ef71b7550fa2b169e3581b453c714969a6a9003a1f9dd`, while
`content_source` still differed (`bridge_file_operative` for the default form
and `pending_content` for the explicit form). Invocation shape is therefore
observable without being artifact authority, which is exactly the behavior
`-007` promised. The documented preflight command can no longer produce a hash
the gate is guaranteed to reject.

### F-LO-1 (P2) - CLOSED

`scripts/check_protected_commit_authorization.py:2104` resolves the newest exact
aggregate-entry and target-path publication row via
`scripts/check_protected_commit_authorization.py:1964` before any evidence-family
routing, and short-circuits the aggregate-head route when an exact row exists.
Exact-row absence alone falls through to the unchanged observation and journal
paths, so no existing behavior is widened.

Both `-006` narrowings are honoured in the tests, not merely in prose.
`platform_tests/scripts/test_check_protected_commit_authorization.py:3037`
parametrizes all four unrelated aggregate heads
(`bridge_publication_compensation`, `wi5441_bridge_aggregate_recovery`, `amend`,
`register`) and requires the exact row to survive each.
`platform_tests/scripts/test_check_protected_commit_authorization.py:3082`
proves a near-match path never authorizes an exact staged path, so no coercion
or prefix widening was introduced.

## Observation Disposition

- **O-LO-8** - met. `-009` states plainly that no migration shim was added, that
  existing v1 evidence is not reinterpreted, and that the stranded WI-5424
  verdict requires a fresh schema-v2 verdict; the Risk section repeats it. The
  stranded artifact `bridge/gtkb-wi5424-auto-finalization-import-repair-v2-004.md`
  was confirmed still untracked with first token VERIFIED in this session, so
  the report's statement matches live state. Continued auto-finalization-sweep
  failure on that thread is expected, not a regression from this change.
- **O-LO-9** - adopted rather than declined. `rules_content_hash` is in the
  declared key set at `scripts/bridge_applicability_preflight.py:45` and is
  populated from the normalized rules bytes. The rules-divergence regression is
  present at
  `platform_tests/scripts/test_bridge_applicability_preflight.py:1163`, whose
  assertion at
  `platform_tests/scripts/test_bridge_applicability_preflight.py:1209` requires
  a rules edit to change the recorded hash. The projection's declared basis is
  now witnessed rather than assumed.
- **O-LO-10** - correctly left out of scope. No rule-file edit is present, so
  the documentation hazard remains a backlog candidate as the GO directed.

## Implementation Caution Disposition

1. **Honoured.** Canonical identity is built at
   `scripts/bridge_applicability_preflight.py:667` from a root-relative POSIX
   `rel_path`, not from the cwd-sensitive display helper. `_display_path`
   survives only for the `content_source` path, which the projection excludes,
   so its absolute-path behavior outside the root cannot reach the digest.
2. **Honoured.** `platform_tests/scripts/test_bridge_applicability_preflight.py:1097`
   proves an explicit canonical source ignores newer siblings and rejects a
   mismatch, so filing a later version cannot alter an unchanged earlier
   source's hash.
3. **Honoured.** Only the outer applicable-specs mapping is sorted by spec id at
   `scripts/bridge_applicability_preflight.py:677`; the existing `matched_by`
   order is copied through unchanged.
4. **Honoured with a negative regression.** The BOM case is covered at
   `platform_tests/scripts/test_bridge_applicability_preflight.py:1151`, so a
   BOM-prefixed source fails loudly instead of silently degrading identity.

## Disclosed Baseline Failure - Accepted, Not Attributable

The single red test in the packet/hook slice,
`test_active_and_template_hooks_remain_byte_identical`, was independently
confirmed to be pre-existing and unrelated to this implementation:

- It appears in `git diff` only as a context line, so this change neither
  authored nor modified it.
- Both hook files are clean at HEAD; neither is in the working-tree diff.
- The live and template hooks are content-identical. Their LF-normalized
  digests are both
  `50aeed9c1d3aaf7da866f59f60b2deb265f6e158f95a6328a2cea6b762eb29d3`; only the
  on-disk end-of-line representation differs (live CRLF, template LF), which is
  a Windows checkout artifact.

The byte-identity invariant the test guards holds at the content level. The
failure is an environment-level end-of-line observation, not a defect introduced
here, and it does not touch any specification linked by this thread. It is
recorded rather than waived: it remains a real red test on this platform and is
tracked outside this five-file scope.

## Applicability Preflight

- packet_hash: `sha256:e28679048a34cec1c08ef71b7550fa2b169e3581b453c714969a6a9003a1f9dd`
- bridge_document_name: `gtkb-wi5441-bridge-publication-capability-commit-clearance`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-009.md`
- operative_file: `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-009.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- candidate_evidence_hash: `sha256:76f5cd7729248b6694853ac8551e1c2fb2c3dd900e73fa8f96fe10d44772a5ee`

## Clause Applicability

- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation), exit 0

| Clause | Applicability | Evidence found |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | may_apply | not required |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | may_apply | not required |

### Blocking Gaps

None.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Spec-to-Test Mapping

| Specification | Executed evidence | Executed | Result |
| --- | --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_schema_v2_verdict_hash_passes_live_and_real_index_only_audits` plus this verdict's own governed finalization | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | 141-test checker module green; 61-test packet and hook slice green excluding the disclosed pre-existing baseline | yes | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight exit 0 with empty missing-required and missing-advisory sets | yes | PASS |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Exact-row publication tests plus registry readback reported coherent and current | yes | PASS |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | `test_registry_commit_rejects_nonterminal_bridge_publication_attempts` and `test_registry_commit_rejects_bridge_publication_binding_mismatch` | yes | PASS |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | No schema change in the five-file diff; existing identities retained | yes | PASS |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Declaration, package, and projection unchanged by this diff | yes | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Diff confined to the five authorized target paths | yes | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Append-only v001 through v010 chain with independent cross-session review | yes | PASS |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Exact-key-set, rules-hash, sibling-independence, BOM, four-aggregate-head, and near-match regressions | yes | PASS |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | v004 through v006 findings became the reviewed v007 proposal before any mutation | yes | PASS |

## Commands Executed

- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5441-bridge-publication-capability-commit-clearance`
- The same preflight with `--content-file bridge\gtkb-wi5441-bridge-publication-capability-commit-clearance-009.md`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5441-bridge-publication-capability-commit-clearance`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_check_protected_commit_authorization.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_applicability_preflight.py platform_tests\hooks\test_bridge_compliance_gate_lo_verdict_candidate_preflight.py -q --tb=short`
- The same packet and hook command with `-k "not active_and_template_hooks_remain_byte_identical"`
- `groundtruth-kb\.venv\Scripts\ruff.exe check` over the exact five targets
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check` over the exact five targets
- `git diff --stat` and `git status --short` over the exact five targets
- `Get-FileHash -Algorithm SHA256` over the exact five targets

## Observed Results

- Checker module: 141 passed, with one pre-existing unknown config warning.
- Packet and hook slice: 61 passed, 1 failed. The sole failure is the disclosed
  pre-existing baseline analysed above.
- Packet and hook slice excluding that baseline: 61 passed, 1 deselected.
- Ruff check: all checks passed. Ruff format check: 5 files already formatted.
  Both gates were run separately.
- All five claimed postimage digests matched the on-disk bytes exactly.
- `git diff --stat`: 5 files changed, 1253 insertions, 9 deletions.
- Default and explicit preflight invocations produced one identical packet hash.
- Applicability preflight and clause preflight both exited 0 with zero gaps.

Every numeric and cryptographic claim in `-009` reproduced exactly. No claim in
the implementation report was found to be overstated.

## Prior Deliberations

- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-004.md` - first NO-GO exposing the hash divergence.
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-006.md` - F-LO-5 through F-LO-7 definitions.
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-007.md` - approved proposal.
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-008.md` - independent GO with cautions and observations.
- `bridge/gtkb-lo-tooling-defect-advisory-002.md` - prior advisory recording the packet-hash deadlock class this thread closes.
- `bridge/gtkb-lo-tooling-defect-advisory-007.md` - prior advisory locating the wrong-table publication-evidence read.

## Owner Decisions / Input

No owner decision is required or requested. Authority remains
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726`
and `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`. This verdict
requests no destruction, dispatcher activation, push, release, deployment,
schema change, registry membership change, or specification amendment. The
dispatcher remains disabled.

## Residual Risk

- Schema-v1 verdicts elsewhere in the bridge chain remain stranded and require
  fresh verification; this thread does not rescue them and does not claim to.
- Parent WI-5441 reverse coverage remains incomplete and is not masked by this
  slice's coherent and current registry readback.
- The end-of-line baseline failure remains red on this platform and is tracked
  outside this scope.

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/gtkb-verify/helpers/write_verdict.py --finalize-verified`
- Intended commit subject: `fix(bridge): reproducible verdict freshness and exact-row publication routing (WI-5441)`
- Same-transaction path set:
- `scripts/bridge_applicability_preflight.py`
- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_bridge_applicability_preflight.py`
- `platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-001.md`
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-002.md`
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-003.md`
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-004.md`
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-005.md`
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-006.md`
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-007.md`
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-008.md`
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-009.md`
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-010.md`
- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.
