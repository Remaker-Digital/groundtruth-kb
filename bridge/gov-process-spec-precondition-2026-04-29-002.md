NO-GO

# Loyal Opposition Review - Interim Stop-the-Bleeding Spec-Linkage Rule

**Document:** `gov-process-spec-precondition-2026-04-29`
**Reviewed version:** `bridge/gov-process-spec-precondition-2026-04-29-001.md`
**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-29

## Claim

The need is valid and the existing framework hook is real, but this proposal cannot receive GO because its rule, mechanism, tests, and migration claims describe different enforcement contracts. The revision should choose one contract and make the implementation, tests, and acceptance criteria match it.

## Findings

### F1 - Rule/mechanism mismatch blocks implementation

**Severity:** High

**Evidence:** Section 0 says the bridge will add `scripts/check_bridge_spec_linkage.py`, `.claude/hooks/bridge-proposal-spec-linkage-gate.py`, a new `.claude/rules/bridge-proposal-spec-linkage.md`, and tests for those new surfaces: `bridge/gov-process-spec-precondition-2026-04-29-001.md:45` through `bridge/gov-process-spec-precondition-2026-04-29-001.md:52`. Section 1 then defines a `**Specs:**` header-field rule with DB resolution and a `pending:NEW-SPEC-PROPOSED-IN-THIS-BRIDGE` exemption: `bridge/gov-process-spec-precondition-2026-04-29-001.md:74` through `bridge/gov-process-spec-precondition-2026-04-29-001.md:90`.

Section 2 reverses that design and says no new enforcement code will be written; instead it will copy and register the existing `bridge-compliance-gate.py`, which checks for a `Specification Links` heading, not a `**Specs:**` field or DB-resolving pre-commit check: `bridge/gov-process-spec-precondition-2026-04-29-001.md:94` through `bridge/gov-process-spec-precondition-2026-04-29-001.md:118`. The actual template confirms the heading/token behavior: `groundtruth-kb/templates/hooks/bridge-compliance-gate.py:26` through `groundtruth-kb/templates/hooks/bridge-compliance-gate.py:35`, `groundtruth-kb/templates/hooks/bridge-compliance-gate.py:221` through `groundtruth-kb/templates/hooks/bridge-compliance-gate.py:237`.

**Risk / impact:** Prime cannot implement this deterministically. Implementing the `Specs:` contract would be new tooling; implementing the activation contract would not satisfy the proposed GOV text.

**Required revision:** Pick one interim contract. Recommended: make this bridge only activate the existing `Specification Links` hook, and defer `**Specs:**`, DB resolution, pending-token rules, and pre-commit semantics to the comprehensive architecture bridge unless they are implemented here.

### F2 - "Must not be committed/submitted" is not satisfied by the proposed activation

**Severity:** High

**Evidence:** The rule statement requires non-compliant bridge proposals to be impossible to commit and says a pre-commit hook must fail closed: `bridge/gov-process-spec-precondition-2026-04-29-001.md:76`. The proposed actual mechanism is a Claude `PreToolUse` hook for `Write` and `Edit`: `bridge/gov-process-spec-precondition-2026-04-29-001.md:107` through `bridge/gov-process-spec-precondition-2026-04-29-001.md:118`. The hook itself exits unless the payload tool is `Write` or `Edit`: `groundtruth-kb/templates/hooks/bridge-compliance-gate.py:24` through `groundtruth-kb/templates/hooks/bridge-compliance-gate.py:25`, `groundtruth-kb/templates/hooks/bridge-compliance-gate.py:212` through `groundtruth-kb/templates/hooks/bridge-compliance-gate.py:237`.

**Risk / impact:** A `PreToolUse` hook is useful but it is not a commit gate and does not cover all edit paths, including Codex `apply_patch`, shell writes, external editors, or direct git commits. The owner directive "must NOT be possible to submit" remains overstated unless the proposal either adds an actual commit/CI gate or explicitly narrows the claim to Claude Write/Edit-time blocking.

**Required revision:** Either add a real pre-commit/CI/check command surface with tests, or revise the GOV statement and acceptance criteria to say this is a partial write/edit-time guard with known bypasses and defense-in-depth from bridge review.

### F3 - Test plan names three different test surfaces

**Severity:** Medium

**Evidence:** The top mapping names `tests/scripts/test_check_bridge_spec_linkage.py` and `tests/hooks/test_bridge_proposal_spec_linkage_gate.py`: `bridge/gov-process-spec-precondition-2026-04-29-001.md:23` through `bridge/gov-process-spec-precondition-2026-04-29-001.md:25`. Section 2.3 names `tests/hooks/test_bridge_compliance_gate_active.py`: `bridge/gov-process-spec-precondition-2026-04-29-001.md:127` through `bridge/gov-process-spec-precondition-2026-04-29-001.md:138`. The existing framework tests live under `groundtruth-kb/tests/test_governance_hooks.py` and already cover the template hook behavior; the GT-KB workspace currently has no active `.claude/hooks/bridge-compliance-gate.py` file.

**Risk / impact:** Verification will either duplicate framework tests, miss workspace activation, or test a script that the proposal no longer intends to create.

**Required revision:** Define one test set. For activation-only, add a GT-KB workspace activation test that checks `.claude/hooks/bridge-compliance-gate.py` exists, matches the template or has a documented divergence, `.claude/settings.json` registers it, and a synthetic hook payload blocks a non-compliant bridge write.

### F4 - Grandfathering examples use the wrong field name

**Severity:** Medium

**Evidence:** Section 5 says several in-flight bridges "have `Specs:` field; would pass": `bridge/gov-process-spec-precondition-2026-04-29-001.md:182` through `bridge/gov-process-spec-precondition-2026-04-29-001.md:189`. The reviewed bridge itself has `## Specification Links`, not a `**Specs:**` field: `bridge/gov-process-spec-precondition-2026-04-29-001.md:8`. The companion smart-poller bridge also has `## Specification Links`: `bridge/spec-smart-poller-auto-trigger-2026-04-29-001.md:8`.

**Risk / impact:** The migration boundary is currently based on a field that the active proposal set does not use. This will produce false claims about what would pass after activation.

**Required revision:** Rework grandfathering around the chosen contract. If using existing hook activation, say future NEW/REVISED bridge writes must include `## Specification Links`; do not claim `Specs:` compliance unless that parser is implemented.

## Positive Evidence

- The existing framework hook behavior is tested: `python -m pytest groundtruth-kb/tests/test_governance_hooks.py -q --tb=short` -> 56 passed.
- The framework helper already rejects missing or placeholder `Specification Links`: `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py:132` through `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py:144`.
- The GT-KB workspace really does appear to lack active hook activation today: `.claude/settings.json:5` through `.claude/settings.json:15` registers only `formal-artifact-approval-gate.py`, and `.claude/hooks/bridge-compliance-gate.py` is absent.

## Decision Needed From Owner

None. This is a revision task for Prime Builder.

