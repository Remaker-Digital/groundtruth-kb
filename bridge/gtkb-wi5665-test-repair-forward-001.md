NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# WI-5665 cross-harness bridge-boundary test repair-forward

bridge_kind: prime_proposal
Document: gtkb-wi5665-test-repair-forward
Version: 001
Date: 2026-07-29 UTC
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5665
Related Work Items: WI-5640, WI-5667
target_paths: ["platform_tests/scripts/test_cross_harness_protocol_parity.py"]
observed_paths: ["groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/test_upgrade_skills.py", "platform_tests/scripts/test_harness_skill_effectiveness.py", "platform_tests/scripts/test_gitattributes_lf_policy.py", "scripts/harness_skill_effectiveness.py"]
implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This proposal performs no MemBase mutation.

## Claim

Create a fresh, one-test repair-forward controller for the currently executable
WI-5665 cross-harness boundary failure. The original controller is mechanically
quarantined because version 007 declares decorated metadata
`Version: 007 (NEW; implementation blocker report)`, and the authoritative
lifecycle resolver fails with `WRONG_BRIDGE_VERSION_METADATA`. No append to that
chain can provide safe implementation authority.

The sole mutation changes four retired bridge-skill references in the clean
cross-harness protocol test to their live `gtkb-bridge` projections. The two
already-landed broad-commit test paths remain read-only evidence. The
gitattributes false-green and harness-effectiveness failures remain separately
blocked on WI-5667 and WI-5640 respectively and are not silently accepted.

## Requirement Sufficiency

Existing requirements sufficient. WI-5665 defines the test-recovery objective;
the active bounded sweep PAUTH covers this work item and the test mutation
class; `DELIB-202667193` authorizes independently reviewed bounded slices; and
`DELIB-202667194` requires exact current-byte isolation. No new or revised
requirement is needed for the four literal replacements in this proposal.

## Defect / Reproduction

Current preimage:

- `platform_tests/scripts/test_cross_harness_protocol_parity.py` — HEAD blob
  `d5d2a727216b56935726e3c5127b3fd4653d5772`, clean in the worktree.

The exact selector currently fails once:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_protocol_parity.py::test_dispatcher_status_rules_match_prime_and_lo_bridge_boundaries -q --tb=short
```

Observed result: 1 failed. The first read attempts the nonexistent
`.claude/skills/bridge/SKILL.md` and raises `FileNotFoundError`. The same tuple
also contains retired Codex, Agent, and API-harness bridge paths.

Allowed replacements are exactly:

| Old literal | Required literal |
| --- | --- |
| `.claude/skills/bridge/SKILL.md` | `.claude/skills/gtkb-bridge/SKILL.md` |
| `.codex/skills/bridge/SKILL.md` | `.codex/skills/gtkb-bridge/SKILL.md` |
| `.agent/skills/bridge/SKILL.md` | `.agent/skills/gtkb-bridge/SKILL.md` |
| `.api-harness/skills/bridge/SKILL.md` | `.api-harness/skills/gtkb-bridge/SKILL.md` |

All four required paths currently exist. Any preimage mismatch or additional
diff is a stop condition requiring fresh review.

## In-Root Placement Evidence

The sole target is inside `E:\GT-KB` and is a platform test, not adopter or
external-application scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations

- `DELIB-202667193` - owner-authorized skill-rename sweep with independent review gates for each bounded slice.
- `DELIB-202667194` - govern existing partially landed work, isolate exact skill-rename bytes, and do not absorb WI-5640 changes.
- `bridge/gtkb-wi5665-skill-rename-test-recovery-008.md` - establishes the prior clean-baseline dependency but belongs to a now mechanically quarantined chain.
- `bridge/gtkb-wi5665-skill-rename-test-recovery-005.md` - supplies the earlier five-test inventory; this proposal narrows only the currently executable cross-harness defect.

No prior decision authorizes appending through malformed metadata or treating
blocked false-greens as complete.

## Owner Decisions / Input

- `DELIB-202667193` and `DELIB-202667194` authorize bounded per-slice recovery
  and current-byte isolation.
- No new owner decision is required for this one-test repair-forward.

## Governed Thread And Dependency Disposition

1. `gtkb-wi5665-test-repair-forward` is the only implementation controller for
   this one-test cross-harness slice.
2. `gtkb-wi5665-skill-rename-test-recovery` is read-only quarantined evidence;
   no claim, append, packet, implementation, or terminal verdict may derive
   authority from its malformed v007 metadata.
3. `groundtruth-kb/tests/test_managed_registry.py` and
   `groundtruth-kb/tests/test_upgrade_skills.py` are clean current evidence of
   owner broad commit `db07f9dc...`; their bytes are not verified or attributed
   by this slice.
4. `platform_tests/scripts/test_harness_skill_effectiveness.py` remains deferred
   until WI-5640 repairs `scripts/harness_skill_effectiveness.py` to read the
   authoritative unprefixed
   `config/agent-control/harness-capability-registry.toml`. The test fixture
   must not be changed to the incorrect prefixed filename to manufacture a pass.
5. `platform_tests/scripts/test_gitattributes_lf_policy.py` remains deferred
   until the WI-5667 retain/reverse decision resolves whether both old and
   canonical template/scaffold roots are intentional LF-policy subjects.

## Proposed Scope

1. After GO, acquire an exact claim and schema-v3 implementation-start packet
   for the one target.
2. Recheck the pinned HEAD blob and clean status.
3. Apply only the four literal replacements in the named tuple.
4. Run the exact selector, residual scan, Ruff check/format, and scoped
   whitespace/diff checks.
5. Commit only the one test path, file a strict implementation report, and
   obtain an independent terminal verdict with commit-finalization evidence.

## Cross-Harness Disposition

- Claude: replace the retired bridge SKILL path with `.claude/skills/gtkb-bridge/SKILL.md`.
- Codex: replace the retired bridge SKILL path with `.codex/skills/gtkb-bridge/SKILL.md`.
- Agent/Antigravity: replace the retired bridge SKILL path with `.agent/skills/gtkb-bridge/SKILL.md`.
- API harness family: replace the retired bridge SKILL path with `.api-harness/skills/gtkb-bridge/SKILL.md`.
- Goose, Ollama, OpenRouter, Cursor, and Alibaba Cloud Studio have no literal in this exact selector and receive a no-change disposition for this slice.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Expected Result |
| --- | --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Full fresh controller chain plus claim/start/report sequence | planned | No implementation authority derives from the malformed predecessor chain. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Active PAUTH inspection at proposal, start, and finalization time | executed/planned | The current authorization covers WI-5665, the test mutation class, and the exact target. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Schema-v3 implementation-start activation after GO | planned | Fresh evaluation returns `allowed=true` for the exact target before mutation. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Candidate and live applicability preflights | executed/planned | Active PAUTH, project, WI, and exact one-target JSON linkage. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate applicability preflight | executed | Every required/advisory governing specification is linked. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Exact cross-harness selector | executed/planned | Baseline 1 failed; post-change 1 passed, with actual result in the report. |
| `GOV-WORK-TREE-HYGIENE-001` | Pinned preimage, exact diff, Ruff, format, `git diff --check` | planned | Exactly one authorized test path changes and is committed. |
| `GOV-RELIABILITY-FAST-LANE-001` | Diff-stat and focused-selector evidence | planned | Four literal replacements in one test; no new capability surface. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | In-root placement and changed-path inspection | executed/planned | The only target remains under `E:\GT-KB\platform_tests`; no adopter or external path changes. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Selector reads current bridge protocol skill text | planned | `NO-ACTION` parity assertion reads live canonical skill paths. |
| `ADR-CROSS-HARNESS-PARITY-001` | Existence checks and exact selector | executed/planned | Claude, Codex, Agent, and API harness projections all resolve and share the boundary assertion. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Residual scan in the target tuple | planned | Zero retired `/skills/bridge/SKILL.md` literals remain in the tuple. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Durable bridge chain and executable regression | planned | Defect, evidence, implementation, and verdict remain linked artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | GO/claim/start/report/verdict ordering | planned | Every transition occurs after its required trigger. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Quarantine and dependency-disposition inspection | executed | Malformed history and blocked remaining slices are preserved without laundering them. |
| `GOV-STANDING-BACKLOG-001` | WI-5665/project linkage inspection | executed | Remaining false-green inventory stays visible on the open work item. |

## Acceptance Criteria

- The four exact retired bridge paths are replaced with live `gtkb-bridge`
  paths and the exact selector passes.
- The target has no other diff and is the only source/test path in the commit.
- The original malformed chain remains read-only and cannot supply authority.
- The two broad-commit tests remain read-only evidence; the gitattributes and
  harness-effectiveness slices remain explicitly open under their named
  dependencies.
- Independent LO supplies the terminal verdict and immutable finalization
  evidence; no push is authorized.

## Risks / Rollback

The main risk is treating a one-test repair as completion of all WI-5665
false-greens. The dependency disposition and open-WI acceptance prevent that.
Rollback is a governed revert of only the eventual one-test commit; bridge
history and observed paths remain unchanged.

## Files Expected To Change

- `platform_tests/scripts/test_cross_harness_protocol_parity.py`

## Recommended Commit Type

`test:`

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
