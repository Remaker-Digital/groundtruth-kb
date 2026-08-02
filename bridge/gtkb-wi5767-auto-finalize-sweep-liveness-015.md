REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher/TAFE deliberately disabled
author_metadata_source: explicit_owner_direction

bridge_kind: prime_proposal
Document: gtkb-wi5767-auto-finalize-sweep-liveness
Version: 015
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5767-auto-finalize-sweep-liveness-014.md
Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5767
target_paths: ["scripts/auto_finalize_sweep.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", ".claude/skills/gtkb-bridge-propose/helpers/write_bridge.py", ".codex/skills/gtkb-bridge-propose/helpers/write_bridge.py", ".codex/skills/MANIFEST.json", "config/agent-control/gtkb-harness-capability-registry.toml", "platform_tests/scripts/test_doctor_auto_finalize_sweep_liveness.py", "platform_tests/hooks/test_auto_finalize_verified_verdicts.py", "platform_tests/skills/test_bridge_propose_helper.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Revised Proposal — WI-5767 Pre-Existing Managed-Projection Drift Stop

## Revision Claim

Prime Builder accepts GO-014 and performed the exact implementation-admission
checks required by proposal v009 before editing any of its seven targets. The
read-only managed-adapter generator check failed:

```text
python scripts/generate_codex_skill_adapters.py --check
Codex skill adapters: would update 2 file(s)
- .codex/skills/MANIFEST.json
- config/agent-control/gtkb-harness-capability-registry.toml
```

Both reported files are outside v009's seven-path authorization and are Git
clean, proving pre-existing projection drift rather than an implementation
diff created by WI-5767. V009 expressly requires implementation to stop and
return through another append-only revision when this condition exists.
Accordingly, Prime Builder made no source, test, generated-projection,
configuration, dispatcher/TAFE, Git, or external-state mutation.

This revision preserves the approved functional design and expands the cohort
to the exact nine paths the canonical generator transaction requires. The two
shared metadata files are added so the generator may atomically normalize the
stale `gtkb-verify` source hash and record the new `gtkb-bridge-propose` helper
projection. This is deterministic forced normalization, not permission to
adopt other manifest or registry changes. Hand-editing generated state remains
forbidden.

## Admission Evidence And Provenance

- `.claude/skills/gtkb-verify/SKILL.md` is canonical at SHA-256
  `d0f13dc12f946f44c8a1536d3734d64e85c35c5a3bdaa5789a96cbf4c965d1e4`.
- `.codex/skills/gtkb-verify/SKILL.md` already declares that exact canonical
  source hash in its generated adapter header.
- `.codex/skills/MANIFEST.json` and the Codex `skill.verify` capability entry
  in `config/agent-control/gtkb-harness-capability-registry.toml` still record
  stale source hash
  `9d54afdc92f5ad5e20650fd7f1da72187816daf8975805dedfb30e1d7d4e5f1f`.
- All four files are Git clean. Their last joint history touch is custodial
  sweep commit `02e12e7b0e1a1172ea8acf1b9a99e2ee9b8e54af`, which changed both
  canonical and Codex `gtkb-verify` skill bytes but did not land matching
  manifest/capability hashes.
- `.codex/skills/MANIFEST.json` is clean at Git blob
  `f7fe3458` and raw SHA-256
  `1f025059`; the capability registry is clean at Git blob `ce1473da` and raw
  SHA-256 `ed6d8b62`. Full hashes must be recomputed in the fresh start packet;
  these prefixes identify the observed admission baseline without creating a
  stale authorization shortcut.
- Open WI-5093 already tracks the systemic generator/registry source-hash
  synchronization class. It currently has no parent project and cannot inherit
  implementation approval. WI-5767 absorbs only this exact observed
  `gtkb-verify` normalization in its active approved project; it neither
  implements nor silently approves WI-5093's broader systemic change.

The drift is a managed-projection partial-commit and atomicity defect, not
evidence against the WI-5767 functional design. Because the active Prime
Builder role cannot author the Loyal Opposition `ADVISORY` status, this
revision preserves the complete report evidence and routes it for independent
advisory disposition; it does not counterfeit an LO artifact. A duplicate
systemic WI is not created because WI-5093 already tracks the class.

## Explicit Preconditions For A Later Start

1. Independently review and approve this exact nine-path revised cohort.
2. Re-read all nine targets and require no foreign ownership or competing
   claim; mint fresh full preimage hashes in the start packet.
3. Acquire a new exact-session nine-path implementation claim and mint a fresh
   schema-v3 start packet. GO-014 and the current packet are historical after
   this REVISED entry.
4. Run the canonical generator in write mode only after the authorized helper
   edit. Require its entire output to remain within the Claude helper, Codex
   helper, Codex manifest, and capability registry. Any other output stops
   implementation and returns through another revision.
5. Inspect the shared-file hunks: only the expected `gtkb-bridge-propose` entry
   update and stale `skill.verify` source-hash normalization are admissible.
6. Re-run `python scripts/generate_codex_skill_adapters.py --check` and require
   exit 0 with no remaining generated-path updates.

## Retained Seven-Path Functional Design

### C1 — Read-only sweep probe and additive actor attribution

Add an opt-in `--probe` mode to `scripts/auto_finalize_sweep.py`. It must reuse
the sweep planner in dry-run mode and emit schema-versioned JSON containing the
terminal backlog, would-finalize cohort, blocked cohort, and skip-reason
histogram. Probe mode must not commit, append audit rows, alter bridge state, or
change normal Stop-hook behavior. Normal execution continues to drain stdin,
honor its disable control, fail soft, and exit zero.

Every normal audit row gains best-effort actor context: a stable source label,
process ID, and only available normalized harness/session identifiers with
their provenance. Missing identity variables never block audit append or sweep
execution.

### C2 — Doctor liveness and attribution check

Add the required `auto_finalize_sweep_liveness` doctor check. It reuses the
existing WI-4871 terminal-VERIFIED backlog enumeration and invokes the probe
with the active interpreter, bounded execution, no shell, and fail-soft JSON
handling.

- Empty terminal backlog is PASS.
- A non-empty backlog with insufficient or stale observation is WARN.
- A non-empty backlog with at least the configured observation window and zero
  finalize actions is FAIL.
- Post-cutoff commits that add finalizing VERIFIED verdicts without a recognized
  finalization trailer or matching audit attribution are WARN.
- Missing Git/audit/probe evidence is diagnostic and must not crash doctor.

The observation window, recency, probe deadline, commit scan cap, and
attribution cutoff must use the project's central timer/threshold configuration
surface or documented environment controls; no new anonymous hard-coded timer
is introduced. This implements the owner's timer/configuration SoT direction
without expanding into unrelated timer repairs.

### C3 — Direct helper usage contract

Give canonical `.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py` a
module CLI surface without changing imports, `__all__`, or public signatures:

- `--help` and `-h` write usage to stdout and exit 0;
- bare or other direct invocation writes usage to stderr and exits 2;
- usage identifies `propose_bridge()`,
  `propose_bridge_codex_non_bypass()`, the version-1-only constraint,
  `BridgeFileAlreadyExistsError`, and governed append/verdict/advisory routes.

Project that canonical change through the managed generator. The two helper
bytes must remain exact, and the generated manifest/registry transaction may
contain only the explicitly admitted helper metadata plus the exact stale
`skill.verify` source-hash normalization.

## Cross-Harness Disposition

The sweep script is the same shared script registered for Claude and Codex;
this proposal changes neither registration. The bridge-propose helper has one
canonical Claude source plus a separately tracked generated Codex projection,
both explicitly in scope. Claude and Codex require exact behavioral and byte
parity, proven by the helper suite and the Codex adapter generator.

The Codex manifest and shared capability registry are generator-owned parity
metadata, not independent behavior forks. Their admissible change is limited
to the `gtkb-bridge-propose` projection metadata plus exact normalization of
the already-current `gtkb-verify` canonical source hash. Antigravity's existing
skill adapter, Cursor's registered fallback, and provider harness surfaces do
not have a separately targeted helper module in this change; their documented
capability dispositions remain unchanged. Doctor and the three test modules
are harness-neutral. No typed parity waiver is requested.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-WI5116-PHASE1-SWEEP-DIAGNOSIS-20260709` — zero-finalize diagnosis.
- `DELIB-202667698`, `DELIB-202667699`, `DELIB-202667700` — owner-selected
  liveness window, interim severity, and attribution cutoff.
- `DELIB-202667710` — current Advisory Corrections program authority.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` — project-only
  approval inheritance; a projectless WI cannot be implementation-approved.
- `DELIB-20260801-GTKB-TIMER-CONCURRENCY-CONFIG-SOT-DIRECTIVE` — centralize
  timers, thresholds, throttles, fan-out, and concurrency controls and tune
  them from evidence.

## Owner Decisions / Input

No new owner decision is required to review WI-5767's exact nine-path revision;
its parent project already carries active authority. WI-5093 remains a separate
projectless systemic backlog item and must be routed as a one-at-a-time AUQ
before anyone implements its broader scope. That AUQ is queued behind the
already-outstanding owner decision and is not duplicated here.

## Requirement Sufficiency

The functional requirements are sufficient. The prior seven-path scope was not
implementation-admissible because the mandatory managed-projection baseline
failed. This nine-path revision makes the generator transaction complete
without weakening parity or granting broad shared-file authority.

## Specification-Derived Verification Plan

| Requirement | Verification | Required result |
| --- | --- | --- |
| Projection atomicity | Generator output plus exact manifest/capability hunk inspection | Only `gtkb-bridge-propose` metadata and stale `skill.verify` source hashes change; final check exits 0. |
| Scope containment | Scoped status/diff/numstat against the nine targets | No undeclared path or unrelated shared-file hunk is adopted. |
| Probe read-only behavior | Focused sweep tests compare HEAD/audit/bridge state before and after probe | Required JSON is emitted with zero mutation. |
| Liveness classifications | New doctor suite covers empty, stale, insufficient, zero-drain, healthy, attribution, and Git-unavailable states | PASS/WARN/FAIL exactly match the retained design. |
| Helper CLI and parity | Subprocess help/error tests, import silence, byte equality, generator check | Streams/exit codes are exact; helper APIs and parity remain intact. |
| Engineering quality | Three focused pytest suites, generator parity, Ruff check, Ruff format check, `git diff --check` | All pass on exactly nine paths. |
| Governed lifecycle | Fresh applicability/clause preflights, GO, claim, start packet, implementation report, independent verification | No stale GO, packet, or approval is reused. |

## Risk, Rollback, And Scope Boundary

The primary risk is a generator run silently absorbing unrelated managed-skill
metadata. Exact hunk admission plus the nine-path allowlist bounds that risk.
Before a later implementation, rollback is claim release and another
append-only revision. After implementation, rollback is a separately governed
revert of only the nine-path cohort.

No WI-5767 source/test/helper change was made in this cycle. No project,
backlog, PAUTH, packet, dispatcher/TAFE, credential, Git index/history,
deployment, release, cleanup, or external-system state is changed by this
revision beyond its governed bridge publication and automatic claim release.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
