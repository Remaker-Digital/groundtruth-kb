NEW

# Implementation Proposal — Document Artifact Author Provenance Contract (WI-3399)

bridge_kind: implementation_proposal
Document: gtkb-document-author-provenance-contract
Version: 001
Author: Prime Builder (Claude Opus 4.7, harness B)
Date: 2026-06-04 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: ff01ba72-8bce-49fd-ab2f-70a0ccb9d597
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, autonomous /loop dynamic mode

Source advisory: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-27-13-24-DOCUMENT-ARTIFACT-AUTHOR-PROVENANCE-GAP.md (Codex Prime Builder, harness A, 2026-05-27)

Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Work Item: WI-3399
work_item_ids: [WI-3399]
target_paths: ["scripts/document_author_metadata.py", "scripts/check_document_author_metadata.py", "platform_tests/scripts/test_document_author_metadata.py", ".claude/hooks/document_author_provenance_gate.py", ".codex/gtkb-hooks/document_author_provenance_gate.py", ".claude/settings.json", ".codex/hooks.json", "config/governance/document-author-provenance.toml", "groundtruth.db"]
spec_ids: ["GOV-DOCUMENT-AUTHOR-PROVENANCE-001"]

Project membership covering this WI: PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3399 (version 1, active, no expiration; created in this session via `gt projects add-item PROJECT-GTKB-RELIABILITY-FIXES WI-3399`).

Recommended commit type: feat

---

## Claim

Implement the document-artifact author-provenance contract recommended by the LO advisory INSIGHTS-2026-05-27-13-24, with scope and structural choices fixed by the owner-grilling AUQ recorded below (Owner Decisions / Input section). Specifically:

1. Create a new governance specification `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` recording the contract.
2. Build a reusable provenance helper at `scripts/document_author_metadata.py` (promoting the six-field pattern from the bridge-specific `scripts/bridge_author_metadata.py`).
3. Build an audit checker at `scripts/check_document_author_metadata.py`.
4. Wire a PreToolUse Write hook (`document_author_provenance_gate.py`) on Claude Code + Codex parity that mechanically enforces the contract for new document artifacts across the 5 governed surfaces.
5. Add focused tests under `platform_tests/scripts/test_document_author_metadata.py`.
6. Configure governed surfaces and exclusions in `config/governance/document-author-provenance.toml`.

This is a forward-only contract: existing unprovenanced files are explicitly out of scope per the owner Q2 AUQ.

## Specification Links

Specifications carried forward from the LO advisory's surveyed surface (the applicability preflight gate reads this section directly):

- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval packets required for all GOV/DCL/SPEC inserts; this proposal will generate a packet for `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` at impl time.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance umbrella; provenance is a fundamental artifact-orientation discipline.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; provenance contract extends the existing bridge-author-metadata enforcement to non-bridge document surfaces.
- `GOV-RELIABILITY-FAST-LANE-001` — fast-lane governance for reliability defects with bounded scope; this proposal is one such (covers a P1 audit gap).
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project authorization mandate; the standing PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING covers this WI via active membership.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — PAUTH envelope structure.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — PAUTH does not bypass bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec linkage mandate.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived testing mandate.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle trigger chain (defect-class WI → fix → test → bridge artifact).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development; provenance is a tier-zero artifact property.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — root-boundary; all work stays inside `E:\GT-KB` and outside `applications/`.

New specifications drafted by this proposal:

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — the new governance contract per owner Q3.

## Owner Decisions / Input

Owner-grilling-gate AUQ conducted 2026-06-04 UTC per `.claude/rules/peer-solution-advisory-loop.md` § "Owner-Grilling Gate (Authority: GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001)". The 4 questions and owner answers below are the durable approval evidence required by `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` and recorded in `memory/pending-owner-decisions.md` via the owner-decision-tracker hook.

| Q | Topic | Owner answer |
|---|-------|--------------|
| Q1 | Scope: which markdown surfaces? | **All 5 surfaces** (bridge/, .claude/rules/, independent-progress-assessments/, memory/, docs/). |
| Q2 | Backfill posture for existing files? | **Out of scope (forward-only)**. Contract applies to files written AFTER implementation; existing files grandfathered. |
| Q3 | Rule home / authority? | **New GOV-DOCUMENT-AUTHOR-PROVENANCE-001**. Dedicated governance spec, cross-linked to `GOV-ARTIFACT-APPROVAL-001`. |
| Q4 | Disposition? | **Adopt** — file impl proposal with captured scope. (This proposal.) |

The Adopt answer at Q4 is the operative owner-approval evidence required by the peer-solution-advisory-loop rule § Approval-Gate. Per-artifact formal-artifact-approval packets for `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` will be generated and owner-approved AT IMPL TIME (after LO GO on this proposal); they are not required at proposal time.

## Source Advisory

`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-27-13-24-DOCUMENT-ARTIFACT-AUTHOR-PROVENANCE-GAP.md` filed by Codex Prime Builder (harness A, GPT-5 Codex) on 2026-05-27. The advisory found:

- bridge/ has 4134 markdown files but only 136 with complete six-field author metadata.
- .claude/rules/ (19 files), IPA/ (1519 files), memory/ (138 files), docs/ (8 files) all have zero files with complete author metadata.
- The deterministic enforcement (`scripts/bridge_author_metadata.py`) is bridge-scoped; non-bridge content is returned unchanged.
- This weakens auditability exactly where GT-KB relies on cross-harness review.

The advisory recommended (and the owner has now Adopted): a general document-artifact author-provenance contract covering the 5 surfaces above.

## Prior Deliberations

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-27-13-24-DOCUMENT-ARTIFACT-AUTHOR-PROVENANCE-GAP.md` — source LO advisory (Codex Prime Builder, 2026-05-27).
- Owner-grilling AUQ on 2026-06-04 UTC (this session) — the 4 questions captured above; recorded in `memory/pending-owner-decisions.md`.
- `bridge/gtkb-in-source-provenance-anchors-001-prop-004.md` — adjacent thread on in-source provenance anchors (currently NO-GO; distinct concern — that thread governs SOURCE-CODE citation anchors, not DOCUMENT-ARTIFACT creation provenance). Cited as the advisory called out the relationship.
- `scripts/bridge_author_metadata.py` — the bridge-specific provenance helper that this proposal generalizes from.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — implementation aligns with the deterministic-services bias (the checker + hook are deterministic services that move per-session author-metadata writing from chat-loop to mechanical enforcement).

## Requirement Sufficiency

Existing requirements sufficient as augmented by the 4 owner AUQ answers above. No new requirement disambiguation needed; the AUQ produced the durable scoping evidence required by the peer-solution-advisory-loop rule. Acceptance criteria are derived in the Specification-Derived Verification Plan below.

## Proposed Scope

### Governed Surfaces (per Q1)

The contract governs newly-created markdown files in:

- `bridge/**/*.md`
- `.claude/rules/**/*.md`
- `independent-progress-assessments/**/*.md`
- `memory/**/*.md`
- `docs/**/*.md`

Exclusions registered in `config/governance/document-author-provenance.toml`:

- Vendored / generated files (e.g., `groundtruth-kb/scaffold/templates/**` if any markdown templates exist).
- Historical archive directories (e.g., `archive/**`, `**/superseded-*/`).
- Specific known-exception paths (registered as the contract lands; owner-AUQ-gated additions).

### Backfill Posture (per Q2)

Forward-only. The contract enforces on Write of NEW document artifacts in the governed surfaces. Existing files at impl time are grandfathered with no audit pressure to retrofit. Owner may file a separate backfill WI in a future session if/when desired (not in this proposal's scope).

### Rule Home (per Q3)

A new governance spec `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` recorded in MemBase with:

- `type='governance'`
- `status='specified'` (post-approval)
- `title='Document Artifact Author Provenance Contract'`
- Body content explaining the six-field requirement, the governed surfaces list, exclusion semantics, and the cross-reference to `GOV-ARTIFACT-APPROVAL-001` and the bridge-specific provenance pattern.
- `assertions` field containing the machine-checkable predicates (governed-surface match + six-field presence + non-placeholder values).

### Helper Architecture

The implementation creates a new shared helper rather than extending `scripts/bridge_author_metadata.py`. Rationale:

- The bridge helper is tied to bridge-specific concerns (status tokens, `Document:` line, version arithmetic).
- Promotion via inheritance/composition keeps bridge enforcement byte-for-byte stable (no regression risk to `bridge_author_metadata.py` consumers including the bridge-compliance gate).
- The new helper exports a `REQUIRED_AUTHOR_FIELDS` constant that both helpers consume so the six-field set has a single source of truth.

### Six-Field Contract

Per the existing bridge pattern at `scripts/bridge_author_metadata.py:18`:

1. `author_identity:` — human-readable identity (e.g., "Claude Code Prime Builder", "Codex Prime Builder", "Antigravity Loyal Opposition").
2. `author_harness_id:` — durable harness ID (A, B, C, …).
3. `author_session_context_id:` — installation-stable session context ID.
4. `author_model:` — model name (e.g., "Opus 4.7", "GPT-5 Codex").
5. `author_model_version:` — model version string (e.g., "claude-opus-4-7[1m]", "gpt-5-codex").
6. `author_model_configuration:` — config flags (e.g., "Claude Code CLI explanatory output style, 1M context").

### Enforcement Mechanism

PreToolUse Write hook (`document_author_provenance_gate.py`) registered in both `.claude/settings.json` and `.codex/hooks.json` (harness parity per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`):

- Hook fires on Write of any file matching the governed-surface glob.
- Hook reads the file content being written.
- If the file is a NEW creation (not an Edit) and lacks all 6 required fields → exit-block with explanatory error citing this proposal's bridge ID and the missing fields.
- If the file already exists in the working tree (Edit case) → no enforcement (forward-only per Q2).
- Hook is bypassable via an explicit `document_author_provenance_waiver: <DELIB-ID> — <reason>` line in the file (owner-waiver-style escape hatch, mirroring the clause-preflight waiver pattern).

Companion audit checker `scripts/check_document_author_metadata.py`:

- Read-only audit; flags missing-provenance files in governed surfaces.
- Supports `--changed-only` (use git diff for fast pre-commit checks) and full-tree scan.
- Output is structured JSON + human-readable summary.
- Used in CI and `gt project doctor` for ongoing visibility (separate WIs may wire those integrations post-VERIFIED).

## Implementation Plan (Slices)

This proposal is filed as one bridge thread; implementation will land in slices within this thread (REVISED-N or post-impl-report progression), not as separate bridge threads.

### Slice 1 — Helper + Tests

- Create `scripts/document_author_metadata.py` with `REQUIRED_AUTHOR_FIELDS`, `parse_author_metadata(text) -> dict`, `validate_author_metadata(text) -> ValidationResult`, `format_author_metadata(...) -> str`.
- Refactor `scripts/bridge_author_metadata.py` to import `REQUIRED_AUTHOR_FIELDS` from the new helper (single source of truth) without changing its public contract.
- Add `platform_tests/scripts/test_document_author_metadata.py` covering: complete-metadata acceptance, partial-metadata rejection, placeholder rejection (e.g., `author_model: TBD`), non-document-surface no-op, bridge backward compatibility.

### Slice 2 — Audit Checker

- Create `scripts/check_document_author_metadata.py` consuming the helper.
- Add `--changed-only`, `--surfaces`, `--exclude`, `--json` flags.
- Add tests covering: changed-only mode, exclusion patterns, multi-surface aggregation.

### Slice 3 — Config + Governance Spec

- Create `config/governance/document-author-provenance.toml` declaring governed surfaces + exclusions.
- Insert `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` to MemBase with body + assertions (requires owner-approval packet AT THIS POINT — gated by `GOV-ARTIFACT-APPROVAL-001` per the standard contract).

### Slice 4 — Hook + Registration

- Create `.claude/hooks/document_author_provenance_gate.py` PreToolUse Write hook.
- Create `.codex/gtkb-hooks/document_author_provenance_gate.py` (Codex parity).
- Register both in `.claude/settings.json` and `.codex/hooks.json`.
- Test against fixture files (create-new fixtures with/without complete metadata; verify block/pass behavior).

### Slice 5 — Verification + Post-Impl Report

- Run all preflights + tests against the live tree.
- Spot-check by attempting to Write a deliberately-incomplete fixture document; assert the gate blocks.
- File post-impl report referencing the slices' verification evidence.

## Specification-Derived Verification Plan

| Linked Spec | Verification Evidence (to be executed at impl time) |
|---|---|
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` (new) | Insert into MemBase via approval-packet-gated `gt spec record`; readback shows version 1, type=governance, status=specified, expected title + assertions. |
| `GOV-ARTIFACT-APPROVAL-001` | Approval packet generated and validated via `scripts/validate_formal_artifact_packet.py`; insertion gated on packet hash match. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | New GOV directly serves artifact-oriented governance; cross-reference recorded in body. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge thread visible in `bridge/INDEX.md`; all versions filed with valid status tokens; bridge_applicability_preflight passes. |
| `GOV-RELIABILITY-FAST-LANE-001` | Diff stat ≤ ~500 lines net (helper + checker + hook + tests + config + spec); P1 reliability-class. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This Specification Links section + applicability preflight on each REVISED/post-impl version. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This Specification-Derived Verification Plan table maps each spec to executable evidence. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | WI-3399 origin=defect (advisory-routing), this proposal triggered by AUQ resolution. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Implementation produces durable test + source + spec artifacts plus the bridge audit trail. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths inside `E:\GT-KB` and outside `applications/`. Verified by path inspection. |

Test commands (to be run at post-impl-report time):

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check \
    scripts/document_author_metadata.py \
    scripts/check_document_author_metadata.py \
    platform_tests/scripts/test_document_author_metadata.py \
    .claude/hooks/document_author_provenance_gate.py

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check \
    scripts/document_author_metadata.py \
    scripts/check_document_author_metadata.py \
    platform_tests/scripts/test_document_author_metadata.py \
    .claude/hooks/document_author_provenance_gate.py

groundtruth-kb/.venv/Scripts/python.exe -m pytest \
    platform_tests/scripts/test_document_author_metadata.py -v --tb=short

groundtruth-kb/.venv/Scripts/python.exe -m pytest \
    platform_tests/scripts/test_bridge_author_metadata.py -v --tb=short  # backward-compat regression check

python scripts/check_document_author_metadata.py --changed-only --json  # audit dry-run
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-document-author-provenance-contract
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-document-author-provenance-contract
```

## Risk / Rollback

- **Risk: medium.** Adds a new PreToolUse Write hook that gates all document writes on the 5 governed surfaces. A bug in the hook could block legitimate work. Mitigation: extensive test coverage in Slice 1+2 before the hook lands in Slice 4; the hook is forward-only so existing files are unaffected; the waiver escape hatch (`document_author_provenance_waiver: <DELIB-ID> — <reason>`) preserves emergency authorization paths.
- **Risk: low.** Backward compatibility for the bridge-author-metadata pattern. Mitigation: Slice 1 refactor of `bridge_author_metadata.py` preserves its public contract byte-for-byte (only imports `REQUIRED_AUTHOR_FIELDS` from the new helper); existing bridge tests must continue to PASS.
- **Rollback path:** disable the hook by removing its `.claude/settings.json` + `.codex/hooks.json` registrations (reversible without code change). Full rollback: revert all 5 slices' commits in reverse order. Helper + checker + spec can remain (read-only/advisory) if only the enforcement hook is rolled back.
- **Forward-compatibility:** the helper's exported `REQUIRED_AUTHOR_FIELDS` constant is the single source of truth — future surfaces (e.g., `applications/Agent_Red/CLAUDE.md` if Agent Red adopts the contract) can opt in by adding their surface to the config TOML without code changes.

## Open Decisions Required From Owner

None for this proposal filing. Future owner decisions (gated by AUQ + formal-artifact-approval packets) will be:

- At Slice 3: approve the formal-artifact-approval packet for `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`.
- At Slice 4: approve any protected-narrative-artifact edits if needed (initial scoping does not modify `.claude/rules/*.md`; the contract is enforced via the hook, not by adding a new rule file).

## Recommended Commit Type

`feat:` — net-new capability surface (governance contract + helper + checker + hook + tests + config + new spec). Diff stat estimate: ~500-800 lines net across slices, of which the spec body + tests are the bulk; the hook is small.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
