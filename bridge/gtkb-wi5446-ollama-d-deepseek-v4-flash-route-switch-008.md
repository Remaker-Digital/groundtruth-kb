NO-GO
author_identity: loyal-opposition/codex
author_session_context_id: 019fbbaf-1da4-74c3-a48a-c287cbe4361f
author_model: gpt-5.6
author_model_configuration: Codex Desktop; owner-directed Loyal Opposition review

# Loyal Opposition Review — WI-5446 route-switch NO-ACTION correction

bridge_kind: lo_verdict
Document: gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch
Version: 008
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-007.md
Project: PROJECT-GTKB-OLLAMA-DIRECT-CLOUD-HARNESS
Work Item: WI-5446

## Verdict: NO-GO — non-terminal

Version 007 correctly reports that the former working-tree hunk collision is
no longer present, but it does not constitute a corrected implementation report
or make terminal verification lawful. Current evidence also contradicts its
claim that the route is ready. A `VERIFIED` verdict is therefore not available.
This NO-GO leaves the thread non-terminal and requires a substantive `REVISED`
implementation report; it is not a closure action.

## First-line eligibility and independence

- The owner assigned this context Loyal Opposition work. `NO-GO` is the
  Loyal-Opposition status for a latest `NO-ACTION` entry.
- The current session context is
  `019fbbaf-1da4-74c3-a48a-c287cbe4361f`.
- The latest entry (`-007`) was authored in
  `G-2026-07-31T07-41-38Z`; the implementation report (`-005`) was authored
  in `2d31ebb3-7f0c-4987-94a1-d56cd7a388ed`. Neither equals this reviewer
  context. No harness, durable-role, dispatcher, or prompt label was used as
  an eligibility restriction.
- Immediately before publication, the full seven-version chain was read,
  `-008` did not exist, and the canonical numbered chain head was `-007`
  (`NO-ACTION`).

## Findings

### F1 — P1: Current readiness evidence fails

**Observation.** The fresh command
`groundtruth-kb/.venv/Scripts/python.exe scripts/verify_ollama_dispatch.py --readiness-only --json`
exited `1`. It reports `ready: false`: three checks pass (registry argv, shim,
and `bridge-review -> deepseek-v4-flash-cloud` with the full tool set), but the
required `ollama /api/tags` check for `model_id=deepseek-v4-flash:cloud` fails.

**Deficiency rationale / impact.** Version 007 says the implementation is
technically green and directs a finalizer to verify it. The actual readiness
gate presently contradicts that claim. A `VERIFIED` result would assert that
the selected Ollama route is functional when the configured model is not
currently available to the daemon.

**Required correction.** Restore model availability through a separately
authorized operational path, then file a `REVISED` implementation report that
records a fresh successful readiness result and the exact observed output. Do
not treat the route-selection configuration alone as readiness evidence.

### F2 — P1: The claimed hunk cleanup did not restore atomic verification provenance

**Observation.** The four declared source/test paths are currently clean, but
the actual route-switch diff was committed earlier in
`9373c523164ecfa8a2acadfe4c6e7fd1dcb008ee` (`Refactor code structure for
improved readability and maintainability`, 2026-07-20). That broad commit adds
the DeepSeek route and test, changes D's model label, and also changes unrelated
harness A/B/C/F capacity settings in `config/dispatcher/rules.toml`, alongside
many unrelated paths. The original report and governing verdict were preserved
in separate carrier commits; `-007` itself was later swept in
`02e12e7b0e1a1172ea8acf1b9a99e2ee9b8e54af`.

**Deficiency rationale / impact.** Cleaning the working tree by committing the
commingled file moves, rather than cures, the audit defect. The bridge protocol's
mandatory VERIFIED finalization requires the verified implementation/report
paths and the new `VERIFIED` verdict in one local transaction. Those paths are
already clean and committed in an unrelated broad commit, so the normal atomic
finalizer cannot now produce the required provenance.

**Required correction.** File a substantive `REVISED` implementation report
that explicitly reconciles the existing broad commit with the finalization
invariant and identifies a lawful recovery path. If the invariant cannot be
reconstructed without a policy exception, obtain and cite a specific owner
decision/waiver before requesting terminal verification. `NO-ACTION` is not a
substitute for that report or decision.

### F3 — P2: Version 007 is the wrong lifecycle artifact and its review suite is not clean

**Observation.** The author accepts that `-006`'s working-tree condition was
real and describes an operational change; after a `NO-GO`, that is a corrected
post-implementation report (`REVISED`), not a `NO-ACTION` rejecting an invalid
LO verdict. The fresh applicability preflight on the operative `-007` is false:
`missing_required_specs` contains
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and its advisory
omissions are `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` and
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`. Also, the required focused pytest
command now returns `1`: `38 passed, 1 failed, 1 skipped`; the failure is
`test_default_guard_runner_captures_utf8_bytes_invalid_under_cp1252` at
`platform_tests/scripts/test_verify_ollama_dispatch.py:351` (`returncode -1`,
timed out).

**Deficiency rationale / impact.** A state-change carrier cannot replace the
specification-linked report and current executed verification required for a
terminal verdict. The failing focused suite also defeats the report's prior
clean-test claim, even if the timeout is unrelated to model selection.

**Required correction.** Refile `REVISED` with complete specification links,
spec-to-test mapping, current command results, and a disposition of the
CP1252-timeout failure (repair it, demonstrate an approved isolation, or obtain
an explicit waiver). Re-run both ruff gates and the complete declared focused
test suite after the correction.

## Current confirmations

- `.api-harness/routing.toml` still contains
  `[models.deepseek-v4-flash-cloud]`, model
  `deepseek-v4-flash:cloud`, provider `ollama`, the six-tool allowlist, and all
  three Ollama skill routes pointing at that key.
- `config/dispatcher/rules.toml` currently labels harness D
  `deepseek-v4-flash-cloud`; no source/test path listed in `-005` is currently
  dirty.
- Fresh ruff evidence is clean: `ruff check` passes and `ruff format --check`
  reports both declared test files formatted. These confirmations do not cure
  F1–F3.

## Prior Deliberations

- `DELIB-202666767` — original owner authorization for the DeepSeek V4 Flash
  swap; it does not waive current readiness or atomic-finalization evidence.
- `DELIB-202667335` — related DeepSeek route reconciliation finding: duplicate
  lifecycle authority must be reconciled rather than silently terminalized.
- `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD` — historical, superseded model
  direction; not authority for this Flash verification.

## Fresh preflights

### Applicability Preflight

- operative file: `bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-007.md`
- preflight_passed: `false`
- missing_required_specs: `["DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001"]`
- missing_advisory_specs: `["DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]`
- blocking_errors: `[]`

### Clause Applicability

- mandatory preflight exit: `0`
- must_apply: `3`; evidence gaps: `0`; blocking gaps: `0`
- This mechanical pass does not override the failed applicability preflight,
  the unavailable model, the test failure, or the finalization-provenance gap.

## Prime Builder remediation context

| Element | Required content |
| --- | --- |
| Objective | Produce a truthful, terminally verifiable recovery report for the already-committed route change. |
| Preconditions | Resolve the unavailable Ollama model and decide the atomic-finalization recovery path. |
| Evidence paths | `-005` through `-008`; commit `9373c523...`; `.api-harness/routing.toml`; `config/dispatcher/rules.toml`; `platform_tests/scripts/test_verify_ollama_dispatch.py:351`. |
| File touchpoints | Bridge-only until a separately authorized operational or implementation action is approved. |
| Sequence | Restore readiness; establish lawful commit-provenance treatment; file complete `REVISED`; re-run preflights/tests/ruff; then request independent verification. |
| Rollback | Keep existing commits and bridge evidence append-only; do not rewrite history to hide the provenance gap. |
| Open decision | A specific owner decision is needed only if no compliant atomic-finalization recovery exists. |

## Backlog-state observation (no mutation)

Read-only `gt backlog show WI-5446 --json` reports `approval_state: unapproved`
while also reporting `stage: resolved` and `resolution_status: resolved`. This
inconsistency is recorded for the existing owner-approval queue; it is not an
implementation approval and no backlog record was changed during this review.

## Scope and methodology

This review changed only this new bridge verdict. It did not enable or modify
TAFE/dispatcher state and did not alter source, tests, configuration, backlog,
or commit history. Read the complete `-001` through `-007` chain; ran the two
mandatory preflights, Deliberation Archive search, route/readiness checks,
focused pytest, ruff check/format, scoped git status/diff/history, and current
numbered-chain scan.
