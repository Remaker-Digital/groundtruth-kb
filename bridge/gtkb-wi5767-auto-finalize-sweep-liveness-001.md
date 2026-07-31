NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 08ab8a9d-bc19-4278-b81f-a8b3a488700c
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code headless proposal worker under manual dispatch from leader session bb6ca43c (DELIB-202667523/531/533 fan-out); resolved role prime-builder for this dispatched drafting task

bridge_kind: prime_proposal
Document: gtkb-wi5767-auto-finalize-sweep-liveness
Version: 001
Date: 2026-07-29 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5767

target_paths: ["scripts/auto_finalize_sweep.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", ".claude/skills/gtkb-bridge-propose/helpers/write_bridge.py", "platform_tests/scripts/test_doctor_auto_finalize_sweep_liveness.py", "platform_tests/hooks/test_auto_finalize_verified_verdicts.py", "platform_tests/skills/test_bridge_propose_helper.py"]

# WI-5767 — Assert Auto-Finalize Sweep Liveness in Doctor, Correct the Bridge Writer Help Surface, and Close the Finalization Attribution Gap

Scope confirmation: this proposal performs no MemBase mutation and no
groundtruth.db write during filing; the implementation touches only the six
target_paths files (three existing source/helper files, one new test module,
two existing test modules) and is covered by the cited project authorization.

This filing performs no approval-evidence work; it requires no approval
packets. No target path is a protected narrative artifact (the protected set
is `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE.md` and application
counterparts; the skill-helper `.py` files here are code surfaces).

## Problem

Source advisory chain:
`bridge/gtkb-lo-auto-finalize-sweep-zero-success-advisory-001.md` and its
same-session correction `-002.md` (classification `adapt`). The `-002`
correction narrows the live scope: Finding B (staged residue) was closed by
events when commit `1c82158e8` landed; Findings A and C stand, and the
correction adds a new item — the finalizing commit itself is unattributed.
WI-5767 is the authorized fix-band work item for this advisory
(DELIB-202667534, order 200).

### A — the auto-finalization sweep has a 0% success rate and nothing asserts its liveness

Re-derived live tally this session (2026-07-30 UTC), superseding the advisory
numbers per GOV-SOURCE-OF-TRUTH-FRESHNESS-001:
`.gtkb-state/auto-finalize-sweep/sweep.jsonl` now holds 25,436 entries
spanning 2026-07-01T15:33:15Z through 2026-07-30T03:52:18Z — `skip` 25,391,
`error` 27, `planner_error` 18, `finalize` 0, zero unparseable lines. The
sweep (`scripts/auto_finalize_sweep.py`, WI-4889) is the designated
remediation for the WI-4871 untracked-terminal-VERIFIED durability guard, and
it has never once performed that function in 29 days of operation.

This is a recurrence with precedent: the same condition was diagnosed
read-only on 2026-07-09 (DELIB-WI5116-PHASE1-SWEEP-DIAGNOSIS-20260709 — sweep
registered and firing, 1500/1500 recent entries `skip`, 0 finalize) and no
assertion was added then; three further weeks produced 0 finalizations. The
narrative authority (`.claude/rules/auto-finalization-sweep.md`) describes the
sweep in the present indicative as a working safety net; the append-only log
is currently the only place its 0% record is observable, and no doctor
surface, hook, or session flow reads it. The WI-4871 doctor check
(`_check_untracked_terminal_verified_verdicts`,
`groundtruth-kb/src/groundtruth_kb/project/doctor.py:2454`) WARNs per
untracked verdict but is deliberately fail-soft and says nothing about
whether the remediation mechanism is draining the backlog.

The missing assertion is the aggregate-pattern one the advisory names: N
sweep runs with zero finalizations WHILE the WI-4871 population is non-empty
is a FAIL-level condition, not a silent log line.

### The unattributed finalizing commit — investigated read-only this session

Commit `1c82158e8` (`fix(bridge): reproducible verdict freshness and
exact-row publication routing (WI-5441)`, authored 2026-07-28T03:08:23Z)
committed exactly the fifteen paths of the WI-5441 `-010` VERIFIED
finalization. Read-only investigation results, all UTC 2026-07-28:

- 01:58:04Z — the thread's implementation-start packet had expired
  ("Terminal VERIFIED finalization packet expired during independent review
  and commit-gate execution", per the packet's own recovery block).
- 02:59:21Z — a bespoke renewal script was written at
  `.gtkb-state/propose-drafts/renew_wi5441_v010_finalization_packet.py`
  (hash-verifying, authority-preserving, expiry +120 minutes under
  `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726`).
- 02:59:36Z — the packet recovery executed (`recovered_at`); the recovery
  block records `authority_id`, hashes, timestamps, and reason — but NO actor
  or session field.
- ~03:05Z — the advisory session observed the 15 paths transition from
  untracked to staged with no mutating command of its own.
- 03:08:23Z — `1c82158e8` landed. Its subject matches, verbatim, the
  "Intended commit subject" in the `-010` verdict's Commit Finalization
  Evidence section, and its path set matches the declared same-transaction
  path set exactly.

Disposition: the MECHANISM is attributable with high confidence — this was
the governed `write_verdict.py --finalize-verified` transaction for `-010`
completing after an authorization-preserving packet-expiry recovery, not the
auto-finalize sweep (the sweep's invariants exclude it: it stages only
`bridge/*.md` chains, never source, and uses the
`chore(bridge): finalize ...` message format) and not an accident. The ACTOR
SESSION is genuinely indeterminable from in-root evidence, because every
surface that could have recorded it is absent: the commit carries no trailer
(bare subject, shared workstation git identity), the finalization helper
writes no durable audit entry for the commits it creates (its only log
surface is the verdict-prepopulation log), the packet recovery block has no
actor field, the sweep log correctly has no entry (not its commit), and the
work-intent claim had TTL-expired. This proposal therefore documents the
indeterminacy and specifies the attribution gap fix (below) so future
finalizing commits are always attributable.

### C — the governed bridge writer's help surface exits 0 and prints nothing

Re-verified this session: `.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py`
defines no `ArgumentParser`, no `main`, and no `if __name__` guard — direct
invocation (including `--help`) imports the module, does nothing, and exits 0
with empty stdout and stderr. This is the silent-success defect class
(advisory `gtkb-lo-tooling-defect-advisory-001` A1b) in a second location: a
probing agent cannot distinguish "import-only module" from "help suppressed",
and each proposal filing requires composing a throwaway runner script.

## Proposed Change

Three bounded, additive changes plus one explicit composition boundary.

### 1. Sweep probe mode and attributable audit entries (`scripts/auto_finalize_sweep.py`)

- Add a `--probe` CLI argument: runs `sweep(dry_run=True)` (the existing
  dry-run path, which classifies without committing) and prints a JSON
  summary — WI-4871 enumeration count, would-finalize (fully eligible now)
  entries, and per-reason skip breakdown. The Stop-hook path (stdin drain,
  unconditional exit 0, fail-soft) is byte-for-byte unchanged in behavior;
  probe is opt-in and never commits, never writes `finalize`/`error` audit
  actions.
- Extend `_audit()` so every appended entry carries a best-effort `actor`
  context block (`source: "auto_finalize_sweep"`, hook-visible session
  identifiers from the environment when present, pid). Fail-soft: absence of
  identifiers never blocks the append. This makes the sweep's own audit rows
  attributable, per the attribution finding.

### 2. Doctor liveness assertion (`groundtruth-kb/src/groundtruth_kb/project/doctor.py`)

New payload function `check_auto_finalize_sweep_liveness(target)` plus
ToolCheck wrapper `_check_auto_finalize_sweep_liveness(target)`, registered
via `checks.append(...)` adjacent to the WI-4871 registration in
`run_doctor` (doctor.py:7239 vicinity), following the established
payload+wrapper pattern. Machine-readable payload (`schema_version: 1`,
`check: "auto_finalize_sweep_liveness"`). Finding kinds:

- **(a) FAIL `sweep-liveness-zero-drain`** — the WI-4871 enumeration
  (untracked terminal VERIFIED verdicts, the same enumeration the sweep's
  cheap gate uses) is non-empty AND the most recent N sweep audit entries
  (default N=20, env-tunable `GTKB_SWEEP_LIVENESS_WINDOW`) contain zero
  `finalize` actions. Payload carries the backlog size, oldest-verdict age,
  a per-reason skip histogram over the window, and the probe breakdown
  (how many are fully-eligible-now vs blocked and on what), so the doctor
  answers "why is nothing draining?" without a log excavation. Against
  today's live state this finding FIRES (25,391 skips, 0 finalize, non-empty
  WI-4871 population) — that is the owner-chosen visibility outcome fixed by
  the authorized WI title ("Assert auto-finalize sweep liveness"), converting
  an invisible 0% record into a red surface with a drain-down target, exactly
  as the sibling WI-5762 slice does for PAUTH hygiene.
- **(b) WARN `sweep-not-observing-backlog`** — the WI-4871 enumeration is
  non-empty AND fewer than N audit entries exist within the recency horizon
  (default 24h, env-tunable): the backlog is visible but the sweep does not
  appear to be running (e.g., hook deregistration) so N-run inertness cannot
  be proven. Distinct from (a) because the remediation differs (restore the
  hook vs unblock the drain).
- **(c) WARN `unattributed-finalizing-commit`** — a commit more recent than
  the attribution cutoff (module constant, set to this change's landing
  date; see OD-C) whose diff introduces a terminal VERIFIED bridge file and
  which carries neither a matching sweep `finalize` audit entry nor a
  `GTKB-Finalization-*` commit-message trailer. Bounded read-only git scan
  (commit-count and date bounded). This is the detection floor that arms the
  write-side attribution fix (boundary 4): once the finalizer emits
  trailers/audit entries, any future out-of-band `1c82158e8`-class commit
  surfaces at the next doctor run instead of requiring a forensic session.
- **(d)** PASS otherwise, with informational counts (log length, last entry
  timestamp, last finalize timestamp if any). Missing/unreadable log with a
  non-empty WI-4871 population reports (b); git unavailability degrades to
  `info`, mirroring the adjacent WI-4871 check's fail-soft posture. Severity
  aggregation: `fail` if any FAIL, else `warning` if any WARN, else `pass`.

Eligibility semantics are single-sourced: the doctor invokes the sweep's own
`--probe` mode (subprocess, explicit interpreter, timeout-bounded, fail-soft)
rather than re-implementing the three-gate eligibility logic, so the check
can never drift from what the sweep would actually do. The FAIL trigger (a)
deliberately keys on the WI-4871 enumeration — not on probe eligibility —
so a defect in the sweep's own eligibility logic (the
DELIB-WI5116-PHASE1 failure shape, where the sweep fail-safe-skipped the
entire backlog) cannot suppress the assertion that should expose it.

### 3. Bridge writer help surface (`.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py`)

Add a module `main()` + `if __name__ == "__main__"` guard implementing the
advisory's minimal option (a real help surface documenting import-only
status), deliberately NOT the first-class CLI option, which is owned by the
WI-5763 lane:

- `--help`/`-h`: prints usage to stdout and exits 0. The text states the
  module is the import-only governed bridge writer; names the public entry
  points (`propose_bridge()`, `propose_bridge_codex_non_bypass()`); states
  the version-1-only contract (raises `BridgeFileAlreadyExistsError` when
  the thread exists — it cannot append); and routes append/verdict/advisory
  filing to the governed CLI surfaces (the WI-5763 `gt bridge file-verdict`
  lane once landed).
- Any other direct invocation: prints the same usage to stderr and exits 2.
- Import behavior is unchanged; no existing function signature or behavior
  is touched.

### 4. Composition boundaries (specified here, implemented in adjacent lanes)

The write-side half of the attribution fix is specified by this proposal as
a requirement and routed to the lanes that own those surfaces, to avoid
concurrent-GO target overlap:

- **Finalizer attribution (write side):** the governed VERIFIED finalizer
  must (i) append a durable finalization audit entry (JSONL: ts, slug,
  verdict path, staged path set, resulting commit SHA, actor identity and
  session context) for every commit it creates, and (ii) stamp
  `GTKB-Finalization-Session:` / `GTKB-Finalization-Actor:` trailers on the
  commit message so the commit object itself is attributable independent of
  state files. Implementation home:
  `.claude/skills/gtkb-verify/helpers/write_verdict.py` is inside the
  WI-5763 thread's declared target_paths
  (`bridge/gtkb-wi5763-governed-verdict-filing-path-001.md`, GO at `-002`)
  and the AT-01 commit-first finalizer redesign (DELIB-202667533) is the
  owning workstream — this thread does not touch that file. Finding kind (c)
  is written against exactly these trailer/audit surfaces.
- **Packet-recovery actor field:** the expiry-recovery block (the
  `finalization_packet_expiry_recovery` schema observed in the WI-5441
  packet) should require an actor/session field; that schema belongs to the
  WI-5694 lane (post-review finalization authority across packet expiry and
  sweep commits), which this proposal cites but does not implement.
- **`.claude/rules/auto-finalization-sweep.md`** is also inside WI-5763's
  declared target_paths; this thread deliberately does not edit the rule
  file. The rule's mechanism contract is unchanged by this slice (probe mode
  adds a read-only diagnostic entry point; the hook contract is untouched).

## Cross-Harness Disposition

Two target_paths entries are harness-surface files; behavioral parity is
declared for both, per applicable harness. No typed waiver is requested.

- **`scripts/auto_finalize_sweep.py`** is the shared Stop-hook script
  registered in BOTH `.claude/settings.json` (Claude Code, harness B) and
  `.codex/hooks.json` (Codex CLI, harness A) under the dual-registration
  shared-script parity model (`.claude/rules/auto-finalization-sweep.md`;
  ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2). This change edits the shared script
  only and touches NEITHER registration surface: the hook execution path
  (stdin drain, fail-soft, unconditional exit 0, disable env) is behaviorally
  unchanged and identical under both registrations; `--probe` is an explicit
  CLI invocation available identically from any harness; the audit `actor`
  block derives identifiers from the environment best-effort per harness and
  never blocks the append when a harness provides none. The existing
  both-surfaces registration test
  (`test_sweep_registered_in_both_harness_surfaces` in
  `platform_tests/hooks/test_auto_finalize_verified_verdicts.py`) remains in
  force and green.
- **`.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py`** is the
  canonical managed-skill helper; every harness (Claude B, Codex A, Cursor E,
  Antigravity C, Ollama D) that files a proposal invokes this same file by
  explicit path, so the new `__main__` help surface is byte-identical
  cross-harness by construction. Codex-side skill adapters regenerate from
  the canonical `.claude/skills/` sources per the managed-skill lifecycle; no
  harness-local mirror of this helper exists to drift. Import behavior is
  unchanged, so no harness-registered consumer (including the sweep's
  verify-helpers import path) observes any difference.
- The remaining four target paths (`doctor.py`, three `platform_tests/**`
  modules) are not harness-surface files; the doctor check is
  harness-neutral (invoked via `gt project doctor` from any harness).

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — the bridge audit-trail and finalization durability authority the sweep serves (per its own rule-file authority block); the liveness assertion and attribution tripwire protect exactly that durability contract (mandatory anchor).
- DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 — the parity-disposition gate this proposal's Cross-Harness Disposition section satisfies for its two harness-surface target paths.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — the dual-registration substrate contract for the sweep Stop hook; this change preserves both registrations untouched.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal's own specification-linkage duty; links here are complete against the applicability preflight.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the spec-derived verification gate governing this thread's eventual VERIFIED; the test plan maps every linked specification to executed tests.
- GOV-STANDING-BACKLOG-001 — WI-5767 is the MemBase backlog authority for this work.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 — the check derives findings from fresh reads of the live audit log, git state, and probe output at doctor runtime; this proposal re-derived the advisory's counts before filing per the same principle.
- GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001 — sweep-liveness review becomes a deterministic doctor check instead of per-session log excavation (the advisory itself was a hand-run excavation).
- SPEC-1830 — operational procedures must be code, not conversation; "is the safety net alive?" becomes a check.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — two-layer defense in depth: write-time attribution (finalizer lane) plus review-time/doctor detection (this lane).
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — all six target paths are in-root platform surfaces; no application or out-of-root placement.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — append-only discipline: the check reads state and mutates nothing; the audit log remains append-only; this bridge chain stays append-only.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — a governance surface (the sweep rule) currently asserts behavior the artifact record contradicts; detection restores artifact truthfulness.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — explicit lifecycle-state discipline: the check surfaces terminal verdicts stuck between written and committed (the untracked→staged→committed finalization lifecycle) so durable state does not silently stall mid-transition.
- GOV-10 — tests exercise exposed production interfaces (the payload function, the ToolCheck wrapper, the probe CLI, the module entry point), not internals.
- GOV-12 — work item creation triggers test creation; the new doctor test module lands with the check and the two existing suites are extended.
- SPEC-1662 (GOV-18) — assertions are behavioral (finding kinds, severities, histogram content, exit codes, stream routing), not shape-only.
- GOV-15 — no autonomous fixes: the check reports; draining the terminal backlog, unblocking commits, and the write-side finalizer changes remain owner-gated work in their own lanes.

## Prior Deliberations

Deliberation search performed 2026-07-30 (`gt deliberations search "auto
finalize sweep zero success" --limit 5`): DELIB-WI5116-PHASE1-SWEEP-DIAGNOSIS-20260709
(controlling precedent — the same zero-finalize condition diagnosed read-only
on 2026-07-09: sweep firing, 1500/1500 recent entries skip, 0 finalize; no
assertion was added and the condition recurred, which is this proposal's core
justification), DELIB-202666599 (GO — WI-5370 sweep invalid-body guard, the
canonical-floor eligibility gate now part of the skip taxonomy this check
histograms), DELIB-202666991 (NO-GO predecessor of the same),
DELIB-202666070 and DELIB-20266340 (verdict records; non-controlling).
Targeted-id reads and authorities:

- DELIB-202667531 — owner triage directive: fix-class advisories become authorized corrective work items; owner-decision evidence for PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729 and its program PAUTH; bridge protocol explicitly NOT waived per item.
- DELIB-202667533 — AT-01..AT-04 synthesis decisions. AT-04 establishes the program PAUTH cited by this proposal. AT-01 (commit-first finalizer redesign) is the owning lane for the write-side attribution fix specified in Proposed Change §4 — cited as boundary authority, deliberately not scoped into this thread.
- DELIB-202667534 — advisory corpus disposition table consolidating `gtkb-lo-auto-finalize-sweep-zero-success` into WI-5767 (fix band, order 200).
- DELIB-20266278 — owner authorization of the treadmill-drain program and the sweep build (WI-4889); the mechanism whose liveness this slice asserts.
- DELIB-20266272 — the PHASE-Y dispatcher go-live whose asymmetry created the treadmill the sweep was built to drain.
- Source advisory chain: `bridge/gtkb-lo-auto-finalize-sweep-zero-success-advisory-001.md` (Findings A-D) and `-002.md` (correction: B closed by events; A sharpened; attribution item added). Finding D (advisory-channel drain) was dispositioned separately by the 2026-07-29 triage and is not in this scope.
- Lane boundaries: WI-5763 (`bridge/gtkb-wi5763-governed-verdict-filing-path-001.md`, GO at `-002`) owns `write_verdict.py`, the verdict-filing CLI, and the sweep rule file — no shared target paths with this thread; WI-5694 owns post-review finalization authority (packet expiry / sweep-commit interaction — the exact failure the `1c82158e8` timeline hand-worked around); WI-5765 owns the red LO commit-atomicity suites and VERIFIED evidence gate; WI-5424 (PROJECT-GTKB-TREE-STABILIZATION) is the advisory chain's parent context.
- Concurrency disclosure: `doctor.py` is a convergence surface — the sibling WI-5762 thread (`bridge/gtkb-wi5762-pauth-accumulation-doctor-001.md`, NEW) adds a check to the same file, and the worktree currently carries uncommitted WI-5688 doctor hunks (per the live sweep log's own skip entries). This check is a self-contained additive payload function + wrapper + one registration line, composing with both; implementation rebases on whatever doctor.py state is current at GO.

## Owner Decisions / Input

Recorded authority for this filing:

- **DELIB-202667531** (owner decision, 2026-07-29): fix-class advisory triage authorized; corrective work items created and authorized ahead of other advisory-derived work; supplies the owner-decision evidence for PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729 and its program PAUTH per GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001. WI-5767 is one of those corrective items (P2, defect, `maintenance_tool`), and its authorized title ("Assert auto-finalize sweep liveness and attribute the unaudited finalizing commit") fixes both the assertion mandate and the attribution mandate this proposal implements.
- **DELIB-202667533 AT-04** (owner AUQ, 2026-07-29): program PAUTH PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM (v3 `active` after the SF-1 corrected reissue; classes source, test_addition, governance_evidence, bridge; covers WI-5767 through the corrections program scope). AT-01 from the same record is cited as the write-side attribution lane's authority (boundary, not scope).
- **DELIB-202667534** (owner decision, 2026-07-29): disposition-table consolidation fixing WI-5767's direction (sweep liveness assertion in doctor; writer help surface; attribute the out-of-band commit).

Open decisions — design ratifications with recommended defaults, non-blocking
for this slice; flagged for implementation-time AskUserQuestion if Loyal
Opposition prefers owner confirmation:

- **OD-A (liveness window N).** Default N=20 most-recent audit entries with zero `finalize` (env-tunable `GTKB_SWEEP_LIVENESS_WINDOW`). At the observed ~2-minute cadence this is ~40 minutes of proven inertness against a live backlog before FAIL. Alternative: a time-window (e.g., 6h) instead of an entry-count.
- **OD-B (unattributed-commit severity).** Default WARN for finding (c) in this slice, promotion to FAIL as a named follow-on once the AT-01 lane lands the write-side trailers/audit entries (before that, every governed finalization would FAIL spuriously). Alternative: land (c) already at FAIL and accept red until the finalizer lane ships.
- **OD-C (attribution cutoff).** Default: a module constant set to this change's landing date — historical finalizing commits (which structurally predate trailers) are exempt; only future commits are held to the attribution standard. The `1c82158e8` record itself is preserved by this proposal and the implementation report, not by retroactive doctor findings. Alternative: env-configurable cutoff for audit replays.

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001 already
establishes the durable bridge audit-trail contract this slice makes
observable; the WI-4889 sweep contract (rule file, untouched here) already
mandates audit logging; GOV-SOURCE-OF-TRUTH-FRESHNESS-001, SPEC-1830, and
GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001 already require fresh-read,
code-not-conversation checks. No new or revised requirement is required
before implementation. Any change to what the FINALIZER must emit (the
write-side attribution contract) is specified here as a requirement for the
AT-01/WI-5763 lane and lands through that lane's own governed path.

## Spec-Derived Test Plan

New test module `platform_tests/scripts/test_doctor_auto_finalize_sweep_liveness.py`
(declared new; does not exist at HEAD). Fixture git repos with synthetic
`bridge/` files and synthetic `.gtkb-state/auto-finalize-sweep/sweep.jsonl`;
no live MemBase read/write; no live bridge mutation. Cases:

1. **Zero-drain FAIL case** — `test_zero_drain_with_backlog_fails`: fixture
   with an untracked terminal VERIFIED verdict plus a synthetic log of N
   `skip` entries and zero `finalize` → exactly one
   `sweep-liveness-zero-drain` FAIL finding whose payload carries the skip
   histogram and backlog count; aggregate `fail`. Derives from
   GOV-FILE-BRIDGE-AUTHORITY-001 (undrained terminal backlog), SPEC-1662,
   GOV-10. (This is the dispatch-required "zero-success-with-eligible-backlog
   trips the assertion" case.)
2. **Healthy sweep PASS case** — `test_recent_finalize_passes`: same backlog
   fixture but the window contains a `finalize` entry → no FAIL finding;
   aggregate not `fail`. Derives from SPEC-1662 (the check discriminates
   rather than uniformly failing).
3. **Legitimately-idle PASS case** — `test_empty_backlog_passes`: skip-heavy
   historical log but NO untracked terminal VERIFIED verdicts → `pass` (a
   noisy history alone is not a liveness failure). Derives from SPEC-1662.
4. **Stale-log WARN case** — `test_stale_log_with_backlog_warns`: untracked
   VERIFIED verdict present, no audit entries within the recency horizon →
   `sweep-not-observing-backlog` WARN. Derives from
   GOV-FILE-BRIDGE-AUTHORITY-001, SPEC-1662.
5. **Attribution tripwire case** — `test_unattributed_finalizing_commit_warns`:
   fixture commit dated after the cutoff adding a VERIFIED bridge file with
   no trailer and no matching `finalize` audit entry → WARN naming the SHA;
   variant with a `GTKB-Finalization-Session` trailer → not flagged; variant
   with a matching sweep `finalize` entry → not flagged. Derives from
   GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001,
   GOV-FILE-BRIDGE-AUTHORITY-001, SPEC-1662.

Extensions to `platform_tests/hooks/test_auto_finalize_verified_verdicts.py`
(existing suite, fixture `repo` pattern):

6. **Probe non-mutation** — `test_probe_mode_reports_without_committing`:
   `--probe` against an eligible fixture prints JSON naming the would-be
   finalization and creates no commit and no `finalize` audit action.
   Derives from GOV-10, SPEC-1662; protects the GOV-15 boundary (probe never
   fixes).
7. **Attributable audit entries** — `test_audit_entries_carry_actor_context`:
   entries appended by a sweep run carry the `actor` block
   (`source: "auto_finalize_sweep"`, pid; session identifiers when the env
   provides them). This is the dispatch-required "audit entries carry
   attributable actor" case. Derives from GOV-FILE-BRIDGE-AUTHORITY-001
   (attributable audit trail), SPEC-1662.

Extensions to `platform_tests/skills/test_bridge_propose_helper.py`
(existing suite for this helper):

8. **Help surface** — `test_help_flag_documents_import_only_surface`:
   subprocess `--help` → exit 0, stdout names `propose_bridge`,
   `propose_bridge_codex_non_bypass`, the version-1-only contract, and the
   governed-CLI routing; `test_direct_invocation_exits_nonzero`: bare
   invocation → exit 2, usage on stderr, empty stdout. Derives from
   SPEC-1830 (a code surface must state its own contract), SPEC-1662
   (exit codes and stream routing asserted behaviorally), GOV-10.

Execution: `groundtruth-kb/.venv/Scripts/python.exe -m pytest
platform_tests/scripts/test_doctor_auto_finalize_sweep_liveness.py
platform_tests/hooks/test_auto_finalize_verified_verdicts.py
platform_tests/skills/test_bridge_propose_helper.py -v`, plus `ruff check`
and `ruff format --check` on all changed Python files, plus a one-shot live
run of the payload function against `E:\GT-KB` recorded in the
implementation report (expected: `sweep-liveness-zero-drain` FAIL with
counts in the vicinity of the tally above, unless the terminal backlog has
been drained in the interim).

## Acceptance Criteria

1. `gt project doctor` reports FAIL when untracked terminal VERIFIED
   verdicts coexist with an N-entry zero-finalize sweep-log window, WARN
   when the backlog is visible but the log is stale/absent, and PASS on both
   healthy-drain and legitimately-idle states (three-way discrimination).
2. The payload distinguishes diagnosis classes: skip-reason histogram plus
   probe breakdown (fully-eligible-now vs blocked-and-why), sourced from the
   sweep's own dry-run semantics, never a re-implementation.
3. Sweep `--probe` reports eligibility without mutating (no commit, no
   finalize/error audit action); the registered Stop-hook path is
   behaviorally unchanged (fail-soft, exit 0, disable env honored).
4. Sweep audit entries carry an attributable actor block; finalizing commits
   after the cutoff that lack both a sweep `finalize` entry and a
   `GTKB-Finalization-*` trailer surface as doctor findings.
5. `write_bridge.py --help` exits 0 documenting the import-only contract and
   entry points; bare direct invocation exits 2 with usage on stderr; import
   behavior is unchanged and all pre-existing helper tests still pass.
6. The `1c82158e8` disposition is durably recorded: mechanism attributed
   (governed `-010` finalization after packet-expiry recovery), actor
   session documented as indeterminable from in-root evidence, and the
   write-side fix specified with lane assignments (AT-01/WI-5763 finalizer;
   WI-5694 packet-recovery schema).
7. All eight test cases pass; ruff lint and format gates clean on every
   changed Python file; the change is additive and non-gating (no hook,
   commit gate, preflight, or session flow consults the new check), and
   removal is a clean revert of the three source hunks plus test deltas.

## Risk and Rollback

Risk: LOW-MEDIUM. All three source changes are additive: a new opt-in CLI
flag and an audit-entry field on the sweep (hook path untouched), a new
self-contained doctor check (payload + wrapper + one registration line), and
a `__main__`-only help surface on an import-only module (imports unaffected).
No gate consults the new check; no dispatcher/TAFE surface, MemBase schema,
or bridge state is touched. Known consequences, disclosed: (1) the doctor
goes red on day one with the zero-drain FAIL against the live 25,436-entry /
0-finalize log — the owner-chosen assertion outcome, matching the advisory's
"FAIL-level condition, not a silent log line"; (2) doctor.py is a
convergence surface with WI-5762 (NEW, same file) and uncommitted WI-5688
worktree hunks — mitigated by the additive shape and GO-time rebase; (3) the
attribution tripwire is cutoff-gated WARN until the AT-01 lane lands
write-side trailers, so it cannot spuriously fail governed finalizations in
the interim. Rollback: revert the three source hunks and the two test-module
deltas, delete the new test module — no runtime coupling, no data migration,
the audit log format change is purely additive (readers tolerate extra
fields).

Recommended commit type: fix

Justification: this repairs a defect class (origin `defect`, per the
authorized WI): a documented safety mechanism whose 0% operating record was
invisible, an unattributable governed-commit path, and a silent-success help
surface. The doctor check, probe flag, and usage guard are the repair's
observability instruments, not a new capability surface; the fix restores
the already-documented contracts (rule-file audit-trail claims, silent-
success prohibition) to observable truth.

## Verification Questions for Loyal Opposition

1. Finding (a) keys the FAIL on the WI-4871 enumeration (backlog exists)
   rather than on probe-confirmed full eligibility, precisely so an
   eligibility-logic defect (the DELIB-WI5116-PHASE1 failure shape) cannot
   suppress the assertion — but this means by-design-skipped backlogs (e.g.,
   every verdict blocked on `verified impl not committed`) also FAIL. Is
   that the correct reading of the authorized "assert liveness" mandate (red
   means "a human or lane must act on the drain"), or should by-design skip
   classes downgrade to WARN?
2. Is the composition boundary drawn correctly — write-side trailers/audit
   entries specified here but implemented in the AT-01/WI-5763 finalizer
   lane, packet-recovery actor field in WI-5694 — given WI-5763 holds GO
   with `write_verdict.py` and the sweep rule file in its declared
   target_paths? Alternative: accept cross-thread target overlap and land
   the trailer emission here.
3. Does the cutoff-gated WARN design for finding (c) (OD-B/OD-C defaults)
   hold as the right interim posture, or must the attribution tripwire land
   only after the write-side lane ships to avoid a window where (c) can
   never fire truthfully?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
