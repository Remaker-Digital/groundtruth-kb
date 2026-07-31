REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5767-auto-finalize-sweep-liveness
Version: 009
Date: 2026-07-30 UTC
Responds to: bridge/gtkb-wi5767-auto-finalize-sweep-liveness-008.md

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5767
target_paths: ["scripts/auto_finalize_sweep.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", ".claude/skills/gtkb-bridge-propose/helpers/write_bridge.py", ".codex/skills/gtkb-bridge-propose/helpers/write_bridge.py", "platform_tests/scripts/test_doctor_auto_finalize_sweep_liveness.py", "platform_tests/hooks/test_auto_finalize_verified_verdicts.py", "platform_tests/skills/test_bridge_propose_helper.py"]

implementation_scope: seven_path_sweep_liveness_doctor_and_managed_helper_projection
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# WI-5767 REVISED — Complete Managed-Projection Cohort for Sweep Liveness

## Revision Claim

This revision accepts the version-008 NO-GO and corrects the sole reviewed
scope defect before any WI-5767 implementation. The canonical Claude and
generated Codex `write_bridge.py` helpers are separate tracked regular files,
and the approved test suite requires their bytes to remain identical. The
Codex projection is therefore added as the seventh exact target. No prior GO,
claim, or implementation-start packet is reused.

The current draft claim is row `35018`, kind `draft`, held by Prime Builder
session `019fb19b-7814-73c1-8707-204e432cbf00`. It authorizes drafting only.
This candidate does not authorize a protected edit, generated projection,
staging action, commit, implementation report, or finalization. A fresh
independent GO responding to this exact version, followed by a fresh exact
`go_implementation` claim and finalized schema-v3 implementation-start packet,
remains mandatory.

## Findings Addressed

### V008-F1 — the Codex managed-helper projection was omitted

Resolved by adding
`.codex/skills/gtkb-bridge-propose/helpers/write_bridge.py` to `target_paths`.
The canonical and Codex paths are presently separate regular tracked files,
both index-clean, with the same Git blob
`dbce8441e23521f29ddc652ef56e81d5ec0db723` and raw SHA-256
`7F4E04698F967BA30C324AE327A39FD2517A51595F169C62AD3CE73F945B33A3`.
`platform_tests/skills/test_bridge_propose_helper.py` directly asserts exact
byte identity. The read-only generator check
`python scripts/generate_codex_skill_adapters.py --check` currently reports
`Codex skill adapters: PASS (44 adapters current)`.

Implementation must change the canonical helper, project it through the
managed adapter generator, and verify that the resulting diff touches only the
two declared helper paths within this concern. If generator output introduces
any undeclared path or pre-existing projection drift, implementation stops and
returns through another append-only revision; hand-editing an undeclared
projection is not an allowed substitute.

### V008-F2 — GO-006 and its start evidence are stale

Accepted. GO-006 approved a six-path cohort and cannot authorize this seven-path
revision. The old implementation claim is absent and the old schema-v3 packet
is historical evidence only. Fresh independent review, claim, and start
evidence must bind version 009, its eventual new GO, the seven exact targets,
current project authority, and operation-time target identities.

## Current Project, Authorization, and Work-Item State

- `PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729` is active, version 1.
- WI-5767 is an active first-class member through
  `PWM-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-WI-5767`, membership version
  2, order 11. Its compatibility `approval_state: unapproved` is historical
  metadata and is not controlling implementation authority.
- The list-free whole-project authorization
  `PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM` is active version
  6, row 944, under `DELIB-202667710`. Version 6 preserves the version-5
  program scope and adds only `documentation` for the neighboring WI-5763
  lane. It permits `source`, `test`, `test_addition`, `configuration`,
  `metadata`, `governance_evidence`, `bridge`, and `documentation`, covering
  all seven WI-5767 target classes without a per-WI exception.
- The PAUTH continues to forbid `dispatcher_mutation`,
  `external_system_mutation`, `credential_lifecycle`, `push`,
  `history_rewrite`, `deployment`, `release`, and `destructive_cleanup`.
  Dispatcher/TAFE activation, routing, eligibility, and runtime mutation are
  outside this proposal.

## Exact Seven-Path Cohort and Collision State

The six existing non-doctor paths are clean; the new doctor-liveness test does
not yet exist. Current clean identities are:

| Target | Current identity | State |
| --- | --- | --- |
| `scripts/auto_finalize_sweep.py` | Git blob `aaf6dc2382b994b7a1f8c44b81c04a84bcbf4ea2`; SHA-256 `6F08E459914D8C397D57453E80C36CBD45F6612A01D415AC2FFE12A3E104D91F` | clean |
| `.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py` | Git blob `dbce8441e23521f29ddc652ef56e81d5ec0db723`; SHA-256 `7F4E04698F967BA30C324AE327A39FD2517A51595F169C62AD3CE73F945B33A3` | clean canonical |
| `.codex/skills/gtkb-bridge-propose/helpers/write_bridge.py` | same Git blob and SHA-256 as canonical | clean generated projection |
| `platform_tests/hooks/test_auto_finalize_verified_verdicts.py` | Git blob `3c3bd4d6cbb787051261a5f96e33ec8b4e1b0c04`; SHA-256 `152846C88BA659901FBADCCB642929793292F5E709DB2120A26C4EF1591D8F1A` | clean |
| `platform_tests/skills/test_bridge_propose_helper.py` | Git blob `b6fe8b9335e8f4c1f3e0f9218234aec89a5f1b24`; SHA-256 `AA80A4F11BC334D8FDC6853D9AC6E2397F1EC9D3231F65D85A620B4DECC6E47D` | clean |
| `platform_tests/scripts/test_doctor_auto_finalize_sweep_liveness.py` | absent | approved test addition |

`groundtruth-kb/src/groundtruth_kb/project/doctor.py` is not clean. It is
currently staged as Git blob `4dbb18a35f390f2916aa46417b6b1e89b91a8605`, raw SHA-256
`E20D1E7D5E15359A294527767B169F43750F77B0A7CFF7E791F782E0AB4960D7`.
The staged 15-line subprocess-decoding hunk belongs to WI-5688, whose bridge
thread is latest `VERIFIED` at version 006. Its eight-path finalization cohort
(six bridge files, `doctor.py`, and its focused test) is presently staged and
no WI-5688 commit is visible. This revision does not adopt, overwrite, unstage,
or finalize that cohort.

WI-5688 serialization is a hard implementation-start prerequisite: its exact
staged cohort must first be governedly finalized or otherwise reach a clean,
authoritatively explained state. Prime Builder must then re-read `doctor.py`,
recompute the seven-path identities, confirm no competing claim, and mint the
fresh start packet from that post-WI-5688 baseline. Any unexplained staged or
unstaged overlap stops implementation.

## Dependency and Composition Boundaries

- **WI-5688:** hard serialization dependency for the shared `doctor.py`
  target, as described above. This proposal performs no WI-5688 Git or bridge
  action.
- **WI-5763:** owns finalizer trailers, durable finalization-audit writes, and
  the governed verdict-filing surface. Its latest thread remains NO-GO at
  version 004. Until that lane lands, WI-5767's owner-selected
  `unattributed-finalizing-commit` disposition remains WARN, not FAIL.
- **WI-5694:** owns packet-expiry-recovery actor/session schema. It remains a
  separate open work item and has no numbered implementation thread found.
- MemBase records no explicit `depends_on_work_items` edge for WI-5767 and the
  parent project has no first-class project dependency rows. These composition
  boundaries therefore constrain target ownership and behavior without
  pretending that adjacent lanes grant implementation authority.

## Proposed Change

The version-005 technical design and owner-selected calibration remain
unchanged, with the managed Codex projection added to the executable cohort.

1. `scripts/auto_finalize_sweep.py` gains an opt-in read-only `--probe` that
   runs the existing dry-run classification and emits backlog, would-finalize,
   and skip-reason JSON. The normal Stop-hook path, stdin drain, disable flag,
   fail-soft behavior, and unconditional exit-zero contract remain unchanged.
   Audit rows gain only a best-effort actor block containing source, available
   session identifiers, and PID; missing identifiers never block append.
2. `doctor.py` gains the payload, wrapper, and registration for
   `auto_finalize_sweep_liveness`: zero drain across the latest 20 audit rows
   against a non-empty WI-4871 backlog is FAIL; stale or insufficient
   observation is WARN; a post-cutoff finalizing commit without required audit
   or trailer attribution is WARN; healthy or empty-backlog state is PASS.
   Probe execution is interpreter-explicit, timeout-bounded, and fail-soft.
3. The canonical Claude bridge-propose `write_bridge.py` gains a module entry
   usage surface: `--help`/`-h` writes usage to stdout and exits 0; any other
   direct invocation writes usage to stderr and exits 2. The text identifies
   the import-only public functions, version-1-only constraint, and governed
   append/verdict route. Imports and public signatures remain unchanged.
4. The canonical helper change is projected to the separately tracked Codex
   helper through the managed generator. Both helper bytes must remain exact,
   and the existing parity assertion remains intact.

The finalizer write-side changes and packet-recovery schema remain in their
adjacent owning lanes. No rule file, hook registration, settings file,
dispatcher/TAFE surface, MemBase record, credential, external system,
deployment, release, or Git history is changed by this slice.

## Cross-Harness Disposition

The sweep script is the same shared script registered for Claude and Codex;
this proposal changes neither registration. The bridge helper has one canonical
Claude source plus a separately tracked generated Codex projection, now both
explicitly in scope. Exact byte parity and `generate_codex_skill_adapters.py
--check` are mandatory evidence. Doctor and the three test modules are
harness-neutral. No parity waiver is requested.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `SPEC-1830`
- `GOV-10`
- `GOV-12`
- `SPEC-1662` (`GOV-18`)
- `GOV-15`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202667531`, `DELIB-202667533`, and `DELIB-202667534` establish the
  Advisory Corrections project, whole-project program authority, and WI-5767
  disposition.
- `DELIB-202667710` authorizes the current program PAUTH version 6, adding only
  the neighboring WI-5763 documentation class while preserving the version-5
  WI-5767 scope, bans, lifecycle gates, and completion discipline.
- `DELIB-202667698`, `DELIB-202667699`, and `DELIB-202667700` close OD-A,
  OD-B, and OD-C respectively.
- `DELIB-WI5116-PHASE1-SWEEP-DIAGNOSIS-20260709` is the earlier zero-finalize
  diagnosis that lacked a durable liveness assertion.
- `DELIB-20266278` authorizes the auto-finalization sweep program.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` confirms that
  active project membership and project authorization, not compatibility
  per-WI approval state, control implementation.
- Source advisory chain:
  `bridge/gtkb-lo-auto-finalize-sweep-zero-success-advisory-001.md` and
  `bridge/gtkb-lo-auto-finalize-sweep-zero-success-advisory-002.md`.

## Owner Decisions / Input

No new owner decision is required.

- **OD-A — `DELIB-202667698`:** latest 20 audit entries is the default
  zero-drain liveness window, retaining the environment override.
- **OD-B — `DELIB-202667699`:** unattributed finalizing commits remain WARN
  until WI-5763 lands trailers and durable audit evidence.
- **OD-C — `DELIB-202667700`:** detection begins at this change's landing date
  through a module constant; historical commits are not flagged retroactively.

These decisions do not waive the fresh GO, exact claim/start, collision
serialization, operation-time PAUTH, independent VERIFIED, or finalization
gates.

## Requirement Sufficiency

Existing requirements are sufficient. The version-008 defect is exact target
completeness, not a missing behavior or authority decision. The active program
PAUTH covers the corrected cohort, and the three behavioral calibrations are
already durable. WI-5688 is a serialization condition, not an owner AUQ.

## Specification-Derived Verification Plan

| Governing requirement | Verification | Required result |
| --- | --- | --- |
| Bridge/project/start authority | Re-run applicability and clause preflights; verify active membership and PAUTH v6; require fresh independent GO, exact claim, and schema-v3 packet | Seven-path cohort allowed at operation time; no prior GO or packet reused. |
| Cross-harness projection parity | Run generator from canonical helper, inspect exact scoped diff, assert helper bytes, then run `python scripts/generate_codex_skill_adapters.py --check` | Claude and Codex helpers are byte-identical; generator check passes; no undeclared generated path changes. |
| Sweep probe and nonimpairment | Extend `platform_tests/hooks/test_auto_finalize_verified_verdicts.py` | Probe emits required JSON without committing or writing finalization actions; normal Stop-hook behavior and both registrations remain unchanged; actor metadata is additive and fail-soft. |
| Doctor liveness behavior | Add `platform_tests/scripts/test_doctor_auto_finalize_sweep_liveness.py` | Exact zero-drain FAIL, stale-log WARN, empty/healthy PASS, post-cutoff attribution WARN, and trailer/audit exemptions pass. |
| Help-surface behavior | Extend `platform_tests/skills/test_bridge_propose_helper.py` | `--help` exits 0 on stdout; invalid direct use exits 2 on stderr; imports/public helpers remain compatible; canonical/Codex bytes match. |
| GOV-10, GOV-12, SPEC-1662, and scope | Run all three focused suites, Ruff check, Ruff format check, scoped status/diff/numstat, and `git diff --check` | Behavioral interfaces are exercised; all checks pass; exactly seven targets, including the new test and generated projection, comprise the WI-5767 cohort. |
| Collision safety | Confirm WI-5688 finalization is no longer staged and recompute the doctor baseline immediately before start | No foreign index/worktree overlap or competing claim exists; otherwise stop without mutation. |
| Independent terminal integrity | File a current-evidence implementation report only after authorized implementation, obtain independent verification, then use governed atomic finalization | Reviewed cohort only; no manual staging/commit, push, dispatcher/TAFE action, release, deployment, or external mutation. |

## Acceptance Criteria

1. A fresh independent GO approves this exact seven-path revision.
2. WI-5688's staged finalization cohort is resolved before implementation
   start; every target identity and collision check is re-observed afterward.
3. A fresh exact `go_implementation` claim and schema-v3 packet bind the
   current proposal/GO frontier, PAUTH v6, active membership, and seven paths.
4. Doctor distinguishes zero-drain FAIL, insufficient-observation WARN,
   attribution WARN, and healthy/empty PASS using the owner-selected values.
5. Probe remains read-only; normal dual-registered Stop-hook behavior is
   unchanged; audit actor context is additive and fail-soft.
6. Canonical and Codex bridge helpers remain byte-identical after managed
   projection, with the documented direct-help exit/stream behavior and
   unchanged import APIs.
7. Focused tests, generator parity, Ruff check/format, scoped diff, and diff
   check pass. Any undeclared generated path or foreign collision aborts.
8. Independent verification and governed atomic finalization precede closure.
   Push, history rewrite, dispatcher/TAFE mutation, credential lifecycle,
   deployment, release, external-system mutation, and destructive cleanup
   remain prohibited.

## Pre-Filing Preflight Subsection

Candidate preflights were run against this `.gtkb-state` draft after the
seven-target correction and current PAUTH-v6 refresh:

- `python scripts/bridge_applicability_preflight.py --bridge-id
  gtkb-wi5767-auto-finalize-sweep-liveness --content-file <this-draft>` exited
  0 with `preflight_passed: true`, `missing_required_specs: []`,
  `missing_advisory_specs: []`, `unclassified_target_paths: []`, and
  `blocking_errors: []`. Operation-time proposal evaluation selected active
  PAUTH version 6 and allowed both `implementation_packet_create` and
  `implementation_start` for all seven paths.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id
  gtkb-wi5767-auto-finalize-sweep-liveness --content-file <this-draft>` exited
  0 in mandatory mode: five clauses evaluated, three `must_apply`, zero
  must-apply evidence gaps, and zero blocking gaps.

These are candidate-draft observations, not filing or implementation
authority. The governed writer must repeat them against the exact filing bytes.
A failure, version race, missing specification, unclassified target,
project/PAUTH drift, or blocking clause gap aborts publication. This draft must
not be manually copied into `bridge/`.

## Risk And Rollback

The principal concurrency risk is the staged WI-5688 cohort on `doctor.py`;
serialization and a fresh post-finalization baseline are mandatory. The main
projection risk is broad generator output; any path outside the seven-target
cohort fails closed and requires a revised plan. The functional risk remains
over-broad liveness or attribution findings, constrained by the owner-selected
window/cutoff/severity and behavioral fixtures.

Before implementation, rollback is release of the draft claim and another
append-only disposition. After independently verified implementation, rollback
is a separately governed exact seven-path repair. No reset, checkout, manual
unstage, broad revert, process mutation, dispatcher/TAFE action, push, history
rewrite, credential action, external mutation, deployment, release, or
destructive cleanup is authorized.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
