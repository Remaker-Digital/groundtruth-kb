NEW

# gtkb-wi5391-sessionstart-hook-timeout-parity — SessionStart native-hook timeout parity (config-only `timeout: 60`)

bridge_kind: prime_proposal
Document: gtkb-wi5391-sessionstart-hook-timeout-parity
Version: 001
Author: Prime Builder (claude, harness B)
Date: 2026-07-17 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2d31ebb3-7f0c-4987-94a1-d56cd7a388ed
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5391-SESSIONSTART-HOOK-TIMEOUT-20260716
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5391

target_paths: [".claude/settings.json"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Every substantive Alibaba H dispatch on 2026-07-16 died at a native SessionStart
hook timeout: run `2026-07-16T23-10-44Z-loyal-opposition-H-61211e` (stderr:
`native hook timed out: SessionStart: ... session-start-governance.py`) and run
`2026-07-16T23-12-32Z-loyal-opposition-H-e94c60` (stderr: `native hook timed
out: SessionStart: ... assertion-check.py`); evidence at
`.gtkb-state/bridge-poller/dispatch-runs/<run>.stderr.log`. The cloud-harness
shim applies `DEFAULT_NATIVE_HOOK_TIMEOUT_SECONDS = 10.0`
(`scripts/cloud_harness_base.py:187`) to any `.claude/settings.json` hook
registration lacking an explicit `timeout` field
(`_native_hook_command_timeout`, `scripts/cloud_harness_base.py:1421-1432`),
while Claude Code's own native default for the same registrations is 60
seconds. The parity shim is therefore 6x stricter than the surface it emulates,
and the heavyweight startup hooks exceed 10s under fleet load.

This proposal is a config-only fix: add `"timeout": 60` to the three
SessionStart registrations in `.claude/settings.json` that currently lack one
(`session-start-governance.py`; `assertion-check.py`, which is registered
twice). The fourth registration (`session_start_dispatch.py`) already carries
`"timeout": 60` — the same fix applied previously to that one registration —
so this change completes the pattern. Interactive Claude Code behavior is
unchanged (60 is already its effective default); only the shim's fallback is
lifted to parity. No Python source is touched: in particular the four WI-5302
byte-verified files (including `scripts/cloud_harness_base.py` and
`platform_tests/scripts/test_cloud_harness_base.py`) remain byte-identical, so
this fix does not disturb the pending WI-5302 `-005` re-file.

The shim-default bump (10.0 -> 60.0 in `cloud_harness_base.py`) and
SessionStart timeout-recovery parity (the WI-5280 pattern) remain in WI-5391
scope for a follow-on slice after WI-5302 finalizes; this slice takes only the
commingling-safe configuration surface.

## Specification Links

- `ADR-CLOUD-HARNESS-TEMPLATE-001` — the native-full-hook lifecycle runtime
  this fix repairs; the shim's hook execution must faithfully emulate the
  Claude-native surface, including timeout semantics.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — capability floor for GT-KB harnesses;
  a harness whose workers die at startup hooks fails the floor in practice.
- `ADR-CROSS-HARNESS-PARITY-001` — cross-harness parity authority; a 10s shim
  fallback vs the 60s Claude-native default is a parity divergence.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — parity enforcement constraint;
  this change closes an enforcement gap on the hook-timeout axis.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this thread follows the governed bridge
  path (append-only numbered files + dispatcher/TAFE state).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section
  provides the mandatory specification linkage for the proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project/PAUTH/WI
  linkage metadata is carried in the header block above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  below derives its checks from the linked specifications.
- `GOV-STANDING-BACKLOG-001` — WI-5391 is the MemBase backlog authority for
  this defect; this proposal implements its config-surface slice.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the defect, owner decisions, and fix
  are preserved as durable artifacts (WI, DELIBs, PAUTH, this thread), not chat
  context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-network framing: this
  slice links backlog, deliberation, authorization, and bridge artifacts by id.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the owner decisions crossing the
  capture threshold were archived (`DELIB-20260716-...REARM...`,
  `DELIB-20260717-...QUIESCE-RATIFIED...`) per the lifecycle triggers.

## Prior Deliberations

- `DELIB-202665632` — `gtkb-wi4929-codex-sessionstart-timeout-alignment`
  VERIFIED: direct precedent aligning SessionStart timeout behavior for the
  Codex surface; this proposal applies the same alignment principle to the
  cloud-harness shim surface via registration-level config.
- `DELIB-20260716-WI5169-ALIBABA-H-REARM-BUDGET-LIVE` — owner re-armed H under
  a live budget to obtain the WI-5169 viability proof; the hook timeouts this
  proposal fixes are what blocked the short-run path to that proof.
- `DELIB-20260717-WI5169-H-QUIESCE-RATIFIED-WI5113-FIRST` — owner ratified the
  protective H quiesce and explicitly authorized filing this WI-5391-scoped
  config fix now, with re-arm sequenced after the WI-5113 finalizer repair.
- `DELIB-20260709-CLOUD-HARNESS-TEMPLATE-SLICE4-SCOPE-SPLIT` — the 4a/4b scope
  split that produced the native-hook runtime this fix tunes.
- `INTAKE-6308b73f` — harness identity = integration+model+config; prefer
  non-GUI maximal-hook harness integrations: the native-hook surface is the
  maximal-hook commitment this fix keeps viable for dispatched workers.

## Owner Decisions / Input

- AskUserQuestion (this session, 2026-07-16): "How should I pursue the WI-5169
  EXPEDITE proof?" — owner selected **"Fast config fix now (Recommended)"**,
  which the question text defined as authorizing the WI-5391-scoped PAUTH and a
  bridge proposal targeting only `.claude/settings.json`.
- AskUserQuestion (this session, 2026-07-17): H-quiesce ratification — owner
  selected **"Ratify — unblock via WI-5113 (Recommended)"**, whose stated plan
  includes "I file the authorized hook-timeout config fix now". Captured as
  `DELIB-20260717-WI5169-H-QUIESCE-RATIFIED-WI5113-FIRST` (First concrete
  actions authorized, item 2).
- Standing authorization envelope:
  `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5391-SESSIONSTART-HOOK-TIMEOUT-20260716`
  (active; owner-decision `DELIB-20260717-WI5169-H-QUIESCE-RATIFIED-WI5113-FIRST`;
  allowed mutation class `configuration`; included work item WI-5391; expires
  2026-07-20T00:00:00Z).

## Requirement Sufficiency

Existing requirements sufficient. `ADR-CLOUD-HARNESS-TEMPLATE-001` (native-hook
lifecycle emulation), `GOV-HARNESS-ONBOARDING-CONTRACT-001` (harness capability
floor), and `ADR-CROSS-HARNESS-PARITY-001` /
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` (parity semantics) already require
the behavior this change restores; no new or revised requirement is needed for
a registration-level timeout field that brings the shim fallback into parity
with the Claude-native default.

## Spec-Derived Verification Plan

1. `ADR-CLOUD-HARNESS-TEMPLATE-001` + `ADR-CROSS-HARNESS-PARITY-001` — every
   SessionStart registration carries an explicit `timeout` >= 60 after the
   change, and the settings file remains valid JSON:

```text
groundtruth-kb/.venv/Scripts/python.exe -c "import json;d=json.load(open(r'.claude/settings.json'));regs=[h for r in d['hooks']['SessionStart'] for h in r['hooks']];assert all(float(h.get('timeout',0))>=60 for h in regs),regs;print('SessionStart timeouts OK:',[h.get('timeout') for h in regs])"
```

   Expected: `SessionStart timeouts OK: [60, 60, 60, 60]` (order per file).

2. `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — the shim honors
   registration-level timeouts without source change; the existing native-hook
   test suite stays green with `scripts/cloud_harness_base.py` and its test file
   byte-untouched (WI-5302 byte-identity preserved):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py -q --no-header
```

   Expected: same pass count as the WI-5302 -004 verdict baseline (no
   regressions, no test edits).

3. `GOV-HARNESS-ONBOARDING-CONTRACT-001` — post-implementation live evidence
   (deferred to H re-arm after WI-5113 per
   `DELIB-20260717-WI5169-H-QUIESCE-RATIFIED-WI5113-FIRST`): the next dispatched
   H run's `.gtkb-state/bridge-poller/dispatch-runs/<run>.stderr.log` contains
   no `native hook timed out: SessionStart` line. This clause is reported in
   the post-implementation report as pending-live-evidence if H remains
   quiesced at report time; the deterministic checks 1-2 are the verification
   floor for this config-only slice.

4. Byte-identity guard — the four WI-5302 files are untouched:

```text
git status --short scripts/cloud_harness_base.py scripts/alibaba_cloud_studio_harness.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py
```

   Expected: identical status to pre-implementation (no new modifications
   introduced by this change).

## Risk / Rollback

- Risk: a genuinely hung SessionStart hook now holds a dispatched worker up to
  60s per registration instead of 10s (worst case ~4 minutes across the four
  registrations) before the shim kills it. Bounded and preferable to the
  current state where healthy-but-heavy hooks are killed and workers
  crash-loop. Interactive Claude Code behavior is unchanged — 60s is already
  its effective default for these registrations.
- Risk: none to WI-5302 — no Python file is touched; byte-identity check is in
  the verification plan.
- Rollback: single-commit revert removing the three `"timeout": 60` fields
  restores the prior file exactly.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5391-sessionstart-hook-timeout-parity`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix — restores dispatched-worker startup viability by correcting a
timeout-parity defect in enforcement configuration; no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
