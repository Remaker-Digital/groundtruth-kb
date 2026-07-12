NEW

# WI-5200..5202 - Corrected implementation report: isolated H parity fixture

bridge_kind: implementation_report
Document: gtkb-wi5200-5202-generous-harness-repair-narrow
Version: 007 (NEW; post-implementation report)
Author: Prime Builder (Codex, harness A)
Date: 2026-07-11 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f522a-849d-7d43-8c60-0afc829438a6
author_model: gpt-5.5
author_model_version: Codex desktop
author_model_configuration: xhigh reasoning; interactive Prime Builder; governed NO-GO remediation

Responds to GO: bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-006.md
Approved proposal: bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-005.md
Prior report: bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-003.md
Prior NO-GO: bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-004.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5200-5202-HARNESS-REPAIR-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5200
Related Work Items: WI-5201, WI-5202
Recommended commit type: fix(harness):

target_paths: [".api-harness/routing.toml", "config/agent-control/harness-capability-registry.toml", "scripts/cloud_harness_base.py", "scripts/alibaba_cloud_studio_harness.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "scripts/dispatcher_runtime.py", "scripts/harness_parity_phase2.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_lo_harness_turn_budget.py", "platform_tests/scripts/test_harness_parity_phase2.py", "platform_tests/scripts/test_check_harness_parity.py"]

implementation_scope: one self-contained parity-test correction; affirmed runtime/config implementation carried forward unchanged
requires_verification: true
kb_mutation_in_scope: false

---

## Implementation Claim

The sole delta approved at `-006` is complete.
`test_alibaba_managed_skill_adoption_review_is_truthfully_unsupported` now
creates a minimal H harness projection and capability registry under
`tmp_path`, derives `KNOWN_HARNESSES` from that fixture, and runs the production
parity checker against the fixture root. It still requires the H
`skill.managed-skill-adoption-review` row to be exactly `UNSUPPORTED` with the
provider-harness reason. It no longer depends on WI-5199's uncommitted generated
registry.

The blank-final recovery, D/F/H routing consumption, dispatcher stale-flag
stripping, generous 29,400-second outer profiles, and Phase 2 H truth affirmed
by Loyal Opposition at `-004` are unchanged. No DB, generated harness registry,
credential, deployment, or foreign skill artifact was modified or staged.

## Implementation Gate Evidence

- GO implementation claim row: `31206`, holder session
  `019f522a-849d-7d43-8c60-0afc829438a6`.
- Implementation-start packet:
  `sha256:e40c929c650362b58172d1e9b7fbcb17c407c182a4996d468383f79f4c508989`.
- Operative GO: `bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-006.md`.
- Exact PAUTH:
  `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5200-5202-HARNESS-REPAIR-20260711`.

## NO-GO Findings Resolved

### FINDING-1 - clean-HEAD H normalization failure

Resolved by the approved fixture rewrite. The exact staged patch applied to a
detached clean-HEAD worktree no longer raises `ValueError: unsupported harness:
alibaba-cloud-studio`. The H test passes as part of both the 376-test isolated
WI-owned run and the 378-test commingled run.

### FINDING-2 - foreign skill-governance-lifecycle baseline

Disclosed and proven unchanged. On untouched detached HEAD `4442943c`, the two
named repository-registry tests fail because the native
`.claude/skills/skill-governance-lifecycle/SKILL.md` is absent while registry
declarations exist. On detached HEAD plus the exact 16-path WI patch, those same
two tests fail for the same capability and all other 376 tests pass. The main
commingled checkout passes them only because it contains the untracked foreign
skill. This repair neither masks nor absorbs that separate lifecycle.

## Specification Links

- `ADR-CLOUD-HARNESS-TEMPLATE-001`
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

- `DELIB-20260711-WI5200-5202-HARNESS-REPAIR-AUTHORIZATION` authorizes the
  repair, truthful parity evidence, generous initial envelopes, independent
  verification, and genuine H reproof.
- Mike's generous-envelope direction remains controlling; no thresholds were
  reduced.
- No new owner decision was required for the independently requested fixture
  correction.

## Prior Deliberations

- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES`
- `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS`
- `DELIB-20260711-WI5200-5202-HARNESS-REPAIR-AUTHORIZATION`
- `DELIB-202666172`
- `bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-004.md`
- `bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-005.md`
- `bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-006.md`

## Specification-Derived Verification

| Governing surface | Executed evidence | Result |
| --- | --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Revised H fixture test alone and in detached exact-patch suite | H normalizes and reports truthful `UNSUPPORTED`; pass. |
| Shared cloud/Alibaba/Ollama/dispatcher specs | Main 378-test scoped suite | `378 passed`; no runtime/config regression. |
| Mandatory isolated verification | Detached HEAD plus exact 16-path patch, excluding two separately proven foreign baseline tests | `376 passed, 2 deselected`. |
| Foreign-baseline disclosure | Untouched detached HEAD, two named parity tests | Both fail for `skill.skill-governance-lifecycle`, proving pre-existence. |
| Exact-patch full census | Detached HEAD plus exact patch, all 378 tests | `376 passed, 2 failed`; failures are the same pure-HEAD foreign baseline only. |
| Static quality | Ruff check and format check on the corrected test; prior 14-file checks carried forward | Clean. |

## Commands Run And Observed Results

1. Main checkout focused H fixture test: `1 passed`.
2. Main checkout eight-module scoped suite: `378 passed in 38.28s`.
3. Main checkout Ruff on corrected test: `All checks passed`; `1 file already formatted`.
4. Detached worktree `E:\GT-KB\.gtkb-state\wi5200-narrow-rehearsal-prime`,
   HEAD `4442943c` plus `git diff --cached -- <16 targets> | git apply`:
   full suite `376 passed, 2 failed in 32.53s`; only the two disclosed foreign
   registry tests failed.
5. Detached untouched baseline worktree
   `E:\GT-KB\.gtkb-state\wi5200-baseline-prime`, HEAD `4442943c`:
   the same two named tests both failed for
   `skill.skill-governance-lifecycle` (`2 failed in 1.30s`). The first attempted
   baseline invocation was discarded because pytest reported the main root;
   the admissible rerun reported the detached baseline root shown here.
6. Detached exact-patch WI-owned suite, excluding only those two proven
   pure-HEAD failures: `376 passed, 2 deselected in 31.01s`.
7. Both temporary worktree directories were verified under
   `E:\GT-KB\.gtkb-state\`, removed through `git worktree remove --force`, and
   confirmed absent. A later broad `git worktree prune` encountered permission
   errors on unrelated pre-existing administrative entries; it did not affect
   the two removed rehearsal worktrees or this patch.

## Files Changed

- `.api-harness/routing.toml`
- `config/agent-control/harness-capability-registry.toml`
- `scripts/cloud_harness_base.py`
- `scripts/alibaba_cloud_studio_harness.py`
- `scripts/ollama_harness.py`
- `scripts/openrouter_harness.py`
- `scripts/dispatcher_runtime.py`
- `scripts/harness_parity_phase2.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_lo_harness_turn_budget.py`
- `platform_tests/scripts/test_harness_parity_phase2.py`
- `platform_tests/scripts/test_check_harness_parity.py`

The exact staged implementation patch remains these 16 approved paths: 545
insertions and 84 deletions. Only D/F/H routing-table hunks and H's capability
block are staged from the two commingled config files; unrelated formatting,
Goose routing, capability hashes, generated registry state, and foreign skill
files remain excluded.

## Acceptance Criteria Status

- [x] Blank final responses recover without an empty assistant turn and retain
  fail-closed overall exhaustion.
- [x] D/F/H use 600 turns, 900-second operations, and 28,800-second sessions.
- [x] Active outer worker profiles are 29,400 seconds in the repaired runtime.
- [x] Dispatcher provider workers discard stale explicit runtime overrides.
- [x] H parity is truthful with zero release-blocking Phase 2 gap.
- [x] The H Phase 1 test passes from clean HEAD without WI-5199 registration.
- [x] The exact isolated WI-owned suite is green; two foreign failures are
  proven on untouched HEAD and separately disclosed.
- [x] Exactly 16 approved implementation paths are staged.
- [ ] Independent Loyal Opposition VERIFIED.
- [ ] Focused commit, daemon reload, genuine H WI-5199 reproof, and final
  B=true/H=false routing restoration.

## Risk And Rollback

The fixture test no longer provides a live-checkout integration assertion, but
it exercises the production schema and checker in isolation while WI-5199 owns
the live H registration and proof. Runtime risks and semantic fail-closed
controls remain as reported at `-003` and affirmed at `-004`. The focused staged
patch can be reverted as one commit; bridge records remain append-only.

## Loyal Opposition Asks

1. Recreate the detached exact-patch rehearsal or inspect the recorded roots and
   rerun the H fixture plus WI-owned suite.
2. Confirm the two residual failures reproduce on untouched HEAD and are not
   introduced or hidden by this WI.
3. Return VERIFIED only if the exact 16-path patch and isolation evidence satisfy
   `-006`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
