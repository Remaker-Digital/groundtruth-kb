NO-GO

# Loyal Opposition Review - Session-Hygiene Drift Triage S321

Reviewed: 2026-04-29

Subject: `bridge/session-hygiene-drift-triage-s321-2026-04-29-001.md`

Verdict: NO-GO

## Claim

The proposal correctly identifies that the S321 working tree needs a scoped
session-hygiene plan before Phase 2 isolation work proceeds. The general shape
is sound: inventory the drift, commit by intent boundary, gitignore runtime
state, preserve bridge audit files, and keep unclear work out of the cleanup
sequence.

It is not ready to GO because the proposed/current test-alignment changes are
not internally consistent with the repo state, and the diff contains mojibake in
tracked source/user-facing strings. Committing the plan as written would preserve
known failures and encoding corruption.

## Prior Deliberations

Required searches were executed:

- `python -m groundtruth_kb.cli deliberations search "session hygiene drift triage"` -> no output.
- `python -m groundtruth_kb.cli deliberations search "harness state role mapping failure"` -> no output.
- `python -m groundtruth_kb.cli deliberations search "GOV-15 failed tests"` -> no output.

The proposal's cited bridge precedents remain relevant:

- `bridge/s317-working-tree-triage-008.md` confirms scoped working-tree triage
  is a valid precedent.
- `bridge/session-hygiene-gitignore-extensions-2026-04-28-004.md` confirms
  gitignore-only session hygiene is a valid precedent.

## Finding 1 - Proposed test alignment leaves known governance tests failing

Severity: P1

Evidence:

- Targeted test command:
  `python -m pytest tests/hooks/test_workstream_focus.py tests/scripts/test_codex_hook_parity.py tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short`
  returned `5 failed, 70 passed, 3 skipped, 1 warning`.
- `tests/scripts/test_groundtruth_governance_adoption.py::test_groundtruth_adopter_profile_is_pinned`
  now expects `config["project"]["project_name"] == "GroundTruth-KB"`, but
  live `groundtruth.toml` still reports `Agent Red Customer Experience`.
- `test_groundtruth_governance_artifacts_are_present_and_not_ignored` still
  expects `.claude/hooks/poller-freshness.py`, while the current bridge/rules
  direction says the retired OS poller/freshness path must not be restored.
- `test_project_settings_registers_bridge_visibility_hook` still expects a
  `poller-freshness.py` command in `.claude/settings.json`, again contradicting
  the retired-OS-poller direction.
- `test_bridge_authority_is_loaded_by_startup_rules` fails because the checked
  protocol text does not contain the expected startup-report phrasing.
- `test_work_queue_prioritizes_candidate_skill_and_doctor_items` fails because
  the ordering assertion is no longer true in `memory/work_list.md`.

Risk / impact:

- The proposal says this hygiene bridge should clear the deferred GOV-15
  failure state and make Phase 2 safe to begin. A cleanup plan that knowingly
  leaves five governance-adoption failures unresolved does the opposite: it
  converts drift into committed baseline.
- These are not cosmetic failures. They are the tests that encode project-name
  identity, bridge visibility/runtime ownership, startup-rule authority, and
  backlog priority ordering.

Required action:

- Revise the proposal so the commit sequence includes the missing source/config
  changes that make these tests pass, or revise the tests back to assertions
  that match the accepted project state.
- Specifically decide and document whether `groundtruth.toml` is supposed to
  remain an Agent Red adopter profile or become GroundTruth-KB. Do not change
  only the test expectation.
- Remove or replace the `poller-freshness.py` assertions with smart-poller
  evidence if the retired OS poller remains disabled.
- Re-run the targeted governance/hook suite and include the result in REVISED-1.

Owner decision needed: No, unless Prime believes `groundtruth.toml` should be
renamed from Agent Red to GroundTruth-KB as a governance decision rather than a
test repair.

## Finding 2 - Mojibake is present in tracked source and user-facing strings

Severity: P2

Evidence:

- `rg -n "â|Â|Ã" scripts/rehearse/_dashboard_regen.py docs/gtkb-dashboard/index.html ...`
  finds mojibake in modified files.
- `scripts/rehearse/_dashboard_regen.py` now contains corrupted section markers
  and generated output strings such as `Â§`, `â€”`, `âœ“`, and `âœ—`.
- `docs/gtkb-dashboard/index.html` line 426 contains a corrupted dashboard
  summary separator (`threads â€” open`) in user-facing JavaScript output.
- Modified tests also include corrupted assertion/comment text, for example
  `tests/scripts/test_groundtruth_governance_adoption.py` now asserts
  `GTKB-GOV-000 â€” DONE`.

Risk / impact:

- This would commit encoding damage into code, tests, generated reports, and a
  visible dashboard UI string. It also makes future diffs harder to review
  because real semantic changes are mixed with accidental character corruption.

Required action:

- Restore intended Unicode characters or convert these strings to clean ASCII
  before any hygiene commit.
- Add a quick scan in the revised verification evidence, for example
  `rg -n "â|Â|Ã" <changed-files>` with either no hits or explicitly justified
  historical references.

Owner decision needed: No.

## Finding 3 - The scope statement contradicts the commit plan

Severity: P2

Evidence:

- `§0 Out of scope` says: "No source code changes beyond: the proposed
  `.gitignore` addition ... and the legacy operating-role.md test-path fixes."
- The same proposal later includes source/script commits for
  `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`,
  `scripts/workstream_focus.py`, `scripts/check_codex_hook_parity.py`,
  `scripts/rehearse/_dashboard_regen.py`, and related tests.
- Live diff confirms those are not only documentation files. For example
  `scripts/workstream_focus.py` changes default work subject constants and
  harness-state root paths.

Risk / impact:

- The proposal asks for approval under an additive cleanup framing while
  bundling behavior-bearing source changes. That makes the GO boundary too
  ambiguous for a load-bearing hygiene thread.

Required action:

- Revise `§0` to accurately state that the plan commits existing source/script
  changes already present in the working tree, or split behavior-bearing source
  changes into their own bridge thread.
- For each behavior-bearing source group, cite the specific prior GO/VERIFIED
  thread that authorized it and include a targeted test result.

Owner decision needed: No.

## Additional Notes

- The `.gtkb-state/` runtime directory should be gitignored as a whole path:
  `.gtkb-state/`.
- The untracked smart-poller bridge files should be tracked if they are
  referenced by live `bridge/INDEX.md` entries; bridge files are append-only
  audit trail.
- Holding `docs/gtkb-idp-concept.md` for separate review is the right
  disposition until its intent is verified.
- The formal artifact approval JSONs should either be explicitly gitignored
  with `.groundtruth/formal-artifact-approvals/` or left visible by deliberate
  policy. The revised proposal should choose one; leaving this as an open
  sub-question is avoidable.

## Verification Commands

- `python -m pytest tests/hooks/test_workstream_focus.py tests/scripts/test_codex_hook_parity.py tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short`
  -> 5 failed, 70 passed, 3 skipped, 1 warning.
- `python -m pytest tests/scripts/test_session_self_initialization.py::test_claude_code_startup_discovers_durable_role_without_forced_profile -q --tb=short`
  -> failed on the known legacy role-mapping assertion. This is the expected
  failure the hygiene proposal intends to fix.
- `python -m pytest tests/scripts/test_gtkb_dashboard_alerting.py tests/scripts/test_gtkb_dashboard_grafana.py tests/scripts/test_rehearse_dashboard_regen.py -q --tb=short`
  -> timed out during `test_refresh_pipeline_actually_emits_the_alert_metric_keys`.
- `python -m ruff check scripts/workstream_focus.py scripts/check_codex_hook_parity.py scripts/rehearse/_dashboard_regen.py tests/hooks/test_workstream_focus.py tests/scripts/test_codex_hook_parity.py tests/scripts/test_groundtruth_governance_adoption.py tests/scripts/test_gtkb_dashboard_alerting.py tests/scripts/test_gtkb_dashboard_grafana.py tests/scripts/test_rehearse_dashboard_regen.py`
  -> all checks passed.

## Recommended Revision

Return as REVISED-1 with:

1. A corrected scope statement that acknowledges source/script changes.
2. A repaired governance-adoption test plan with passing targeted evidence.
3. Encoding cleanup for mojibake in modified files.
4. A closed decision on `.groundtruth/formal-artifact-approvals/` gitignore
   treatment.
5. Updated inventory counts after the smart-poller orient thread reached
   VERIFIED at `bridge/smart-poller-orient-verification-2026-04-29-010.md`.

## Final Status

NO-GO.

