# Implementation Proposal - Advisory-to-Backlog Router (Self-Diagnostic Leak Closure Slice 1)

bridge_kind: prime_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-1-advisory-router
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-13 UTC
Session: S349
Work Item: new MemBase work item to be created from this proposal's IP-1 SPEC creation; current proposal scope is Slice 1 of the GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE umbrella
target_paths: ["scripts/advisory_backlog_router.py", "platform_tests/scripts/test_advisory_backlog_router.py", ".claude/hooks/advisory-router-scan.py", ".claude/settings.json", ".codex/hooks.json", "groundtruth.db", ".claude/rules/peer-solution-advisory-loop.md", "config/agent-control/harness-capability-registry.toml"]

## Claim

Add a deterministic read-only Python service that watches `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` and bridge `ADVISORY` entries, and routes each unhandled advisory into the canonical MemBase backlog as a `work_items` row.

The service must close the self-improvement consumption edge identified in S349 investigation: as of 2026-05-13 UTC, three substantive LO advisories filed on 2026-05-10 and 2026-05-11 are sitting in the dropbox unhandled, with no Prime acknowledgement, no bridge thread opened, and no MemBase work item created. The strategic self-improvement directive in `CLAUDE.md` and `.claude/rules/peer-solution-advisory-loop.md` already prescribe the routing behavior; this slice adds the deterministic plumbing that makes the routing observable and auditable.

The service is plumbing, not policy. It does not classify advisory severity beyond what the advisory itself carries; it does not pre-judge adopt/adapt/reject/defer disposition; it does not bypass the bridge protocol for any subsequent implementation. It only converts "advisory exists" into "MemBase work item exists" so the standing backlog reflects the actual work the platform has surfaced.

## Why Now

S349 self-diagnostic investigation surfaced this as LEAK 1 of five identified leaks. Quantitative evidence:

- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM proposes the GT-KB Effectiveness Observatory with 7 measurement portfolios, 4 counterfactual designs, and a 5-phase roadmap. Unhandled.
- INSIGHTS-2026-05-11-07-11-CLAUDE-DESIGN-GTKB-INTEGRATION-REVIEW proposes a governed Claude Design intake pipeline. Unhandled.
- INSIGHTS-2026-05-11-08-44-LO-HYGIENE-ASSESSMENT-SKILL-ADVISORY proposes a Loyal Opposition hygiene-orchestration skill. Unhandled.

Per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, repetitive AI work where the substantive contribution is below 20% of total work belongs in a deterministic service. Manually scanning the INSIGHTS dropbox each session, classifying each advisory, and creating per-advisory work items is exactly such plumbing. Today, that plumbing is not running, which is why the three advisories above are stalled.

This slice is the smallest action that closes the largest observed leak in the system. It is plumbing-only and does not mutate any existing canonical artifact except through the standard `db.insert_work_item()` write path.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - live `bridge/INDEX.md` remains the authoritative bridge queue; this proposal files the governed work before implementation.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths are inside the active `E:/GT-KB` project root.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites the relevant existing governing specs and names new specs to be created from the owner authorization before code semantics depend on them.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification requires created or identified tests derived from the linked specs and proposed specs.
- GOV-STANDING-BACKLOG-001 - the standing backlog is the durable cross-session work authority; advisory-router output flows here.
- ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001 - MemBase work items remain the canonical authority; markdown views remain derived.
- ADR-STANDING-BACKLOG-DB-AUTHORITY-001 - MemBase is the canonical DB-backed backlog/project authority.
- DCL-STANDING-BACKLOG-DB-SCHEMA-001 - work_items field schema must remain stable; advisory-router uses existing fields without schema extension.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - capture noticed fix-worthy issues as durable artifacts rather than relying on transient agent recall.
- GOV-ARTIFACT-APPROVAL-001 - no canonical formal artifact (GOV/ADR/DCL/SPEC/PB) is mutated by this slice; only `work_items` rows are created, which follow append-only versioning per existing convention.
- GOV-CHAT-DERIVED-SPEC-APPROVAL-001 - this slice does not formalize specifications from chat; only routes pre-formalized advisories.
- ADR-DA-READ-SURFACE-PLACEMENT-001 - INSIGHTS reports remain a Deliberation Archive read surface; this slice does not change DA placement, only adds a downstream consumer.
- DCL-CONCEPT-ON-CONTACT-001 - "advisory-router" is a new load-bearing concept introduced by this slice; glossary entry added as part of IP-1.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - improvement opportunities flow to MemBase backlog; this slice operationalizes the routing.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - repetitive AI plumbing belongs in services, not in sessions.

Advisory / cross-cutting:

- `.claude/rules/peer-solution-advisory-loop.md` - canonical procedure for handling LO peer-solution advisories; this slice provides the mechanical plumbing that the procedure currently lacks.
- `.claude/rules/operating-model.md` - operating model alignment baseline.
- `.claude/rules/canonical-terminology.md` - glossary maintenance baseline.
- `.claude/rules/file-bridge-protocol.md` - bridge protocol authority.
- `.claude/rules/codex-review-gate.md` - implementation requires Codex GO.

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-13 UTC) - owner asked Prime to probe agent behavior for leaks/gaps/waste; investigation surfaced three stalled LO advisories as LEAK 1 of five identified leaks; owner authorized "File both, sequenced" via AskUserQuestion (Slice 1 advisory-router, Slice 2 benchmark suite, Slice 3 assertion S/N triage).
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex Loyal Opposition advisory, 2026-05-10) - the unhandled advisory that motivates this slice; its Phase 1 recommendation is a passive baseline collector that this slice partially implements via the advisory-router.
- INSIGHTS-2026-05-11-08-44-LO-HYGIENE-ASSESSMENT-SKILL-ADVISORY (Codex Loyal Opposition advisory, 2026-05-11) - second unhandled advisory; this slice routes it to MemBase as a candidate WI for subsequent owner disposition.
- INSIGHTS-2026-05-11-07-11-CLAUDE-DESIGN-GTKB-INTEGRATION-REVIEW (Codex Loyal Opposition advisory, 2026-05-11) - third unhandled advisory; same routing.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION - recent owner authorization pattern preserving proposal-level bridge review while reducing per-proposal owner-approval overhead; this slice is consistent with that pattern (the AUQ authorization in S349 is the parent owner approval; per-slice bridge review still occurs).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - converts repetitive plumbing to services; the advisory-router is a concrete first manifestation in addition to the existing GTKB-ARTIFACT-RECORDER-CLI work.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - improvement opportunities go to MemBase backlog; this slice closes the routing gap between LO advisory production and MemBase backlog consumption.
- DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS - placement-over-coercion principle; the advisory-router is placement: it positions advisory consumption on a path the system already traverses (MemBase work_items) rather than introducing a new behavior agents must remember.

## Owner Decisions / Input

- 2026-05-13 UTC, S349: owner asked Prime Builder to investigate GT-KB behavior for "leaks, gaps and waste" via four probe questions (history review after append, deliberation capture, spec/test consistency, skill activation vs. improvisation).
- 2026-05-13 UTC, S349: owner authorized "File both, sequenced" via AskUserQuestion in this session, sequencing as Slice 1 advisory-router (this proposal), Slice 2 benchmark suite (follow-on), Slice 3 assertion S/N triage (follow-on). The AUQ answer is the parent owner authorization for the umbrella GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE work.
- 2026-05-13 UTC, S349: owner framed the work in service of the meta-question "If GT-KB can self-diagnose and self-improve, then it will also reliably do the same for applications." This slice is positioned as the smallest action that closes the largest leak preventing that meta-claim from being true today.

No additional owner decision is required before this proposal can be reviewed. Any subsequent production deployment, broad MemBase mutation, or expansion beyond the target_paths below still requires the normal separate approval path. The slice does not create or modify formal artifacts (GOV/ADR/DCL/SPEC/PB) without the standard formal-artifact-approval packet workflow per `GOV-ARTIFACT-APPROVAL-001`.

## Requirement Sufficiency

Existing requirements sufficient.

The strategic self-improvement directive in `CLAUDE.md` plus `GOV-STANDING-BACKLOG-001` plus `DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE` plus `.claude/rules/peer-solution-advisory-loop.md` together already authorize Prime Builder to route noticed fix-worthy issues into the MemBase backlog. What is missing is mechanical plumbing, not new requirements.

One small new SPEC is required to formalize the advisory-router's behavior contract (SPEC-ADVISORY-BACKLOG-ROUTER-001 below), but this SPEC formalizes mechanical behavior consistent with existing governance, not a new product behavior. The SPEC creation runs through the standard formal-artifact-approval-packet workflow at IP-1.

## Current Implementation Baseline

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` contains 13 INSIGHTS-*.md files dated 2026-05 (the May LO output surface). 3 are P1-class with unhandled disposition as of 2026-05-13 UTC.
- `bridge/INDEX.md` supports `ADVISORY` status entries per the bridge protocol extension VERIFIED at `bridge/gtkb-advisory-report-protocol-extension-NNN.md`. Current INDEX shows one active ADVISORY entry: `gtkb-owner-role-switch-codex-loyal-opposition`.
- `groundtruth-kb/src/groundtruth_kb/db.py` `work_items` table supports the fields needed for advisory-routed WIs without schema changes: `id`, `title`, `description`, `origin` (set to `advisory_routed`), `component`, `priority`, `related_deliberation_ids`, `related_bridge_threads`, `source_owner_directive`, `change_reason`, `changed_by`.
- No current process scans the INSIGHTS dropbox or ADVISORY bridge entries on a schedule. The peer-solution-advisory-loop rule prescribes Prime's response classification (adopt/adapt/reject/defer/monitor) but provides no mechanical surfacing of advisories awaiting that classification.
- The cross-harness event-driven trigger at `scripts/cross_harness_bridge_trigger.py` registers PostToolUse and Stop hooks. The same registration pattern is appropriate for a periodic advisory scan.

## Proposed New Specs

IP-1 must create this MemBase record from the S349 AUQ authorization before implementing runtime behavior:

1. SPEC-ADVISORY-BACKLOG-ROUTER-001 - advisory-router behavior contract:
   - Scope: scans `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` and `bridge/INDEX.md` ADVISORY entries.
   - Trigger: invoked by a Stop hook on Prime Builder turn-end and by `gt advisory route` CLI on owner command.
   - Behavior: for each advisory not already represented in `work_items` by `related_bridge_threads` or filename-anchored `related_deliberation_ids`, create one `work_items` row with `origin='advisory_routed'`, `changed_by='advisory-router-service@1.0'`, `change_reason` citing the source advisory path, `priority` derived from advisory severity field when present (P0/P1 -> high, P2 -> medium, P3/P4 or unset -> low).
   - Idempotency: re-running must not create duplicate WIs; idempotency key is the advisory file path + content hash.
   - Read-only on source: never mutates the advisory file or the bridge thread.
   - Out of scope: does not classify advisory disposition (adopt/adapt/reject/defer/monitor); that remains a Prime Builder governance decision per `.claude/rules/peer-solution-advisory-loop.md`. Does not modify any formal artifact (GOV/ADR/DCL/SPEC/PB).

The SPEC creation requires a formal-artifact-approval packet at IP-1 per `GOV-ARTIFACT-APPROVAL-001`. The packet will reference the S349 AUQ authorization as `presented_to_user` evidence.

## Proposed Scope

### IP-1: Create SPEC and approval packet

1. Create `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-ADVISORY-BACKLOG-ROUTER-001.json` with required fields (artifact_type, artifact_id, action, full_content, full_content_sha256, presented_to_user=true, transcript_captured=true, explicit_change_request, changed_by, change_reason, approved_by=owner).
2. Insert SPEC-ADVISORY-BACKLOG-ROUTER-001 into MemBase via `db.insert_specification()`, citing the packet path in change_reason.

### IP-2: Implement the router service

1. Create `scripts/advisory_backlog_router.py`:
   - CLI entry: `python scripts/advisory_backlog_router.py [--dry-run] [--source dropbox|bridge|both] [--since YYYY-MM-DD]`.
   - Scans configured sources, computes idempotency keys, queries existing `work_items.related_bridge_threads` and `related_deliberation_ids` for matches, creates one new WI per unhandled advisory.
   - Returns structured JSON output with `created` (list of new WI IDs), `skipped_existing` (list of advisory paths matched by idempotency), `errors` (list of malformed advisories with reason).
   - Reads severity from advisory `Severity:` line if present; defaults to P2 if missing.
   - Stores last-scan timestamp at `.gtkb-state/advisory-router/last-scan.json`.

### IP-3: Register the Stop hook for advisory scan

1. Create `.claude/hooks/advisory-router-scan.py` as a thin wrapper that invokes the router CLI in `--source both --since <last-scan>` mode on Prime Builder Stop events.
2. Register in `.claude/settings.json` under `hooks.Stop` array.
3. Add Codex parity registration in `.codex/hooks.json` so the hook fires regardless of which harness is Prime.
4. Add capability registry entry in `config/agent-control/harness-capability-registry.toml` per the standard skill/hook pattern.

### IP-4: Backfill existing unhandled advisories

1. Run the router in `--dry-run` mode against current dropbox state.
2. Inspect dry-run output; expected: 3 new WIs from the May 2026 unhandled advisories, plus N from earlier unhandled entries.
3. Owner reviews dry-run output via AskUserQuestion before applying.
4. Apply with `--source dropbox --since 2026-04-01` (cutoff date excludes the Agent Red Phase 1-5 review burst from March-April which was contemporaneously handled).

### IP-5: Update peer-solution-advisory-loop rule

1. Add a "Mechanical Surfacing" subsection to `.claude/rules/peer-solution-advisory-loop.md` documenting the advisory-router as the canonical surfacing mechanism.
2. Cross-reference the router's idempotency contract so future advisory-loop work doesn't duplicate the surface.
3. Note that the rule's classification states (adopt/adapt/reject/defer/monitor) remain Prime Builder responsibility; the router only routes, it does not classify.

## Tests

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, create `platform_tests/scripts/test_advisory_backlog_router.py` with at minimum:

1. `test_router_creates_wi_for_new_advisory` - given a fixture advisory file and an empty work_items table, router creates exactly one new WI with correct origin, changed_by, related_deliberation_ids fields.
2. `test_router_idempotent_on_rerun` - second invocation against same fixture creates zero new WIs.
3. `test_router_parses_severity_from_header` - fixture with `Severity: P1` line maps to priority='high'.
4. `test_router_defaults_priority_when_severity_missing` - fixture without severity defaults to priority='medium'.
5. `test_router_skips_advisories_already_in_bridge_threads` - if a WI already cites the advisory path in related_bridge_threads, the router skips it.
6. `test_router_dry_run_does_not_mutate` - dry-run mode emits planned-creates JSON without writing to MemBase.
7. `test_router_handles_malformed_advisory` - file missing required headers is reported in errors list, not crashed on.
8. `test_router_writes_last_scan_timestamp` - successful run updates `.gtkb-state/advisory-router/last-scan.json`.

## Verification Plan

After implementation, the post-impl report at version -003 (or higher) must include:

1. Test execution evidence: all 8 tests above PASS, output captured.
2. Idempotency proof: two consecutive live runs against current dropbox state, second run shows zero new WIs and the same set as the first run.
3. Backfill evidence: the 3 unhandled May 2026 advisories now appear as WIs in MemBase with origin='advisory_routed'; sample WI IDs cited in the report.
4. Hook firing proof: hook trigger event logged in `.gtkb-state/advisory-router/last-scan.json` after a Stop event in a verification session.
5. Specification linkage check: every linked spec from the Specification Links section above remains satisfied at post-impl time.
6. Applicability preflight: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-1-advisory-router` returns preflight_passed=true.
7. Clause preflight: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-1-advisory-router` returns no blocking gaps.

## Risks and Rollback

Risks:

- Router false-positive: an INSIGHTS file that is not actionable (e.g., session-wrap-only notes) gets routed to a WI. Mitigation: severity-defaulting plus idempotency means the WI can be retired with no data loss; the router never deletes advisory files.
- Hook performance: scanning the dropbox on every Stop event could add latency. Mitigation: the router uses `--since <last-scan>` to scan only new files; expected per-invocation cost is sub-second.
- Backfill volume: dry-run may surface dozens of historical advisories. Mitigation: `--since 2026-04-01` cutoff plus owner review of dry-run output before apply.

Rollback:

- Disable hook: remove the entry from `.claude/settings.json` `hooks.Stop` array and `.codex/hooks.json` parity entry.
- Retire created WIs: standard `db.update_work_item()` with `resolution_status='retired_by_rollback'` and `change_reason` citing this proposal.
- Source file is preserved; no advisory content is mutated by this slice.

## Sequenced Follow-Ons

This is Slice 1 of the GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE umbrella authorized by the S349 AUQ. After Slice 1 reaches VERIFIED:

- Slice 2: benchmark suite — implements Benchmarks 1-6 from the S349 investigation report (cross-artifact linkage heat map, recall evidence coverage, tool identification, deliberation recall quality, advisory-to-action latency, assertion signal/noise ratio). Builds on the Codex Self-Measurement System advisory's architecture.
- Slice 3: assertion S/N triage — categorizes the 1,463 currently-failing assertions into genuine drift / chronic noise / flaky / healthy and proposes retirement-or-owner-accept disposition for chronic noise.

Each slice will file its own bridge thread when Slice 1 reaches VERIFIED; this slice's GO does not pre-approve Slices 2 and 3.

## Recommended Commit Type

`feat:` - new functionality (advisory-router service, hook, capability registry entry, SPEC). Backfill commit may be a separate `chore:` if owner prefers to keep the SPEC/code commit separate from the data-creation commit.

## Bridge-Compliance Self-Check

This proposal includes:

- non-empty `## Specification Links` section with cited governing specs.
- non-empty `## Prior Deliberations` section with cited DELIB-IDs and INSIGHTS files.
- non-empty `## Owner Decisions / Input` section enumerating the S349 AUQ evidence.
- `target_paths` metadata in the header block.
- `## Requirement Sufficiency` subsection with explicit state.
- `## Recommended Commit Type` per recent governance hygiene bundle.

If applicability preflight or clause preflight returns missing items, this proposal will be revised at version -003 (after Codex review at -002).
