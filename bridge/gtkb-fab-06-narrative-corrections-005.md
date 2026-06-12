NEW

bridge_kind: implementation_report
Document: gtkb-fab-06-narrative-corrections
Version: 005
Author: prime-builder (Claude Opus 4.8, harness B) — owner-present autonomous FABLE drive (/loop)
Date: 2026-06-12
Responds-To: bridge/gtkb-fab-06-narrative-corrections-004.md (GO)

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4418
Project Authorization: PAUTH-FAB06-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 0f59a219-caee-4943-be84-23ec6ada1d07
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: owner-present autonomous FABLE drive (/loop), ::init gtkb pb

---

# FAB-06 — Correct always-loaded narrative inaccuracies — Post-Implementation Report

Implements the GO'd proposal `bridge/gtkb-fab-06-narrative-corrections-003.md` (GO at `-004`).
Implementation-start authorization: packet derived from the live GO (7 target_path globs).

## Summary of Changes

**HYG-031 — CLAUDE.md Governance Index regenerated from the canonical MemBase GOV rows (GOV-08).**
Added `scripts/generate_governance_index.py`, a deterministic generator that renders the GOV index table
from the live `groundtruth.db` GOV rows. Applied its output to the CLAUDE.md Governance Index — so the
index now carries the DB meaning (e.g. `GOV-06 = Spec-first correction cycle`, not the old
"specify-on-contact" mnemonic), GOV-18 is shown as the `SPEC-1662` alias (no new GOV row), and the stale
`GOV-LO-ADVISORY-OWNER-GILLING-GATE-001` row was corrected to the DB's canonical
`GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` ("Grilling"). Swept the wrong-number GOV-06 citations in
`.claude/rules/canonical-terminology.md`; `scripts/assertion_categorize.py` already carries the
`SPEC-1662 (GOV-18)` alias.

**HYG-037 — AGENTS.md realigned to the S347 reference-adopter framing.** Removed the "Agent Red is not
part of GT-KB / a separate project" framing; AGENTS.md now mirrors `project-root-boundary.md`
(in-root `applications/Agent_Red/` reference adopter, lifecycle-independent hosted repo, the 2026-05-04
tooling-reference narrowing), citing `GOV-AGENT-RED-GTKB-CONFORMANCE-001` + `DELIB-0834`.

**HYG-017 — CLAUDE.md Knowledge Database Access repointed.** The KB-access section now cites the
`groundtruth_kb` API + root `groundtruth.db` (the `tools/knowledge-db/db.py` shim pointer is gone). The
shim's physical disposition remains a separate Agent-Red-scoped follow-up per the proposal.

Each protected-narrative edit (CLAUDE.md, AGENTS.md, `.claude/rules/canonical-terminology.md`) carries a
per-file narrative-approval packet under `.groundtruth/formal-artifact-approvals/` (artifact_type
`narrative_artifact`, approval_mode `auto`, `auto_approval_activated_by: owner`,
`presented_to_user`/`transcript_captured` true, content-hash matched to the live file) — owner-decided
`DELIB-FAB06-REMEDIATION-20260610`, displayed in-session this turn.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching INDEX entry (see Bridge Protocol Compliance).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.
- `GOV-STANDING-BACKLOG-001` — WI-4418 is the governed backlog authority.
- `GOV-ARTIFACT-APPROVAL-001` — the CLAUDE.md/AGENTS.md/canonical-terminology edits carry per-file approval packets.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` (+ `DELIB-0834`) — the S347 reference-adopter framing.
- `SPEC-1662` (GOV-18 Assertion Quality) — GOV-18 represented as this alias, not a new row.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all edits are in-root; nothing relocated.
- Governing rule (non-spec): `GOV-08` (KB-is-truth — the canonical DB GOV rows win the numbering).

## Spec-to-Test Mapping

| Spec / requirement | Derived test | Result |
|---|---|---|
| GOV-08 (KB-is-truth, HYG-031) | `test_gov_index_matches_generator_output` — every generator row (from live DB) appears in CLAUDE.md | PASS |
| GOV-08 / HYG-031 | `test_gov06_canonical_meaning` (GOV-06 = "Spec-first correction cycle") ; `test_gov18_is_spec1662_alias` | PASS |
| HYG-017 pointer | `test_kb_access_repointed_off_shim` — no `tools/knowledge-db/db.py`; cites `groundtruth_kb` | PASS |
| `GOV-AGENT-RED-GTKB-CONFORMANCE-001` (HYG-037) | `test_agents_reference_adopter_framing` — no "not part of GT-KB" | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest` + `ruff check`/`format --check` | PASS |

## Verification Commands and Observed Results

```
python -m pytest platform_tests/scripts/test_fab06_narrative_correctness.py -q
  -> 5 passed in 0.39s

python -m ruff check scripts/generate_governance_index.py platform_tests/scripts/test_fab06_narrative_correctness.py
  -> All checks passed!
python -m ruff format --check <same two files>
  -> 2 files already formatted

python scripts/generate_governance_index.py
  -> exit 0; 61 GOV rows rendered; all present in CLAUDE.md (index-matches-DB)

wc -l CLAUDE.md  -> 259 (GOV-01: <=300 honored)

# narrative-approval packets (each presented_to_user=true, transcript_captured=true, hash==file)
.groundtruth/formal-artifact-approvals/2026-06-12-fab06-claude-md.json   (CLAUDE.md)
.groundtruth/formal-artifact-approvals/2026-06-12-fab06-agents-md.json   (AGENTS.md)
.groundtruth/formal-artifact-approvals/2026-06-12-fab06-canon-term.json  (canonical-terminology.md)
```

## Acceptance Criteria Check

1. CLAUDE.md GOV index regenerated to match the DB rows; GOV-18 = SPEC-1662 alias; citations swept (incl. GRILLING correction). PASS
2. AGENTS.md realigned to the S347 reference-adopter framing. PASS
3. CLAUDE.md KB-access repointed to the `groundtruth_kb` API + root `groundtruth.db`. PASS
4. Each protected edit has its narrative-approval packet; index-matches-DB test passes; ruff-clean. PASS

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-017/031/037).
- `DELIB-FAB06-REMEDIATION-20260610` — the three owner dispositions.
- `bridge/gtkb-fab-06-narrative-corrections-003.md` / `-004.md` — the REVISED proposal and its GO.

## Owner Decisions / Input

Fix-scope owner decisions were collected via `AskUserQuestion` on 2026-06-10 and persisted to
`DELIB-FAB06-REMEDIATION-20260610` (HYG-031 MemBase-rows-win + GOV-18 alias + citation sweep; HYG-037
S347 realign; HYG-017 KB-pointer repoint). The owner's 2026-06-12 standing auto-approve-inline
authorization (this session) governs the three narrative-approval packets, whose content was displayed
in-session before minting. No new owner decision was required for implementation.

## Files Changed

- `CLAUDE.md` — HYG-031 GOV index regen (incl. GRILLING correction) + HYG-017 KB-access repoint (packet).
- `AGENTS.md` — HYG-037 reference-adopter realign (packet).
- `.claude/rules/canonical-terminology.md` — HYG-031 GOV-06 citation sweep (packet).
- `scripts/generate_governance_index.py` — NEW; deterministic GOV-index generator from the DB.
- `platform_tests/scripts/test_fab06_narrative_correctness.py` — NEW; spec-derived tests (5).
- `.groundtruth/formal-artifact-approvals/2026-06-12-fab06-{claude-md,agents-md,canon-term}.json` — NEW; approval packets.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-06-narrative-corrections-005.md` with a matching `NEW` line inserted at the top
of the `gtkb-fab-06-narrative-corrections` entry in `bridge/INDEX.md` (INDEX update: insert at the top of
the entry's version list). `bridge/INDEX.md` remains the canonical workflow state; append-only — all
prior versions (`-001`..`-004`) are preserved, none deleted or rewritten. `GOV-FILE-BRIDGE-AUTHORITY-001`
(CLAUSE-INDEX-IS-CANONICAL) honored.

## Recommended Commit Type

`docs:` — governance-narrative corrections (GOV index regen, AGENTS realign, KB-pointer fix) with a
`feat:`-class governance-index generator and `test:`-class coverage.
