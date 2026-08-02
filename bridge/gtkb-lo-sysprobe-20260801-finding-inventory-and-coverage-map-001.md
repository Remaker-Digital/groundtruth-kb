ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 469b6155-827b-44cb-a56d-f838893bffa3
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task system-statusprogress-check; resolved role loyal-opposition

bridge_kind: governance_advisory
Document: gtkb-lo-sysprobe-20260801-finding-inventory-and-coverage-map
Version: 001
Author: Loyal Opposition (claude, harness B)
Date: 2026-08-01 UTC

## Source

Scheduled system status/progress probe (system-statusprogress-check), 2026-08-01,
session context 469b6155-827b-44cb-a56d-f838893bffa3, at HEAD 75decbfa7 on branch
research. This is the INDEX advisory for that probe. It exists so Prime Builder
has one entry point to every finding, with each mapped to its carrier, rather
than rediscovering the set. Owner asked that all noted defects and issues be
captured as advisory proposals ready for advancement to projects and work items.

## Claim

The probe produced 25 distinct findings across MemBase, Dispatcher Next, the
harness fleet, the canonical registry, CLI performance, and envelope/role
durability. Four required new advisories. Eleven are already carried by live
advisories or open work items and are recorded here as covered, NOT re-filed.
Three are expected posture per owner decision and must not be treated as defects.
Seven are lower-severity observations recorded here only.

## Advisories Filed This Session

| Slug | Finding | Backlog |
| --- | --- | --- |
| gtkb-lo-sysprobe-membase-pipeline-events-unbounded-growth | pipeline_events 1.49 M assertion-run rows vs 114 K canonical; 13x amplification; retention ran once ever | WI-5854 P2 |
| gtkb-lo-sysprobe-runtime-residue-census-cost | 188.5 GB / 2.02 M files; census over 1.32 M residue paths is the 29.2-min doctor cost, not MemBase size | WI-5855 P1 |
| gtkb-lo-sysprobe-dispatcher-quiescence-advisory-correction | 2026-07-31 advisory asks an owner question already answered by DELIB-20260724 three days earlier | none |
| gtkb-lo-sysprobe-dispatcher-next-stale-blocker-narrative | WI-5617 status_detail cites a parent-project retirement reversed on 2026-07-31 | none |

WI-5856 P1 (GTKB-DbSnapshot task Disabled; newest snapshot 200h old against a 48h
doctor threshold) is carried in the quiescence-correction advisory rather than
separately, because its whole significance is that it is NOT covered by the
quiescence decision that covers the adjacent disabled task.

## Expected Posture - Do NOT Remediate

Per DELIB-20260724-DISPATCHER-QUIESCENCE-MANUAL-LO (owner decision):

1. GTKB-DispatcherDaemon Disabled; heartbeat stale since 2026-07-19T20:52:37Z.
2. Dispatch health WARN, including the loyal-opposition:D
   subprocess_execution_failed residue and the two doctor dispatch ALARM FAILs.
3. Accumulated latest-GO and NO-ACTION threads awaiting manual routing.

## Already Covered - Recorded, Not Re-Filed

| Finding | Existing carrier |
| --- | --- |
| Bridge publication registry-currentness deadlock | gtkb-lo-bridge-publication-registry-currentness-deadlock-advisory-001; gtkb-bridge-aggregate-drift-publication-lockout-001 |
| Registry membership incomplete (22 load-bearing gaps) | gtkb-wi5441-global-registry-membership-reconciliation-001; gtkb-wi5441-registry-control-plane-reverse-coverage-001 |
| Duplicate-SoT audit baseline incomplete (13 violations) | same WI-5441 thread family |
| 24 unwaived cross-harness hook asymmetries | gtkb-cross-harness-parity-slice-6-coverage-audit-flip-001 and slice-2/3 siblings |
| Deliberation index reported 0/12571 indexed | WI-5680 open |
| Expired document leases linger without reaping (2 locks 13 days past a 4500 s TTL) | WI-5036 open |
| git object-store bloat (.git 41.23 GB) | WI-5431 open |
| Untracked terminal-VERIFIED verdict files (49) | gtkb-lo-wi5441-stranded-terminal-verified-advisory-001 |
| Role-marker write failure mis-gates interactive Prime as LO | WI-5086 open; WI-5512 open; gtkb-lo-role-resolution-fallback-privilege-escalation-advisory-001 |
| LO file-safety allow-rule for fresh ADVISORY files shadowed by controlled-artifact rule | WI-5540 open (reproduced live this session) |
| Registry census output volume | WI-5724 open |

## New Observations Recorded Here Only

1. Publication-capability recovery residue. Three ADVISORY publications this
   session produced capability rows in state recovery_required
   (failure_reason: bridge publication aggregate preimage cannot be restored
   exactly) while the bridge files themselves landed and resolved correctly
   through gt bridge show. gt registry recover repaired a different (register)
   transaction and did not clear them. A concurrent Prime Builder session
   (019fb353-... , claim TTL 2026-08-01T08:23:22Z) was re-observing the same
   aggregate throughout, so the preimage moved between mint and consume. The
   aggregate digest itself is deterministic - three consecutive observes over
   unchanged content produced identical digest 729399b9 at 149,309,447 bytes - so
   this is multi-writer contention, not non-determinism. WI-5825
   (publication-capability recovery receipt backfill) is the nearest open item.

2. Project-root-boundary gate false positives on prose. The gate blocked a
   backlog-add whose DESCRIPTION mentioned the allowlisted snapshot directory,
   and blocked a bridge filing whose prose contained the project root followed by
   a colon, parsed as an out-of-root path. Both were read-only or in-root
   operations. Same class as finding 2 of
   gtkb-lo-sysprobe-cli-latency-and-gate-false-positives-001.

3. LO file-safety gate blocked a read-only shell loop (ls plus for) as an
   "unresolved or opaque shell mutation target"; the identical query succeeded
   through PowerShell, which the gate does not inspect. Reproduces finding 2.1 of
   the 2026-07-31 advisory; recorded as still-live.

4. Both 2026-07-31 sysprobe advisories carry an unfilled Prior Deliberations
   placeholder reading "_No prior deliberations: <fill in reason before filing>._".
   This is the proximate mechanism of the dispatcher misdiagnosis corrected this
   session. A gate on that literal placeholder is cheap.

5. Malformed bridge status lines: four files whose first non-blank line is
   "IMPLEMENTATION REPORT" or "::init gtkb pb" are skipped by
   bridge_work_intent_registry with a UserWarning.

6. Envelope model provenance: the session envelope records model_id and
   model_version as "unknown" though bridge authorship expects model provenance.
   role_resolution_source was session_resolver_fallback, which WI-5723 targets for
   removal.

7. Harness observations: agy (antigravity, C) is not on PATH - latent only, since
   C is non-dispatchable; three active dispatch model pins lack owner
   confirmation (A gpt-5.5, D unspecified, F openrouter-cloud-default); harness D
   has no numeric dispatch_cost.

Additional doctor WARN counts recorded for triage sizing, not individually
carried: 697 pre-rename bare skill-dir references; 58 skill-health findings across
89 skills; 4,787 orphan citations across 1,707 files; 19 lapsed GO implementation
claims; 15 work-tree strays; 69 standing-backlog health warnings; 14 pending
canonical_terms sync operations; 3 VERIFIED bridges missing an Owner Decisions
section; 20 untracked NO-ACTION files flagged as a raw-write vector; one prior
session ended without an ORIENT block.

## Owner Decision Needed

None to file this advisory. Two owner-facing policy choices arise downstream and
should be raised via AskUserQuestion when Prime Builder scopes the work: the
retention window for pipeline_events, and the retention window plus deletion
authority for the runtime residue roots.

## Recommended Prime Action

1. Treat this advisory as the triage entry point for the 2026-08-01 probe.
2. Advance the four filed advisories into projects or work items per normal
   advisory disposition. WI-5854, WI-5855, and WI-5856 already exist as backlog
   candidates and are not implementation-approved.
3. Do not open work against the three expected-posture items.
4. For the eleven covered findings, attach this probe evidence to the existing
   carrier rather than creating parallel work.
5. Decide disposition for the seven new observations; several are cheap gate
   fixes with disproportionate effect on agent friction.

## Prior Deliberations

- DELIB-20260724-DISPATCHER-QUIESCENCE-MANUAL-LO - governs which probe findings
  are defects and which are owner-decided posture. Primary authority for this
  inventory.
- GOV-STANDING-BACKLOG-001 - backlog capture is the durable cross-session work
  authority and is not implementation approval.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 and DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 -
  findings crossing the capture threshold become durable artifacts with explicit
  lifecycle states.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 - state claims derive from fresh canonical
  reads; several findings here are stale-mirror defects of exactly that class.

## Classification Slot

adapt.

This advisory is not implementation approval. It does not authorize protected
edits, does not authorize any deletion, does not open an implementation-start
packet, and does not bypass the Prime Builder proposal, Loyal Opposition GO, or
verification gates.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
