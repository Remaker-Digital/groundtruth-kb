NEW

# WI-5223 - Dispatcher eligibility precedence implementation report

bridge_kind: implementation_report
Document: gtkb-wi5223-dispatch-eligibility-precedence
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5223-dispatch-eligibility-precedence-002.md
Approved proposal: bridge/gtkb-wi5223-dispatch-eligibility-precedence-001.md
Author: Prime Builder (Codex, harness A)
Date: 2026-07-13 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; hunk-scoped detached verification

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5223-ELIGIBILITY-PRECEDENCE-20260713
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5223
Test: TEST-11377
Implementation Authorization Packet: sha256:5f9d44510d262f6d5bf1d41faaa6b174c8de038761bd952a56aab48fc53cbfd3
target_paths: ["groundtruth-kb/src/groundtruth_kb/harness_projection.py", "platform_tests/groundtruth_kb/test_harness_projection.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_eligibility_precedence.py"]
Recommended commit type: fix:

## Implementation Claim

Canonical dispatcher eligibility now remains authoritative when
`invocation_surfaces.dispatch.can_receive_dispatch` is explicit. The
`headless.can_receive_dispatch` declaration remains available only as a
compatibility fallback when no top-level, dispatch, or dispatchability value is
present. The `can_fire_events` path remains neutralized and unchanged.

The committed baseline already carried the correct source order. A foreign
uncommitted hunk had temporarily moved `headless` to the front for receive
resolution. This implementation removes that conflicting precedence and adds
an explicit fallback comment, leaving a two-line source diff against
post-WI-5220 `HEAD 89198140`. Two new approved test files make the behavior
durable:

- a pure projection test covers canonical false over stale headless true and
  the headless-only fallback case;
- a real CLI transaction test disables and re-enables Ollama D through
  `gt bridge dispatch config set-eligibility`, proves append-only versions 2
  and 3, confirms projected eligibility follows the canonical dispatch value,
  and confirms headless capability and event metadata remain unchanged.

No routing rule, role, lifecycle status, launch argv, timer, allowance, lease,
runtime JSON, or unrelated dirty file changed.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

- `DELIB-202666173` authorizes completing genuine fleet proof and correcting
  every blocking dispatcher defect found during that work.
- The owner identified D and H viability as the immediate priority. This fix
  makes canonical disable/re-enable controls truthful for those reviewers.
- No new owner decision is required.

## Prior Deliberations

- `DELIB-202666173` - fleet proof and blocking-defect correction authorization.
- `INTAKE-f8bc08a3` - dispatcher CLI is the primary mutating operator surface.
- `INTAKE-da01f846` - installed lifecycle/headless capability and current
  dispatch eligibility are distinct.
- `bridge/gtkb-wi5223-dispatch-eligibility-precedence-001.md` - approved proposal.
- `bridge/gtkb-wi5223-dispatch-eligibility-precedence-002.md` - genuine Alibaba H
  GO and binding conditions.

## Specification-Derived Verification Plan

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | New pure projection and CLI transaction tests | yes | PASS |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | CLI disable/re-enable through `set-eligibility` | yes | PASS; projected false then true |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Assert headless true survives while dispatch false controls projection | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | WI, TEST, PAUTH, H GO, claim 31291, packet, report | yes | PASS |
| `GOV-WORK-TREE-HYGIENE-001` | Disposable index seeded from HEAD plus three exact hunk patches | yes | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Packet hash and exact three-path target set | yes | PASS |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Source/test edits began after GO and packet | yes | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Carried-forward specification links | yes | PASS |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH, project, WI, TEST, target paths above | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused, existing reader/config, committed projection, Ruff, patch checks | yes | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Reproducible defect captured as WI-5223/TEST-11377 | yes | PASS |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Exact patch/blob/test evidence remains linked | yes | PASS |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Live canonical-control failure triggered governed correction | yes | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All implementation and evidence under `E:/GT-KB` | yes | PASS |

## Commands Run And Observed Results

Live worktree, exercising the effective current CLI stack:

- `python -m pytest platform_tests/groundtruth_kb/test_harness_projection.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_eligibility_precedence.py -q --tb=short`
  - PASS, 3 passed.
- `python -m pytest platform_tests/groundtruth_kb/cli/test_bridge_dispatch_config_transactions_cli.py -q --tb=short`
  - PASS, 5 passed.
- `python -m pytest platform_tests/scripts/test_harness_projection_reader.py -q --tb=short`
  - PASS, 8 passed.
- `python -m ruff check <three approved paths>`
  - PASS, all checks passed.
- `python -m ruff format --check <three approved paths>`
  - PASS, 3 files already formatted.

Detached post-WI-5220 `HEAD 89198140` plus only the three WI-5223 hunk
patches:

- new tests, committed `groundtruth-kb/tests/test_harness_projection.py`, and
  `platform_tests/scripts/test_harness_projection_reader.py`
  - PASS, 34 passed together.
- `git apply --cached --check --whitespace=error-all` for all three patches
  - PASS.
- `git diff --cached --check`
  - PASS.

The broader clean `test_bridge_dispatch_config_transactions_cli.py` contains a
pre-existing baseline fixture that does not seed the MemBase harness registry
and therefore fails one transaction at `HEAD`; the live corrected fixture suite
passes 5/5. Neither that existing test file nor the CLI source is an approved
WI-5223 path, and neither is included here.

## Hunk-Scoped Review Evidence

Detached review root: `E:/GT-KB/.gtkb-state/wi5223-checkout2` at
`89198140`.

Exact reconstructed blobs:

- `groundtruth-kb/src/groundtruth_kb/harness_projection.py`:
  `e221aed0635d8dc845169ffc64d765463bd13992`
- `platform_tests/groundtruth_kb/test_harness_projection.py`:
  `f7c5f9da9eab685ce164016e9718bd7672fb6409`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_eligibility_precedence.py`:
  `57a3f86b8492178130047892ec13f55c355775be`

Binary-safe patch inputs:

- `.gtkb-state/bridge-hunk-patches/wi5223-groundtruth-kb__src__groundtruth_kb__harness_projection.py.patch`
  - SHA-256 `631231d9cfc93291a7a976b59d5f7c1ae7c9435bdccc66f8520bbf7f1bda2e58`
- `.gtkb-state/bridge-hunk-patches/wi5223-platform_tests__groundtruth_kb__test_harness_projection.py.patch`
  - SHA-256 `61661581853aefd7b2d58afc527376a9425b9c2b06c315034aa8a8cd931a4e1e`
- `.gtkb-state/bridge-hunk-patches/wi5223-platform_tests__groundtruth_kb__cli__test_bridge_dispatch_eligibility_precedence.py.patch`
  - SHA-256 `63cf2b960d3fc0a72667bdaebfc47472c244c86e99028d969ce497533828c440`

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/harness_projection.py`
- `platform_tests/groundtruth_kb/test_harness_projection.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_eligibility_precedence.py`

The foreign uncommitted test
`groundtruth-kb/tests/test_harness_projection.py::test_headless_receive_declaration_overrides_retired_dispatch_false`
asserts the defective precedence and remains untouched, per the GO-scoped target
set and dirty-worktree preservation rule. The committed version of that module
passes 23/23 against this patch.

## Loyal Opposition Verification Request

Review the detached root or reconstruct the three exact blobs from the named
patches. Confirm canonical false wins over stale headless true, headless remains
a fallback when canonical eligibility is absent, `can_fire_events` remains
unchanged, disable/re-enable appends versions and reports effective state, and
only these three paths enter the commit. Use WI-5112 hunk-scoped finalization if
the shared worktree remains dirty.

## Risk And Rollback

Risk is limited to eligibility projection precedence and its tests. A focused
revert restores the prior projection comment and removes the two new tests. The
canonical transaction history remains append-only and no runtime state is
edited directly.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
