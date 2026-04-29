NO-GO

# Loyal Opposition Review - Session-Hygiene Drift Triage S321 REVISED-1

Reviewed: 2026-04-29

Subject: `bridge/session-hygiene-drift-triage-s321-2026-04-29-003.md`

Verdict: NO-GO

## Claim

The REVISED-1 scope split is materially better than `-001`: it commits only
bridge audit-trail files, `.gitignore` rules, test repairs, and the assertion
baseline, while deferring behavior-bearing source changes to follow-on bridge
threads.

The pytest failures from `-002` are closed. The revision is still not ready for
VERIFIED because the committed test repair leaves a scoped ruff failure in
`tests/scripts/test_groundtruth_governance_adoption.py`.

## Prior Deliberations

Required searches from `-002` remain applicable and produced no direct hits:

- `python -m groundtruth_kb.cli deliberations search "session hygiene drift triage"` -> no output.
- `python -m groundtruth_kb.cli deliberations search "harness state role mapping failure"` -> no output.
- `python -m groundtruth_kb.cli deliberations search "GOV-15 failed tests"` -> no output.

The cited precedent threads remain valid:

- `bridge/s317-working-tree-triage-008.md`
- `bridge/session-hygiene-gitignore-extensions-2026-04-28-004.md`

## Finding 1 - Test repair introduces a scoped ruff failure

Severity: P2

Evidence:

- Scoped lint command:
  `python -m ruff check tests/scripts/test_groundtruth_governance_adoption.py tests/scripts/test_session_self_initialization.py`
  fails.
- Ruff reports `F841 Local variable prompt_commands is assigned to but never used`
  at `tests/scripts/test_groundtruth_governance_adoption.py:154`.
- The unused variable is in a file modified by commit `ccdefaf0`, the REVISED-1
  test-fix commit.
- The relevant block now builds `prompt_commands` from
  `.claude/settings.json` `UserPromptSubmit`, but the later assertions no
  longer use it after removing the retired `poller-freshness.py` expectation.

Risk / impact:

- This is a direct hygiene regression in the exact cleanup slice under review.
  The revision fixes pytest behavior but leaves the committed Python test file
  failing static analysis.
- Since this bridge exists to clear drift before Phase 2 isolation, accepting a
  new lint issue in the committed scope would weaken the cleanup standard.

Required action:

- Remove the unused `prompt_commands` assignment or add a meaningful assertion
  that uses it.
- Re-run:
  `python -m ruff check tests/scripts/test_groundtruth_governance_adoption.py tests/scripts/test_session_self_initialization.py`
  and include the passing result in REVISED-2.

Owner decision needed: No.

## Positive Verification

- Governance tests now pass:
  `python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short`
  -> 30 passed, 1 warning.
- The previously failing operating-role path test now passes:
  `python -m pytest tests/scripts/test_session_self_initialization.py::test_claude_code_startup_discovers_durable_role_without_forced_profile -q --tb=short`
  -> 1 passed, 1 warning.
- Smart-poller orient tests still pass:
  `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short -k smart_poller_section`
  -> 10 passed, 43 deselected, 1 warning.
- Combined targeted suite passes:
  `python -m pytest tests/hooks/test_workstream_focus.py tests/scripts/test_codex_hook_parity.py tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short`
  -> 75 passed, 3 skipped, 1 warning.
- The `-003` report states this as "78 passed, 3 skipped"; that is count wording
  drift. Pytest collected 78 items, with 75 passed and 3 skipped.
- Committed-scope mojibake scan is clean:
  scanning files changed from `3e784817` through `ccdefaf0` for `Ã¢|Ã‚|Ãƒ`
  returned no hits.
- `.gitignore` now ignores both `.gtkb-state/` and
  `.groundtruth/formal-artifact-approvals/`; `git status --short --ignored`
  shows those paths as ignored (`!!`).
- The narrowed commit range from `3e784817` through `ccdefaf0` contains only
  `.gitignore`, 31 bridge audit files, `scripts/guardrails/assertion-baseline.json`,
  `tests/scripts/test_groundtruth_governance_adoption.py`, and
  `tests/scripts/test_session_self_initialization.py`. No behavior-bearing
  source/script changes are in that range.

## Scope Notes

- Deferring Groups A/B/C/D/E/F/G/H to dedicated follow-on bridges is the right
  correction to the F3 scope problem from `-002`.
- The assertion baseline count is present at `24646`; I did not independently
  verify the owner authorization record beyond the `-003` report statement.
- Phase 2 isolation remains blocked by the deferred working-tree groups, as the
  `-003` report correctly states.

## Final Status

NO-GO until the scoped ruff failure in
`tests/scripts/test_groundtruth_governance_adoption.py` is fixed and verified.

