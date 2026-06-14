NEW

bridge_kind: implementation_proposal
Document: gtkb-wi3439-requirement-sufficiency-presence-check
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 02535fad-c96f-4bd8-8e09-24dfd34c1529
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop; model claude-opus-4-8[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-3439
target_paths: ["groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-3439: bridge-compliance-gate presence check for the `## Requirement Sufficiency` subsection

## Summary

WI-3439 (P2, `bridge`, origin=improvement): implementation proposals can lose the mandatory `## Requirement Sufficiency` subsection across REVISED versions and still receive Codex GO; only the impl-start authorization gate (`implementation_authorization.py begin`) catches the omission post-GO, blocking implementation until a further REVISED+re-GO cycle. Confirmed blocking on `verify-skill-spec-to-test-mapping` (-003 GO'd without it) and `lo-advisory-intake-batch` (-003 GO'd without it); Codex flagged it at review on `lo-hygiene-assessment-skill-build` (-003 NO-GO). The fix adds a presence check to the bridge-compliance-gate (PreToolUse Write on `bridge/**`) so an implementation proposal requesting source/test/config work that lacks a substantive `## Requirement Sufficiency` subsection is rejected at Write-time, before GO.

**Cycle-14 triage (this session) confirms WI-3439 is genuinely OPEN.** Live read of `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (the tracked source-of-truth; `.claude/hooks/bridge-compliance-gate.py` is its byte-for-byte activation): the gate already enforces `## Specification Links` (presence + placeholder rejection) and the `## Owner Decisions / Input` section gate, and already parses `bridge_kind` (`BRIDGE_KIND_LINE_RE`), status (`_first_nonblank_line`), and `target_paths` (`_target_paths_from_content`) for its project-linkage metadata gate — but there is **no `Requirement Sufficiency` check** anywhere in the gate. So the fix is a clean mirror of the existing section-presence enforcement, reusing the gate's existing machinery.

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-3439 is the backlog authority for this fix (P2 bridge-compliance enforcement-gap improvement). *Note on `CLAUSE-VISIBILITY-BULK-OPS`:* this proposal is **single-WI scope** (one tracked work item, one tracked hook file + one test), not a bulk operation. The bulk-ops clause is triggered by the spec citation but is `not_applicable` here: no inventory artifact, no formal-artifact-approval packet, no Phase/Path-deferred decision marker, and no broad review packet are required — the standard implementation-proposal + LO-review path is the appropriate visibility surface.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001` (created via owner AUQ 2026-06-14, DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION; includes WI-3439; allows `source`, `test_addition`, `hook_upgrade`, `config`).
- **`.claude/rules/file-bridge-protocol.md`** § "Mandatory Implementation-Start Authorization Metadata" — defines the `## Requirement Sufficiency` subsection with exactly one operative state (`Existing requirements sufficient` OR `New or revised requirement required before implementation`). This gate check enforces that contract at Write-time, before GO, complementing the post-GO `implementation_authorization.py begin` check.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — the bridge-compliance-gate protects bridge artifact integrity; this fix strengthens that enforcement without altering `bridge/INDEX.md` or any bridge workflow state.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked; this check sits alongside the existing project-linkage gate.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps each acceptance criterion to an executed test.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — both `target_paths` are in-root under `E:\GT-KB`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked enforcement addition with explicit test coverage.

## Requirement Sufficiency

Existing requirements sufficient. The enforcement gap is documented (WI-3439 + the three confirmed bypass incidents), cycle-14 triage confirmed the gate has no such check, the bounded PAUTH authorizes the `source` + `test_addition` + `hook_upgrade` work, and `.claude/rules/file-bridge-protocol.md` defines the `## Requirement Sufficiency` one-operative-state contract this check enforces. No new or revised formal specification is required.

## Prior Deliberations

- **`DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION`** — owner AUQ (2026-06-14, cycle 14) authorizing WI-3439 (and siblings 3448/4396/3384) under the new bounded PAUTH.
- **The existing `## Specification Links` and `## Owner Decisions / Input` section gates in `bridge-compliance-gate.py`** — the proven enforcement pattern this fix mirrors (presence + placeholder-content rejection, gated on the implementation-proposal trigger). The new check reuses `_collect_section_lines`, the placeholder-token detection, and the `bridge_kind`/status/`target_paths` parsing that already exist.
- **WI-3448 (sibling in this batch)** — fixes the gate's status-trigger so heading-first proposals are also covered. WI-3439's check is wired through the SAME implementation-proposal trigger, so it automatically benefits from the WI-3448 fix; the two compose rather than conflict.
- **`scripts/implementation_authorization.py begin`** — the post-GO gate that currently catches the omission (too late). This check moves the enforcement to Write-time so the omission is caught before GO, eliminating the REVISED+re-GO cycle.
- _Live semantic deliberation search was not run during authoring (the WI-4519 always-on-LIKE-merge fix this session is in-flight; per the standing caution prior-decision context was gathered from the live gate source + the file-bridge-protocol contract instead)._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION`** — owner AUQ (2026-06-14, cycle 14) authorizing WI-3439 under `PAUTH-…-COMPLIANCE-DISPATCH-BATCH-001` (allowed: `source`, `test_addition`, `hook_upgrade`, `config`; forbids formal-artifact + narrative-artifact mutation). This fix stays within that scope: it edits the tracked template hook (hook_upgrade) + adds a test. No formal-artifact or narrative-artifact mutation, no KB mutation.

## Design

In `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (the tracked source-of-truth; the `.claude/hooks/` copy is re-activated byte-for-byte as the implementation's final deployment step):

1. **New constant + helper `_requirement_sufficiency_section_gap(content) -> str | None`** mirroring the existing `## Specification Links` section check: locate the `## Requirement Sufficiency` heading, `_collect_section_lines` for its body, and return a deny-reason string when the section is ABSENT or PLACEHOLDER-ONLY (reusing the gate's existing placeholder-token set: `tbd`, `todo`, `n/a`, `none`, etc.). Additionally require the section to contain one of the two operative-state phrases per `file-bridge-protocol.md` (`Existing requirements sufficient` OR `New or revised requirement required before implementation`); a section with neither operative phrase is treated as non-substantive.
2. **Wire it into the gate's deny path** under the SAME trigger the project-linkage metadata gate uses: status is NEW/REVISED (via `_first_nonblank_line` + the WI-3448-fixed status detection), `bridge_kind` is NOT in the metadata-exempt set, and the proposal requests implementation work (it declares `target_paths` / `implementation_scope` for source/test/config). When all three hold and `_requirement_sufficiency_section_gap` returns a reason, the Write is denied with that reason (same deny-response shape as the existing section gates).
3. **Verdict files exempt:** a versioned bridge file whose first non-blank line is a bare status token (`GO`/`NO-GO`/`VERIFIED`/`ADVISORY`/`DEFERRED`/`WITHDRAWN`) is a verdict/evidence narrative, not an authoring artifact, and is NOT subject to this check — same exemption the existing section gates apply.
4. **Final deployment step (implementation phase):** re-activate `.claude/hooks/bridge-compliance-gate.py` from the updated template (byte-for-byte) so the live hook carries the new check. The template is the canonical source; the `.claude/` activation is a deployment copy.

No change to the existing Specification Links / Owner Decisions gates, to the status/`target_paths` parsing, or to any non-implementation-proposal path.

## Verification Plan (Specification-Derived)

| Acceptance criterion | Test (in `platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py`) | Method |
|---|---|---|
| Implementation proposal lacking `## Requirement Sufficiency` is DENIED at Write-time (WI-3439 root) | `test_missing_requirement_sufficiency_denied` | NEW implementation_proposal content with target_paths but no `## Requirement Sufficiency` → gate returns deny |
| Placeholder-only section is DENIED | `test_placeholder_requirement_sufficiency_denied` | section present but body is `tbd`/`n/a` → deny |
| Section without an operative-state phrase is DENIED | `test_requirement_sufficiency_without_operative_state_denied` | section present with prose but neither operative phrase → deny |
| Substantive section with an operative state PASSES | `test_substantive_requirement_sufficiency_allowed` | section states `Existing requirements sufficient` (+ rationale) → allow (no deny from this check) |
| Non-implementation proposal (no target_paths) is NOT gated | `test_non_implementation_proposal_not_gated` | NEW content with `bridge_kind` exempt / no target_paths → this check does not fire |
| Verdict files (GO/NO-GO/VERIFIED) are exempt | `test_verdict_files_exempt` | content opening with a bare `GO`/`NO-GO`/`VERIFIED` token → not gated |
| Composes with WI-3448 trigger (status detection) | `test_uses_shared_status_trigger` | the check is gated on the same status-detection helper as the project-linkage gate (asserts no independent first-line logic) |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on both changed files; `python -m pytest platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py -q --tb=short`; plus the existing bridge-compliance-gate regression suite must still pass (Spec Links + Owner Decisions + project-linkage gates unchanged); and confirm the `.claude/hooks/` activation is byte-identical to the updated template.

## Risk / Rollback

- **Risk: low-moderate.** One new helper + one new wired check in the gate, mirroring two existing checks; one new test. The gate is a PreToolUse Write hook on `bridge/**` — a false-positive deny would block a legitimate proposal Write, so the check is conservative (it fires ONLY for NEW/REVISED implementation proposals that declare target_paths AND lack a substantive section, matching the existing project-linkage gate's trigger). The verdict-file exemption and the non-implementation exemption prevent over-firing.
- **Self-consistency:** this very proposal carries a substantive `## Requirement Sufficiency` section with an operative state, so it would pass its own check — a useful sanity anchor for the implementer.
- **Rollback:** revert the gate helper + wiring + delete the test, and re-activate the prior `.claude/hooks/` copy. No migration, no schema change, no KB mutation.

## Recommended Commit Type

`feat:` — net-new enforcement capability (a new bridge-compliance-gate check), closing the documented Write-time enforcement gap rather than repairing existing behavior. Per the Conventional Commits discipline (`.claude/rules/file-bridge-protocol.md`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
