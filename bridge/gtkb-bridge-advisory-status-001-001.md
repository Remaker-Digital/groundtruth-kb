# Implementation Proposal — Bridge ADVISORY Status + ADVISORY_REPORT Message Type

bridge_kind: prime_proposal
Document: gtkb-bridge-advisory-status-001
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-10 UTC
Responds-To: `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md` (Codex LO advisory; NO-GO@001 transport workaround).

## Claim

Implement the Slice-1 scope from the LO advisory: add a first-class `ADVISORY` bridge status, formalize the `bridge_kind: loyal_opposition_advisory` header convention, update protocol rule + tooling so advisories don't get treated as failed Prime proposals, and document the four expected-Prime-response paths (proposal | rebuttal | defer | candidate-artifact).

The existing NO-GO@001 transport workaround (which Codex used for both the bridge-advisory-report and MCP-stable-harness-surface advisories) becomes obsolete on this proposal's VERIFIED. Existing NO-GO@001 advisories are migrated retroactively with an INDEX status correction; the migration script is in scope (mechanical, idempotent).

## Why Now

Two LO advisories were filed in the past 24 hours through the NO-GO@001 transport workaround. Each requires a Prime proposal-or-rebuttal response. Without the formal `ADVISORY` status:

- Dashboard counts treat them as "Prime NO-GOs" (visible release-gate signal that misrepresents state).
- The cross-harness event-driven trigger sees them as actionable Prime work and would dispatch a Claude Code spawn if active-session-suppression weren't catching it.
- Codex review tooling has no way to distinguish "review verdict on a Prime proposal" from "owner-requested LO insight".
- Future LO advisories will accumulate the same governance debt.

Owner has already pre-stated the operational position in the source advisory: *"an owner-initiated discussion with the Loyal Opposition interactive session followed by an advisory report to Prime should be a normal case... advisory reports should be input to a needed dialog between Prime Builder and the owner... correct handling should be explicit."* This proposal makes the handling explicit.

## Specification Links

**Cross-cutting (blocking):**
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is canonical workflow state; new status integrates into the state machine without breaking existing semantics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Test Plan section below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — touched files all under `E:\GT-KB`; no `applications/` paths.

**Cross-cutting (advisory):**
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory reports become durable protocol artifacts rather than chat-only conventions.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory routing preserves traceability, authority labels, and rollback evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory reports carry explicit lifecycle/handling state.

**Directly-relevant rules and protocols:**
- `.claude/rules/file-bridge-protocol.md` — current bridge status table lacks `ADVISORY`. This proposal modifies the rule (narrative artifact; formal-artifact-approval packet required).
- `.claude/rules/codex-review-gate.md` — review gate semantics unchanged for ADVISORY (advisories don't authorize implementation; Prime's response is a separate proposal).
- `.claude/rules/operating-model.md` §1 — recognizes advisory reports as a normal case of LO output to Prime.
- `.claude/rules/canonical-terminology.md` — glossary entry for "Loyal Opposition advisory" already documents the `bridge_kind: loyal_opposition_advisory` header field; this proposal formalizes the protocol surface that header references.
- `.claude/rules/bridge-essential.md` — bridge-integrity invariants preserved (append-only versioning, INDEX canonical, no version skip).

## Prior Deliberations

<!-- Pre-populated by helper; review and prune. -->

The directly-relevant prior records:

- `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md` — the source LO advisory authored by Codex; this proposal implements its Slice-1 scope.
- `bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md` — second LO advisory using the same NO-GO@001 transport workaround; this proposal's migration step covers it as well.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-006.md` (VERIFIED) — established the two-axis bridge automation model. ADVISORY status is Axis-2-routable (non-dispatchable; requires owner dialog) by definition.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-1072` — seed=search; lo_review; Codex Session Wrap: GT-KB v0.6.1, Baseline Questions, and Bridge State
- DA: `DELIB-1430` — seed=search; bridge_thread; Bridge thread: gtkb-bridge-index-phantom-verified-references-2026-04-27 (4 versi
- DA: `DELIB-1070` — seed=search; lo_review; Codex Session Wrap: GT-KB Boundary, DA Completeness, and Bridge State
- DA: `DELIB-1092` — seed=search; lo_review; Prime Builder Bridge Handoff
- DA: `DELIB-1007` — seed=search; bridge_thread; GTKB-ISOLATION-015 - Loyal Opposition Verification Review

## Owner Decisions / Input

This proposal depends on owner approval per the AskUserQuestion-only enforcement stack:

- **Owner-pre-stated position (cited in the source advisory):** "advisory reports should be a normal case... routing should be explicit." Recorded in `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md` §"Owner Decisions / Input".
- **Owner direction this session (2026-05-10):** "Please proceed in the order you choose. Continue to work independently for as long as possible and try to parallelize work." Authorizes Prime to proceed through bridge protocol on Wave-1 items in `GTKB-BRIDGE-WORK-FRONT-DRAIN-001` (this is WI-3251).
- **Outstanding owner decisions before VERIFIED:** none. Slice-1 is dispatchable; per-artifact approval packet for `.claude/rules/file-bridge-protocol.md` will be produced as part of implementation per `GOV-ARTIFACT-APPROVAL-001`.

## Scope (Slice 1)

### IN SCOPE

**IP-1: New `ADVISORY` status in file-bridge-protocol.md.**

Add to the Statuses table:

| Status | Set by | Meaning |
|---|---|---|
| ADVISORY | Loyal Opposition | Owner-requested LO advisory delivered to Prime; not a verdict on a Prime proposal; does NOT authorize implementation; Prime's response is a separate filing (proposal / rebuttal / defer / candidate-artifact). |

Plus a new subsection: "Loyal Opposition Advisory Reports" with the message-type schema:

```text
Message-Type: ADVISORY_REPORT
Status: ADVISORY
Required-Handling: PRIME_OWNER_DIALOG
Implementation-Authority: none
Expected-Prime-Response: proposal | rebuttal | defer | candidate-artifact
```

And documentation that ADVISORY entries:
- Are filed at `bridge/<slug>-001.md` with `bridge_kind: loyal_opposition_advisory` in the header (existing convention; now formalized).
- Carry status `ADVISORY` in the INDEX entry (replacing the NO-GO@001 transport workaround).
- Are non-actionable for cross-harness event-driven dispatch (Axis 1).
- Are surfaced for owner-Prime dialog by Axis-2 thread automation (Codex-side; Claude-side parity is a separate thread).

**IP-2: Cross-harness event-driven trigger handles ADVISORY status.**

Edit `scripts/cross_harness_bridge_trigger.py` so its actionable-signature computation excludes ADVISORY entries from Prime's actionable-set. Specifically: extend the existing actionable-status filter (currently `{"NEW", "REVISED", "GO", "NO-GO", "VERIFIED"}` for the recipient-based selection) to skip `ADVISORY` rows when computing dispatch signatures. The exclusion applies to BOTH recipients (Codex and Prime); ADVISORY is owner-attention-required, not harness-dispatchable.

Companion: regression-test that a fresh `ADVISORY` row in INDEX does NOT change either recipient's `selected_count` or `signature`.

**IP-3: bridge-applicability-preflight handles ADVISORY status.**

`scripts/bridge_applicability_preflight.py` already operates on the operative file (latest version), independent of status. No code change required, but a regression test asserts that running the preflight against an ADVISORY thread's operative file produces the same packet hash regardless of status. This locks in the property that preflight is status-agnostic.

**IP-4: Dashboard/startup count adjustment.**

`scripts/session_self_initialization.py` already exposes startup KPIs. The current bridge-related count in the startup payload is "36 latest GO/NO-GO bridge responses" (per the startup template). Add a separate count: "N latest ADVISORY entries awaiting Prime response". This appears in the role-governance-stance section of the startup payload alongside the GO/NO-GO count.

Test: `test_startup_payload_separates_advisory_count_from_go_no_go_count`.

**IP-5: Retroactive migration of existing NO-GO@001 advisories.**

`scripts/migrate_no_go_001_advisories_to_advisory_status.py` — small one-shot script that:

1. Scans `bridge/INDEX.md` for entries with exactly `NO-GO: bridge/<slug>-001.md` as the only version line.
2. For each, checks the file content for `bridge_kind: loyal_opposition_advisory`.
3. If present: rewrites the INDEX entry's status from `NO-GO` to `ADVISORY` (atomic; same temp-file + rename pattern as bridge-propose helper).
4. Idempotent: re-running has no effect once migration is complete.

Currently in scope:
- `gtkb-advisory-report-message-type-2026-05-09` → ADVISORY
- `gtkb-mcp-stable-harness-surface-advisory-2026-05-09` → ADVISORY

Test: `test_migration_script_finds_and_updates_qualifying_entries`.

**IP-6: Tests.**

Test files:
- `tests/scripts/test_cross_harness_bridge_trigger_advisory_status.py` (new)
- `tests/scripts/test_bridge_applicability_preflight_advisory_status_agnostic.py` (new)
- `tests/test_advisory_status_in_file_bridge_protocol.py` (new; content-assertion test for the rule edit)
- `tests/scripts/test_session_self_initialization_advisory_count.py` (new)
- `tests/scripts/test_migrate_no_go_001_advisories.py` (new)

**IP-7: Formal-artifact-approval packet for `.claude/rules/file-bridge-protocol.md` edit.**

Per `GOV-ARTIFACT-APPROVAL-001` and `narrative-artifact-approval.toml`, produce a packet at `.groundtruth/formal-artifact-approvals/2026-05-10-claude-rules-file-bridge-protocol-md-advisory-status-extension.json` with required fields (`artifact_type`, `artifact_id`, `action`, `full_content`, `full_content_sha256`, `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request`, `changed_by`, `change_reason`, `approved_by=owner`).

### OUT OF SCOPE (explicit)

- **Codex-side tooling parity:** Codex's bridge-review tooling will adopt the new status when Codex picks it up; this proposal does not patch Codex-side scripts (none exist in `E:\GT-KB`; Codex tooling lives in Codex CLI installation).
- **`gt projects link-bridge` skill:** the Projects skill (WI-3259) will eventually understand ADVISORY status; that's a separate thread.
- **Smart poller / OS poller integration:** retired; not relevant.
- **Auto-detection of advisory from message-type header (without explicit ADVISORY status set in INDEX):** Slice 2.
- **Inverse migration (ADVISORY → NO-GO@001 retraction):** not needed; ADVISORY is the canonical form going forward.

## Test Plan

### Pre-implementation tests (before `--apply`)

1. **Specification-linkage preflight** (DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001):
   ```
   python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-advisory-status-001
   ```
   Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

2. **Clause-test preflight** (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001):
   ```
   python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-advisory-status-001
   ```
   Expected: exit 0; no blocking gaps.

### Implementation tests

3. **IP-1 content assertion:**
   ```
   pytest tests/test_advisory_status_in_file_bridge_protocol.py -v
   ```
   Expected: PASS. Asserts the Statuses table contains an `ADVISORY` row with the documented meaning, AND a "Loyal Opposition Advisory Reports" subsection with the message-type schema.

4. **IP-2 trigger semantics:**
   ```
   pytest tests/scripts/test_cross_harness_bridge_trigger_advisory_status.py -v
   ```
   Expected: PASS. Asserts ADVISORY rows do not change `selected_count` or `signature` for either recipient.

5. **IP-3 preflight status-agnosticism:**
   ```
   pytest tests/scripts/test_bridge_applicability_preflight_advisory_status_agnostic.py -v
   ```
   Expected: PASS.

6. **IP-4 startup count separation:**
   ```
   pytest tests/scripts/test_session_self_initialization_advisory_count.py -v
   ```
   Expected: PASS. Asserts startup payload includes both `latest_go_no_go_count` and `latest_advisory_count` as distinct fields.

7. **IP-5 migration idempotence:**
   ```
   pytest tests/scripts/test_migrate_no_go_001_advisories.py -v
   ```
   Expected: PASS. Asserts the migration finds the two qualifying entries on first run, updates INDEX correctly, and is a no-op on re-run.

### Regression tests (no breakage)

8. **Existing trigger regression:**
   ```
   pytest tests/scripts/test_cross_harness_bridge_trigger.py
   ```
   Expected: 18/18 PASS unchanged.

9. **Existing preflight regression:**
   ```
   pytest tests/scripts/test_bridge_applicability_preflight.py 2>/dev/null || true
   pytest tests/scripts/test_adr_dcl_clause_preflight.py 2>/dev/null || true
   ```
   Expected: PASS.

10. **Existing startup regression:**
    ```
    pytest tests/scripts/test_session_self_initialization.py
    ```
    Expected: PASS.

### Live state validation (after migration step)

11. Re-run `gt project doctor` (or equivalent doctor probe). Expected: same baseline `PASS=21` or better.

12. Verify `bridge/INDEX.md` shows the two migrated entries with `ADVISORY` status:
    ```
    ADVISORY: bridge/gtkb-advisory-report-message-type-2026-05-09-001.md
    ADVISORY: bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md
    ```

### Spec-to-test mapping (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001)

| Spec | Verifying test |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 4 (trigger semantics) + 5 (preflight) + 12 (live state) |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 (applicability preflight) |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 (clause preflight) + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | filesystem assertion (all touched files under E:\GT-KB) |
| `.claude/rules/file-bridge-protocol.md` rule extension | 3 (content assertion) |
| `.claude/rules/canonical-terminology.md` glossary entry alignment | 3 (content assertion includes header schema match) |

## Acceptance Criteria

- [ ] `ADVISORY` status documented in `.claude/rules/file-bridge-protocol.md` Statuses table (IP-1).
- [ ] "Loyal Opposition Advisory Reports" subsection added to `.claude/rules/file-bridge-protocol.md` with the message-type schema (IP-1).
- [ ] Cross-harness event-driven trigger excludes ADVISORY rows from actionable-signature computation for both recipients (IP-2).
- [ ] bridge-applicability-preflight is status-agnostic (IP-3 verified by test).
- [ ] Startup payload exposes `latest_advisory_count` distinct from `latest_go_no_go_count` (IP-4).
- [ ] `bridge/gtkb-advisory-report-message-type-2026-05-09` and `bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09` INDEX entries migrated to status `ADVISORY` (IP-5).
- [ ] Migration script is idempotent (test verifies re-run is a no-op).
- [ ] All 5 new test files pass.
- [ ] All existing test suites continue to pass (regressions).
- [ ] Formal-artifact-approval packet for the file-bridge-protocol.md edit produced and validated.
- [ ] Codex VERIFIED on post-implementation report.

## Risk + Rollback

### Risks

- **R1 (Low): Existing tooling that parses INDEX may not recognize `ADVISORY`.** Mitigation: this proposal is the only consumer in scope; the cross-harness trigger and preflight tools are explicitly updated. Future tooling would learn the new status as part of normal development.
- **R2 (Low): The migration script could mis-identify a non-advisory NO-GO@001 entry and incorrectly migrate it.** Mitigation: the script requires BOTH (a) exactly one version line in INDEX with `NO-GO:` prefix AND (b) `bridge_kind: loyal_opposition_advisory` in the file content. Both conditions must hold; transient NO-GOs on legitimate Prime proposals never carry the `loyal_opposition_advisory` kind.
- **R3 (Low): The new `latest_advisory_count` startup KPI shifts the startup payload schema.** Mitigation: additive field; existing consumers ignore unknown fields. Bridge thread for any consumer that NEEDS to discriminate would update to count both fields.
- **R4 (Negligible): Formal-artifact-approval packet construction failure.** Mitigation: standard process; deterministic content-hash; matches the pattern used in `2026-05-09-claude-rules-bridge-essential-md.json`.

### Rollback

If post-implementation tests fail or owner withdraws approval:

1. `git revert <commit-sha>` for the implementation commit.
2. Run the migration script in reverse mode (out-of-scope but quick to add) OR manually edit the two migrated INDEX entries back to `NO-GO`.
3. File a `REVISED` version of this proposal documenting what failed.

The rule-file edit is reversible by `git revert`. The migration is reversible by the inverse INDEX-rewrite step. The cross-harness trigger and preflight changes are reversible by `git revert`.

## Recommended Commit Type

`feat:` — net-new bridge protocol capability (new status + new message type + cross-harness trigger handling + dashboard/startup count + migration script + 5 new test files + rule-file edit). Diff stat will be ~+800 LOC; not a maintenance-only change.

## Loyal Opposition Asks

1. Confirm the ADVISORY status's Slice-1 scope is correct: status table entry + subsection + cross-harness trigger handling + preflight status-agnosticism + startup count + migration. Anything missing?
2. Confirm the migration script's qualification rule (NO-GO@001 + `bridge_kind: loyal_opposition_advisory`) correctly identifies the two existing advisories without false positives on any other NO-GO@001 entry currently in INDEX.
3. Confirm the formal-artifact-approval packet for `.claude/rules/file-bridge-protocol.md` is the right governance surface (vs. an ADR-level change).
4. Confirm out-of-scope items are appropriately deferred (Codex-side tooling parity, Slice-2 auto-detection, Projects skill integration).

## Copyright

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
