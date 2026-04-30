NO-GO

# NO-GO - GT-KB Platform Spec-Coverage VERIFIED Runner Implementation

**Status:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Reviewed proposal:** `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-001.md`
**Date:** 2026-04-29

## Verdict

NO-GO. The umbrella architecture approval supports a focused full-history VERIFIED runner, and the selected bridge entry is actionable, but this implementation proposal does not yet satisfy the bridge protocol's specification-derived test mapping and fail-closed enforcement requirements.

The proposal should be revised and resubmitted before implementation.

## Evidence Reviewed

- Live authoritative queue: `bridge/INDEX.md` shows latest status `NEW: bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-001.md`.
- Active bridge protocol: `.claude/rules/file-bridge-protocol.md`.
- Project root boundary: `.claude/rules/project-root-boundary.md`.
- Reviewed proposal: `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-001.md`.
- Parent umbrella: `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-005.md` and Codex GO at `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-006.md`.
- Sibling Slice 1 verification: `bridge/gov-process-spec-precondition-2026-04-29-008.md`.
- KB verification: direct SQLite reads confirmed `DCL-VERIFIED-BRIDGE-HISTORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, and `ADR-CODEX-HOOK-PARITY-FALLBACK-001` exist in `groundtruth.db`.

## Blocking Findings

### F1 - Test mapping omits linked governing specs

**Claim:** The proposal links more governing specs and rules than its test mapping covers, so the only valid verdict is NO-GO under the bridge protocol.

**Evidence:** The bridge protocol requires proposals to state how tests derive from linked specifications and requires LO to reject omissions (`.claude/rules/file-bridge-protocol.md:32-35`). The proposal links `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001`, `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `.claude/rules/project-root-boundary.md`, `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, and `.claude/rules/bridge-essential.md` as constraining this work (`-001.md:33-46`). The test mapping then states every listed test derives only from `DCL-VERIFIED-BRIDGE-HISTORY-001.A1/.A2` plus `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (`-001.md:50-64`).

The proposal later expects dogfood output to show all governance specs cited above with tests found and passing (`-001.md:264-267`), but that expected coverage is not mapped to concrete tests.

**Risk/impact:** A post-implementation report could claim VERIFIED while linked governance/rule constraints have no derived tests. That is the exact failure class this slice is meant to eliminate.

**Required action:** Revise the Specification-Derived Verification table so every linked spec/rule/ADR/DCL that constrains the implementation has an explicit derived test or a documented owner-approved waiver. At minimum, add coverage for bridge index authority, non-mutation of `bridge/INDEX.md`, project-root confinement, mechanical enforcement semantics, and Codex review-skill consumption if those remain linked.

**Owner decision needed:** None.

### F2 - CLI defaults are fail-open for coverage gaps

**Claim:** The proposed default CLI behavior allows a missing derived-test gap to exit successfully, which contradicts the VERIFIED-time gate and mechanical enforcement purpose.

**Evidence:** `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` says VERIFIED is conditional on every linked spec having at least one derived test, all derived tests being executed, and all executed tests passing. `DCL-VERIFIED-BRIDGE-HISTORY-001` says the runner fails closed for missing index entries and that VERIFIED is only true when every union spec has at least one derived test and all derived tests pass. The proposal makes `--strict` optional and states the default is to "print warning but exit 0 if all derived tests pass" when any spec lacks a derived test (`-001.md:86-92`). The proposed Codex review invocation also omits `--strict` (`-001.md:222-226`), while the actual prompt update is explicitly out of scope (`-001.md:228`).

**Risk/impact:** A consumer that treats the runner as a gate by exit code can pass a bridge thread with untested linked specs. That is not strict mechanical enforcement.

**Required action:** Make fail-closed behavior the default for the runner: non-zero exit when any union spec lacks derived tests, when any derived test fails, when waiver validation fails, or when the bridge entry is absent. If an advisory mode is wanted, make it explicit, for example `--advisory`, and keep the documented VERIFIED invocation fail-closed.

**Owner decision needed:** None.

### F3 - Waiver validation accepts text instead of verified owner approval

**Claim:** A2 says removal requires an owner-approved waiver, but the proposal only requires a non-empty `approved_by` field.

**Evidence:** The proposal describes A2 as "removal requires owner-approved waiver" (`-001.md:26`), but the waiver parser requirement is only that `approved_by` be non-empty (`-001.md:180-190`). The mapped acceptance test accepts a bridge revision that includes a `Specification-Coverage-Waivers` section (`-001.md:56-57`); it does not require the runner to verify that the referenced approval exists, is an owner decision, and applies to the removed spec and version.

**Risk/impact:** Prime Builder or another writer could remove a previously linked spec by adding arbitrary waiver text. The runner would then certify a reduced spec set without durable owner approval.

**Required action:** Require the runner to validate waiver evidence, not just parse it. A revised proposal should specify the durable approval source and checks, such as verifying `approved_by` against `groundtruth.db` deliberation/owner-decision records or a formal approval packet, and add negative tests for missing, malformed, nonexistent, non-owner, and wrong-spec waiver references.

**Owner decision needed:** None unless Mike wants a different canonical waiver evidence source.

### F4 - Target classification conflicts with the root-boundary rule

**Claim:** The proposal calls the implementation an "Agent-Red-side script" but places new files in root-level `scripts/` and `tests/`, creating an application-boundary ambiguity that must be resolved before implementation.

**Evidence:** The proposal declares `target_project: agent-red (in-root scripts/ + tests/)` near the metadata block (`-001.md:14`) and later says "This is an Agent-Red-side script (lives in `scripts/`)" (`-001.md:307-311`). The root-boundary rule says Agent Red application files must live under `E:\GT-KB\applications\Agent_Red\` (`.claude/rules/project-root-boundary.md:11-12`) and that new application files must not be added outside `E:\GT-KB\applications\` (`.claude/rules/project-root-boundary.md:32-34`).

**Risk/impact:** This can continue the historical platform/application isolation drift. If the runner is platform governance tooling, the proposal should label it as GT-KB platform/root governance infrastructure. If it is Agent Red application tooling, the file routing is wrong.

**Required action:** Revise the metadata and file plan to make ownership explicit. Either classify the runner as GT-KB platform governance tooling under root `scripts/`/`tests/`, or move Agent Red application files under `applications/Agent_Red/`. The final path should match the DCL `source_paths` expectation or the DCL should be revised through the proper artifact process.

**Owner decision needed:** None if Prime Builder classifies the runner as platform governance tooling consistent with the parent umbrella and DCL source path.

## Non-Blocking Notes

- The proposal's module-level docstring discovery is conservative and acceptable as a starting point if the revised tests prove it does not miss intended derived coverage.
- Running the runner against its own bridge thread is acceptable as dogfood evidence, but it cannot substitute for the missing test mapping and fail-closed behavior above.

## Required Revision Checklist

1. Add spec-derived tests or waivers for every linked governing spec/rule/ADR/DCL.
2. Make the default CLI and documented Codex invocation fail closed for any unverified spec.
3. Validate waiver approval evidence against a durable owner-approval source.
4. Resolve Agent Red vs. GT-KB platform file ownership in the metadata and file plan.

## Scan Result

File bridge scan: 1 entry processed.
