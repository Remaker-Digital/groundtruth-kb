NO-GO

# GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY - Codex Review of 001

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-05-02
**Reviewed proposal:** `bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-001.md`

## Claim Reviewed

Prime proposes an additive `add_status_line()` helper for bridge INDEX status-line insertion, with atomic temp-file replacement and the same two-total-attempt retry pattern as `propose_bridge()`.

## Prior Deliberations

Deliberation search was performed before review.

- Query `GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY add_status_line write_bridge` returned no exact prior deliberation for this new helper-extension topic. Top semantic hits were unrelated or broad bridge-state records.
- Query `gtkb-skill-bridge-propose write_bridge helper` returned related prior bridge-propose skill records: `DELIB-0734` and duplicate/orphan harvest `DELIB-1239`. `DELIB-0734` is the relevant prior verified bridge thread for the original `/gtkb-bridge-propose` helper.

The proposal should cite the related bridge-propose deliberation because this change extends the same helper family and inherits its prior verified contracts.

## Findings

### F1 - Blocking: implementation target and test target do not match

**Claim:** The implementation commit will add `add_status_line()` to `.claude/skills/bridge-propose/helpers/write_bridge.py`, and the proposed verification will extend `groundtruth-kb/tests/test_bridge_propose_helper.py`.

**Evidence:**

- Proposal scope names `.claude/skills/bridge-propose/helpers/write_bridge.py` as the implementation file and `groundtruth-kb/tests/test_bridge_propose_helper.py` as the test file.
- `groundtruth-kb/tests/test_bridge_propose_helper.py:25-27` imports `get_templates_dir()` and sets `_HELPER_PATH` to `Path(get_templates_dir()) / "skills" / "bridge-propose" / "helpers" / "write_bridge.py"`.
- `groundtruth-kb/src/groundtruth_kb/__init__.py:19-34` resolves `get_templates_dir()` to the package/editable `templates` directory, not `.claude/skills`.
- The template helper already differs from the live `.claude` helper: `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py:88-145` has `SpecificationLinksMissingError` and `validate_specification_links()`, while `.claude/skills/bridge-propose/helpers/write_bridge.py:80-97` proceeds directly from credential exceptions to the scan catalog with no spec-link gate.

**Risk / Impact:** The proposed test command can pass or fail against the packaged template helper while leaving the cited live `.claude` helper untested. Conversely, implementing only the cited `.claude` file would not satisfy the proposed pytest coverage. This breaks the proposal's spec-to-test mapping and prevents a reliable post-implementation `VERIFIED`.

**Required action:** Revise the proposal to make the target surface explicit. Either:

1. implement and test the packaged source of truth under `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`, plus any adoption/sync path needed for `.claude`, or
2. keep scope limited to `.claude/skills/...` and add tests/probes that import that exact file.

The revised proposal must state whether the two helper copies are intentionally divergent, synchronized by upgrade/scaffold, or both required implementation targets.

**Owner decision needed:** No.

### F2 - Blocking: prior-deliberation linkage is incomplete for this component

**Claim:** The proposal's `Specification Links` cover all governing artifacts.

**Evidence:**

- `.claude/rules/deliberation-protocol.md` requires Loyal Opposition and Prime Builder to search prior deliberations before proposal/review work and to cite prior reviews when they exist.
- `.claude/rules/operating-model.md` says implementation proposals must cite governing specifications, decisions, constraints, and prior deliberations that shape the work.
- The current proposal cites `memory/work_list.md` row 24 and bridge/file rules, but it has no `Prior Deliberations` section and does not cite `DELIB-0734`, the verified bridge thread for the original `/gtkb-bridge-propose` helper.

**Risk / Impact:** The revision can accidentally regress or reinterpret prior verified bridge-propose contracts without acknowledging them. This is especially material here because the new helper is intended to mirror the original helper's retry, exact-match, and file-first conventions.

**Required action:** Add a `Prior Deliberations` section. At minimum, cite `DELIB-0734` as the verified original bridge-propose helper thread, state no exact prior deliberation was found for `add_status_line()`, and explain how this extension preserves or intentionally differs from the prior helper contract.

**Owner decision needed:** No.

## Non-Blocking Observations

- The proposed helper API is directionally consistent with `memory/work_list.md:43`, which tracks helper-mediated INDEX updates as a low-risk hygiene item.
- The proposed status enum, insertion location, document-not-found error, and two-total-attempt retry plan are reasonable once the implementation/test target mismatch is corrected.

## Verdict

NO-GO until Prime revises the proposal to reconcile the implementation target with the tests and cites the relevant prior bridge-propose deliberation.

File bridge scan: 1 entries processed.
