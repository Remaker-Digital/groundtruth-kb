NEW

# gtkb-backlog-update-title-desc-cli-001 — Extend `gt backlog update` with `--title` and `--description` flags under a disjunctive safety gate

bridge_kind: implementation_proposal
Document: gtkb-backlog-update-title-desc-cli-001
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-04 UTC

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

## Summary

Add `--title TEXT` and `--description TEXT` flags to `gt backlog update` so cross-thread work-item text drift can be repaired through the deterministic CLI path instead of direct sqlite writes (which would violate GOV-15, the deterministic-services principle `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, and the standing self-improvement directive).

The capability already exists in the DB layer: `KnowledgeDB.update_work_item` accepts `title` and `description` via `**fields` (`groundtruth-kb/src/groundtruth_kb/db.py:3560-3561`). The omission is at the CLI boundary in `cli.py:1414` (`@backlog.command("update")` decorator + signature) and `cli_backlog_update.py:27-39` (`BacklogUpdateRequest` dataclass + `update_backlog_item` validation). This proposal closes that boundary gap with a deliberate safety gate so text-edit authority is not silently broader than the existing field gates.

Proximate driver: the SoT umbrella thread `bridge/gtkb-platform-sot-consolidation-umbrella-006.md` is NO-GO because three active work items (WI-4340 active, WI-4343 active, WI-4341 resolved-but-historical) carry titles and descriptions that direct Prime to a withdrawn DCL name `DCL-SOT-REGISTRY-SCHEMA-001`. Per owner AUQ #11 in `DELIB-20260672`, the canonical authority is `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` (extended). The umbrella proposal `-005` shows the corrected scope in its body but the live WI text was not updated alongside — and there is no governed CLI path to update it.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is canonical workflow state; this proposal is filed under the standard NEW/REVISED/GO lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section enumerates every governing spec for the proposed work.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item metadata above link this proposal to PROJECT-GTKB-DETERMINISTIC-SERVICES-001 and WI-4357.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Spec-Derived Verification Plan below maps each cited spec to executable evidence.
- `GOV-STANDING-BACKLOG-001` — the backlog is a source of truth; this proposal extends the governed CLI surface that mutates that truth, with safety gates appropriate to the elevated leverage of `title` / `description` fields.
- `GOV-15` — the disjunctive safety gate adopts the same `--owner-approved` shape used by the existing terminal-resolution gate (`cli_backlog_update.py:97-104`), preserving precedent.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` + `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-BACKLOG-UPDATE-TITLE-DESC-CLI-WI-4357` (version 1, status=active) authorizes WI-4357 with `allowed_mutation_classes=[cli_extension, source, test_addition]`, owner-decision `DELIB-20260871`.
- `GOV-ARTIFACT-APPROVAL-001` — backlog text edits produce versioned canonical-artifact mutations; the disjunctive gate ensures the operator demonstrates approval evidence per edit.

## Prior Deliberations

- `DELIB-20260870` — Owner AUQ on 2026-06-04 selecting design parameters: (1) disjunctive safety gate, (2) new `platform_tests/cli/test_backlog_update_title_desc.py` unit-test file, (3) PROJECT-GTKB-DETERMINISTIC-SERVICES-001 as the project home. This proposal directly implements those three answers.
- `DELIB-20260871` — Owner AUQ on 2026-06-04 selecting PAUTH-strategy Option 1 (mint a new narrow PAUTH). That PAUTH is cited above as the Project Authorization.
- `DELIB-20260672` — Owner AUQ #11 establishing `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` (extended) as the canonical authority, rendering `DCL-SOT-REGISTRY-SCHEMA-001` (withdrawn) stale in WI-4340 and WI-4343 text. Drives the proximate need.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — Repetitive AI plumbing is a defect; deterministic services own the plumbing. This CLI extension converts a recurring class of friction (cross-thread WI text drift) into a deterministic operator surface.
- `DELIB-S385-CLI-SUBSET-FILTERS-AUTHORIZATION` — Precedent for narrow, WI-scoped PAUTHs under DETERMINISTIC-SERVICES-001 (`PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-CLI-SUBSET-FILTERS-WI-4220`). This proposal mirrors that pattern.

The pre-seeded `INTAKE-9a936aee`, `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE`, `DELIB-S378-SLICE1-CLI-PACKET-FORM-WAIVER`, and `DELIB-S364-SKILL-MODERNIZATION-SLICE-0-PAUTH` candidates were inspected and pruned — they do not bear on this proposal.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-2235` — seed=search; bridge_thread; Bridge thread: gtkb-backlog-add-cli-slice-1 (6 versions, VERIFIED)
- DA: `DELIB-2380` — seed=search; bridge_thread; Loyal Opposition Review - work_list.md GTKB-GOV-010 Path Correction
- DA: `DELIB-2783` — seed=search; bridge_thread; Bridge INDEX startup comment compaction snapshot 2026-06-02T00:23:25Z
- DA: `DELIB-20260794` — seed=search; bridge_thread; Loyal Opposition Review - Discoverability CLI Status Scanner API Regression
- DA: `DELIB-2379` — seed=search; bridge_thread; Loyal Opposition Review - work_list.md GTKB-GOV Stale-Path Correction

## Owner Decisions / Input

This proposal depends on owner approval recorded via AskUserQuestion. The relevant AUQ evidence:

1. **`DELIB-20260870`** (2026-06-04, S408) — three-question AUQ on design parameters:
   - Q1 "How should `gt backlog update --title/--description` gate write authority?" → **Disjunctive gate (Recommended)**: allow if `WI.approval_state == bridge_authorized` OR `--owner-approved` is set OR `--change-reason` cites an active `PAUTH-*` or `DELIB-*` token.
   - Q2 "What test surface should the bridge proposal commit to?" → **Unit tests on CLI + helper (Recommended)**: new `platform_tests/cli/test_backlog_update_title_desc.py` covering happy path, dry-run, gate enforcement, forbidden-field combinations, and change_reason validation.
   - Q3 "Which project should host this WI + bridge proposal?" → **PROJECT-GTKB-DETERMINISTIC-SERVICES-001 (Recommended)**.

2. **`DELIB-20260871`** (2026-06-04, S408) — single-question AUQ on PAUTH strategy:
   - Q1 "How should the new bridge proposal cite project authorization?" → **Mint a new narrow PAUTH now (Recommended)**. The minted PAUTH is the Project Authorization cited above.

No further owner decision is required before Loyal Opposition review.

## Requirement Sufficiency

**Existing requirements sufficient** — the governing requirements are:

- `GOV-15` (test fix gate; sets the `--owner-approved` precedent the disjunctive gate mirrors)
- `GOV-STANDING-BACKLOG-001` (backlog as source of truth; informs why text edits warrant heightened gates)
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (PAUTH-token citation path in `--change-reason` satisfies bridge-authorized work)
- The disjunctive gate design from `DELIB-20260870`

No new specification, ADR, or DCL is required. The proposal implements the gate inside the existing `update_backlog_item` helper without adding a new governance surface.

## Spec-Derived Verification Plan

| Specification | Verification command (executed against the implementation) | Expected result |
| --- | --- | --- |
| `GOV-STANDING-BACKLOG-001` + `GOV-15` (disjunctive gate enforcement) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/cli/test_backlog_update_title_desc.py::test_gate_rejects_without_evidence -q` | PASS — CLI returns exit 1 with a clear error citing the three gate options when none satisfied |
| `GOV-STANDING-BACKLOG-001` (happy path: owner_approved=true) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/cli/test_backlog_update_title_desc.py::test_owner_approved_admits_title_edit -q` | PASS — new WI version persists; `current_work_items.title` reflects the edit |
| `GOV-STANDING-BACKLOG-001` (happy path: PAUTH citation in change_reason) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/cli/test_backlog_update_title_desc.py::test_pauth_citation_admits_description_edit -q` | PASS — PAUTH-* token in `--change-reason` admits the edit |
| `GOV-STANDING-BACKLOG-001` (happy path: bridge_authorized approval_state) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/cli/test_backlog_update_title_desc.py::test_bridge_authorized_admits_text_edit -q` | PASS — WI with `approval_state=bridge_authorized` admits text edits without further evidence |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (dry-run discipline) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/cli/test_backlog_update_title_desc.py::test_dry_run_validates_and_reports_no_write -q` | PASS — `--dry-run` returns the would-be fields without persisting a new version |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (change_reason validation) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/cli/test_backlog_update_title_desc.py::test_empty_change_reason_rejected_with_title_edit -q` | PASS — text edits with empty `--change-reason` are rejected with the same error as the existing gate |
| Full CLI test suite regression | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_backlog_update_cli.py -q --no-header --cache-clear` | PASS — existing tests unaffected (no breaking changes to the existing flag set) |
| Code quality gates | `cd groundtruth-kb && .venv/Scripts/ruff check src/groundtruth_kb/cli.py src/groundtruth_kb/cli_backlog_update.py && .venv/Scripts/ruff format --check src/groundtruth_kb/cli.py src/groundtruth_kb/cli_backlog_update.py` | PASS — both gates clean (`ruff check` AND `ruff format --check` are SEPARATE gates per `.claude/rules/file-bridge-protocol.md` § "Pre-File Code-Quality Gates") |

The new test file `platform_tests/cli/test_backlog_update_title_desc.py` is the spec-to-test mapping evidence for `GOV-STANDING-BACKLOG-001` text-edit gating. The implementation report (post-impl version) will carry forward this mapping and report the actual pytest output.

## Risk / Rollback

**Risk surface:**
1. **Gate-evasion via crafted change_reason** — a `--change-reason` string containing the literal substring `PAUTH-` or `DELIB-` would satisfy the citation check without a real authorization. Mitigation: the gate uses a regex matching the canonical `PAUTH-[A-Z0-9-]+` / `DELIB-[A-Z0-9-]+` shape, AND the implementation will look up the cited PAUTH or DELIB row to confirm it exists. Pure-string-match evasion is rejected.
2. **Cross-thread WI text edits applied to a still-live umbrella scope** — operators using this CLI to "fix" WI text could inadvertently edit a WI whose current scope is correct under a different PAUTH. Mitigation: the existing `--dry-run` discipline is retained; the gate's PAUTH/DELIB citation requirement forces the operator to think about the authority for the edit; new tests assert dry-run behavior.
3. **Future "approval_state evasion"** — the `bridge_authorized` arm of the gate is data-driven; a future PAUTH whose included_work_item set incorrectly flips a WI to bridge_authorized could enable inappropriate edits. This is bounded by the existing PAUTH authoring flow's owner-AUQ requirement.

**Rollback:** single commit revert. The change is fully contained to the three target paths above and adds no new DB columns, no new tables, no new schema migrations. `git revert <commit-sha>` returns the CLI to its pre-change behavior; existing `--resolution-status / --stage / --priority / --related-bridge-threads / --status-detail / --owner-approved / --change-reason / --dry-run / --json` flags continue to work because they are not modified.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-backlog-update-title-desc-cli-001` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`feat:` — adds two new user-visible CLI flags (`--title`, `--description`) plus a new safety-gate code path. Net new capability, not a fix or refactor. Net LOC: estimated ~80 lines source (~30 in `cli.py` for flag wiring, ~50 in `cli_backlog_update.py` for the gate + validation) + ~150 lines test. Matches `feat:` per the Conventional Commits discipline in `.claude/rules/file-bridge-protocol.md` § "Conventional Commits Type Discipline".

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
