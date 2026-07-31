NEW
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default;thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


# Implementation Proposal — WI-5667 clean authorization recovery

bridge_kind: prime_proposal
Document: gtkb-wi5667-scaffold-managed-skill-rename-recovery
Version: 001
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5667

target_paths: ["groundtruth-kb/templates/managed-artifacts.toml", "groundtruth-kb/templates/skills/gtkb-decision-capture/SKILL.md", "groundtruth-kb/templates/skills/gtkb-decision-capture/helpers/record_decision.py", "groundtruth-kb/templates/skills/gtkb-bridge-propose/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/gtkb-spec-intake/SKILL.md", "groundtruth-kb/templates/skills/gtkb-spec-intake/helpers/spec_intake.py", "groundtruth-kb/templates/skills/gtkb-bridge/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/revise_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/impl_report_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/show_thread_bridge.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_scaffold_skills.py", "groundtruth-kb/tests/test_upgrade_skills.py", "groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/test_doctor.py"]

implementation_scope: source | tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Recover the owner-authorized WI-5667 managed scaffold/template rename through a
new, independently reviewable chain with readable PB provenance. The original
`gtkb-wi5667-scaffold-managed-skill-rename` chain is retained as historical
evidence but cannot issue an implementation packet because its v001 author-role
metadata is unreadable. This proposal does not rewrite that chain.

## Claim

After an independent LO GO and a successful packet for this recovery slug,
Prime Builder will revalidate and commit only the 17 paths below. The existing
uncommitted candidate content is observed evidence, not attributed work: it
will be staged only after the new packet succeeds and all verification gates
are rerun. No pre-GO source, template, test, or fixture mutation is requested
by this proposal filing.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-202667193` selects the gtkb-prefixed
managed scaffold/template outcome and the active exact WI-5667 authorization
covers this recovery. The fresh chain is required solely because the historical
chain cannot prove implementation-start authority.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-202667193` — owner-directed gtkb-prefixed scaffold/template and
  managed-artifact outcome.
- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` — lifecycle gates are retained
  rather than bypassed for the recovery.
- `bridge/gtkb-wi5667-scaffold-managed-skill-rename-006.md` — requires a fresh
  append-only recovery proposal, independent GO, claim, and packet.

## Owner Decisions / Input

- `DELIB-202667193` is the owner decision for the actual rename deliverable.
- No decision is requested for fixture capture: it is out of scope and remains
  quarantined evidence.

## Exact Scope

The recovery will materialize eleven canonical managed template artifacts,
retarget their registry records and doctor expectations, and update bounded
temporary-project tests. The exact target list is the machine-readable
`target_paths` header above: one registry, eleven templates, one doctor module,
and four test files. `groundtruth-kb/tests/test_doctor.py` is an allowed
verification target but has no current candidate diff.

The retained bare template families remain untouched migration sources. A
successful recovery must not add any target beyond the declared 17 paths.

## Quarantine And Explicit Exclusions

- Do not read, modify, stage, restore, rebaseline, attribute, or commit any
  path under either `groundtruth-kb/tests/fixtures/scaffold_golden/local-only`
  or `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent`.
- Do not run `scripts/_capture_scaffold_golden.py`, including help or dry-run
  modes.
- Do not modify bare retained templates, WI-5640 policy/interpreter/tests,
  generated adapters, canonical runtime skills, or unrelated baseline-audit
  behavior.

## Implementation And Verification Plan

1. Acquire a recovery-slug claim and issue
   `python scripts/implementation_authorization.py begin --bridge-id
   gtkb-wi5667-scaffold-managed-skill-rename-recovery`. Abort before staging if
   it cannot issue a current packet.
2. Verify the staged set is a subset of the 17 target paths and excludes both
   scaffold-golden roots; re-run `git diff --check` on the exact set.
3. Run the exact focused selector:

```text
python -m pytest --rootdir=groundtruth-kb --override-ini=testpaths=tests groundtruth-kb/tests/test_scaffold_skills.py groundtruth-kb/tests/test_upgrade_skills.py::test_plan_upgrade_adds_missing_bridge_propose_skill_at_same_version groundtruth-kb/tests/test_upgrade_skills.py::test_plan_upgrade_adds_missing_spec_intake_skill_at_same_version groundtruth-kb/tests/test_upgrade_skills.py::test_plan_upgrade_adds_missing_spec_intake_helper_at_same_version groundtruth-kb/tests/test_execute_creates_missing_spec_intake_files_at_same_version groundtruth-kb/tests/test_upgrade_skills.py::test_plan_upgrade_adds_missing_bridge_skill_files_at_same_version groundtruth-kb/tests/test_upgrade_skills.py::test_execute_creates_missing_bridge_skill_files_at_same_version groundtruth-kb/tests/test_managed_registry.py::test_bridge_skill_records_are_managed_for_dual_agent_profiles groundtruth-kb/tests/test_managed_registry.py::test_scaffold_dual_agent_copies_everything groundtruth-kb/tests/test_managed_registry.py::test_upgrade_dual_agent_manages_full_set_including_gap_28_rules groundtruth-kb/tests/test_doctor.py::test_check_rules_with_files -q --tb=short
```

4. Run Ruff check and `ruff format --check` on the doctor module and four test
   files, then bridge applicability and mandatory clause preflights.
5. Commit only the packet-authorized slice, file a committed implementation
   report, and leave terminal verification to independent LO.

## Pre-Filing Preflight

- `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/wi5667-recovery-001.md` passed with packet hash `sha256:e0882c0ce4e0ade391f9fa4305849e375e26e65b53b40463b17eb3f7e38bc730`, no missing required/advisory specifications, and no blocking errors.
- `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/wi5667-recovery-001.md` passed: three must-apply clauses, zero evidence gaps, and zero blocking gaps.

## Specification-Derived Verification Mapping

| Requirement | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Current recovery GO, host-bound claim, packet, exact staged boundary, and protected-commit check. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability and mandatory clause preflights on this recovery proposal/report. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The 17-test temporary-project selector plus Ruff check/format and scoped diff check. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Exact 17-path commit and append-only bridge report preserve the recovery provenance. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | No VERIFIED request until a committed report and independent finalization exist. |

## Acceptance Criteria

- A fresh temporary dual-agent scaffold/upgrade emits exactly eleven canonical
  gtkb-prefixed managed artifacts.
- Registry, templates, doctor, and the declared tests agree on canonical names.
- Only declared paths are committed; all scaffold-golden paths remain excluded.
- A fresh packet and independent LO review, not historic chain metadata,
  determine any terminal status.

## Cross-Harness Disposition

The managed registry emits shared Claude-profile artifacts and the bounded
temporary-project tests validate the dual-agent profile. No adapter generation
or harness-local runtime change is included.

## Risks And Rollback

The key risk is absorbing unowned dirty content or the quarantined fixture
diff. The recovery fails closed unless the new packet authorizes the exact
declared slice and all checks rerun. Rollback, if later needed, is a separately
governed revert of only the recovery commit; historical chains and retained
templates remain append-only evidence.

## Recommended Commit Type

fix
