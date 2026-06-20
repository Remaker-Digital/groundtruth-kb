NEW

# Correct the automation value/cost principle and re-correct the superseded poller-history framing

bridge_kind: prime_proposal
Document: gtkb-wi4682-automation-value-cost-principle
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-20 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 63d5063e-7f17-46be-9b91-d41960410cbe
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4682

target_paths: [".claude/rules/bridge-essential.md", ".claude/rules/canonical-terminology.md", ".groundtruth/formal-artifact-approvals/*-claude-rules-bridge-essential-md.json", ".groundtruth/formal-artifact-approvals/*-claude-rules-canonical-terminology-md.json", ".groundtruth/formal-artifact-approvals/*gov-automation-value-cost*.json"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

WI-4682 (first item of the release-gating PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH, owner-decision anchor DELIB-20265287) captures the owner's corrected automation value/cost principle and re-corrects the poller-history framing that currently carries the superseded version.

The corrected principle (verbatim owner framing in DELIB-20265287): **automation is wasteful only when it spends an EXPENSIVE resource — principally agent investigation tokens — without a commensurate chance of value.** The remedy is to gate the expensive action behind a CHEAP, deterministic check; it is NOT to avoid the cheap repetition. Avoiding negligible-cost work is itself a bad trade (the engineering to suppress it costs more than the work it saves). The governing question is always **relative value vs. cost, evaluated per action.** "Negligible" is contextual: frequency scales cost, so if a cheap check stops being cheap the same test re-applies to the check.

This proposal does three things:

1. **Create a new governance principle** `GOV-AUTOMATION-VALUE-VS-COST-001` recording the corrected principle as the citable source of truth, with machine-checkable assertions binding the corrected framing into the auto-loaded rule surfaces.
2. **Re-correct `.claude/rules/bridge-essential.md`** at the two passages DELIB-20265287 explicitly quotes as "incorrect and too broad": the Operational Mode passage ("The defect was blind repetition, not the ~50k tokens each spawn consumed") and the S308 Incident History Lesson ("blind, activity-independent automation — work repeated whether or not there is anything to do — is the defect ... The waste was work without information, not token volume").
3. **Re-correct `.claude/rules/canonical-terminology.md`** OS-poller glossary entry, which frames the defect as "polled blindly — waking the harnesses on a fixed interval regardless of bridge activity."

The corrected framing names the real defect: the S308 OS poller spent the expensive resource — woke a harness into a full ~50k-token investigation — UNCONDITIONALLY on every fixed-interval tick, with no cheap deterministic gate in front of the spawn. The fixed schedule itself was negligibly cheap (CPU/electricity); the cross-harness trigger's actionable-signature check is exactly the cheap gate the poller lacked.

**Supersession.** This work supersedes the framing established by the prior VERIFIED thread `gtkb-s358-w5-token-framing-correction` (anchor DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME; GO at DELIB-2284; VERIFIED at DELIB-2283). That S358 work (2026-05-18) corrected the wording away from a token-volume framing to a "blind/repetitive work is the defect" framing; DELIB-20265287 (2026-06-19) now deems THAT framing too broad and re-corrects it to the value-vs-cost framing. This is a deliberate, owner-authorized re-correction of governance narrative, implemented as new versions of the same protected surfaces — not a code rollback.

**Excluded:** `CLAUDE.md` (its current poller text is already neutral — line 74 names only the retired/archived status with no value/cost claim); the MemBase specifications S358 deferred (out of WI-4682 acceptance scope; the new GOV is the citable principle).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs this bridge proposal's authority and the dispatcher/TAFE + numbered-file workflow state it publishes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every governing spec; the gate it operationalizes is satisfied here.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the Project Authorization / Project / Work Item header triple is present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Spec-Derived Verification Plan below maps each linked spec to a verification check; the implementation report will carry executed evidence.
- `GOV-STANDING-BACKLOG-001` — WI-4682 is a MemBase work_items backlog item under the cited project and active PAUTH.
- `GOV-ARTIFACT-APPROVAL-001` — the new `GOV-AUTOMATION-VALUE-VS-COST-001` insert and each protected-narrative re-correction are gated by formal-artifact / narrative-artifact approval packets presented to and approved by the owner before the write.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — each protected narrative-file change clears the universal pre-commit narrative-artifact evidence floor only when its matching approval packet is staged.
- `config/governance/narrative-artifact-approval.toml` — the registry constraining narrative-artifact packet location, protected-path matching, and packet schema for the two `.claude/rules/*.md` files.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — this work preserves the corrected principle as a durable governance artifact rather than chat-only context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the corrected principle, its supersession lineage, and its verification are captured as traceable MemBase/Deliberation artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the supersession of the S358 framing (deferred/superseded/verified/retired lifecycle states) is recorded explicitly.

## Prior Deliberations

- `DELIB-20265287` — **owner-decision anchor.** Activity-Envelope Disposition, Autonomous Fan-Out Dispatch & Scope Isolation. Its "Corrected automation value/cost principle" section is the verbatim source of this work and explicitly directs the bridge-essential.md S308 re-correction as an approval-gated narrative edit. This proposal implements WI-4682, the first item it spawned.
- `DELIB-S358-TOKEN-CONCERN-IS-WASTE-NOT-VOLUME` — **superseded framing.** S358 owner clarification (2026-05-18) that the token concern is "waste, not volume / blind repetitive work." DELIB-20265287 re-corrects this as too broad. This proposal supersedes its framing while preserving the audit trail.
- `DELIB-2284` — Loyal Opposition GO on the S358 W5 correction (the prior implementation now being re-corrected). Cited so review sees the full lineage.
- `DELIB-2283` — Loyal Opposition VERIFIED on the S358 W5 correction. The current (now-superseded) rule-file wording is the output of this VERIFIED thread; re-opening it is owner-authorized by DELIB-20265287.

## Owner Decisions / Input

This proposal depends on owner approval, authorized by:

- `DELIB-20265287` (outcome=owner_decision, AUQ-backed, 2026-06-19): the corrected value/cost principle and the explicit directive to re-correct the bridge-essential.md S308 wording. This is the substantive owner decision authorizing WI-4682.
- AskUserQuestion (S 2026-06-20, this session): owner selected "Authorize all, drive autonomously" for WI-4682 → WI-4694, recorded as the basis for `PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-...-BOUNDED-IMPLEMENTATION-AUTHORIZATION` (active), citing DELIB-20265287.
- The two protected-narrative re-corrections and the new GOV insert remain individually gated: each requires an owner-approved narrative-artifact / formal-artifact approval packet at implementation time (per GOV-ARTIFACT-APPROVAL-001). The owner's drive-cadence choice does not waive those per-artifact approvals.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement is the owner decision `DELIB-20265287` (corrected value/cost principle) together with WI-4682's acceptance summary ("Governance record of the value/cost principle exists; bridge-essential.md S308 wording corrected; agents cite corrected framing"). No new or revised requirement is needed before implementation; the new `GOV-AUTOMATION-VALUE-VS-COST-001` is the *implementation artifact* recording the already-decided principle, not a new requirement to be elicited.

## Specification-Derived Verification Plan (spec-to-test mapping)

This is the specification-derived verification spec-to-test mapping. Because WI-4682 is governance + protected-narrative work with no source/runtime change, the "tests" are logical assertions (grep present/absent), packet-evidence checks, and the mandatory bridge preflights; the implementation report will carry the executed command evidence and observed results for each row.

| Linked spec / requirement | Verification check | Expected result |
|---|---|---|
| `DELIB-20265287` corrected principle → `GOV-AUTOMATION-VALUE-VS-COST-001` | `python -m groundtruth_kb deliberations`/`get_spec("GOV-AUTOMATION-VALUE-VS-COST-001")` returns a current `specifications` row, status `specified`, carrying assertions for the corrected framing | GOV exists, status=specified, assertions present |
| WI-4682 acceptance: "bridge-essential.md S308 wording corrected" | grep `.claude/rules/bridge-essential.md` for the superseded phrases ("blind repetition, not the ~50k tokens"; "waste was work without information, not token volume") | 0 matches (superseded phrases removed) |
| WI-4682 acceptance: corrected framing present | grep `.claude/rules/bridge-essential.md` + `.claude/rules/canonical-terminology.md` for the corrected framing (expensive-resource / cheap-gate / value-vs-cost-per-action) | >=1 match per file |
| `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` | `python scripts/check_narrative_artifact_evidence.py --staged` with the two protected files + their packets staged | PASS, both protected files cleared |
| `GOV-AUTOMATION-VALUE-VS-COST-001` formal packet | `python scripts/validate_formal_artifact_packet.py <packet>` for the GOV insert packet | packet valid, content hash matches inserted row |
| Bridge applicability + clause preflights | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4682-automation-value-cost-principle` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4682-automation-value-cost-principle` on the implementation report | preflight_passed: true; Blocking gaps: 0 |

The new `GOV-AUTOMATION-VALUE-VS-COST-001` will carry grep/grep-absent assertions binding the corrected framing into the auto-loaded rule files, so the principle is mechanically self-verifying after implementation (per the GT-KB assertion model).

## Risk / Rollback

- **Risk: re-opening VERIFIED governance narrative.** Mitigated by explicit owner authorization (DELIB-20265287 directs the correction) and by preserving the S358 audit trail (append-only narrative versions; the superseded deliberations remain). The Prior Deliberations section records the full lineage so future sessions see why the framing changed twice.
- **Risk: half-correction leaves auto-loaded surfaces self-contradictory.** Mitigated by scoping to all surfaces that currently carry the superseded framing (bridge-essential.md + canonical-terminology.md), mirroring S358's surface set minus CLAUDE.md (already neutral).
- **Risk: protected-narrative edit without owner-visible approval.** Mitigated by the mandatory per-file narrative-artifact-approval packets and the staged-evidence commit floor.
- **Rollback:** single-commit revert of the implementation commit (the two narrative re-corrections + the GOV packet + report) restores the prior S358 wording; the GOV insert is append-only and can be retired by a follow-on if the principle is later revised. No code or runtime behavior changes, so rollback carries no operational risk.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4682-automation-value-cost-principle`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`docs` — the change set is a new governance principle plus governance/rule narrative re-corrections; no source, test, or runtime behavior is added or modified. (Consistent with the S358 W5 correction, which was also `docs`.)

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
