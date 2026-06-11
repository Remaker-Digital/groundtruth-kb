REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-09-safety-gate-registration
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4421
Project Authorization: PAUTH-FAB09-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 430d5513-21a1-4e1c-b244-743f2ca7ed00
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: [".claude/settings.json", ".codex/hooks.json", ".claude/hooks/owner-decision-capture.py", ".claude/hooks/gov09-capture.py", ".claude/hooks/_delib_common.py", ".claude/hooks/scheduler.py", ".claude/SCHEDULE.md", ".claude/hooks/turn-marker.py", ".claude/hooks/delib-preflight-gate.py", "CLAUDE.md", ".claude/rules/canonical-terminology.md", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/templates/hooks/**", ".groundtruth/formal-artifact-approvals/*.json", "platform_tests/scripts/**"]

No KB mutation by this implementation: FAB-09 IMPLEMENTS owner-decision-capture.py (whose RUNTIME behavior inserts DELIBs); the implementation itself writes source/config, not `groundtruth.db`. `groundtruth.db` is intentionally NOT in target_paths.

---

# FAB-09 — Safety-gate + hook-registration normalization, REVISED

WI-4421 (FAB-09) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-041, HYG-045, HYG-050.
Revises the proposal after the NO-GO at `bridge/gtkb-fab-09-safety-gate-registration-002.md` (FINDING-P1-001).

## Revision Scope

Addresses the single finding in the `-002` NO-GO:

> FINDING-P1-001 — required narrative-approval packet files are not in `target_paths`.

The CLAUDE.md + `.claude/rules/canonical-terminology.md` edits are protected always-loaded narrative
artifacts, each requiring a per-file narrative-approval packet per `GOV-ARTIFACT-APPROVAL-001` and
PAUTH-FAB09-20260610. The `-001` referenced the packets in prose but did not list the packet directory
in `target_paths`, so the impl-start gate would deny those writes. This revision adds
`.groundtruth/formal-artifact-approvals/*.json` to `target_paths`. No disposition, owner decision, or
verification claim changed; this is a scope-coverage correction only.

## Summary

Three hook-registration drift findings, one HIGH-risk:

- **HYG-041 (HIGH):** `destructive-gate.py` + `credential-scan.py` (destructive-action +
  credential-write gates) are registered **only** in git-ignored `settings.local.json`, so
  fresh clones, worktrees, and headless workers run with **no safety gate** — while
  `canonical-terminology.md` documents a third hook (`scanner-safe-writer.py`) as the live
  credential gate that is registered nowhere. The S294 "essential → tracked" lesson, recurring.
- **HYG-045:** CLAUDE.md claims a live Session Scheduler, but `scheduler.py` is registered in no
  hook surface and `SCHEDULE.md` has been frozen 7 weeks (a stale LO-wrap group on the Prime
  harness). S292 "don't claim mechanisms that don't run."
- **HYG-050:** four no-op scaffold-stub hooks; registering them would be false-green. Two are
  load-bearing — `owner-decision-capture.py` (auto-archive AskUserQuestion → DA) and
  `gov09-capture.py` — and their absence is the mechanism gap behind the DA/AUQ coverage signals.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle authority for this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.
- `GOV-STANDING-BACKLOG-001` — WI-4421 is the governed backlog authority.
- `GOV-ARTIFACT-APPROVAL-001` — CLAUDE.md + canonical-terminology.md edits are protected
  narrative artifacts requiring per-file approval packets.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — the safety-gate registration adds `.codex/hooks.json`
  parity via the existing `.cmd` adapter pattern.
- `SPEC-AUQ-POLICY-ENGINE-001` — `owner-decision-capture.py` serves the AUQ-only enforcement
  stack by mechanizing AUQ→DA capture.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — FAB-09 edits in-root config/hooks/rules + the
  in-root doctor module + the adopter stub templates; it writes **no** out-of-root artifacts
  (this bridge file is under `E:\GT-KB\bridge\`) and relocates nothing. No application-placement change.

Governing rule (non-spec): `.claude/rules/bridge-essential.md` (the S294/S292 lessons this enforces).

## Isolation Placement Compliance

All FAB-09 edits stay **in-root under `E:\GT-KB`**: the config/hook surfaces (`.claude/settings.json`,
`.codex/hooks.json`, `.claude/hooks/*.py`, `.claude/SCHEDULE.md`), the in-root narrative files
(`CLAUDE.md`, `.claude/rules/canonical-terminology.md`), the doctor module, the adopter stub templates
under `groundtruth-kb/templates/hooks/`, the test under `platform_tests/scripts/`, and the
narrative-approval packets under `.groundtruth/formal-artifact-approvals/`. No `applications/` subtree
is touched and no out-of-root artifact is created or required.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-041/045/050).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB09-REMEDIATION-20260610` — this cluster's owner-decision set.
- _`bridge/gtkb-da-governance-completeness-implementation-015.md` §5.5 is the stubs' origin; the
  owner-decision-capture hook automates the manual AUQ→DA capture this campaign has been doing by
  hand (the part throwing exit-255 under Chroma-index load) — DELIB-S312 deterministic-services._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB09-REMEDIATION-20260610`:

1. **HYG-041 = Promote to tracked settings.json** — move both registrations to tracked
   `settings.json` + `.codex/hooks.json` parity (credential-scan.py canonical); retire the
   scanner-safe-writer doc references; extend the doctor registration check to flag missing safety
   gates. (Rejected: scanner-safe-writer-canonical; keep-local-only.)
2. **HYG-045 = Retire** — delete `scheduler.py` + `SCHEDULE.md` + strike the CLAUDE.md Session
   Scheduler section (owner-approved removal). (Rejected: revive; downgrade-claim-only.)
3. **HYG-050 = Implement the 2 capture hooks** — `owner-decision-capture.py` + `gov09-capture.py`;
   doctor reports unimplemented stubs as "stubbed"; defer/remove `turn-marker.py` +
   `delib-preflight-gate.py` + their adopter templates. (Rejected: implement-all-four; remove-all.)

## Requirement Sufficiency

**Existing requirements sufficient.** Governed by bridge-essential.md (S294/S292), SPEC-AUQ-POLICY-ENGINE-001
(the AUQ-capture mechanism), and GOV-ARTIFACT-APPROVAL-001 (narrative packets); the dispositions are
fixed by `DELIB-FAB09-REMEDIATION-20260610`. No new requirement needed.

## Scope and Boundaries

In scope: the three dispositions above. Out of scope: the broader hook-parity audit (FAB-16); any
poller restoration (FAB-01); the orchestrator's hook model (captured separately).

## Proposed Implementation

1. **HYG-041:** move the `destructive-gate.py` + `credential-scan.py` PreToolUse stanzas from
   `settings.local.json` into tracked `settings.json` (matcher `Write|Edit|MultiEdit|Bash`); add
   `.codex/hooks.json` parity via the `.cmd` adapter; update the `canonical-terminology.md`
   scanner-safe-writer entry to name `credential-scan.py` (the registered hook); extend the doctor's
   registration check expected-set to include the safety gates.
2. **HYG-045:** delete `scheduler.py` + `SCHEDULE.md`; remove the CLAUDE.md Session Scheduler section
   (narrative packet).
3. **HYG-050:** implement `owner-decision-capture.py` (PostToolUse on `AskUserQuestion` → DELIB insert
   via `_delib_common.py`) + `gov09-capture.py`; register both; update `doctor.py` to report
   unimplemented stubs as "stubbed" (not "registration-missing"); remove `turn-marker.py` +
   `delib-preflight-gate.py` + their `groundtruth-kb/templates/hooks/` copies.

Each CLAUDE.md/canonical-terminology edit is preceded by its narrative-approval packet
(`.groundtruth/formal-artifact-approvals/*.json`).

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| S294 (essential → tracked) | a test asserts `destructive-gate`/`credential-scan` are registered in tracked `settings.json` + `.codex/hooks.json`; the doctor FAILs if a clone lacks them |
| `SPEC-AUQ-POLICY-ENGINE-001` | a test asserts `owner-decision-capture.py` writes a DELIB row for an AUQ result (PostToolUse contract); the doctor reports it implemented, not stubbed |
| S292 (no dead-mechanism claims) | grep: `scheduler.py`/`SCHEDULE.md` absent; CLAUDE.md has no Session Scheduler claim |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` + `ruff check`/`format --check` on the changed `.py` |

## Acceptance Criteria

1. Both safety gates registered in tracked `settings.json` + `.codex/hooks.json`; doctor flags absence; docs name `credential-scan.py`.
2. `scheduler.py` + `SCHEDULE.md` + the CLAUDE.md Session Scheduler section removed.
3. `owner-decision-capture.py` + `gov09-capture.py` implemented + registered; doctor reports stubs as "stubbed"; turn-marker + delib-preflight-gate stubs + templates removed.
4. Each protected edit has its narrative packet; tests pass; ruff-clean.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-09-safety-gate-registration-003.md` with a matching `REVISED` entry inserted at
the top of the `gtkb-fab-09-safety-gate-registration` entry in `bridge/INDEX.md`; append-only, no prior
bridge version deleted or rewritten. The hook-registration changes do not alter `bridge/INDEX.md` as
canonical workflow state or the bridge versioning discipline (`GOV-FILE-BRIDGE-AUTHORITY-001` preserved);
they strengthen safety enforcement that was silently absent.

## Risk and Rollback

- **Risk:** promoting registrations changes runtime hook behavior on every context → covered by a
  smoke test (a destructive command is blocked; a credential write is scanned) before merge.
- **Risk:** removing a real implementation (scheduler.py) → owner-approved; AXIS-2 covers prompt-surfacing;
  archived in git history.
- **Rollback:** revert the settings/hook/doctor edits + restore the deleted files from git; no MemBase mutation.

## Recommended Implementation Routing

**Mixed, Opus/Codex-supervised** — the safety-gate registration + the capture-hook implementation are
safety-critical, and CLAUDE.md/canonical-terminology edits are packet-gated; not a cheap-model candidate.

## Recommended Commit Type

`fix:` — restores silently-absent safety gates + removes a dead mechanism (with `feat:`-class capture
hooks and `docs:`-class narrative corrections).
