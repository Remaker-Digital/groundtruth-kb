REVISED

# Implementation Proposal - Proposal-Standards Test-Claim Re-Run Verifier (Slice 2) - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-proposal-standards-test-claim-rerun-verifier
Version: 003
Responds to: bridge/gtkb-proposal-standards-test-claim-rerun-verifier-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-PROPOSAL-STANDARDS-SLICES-2-3
Project: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS
Work Item: GTKB-GOV-PROPOSAL-STANDARDS-SLICE2

target_paths: ["scripts/bridge_report_test_claim_rerun_verifier.py", "platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py"]

This REVISED-1 (`-003`) lands GTKB-GOV-PROPOSAL-STANDARDS Slice 2: a verifier that parses claimed `pytest` command-and-output blocks out of bridge **post-implementation reports** and re-runs the same commands in an in-root fixture workspace to catch stale or false pass-claims.

## Revision Notes

This `-003` REVISED-1 addresses every finding in the `-002` NO-GO:

- **FINDING-P1-001 (P1) — the proposed verifier checked the wrong artifact and the wrong claim type.** Resolved with a full scope rewrite. The `-001` proposal parsed *planned* `test_*` names from bridge *proposal* `Specification-Derived Verification Plan` sections and checked function existence. Slice 2's operative work item is about *claimed pytest output blocks in post-implementation reports*. The verifier is rebuilt to: (1) target bridge post-implementation reports, not ordinary proposals; (2) parse fenced/indented blocks containing an explicit `pytest` command plus a claimed observed result (e.g. "44 passed"); (3) re-run the same command in a controlled in-root fixture workspace; (4) compare the observed pytest outcome summary / exit code to the claimed summary; (5) fail on divergence. The script is renamed `scripts/bridge_report_test_claim_rerun_verifier.py` to reflect the corrected artifact target. A regression fixture encodes the stale "44 tests pass" claim vs an actual "7 failed, 16 passed" run. See IP-1 and the Scope Rewrite section.
- **FINDING-P2-002 (P2) — the verification plan omitted the gate behavior and one authorized test surface.** Resolved. `target_paths` no longer lists a nonexistent root `tests/scripts/...`; the live checkout has no root `tests/` directory. The single authorized test file is `platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py` and the run command executes exactly that path. The pre-commit gate *wiring* is **explicitly deferred** to a named follow-on slice (Slice 2b — see Deferred Scope) so this slice is not claimed to deliver the gate; this slice delivers the standalone re-run verifier CLI that the gate will later invoke. The test plan covers output-block parsing, same-command re-run, fixture-environment isolation, divergence failure, matching-output pass, and out-of-root command rejection.
- **Advisory preflight omissions** (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` flagged in the `-002` applicability preflight). Resolved. All three are now cited in `## Specification Links`. Both preflights were re-run on this `-003` content; results are embedded below.

## Claim

Build a CLI: `python scripts/bridge_report_test_claim_rerun_verifier.py --bridge-id <id> [--report-version NNN] [--strict]`. It reads a bridge post-implementation report, extracts every fenced/indented block that contains an explicit `pytest` invocation alongside a claimed observed result, re-runs each command in an in-root fixture workspace, parses the actual pytest outcome summary, and emits a per-claim PASS / DIVERGED / ERROR report. A claimed result that does not match the re-run result is a DIVERGED finding. `--strict` returns a non-zero exit when any claim is DIVERGED or ERROR (for CI / gate use); the default exit is 0 (advisory).

## In-Root Placement Evidence

All `target_paths` are inside `E:\GT-KB`. The re-run fixture workspace is created inside `E:\GT-KB` (a temporary directory under the project root or under `.gtkb-state/`); the verifier rejects any extracted command that would execute outside the project root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; the verifier protects the integrity of post-implementation-report evidence by re-running claimed pytest commands.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation reports must rest on executed spec-derived tests; this verifier catches reports whose claimed pytest output is stale or false, directly serving that constraint.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only; the verifier rejects out-of-root re-run commands and runs the fixture workspace in-root.
- `GOV-STANDING-BACKLOG-001` - `GTKB-GOV-PROPOSAL-STANDARDS-SLICE2` is a tracked work item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; the verifier is a governed enforcement artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, bridge thread, and verifier form the artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the verifier checks the post-implementation-report lifecycle stage (the VERIFIED-review step).

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - batch-2 owner authorization for `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS` and its Slice 2/3 work items.
- `DELIB-0991` - prior Loyal Opposition review of `gtkb-gov-proposal-standards-slice1`; parent-thread context establishing that proposal-standards checks must be concrete and mechanically enforceable.

The `-002` NO-GO noted that semantic deliberation hits (`DELIB-1667`, `DELIB-1806`, `DELIB-1852`) were less controlling than the Slice 2 work-item text; this revision is scoped directly to that work-item text. No retrieved deliberation waives the requirement that the verifier address the stale-pytest-output-claim failure mode in post-implementation reports.

## Owner Decisions / Input

This proposal is filed under an active project authorization and is authorized by:

- 2026-05-14 UTC, S350+: owner AUQ "Authorize all 3 groups (7 WIs added)" — authorized `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS` including `GTKB-GOV-PROPOSAL-STANDARDS-SLICE2`. Recorded as `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS`.

No new owner decision is required for this revision; `-003` aligns the implementation scope with the Slice 2 work-item text and fixes the test surface.

## Requirement Sufficiency

Existing requirements sufficient. The `GTKB-GOV-PROPOSAL-STANDARDS-SLICE2` work-item description — parse claimed `pytest` output blocks in post-implementation reports, re-run the same commands in a fixture environment, and fail when real output diverges from claimed output — is the operative requirement. This revision implements that requirement as written (the `-001` interpretation built a different verifier against the wrong artifact). No new or revised requirement or specification is created.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-WI implementation proposal (`GTKB-GOV-PROPOSAL-STANDARDS-SLICE2`). It performs no batch resolve, promote, or retire of work items or specifications. References to "work item", "backlog", and "standing backlog" describe the single Slice-2 work item. The review-packet inventory is one bridge thread: IP-1 (re-run verifier CLI) + IP-2 (tests). The Slice-2 project membership is recorded under the formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json`.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-003` REVISED line is inserted under the existing `Document: gtkb-proposal-standards-test-claim-rerun-verifier` entry; the prior `-001` NEW and `-002` NO-GO lines are preserved unchanged.

## Scope Rewrite (resolves FINDING-P1-001)

The `-001` verifier and the `-003` verifier differ fundamentally:

| Aspect | `-001` (rejected) | `-003` (this revision) |
|---|---|---|
| Target artifact | bridge implementation *proposals* | bridge *post-implementation reports* |
| What is parsed | planned `test_*` names from `Specification-Derived Verification Plan` | fenced/indented blocks with an explicit `pytest` command + claimed observed result |
| What is checked | "does a `def test_<name>` exist somewhere" | "does re-running the claimed command reproduce the claimed result" |
| Failure mode addressed | none of the real Slice-2 risk | a report claiming "44 tests pass" when the live run had failures |
| Action | report `{claim, found, file}` | re-run command in an in-root fixture workspace; report PASS / DIVERGED / ERROR |

The `-003` verifier is the tool Slice 2 actually requires.

## Deferred Scope (resolves FINDING-P2-002 gate concern)

Pre-commit gate *wiring* — registering this verifier as a pre-commit hook that blocks a commit when a post-implementation report's pytest claims diverge — is **explicitly deferred** to a named follow-on slice: **Slice 2b (`GTKB-GOV-PROPOSAL-STANDARDS-SLICE2B`, pre-commit gate wiring)**, to be filed as a separate bridge thread after this slice's standalone verifier is VERIFIED. This slice (Slice 2) delivers the standalone re-run verifier CLI only. Slice 2 is claimed complete when the CLI lands and is verified; the gate-wiring claim belongs to Slice 2b. This deferral is recorded here so no reviewer treats the absence of gate wiring as a Slice-2 gap.

## Proposed Scope

### IP-1: Post-implementation-report pytest-claim re-run verifier

`scripts/bridge_report_test_claim_rerun_verifier.py`:

1. Read the bridge post-implementation report at `bridge/<bridge-id>-NNN.md` (latest version, or `--report-version NNN`).
2. Extract every fenced (```` ``` ````) or indented code block. For each block, detect an explicit `pytest` invocation (a line matching a `pytest` / `python -m pytest` command pattern) and a claimed observed pytest result on the same or an adjacent line in the same block (the pytest summary line, e.g. `44 passed`, `7 failed, 16 passed`, `2 errors`).
3. Safety gate: reject any extracted command that is not a `pytest` / `python -m pytest` invocation, or whose target path resolves outside the project root, or that contains shell metacharacters indicating chaining. Such a command is reported as `ERROR: command not safely re-runnable` and never executed.
4. For each safely-extracted claimed command, re-run it inside an in-root fixture workspace (a temp directory created under the project root; the working tree is the in-root checkout). Capture the actual pytest summary line and exit code.
5. Compare: parse the claimed summary into a `{passed, failed, errors, skipped}` tuple and the observed summary into the same shape. If they do not match, the claim is `DIVERGED`; if they match, `PASS`; if the re-run could not run, `ERROR`.
6. Emit a JSON report `{claim_block_index, command, claimed_summary, observed_summary, status}` per claim, plus a markdown `Test-Claim Re-Run` section.
7. Exit 0 by default (advisory). With `--strict`, exit non-zero when any claim is `DIVERGED` or `ERROR`.

### IP-2: Tests

`platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py` covers: parsing a pytest command+output block from a post-implementation report fixture; same-command re-run behavior; in-root fixture-workspace isolation; the stale "44 tests pass" vs actual "7 failed, 16 passed" divergence regression; the matching-output PASS case; out-of-root / non-pytest command rejection; `--strict` non-zero exit on divergence; default exit 0; and the output JSON schema.

## Specification-Derived Verification Plan

Every linked specification maps to at least one test in `platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py`.

| Linked spec | Behavior verified | Test |
|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | a pytest command+output block in a post-implementation report fixture is parsed (command + claimed summary extracted) | `test_parse_pytest_block_from_post_impl_report` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | the verifier re-runs the claimed command and reports PASS when the observed summary matches the claim | `test_rerun_matching_output_reports_pass` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | the stale-claim regression: a report claiming "44 tests pass" against a fixture whose real run is "7 failed, 16 passed" is reported DIVERGED | `test_stale_claim_44_pass_vs_real_failures_diverged` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | the re-run executes in an in-root fixture workspace (no out-of-root execution) | `test_rerun_fixture_workspace_in_root` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | a claimed command whose target resolves outside the project root, or that is not a pytest invocation, is rejected as ERROR and not executed | `test_out_of_root_or_non_pytest_command_rejected` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `--strict` returns a non-zero exit when any claim is DIVERGED; default returns exit 0 | `test_strict_nonzero_on_divergence`, `test_default_exit_zero` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | the output JSON conforms to the documented per-claim schema | `test_output_json_schema` |
| `GOV-STANDING-BACKLOG-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | a post-implementation report with no pytest claim blocks yields an empty (well-formed) report rather than an error | `test_report_with_no_pytest_blocks_empty_result` |

Run: `python -m pytest platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py -v --tb=short`.

Lint: `python -m ruff check scripts/bridge_report_test_claim_rerun_verifier.py platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py`.

## Acceptance Criteria

- IP-1 (re-run verifier CLI), IP-2 (tests) landed; all tests in `test_bridge_report_test_claim_rerun_verifier.py` PASS.
- The verifier targets bridge post-implementation reports and parses pytest command+output blocks (not planned test names from proposals); proven by tests.
- The verifier re-runs claimed commands in an in-root fixture workspace and reports DIVERGED on a stale "44 tests pass" claim; the regression fixture proves it.
- The verifier rejects out-of-root / non-pytest commands without executing them; proven by a test.
- The verification command runs `platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py` and collects all tests successfully (no nonexistent root `tests/` path).
- Pre-commit gate wiring is explicitly deferred to Slice 2b; Slice 2 is claimed complete only for the standalone verifier CLI.
- Both bridge preflights PASS for this proposal (`-003`).
- `ruff check` is clean on the touched files.

## Risks / Rollback

- Risk: re-running a claimed pytest command is slow or has side effects. Mitigation: the re-run is bounded to pytest invocations only, executed in an in-root fixture workspace; the verifier is advisory by default (exit 0) so it never blocks unless `--strict` is explicitly used.
- Risk: a claimed command cannot be safely re-run (shell chaining, out-of-root path). Mitigation: the safety gate rejects such commands as ERROR and never executes them; a test proves the rejection.
- Risk: pytest summary-line parsing is brittle across pytest versions. Mitigation: the summary parser matches the stable `N passed` / `N failed` / `N error(s)` / `N skipped` tokens; tests cover the common shapes including a clean pass and a mixed failure.
- Rollback: remove `scripts/bridge_report_test_claim_rerun_verifier.py` and the test file. No existing surface is modified (gate wiring is not part of this slice).

## Recommended Commit Type

`feat` - a new post-implementation-report pytest-claim re-run verifier plus tests; a new mechanical-enforcement capability with no behavior change to existing surfaces.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-proposal-standards-test-claim-rerun-verifier`

- packet_hash: `sha256:fc0a995589d2706d5890502ec41463711ed5a5b121eed981147ea1174a234e0c`
- bridge_document_name: `gtkb-proposal-standards-test-claim-rerun-verifier`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-003.md`
- operative_file: `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-proposal-standards-test-claim-rerun-verifier`

- Bridge id: `gtkb-proposal-standards-test-claim-rerun-verifier`
- Operative file: `bridge\gtkb-proposal-standards-test-claim-rerun-verifier-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation); exit code `0`

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
