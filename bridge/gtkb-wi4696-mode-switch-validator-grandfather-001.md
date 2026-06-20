NEW

# Grandfather legacy bridge files in the mode-switch bridge-artifact validator (fast-lane defect fix)

bridge_kind: prime_proposal
Document: gtkb-wi4696-mode-switch-validator-grandfather
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-20 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 63d5063e-7f17-46be-9b91-d41960410cbe
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4696

target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "platform_tests/groundtruth_kb/test_mode_switch_validation.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`validate_bridge_artifact` in `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py` is the bridge-axis preflight for the role/topology-switch transaction (`SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` AC#2). It scans every numbered `bridge/*.md` file and **hard-fails the whole transaction** if any file's first non-blank line is not a canonical status token. Roughly 450 legacy bridge files pre-date the Body Status-Token Rule and have non-canonical first lines (e.g., `Document:` or a markdown title). Per `.claude/rules/file-bridge-protocol.md` § "Body Status-Token Rule", those files are explicitly **grandfathered**: "Files that already exist on disk with a non-canonical first line are grandfathered, so the rule never retroactively breaks historical bridge files." The Write-time `bridge-compliance-gate` is the enforcement point and only fires on new versioned `Write`s.

This mode-switch validator does **not** honor the grandfather clause, so it fails on the legacy corpus and blocks **both** role-switch CLIs (`gt mode set-role` and `gt harness set-role`). The defect makes every role switch impossible while legacy files exist — a latent platform defect surfaced 2026-06-20 while bootstrapping the release-gating `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH` (the cheap Loyal Opposition reviewer pool was circuit-broken on governance-grade proposals, and reassigning a capable harness to LO was blocked by this validator).

**Fix.** Align `validate_bridge_artifact` with the documented grandfather clause: a non-canonical first line (whether it yields no recognizable token OR an unknown token) is a grandfathered legacy condition and MUST NOT fail the transaction. The Write-time gate is the enforcement point for new files. The validator's fatal floor becomes bridge-corpus structural coherence — (1) bridge directory exists, (2) it contains numbered bridge files, (3) all are readable — which preserves the SPEC's "validate authoritative bridge artifacts before durable write" intent. The status-token scan is retained as non-fatal observability (it counts compliant vs. grandfathered-legacy files) rather than a hard gate.

This is a `GOV-RELIABILITY-FAST-LANE-001`-eligible fix: origin **defect**; introduces no new public API, CLI surface, or behavior beyond removing the defect; requires no new or revised requirement (it conforms the validator to the EXISTING grandfather clause); single-concern, ~1 source file + 1 test file, well under the ~3-file / ~150-line guide. It is created under `PROJECT-GTKB-RELIABILITY-FIXES` and covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — this fix asserts and meets all four fast-lane eligibility criteria (defect origin; no new API/behavior; no new/revised requirement; small single-concern); home project + standing PAUTH per its mechanism clause.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the bridge protocol whose Body Status-Token Rule (in `file-bridge-protocol.md`) defines the grandfather clause this fix conforms the validator to; also governs this proposal's own bridge filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every governing spec.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the Project Authorization / Project / Work Item header triple is present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps the fix to executed pytest evidence; the implementation report will carry observed results.
- `GOV-STANDING-BACKLOG-001` — WI-4696 is a MemBase work_items backlog item under the cited project + active standing PAUTH.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the defect and its fix are preserved as durable WI + bridge + test artifacts, not chat-only context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the fix is captured as traceable MemBase/bridge artifacts with a regression test.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — WI-4696 records the defect's lifecycle (captured -> fast-lane -> verified).

## Prior Deliberations

- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — the owner decision that landed the Body Status-Token Rule (`GTKB-GOV-PROPOSAL-STANDARDS` Slice 1), whose grandfather clause this fix conforms the mode-switch validator to. This proposal does not change the rule; it makes a second validator honor the rule's existing grandfather provision.
- _No prior deliberations on the mode-switch bridge-artifact validator's grandfather behavior specifically; this is the first time a role switch has been attempted against the full legacy corpus, which is what surfaced the defect._

## Owner Decisions / Input

- AskUserQuestion (S 2026-06-20, this session): owner selected **"Fix validator, then reassign A"** when shown that both role-switch CLIs were blocked by this validator defect, then **"Start Codex LO; I bootstrap headless"** authorizing this validator-fix proposal as the bootstrap step. The fix is additionally pre-authorized for implementation by the standing fast-lane authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`. No formal-artifact or protected-narrative approval packet is required (the change is to source + test only; `kb_mutation_in_scope: false`).

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement is `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` AC#2 (validate authoritative bridge artifacts before durable write) read together with the `file-bridge-protocol.md` Body Status-Token Rule grandfather clause. The fix conforms the validator to those existing requirements; no new or revised requirement is needed (fast-lane criterion #3).

## Specification-Derived Verification Plan (spec-to-test mapping)

This is the specification-derived verification spec-to-test mapping.

| Linked spec / requirement | Verification check (pytest / command) | Expected result |
|---|---|---|
| `file-bridge-protocol.md` grandfather clause -> validator honors it | New case in `platform_tests/groundtruth_kb/test_mode_switch_validation.py`: build a temp `bridge/` with a legacy `*-001.md` whose first line is non-canonical (`Document: x`) PLUS a canonical `*-002.md` (`NEW`); assert `validate_bridge_artifact(root).is_valid is True` | PASS (grandfathered legacy file does not fail) |
| `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` AC#2 fatal floor retained | Cases asserting `is_valid is False` for: missing `bridge/` dir; `bridge/` with no numbered files; an unreadable numbered file | PASS (fatal coherence checks retained) |
| End-to-end unblock (post-VERIFIED, reported as evidence) | `GTKB_HARNESS_NAME=claude python -m groundtruth_kb harness set-role --harness A --role loyal-opposition` succeeds against the current corpus | role switch applies (no bridge-artifact failure) |
| Regression suite | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_mode_switch_validation.py -q --no-header` | all pass |
| Lint/format gates | `ruff check` + `ruff format --check` on the two changed files | clean |

## Risk / Rollback

- **Risk: weakening the mode-switch bridge validation.** Mitigated by retaining the structural fatal floor (dir exists, has numbered files, readable) and by the fact that the Write-time `bridge-compliance-gate` already hard-blocks missing/bad status tokens on every new governed bridge write — so new malformed files cannot enter via the governed path regardless. The mode-switch validator's token gate provided no incremental safety for new files and actively blocked on historical files.
- **Risk: a genuinely-corrupt current bridge file slips past.** Low: corruption of the leading line of a current actionable file would still be observable (the non-fatal count surfaces it), and the Write gate is the enforcement point. Tightening to "validate only current/actionable-thread files" is a possible future enhancement, intentionally out of this single-concern fast-lane scope.
- **Rollback:** single-commit revert restores the prior validator. No runtime/data migration; the change is pure validation logic + a test.

## Bridge Filing

Filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4696-mode-switch-validator-grandfather`; append-only. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — a defect repair to validator logic (plus its regression test); no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.*
