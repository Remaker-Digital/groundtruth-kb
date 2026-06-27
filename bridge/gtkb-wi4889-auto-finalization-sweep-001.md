NEW

# gtkb-wi4889-auto-finalization-sweep — shared Stop-hook that auto-finalizes untracked terminal VERIFIED verdicts (drain dispatch treadmill)

bridge_kind: prime_proposal
Document: gtkb-wi4889-auto-finalization-sweep
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: ba2cbba9-87c3-41df-af06-ba16eea854be
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4889-AUTO-FINALIZATION-SWEEP
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4889

target_paths: ["scripts/auto_finalize_sweep.py", ".claude/settings.json", ".codex/hooks.json", "platform_tests/hooks/test_auto_finalize_verified_verdicts.py", ".claude/rules/auto-finalization-sweep.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The PHASE-Y dispatcher-daemon go-live (`DELIB-20266272`) created a durability
treadmill. The only dispatchable Loyal Opposition harness (Cursor-E) auto-verifies
through the live `dispatcher_daemon` substrate, but its `--finalize-verified`
commits are blocked by the inventory-drift pre-commit gate, and there is no
dispatchable hooked Prime Builder (Codex-A unavailable; Claude-B quiesced to
`can_receive_dispatch=false` for interactive safety). The result is that terminal
VERIFIED verdicts accumulate untracked and continuously re-fail the WI-4871
untracked-VERIFIED durability guard, requiring a hooked harness to finalize them
by hand each session (this session finalized seven such verdicts manually).

This proposal (Slice 1 of the treadmill-drain program, owner decision
`DELIB-20266278` "build the sweep first") adds a single shared finalization
service `scripts/auto_finalize_sweep.py`, registered as a **Stop hook in BOTH
`.claude/settings.json` and `.codex/hooks.json`** (the same cross-harness pattern
as `scripts/cross_harness_bridge_trigger.py`). On turn-end it runs the existing
cheap WI-4871 guard predicate `_check_untracked_terminal_verified_verdicts`; if
(and only if) that predicate reports untracked terminal VERIFIED verdict files,
it finalizes each eligible one by committing the verdict file plus its untracked
thread-chain `.md` files. It is **verdict-file finalization only** — it never
stages source or test files — so it drains exactly the durability gap the WI-4871
guard detects without attempting the per-thread implementation judgment that must
remain interactive.

### Eligibility (deterministic; both required)

A flagged untracked terminal VERIFIED verdict is auto-finalized only when:

1. **Independence check passes** — the verdict's `author_session_context_id`
   differs from the `author_session_context_id` of the implementation report it
   `Responds to`, evaluated via `scripts/bridge_review_independence.py`. A
   self-review verdict, or one with missing/unreadable author metadata, is
   **skipped and audit-logged** (never auto-committed).
2. **Verified implementation already committed** — the responded-to report's
   `target_paths` are parsed (reusing `implementation_authorization.extract_target_paths`);
   if every target path is clean in `git status` (already committed), the verdict
   is eligible. If any target path is dirty/untracked, the verdict is **skipped
   and audit-logged** for manual finalization (the hook does not guess source
   staging or hunk-selection).

### Action per eligible verdict

Stage the verdict file plus all untracked `bridge/<slug>-NNN.md` files for the
same thread slug, then `git commit` with
`chore(bridge): finalize <author>-LO <slug> VERIFIED verdict (-NNN)`. The commit
runs the standard `.githooks/pre-commit` chain (credential scan, inventory-drift,
narrative-artifact-evidence, ruff-format, protected-commit-authorization); a
commit that the gate blocks is rolled back to staged-clean and audit-logged, not
forced.

### Safety properties

- **Cheap-gated:** the only unconditional work each turn-end is the cheap guard
  enumeration; the commit (the bounded action) runs only when verdicts exist.
  This honors the poller-retirement lesson (`bridge-essential.md`): gate the
  bounded action behind a cheap deterministic check; never spend an expensive
  resource unconditionally.
- **Bounded:** commits only `bridge/*.md` audit files; no source/test staging.
- **Idempotent:** a second run finds no untracked terminal VERIFIED verdicts.
- **Audit-logged:** every finalize/skip is recorded under
  `.gtkb-state/auto-finalize-sweep/`.
- **Not a dispatcher:** it spawns no workers and makes no review decisions; it
  only commits verdicts another harness already decided.

## Cross-Harness Disposition

**Disposition: behavioral parity (single shared implementation, both harnesses).**

This slice does NOT introduce harness-divergent behavior. The finalization logic
lives in one shared module `scripts/auto_finalize_sweep.py`; there is no
Claude-only or Codex-only code path. It is registered identically as a `Stop`
hook in both harness surfaces:

| Harness | Surface | Registration | Behavior |
|---|---|---|---|
| Claude (B) | `.claude/settings.json` `Stop` | invokes `scripts/auto_finalize_sweep.py` | identical |
| Codex (A) | `.codex/hooks.json` `Stop` | invokes `scripts/auto_finalize_sweep.py` | identical |

Both registrations call the same script with the same arguments, so the two
harnesses run byte-identical finalization logic (the same parity model as the
existing `cross_harness_bridge_trigger.py`, registered in both surfaces). Per
`ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2, Codex `Stop` hooks fire on Windows for
Codex CLI ≥ 0.128.0-alpha.1 (`codex_hooks` `stable, true`); the Codex
registration therefore activates whenever Codex runs, even though Codex is
currently not an active dispatch target (owner: Codex unavailable). No
owner-approved typed waiver is required because parity is satisfied by
construction. The verification plan tests the shared module's logic once and
asserts both registrations are present (registration-parity assertion), per the
cross-harness parity test pattern.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the sweep finalizes bridge audit-trail files
  into git, the exact durability the bridge authority requires; it preserves the
  append-only numbered-file chain and never deletes or rewrites a version.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — governs the Codex `Stop`-hook surface
  this proposal registers; the shared script + dual registration satisfies the
  parity contract.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: this
  section cites every governing spec; the verification plan maps to them.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: WI-4889 +
  PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY + active PAUTH metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the spec-derived tests in
  the verification plan exercise the eligibility gates, the commit path, and
  registration parity.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are GT-KB platform
  surfaces in-root under `E:\GT-KB`; the hook commits only in-root working-tree
  files and reads no out-of-root dependency.
- `GOV-STANDING-BACKLOG-001` — WI-4889 is the canonical backlog record under the
  cited PAUTH.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the new behavior
  is enforced by spec-derived hook tests.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
  / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — durable artifacts (WI,
  bridge thread, shared script, tests, rule doc).

## Prior Deliberations

- `DELIB-20266278` — owner AUQ (S20260627) authorizing the treadmill-drain
  program and the "build the sweep first" sequencing; the basis for the PAUTH.
- `DELIB-20266272` — owner AUQ authorizing the dispatcher-daemon go-live whose
  asymmetry (dispatchable LO, no dispatchable hooked PB) creates the treadmill.
- `INTAKE-2ce995f2` — intake on bounded parallel cross-harness auto-dispatch;
  related future direction (a dispatchable hooked PB would reduce, but not
  remove, the verdict-finalization gap this hook drains).
- `DELIB-WI4723-OWNER-PROCEED-20260621` — the VERIFIED finalization-gate retry
  fix; this hook is downstream finalization automation, not a change to the
  finalization gate itself.
- WI-4871 untracked-VERIFIED durability guard (commit `4afbcc8c5`) — the
  detector this hook acts on; the sweep is its automated remediation.

## Owner Decisions / Input

- `DELIB-20266278` — owner AskUserQuestion (S20260627): "Build the sweep first"
  (plus "Codex is not available. We may have to fix Cursor as part of this
  program."). This authorizes building the auto-finalization sweep as Slice 1.
- Owner AskUserQuestion (S20260627) on the cross-harness parity disposition:
  **"Build Codex parallel now"** — i.e., implement full behavioral parity in this
  slice (shared module + Claude + Codex Stop registrations) rather than an
  owner-approved typed waiver deferring the Codex side. This proposal implements
  that choice. No further owner decision is required to file or implement.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001`'s
finalization-durability requirement and the WI-4871 guard already define the
target state (no untracked terminal VERIFIED verdicts); this slice supplies the
automated remediation. No new or revised requirement; no formal
spec/governance mutation in scope (`kb_mutation_in_scope: false`). The
`.claude/rules/auto-finalization-sweep.md` narrative doc documents the hook
contract and will carry a narrative-artifact-approval packet at implementation
time.

## Spec-Derived Verification Plan

| Spec / clause | Test | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (finalizes untracked terminal VERIFIED verdict + chain) | `test_sweep_finalizes_eligible_verdict` | verdict + untracked chain committed; guard then passes |
| Eligibility gate 1 (independence) | `test_sweep_skips_self_review_verdict` | self-review verdict skipped + audit-logged, not committed |
| Eligibility gate 2 (impl committed) | `test_sweep_skips_when_impl_uncommitted` | verdict with dirty target_paths skipped + audit-logged |
| Cheap-gate / no-op | `test_sweep_noops_when_no_untracked_verdicts` | no commit, no error when guard is clean |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (idempotency) | `test_sweep_idempotent` | second run finds nothing to finalize |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (registration parity) | `test_sweep_registered_in_both_harness_surfaces` | the shared script is in both `.claude/settings.json` and `.codex/hooks.json` Stop arrays |

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_auto_finalize_verified_verdicts.py -q --no-header
```

## Risk / Rollback

- **Risk — over-eager commit:** mitigated by the two deterministic eligibility
  gates (independence + impl-committed) and verdict-file-only staging; the hook
  cannot commit source, cannot finalize a self-reviewed verdict, and cannot
  finalize a verdict whose impl is not already in git.
- **Risk — interactive surprise:** the hook commits only terminal VERIFIED
  verdicts (already decided by an independent LO), with the standard finalize
  commit message; it never amends or rewrites history and is announced via the
  audit log. The narrative rule doc documents the behavior.
- **Risk — pre-commit gate block:** a blocked commit is rolled back to
  staged-clean and audit-logged; the verdict simply remains untracked for the
  next run or manual handling (no partial/broken commit).
- **Risk — Codex side untestable at runtime now:** Codex is not an active
  dispatch target, so the Codex `Stop` registration cannot be runtime-exercised
  this slice; it is covered by the registration-parity assertion and the shared
  logic's unit tests, and activates when Codex runs (`ADR-CODEX-HOOK-PARITY-FALLBACK-001`).
- **Rollback:** remove the `Stop`-hook registrations from `.claude/settings.json`
  and `.codex/hooks.json` (line reverts) and/or delete the shared script; no KB
  mutation; the bridge audit trail is unaffected.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4889-auto-finalization-sweep`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat` — adds a net-new governance automation surface (a shared Stop-hook service
plus its dual-harness registration, tests, and narrative contract doc).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
