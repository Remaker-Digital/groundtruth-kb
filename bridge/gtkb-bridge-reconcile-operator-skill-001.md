NEW

# Bridge Reconciliation Operator Skill + Runbook (WI-4237), with broken terminal-reconciliation shim repair

bridge_kind: prime_proposal
Document: gtkb-bridge-reconcile-operator-skill
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-20 UTC

author_identity: Prime Builder (Claude Code)
author_harness_id: B
author_session_context_id: 37181347-9803-42aa-b7d1-17587336e1e5
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: default (1m context)

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION
Project: PROJECT-GTKB-BRIDGE-RECONCILIATION
Work Item: WI-4237

target_paths: [".claude/skills/bridge-reconcile/**", ".codex/skills/bridge-reconcile/**", ".agent/skills/bridge-reconcile/**", ".api-harness/skills/bridge-reconcile/**", ".claude/skills/MANIFEST.json", ".codex/skills/MANIFEST.json", ".agent/skills/MANIFEST.json", ".api-harness/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "scripts/bridge_backlog_terminal_reconciliation.py", "platform_tests/scripts/test_bridge_reconcile_skill.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal implements **WI-4237** — a bridge reconciliation operator
skill and runbook — and repairs a prerequisite defect found while scoping it.

`PROJECT-GTKB-BRIDGE-RECONCILIATION` has already built the detection/correction
engine: the terminal-state sanity gate, the INDEX/file-chain deviation
detector, the triage-class correction-packet generator, and the hygiene-sweep
integration (project work items `WI-4234`, `WI-4235`, `WI-4236`, `WI-4238`) are
all **resolved** and are cited here only as completed sibling context, not as
this proposal's scope. The missing piece is the ergonomic operator surface —
**WI-4237 is open** — so reconciliation is run ad hoc and drifts between
sessions.

A 2026-06-20 session-start reconciliation of the live GO/ADVISORY queue
demonstrates the cost of that gap. Applying the canonical disposition matrix
(`groundtruth_kb.bridge.disposition`, status token **plus** `bridge_kind`) plus
a sibling-VERIFIED cross-check to the 70 actionable-status tops shows only a
minority are genuine open work: **19** are pre-cutover vestigial threads
(2026-04-20, `E:\Claude-Playground` era; work re-done and landed), **16** are
ADVISORY owner-disposition records, **6** are terminal-by-`bridge_kind` GO
records, and of **29** `lo_verdict` GOs roughly half are umbrella/scoping
threads stuck at GO while all their child threads are VERIFIED (e.g.,
`gtkb-harness-state-sot-consolidation-phase-1` GO with `-foundation` /
`-rule-files` / `-mirror-retirement` VERIFIED; `gtkb-platform-sot-consolidation-umbrella`
GO with `-slice-2a-read-discipline` VERIFIED; `gtkb-work-tree-hygiene-mechanism-scoping`
GO with `-slice-a-detector` VERIFIED). A read-only dry-run of
`scripts/bridge_verified_backlog_reconciler.py` examined **95** candidate work
items and auto-resolved **0**, every one skipped `linked_bridge_not_verified`
or `missing_parent_evidence`. The operator skill makes running the read-only
audit, classifying by triage class, generating one-class-at-a-time correction
packets, and presenting exactly one gated owner decision a repeatable governed
service rather than a per-session reconstruction — directly serving
`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`.

**Prerequisite defect.** `scripts/bridge_backlog_terminal_reconciliation.py`
(the terminal-state-audit compatibility entrypoint) does `from
bridge_reconciliation_audit import main`, but `bridge_reconciliation_audit.py`
exists **nowhere** in the tree (confirmed by repository-wide glob). The shim
therefore raises `ModuleNotFoundError` on invocation. Because the operator
runbook must cite working audit commands, repairing (or repointing) this shim is
in scope.

**Scope.**
1. Author `.claude/skills/bridge-reconcile/` (SKILL.md + runbook + optional
   helper) guiding the `audit -> classify -> select ONE triage class -> generate
   correction packet -> present exactly ONE owner decision -> preserve
   bridge/PAUTH/implementation-start gates before any mutation` flow; cite the
   concrete command names and state the no-bulk-mutation policy. Mirror to
   `.codex` / `.agent` / `.api-harness` via the skill-adapter generator and
   register in each `MANIFEST.json`.
2. Repair `scripts/bridge_backlog_terminal_reconciliation.py` so it delegates to
   the working reconciler entrypoint instead of the absent module.
3. Add a discoverability + shim-repair regression test.

**Out of scope (captured as a follow-on).** The engine-level fixes that would
let the reconciler *auto-resolve* the 95 stuck WIs — umbrella auto-closure
(close an umbrella thread to VERIFIED once all children are VERIFIED) and the
`missing_parent_evidence` strictness relaxation — are larger behavior changes to
the reconciler and are intentionally **not** bundled here. This proposal
delivers the operator surface that lets a human-gated operator perform those
closures correctly today, and recommends a sibling work item for the engine
work.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the skill reads and reasons over canonical
  TAFE/dispatcher bridge state plus the numbered file chain; it must preserve
  bridge-state authority and must not treat retired aggregate queue artifacts as
  canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — governs this
  proposal's own linkage completeness.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal cites the
  `WI-4237` / `PROJECT-GTKB-BRIDGE-RECONCILIATION` /
  `PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION` triple.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the discoverability and
  shim-repair tests derive from the WI-4237 acceptance criteria; the post-impl
  report will carry the spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` — the activity the skill operates on is backlog/WI
  terminal-state reconciliation; the skill must honor the MemBase `work_items`
  table as the canonical backlog authority and enforce the no-bulk-mutation +
  owner-gate policy on any correction.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — reconciliation moves bridge
  threads and work items through lifecycle states (verified, retired); the skill
  must preserve those lifecycle states as durable artifacts rather than discard
  them.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the triage classes the skill
  selects map to artifact lifecycle triggers (candidate, verified, retired); the
  runbook documents that mapping.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the operator skill treats
  the backlog and bridge as a network of durable artifacts, consistent with the
  ADR's core stance.

## Prior Deliberations

- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` — owner decision
  that bridge VERIFIED mechanically retires the parent backlog item. The
  operator skill operationalizes this for exactly the cases the automatic
  reconciler currently skips (`missing_parent_evidence` /
  `linked_bridge_not_verified`).
- `DELIB-2566` / `DELIB-20264911` — Stale Thread Closure Slice 3 (mid-chain
  NO-GO, later VERIFIED at `bridge/gtkb-stale-thread-closure-slice-3-impl-006.md`).
  This proposal does **not** re-litigate closure semantics or revive a rejected
  approach; it adds the ergonomic operator surface the prior slices lacked and
  wraps the already-VERIFIED tooling.
- `DELIB-20263854` — GTKB Bridge Skill Unified Slice 1+2 (VERIFIED): the
  bridge-skill consolidation pattern this new skill follows.
- `DELIB-20263860` — Bridge VERIFIED Backlog Retirement -010 (VERIFIED): the
  `bridge_verified_backlog_reconciler.py` engine the operator skill wraps.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive reconciliation
  classification is a deterministic service, not per-session AI reconstruction;
  the motivating principle for WI-4237.

## Owner Decisions / Input

- **This session (2026-06-20), via AskUserQuestion**, the owner selected
  **"Resume WI-4237 (build the tool)"** as the direction for reconciling the
  GO/ADVISORY backlog, explicitly authorizing the operator skill/runbook and the
  broken-shim repair. The owner's AUQ-presented option also named umbrella-closure
  logic; this proposal scopes the engine-level umbrella-closure **out** as a
  follow-on (see Summary) and delivers the operator surface + shim fix, which is
  the WI-4237 acceptance scope.
- **Durable project authorization:**
  `PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION` (active) covers
  WI-4237 under `PROJECT-GTKB-BRIDGE-RECONCILIATION` (validated read-only against
  MemBase by the propose scaffold).

## Requirement Sufficiency

Existing requirements sufficient. Governing requirements: the **WI-4237**
acceptance criteria (a skill/runbook exists; it invokes the reusable CLI/check;
it documents one-class-at-a-time correction packets; it requires owner/bridge
gates for mutation; it includes tests or manifest checks proving discoverability),
plus `GOV-STANDING-BACKLOG-001` and `GOV-FILE-BRIDGE-AUTHORITY-001`. No new or
revised requirement is needed before implementation; this work implements an
existing, owner-authorized backlog item.

## Spec-Derived Verification Plan

| Linked specification | Test / command | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-STANDING-BACKLOG-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_verified_backlog_reconciler.py --dry-run` (the skill's documented read-only audit command) | exit 0; reports candidates without mutating MemBase (`would_resolve_ids` only populated under `--apply`) |
| WI-4237 discoverability | `platform_tests/scripts/test_bridge_reconcile_skill.py` | asserts `.claude/skills/bridge-reconcile/SKILL.md` exists, is registered in every harness `MANIFEST.json`, and the SKILL.md text cites the audit command names and the no-bulk-mutation policy string |
| Shim repair (reliability) | `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_backlog_terminal_reconciliation.py --help` | exit 0; no `ModuleNotFoundError: bridge_reconciliation_audit` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | spec-to-test mapping table carried into the post-implementation report | each linked spec maps to an executed test/command |

Aggregate run command:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_reconcile_skill.py -q --no-header
```

Pre-file code-quality gates on any changed Python (shim + test):

```text
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/bridge_backlog_terminal_reconciliation.py platform_tests/scripts/test_bridge_reconcile_skill.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/bridge_backlog_terminal_reconciliation.py platform_tests/scripts/test_bridge_reconcile_skill.py
```

## Risk / Rollback

Low risk and additive. The skill wraps existing read-only tools and encodes the
no-bulk-mutation + owner-gate policy; it introduces no new mutation path. The
shim repair restores a broken entrypoint (reliability fast-lane class:
`GOV-RELIABILITY-FAST-LANE-001`) and changes no reconciler behavior. No engine
logic (`classify_work_item`, parent-evidence semantics) is altered.

Risk: skill-adapter drift across the four harness mirrors. Mitigation: run
`scripts/generate_codex_skill_adapters.py --update-registry` and assert
cross-harness manifest parity in the discoverability test.

Rollback: single-commit revert removes the `bridge-reconcile` skill directory,
its manifest registrations, the shim change, and the test.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-bridge-reconcile-operator-skill`; no prior version is
deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat` — the predominant surface is a net-new operator skill + runbook + its
discoverability test (a new capability). The shim repair is a `fix:`-class
change folded in as a prerequisite; the new-capability surface dominates the
diff, so `feat` is the honest aggregate type.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
