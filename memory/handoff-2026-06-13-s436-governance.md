# Handoff: S436 Governance Session (TAFE close-out + CQ baseline + Role-Authority model)

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c76b3a89-6bf6-4836-b44e-681ee94a2aef
author_model: claude-fable-5
author_model_version: 5
author_model_configuration: default

Supersedes the "DO NEXT" of `memory/handoff-2026-06-12-tafe-program-drive.md`
(TAFE Phase 0 is now VERIFIED; that file remains valid history).

## Standing owner directives (carry forward)

1. **Drive `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE` (TAFE) to completion**, multi-session, with strong continuity. Phase 0 is done; later phases remain.
2. **Collect owner decisions via AskUserQuestion ONLY.** The owner explicitly enjoys AUQ — use them liberally; bring contentious details forward as AUQ walkthroughs (as done for the CQ SPEC/DCL).
3. **NEW — Role authority is owner-DECLARED, not agent-DETECTED** (now canonical: `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001`, `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001`, `DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613`). Two-layer model: a running session's role ← the explicit hint in the first lines of its session envelope (AUTHORITATIVE); absent a hint, the harness registry is informative fallback. The dispatcher routes by the registry (authoritative) deterministically. **Agents WARN + SUGGEST about non-functional/suspended/mismatched registry entries but MUST NOT override the declaration or invalidate/park work on that basis (DCL R5).** This corrects the S436 harness-C over-detection — do not repeat it.

## Paste-ready continuation prompt

Send `::init gtkb pb` first, wait for the startup disclosure, then paste:

---

Continue work on GroundTruth-KB platform. Location: E:\GT-KB. Branch: develop.
Role: Prime Builder (harness B). Standing directives: drive TAFE to completion;
AUQ-only owner decisions; apply the declared-not-detected role model (warn, never
invalidate, on registry mismatch).

READ FIRST (routing context, NOT state truth — verify by fresh reads):
1. memory/handoff-2026-06-13-s436-governance.md — this file; full S436 state + gates.
2. bridge/INDEX.md (live) — but note INDEX is being CLOBBERED by a concurrent
   session's rewrites; trust the bridge FILES + git log over INDEX for terminal
   state. Use `git log --oneline -20` to see recent VERIFIED verdicts.
3. DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001 (MemBase) — the role-resolution
   rules that now govern; R5 = no-invalidation-on-registry-mismatch-alone.

STATE AT S436 END (2026-06-13 — verify before acting):
- ALL VERIFIED/terminal: gtkb-tafe-spec-promotion (8 SPEC-TAFE specs now
  `specified`), gtkb-tafe-backlog-reconciliation, gtkb-tafe-phase-0-enablement
  (@ -007; PAUTH-...-WI-4487-4491 created, WI-4487..4491 enriched to
  approval_state=auq_resolved, spec links + implementation_order set),
  gtkb-gov-code-quality-baseline-formal-artifact-approval (@ -010; 4 CQ artifacts
  GOV/ADR/SPEC/DCL inserted), gtkb-role-authority-declared-not-detected (@ -004;
  ADR + DCL inserted).
- New MemBase governance artifacts (all v1 specified): GOV-CODE-QUALITY-BASELINE-001,
  ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001, SPEC-CODE-QUALITY-CHECKLIST-001 (11 CQ-*
  rules incl. owner-added CQ-PERF-001 + CQ-DEPS-001), DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001
  (N/A requires LO concurrence), ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001,
  DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001.
- Owner DELIBs this session: DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612,
  DELIB-TAFE-PHASE-0-ENABLEMENT-GO-DEFERRAL-20260612 (superseded by re-activation),
  DELIB-CQ-BASELINE-CEREMONY-RELEASE-20260613,
  DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613.
- Backlog captured: WI-4513 (impl-start gate author-role-blind, P2), WI-4515
  (harness-C LO self-label vs prime-builder/suspended registry — reconcile, P2),
  WI-4517 (reconcile duplicate CQ Slice-2 tracking WIs + set source_spec_id, P3).
- WORKING TREE UNCOMMITTED: all S436 bridge files, the live groundtruth.db
  mutations (6 new specs + 5 WI enrichments + 4 DELIBs + 3 backlog WIs), the
  approval packets under .groundtruth/formal-artifact-approvals/, and the
  .gtkb-state/ ceremony scripts. Commit is owner-gated (no sweep-commit yet).

DO NEXT (each through its own gate):
1. INDEX REPAIR (bridge integrity, top priority once concurrency settles): the
   concurrent session's INDEX rewrites dropped terminal entries for
   gtkb-tafe-phase-0-enablement, gtkb-tafe-spec-promotion, and
   gtkb-role-authority-declared-not-detected. Files persist; re-add their latest
   VERIFIED lines to bridge/INDEX.md (use the gtkb-index-agent-edit-serialization
   CLI if landed, else fresh-read-immediately-before-edit). Confirm no NON-terminal
   entries were lost.
2. Two GO advisory-disposition threads (gtkb-dashboard-operations-cockpit-advisory-disposition,
   gtkb-propose-scaffold-validation-gap-advisory-disposition) — Prime-actionable but
   likely the concurrent session's; confirm ownership before acting.
3. TAFE Phase 1+: WI-4487 flow_definitions implementation proposal (resolve F5:
   stage_attempts/stage_leases/agent_capability_snapshots schema home; compatibility_views
   NOT canonical per CX7). Then WI-4488 → 4489/4490/4491. Each via propose→GO→impl→report→VERIFIED.
4. Follow-ons: WI-4513/4515/4517; implement the DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001
   R1-R5 assertion-enforcement code (separate proposal); offer the owner a sweep-commit.

CONSTRAINTS (standing): INDEX canonical (but clobber-prone under concurrency);
formal artifacts need owner approval packets; AUQ is the only owner-decision channel;
declared-not-detected (warn, never invalidate on registry mismatch); never remove
protected behaviors.

---

## Gate mechanics verified in S436 (reuse; saves a blocked-write cycle each)

- **Reusable formal-artifact ceremony driver:** `.gtkb-state/cq_baseline_ceremony.py`
  (modes `packet|insert|verify`) reads a data JSON via `GTKB_CEREMONY_DATA` env var
  (default = cq data). Data file holds per-artifact {artifact_id, artifact_type,
  spec_type, title, status, source_ref, approval_question, approval_answer, body
  or body_file}. Large bodies live in files (e.g. `.gtkb-state/role_bodies/*.md`,
  `.gtkb-state/cq_bodies/*.md`) and are read byte-exact via `body_file`. Packet
  filename = `<packet_date>-<artifact-id-lower>.json`.
- **Formal-artifact inserts are gated by the per-artifact APPROVAL PACKETS, not the
  impl-start packet.** The impl-start gate (`implementation_authorization.py begin`)
  REFUSES while a thread is DEFERRED and is NOT the gate for formal GOV/ADR/DCL/SPEC
  mutation (codex-review-gate says so). Inserts run via the `.gtkb-state` driver
  (which avoids the impl-start-gate false-positive) with `GTKB_FORMAL_APPROVAL_PACKET`
  set per insert. This is how the CQ ceremony ran inserts while the thread was still
  DEFERRED, then filed the report to clear it.
- **DEFERRED is a self-sealing park:** both auto-dispatch AND manual Codex scans skip
  DEFERRED/ADVISORY/WITHDRAWN/VERIFIED. A "DEFERRED pending Codex GO" thread CANNOT
  self-clear (only an LO sets GO) — it must be owner-directed re-activated to
  NEW/REVISED first. (TAFE enablement needed a concurrent session to REVISE it.)
- **Bridge claim before any bridge Write:** `python scripts/bridge_claim_cli.py claim
  <slug> --session-id <UUID>`, UUID = NEWEST transcript in ~/.claude/projects/E--GT-KB/*.jsonl
  (NOT the CLAUDE_CODE_SESSION_ID env var). Re-claim before each post-filing edit; TTL 10 min.
- **implementation_report bridge_kind** requires line-start `Project Authorization:` /
  `Project:` / `Work Item:` metadata; use `governance_advisory` (metadata-exempt) for
  formal-artifact-creation reports with no PAUTH (as the role-authority -003 report did).
- **Concurrency:** TWO+ interactive Claude PB sessions ran on shared worktree/git index.
  INDEX read-modify-write loses updates. Mitigation: fresh-read bridge/INDEX.md
  IMMEDIATELY before each edit; expect your entries to sometimes be clobbered (re-add).
  Trust bridge files + `git log` over INDEX for terminal state.
- **Validator + verify:** `scripts/validate_formal_artifact_packet.py <packet>` per packet;
  driver `verify` mode asserts row.description == packet.full_content + hash match.
- **Decision capture:** `.gtkb-state/record_*.py` drivers call the decision-capture helper
  (`.claude/skills/decision-capture/helpers/record_decision.py`); fixed
  source_type=owner_conversation, outcome=owner_decision.

## Session outcome summary

S436 closed out TAFE Phase 0 (spec promotion + reconciliation + enablement, all
VERIFIED), ran two full formal-artifact ceremonies (CQ baseline 4 artifacts; role
authority 2 artifacts), and — most importantly — formalized the owner's
declared-not-detected role-authority model after catching (and the owner correcting)
a harness-C over-detection. The model now governs and is Codex-verified. The one
open integrity item is INDEX-clobber repair, deferred until the concurrent session
settles.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
