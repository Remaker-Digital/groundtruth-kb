REVISED
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T13-15-03Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


# Implementation Proposal Revision — WI-5668 skill-rename sweep completion gate

bridge_kind: prime_proposal
Document: gtkb-wi5668-skill-rename-sweep-completion-gate
Version: 003
Date: 2026-07-24 UTC
Responds to: bridge/gtkb-wi5668-skill-rename-sweep-completion-gate-002.md

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5668

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor.py", "scripts/release_candidate_gate.py", "platform_tests/scripts/test_release_candidate_gate.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision replaces the warning-only, under-specified completion signal rejected at version 002 with one deterministic predicate shared by the project-doctor surface and the existing top-level release-candidate gate. Remaining active bare legacy skill-path references are a required doctor failure and a release-gate failure; zero findings is the only passing completion condition. It does not authorize repairs to the references themselves, generated adapters, rules/config mirrors, scaffold artifacts, bridge audit history, or historical content.

## Finding-by-Finding Resolution

### P1 — release-blocking enforcement route

The doctor check will be named `skill-rename reference sweep completion`, marked `required=True`, and return `status="fail"` when its deterministic finding list is non-empty. `DoctorReport._compute_overall()` already makes a required failed check an overall failure. The relevant profile is the bridge-capable GT-KB project profile that executes the check.

The release enforcement owner is `scripts/release_candidate_gate.py`, which is invoked by `.github/workflows/release-candidate-gate.yml`. It will call the same exported evaluation function rather than reimplementing the scan. A non-empty finding list raises `GateFailure` before the Python test lane and emits a stable, count-bearing failure reason; an empty list emits `PASS skill-rename reference sweep completion (0 findings)`. Therefore the CI release decision exits non-zero while the sweep is incomplete, including when the normal project-doctor command is not the command invoking CI.

### P2 — reproducible detector contract

The implementation will define one exported evaluator in `groundtruth_kb.project.doctor` whose input is a project root and whose output contains a sorted list of normalized finding records (`path`, `line`, `alias`, `matched_text`) plus the count. Both the doctor `ToolCheck` and release gate consume that evaluator.

The evaluator’s source of record is `config/agent-control/skill-rename-map.toml`. It parses every `[[skills]]` record and derives the legacy alias set from: (1) each `dir` after removing exactly one leading `gtkb-`; (2) each `canonical_name` after removing exactly one leading `gtkb-`; and (3) each non-empty `registry_old_name`. The set is deduplicated and sorted lexicographically before scanning. No free-text skill-name matching is permitted.

A finding is only a path-segment reference matching the normalized grammar `(?:^|[\\\"'`(=:\\s])(?:\\.(?:claude|codex|agent|agents)/)?skills/<legacy-alias>(?=$|[/.\\\"'`),:\\s])`, with `<legacy-alias>` substituted from that sorted alias set and path separators normalized to `/`. This detects a former bare skill directory only when it occurs in a skill-path reference; it does not count prose such as “bridge review”, a canonical `gtkb-*` path, or a longer directory name sharing an alias prefix.

The file enumerator is `git -C <target> ls-files -z`. The evaluator decodes the NUL-delimited tracked paths, normalizes `\\` to `/`, excludes non-files, and scans paths in lexical normalized-path order. The allowlisted exclusions are exact and auditable: `bridge/`, `.gtkb-state/`, any path segment whose name begins `RETIRED-` or `BARRED-`, any path segment exactly `archive` or `archives`, and `config/agent-control/skill-rename-map.toml` itself. The map is excluded because it is the classifier’s source of record, not a stale consumer. No other exclusions are permitted. Findings are sorted by normalized path, line number, and alias; the message reports the first ten findings in that order.

## Requirement Sufficiency

Existing requirements are sufficient. `WI-5668`, `DELIB-202667193`, and the active project authorization require a mechanical self-driving completion signal. This revision narrows and makes the already-authorized mechanism testable; it does not create a new requirement or change the sweep’s ownership boundary.

## In-Root Placement Evidence

All implementation and test targets are inside `E:\\GT-KB`. The release-gate script is the current in-root CI entrypoint, not an Agent Red repository dependency.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — preserves Prime/LO authority, scoped target paths, and independent verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — retains the completion condition as a durable and inspectable control.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires concrete governing links and a requirements-sufficiency statement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the mapping below and executed evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires this proposal’s PAUTH, project, WI, and target-path metadata.
- `GOV-STANDING-BACKLOG-001` — WI-5668 remains an active, visible completion condition for the standing backlog project.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — keeps platform doctor and release-control behavior in the GT-KB root scope.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — keeps the classifier contract, review packet, and test evidence as durable artifacts rather than an unrepeatable session procedure.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — preserves the NO-GO → REVISED lifecycle and leaves detected remediation to separately owned work items.

## Prior Deliberations

- `DELIB-202667193` — owner decision requiring a self-driving mechanical completion gate for the skill-rename sweep, with bridge audit history and historical directories excluded.
- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` — owner authorization to process WI-5668 through the normal proposal, review, implementation-start, and verification lifecycle.
- `bridge/gtkb-wi5668-skill-rename-sweep-completion-gate-002.md` — the prior NO-GO; this revision adopts its required blocking release route and exact detector contract.

## Owner Decisions / Input

- `DELIB-202667193` records the owner’s decision that the sweep remains loud until the mechanically measured reference count reaches zero.
- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` records the owner’s direction to process WI-5668 under its scoped project authorization; no new owner approval is asserted by this revision.

## Inventory and Review Packet

The shared evaluator is the project’s deterministic inventory of active legacy skill-path findings. This numbered REVISED bridge document is the review packet for the bounded four-path implementation; it does not perform a bulk backlog mutation or defer any phase/path decision. Each detected path remains visible to its already-assigned remediation work item rather than being silently resolved or retired by this completion-gate slice.

## Proposed Scope

1. Add the exported deterministic evaluator and required project-doctor check in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.
2. Add focused doctor tests that use fixture repositories or injected tracked-path output to prove: positive legacy path detection; exclusion of bridge, runtime, RETIRED, BARRED, archive, and classifier-map paths; false-positive rejection for prose, canonical `gtkb-*` paths, and longer segment names; stable normalized ordering; fail-with-count at non-zero; and pass at zero.
3. Add a release-candidate gate helper/call in `scripts/release_candidate_gate.py` that consumes the exported evaluator and raises `GateFailure` for any remaining finding.
4. Add focused release-gate tests proving the helper’s pass output, its failure reason/count, and that `main()` reaches and obeys this lane without relying on a full release run.

## Explicit Non-Scope

- Editing any stale reference detected by this checker; those remain owned by WI-5661 through WI-5667.
- Editing generated adapters, templates, rules/config mirrors, scaffold artifacts, or their tests.
- Scanning untracked files, bridge audit history, retained/barred archival material, or runtime state.
- Any change to deployment, external services, the release workflow YAML, or the release-gate’s other existing lanes.

## Specification-Derived Verification Plan

| Specification | Focused verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Review `target_paths`, latest GO, and implementation-start packet before edits. | Only the four declared paths are modified under this thread. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest --rootdir=groundtruth-kb --override-ini=testpaths=tests groundtruth-kb/tests/test_doctor.py -q --tb=short` | Fixture cases prove the durable deterministic completion condition. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate and operative `bridge_applicability_preflight.py` plus `adr_dcl_clause_preflight.py`. | No missing required/advisory specifications and no blocking clause gap. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The doctor test command above plus `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_release_candidate_gate.py -q --tb=short`. | Doctor and release-decision outcomes are both executed and reported. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Validate active PAUTH and implementation-start authorization. | PAUTH/project/WI and four-path scope remain aligned. |
| `GOV-STANDING-BACKLOG-001` | `gt backlog list --id WI-5668 --json` and direct evaluator tests. | The open WI has a deterministic completion signal that blocks release until zero. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Path review plus focused tests from the GT-KB root. | No external or adopter-repository dependency is introduced. |

Before the implementation report, run `ruff check` and `ruff format --check` on the two changed Python source files and the two changed Python test files.

## Acceptance Criteria

1. The same evaluator drives project-doctor status and release-candidate status; there is no second scan implementation.
2. A remaining in-scope legacy skill-path reference makes the doctor required-fail and the release-candidate gate return non-zero.
3. Zero deterministic findings produces an explicit pass in both surfaces.
4. The alias derivation, grammar, enumeration, exclusions, ordering, samples, and false-positive behavior are covered by focused fixture tests.
5. Only the declared four target paths are attributed to implementation under this proposal.

## Risks and Rollback

The chief risk is an over-broad classifier creating false release blocks. The exact path grammar, map-driven aliases, explicit exclusions, and fixture set bound that risk. The second risk is diverging doctor and release behavior; using a shared evaluator removes duplicate classification logic. If the implementation must be reverted, revert only the four approved targets under a new governed authority and rerun both focused suites. Bridge chain and project authorization artifacts remain append-only.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_doctor.py`
- `scripts/release_candidate_gate.py`
- `platform_tests/scripts/test_release_candidate_gate.py`

## Recommended Commit Type

`feat`
