REVISED

bridge_kind: implementation_report
Document: gtkb-fab-06-narrative-corrections
Version: 007
Responds-To: bridge/gtkb-fab-06-narrative-corrections-006.md
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-12

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4418
Project Authorization: PAUTH-FAB06-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 0f59a219-caee-4943-be84-23ec6ada1d07
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb, 1m context

target_paths: ["CLAUDE.md", "AGENTS.md", ".claude/rules/canonical-terminology.md", "scripts/generate_governance_index.py", "platform_tests/scripts/test_fab06_narrative_correctness.py", ".groundtruth/formal-artifact-approvals/2026-06-12-fab06-*.json"]

KB mutation: groundtruth.db is NOT in target_paths. No MemBase mutations in this report.

---

# FAB-06 — Correct always-loaded narrative inaccuracies — REVISED Post-Implementation Report

Implements the GO'd proposal `bridge/gtkb-fab-06-narrative-corrections-003.md` (GO at `-004`). This REVISED report addresses the three findings in the NO-GO at `-006`.

## Revision Scope

Addresses all three findings from `bridge/gtkb-fab-06-narrative-corrections-006.md` (NO-GO):

**FINDING-P1-001 (staged CLAUDE.md hash mismatch / "GILLING" typo):** The staged CLAUDE.md blob contained a stale "GILLING" typo; the working-tree copy had the correct "GRILLING". Resolved by restaging CLAUDE.md from the corrected working tree and regenerating the approval packet (`2026-06-12-fab06-claude-md.json`) with the correct `full_content` and `full_content_sha256` computed from the live staged content. The narrative evidence checker now passes all 3 files:
```
python scripts/check_narrative_artifact_evidence.py --paths CLAUDE.md AGENTS.md .claude/rules/canonical-terminology.md --json
  -> {"status": "pass", "findings": [], "cleared": ["CLAUDE.md", "AGENTS.md", ".claude/rules/canonical-terminology.md"]}
```

**FINDING-P1-002 (approval packets gitignored):** The three approval packets under `.groundtruth/formal-artifact-approvals/` were gitignored by the `.groundtruth/` blanket pattern at `.gitignore:551`. Resolved by force-adding all three packets:
```
git add -f .groundtruth/formal-artifact-approvals/2026-06-12-fab06-claude-md.json
git add -f .groundtruth/formal-artifact-approvals/2026-06-12-fab06-agents-md.json
git add -f .groundtruth/formal-artifact-approvals/2026-06-12-fab06-canon-term.json
```
All three now appear in `git status` as staged new files.

**FINDING-P2-003 (recommended commit type):** Changed from `docs:` to `feat:` — the net-new `scripts/generate_governance_index.py` is a first-class governance capability, not a documentation touch-up.

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
`DELIB-FAB06-REMEDIATION-20260610`, displayed in-session this turn. All three packets are now force-added
to git staging per FINDING-P1-002 resolution.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching INDEX entry.
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
python -m pytest platform_tests/scripts/test_fab06_narrative_correctness.py -q --tb=short
  -> 5 passed in 4.02s

python -m ruff check scripts/generate_governance_index.py platform_tests/scripts/test_fab06_narrative_correctness.py
  -> All checks passed!

python -m ruff format --check scripts/generate_governance_index.py platform_tests/scripts/test_fab06_narrative_correctness.py
  -> 2 files already formatted

python scripts/generate_governance_index.py --check
  -> exit 0; table rendered; all GOV rows present in CLAUDE.md

python scripts/check_narrative_artifact_evidence.py --paths CLAUDE.md AGENTS.md .claude/rules/canonical-terminology.md --json
  -> {"status": "pass", "findings": [], "cleared": ["CLAUDE.md", "AGENTS.md", ".claude/rules/canonical-terminology.md"]}

git status (approval packets):
  new file: .groundtruth/formal-artifact-approvals/2026-06-12-fab06-agents-md.json
  new file: .groundtruth/formal-artifact-approvals/2026-06-12-fab06-canon-term.json
  new file: .groundtruth/formal-artifact-approvals/2026-06-12-fab06-claude-md.json
```

## Acceptance Criteria Check

1. CLAUDE.md GOV index regenerated to match the DB rows; GOV-18 = SPEC-1662 alias; citations swept (incl. GRILLING correction). PASS
2. AGENTS.md realigned to the S347 reference-adopter framing. PASS
3. CLAUDE.md KB-access repointed to the `groundtruth_kb` API + root `groundtruth.db`. PASS
4. Each protected edit has its narrative-approval packet; index-matches-DB test passes; ruff-clean. PASS
5. (REVISED) All three approval packets force-added to git staging. PASS
6. (REVISED) Narrative evidence checker passes all 3 files (no hash mismatch, no GILLING). PASS

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-017/031/037).
- `DELIB-FAB06-REMEDIATION-20260610` — the three owner dispositions.
- `bridge/gtkb-fab-06-narrative-corrections-003.md` / `-004.md` — the REVISED proposal and its GO.
- `bridge/gtkb-fab-06-narrative-corrections-006.md` — Codex NO-GO with 3 findings (all addressed above).

## Owner Decisions / Input

Fix-scope owner decisions were collected via `AskUserQuestion` on 2026-06-10 and persisted to
`DELIB-FAB06-REMEDIATION-20260610` (HYG-031 MemBase-rows-win + GOV-18 alias + citation sweep; HYG-037
S347 realign; HYG-017 KB-pointer repoint). The owner's 2026-06-12 standing auto-approve-inline
authorization (this session) governs the three narrative-approval packets, whose content was displayed
in-session before minting. No new owner decision was required for the revision.

## Files Changed

| File | Change |
|------|--------|
| `CLAUDE.md` | HYG-031 GOV index regen (incl. GRILLING correction) + HYG-017 KB-access repoint (packet) |
| `AGENTS.md` | HYG-037 reference-adopter realign (packet) |
| `.claude/rules/canonical-terminology.md` | HYG-031 GOV-06 citation sweep (packet) |
| `scripts/generate_governance_index.py` | **NEW** — deterministic GOV-index generator from the DB |
| `platform_tests/scripts/test_fab06_narrative_correctness.py` | **NEW** — spec-derived tests (5) |
| `.groundtruth/formal-artifact-approvals/2026-06-12-fab06-claude-md.json` | **NEW** — CLAUDE.md approval packet (regenerated with correct hash) |
| `.groundtruth/formal-artifact-approvals/2026-06-12-fab06-agents-md.json` | **NEW** — AGENTS.md approval packet |
| `.groundtruth/formal-artifact-approvals/2026-06-12-fab06-canon-term.json` | **NEW** — canonical-terminology.md approval packet |

## Recommended Commit Type

`feat:` — net-new `scripts/generate_governance_index.py` is a first-class governance capability (deterministic GOV-index generation from MemBase), accompanied by governance-narrative corrections and spec-derived tests.

## Requirement Sufficiency

Existing requirements sufficient. All acceptance criteria from the GO at `-004` are covered by the 5 tests and the 3 narrative-approval packets. The revision addresses only evidence-hygiene findings from the NO-GO at `-006`; no new requirements were needed.
