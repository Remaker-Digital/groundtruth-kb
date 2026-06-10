REVISED

# Governance Review — S509 Proposal Remediation Umbrella

bridge_kind: governance_advisory
Document: gtkb-v1-s509-proposal-remediation
Version: 002
Author: Prime Builder (goose, harness E)
Date: 2026-06-08 UTC

author_identity: Goose Prime Builder
author_harness_id: E
author_session_context_id: S509
author_model: goose-desktop
author_model_configuration: Goose Desktop interactive

Project: PROJECT-GTKB-PLATFORM-CORE
primary_work_item: WI-4605

## 1. Claim

This governance review establishes a shared remediation template for five proposals rejected by Loyal Opposition on 2026-06-08 due to common mechanical failures in envelope metadata and specification linkage.

## 2. Status Matrix

| Proposal | Disposition | Action |
|----------|-------------|--------|
| gtkb-platform-observability-hygiene | REVISE | Apply umbrella template; file as \`-003 REVISED\` |
| gtkb-bridge-kind-taxonomy-stabilization | DEFER | Migration script too high-risk without audit-trail substrate; defer to future slice |
| gtkb-workstream-focus-marker-race-fix | REVISE | Apply umbrella template; file as \`-003 REVISED\` |
| gtkb-mcp-stable-harness-surface-implementation | REVISE | Apply umbrella template; file as \`-003 REVISED\` |
| gtkb-bridge-advisory-message-type-implementation | WITHDRAW | Redundant — ADVISORY semantics already landed in \`file-bridge-protocol.md\` |

## 3. Shared Remediation Template

All REVISED proposals must include the following sections:

### 3.1 Envelope Metadata (YAML-front-matter style)

\`\`\`yaml
bridge_kind: governance_advisory
Document: <doc-name>
Version: <NNN>
Author: Prime Builder (<harness>, harness <ID>)
Date: <YYYY-MM-DD UTC>

author_identity: <identity>
author_harness_id: <single-char-ID>
author_session_context_id: <session-id>
author_model: <model-name>
author_model_configuration: <config-description>

bridge_kind: governance_advisory
target_paths:
  - path/to/file1.py
  - path/to/file2.py
implementation_scope: <brief-description>
primary_work_item: WI-<NNNN>
\`\`\`

### 3.2 Specification Links Section (mandatory)

\`\`\`markdown
## Specification Links

### Required Specifications

- \`GOV-FILE-BRIDGE-AUTHORITY-001\` — File bridge protocol governance
- \`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001\` — Implementation proposals must cite specs
- \`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001\` — Verified proposals must have spec-to-test mapping

### Project Requirements

- \`REQ-<PROJECT>-<ID>\` — <requirement-title>

### Deliberations

- \`DELIB-<NNNN>\` — <deliberation-title>
\`\`\`

### 3.3 Requirement Sufficiency Section (mandatory)

\`\`\`markdown
## Requirement Sufficiency

| Requirement | Source | Satisfied By | Test Coverage |
|-------------|--------|--------------|---------------|
| REQ-<ID> | <spec-or-delib> | <implementation-section> | <test-file-or-N/A> |
\`\`\`

### 3.4 Spec-to-Test Mapping (mandatory for implementation_proposal)

\`\`\`markdown
## Spec-to-Test Mapping

| Spec ID | Test File | Test Case(s) |
|---------|-----------|--------------|
| req-<id> | tests/path/to/test_file.py | test_function_name |
\`\`\`

## 4. Critical Governance Gap: GOV-FILE-BRIDGE-AUTHORITY-001

**Finding:** The spec \`GOV-FILE-BRIDGE-AUTHORITY-001\` does not exist as a formal artifact in \`spec_corpus\` or \`assertion-triage\`. However, the file bridge protocol is governed by \`.claude/rules/file-bridge-protocol.md\`.

**Remediation:** Either:
1. **Create the spec:** File a \`formal_spec_creation\` proposal to add \`GOV-FILE-BRIDGE-AUTHORITY-001\` to the spec corpus, OR
2. **Cite the rule file:** Treat \`.claude/rules/file-bridge-protocol.md\` as the authoritative source and cite it directly in the Specification Links section.

**Recommendation:** Option 2 (cite the rule file) is sufficient for S509 remediation. Formal spec creation can be deferred to a future governance slice.

## 5. Per-Item Remediation Details

### 5.1 B1: gtkb-platform-observability-hygiene

**Unique Concern:** 1-hour staleness threshold has no spec backing; \`*.tmp\` cleanup risks clobbering live atomic-write temporaries.

**Remediation:**
- Add envelope metadata with \`target_paths: [groundtruth_kb/cli/platform_doctor.py, scripts/check_harness_parity.py, scripts/cross_harness_bridge_trigger.py]\`
- Add Specification Links section citing the three mandatory specs
- Address staleness threshold: cite \`DCL-BRIDGE-POLLER-STATE-FRESHNESS-001\` (or propose new DCL if none exists)
- Scope \`*.tmp\` cleanup narrowly: exclude files with active PIDs; define staleness as "older than 30 minutes with no associated bridge-poller process"

### 5.2 B2: gtkb-bridge-kind-taxonomy-stabilization

**Unique Concern:** Migration script modifies all \`bridge/*.md\` (audit trail touch); no rollback procedure; \`BridgeKind\` enum conflicts with existing \`BridgeStatus\`.

**Remediation:**
- **DEFER** this proposal until:
  1. Audit-trail substrate supports reversible migrations
  2. \`BridgeKind\` vs \`BridgeStatus\` design is clarified (document-type vs workflow-status)
  3. Rollback procedure is defined
- File a new governance_review proposal \`gtkb-bridge-kind-migration-substrate-001\` to address these prerequisites before revisiting taxonomy stabilization

### 5.3 B3: gtkb-workstream-focus-marker-race-fix

**Unique Concern:** LO claimed \`scripts/workstream_focus.py\` may not exist.

**Verification:** Script **does exist** at \`scripts/workstream_focus.py\` (verified 2026-06-08).

**Remediation:**
- Add envelope metadata with \`target_paths: [scripts/workstream_focus.py]\`
- Add Specification Links section citing \`DCL-SESSION-ROLE-RESOLUTION-001\` and \`GOV-SESSION-ROLE-AUTHORITY-001\`
- Define atomic write pattern: file lock + session-ID validation + expiry check

### 5.4 B4: gtkb-mcp-stable-harness-surface-implementation

**Unique Concern:** \`fastmcp\` dependency not declared; RBAC design undefined.

**Remediation:**
- Add envelope metadata with \`target_paths: [groundtruth_kb/mcp_surface/server.py, tests/framework/test_mcp_surface_tools.py]\`
- Add \`fastmcp~=1.0\` to \`pyproject.toml\[project.dependencies]\`
- Define RBAC design:
  - Authority check via \`groundtruth_kb.harness_projection.read_roles()\`
  - Active role determined from \`harness-state/harness-registry.json\`
  - Role resolution failure raises \`PermissionDenied\` (fail-closed)

### 5.5 B5: gtkb-bridge-advisory-message-type-implementation

**Disposition:** WITHDRAW

**Evidence:** \`.claude/rules/file-bridge-protocol.md\` already contains:
- ADVISORY status definition with full semantics
- Routing rules (owner-initiated, non-dispatchable)
- Prime/LO behavior contracts
- Status display in INDEX.md

**Action:** File a \`WITHDRAWN\` entry at \`bridge/gtkb-bridge-advisory-message-type-implementation-003.md\` citing this umbrella as authority. Update \`bridge/INDEX.md\` to mark the thread as WITHDRAWN.

## 6. Acceptance Criteria

This governance_review is **accepted** when:
1. Owner approves the shared template structure (Sections 3.1–3.4)
2. Owner decides whether to create \`GOV-FILE-BRIDGE-AUTHORITY-001\` or cite \`file-bridge-protocol.md\` directly (recommendation: cite the rule file)
3. Owner approves the per-item remediation plan (Section 5)
4. Owner authorizes filing of REVISED proposals for B1, B3, B4 and WITHDRAWN entry for B5

## 7. Execution Plan

### Phase 1: File Umbrella (this proposal)
1. File \`bridge/gtkb-v1-s509-proposal-remediation-001.md\` as NEW
2. Update \`bridge/INDEX.md\` with entry under \`Document: gtkb-v1-s509-proposal-remediation\`
3. Await LO verdict (GO/NO-GO)

### Phase 2: File B5 Withdrawal
1. File \`bridge/gtkb-bridge-advisory-message-type-implementation-003.md\` as WITHDRAWN
2. Update \`bridge/INDEX.md\`

### Phase 3: File B1, B3, B4 Revisions
1. File \`bridge/gtkb-platform-observability-hygiene-003.md\` as REVISED (applies umbrella template)
2. File \`bridge/gtkb-workstream-focus-marker-race-fix-003.md\` as REVISED
3. File \`bridge/gtkb-mcp-stable-harness-surface-implementation-003.md\` as REVISED
4. Update \`bridge/INDEX.md\` for each
5. Await LO verdicts

### Phase 4: Defer B2
1. No action on B2 in S509
2. Add to standing backlog: "Bridge Kind Migration Substrate" (future governance review)

## 8. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Umbrella template rejected by LO | High | Defer all B-item revisions until umbrella is approved |
| GOV-FILE-BRIDGE-AUTHORITY-001 spec creation delayed | Medium | Use rule file citation as interim solution |
| B2 migration attempted prematurely | Critical | Explicit deferral; file prerequisite proposal first |
| B1 staleness threshold unvalidated | Medium | Cite existing DCL or propose new one in REVISED proposal |

## 9. Prior Deliberations

- \`DELIB-S509-B1-B5-TRIAGE\` — This session's triage (to be captured in Deliberation Archive)
- \`DELIB-1104\` — Bridge poller thread state (relevant to B1 dispatch-state work)
- \`DELIB-0101\` / \`DELIB-0486\` — Bridge poller predecessors

## 10. Conclusion

This umbrella establishes the remediation methodology for five mechanically-rejected proposals. Withdrawal of B5 (redundant) and deferral of B2 (high-risk migration) are correct. Three proposals (B1, B3, B4) can proceed with revised envelopes and addressed concerns once this umbrella receives GO verdict.

---

## 11. Option A Amendment (GOV Spec Formalized)

Per owner direction ("A"), GOV-FILE-BRIDGE-AUTHORITY-001 has been formalized
as a standalone spec document at `config/governance/gov-file-bridge-authority-001.md`
(filed 2026-06-08, bridge thread `gtkb-gov-file-bridge-authority-001`).

The formal spec enumerates 16 clauses (C-001 through C-016) extracted from
`.claude/rules/file-bridge-protocol.md`. It is registered at blocking severity
in `config/governance/spec-applicability.toml` with `spec_body_path` and
`clause_count` fields added to the existing rule.

### Effect on this umbrella's Specification Links (Section 4)

- The interim-citation fallback is no longer necessary.
- B1, B3, B4 REVISED proposals should cite the formal spec directly
  (not just the protocol) to satisfy the applicability preflight.
- The LO preflight pass on B1/B3/B4 will find `GOV-FILE-BRIDGE-AUTHORITY-001`
  with a machine-readable `spec_body_path`, closing the original NO-GO
  gap cleanly.

### Audit trail

- Umbrella v1: `bridge/gtkb-v1-s509-proposal-remediation-001.md` (NEW)
- GOV spec: `config/governance/gov-file-bridge-authority-001.md` (formal body)
- GOV bridge entry: `bridge/gtkb-gov-file-bridge-authority-001-001.md` (NEW, `spec_creation`)
- Umbrella v2: this file (REVISED, Option A amendment)

---

*Prime Builder: goose (harness E) — Option A executed*
*Session S509 — 2026-06-08 ~10:28 UTC*
