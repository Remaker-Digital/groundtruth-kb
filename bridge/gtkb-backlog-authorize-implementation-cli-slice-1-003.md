REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 5a45a93f-e7c3-467b-a741-f447d2d6cd16
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI, default reasoning, explanatory output style
author_attribution_note: GTKB_HARNESS_NAME=claude set this session due to dual-PB role-map drift (B and C both hold prime-builder); durable role for B is prime-builder.

Project Authorization: PAUTH-WI-3494-BACKLOG-AUTHORIZE-IMPLEMENTATION-CLI-001
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3494

# GT-KB gt backlog authorize-implementation CLI - Slice 1 - Implementation Proposal - 003 (REVISED after NO-GO -002)

bridge_kind: implementation_proposal

Document: gtkb-backlog-authorize-implementation-cli-slice-1
Version: 003 (REVISED)
Date: 2026-06-01 UTC
Session: S379

## Response to Loyal Opposition NO-GO (-002)

All four findings are accepted and addressed; no owner decision is required (per the NO-GO, the REVISED proceeds under the same WI/PAUTH with unchanged mutation classes `cli_extension` + `test_addition`). Each fix was verified against the live checkout.

| Finding | Severity | Resolution |
|---|---|---|
| F1 - non-regression test path does not exist | P1 | `target_paths` and T9 retargeted to the live CLI-test convention `platform_tests/scripts/` (verified: `platform_tests/scripts/test_cli_backlog_add.py` exists; there is no `groundtruth-kb/tests/` CLI-test surface). The new test is now `platform_tests/scripts/test_cli_backlog_authorize_implementation.py`. All verification commands are now environment-explicit (repo venv interpreter + `PYTHONPATH=groundtruth-kb/src`). |
| F2 - owner-decision authority boundary untested | P1 | The Implementation Plan now specifies the owner-authority predicate explicitly (the cited deliberation must have `source_type='owner_conversation'` AND `outcome='owner_decision'`), and two new negative tests are added: T11 (a non-owner deliberation is rejected fail-closed) and T12 (supplying both `--owner-decision` and fresh AUQ evidence is rejected). This closes the gap that `KnowledgeDB.insert_project_authorization()` (db.py:4216) only checks deliberation existence, not authority. |
| F3 - overclaim of `gt projects authorize` approval-packet behavior | P2 | Corrected. Verified that `insert_project_authorization()` performs no approval-packet generation on initial (version 1) creation; only `_validate_spec_amendment_approval_packet` runs for version > 1 spec amendments. The Governance Preservation section now states accurately that the owner-decision deliberation IS the approval evidence and `gt projects authorize` writes the PAUTH row citing it. |
| F4 - missing advisory spec | P3 | `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified, architecture_decision) added to Specification Links. |

## Summary

Add a governed `gt backlog authorize-implementation` CLI subcommand (with `python -m groundtruth_kb backlog authorize-implementation` parity) that collapses the multi-call project-authorization plumbing required before filing a bridge proposal for an owner-selected backlog work item into a single deterministic command. Implements WI-3494 (broadened from its original `--auto-create-pauth on gt backlog add` framing to the more general authorize-implementation command).

**Why this advances the owner-burden-reduction objective (operating-model section 1; DELIB-S312 Deterministic Services Principle):** When the owner selects a backlog work item for implementation, Prime Builder cannot file the bridge proposal until the work item is covered by an active project authorization whose envelope the Write-time bridge-compliance gate accepts. For a newly-selected member work item that is not already on a PAUTH allowlist, that means three governed steps performed by hand: (1) `gt deliberations record` to capture the owner-decision basis, (2) `gt projects authorize` to create or extend a project-authorization envelope explicitly including the work item and at least one governing specification, then (3) cite the resulting PAUTH in the proposal header. This session (S379) performed exactly that ceremony by hand to authorize this very work item (DELIB-2547, then PAUTH-WI-3494-BACKLOG-AUTHORIZE-IMPLEMENTATION-CLI-001). That plumbing is repetitive, deterministic, and template-following; per DELIB-S312 it belongs in a service, not in per-item session ceremony.

This Slice 1 delivers the **create** path: given a work item and owner-decision evidence, the command resolves the work item's active project, records the owner-decision deliberation when fresh evidence is supplied (or validates an existing one as owner-authority), creates a narrow project authorization including the work item plus the supplied governing specs and mutation classes, and reports the deliberation id and PAUTH id ready to cite. The **extend-existing-allowlist** path (the S379 "PAUTH exists but its allowlist omits the work item" case - which is a version > 1 amendment and therefore subject to `_validate_spec_amendment_approval_packet`), automatic governing-spec selection, and integration with `gt backlog add` are deferred to Slice 2 to keep this slice a single clean, additive `cli_extension`.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - the standing backlog as the durable cross-session work authority surfaced via `gt backlog`. This proposal adds a governed authorization-preparation surface adjacent to that authority; it operates on one work item per invocation (not a bulk backlog operation; see Clause Scope Clarification).
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the bounded owner-authorization-envelope contract. This command produces or reuses an authorization envelope from owner-decision evidence; it never fabricates owner authorization. The cited work item WI-3494 is explicitly included in the active `PAUTH-WI-3494-BACKLOG-AUTHORIZE-IMPLEMENTATION-CLI-001` envelope (owner-decision basis DELIB-2547).
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the envelope schema this command writes through the existing governed `gt projects authorize` path; mutation classes are `cli_extension` and `test_addition`, within the cited PAUTH's `allowed_mutation_classes`.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - every authorization the command creates must include at least one governing specification; the command requires `--include-spec` (fail-closed) so no spec-less authorization is ever produced.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected behavior preserved: the produced authorization does NOT bypass bridge GO, the implementation-start packet, `target_paths`, spec-derived tests, the post-implementation report, or VERIFIED. The command prepares authorization evidence; it does not implement.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - the Write-time gate this friction originates from. The command makes producing a conformant authorization cheap; it does NOT alter, relax, or bypass the gate. The cross-gate `included_work_item_ids` semantic divergence is captured separately as a backlog finding (see Prior Deliberations) and is explicitly out of scope here.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the `Project Authorization` / `Project` / `Work Item` metadata lines at this file's header satisfy the linkage requirement; this proposal's own authorization is the live PAUTH cited above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - filed as a `REVISED` entry at the top of the thread in `bridge/INDEX.md`; append-only; no prior versions rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this Specification Links section enumerates the governing surface; the Spec-Derived Verification Plan provides the spec-to-test mapping.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Spec-Derived Verification Plan below lists executable spec-derived tests against the live checkout; the post-implementation report will carry the spec-to-test mapping with executed results.
- `GOV-08` - KB is truth: authorization envelopes and owner-decision deliberations are written through governed, append-only MemBase paths, never ad-hoc.
- `GOV-12` - the new command does not create work items, so it does not itself trigger GOV-12 linked-test creation; the proposal's own implementation carries spec-derived tests.
- `GOV-RELIABILITY-FAST-LANE-001` - cited for scope boundary: WI-3494 is `improvement`-origin and adds a new CLI surface, so it is NOT fast-lane eligible; this proposal correctly uses the standard project path with a dedicated PAUTH rather than the reliability fast-lane standing authorization.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths reside in-root under `E:\GT-KB` (the new CLI module under `groundtruth-kb/`, the new test under `platform_tests/`, the bridge file under `bridge/`); no `applications/` path is touched.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory; added per NO-GO -002 F4) - durable artifact graph: the command strengthens the owner-decision -> authorization -> work-item linkage the artifact graph depends on.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) - artifact-oriented governance baseline preserved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) - the command is a governed surface for the authorization-envelope lifecycle transition.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the Deterministic Services Principle. This proposal is a direct application: repetitive multi-step authorization plumbing where the AI's substantive contribution is small belongs behind a service.
- `DELIB-2547` - the S379 disposition decision ("Reduce friction, keep gates") and the owner-decision basis for this work item's authorization (`source_type='owner_conversation'`, `outcome='owner_decision'`). It explicitly directed advancing the friction-reduction via the deterministic-authorization command path, coordinating with WI-3494, and filing a normal bridge proposal, with no gate-semantics change.
- The S379 investigation that produced DELIB-2547 established (with live evidence) that the project-authorization friction is allowlist-specific: 38/41 active PAUTHs use restrictive `included_work_item_ids` allowlists, while `PROJECT-GTKB-RELIABILITY-FIXES` uses a standing membership-only PAUTH and never hits the friction. This proposal targets the allowlist-PAUTH plumbing cost without changing any gate.
- The cross-gate `included_work_item_ids` semantic divergence (Write-time restrictive vs impl-start additive) was captured this session as a separate backlog finding, WI-3510, for separate governance consideration; this proposal deliberately does NOT touch that divergence or either gate.
- No prior deliberation proposed or rejected a `gt backlog authorize-implementation` command; a deliberation search for the topic returned zero prior decisions, and the Loyal Opposition reviewer independently confirmed zero priors at -002. The gap is an acknowledged absence, not a previously-considered-and-rejected design.

## Owner Decisions / Input

This proposal proceeds under owner authorization established through two channels, both recorded:

1. **Disposition decision (AskUserQuestion, S379, 2026-05-31), archived as DELIB-2547** (`source_type=owner_conversation`, `outcome=owner_decision`, `detected_via: ask_user_question`): the owner was presented the S379 authorization-friction findings and chose "Reduce friction, keep gates" over "Reconcile the two gates" and "Capture findings only." That decision directs advancing the friction-reduction via this command path while leaving the gates intact.
2. **Project-scoped implementation authorization (durable):** WI-3494 is explicitly included in the active `PAUTH-WI-3494-BACKLOG-AUTHORIZE-IMPLEMENTATION-CLI-001` envelope (owner-decision basis DELIB-2547), which authorizes `cli_extension` + `test_addition` work bounded to this command build.

No additional per-artifact owner approval is required for this `cli_extension`: it creates CLI code + tests only and no canonical GOV/ADR/DCL/SPEC artifact. Any owner-decision evidence the command consumes at runtime (`--owner-decision` / `--auq-id`) remains the owner's authority; the command never fabricates it.

## Requirement Sufficiency

Existing requirements sufficient. No new specification, ADR, DCL, GOV, or PB is needed. The underlying governed methods (`gt deliberations record`, `gt projects authorize`) already exist and already enforce their approval contracts; this proposal authorizes only a CLI orchestration surface (`cli_extension`) plus spec-derived tests (`test_addition`) over those existing methods, adding the owner-authority predicate on the `--owner-decision` input (F2) at the CLI layer.

## Governance Preservation (Not an Authorization Bypass)

This is the load-bearing design constraint. The command does NOT let Prime Builder grant itself authorization. It REQUIRES owner-decision evidence as input and refuses (non-zero exit, no MemBase write) when none is supplied, exactly as the manual path does:

- It accepts an existing `--owner-decision DELIB-NNNN` (validated at the CLI layer as owner-authority: `source_type='owner_conversation'` AND `outcome='owner_decision'`, rejecting non-owner deliberations such as `lo_review`, `bridge_thread`, `prime_builder_investigation`, or any `outcome` other than `owner_decision`), OR records a fresh `owner_conversation` deliberation from `--auq-id` + `--auq-answer` + `--decision-content-file` through the already-governed `gt deliberations record` service (which DOES emit a formal-artifact-approval packet for the deliberation it creates).
- It then creates the project authorization through the already-governed `gt projects authorize` path. Per the live implementation (`KnowledgeDB.insert_project_authorization()`, db.py:4214-4217), initial (version 1) creation validates that the project exists, the owner-decision deliberation exists, and the included specs satisfy the active-spec rule, then writes the PAUTH row; it does NOT generate a separate approval packet for initial creation. The owner-decision deliberation IS the approval evidence the PAUTH cites. (Approval-packet validation applies only to version > 1 spec amendments via `_validate_spec_amendment_approval_packet`, which is the Slice 2 extend path, out of scope here.)
- It collapses the PLUMBING (resolve project -> validate/record deliberation -> create authorization -> report ids) from three hand-run governed calls into one; it does not collapse, weaken, or remove any owner-approval requirement, and it touches no gate logic.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` is preserved end to end: the produced PAUTH still requires a bridge proposal, Codex GO, an implementation-start packet, spec-derived tests, a post-implementation report, and VERIFIED before any implementation lands.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal adds a single-work-item authorization-preparation command (one work item authorized per invocation), not a bulk standing-backlog operation. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` governs bulk transitions; it is satisfied here by the single-work-item design plus this proposal-as-review-packet. The command does not iterate over the backlog, perform batch authorization, or change backlog ordering.

## target_paths

- `groundtruth-kb/src/groundtruth_kb/cli_backlog_authorize_implementation.py` (new module: request/error dataclasses, project resolution, fail-closed validation including the owner-authority predicate on `--owner-decision`, delegation to the existing governed deliberations-record and projects-authorize internals; mirrors the structure of `cli_backlog_add.py`)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (register `authorize-implementation` under the `backlog` group, mirroring the `add` registration)
- `platform_tests/scripts/test_cli_backlog_authorize_implementation.py` (new: spec-derived tests, co-located with the existing CLI-test surface `platform_tests/scripts/test_cli_backlog_add.py` per F1)

No other files are authorized for mutation. `groundtruth.db` is NOT a target_path: this slice ships CLI code + tests only; the command is exercised against ephemeral test databases in the test suite, per the existing `gt backlog add` test pattern. No `db.py` schema or method change is required (the command reuses existing governed methods; the owner-authority predicate is enforced in the new CLI module).

## Implementation Plan

After Codex GO:

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-backlog-authorize-implementation-cli-slice-1` to create the implementation-start packet from the GO (validates coverage via WI-3494's explicit inclusion in the cited PAUTH and the cli_extension/test_addition mutation classes against the revised `target_paths`).
2. Create `groundtruth-kb/src/groundtruth_kb/cli_backlog_authorize_implementation.py` mirroring `cli_backlog_add.py`:
   - An `AuthorizeImplementationError(Exception)` and an `AuthorizeImplementationRequest` dataclass.
   - Resolve the work item's active project from `current_project_work_item_memberships` (single active membership), or accept `--project`; fail closed when the work item has zero active memberships or multiple and `--project` is omitted.
   - Owner-decision evidence: require exactly one of `--owner-decision DELIB-NNNN` XOR (`--auq-id` + `--auq-answer` + `--decision-content-file`); fail closed when neither or both are supplied (F2 conflict guard).
   - For the existing-DELIB path, validate the deliberation is owner-authority: load it and require `source_type == 'owner_conversation'` AND `outcome == 'owner_decision'`; fail closed (no PAUTH, no packet) otherwise (F2). This predicate lives in the CLI module because `insert_project_authorization()` checks only existence (db.py:4216).
   - For the fresh-AUQ path, delegate to the existing governed deliberations-record path (which records `source_type='owner_conversation'`, `outcome='owner_decision'` and emits its packet).
   - Require at least one `--include-spec` (GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001) and at least one `--allowed-mutation`.
   - Create the authorization through the existing governed projects-authorize path, including the work item, the governing specs, and the mutation classes, citing the deliberation id.
   - Support `--dry-run` (report the resolved project, deliberation id, and proposed authorization envelope without writing) and `--json`.
3. Register `gt backlog authorize-implementation` in `cli.py`'s `backlog` group.
4. Author `platform_tests/scripts/test_cli_backlog_authorize_implementation.py` with the spec-derived tests below.
5. Run the verification plan; file the post-implementation report for Codex VERIFIED review.

## Spec-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, the spec-derived verification the implementation report will execute. **Environment (per NO-GO -002 F1):** all commands run from the `E:\GT-KB` root using the repo venv interpreter `groundtruth-kb\.venv\Scripts\python.exe` with `PYTHONPATH=groundtruth-kb/src` set; bare `python` does not resolve `groundtruth_kb` in this environment. Below, `VPY` denotes `groundtruth-kb\.venv\Scripts\python.exe`.

| # | Verification | Spec Coverage | Command | Expected |
|---|---|---|---|---|
| T1 | Command exists + is registered | GOV-STANDING-BACKLOG-001 | `VPY -m groundtruth_kb backlog authorize-implementation --help` | exit 0; help lists `--owner-decision`, `--auq-id`, `--include-spec`, `--allowed-mutation`, `--project`, `--dry-run`, `--json` |
| T2 | Create path from existing owner-authority DELIB | GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 | pytest: in a temp DB, work item is an active project member + an `owner_conversation`/`owner_decision` DELIB exists; run the command; assert a PAUTH exists including the work item, citing the DELIB, with the supplied mutation classes | PASS |
| T3 | Record-fresh-DELIB path | GOV-08, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | pytest: with `--auq-id/--auq-answer/--decision-content-file` and no `--owner-decision`, assert a new owner_conversation deliberation is recorded and the created PAUTH cites it | PASS |
| T4 | Refuses without any owner evidence | PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | pytest: run with neither `--owner-decision` nor AUQ evidence; assert non-zero exit and NO PAUTH/deliberation written | PASS (fails closed) |
| T5 | Spec-linkage required | GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001 | pytest: run with no `--include-spec`; assert non-zero exit and no authorization written | PASS (fails closed) |
| T6 | Project auto-resolution + ambiguity guard | DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 | pytest: (a) single active membership, `--project` omitted -> resolves correctly; (b) zero memberships -> error; (c) multiple memberships, `--project` omitted -> error | PASS |
| T7 | Gates unchanged (no bypass) | DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001, PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 | pytest: assert the produced PAUTH is a normal envelope row (no special flag) and that no gate module is imported or modified by the new code | PASS |
| T8 | `--dry-run` writes nothing | GOV-08 | pytest: `--dry-run`, assert no deliberation/authorization rows written and the proposed envelope is reported | PASS |
| T11 | Owner-authority predicate (NO-GO -002 F2) | PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | pytest: create a NON-owner deliberation (e.g. `source_type='lo_review'` or `outcome='informational'`); run `--owner-decision <that-id>`; assert non-zero exit, NO PAUTH row, and no approval-packet side effect | PASS (fails closed) |
| T12 | Mutually-exclusive authority inputs (NO-GO -002 F2) | GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | pytest: supply BOTH `--owner-decision` and `--auq-id/--auq-answer`; assert non-zero exit and no write | PASS (fails closed) |
| T9 | Non-regression on the live backlog-add CLI surface | GOV-08 | `VPY -m pytest platform_tests/scripts/test_cli_backlog_authorize_implementation.py platform_tests/scripts/test_cli_backlog_add.py -q` | all PASS |
| T10 | Lint + format on changed files | (code quality) | `VPY -m ruff check <changed.py>` AND `VPY -m ruff format --check <changed.py>` | both clean |

## Authorization Evidence

Live project-authorization coverage for the cited work item (captured 2026-05-31):

- Active PAUTH: `PAUTH-WI-3494-BACKLOG-AUTHORIZE-IMPLEMENTATION-CLI-001` (status `active`, owner-decision `DELIB-2547`).
- `included_work_item_ids`: `["WI-3494"]` (explicit inclusion; satisfies the Write-time bridge-compliance gate).
- `included_spec_ids`: `["GOV-STANDING-BACKLOG-001", "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001"]` (satisfies GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001).
- `allowed_mutation_classes`: `["cli_extension", "test_addition"]` - this work is exactly those classes; the revised `target_paths` (CLI module + cli.py + a `platform_tests/` test) remain within them.
- `forbidden_operations`: `["deploy", "git_push_force", "spec_deletion"]` - none implicated.
- WI-3494 is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`; the dedicated PAUTH above (not the reliability fast-lane standing PAUTH) carries this `improvement`-origin, new-CLI-surface work per GOV-RELIABILITY-FAST-LANE-001 eligibility.
- The implementation-start packet created post-GO will mechanically re-validate coverage and the revised `target_paths`.

## Risk / Rollback

- **Risk: the command is perceived as letting Prime self-authorize.** Mitigation: it requires owner-decision evidence and validates an existing `--owner-decision` as owner-authority (`source_type='owner_conversation'` AND `outcome='owner_decision'`); fails closed without valid evidence (T4, T11, T12). It only orchestrates the existing governed services.
- **Risk: a non-owner deliberation is accepted as authorization.** Mitigation: the CLI owner-authority predicate (F2) rejects non-owner deliberations; T11 proves fail-closed.
- **Risk: project auto-resolution picks the wrong project for a multi-membership work item.** Mitigation: the command fails closed on ambiguity and requires explicit `--project` (T6).
- **Risk: an authorization without a governing spec.** Mitigation: `--include-spec` is required; fail-closed (T5).
- **Risk: scope creep into the gate divergence or the amendment/extend path.** Mitigation: this slice touches no gate and is create-only (version 1, no amendment-packet path); the divergence is tracked as a separate backlog finding and the extend path is deferred to Slice 2.
- **Rollback if NO-GO:** no canonical mutations occur pre-GO; the slice is additive code. If NO-GO post-implementation: `git restore` `cli.py` + remove the new module and test file; no MemBase rows are touched by the slice itself.

## Recommended Commit Type

**`feat:`** - adds a net-new governed CLI capability (`gt backlog authorize-implementation`). Net-new command surface + new test module. Suggested message:

```
feat(cli): add gt backlog authorize-implementation to collapse project-authorization plumbing into one governed command (Slice 1 of gtkb-backlog-authorize-implementation-cli; WI-3494)
```

## Owner Action Required

None for this REVISED. Awaiting Codex GO at `-004` (or NO-GO with findings). After GO, implementation proceeds under the cited PAUTH per the Implementation Plan; the post-implementation report is filed for Codex VERIFIED review.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
