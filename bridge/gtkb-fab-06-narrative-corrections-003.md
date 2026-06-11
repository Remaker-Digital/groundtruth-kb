REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-06-narrative-corrections
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4418
Project Authorization: PAUTH-FAB06-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 430d5513-21a1-4e1c-b244-743f2ca7ed00
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["CLAUDE.md", "AGENTS.md", ".claude/rules/canonical-terminology.md", "scripts/assertion_categorize.py", "scripts/generate_governance_index.py", ".groundtruth/formal-artifact-approvals/*.json", "platform_tests/scripts/**"]

No KB mutation: FAB-06 READS the canonical MemBase GOV rows to regenerate the CLAUDE.md index; it does NOT mutate `groundtruth.db` (GOV-18 stays represented as the SPEC-1662 alias — no new GOV-row insert). `groundtruth.db` is intentionally NOT in target_paths.

---

# FAB-06 — Correct always-loaded narrative inaccuracies (CLAUDE.md / AGENTS.md), REVISED

WI-4418 (FAB-06) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-017 (CLAUDE.md half), HYG-031, HYG-037.
Revises the proposal after the NO-GO at `bridge/gtkb-fab-06-narrative-corrections-002.md` (FINDING-P1-001).

## Revision Scope

Addresses the single finding in the `-002` NO-GO:

> FINDING-P1-001 — required narrative-approval packet files are not in `target_paths`.

The three edits touch protected always-loaded narrative artifacts (CLAUDE.md, AGENTS.md,
`.claude/rules/canonical-terminology.md`), each requiring a per-file narrative-approval packet per
`GOV-ARTIFACT-APPROVAL-001` and PAUTH-FAB06-20260610. The `-001` referenced the packets in prose but
did not list the packet directory in `target_paths`, so the impl-start gate would deny those writes.
This revision adds `.groundtruth/formal-artifact-approvals/*.json` to `target_paths`. No disposition,
owner decision, or verification claim changed; this is a scope-coverage correction only.

## Summary

Three always-loaded narrative inaccuracies that mis-teach **every session**:

- **HYG-031:** the CLAUDE.md Governance Index assigns different meanings to GOV-01..06/17
  than the canonical MemBase GOV rows (index "GOV-06 = specify-on-contact" vs DB GOV-06 =
  "spec-first correction cycle"); GOV-18 isn't a row (it lives as SPEC-1662). Per GOV-08
  (KB-is-truth) the DB wins, so every session loads wrong governance mappings.
- **HYG-037:** AGENTS.md tells Codex "Agent Red is not part of GT-KB; a separate project,"
  contradicting CLAUDE.md + 4 other auto-loaded rules (Agent Red = in-root reference adopter,
  post-S347) — a cross-harness GO/NO-GO scope split on the Agent_Red subtree.
- **HYG-017 (CLAUDE.md half):** the CLAUDE.md "Knowledge Database Access" section directs
  every session to the Agent-Red shim (`tools/knowledge-db/db.py`, `localhost:8090`) beside a
  decoy **empty** 507 KB `groundtruth.db` (29 tables, 0 rows) — a wrong-DB trap with a
  documented S421 near-miss.

All three are protected-narrative edits (CLAUDE.md/AGENTS.md/canonical-terminology →
per-file approval packets). The `tools/knowledge-db` **physical** disposition is a separate
Agent-Red-scoped follow-up; FAB-06 fixes the dangerous **pointer** now.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle authority for this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.
- `GOV-STANDING-BACKLOG-001` — WI-4418 is the governed backlog authority.
- `GOV-ARTIFACT-APPROVAL-001` — CLAUDE.md/AGENTS.md/canonical-terminology edits are
  protected narrative artifacts requiring per-file approval packets.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` (+ `DELIB-0834`) — the S347 reference-adopter framing
  AGENTS.md is realigned to.
- `SPEC-1662` (GOV-18 Assertion Quality) — GOV-18 is represented as this alias, not a new row.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — HYG-037 concerns Agent-Red **scope framing** and
  HYG-017 references the Agent-Red shim's placement. FAB-06 edits only **in-root** narrative
  files (CLAUDE.md, AGENTS.md, canonical-terminology.md) and writes **no** out-of-root
  artifacts (this bridge file is under `E:\GT-KB\bridge\`); it **relocates nothing** — the
  `tools/knowledge-db` physical move is the deferred follow-up. No application-placement change here.

Governing rule (non-spec): `GOV-08` (KB-is-truth — the canonical DB GOV rows win the numbering).

## Isolation Placement Compliance

All FAB-06 edits stay **in-root under `E:\GT-KB`**: the narrative files (`CLAUDE.md`, `AGENTS.md`,
`.claude/rules/canonical-terminology.md`), the generator (`scripts/generate_governance_index.py`),
the swept script, the test under `platform_tests/scripts/`, and the narrative-approval packets under
`.groundtruth/formal-artifact-approvals/`. No `applications/` subtree is touched, nothing is relocated
(the `tools/knowledge-db` physical disposition is the deferred Agent-Red follow-up), and no out-of-root
artifact is created or required.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-017/031/037).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB06-REMEDIATION-20260610` — this cluster's owner-decision set (the 3 dispositions).
- _The `tools/knowledge-db` physical-shim disposition (HYG-017 other half) is a separate
  Agent-Red-scoped follow-up; the open Slice-9 CLAUDE/AGENTS work item covers the durable-vs-session
  role split, not these inaccuracies._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB06-REMEDIATION-20260610`:

1. **HYG-031 = MemBase rows win (GOV-08)** — regenerate the CLAUDE.md index from a DB query
   (deterministic-services); represent GOV-18 as the SPEC-1662 alias; sweep the ~20 wrong-number
   GOV citations in rules/scripts. (Rejected: CLAUDE.md-index-wins; decouple-mnemonic.)
2. **HYG-037 = Realign AGENTS.md to S347 framing** — update L11/L19-20 to mirror
   project-root-boundary.md, citing GOV-AGENT-RED-GTKB-CONFORMANCE-001 + DELIB-0834.
   (Rejected: keep-separate-project; fold-into-WI-3479.)
3. **HYG-017 = Fix the CLAUDE.md KB-access pointer now** — repoint to the groundtruth_kb API +
   root groundtruth.db; the shim physical cleanup is a separate Agent-Red follow-up.
   (Rejected: archive-shim-now; keep+LEGACY-marker.)

## Requirement Sufficiency

**Existing requirements sufficient.** Governed by GOV-08 (KB-is-truth), GOV-AGENT-RED-GTKB-CONFORMANCE-001
(Agent-Red framing), and GOV-ARTIFACT-APPROVAL-001 (narrative packets); the dispositions are fixed by
`DELIB-FAB06-REMEDIATION-20260610`. No new requirement needed. The governance-index generator encodes
the deterministic-services derivation of the index from the DB.

## Scope and Boundaries

In scope: regenerate the CLAUDE.md GOV index from the DB (+ a generator script) + GOV-18 alias + GOV
citation sweep; realign AGENTS.md; repoint the CLAUDE.md KB-access section. Out of scope: the
`tools/knowledge-db` physical relocation/archival + decoy-DB removal (separate Agent-Red follow-up);
any new formal GOV-row insert (GOV-18 stays a SPEC-1662 alias); renumbering the canonical DB GOV rows.

## Proposed Implementation

1. **HYG-031:** add `scripts/generate_governance_index.py` that renders the CLAUDE.md Governance
   Index table from the live MemBase GOV rows (deterministic-services); apply the regenerated table
   to CLAUDE.md (narrative packet); represent GOV-18 as "SPEC-1662 (GOV-18: Assertion Quality)";
   sweep the wrong-number citations (`canonical-terminology.md` GOV-06 lines; `scripts/assertion_categorize.py`
   GOV-18 lines; plus grep-derived remainder within scope).
2. **HYG-037:** edit AGENTS.md L11/L19-20 (narrative packet) to mirror project-root-boundary.md's
   reference-adopter language (in-root Agent_Red subtree, lifecycle-independent hosted repo,
   tooling-reference narrowing), citing GOV-AGENT-RED-GTKB-CONFORMANCE-001 + DELIB-0834.
3. **HYG-017:** edit the CLAUDE.md "Knowledge Database Access" section (narrative packet) to cite the
   groundtruth_kb API + root groundtruth.db (drop the `tools/knowledge-db/db.py` + `localhost:8090`
   pointer); note the shim is legacy pending the separate disposition bridge.

Each CLAUDE.md/AGENTS.md/canonical-terminology edit is preceded by its narrative-approval packet
(`.groundtruth/formal-artifact-approvals/*.json`).

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| GOV-08 (KB-is-truth) | a test asserts the CLAUDE.md GOV index table matches the live MemBase GOV rows (generator output == committed table); GOV-18 shown as the SPEC-1662 alias; no wrong-number GOV citation remains (grep) |
| `GOV-AGENT-RED-GTKB-CONFORMANCE-001` | grep: AGENTS.md contains no "not part of GT-KB" / "not GT-KB files"; carries the in-root reference-adopter framing |
| HYG-017 pointer | grep: CLAUDE.md KB-access cites `groundtruth_kb` + root `groundtruth.db`, not `tools/knowledge-db/db.py` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` (index-matches-DB + grep-absence) + `ruff check`/`format --check` on the generator |

## Acceptance Criteria

1. CLAUDE.md GOV index regenerated to match the DB rows; GOV-18 = SPEC-1662 alias; citations swept.
2. AGENTS.md realigned to the S347 reference-adopter framing.
3. CLAUDE.md KB-access repointed to the groundtruth_kb API + root groundtruth.db.
4. Each protected edit has its narrative-approval packet; the index-matches-DB test passes; ruff-clean.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-06-narrative-corrections-003.md` with a matching `REVISED` entry inserted at
the top of the `gtkb-fab-06-narrative-corrections` entry in `bridge/INDEX.md`; append-only, no prior
bridge version deleted or rewritten. `bridge/INDEX.md` remains canonical workflow state
(`GOV-FILE-BRIDGE-AUTHORITY-001` preserved).

## Risk and Rollback

- **Risk:** the generated index drifts from CLAUDE.md's 300-line GOV-01 limit → the generator emits
  only the compact table; the test guards the line-count rule.
- **Risk:** a swept citation breaks a code path → citation edits are mnemonic-only (GOV labels); a
  grep-absence test confirms no wrong-number remains.
- **Rollback:** revert the narrative edits (each a discrete packet change) and the generator; no
  MemBase mutation to undo.

## Recommended Implementation Routing

**Opus/Codex-supervised** — protected-narrative governance edits gated by per-file approval packets;
not a cheap-model candidate. The generator script is mechanical but its output feeds a protected file.

## Recommended Commit Type

`docs:` — governance-narrative corrections (GOV index regen, AGENTS.md realign, KB-pointer fix) with a
`feat:`-class governance-index generator.
