NEW

# gtkb-wi4693-supersession-hygiene-scanner - Supersession Hygiene Scanner

bridge_kind: prime_proposal
Document: gtkb-wi4693-supersession-hygiene-scanner
Version: 001
Author: Prime Builder / Codex
Date: 2026-06-23T15:27:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef0d4-5474-7af3-af31-4c8ab4cf4f7a
author_model: GPT-5
author_model_version: 2026-06-23
author_model_configuration: Codex desktop, Prime Builder interactive session

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4693

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/hygiene/supersession.py", "groundtruth-kb/src/groundtruth_kb/hygiene/__init__.py", "platform_tests/scripts/test_hygiene_supersession_cli.py"]

implementation_scope: cli_extension, source, test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
formal_artifact_mutation_in_scope: false

---

## Summary

Implement a bounded, read-only supersession hygiene scanner under the existing `gt hygiene` CLI surface. The scanner will detect live working-directory artifacts that advertise supersession, retirement, withdrawal, or obsolescence signals outside preserved audit-history locations, emit structured findings, and provide cautious remediation hints without deleting, moving, rewriting, or retiring any artifact.

This is the implementable source/test slice of WI-4693. It operationalizes the owner's supersession-hygiene concern from `DELIB-20265287` by giving agents a deterministic cheap check before they follow obsolete live clues. It deliberately leaves all destructive cleanup, formal GOV/SPEC/ADR/DCL amendment, and MemBase lifecycle mutation behind the existing bridge, approval, and owner-confirmation gates.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs use of the active project authorization as the bounded implementation authority for this snapshot member WI.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - constrains the proposal to the active PAUTH's included work-item set and allowed mutation classes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires this proposal and subsequent implementation report to move through the bridge rather than direct protected-file mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete relevant spec linkage before Loyal Opposition can approve implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the machine-readable Project Authorization, Project, and Work Item metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires verification evidence to map linked specs to executed tests before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - makes WI-4693 the durable work authority and requires completion evidence to resolve the backlog item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - supplies the artifact-lifecycle interpretation stance and requires formal artifact mutations to stay behind approval gates.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - frames supersession hygiene as durable artifact-graph maintenance rather than transient chat cleanup.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - names supersession, retired, lifecycle-state preservation, and confirmation-flow constraints this scanner must respect.
- `GOV-ARTIFACT-APPROVAL-001` - keeps all GOV/SPEC/ADR/DCL/REQ/PB mutations, if any are later needed, outside this source/test proposal unless separately approval-packeted.

## Prior Deliberations

- `DELIB-20265287` - primary owner decision set for the Activity-Envelope program; includes the WI-4693 supersession-hygiene concern: preserve rich audit trails, but remove or quarantine superseded/obsoleted live working-directory clues because agents infer meaning from names and structures.
- `DELIB-20265586` - owner mass project authorization; authorizes this project's snapshot member work items for bounded implementation with mutation classes `source`, `test_addition`, `hook_upgrade`, `cli_extension`, and `scaffold_update`, while preserving bridge, impl-start, spec-derived verification, formal-artifact approval, and ACID scope-expansion gates.
- `DELIB-S365-LAYER-A-HYGIENE-COHERENCE-AUTHORIZATION` - prior owner authorization for deterministic hygiene services, relevant because this proposal extends the same `gt hygiene` family instead of creating an ad hoc scanner.
- `DELIB-S365-WI-3418-OBSOLETED-BY-HYGIENE-SWEEP` - prior owner decision that obsoleted work can be retired by a hygiene service when the replacement path is explicit; relevant precedent for scanner-first obsolescence handling.

## Owner Decisions / Input

Owner approval is already present for this bounded implementation proposal through `DELIB-20265586` and the active PAUTH cited above. The WI-specific requirement source is `DELIB-20265287`, which captured the owner's supersession-hygiene concern as a first-class project item. No additional owner input is required for this read-only CLI/test slice because the proposal does not delete artifacts, move artifacts, mutate MemBase, or alter formal GOV/SPEC/ADR/DCL/PB/REQ records.

## Requirement Sufficiency

Existing requirements sufficient - `DELIB-20265287` defines the supersession-hygiene requirement, `DELIB-20265586` plus the active PAUTH provides bounded project implementation authority, and the linked artifact-oriented governance specs define the lifecycle-state and approval constraints. No new or revised formal requirement is required before implementing this read-only scanner slice.

## Proposed Implementation

1. Add `groundtruth_kb.hygiene.supersession` with pure functions/dataclasses for scanning a repository tree for supersession/retirement/withdrawal/obsolescence markers in live working-directory files.
2. Preserve audit history by default: exclude append-only bridge numbered files, formal approval packets, Deliberation Archive records, `.git`, `.gtkb-state`, local worktrees, caches, and test temp directories from actionable cleanup findings unless explicitly included by tests.
3. Emit structured findings with path, line, marker class, matched excerpt, classification, and remediation hint. Findings are advisory evidence only.
4. Add a `gt hygiene supersession-scan` command with JSON output, optional markdown output directory, `--report-only/--fail-on-findings`, and root selection following the existing `gt hygiene sweep` conventions.
5. Export the scanner API from `groundtruth_kb.hygiene.__init__`.
6. Add focused platform tests for detection, audit-history exclusion, CLI JSON shape, read-only behavior, and exit-code policy.

## Code Quality Baseline

| Baseline | Current State | Proposal Requirement |
| --- | --- | --- |
| Existing CLI pattern | `gt hygiene sweep` is read-only against the repo and writes only optional output under `.gtkb-state`. | New command follows the same Click style and read-only contract. |
| Existing hygiene package | `groundtruth_kb.hygiene.sweep` uses dataclasses, pure scan functions, JSON/Markdown emitters, and focused tests. | New scanner uses the same package-local style instead of embedding logic directly in `cli.py`. |
| Formal artifact gate | `GOV-ARTIFACT-APPROVAL-001` is verified and not waived by the PAUTH. | Implementation must not mutate formal artifacts or encode approval bypasses. |
| Verification surface | Existing hygiene tests live under `platform_tests/scripts/`. | Add `platform_tests/scripts/test_hygiene_supersession_cli.py` and run it with the repo venv. |

## Spec-Derived Verification Plan

| Specification / Requirement | Derived Verification | Expected Result |
| --- | --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4693-supersession-hygiene-scanner` after GO. | Packet authorizes only the four target paths and WI-4693 under the active PAUTH. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Mandatory bridge preflights before filing and Loyal Opposition review before implementation. | Applicability preflight passes, clause preflight has zero blocking gaps, and bridge compliance accepts metadata/target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_hygiene_supersession_cli.py -q --no-header` | Tests prove scanner behavior, CLI JSON shape, read-only behavior, and exit policy. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-APPROVAL-001` | Unit/CLI tests with fixture files containing supersession markers in live files and audit-history files. | Live files are reported as candidates; audit-history files are preserved/excluded; no deletion, move, MemBase mutation, or formal-artifact mutation occurs. |
| Repository style gates | `ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/hygiene/supersession.py groundtruth-kb/src/groundtruth_kb/hygiene/__init__.py platform_tests/scripts/test_hygiene_supersession_cli.py` and matching `ruff format --check` on the same paths. | Lint and format checks pass on touched files. |

## Pre-Filing Preflight

Applicability preflight was run against this draft before filing:

- Command: `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --content-file .gtkb-state\propose-drafts\gtkb-wi4693-supersession-hygiene-scanner-001.md`
- Result: `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- Packet hash: `sha256:4400329211bb41841f32794765dfe5f8ff4fea69f7e07e4c13362ce96ac1ab02`

Clause preflight was run against this draft before filing:

- Command: `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --content-file .gtkb-state\propose-drafts\gtkb-wi4693-supersession-hygiene-scanner-001.md`
- Result: exit 0
- `must_apply: 3`
- `Evidence gaps in must_apply clauses: 0`
- `Blocking gaps (gate-failing): 0`

Phantom-spec sweep was run against this draft before filing:

- Result: all cited `GOV`/`ADR`/`DCL` specification IDs exist in the live `specifications` table.

## Risk / Rollback

Risk is low-to-moderate: a noisy scanner could train agents to over-trust candidate findings or ignore legitimate historical context. Mitigation: keep output advisory/read-only, preserve audit-history exclusions, classify findings as candidates, and require later governed confirmation for any cleanup.

Rollback is a normal source/test revert of the four target paths. Because this proposal does not mutate MemBase, formal artifacts, or live content artifacts, rollback does not require data repair or artifact retirement.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4693-supersession-hygiene-scanner`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat` - the implementation would add a new read-only `gt hygiene` CLI capability with regression tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
