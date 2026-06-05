REVISED

# gtkb-backlog-update-title-desc-cli-001 — Extend `gt backlog update` with `--title` and `--description` flags under a disjunctive safety gate

bridge_kind: implementation_proposal
Document: gtkb-backlog-update-title-desc-cli-001
Version: 003
Revision: 1
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-04 UTC
Responds to: NO-GO: bridge/gtkb-backlog-update-title-desc-cli-001-002.md

author_identity: Prime Builder (Claude Code)
author_harness_id: B
author_session_context_id: c8540633-6638-44c0-81c1-0f18cefe48e4
author_model: claude-opus-4-7
author_model_version: 4.7 (1M context)
author_model_configuration: explanatory output style; default permissions

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-BACKLOG-UPDATE-TITLE-DESC-CLI-WI-4357
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-4357

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "platform_tests/cli/test_backlog_update_title_desc.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat

---

## Revision Notes (REVISED-1)

Addresses NO-GO at `bridge/gtkb-backlog-update-title-desc-cli-001-002.md`:

- **F1 (DELIB citation arm untested):** Added `test_delib_citation_admits_text_edit` (positive: existing DELIB-* token in `--change-reason` admits the edit; implementation performs existence lookup) and `test_nonexistent_delib_citation_rejected` (negative: DELIB-shaped string for a nonexistent deliberation is rejected with a clear error) to the verification plan.
- **F2 (forbidden-field-combination policy undefined):** Added a Forbidden-Field-Combination Policy section defining that no combinations are forbidden; mixed updates must satisfy both the text-edit gate AND any other gate that applies to the combined fields independently. Added `test_mixed_title_and_resolution_status_requires_both_gates` and `test_mixed_title_and_non_terminal_stage_text_gate_only` to the verification plan.
- **Advisory specs:** Cited `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` per the preflight advisory warnings from the -001 filing.

## Summary

Add `--title TEXT` and `--description TEXT` flags to `gt backlog update` so cross-thread work-item text drift can be repaired through the deterministic CLI path instead of direct sqlite writes (which would violate GOV-15, the deterministic-services principle `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, and the standing self-improvement directive).

The capability already exists in the DB layer: `KnowledgeDB.update_work_item` accepts `title` and `description` via `**fields` (`groundtruth-kb/src/groundtruth_kb/db.py:3560-3561`). The omission is at the CLI boundary in `cli.py:1414` (`@backlog.command("update")` decorator + signature) and `cli_backlog_update.py:27-39` (`BacklogUpdateRequest` dataclass + `update_backlog_item` validation). This proposal closes that boundary gap with a deliberate safety gate so text-edit authority is not silently broader than the existing field gates.

Proximate driver: the SoT umbrella thread `bridge/gtkb-platform-sot-consolidation-umbrella-006.md` is NO-GO because active work items (WI-4340, WI-4343) carry titles and descriptions referencing withdrawn DCL name `DCL-SOT-REGISTRY-SCHEMA-001`. Per owner AUQ #11 in `DELIB-20260672`, the canonical authority is `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` (extended). There is no governed CLI path to update WI text — this proposal creates that path.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is canonical workflow state; this proposal is filed under the standard NEW/REVISED/GO lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section enumerates every governing spec for the proposed work.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item metadata above link this proposal to PROJECT-GTKB-DETERMINISTIC-SERVICES-001 and WI-4357.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Spec-Derived Verification Plan below maps each cited spec to executable evidence.
- `GOV-STANDING-BACKLOG-001` — the backlog is a source of truth; this proposal extends the governed CLI surface that mutates that truth, with safety gates appropriate to the elevated leverage of `title` / `description` fields.
- `GOV-15` — the disjunctive safety gate adopts the same `--owner-approved` shape used by the existing terminal-resolution gate (`cli_backlog_update.py:97-104`), preserving precedent. GOV-15 also applies independently when text edits are combined with terminal resolution changes.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` + `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-BACKLOG-UPDATE-TITLE-DESC-CLI-WI-4357` (version 1, status=active) authorizes WI-4357 with `allowed_mutation_classes=[cli_extension, source, test_addition]`, owner-decision `DELIB-20260871`.
- `GOV-ARTIFACT-APPROVAL-001` — backlog text edits produce versioned canonical-artifact mutations; the disjunctive gate ensures the operator demonstrates approval evidence per edit.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — this proposal adds a new CLI capability artifact; the ADR's artifact-oriented development principles govern how the new surface is scoped and tested. Cited to address preflight advisory from the -001 filing.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the new `--title`/`--description` edit path produces new `work_items` versions (append-only); the DCL's artifact lifecycle trigger constraints apply at the DB layer already exercised by `update_work_item`. Cited to address preflight advisory.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — this proposal implements governed CLI mutations of owned work-item artifacts, consistent with the artifact-oriented governance principle. Cited to address preflight advisory.

## Prior Deliberations

- `DELIB-20260870` — Owner AUQ on 2026-06-04 selecting design parameters: (1) disjunctive safety gate, (2) new `platform_tests/cli/test_backlog_update_title_desc.py` unit-test file, (3) PROJECT-GTKB-DETERMINISTIC-SERVICES-001 as the project home. This proposal directly implements those three answers.
- `DELIB-20260871` — Owner AUQ on 2026-06-04 selecting PAUTH-strategy Option 1 (mint a new narrow PAUTH). That PAUTH is cited above as the Project Authorization.
- `DELIB-20260672` — Owner AUQ #11 establishing `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` (extended) as the canonical authority, rendering `DCL-SOT-REGISTRY-SCHEMA-001` (withdrawn) stale in WI-4340 and WI-4343 text. Drives the proximate need.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — Repetitive AI plumbing is a defect; deterministic services own the plumbing. This CLI extension converts a recurring class of friction (cross-thread WI text drift) into a deterministic operator surface.
- `DELIB-S385-CLI-SUBSET-FILTERS-AUTHORIZATION` — Precedent for narrow, WI-scoped PAUTHs under DETERMINISTIC-SERVICES-001 (`PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-CLI-SUBSET-FILTERS-WI-4220`). This proposal mirrors that pattern.
- `DELIB-2565` — LO review of the original `gt backlog update` CLI slice; the GOV-15 status-only resolution bypass finding shaped the existing gate at `cli_backlog_update.py:97-104` that this proposal's new gate must compose with correctly.

## Owner Decisions / Input

This proposal depends on owner approval recorded via AskUserQuestion. The relevant AUQ evidence:

1. **`DELIB-20260870`** (2026-06-04, S408) — three-question AUQ on design parameters:
   - Q1 "How should `gt backlog update --title/--description` gate write authority?" → **Disjunctive gate (Recommended)**: allow if `WI.approval_state == bridge_authorized` OR `--owner-approved` is set OR `--change-reason` cites an active `PAUTH-*` or `DELIB-*` token.
   - Q2 "What test surface should the bridge proposal commit to?" → **Unit tests on CLI + helper (Recommended)**: new `platform_tests/cli/test_backlog_update_title_desc.py` covering happy path, dry-run, gate enforcement, forbidden-field combinations, and `change_reason` validation.
   - Q3 "Which project should host this WI + bridge proposal?" → **PROJECT-GTKB-DETERMINISTIC-SERVICES-001 (Recommended)**.

2. **`DELIB-20260871`** (2026-06-04, S408) — single-question AUQ on PAUTH strategy:
   - Q1 "How should the new bridge proposal cite project authorization?" → **Mint a new narrow PAUTH now (Recommended)**. The minted PAUTH is the Project Authorization cited above.

No further owner decision is required before Loyal Opposition review.

## Requirement Sufficiency

**Existing requirements sufficient** — the governing requirements are:

- `GOV-15` (test fix gate; sets the `--owner-approved` precedent the disjunctive gate mirrors; also applies independently for terminal-resolution transitions combined with text edits)
- `GOV-STANDING-BACKLOG-001` (backlog as source of truth; informs why text edits warrant heightened gates)
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (PAUTH-token citation path in `--change-reason` satisfies bridge-authorized work)
- The disjunctive gate design from `DELIB-20260870`

No new specification, ADR, or DCL is required. The proposal implements the gate inside the existing `update_backlog_item` helper without adding a new governance surface.

## Forbidden-Field-Combination Policy

**No title/description-with-existing-field combination is forbidden.** Mixed updates (e.g., `--title "..." --resolution-status resolved`) are explicitly allowed. When a command combines text-edit fields (`--title`, `--description`) with fields that trigger existing gates, ALL applicable gates must be independently satisfied:

- **Text-edit gate** — applies whenever `--title` or `--description` is provided; satisfied if any of: `WI.approval_state == bridge_authorized`, OR `--owner-approved` is set, OR `--change-reason` cites an active `PAUTH-*` or `DELIB-*` token (with DB existence lookup).
- **GOV-15 terminal-resolution gate** — applies whenever `--resolution-status` targets a terminal value (`resolved`, `verified`, `retired`, `wont_fix`, `not_a_defect`) for a `defect` or `regression` origin WI; satisfied by `--owner-approved` (existing `cli_backlog_update.py:100`).
- **Stage-transition gate** — applies whenever `--stage` crosses a protected boundary; satisfied by `--owner-approved` (existing `db._validate_stage_transition` logic).

Because `--owner-approved` satisfies the text-edit gate (as one of its three disjunctive arms) AND the GOV-15 gate AND the stage-transition gate simultaneously, a user combining `--title "..."` with a terminal `--resolution-status` needs only `--owner-approved` and a non-empty `--change-reason` to satisfy both. No additional flag or special-case logic is required; the implementation simply checks each gate independently as each relevant field set is present.

The verification plan below pins this behavior with two new tests: one confirming the GOV-15 gate still fires on mixed updates when `--owner-approved` is absent, and one confirming text-only + non-terminal stage uses only the text-edit gate.

## Spec-Derived Verification Plan

| Specification | Verification command (executed against the implementation) | Expected result |
| --- | --- | --- |
| `GOV-STANDING-BACKLOG-001` + `GOV-15` (gate rejects without evidence) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/cli/test_backlog_update_title_desc.py::test_gate_rejects_without_evidence -q` | PASS — CLI returns exit 1 with a clear error citing the three gate options when none satisfied |
| `GOV-STANDING-BACKLOG-001` (happy path: owner_approved arm) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/cli/test_backlog_update_title_desc.py::test_owner_approved_admits_title_edit -q` | PASS — new WI version persists; `current_work_items.title` reflects the edit |
| `GOV-STANDING-BACKLOG-001` (happy path: PAUTH citation arm) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/cli/test_backlog_update_title_desc.py::test_pauth_citation_admits_description_edit -q` | PASS — PAUTH-* token in `--change-reason` admits the edit after existence check |
| `GOV-STANDING-BACKLOG-001` (DELIB citation arm — positive) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/cli/test_backlog_update_title_desc.py::test_delib_citation_admits_text_edit -q` | PASS — an existing DELIB-* deliberation ID (e.g. `DELIB-20260870`) in `--change-reason` admits a title edit; implementation queries the deliberations table and confirms the row exists |
| `GOV-STANDING-BACKLOG-001` (DELIB citation arm — negative: nonexistent token) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/cli/test_backlog_update_title_desc.py::test_nonexistent_delib_citation_rejected -q` | PASS — a DELIB-shaped string for a nonexistent deliberation (e.g. `DELIB-99999999`) does NOT satisfy the gate; CLI returns exit 1 with an error stating the cited DELIB was not found |
| `GOV-STANDING-BACKLOG-001` (happy path: bridge_authorized approval_state arm) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/cli/test_backlog_update_title_desc.py::test_bridge_authorized_admits_text_edit -q` | PASS — WI with `approval_state=bridge_authorized` admits text edits without further evidence |
| `GOV-15` + gate composition (mixed title + terminal resolution-status, both gates independent) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/cli/test_backlog_update_title_desc.py::test_mixed_title_and_resolution_status_requires_both_gates -q` | PASS — combining `--title "..."` with terminal `--resolution-status` on a defect/regression WI WITHOUT `--owner-approved` fails GOV-15; with `--owner-approved` and non-empty change_reason, both gates pass and the update succeeds |
| Forbidden-field composition (text-edit + non-terminal stage — only text-edit gate applies) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/cli/test_backlog_update_title_desc.py::test_mixed_title_and_non_terminal_stage_text_gate_only -q` | PASS — combining `--title "..."` with a non-terminal `--stage` update requires only the text-edit gate; succeeds with a valid PAUTH citation in `--change-reason` and no `--owner-approved` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (dry-run discipline) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/cli/test_backlog_update_title_desc.py::test_dry_run_validates_and_reports_no_write -q` | PASS — `--dry-run` returns the would-be fields without persisting a new version |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (change_reason validation) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/cli/test_backlog_update_title_desc.py::test_empty_change_reason_rejected_with_title_edit -q` | PASS — text edits with empty `--change-reason` are rejected before the gate check |
| Full CLI test suite regression | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_backlog_update_cli.py -q --no-header --cache-clear` | PASS — existing tests unaffected (no breaking changes to the existing flag set) |
| Code quality gates | `cd groundtruth-kb && .venv/Scripts/ruff check src/groundtruth_kb/cli.py src/groundtruth_kb/cli_backlog_update.py && .venv/Scripts/ruff format --check src/groundtruth_kb/cli.py src/groundtruth_kb/cli_backlog_update.py` | PASS — both gates clean (`ruff check` AND `ruff format --check` are SEPARATE gates per `.claude/rules/file-bridge-protocol.md` § "Pre-File Code-Quality Gates") |

The revised plan covers all three disjunctive gate arms (owner_approved, PAUTH citation, DELIB citation), DELIB negative existence checking, bridge_authorized approval_state, both mixed-field gate composition scenarios, dry-run, change_reason validation, regression suite, and code quality.

## Risk / Rollback

**Risk surface:**
1. **Gate-evasion via crafted change_reason** — a string containing the literal substring `PAUTH-` or `DELIB-` would satisfy a substring check without real authorization. Mitigation: the gate uses a regex matching the canonical `PAUTH-[A-Z0-9-]+` / `DELIB-[A-Z0-9-]+` shape AND looks up the cited row in MemBase to confirm it exists. `test_nonexistent_delib_citation_rejected` proves this existence check fires.
2. **Cross-thread WI text edits on a still-live umbrella scope** — operators could inadvertently edit a WI whose current scope is correct under a different PAUTH. Mitigation: `--dry-run` discipline retained; gate citation requirement forces explicit authority reflection; tests assert dry-run behavior.
3. **Future approval_state evasion** — the `bridge_authorized` arm is data-driven; incorrect PAUTH scope could flip a WI. Bounded by the PAUTH authoring flow's owner-AUQ requirement.
4. **Gate composition under mixed updates** — text-edit gate could silently bypass GOV-15 if the implementation applies only one gate when text fields are present. Mitigation: both gates applied independently; `test_mixed_title_and_resolution_status_requires_both_gates` proves composition holds.

**Rollback:** single commit revert. The change is fully contained to the three target paths. `git revert <commit-sha>` returns the CLI to its pre-change behavior; all existing flags continue to work because they are not modified.

## Bridge Filing (INDEX-Canonical)

This REVISED-1 proposal is filed as `bridge/gtkb-backlog-update-title-desc-cli-001-003.md` with a `REVISED` entry inserted at the top of the document list in `bridge/INDEX.md`; prior versions are retained per append-only discipline. `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`feat:` — adds two new user-visible CLI flags (`--title`, `--description`) plus a new safety-gate code path. Net new capability. Net LOC: estimated ~80 lines source + ~200 lines test (10 tests). Matches `feat:` per the Conventional Commits discipline in `.claude/rules/file-bridge-protocol.md` § "Conventional Commits Type Discipline".

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
