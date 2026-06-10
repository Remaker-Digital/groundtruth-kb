NEW

# Bridge-Proposal Lint: Flag `.git/hooks` Target Surface When `core.hooksPath` Differs (WI-3482)

bridge_kind: prime_proposal
Document: gtkb-git-hooks-path-mismatch-lint
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC
Implements: GOV-FILE-BRIDGE-AUTHORITY-001; DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001; WI-3482
Project Authorization: PAUTH-WI-3482-GIT-HOOKS-PATH-LINT-001
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3482
target_paths: ["scripts/bridge_proposal_pattern_lint.py", "platform_tests/scripts/test_bridge_proposal_pattern_lint.py"]
Recommended commit type: feat:
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 86d7f8a9-b8da-4284-b937-60eb056adda0
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

## Claim

This repository runs Git hooks from a non-default path: `git config --get core.hooksPath` returns `.githooks` (live value confirmed this session; the setting is documented in `.githooks/setup-hooks.sh:34`). Despite that, the default `.git/hooks/` directory still contains live-looking hook scripts — `.git/hooks/pre-commit`, `.git/hooks/pre-push`, `.git/hooks/commit-msg`, and several `post-*` hooks with recent mtimes. Because `core.hooksPath` overrides the default, **every one of those `.git/hooks/*` files is inert.** A bridge proposal that lists `.git/hooks/pre-commit` (or the historical staging path `scripts/guardrails/pre-commit`) in its `target_paths` and edits it would modify a directory Git never consults, producing a silently-broken governance integration plus workstation-local drift.

This is a recurring Prime-Builder hazard that has cost at least two Codex review rounds, both NO-GO'd on exactly this surface:

- `bridge/gtkb-ruff-format-pre-file-gate-002.md:169-192` — F1 (P1) "Proposed guardrail targets an inactive hook surface": "the proposal proposes to register at `.git/hooks/pre-commit`, but the live repository is configured to run hooks from `.githooks` … `git config --get core.hooksPath` returned `.githooks`."
- `bridge/gtkb-commit-scope-bundling-detection-001-prop-002.md:66-79` — F1 "Proposal targets `.git/hooks/pre-commit`, but this repository uses tracked `.githooks`": cites `target_paths` listing `.git/hooks/pre-commit` and the same `git config --get core.hooksPath` reproduction.

WI-3482 (`origin=defect`, `component=governance`, `project_name=GTKB-RELIABILITY-FIXES`) captures this class and names the candidate home explicitly: a `scripts/bridge_proposal_pattern_lint.py` extension OR a doctor check, with a deterministic detector ("read core.hooksPath, grep proposal for the inactive hook tokens").

The natural home is the existing bridge-proposal pattern linter at `scripts/bridge_proposal_pattern_lint.py` — a diagnostic-by-default tool (exits 0 unless `--strict`, per its module docstring lines 5-7 and `main()` at lines 224-229) that already emits structured `Finding` objects keyed by `pattern_id` (dataclass at lines 43-53) for recurring Codex feedback patterns. The doctor's `_check_hooks` (`groundtruth-kb/src/groundtruth_kb/project/doctor.py:325-360`) inspects only `.claude/hooks/*.py` presence and does **not** read `core.hooksPath` (confirmed: no `hooksPath`/`hooks_path` reference anywhere in `doctor.py`), so the doctor angle would be genuinely new behavior too; this proposal scopes the fix to the bridge-proposal lint, which is the point-of-use closest to the hazard (proposal drafting) and is named first in the WI candidate list.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 (v1, live) — the bridge-proposal lint is bridge-quality infrastructure; this proposal extends a bridge-drafting guard. `bridge/INDEX.md` remains canonical workflow state and is unchanged.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 (v1, live) — governs the machine-readable `target_paths`/`Project`/`Work Item` metadata block that this lint parses; the new check reads the proposal's `target_paths` lines, the same metadata surface this DCL makes mandatory.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 (v1, live) — the in-root placement and root-boundary decision; both target paths (`scripts/bridge_proposal_pattern_lint.py`, the new test) are in-root under `E:\GT-KB`, and the lint reasons about in-root hook paths (`.git/hooks` vs `.githooks`) without writing any out-of-root path. Clause-in-root is satisfied.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (v1, live) — this proposal cites every relevant governing specification; the lint reinforces correct proposal authoring at draft time.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (v1, live) — verification is derived from the linked specifications and executed against the implementation; the Spec-To-Test Mapping carries this forward, and the regression reproduces the two prior NO-GO cases.
- GOV-RELIABILITY-FAST-LANE-001 (v1, live) — cited for the honest eligibility assessment below; this proposal explicitly does NOT claim fast-lane (criterion 2 fails — it adds a new check), and is instead authorized via the dedicated PAUTH in the Authorization section.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (v1, live) — durable preservation of the proposal/deliberation/report chain (advisory).

## Authorization

This work is **not** reliability-fast-lane eligible — it adds a new lint detector (a new `Finding` `pattern_id` plus a new `git config core.hooksPath` read, and a new `--strict` gating effect), which is new behavior, so `GOV-RELIABILITY-FAST-LANE-001` criterion 2 ("no new public API/CLI/behavior beyond removing the defect") is not met. It was therefore routed to a dedicated standard project authorization rather than the standing fast-lane PAUTH.

That authorization is now granted: `PAUTH-WI-3482-GIT-HOOKS-PATH-LINT-001` (project `PROJECT-GTKB-RELIABILITY-FIXES`; owner decision `DELIB-2548`; owner-approved via AskUserQuestion in S381; `allowed_mutation_classes = ["source", "test_addition", "cli_extension"]`; forbids deploy / git_push_force / spec_deletion). The mutations map: the new detector in `scripts/bridge_proposal_pattern_lint.py` is `source` (the lint already exposes a `--strict` mode, so no new CLI surface is added — `cli_extension` is reserved but not exercised), and the regression test is `test_addition`. The authorization is additive to the bridge gate: implementation proceeds only after Loyal Opposition records `GO` and Prime Builder creates the implementation-start packet from that GO per `.claude/rules/codex-review-gate.md`.

## Prior Deliberations

- `bridge/gtkb-ruff-format-pre-file-gate-002.md` (Codex NO-GO, F1/P1 at lines 169-192) — first recorded Codex NO-GO on a proposal targeting the inactive `.git/hooks/pre-commit` surface; this is one of the two regression cases this lint must reproduce.
- `bridge/gtkb-commit-scope-bundling-detection-001-prop-002.md` (Codex NO-GO, F1 at lines 66-79) — second recorded NO-GO on the same hazard; the second regression case. `DELIB-COMMIT-SCOPE-BUNDLING-DETECTION-001-PROJECT-HOMING` (cited in that file at line 41) records that hook wiring there had to be split out and re-homed precisely because the `.git/hooks` target was wrong.
- `DELIB-2548` — the owner decision (S381 AskUserQuestion) that authorized WI-3482 (with the rest of the S381 batch) under `PROJECT-GTKB-RELIABILITY-FIXES`, operationalized as `PAUTH-WI-3482-GIT-HOOKS-PATH-LINT-001`.
- The reliability fast-lane (`GOV-RELIABILITY-FAST-LANE-001`, `PROJECT-GTKB-RELIABILITY-FIXES`, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`) is the standing authorization used by sibling reliability fixes such as `bridge/gtkb-cross-harness-trigger-import-repair-001.md`; this proposal deliberately does NOT use that standing authorization because the new-check work falls outside fast-lane criterion 2 — it uses the dedicated WI-specific PAUTH instead.

## Owner Decisions / Input

- 2026-06-01 (S381): via AskUserQuestion the owner approved authorizing WI-3482 for implementation (the new `git-hooks-path-mismatch` lint), recorded as owner decision `DELIB-2548` and operationalized as the dedicated project authorization `PAUTH-WI-3482-GIT-HOOKS-PATH-LINT-001` (project `PROJECT-GTKB-RELIABILITY-FIXES`; allowed mutation classes `source`, `test_addition`, `cli_extension`; forbidden deploy / git_push_force / spec_deletion).
- No further owner decision is required before GO. The authorization covers the new-check implementation scope; no formal-artifact-approval packet is required because this proposal creates no GOV/SPEC/PB/ADR/DCL artifact and edits no protected narrative path.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation. `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` already establishes the `target_paths` metadata surface the lint inspects, and `GOV-FILE-BRIDGE-AUTHORITY-001` already establishes the bridge-quality concern. The check operationalizes those existing requirements; it does not introduce a new requirement.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped addition of one detector pattern to one bridge-lint script plus its regression test file. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is not applicable. The single work item cited (WI-3482) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Scope

### IP-1: Add the `git-hooks-path-mismatch` detector to the bridge-proposal lint

Extend `scripts/bridge_proposal_pattern_lint.py` with a new detector that emits a `Finding(pattern_id="git-hooks-path-mismatch", ...)` when a bridge proposal plans to modify an inactive Git-hook surface:

1. **Resolve the active hook path deterministically.** Add a small helper that reads the live setting via `git config --get core.hooksPath` (run with `cwd=PROJECT_ROOT`, captured output, no shell). Normalize the result (strip, forward-slash). If the command fails or returns empty, the active path is the Git default `.git/hooks` and the detector is a no-op (no false positives when the repo uses the default path).
2. **Identify inactive-surface tokens in the proposal.** Scan the proposal text for references to the inactive default hook surface — the literal path tokens `.git/hooks/` and the historical staging path `scripts/guardrails/pre-commit` (both named verbatim in the WI-3482 acceptance summary). Detection prioritizes the `target_paths:` metadata line (the machine-readable surface governed by `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`) and also covers `Files Expected To Change` / prose references so a proposal cannot evade the check by mentioning the path only in body text.
3. **Fire only on genuine mismatch.** Emit the finding only when (active hook path != `.git/hooks`) AND the proposal references a `.git/hooks/` (or `scripts/guardrails/pre-commit`) token. The finding message names the live `core.hooksPath` value and directs the author to the active surface. The `hint` mirrors the remediation language Codex used in the two prior NO-GOs.
4. **Self-documentation guard.** The lint already skips lines that document lint rules (`_line_documents_lint_rule`, lines 76-77 / `RULE_DOCUMENTATION_RE`). The new detector reuses/extends that guard so a proposal *describing* this very check (as this proposal does) does not self-trigger. This is consistent with how the existing `bare-pytest` detector avoids flagging rule-documentation lines.

The detector keeps the lint's diagnostic-by-default contract: it adds findings to the existing list, and only `--strict` (existing flag, line 220) makes findings exit non-zero. No new CLI flag and no change to `main()`'s exit semantics are introduced beyond the new `Finding`.

### IP-2: Regression tests reproducing the two prior NO-GO cases

Create `platform_tests/scripts/test_bridge_proposal_pattern_lint.py` (no test file currently exists for this module). Tests import the module via the `platform_tests/scripts/conftest.py` REPO_ROOT-on-`sys.path` convention (lines 14-16) using `importlib.util`, matching the sibling `test_adr_dcl_clause_preflight.py`. Tests are hermetic: `core.hooksPath` is supplied through a monkeypatched/injected resolver (the helper from IP-1 is structured to accept an override or read from an injected callable) so no test mutates real Git config. Coverage:

1. **Positive — ruff-gate case:** proposal text with `target_paths: ["scripts/...", ".git/hooks/pre-commit"]` while active hook path is `.githooks` produces a `git-hooks-path-mismatch` finding (reproduces `gtkb-ruff-format-pre-file-gate-002` F1).
2. **Positive — commit-scope case:** proposal listing `.git/hooks/pre-commit` in `target_paths` and proposing to register at `.git/hooks/pre-commit` while active path is `.githooks` produces a finding (reproduces `gtkb-commit-scope-bundling-detection-001-prop-002` F1).
3. **Positive — legacy staging token:** proposal referencing `scripts/guardrails/pre-commit` while active path is `.githooks` produces a finding.
4. **Negative — default hook path:** same proposal text but active hook path resolves to empty/`.git/hooks` (repo uses the Git default) produces no finding (no false positive).
5. **Negative — correct surface:** proposal targeting `.githooks/pre-commit` while active path is `.githooks` produces no finding.
6. **Negative — self-documentation:** proposal text that merely describes the mismatch hazard (rule-documentation lines) produces no finding (guard holds).
7. **`--strict` behavior:** a positive case under `--strict` causes `main()` to return non-zero; the same case without `--strict` returns 0 (preserves the diagnostic-by-default contract).

## Out Of Scope

- A doctor check that reads `core.hooksPath` — `groundtruth-kb/src/groundtruth_kb/project/doctor.py:325 _check_hooks` does not read it today; adding a doctor surface is a separate (also non-fast-lane) follow-on if the owner wants startup-time visibility in addition to draft-time linting. This proposal scopes to the bridge-proposal lint (the WI's first-named candidate, closest to the hazard).
- Auto-fixing or rewriting `target_paths` — the lint flags and directs; it does not mutate proposals.
- Registering this lint as a blocking `bridge-compliance-gate` PreToolUse hook — the existing diagnostic/`--strict` model is preserved; promoting to a hard Write-time gate is a separate owner decision.
- Removing or relocating the stale inert files under `.git/hooks/` — those are local, untracked, regenerable Git artifacts; cleaning them is out of scope and unrelated to the lint.
- Any change to the hook scripts under `.githooks/` themselves.
- Any file outside `E:\GT-KB`. Both target paths are within the `E:\GT-KB` project root.

## Files Expected To Change

- `scripts/bridge_proposal_pattern_lint.py` — add the `git-hooks-path-mismatch` detector: a `core.hooksPath` resolver helper, the inactive-surface token scan, and a new `Finding` emission wired into `lint_text` (IP-1).
- `platform_tests/scripts/test_bridge_proposal_pattern_lint.py` — new regression test file reproducing the two prior NO-GO cases plus the negative and `--strict` cases (IP-2).

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 | Tests 1-2: a proposal whose `target_paths` metadata lists `.git/hooks/pre-commit` while `core.hooksPath=.githooks` produces a `git-hooks-path-mismatch` finding (reproduces both prior NO-GO cases on the governed metadata surface). |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Tests 3-5: the detector fires on the legacy `scripts/guardrails/pre-commit` staging token, and does NOT fire when the repo uses the default hook path or correctly targets `.githooks/pre-commit` (no false positives against the bridge-quality guard). |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Applicability + clause preflight confirm both target paths are in-root under `E:\GT-KB`; the lint writes no out-of-root path. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Test 6: rule-documentation lines (a proposal describing the hazard, like this one) do not self-trigger; the lint stays usable while authoring proposals that discuss the check. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Test 7 plus the post-implementation report carrying this mapping with executed command output (the `--strict` exit-code contract and observed results). |

Implementation verification will run:
- `python -m pytest platform_tests/scripts/test_bridge_proposal_pattern_lint.py -q --tb=short`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-git-hooks-path-mismatch-lint`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-git-hooks-path-mismatch-lint`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `scripts/bridge_proposal_pattern_lint.py` emits a `git-hooks-path-mismatch` finding when a proposal references `.git/hooks/` (or `scripts/guardrails/pre-commit`) while live `core.hooksPath` differs from `.git/hooks`; covered by tests reproducing the two prior NO-GO cases.
- [ ] The detector does NOT fire when the repo uses the default hook path, when the proposal correctly targets `.githooks`, or on rule-documentation lines; covered by negative tests.
- [ ] The diagnostic-by-default contract is preserved: findings exit 0 unless `--strict`; covered by a test.
- [ ] Tests are hermetic — no test mutates real Git config; `core.hooksPath` is injected/overridden.
- [ ] `ruff check` and `ruff format --check` pass on the changed files.
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Risk And Rollback

**Risk R1 (low): false positives when the repo legitimately uses `.git/hooks`.** Mitigation: the detector is a strict no-op whenever the resolved active hook path is empty or `.git/hooks` (the Git default), so a default-configured clone never sees the finding. Negative test 4 asserts this.

**Risk R2 (low): the `core.hooksPath` read adds a subprocess to the lint.** Mitigation: one short `git config --get core.hooksPath` invocation with captured output and no shell, guarded by try/except so a missing/failed `git` degrades to the default-path no-op. Tests inject the value, so the subprocess is not exercised in CI and cannot make tests flaky.

**Risk R3 (low): the detector misses a path token spelled differently (e.g., back-slashed).** Mitigation: normalize separators to forward-slash before matching; the token scan covers the `.git/hooks/` prefix and the named legacy staging path. This is a draft-time advisory guard, not a hard gate, so a missed spelling degrades to today's behavior (Codex still catches it at review) rather than a regression.

**Risk R4 (low): over-broad matching flags a proposal that mentions `.git/hooks` only to explain it is inactive (like this proposal).** Mitigation: the self-documentation guard (reusing `_line_documents_lint_rule`) skips rule-documentation lines; negative test 6 asserts a hazard-describing proposal does not self-trigger.

Rollback: the change is contained to one script plus one new test file. Reverting `scripts/bridge_proposal_pattern_lint.py` to its prior version removes the detector entirely; deleting the new test file removes the coverage. No data migration, no canonical-artifact mutation, no hook registration change.

## Loyal Opposition Asks

1. Confirm the non-fast-lane classification (criterion 2 — new detector is new behavior) and that the dedicated `PAUTH-WI-3482-GIT-HOOKS-PATH-LINT-001` (now granted via DELIB-2548) is the correct authorization basis rather than the standing fast-lane PAUTH.
2. Confirm the bridge-proposal lint (`scripts/bridge_proposal_pattern_lint.py`) is the right home versus a doctor check — and whether the owner should additionally want a doctor surface as a separate follow-on.
3. Confirm the detection token set (`.git/hooks/` plus the legacy `scripts/guardrails/pre-commit`) and the "no-op when active path is the Git default" rule are the correct precision boundary to avoid false positives on default-configured clones.
4. Confirm that prioritizing the `target_paths:` metadata line while still scanning body/prose references is the right scope for catching evasion without over-flagging.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
