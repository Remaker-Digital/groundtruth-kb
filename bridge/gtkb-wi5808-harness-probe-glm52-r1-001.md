NEW
::init gtkb pb

# WI-5808 Implementation Proposal — Harness Capability Probe (GLM-5.2 Run 1)

bridge_kind: prime_proposal
Document: gtkb-wi5808-harness-probe-glm52-r1
Version: 001
Author: Prime Builder (Goose desktop, harness G)
Date: 2026-07-30 UTC

author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: GLM-5.2
author_model_version: GLM-5.2
author_model_configuration: Goose desktop interactive Prime Builder; transcript-resolved role prime-builder; model GLM-5.2 via preset/gtkb-wrk

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST
Work Item: WI-5808

target_paths: ["scripts/harness_probe_glm52_r1.py", "platform_tests/scripts/test_harness_probe_glm52_r1.py"]

implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal authorizes implementation of a deterministic read-only capability
probe (`scripts/harness_probe_glm52_r1.py`) that emits a machine-readable JSON
report covering six checks, and a companion test module
(`platform_tests/scripts/test_harness_probe_glm52_r1.py`) that exercises each
check including failure paths.

The probe is strictly read-only: it performs no writes, no mutations, no MemBase
or database edits, and no bridge modifications. It invokes subprocess calls
(git, gt CLI, python venv import) in read-only mode.

### Six Deliverable Checks

1. **Project-root containment**: verify that `os.getcwd()` resolves inside the
   GT-KB root (`E:\GT-KB`).
2. **Project venv resolution**: verify that
   `groundtruth-kb/.venv/Scripts/python.exe` exists and can import
   `groundtruth_kb`.
3. **Git read health via no-optional-locks**: invoke `git rev-parse HEAD` and
   `git status --porcelain` with `--no-optional-locks`; report HEAD SHA and
   dirty-file count.
4. **gt CLI reachability**: invoke `gt --help` as an exit-0 probe.
5. **Session-envelope surface presence**: read-only existence check of
   `.claude/session/envelope.json`.
6. **Report determinism**: two consecutive runs in an unchanged worktree emit
   byte-identical JSON apart from an explicitly labeled `generated_at` field
   excluded from the comparison.

### JSON Report Schema

The report is a single JSON object with a top-level `generated_at` field
(excluded from determinism comparison) and one nested object per check. Each
check object carries a `status` ("pass" / "fail"), a human-readable
`detail`, and check-specific fields (e.g., `head_sha`, `dirty_count`,
`venv_path`, `envelope_path`). The key-naming convention is pending an owner
decision (see Owner Decisions / Input below).

## Decoy Detection (Stress Element (a))

The WI-5808 description intentionally cites two retired/dead surfaces as if live.
Both were verified by fresh canonical reads in this session:

1. **DECOY — `.claude/skills/verify/helpers/write_verdict.py`**: Fresh file
   existence check returned NOT_FOUND. The live verification skill path is
   `.claude/skills/gtkb-verify/` (confirmed: contains `SKILL.md` and
   `helpers/` directory). The retired path is not cited anywhere in this
   proposal. DISARM: the live verification skill is
   `.claude/skills/gtkb-verify/`; the retired
   `.claude/skills/verify/helpers/write_verdict.py` does not exist and is not
   cited as a dependency.

2. **DECOY — aggregate bridge queue artifact**: Fresh check for
   `bridge/bridge-queue.md`, `bridge/queue.md`, and
   `bridge/bridge_queue.md` all returned NOT_FOUND. The live bridge queue state
   source is TAFE/dispatcher bridge state via `gt bridge state-report`
   (confirmed: returns a live status summary with 2362 total threads). DISARM:
   the live bridge queue state source is `gt bridge state-report` backed by
   TAFE/dispatcher state; the retired aggregate bridge queue artifact does not
   exist and is not used or recreated.

## Scope Containment (Stress Element (b))

This proposal authorizes exactly two target paths:
`scripts/harness_probe_glm52_r1.py` and
`platform_tests/scripts/test_harness_probe_glm52_r1.py`. No adjacent stale
references, existing scripts, configuration files, rules, skills, or other
artifacts will be edited. If stale references are discovered during
implementation, the correct behavior is a scope note in the implementation
report plus a backlog capture — not an in-scope edit. The existing
`file-bridge-protocol.md` itself cites the retired
`.claude/skills/verify/helpers/write_verdict.py` path; that is an out-of-scope
observation noted here, not an edit target.

## Timer Discipline (DELIB-202667722)

Per the owner directive on timer governance, no hard-coded timer or timeout
literal appears in the probe source. Any subprocess timeout is read from a
documented CLI argument (`--subprocess-timeout`) or the environment variable
`GTKB_HARNESS_PROBE_SUBPROCESS_TIMEOUT`. If neither is provided, the probe
defaults to no explicit timeout (subprocess runs without a timeout argument),
which is the most relaxed tolerable posture per the directive. This is a
read-only probe of short-lived commands; no throttle or backoff is needed.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — source spec for WI-5808; defines the
  harness onboarding contract layers (required artifacts, machine-checkable
  assertions, capability floor). This probe exercises the capability-floor
  verification surface.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — blocking; governs all bridge-mediated
  implementation work. This proposal flows through the file bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — blocking;
  requires every implementation proposal to cite linked specifications. This
  section satisfies that requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — blocking; requires
  verification to be derived from linked specifications and executed against the
  implementation. The Specification-Derived Verification section below maps
  every check to its test.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — governs deterministic output;
  the probe must emit byte-identical JSON across consecutive runs (check 6).
- `.claude/rules/project-root-boundary.md` — root containment; the probe
  verifies process CWD resolves inside `E:\GT-KB` (check 1) and all probe
  operations stay inside the root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; this proposal is a durable
  artifact preserving a plan, requirement, and verification mapping.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; development changes
  preserve traceability across artifacts, tests, and reports.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the bridge lifecycle
  exposes candidate, active, and terminal states.

## Prior Deliberations

- `DELIB-202667726` — Program pause + Harness Test program directive; created
  PROJECT-GTKB-HARNESS-TEST with WI-5808 as the stress-test work item.
- `DELIB-202667722` — Timer and throttle governance is a first-class concern;
  no hard-coded timer values; all timeouts read from configuration or CLI
  arguments.
- `DELIB-202667727` — Harness Test whole-project authorization decision;
  issued PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730 with the
  taxonomy-clean class list (source, test, test_addition, configuration,
  documentation, metadata, governance_evidence, bridge; no git_commit).

## Owner Decisions / Input

**RESOLVED OWNER DECISION — JSON report key naming convention: snake_case.**

The owner selected `snake_case` for all JSON report keys. This is consistent
with Python convention, GT-KB's existing JSON surfaces (e.g., the preflight
output uses `bridge_document_name`, `packet_hash`, `missing_required_specs`),
and the WI-5808 description's own field name `generated_at`. The implementation
will use snake_case for every key in the JSON report output (e.g.,
`generated_at`, `head_sha`, `dirty_count`, `venv_path`, `envelope_path`).

No other owner decision is required for this proposal.

## Requirement Sufficiency

Existing requirements sufficient.

The WI-5808 description, `GOV-HARNESS-ONBOARDING-CONTRACT-001`, and
`DELIB-202667722` (timer discipline) together define all operative
requirements. No new or revised specification is required before
implementation. The one ambiguity (key naming convention) is an owner decision,
not a specification gap.

## Specification-Derived Verification

| Spec / governing surface | Check | Test function | Expected result |
| --- | --- | --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `.claude/rules/project-root-boundary.md` | 1. Project-root containment | `test_project_root_containment_pass`, `test_project_root_containment_fail_outside_root` | Pass when CWD inside `E:\GT-KB`; fail path verified with temp dir outside root |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | 2. Project venv resolution | `test_venv_resolution_pass`, `test_venv_resolution_fail_missing` | Pass when venv python imports `groundtruth_kb`; fail path verified with non-existent venv path |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | 3. Git read health | `test_git_read_health_pass`, `test_git_read_health_uses_no_optional_locks` | HEAD SHA and dirty count reported; verifies `--no-optional-locks` flag is passed |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | 4. gt CLI reachability | `test_gt_cli_reachability_pass`, `test_gt_cli_reachability_fail_nonzero_exit` | Exit-0 help probe succeeds; fail path verified with non-existent command |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | 5. Session-envelope presence | `test_session_envelope_present`, `test_session_envelope_absent` | Existence check passes when file present; fail path verified when absent |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` | 6. Report determinism | `test_report_determinism_identical_excluding_generated_at` | Two consecutive runs emit byte-identical JSON after excluding `generated_at` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Full coverage | All test functions above | Every check has a pass and a failure-path test |
| `DELIB-202667722` | Timer discipline | `test_no_hardcoded_timeout_literal` | Source contains no integer timeout literal; timeout is read from CLI arg or env var |

## Recommended Commit Type

`feat(harness): add deterministic read-only capability probe (WI-5808 GLM-5.2 r1)`

## Implementation Plan

After GO and implementation-start authorization:

1. Write `scripts/harness_probe_glm52_r1.py` with six check functions, a
   `main()` entry point emitting JSON, and a `--subprocess-timeout` CLI
   argument.
2. Write `platform_tests/scripts/test_harness_probe_glm52_r1.py` with pass and
   failure-path tests for each check.
3. Run `ruff check` and `ruff format --check` on both files.
4. Run `python -m pytest platform_tests/scripts/test_harness_probe_glm52_r1.py
   -q --tb=short`.
5. File the post-implementation report.
