# Slice Progression and Follow-On Plan

**Authority:** `bridge/gtkb-push-gate-design-governance-review-004.md` (Codex GO on REVISED-3)
**Sequencing assumption:** Option A (clean-then-enable; recommended per `cleanup-sequencing-analysis.md`)
**Owner-decision gating:** Slices 1+ implementation cannot file until the `gtkb-push-gate-design-contract-final` thread lands VERIFIED. That thread itself cannot file until the 5 deferred owner decisions in `open-decisions-and-aauq-plan.md` are answered.

## Slice Inventory

| Slice | Purpose | Proposed Bridge Slug | target_paths | Gated By |
|---|---|---|---|---|
| 0 | Decision-ready design packet (THIS slice) | `gtkb-push-gate-design-governance-review` | `docs/design/push-gate/**` | n/a (originating) |
| Final-Contract | Lock 5 deferred decisions into binding design | `gtkb-push-gate-design-contract-final` | `docs/design/push-gate/2026-MM-DDTHH-MMZ-final/**` | All 5 AUQs answered; this Slice 0 VERIFIED |
| 1 | Canonical `gt push-gate` CLI scaffold + cache substrate | `gtkb-push-gate-slice-1-cli-scaffold` | `groundtruth-kb/src/groundtruth_kb/cli.py`, `groundtruth-kb/src/groundtruth_kb/push_gate/**`, `tests/push_gate/**` | Final-Contract VERIFIED |
| 1.5 | Minimum-viable debt-discovery audit script | `gtkb-push-gate-slice-1-5-debt-audit` (already filed at NEW-001 / NO-GO-002) | `scripts/push_gate_audit.py`, `platform_tests/scripts/test_push_gate_audit.py`, `.gtkb-state/push-gate/audits/**` | Slice 1 VERIFIED (per Codex NO-GO-002 P1-001 sequencing) |
| 2 | Layer 2 AST checkers (hardcoded-externals, SHA, magic-number, import-topology) | `gtkb-push-gate-slice-2-ast-checkers` | `groundtruth-kb/src/groundtruth_kb/push_gate/ast/**`, `tests/push_gate/ast/**` | Slice 1 VERIFIED |
| 3 | **Debt cleanup phase.** All inventoried defects fixed under normal cadence. | `gtkb-push-gate-slice-3-debt-cleanup-batch-NN` (multiple batches) | varied by batch | Slice 1.5 VERIFIED + Slice 2 VERIFIED |
| 4 | Layers wired into local `.githooks/pre-push` (audit mode initially) | `gtkb-push-gate-slice-4-prepush-wiring` | `.githooks/pre-push`, `scripts/install_push_gate_hook.py`, `tests/push_gate/test_prepush_wiring.py` | Slice 3 inventoryreport-clean |
| 5 | Flip pre-push from audit-only to mechanical blocker | `gtkb-push-gate-slice-5-mechanical-blocker` | `.githooks/pre-push`, config flag in `config/push-gate/runtime.toml` | Slice 4 VERIFIED |
| 6 | GitHub Actions workflow + branch protection | `gtkb-push-gate-slice-6-ci-integration` | `.github/workflows/push-gate.yml`, `scripts/sync_branch_protection.py` | Slice 5 VERIFIED; owner Q3/Q4 answers honored |
| 7 | Final hardening (cache lifecycle, owner-override path, edge cases) | `gtkb-push-gate-slice-7-hardening` | `groundtruth-kb/src/groundtruth_kb/push_gate/cache/**`, `groundtruth-kb/src/groundtruth_kb/push_gate/override/**`, tests | Slice 6 VERIFIED; owner Q2 answer honored |

## Sequencing Dependencies

```
Slice 0 (this packet)
   │
   ├── Owner answers 5 AUQs (via open-decisions-and-aauq-plan.md)
   │
   └── Final-Contract thread (locks design)
          │
          ├── Slice 1 (CLI scaffold + cache substrate)
          │      │
          │      ├── Slice 1.5 (audit-only mode; produces inventory)
          │      │
          │      └── Slice 2 (AST checkers)
          │             │
          │             └── Slice 3 (debt cleanup, multiple batches)
          │                    │
          │                    └── Slice 4 (pre-push wiring; audit mode)
          │                           │
          │                           └── Slice 5 (mechanical blocker flip)
          │                                  │
          │                                  └── Slice 6 (CI integration)
          │                                         │
          │                                         └── Slice 7 (hardening)
```

## Owner-Decision Checkpoints

Each checkpoint requires an AskUserQuestion-answered owner decision before the corresponding slice can file:

| Checkpoint | Question | Affected Slices |
|---|---|---|
| AUQ-1 | Cleanup sequencing — Option A or Option B? | Slice 3 timing relative to Slices 4-5 |
| AUQ-2 | Override path scope | Slice 7 design |
| AUQ-3 | Multi-platform CI | Slice 6 workflow shape |
| AUQ-4 | PR-vs-push gating scope | Slice 6 workflow trigger config |
| AUQ-5 | Test impact analysis dependency | Slice 1 cache substrate + Slice 3 test execution shape |

All 5 are surfaced in `open-decisions-and-aauq-plan.md` with structured packets.

## Slice 1.5 Special Status

Slice 1.5 was filed in parallel with Slice 0 (NEW-001) under the original assumption of structural independence. Codex's NO-GO at `bridge/gtkb-push-gate-slice-1-5-debt-audit-002.md` P1-001 clarified that **Slice 1.5 is sequencing-gated by Slice 0**: it is an implementation slice, and Slice 0's GO authorizes ONLY the design packet, not follow-on implementation. Slice 1.5 must wait for:

1. This Slice 0 packet to land VERIFIED.
2. The `gtkb-push-gate-design-contract-final` thread to land VERIFIED.

Until both gates pass, Slice 1.5 REVISED-3 is parked at NO-GO. The minimum-viable audit script implementation is sound; the bridge file just sits in NO-GO state until sequencing unblocks.

## Estimated Cadence

Pure estimate, owner-revisable:

- Slice 0 VERIFIED: 1 session.
- 5 AUQ answers: 1 session.
- Final-Contract thread (NEW → GO → impl → VERIFIED): 1-2 sessions.
- Slice 1 (CLI scaffold + cache substrate): 2-3 sessions (substantive work).
- Slice 1.5 (audit-only): 1 session (small).
- Slice 2 (AST checkers): 2 sessions.
- Slice 3 (debt cleanup): unknown until inventory lands; estimate 2-5 sessions.
- Slice 4 (pre-push wiring audit mode): 1 session.
- Slice 5 (mechanical blocker flip): 1 session (mostly verification).
- Slice 6 (CI integration): 2 sessions.
- Slice 7 (hardening): 2-3 sessions.

Total estimated: 15-22 sessions. Real cadence depends on debt inventory volume and parallel-session interleave with other GT-KB work.

## Backward Compatibility With Existing Surfaces

The push gate's slice progression must preserve compatibility with existing GT-KB infrastructure:

- **`gt project doctor`** (SPEC-DSI-DOCTOR-CHECK-001) — Slice 4-5 add `push_gate` invariants to doctor; existing invariants unchanged.
- **`gt secrets scan`** (SPEC-SEC-SCANNER-CLI-001) — Slice 5 (Layer 5) wraps the existing CLI; the CLI itself is unchanged.
- **`gt github security doctor`** (SPEC-SEC-GITHUB-POSTURE-001) — Slice 6 registers the push-gate workflow as a required check via this doctor's existing branch-protection invariants; no change to the doctor's other invariants.
- **`release-candidate-gate` skill** (GOV-RELEASE-READINESS-GOVERNED-TESTING-001) — Slice 6 (Layer 7) wraps the existing skill; the skill itself is unchanged.
- **`.githooks/pre-commit`** (SPEC-SEC-HOOK-PORTABILITY-001) — Slice 4 adds `.githooks/pre-push` under the same `core.hooksPath` invariant; existing `pre-commit` is unchanged.
- **`bridge/INDEX.md`** (GOV-FILE-BRIDGE-AUTHORITY-001) — INDEX remains canonical workflow state across all slices; no change to bridge protocol itself.

## Out-of-Scope Surfaces (Explicit Non-Coupling)

These existing GT-KB surfaces are explicitly NOT coupled to the push gate (they remain governed by their own specs):

- Smart-poller / cross-harness event-driven trigger — bridge dispatch is separate from push-gate.
- AUQ-only owner-decision enforcement stack — AUQ enforcement is separate.
- MemBase append-only versioning — KB writes are governed by KB-specific gates.
- Dashboard / KPI rollup — observability surface; push gate emits structured data the dashboard may consume but does not depend on.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
