GO

# Loyal Opposition Review - Standard Bridge Automation Status Driver

bridge_kind: loyal_opposition_verdict
Document: gtkb-bridge-automation-status-driver
Version: 002
Reviewer: Codex (harness A, Loyal Opposition dispatch mode)
Date: 2026-05-12 UTC
Reviewed: `bridge/gtkb-bridge-automation-status-driver-001.md`

## Verdict

GO.

The proposal is sufficiently scoped for a read-only bridge automation status driver and status-surface enhancement. It preserves `bridge/INDEX.md` as canonical queue state, pins role-correct actionability, distinguishes dispatch from supplemental thread monitoring, and explicitly excludes restoring retired pollers or creating new recurring automation.

## Prior Deliberations

Required deliberation searches were performed before this review.

Commands:

```text
python -m groundtruth_kb deliberations search "bridge automation status driver cross harness trigger two axis" --limit 8
python -m groundtruth_kb deliberations search "retired smart poller bridge automation status owner disposition" --limit 8
```

Relevant results:

- `DELIB-1887` - verified compressed thread for `gtkb-startup-trigger-awareness-and-skill-reference-001`.
- `DELIB-1520` - Loyal Opposition verification of trigger-awareness and the two-axis bridge automation model.
- `DELIB-1521` - Loyal Opposition GO for the two-axis bridge automation articulation.
- `DELIB-1522` - earlier NO-GO rejecting unapproved ratification of specific Codex-side automations.
- `DELIB-1549`, `DELIB-1551`, and `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - smart-poller policy and retirement context.
- `DELIB-1511`, `DELIB-1533`, and related results - single-harness dispatcher and active-session suppression context.

No prior deliberation result blocks a read-only status driver. The relevant constraint is that the implementation must not ratify external thread automations as canonical dispatch or restore any retired poller surface.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-automation-status-driver
```

Result:

```text
## Applicability Preflight

- packet_hash: `sha256:b5e2ce236b27c2051d353b8cdca2b041a20419139c316e9d6d9f319dcb848911`
- bridge_document_name: `gtkb-bridge-automation-status-driver`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-automation-status-driver-001.md`
- operative_file: `bridge/gtkb-bridge-automation-status-driver-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-automation-status-driver
```

Result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-automation-status-driver`
- Operative file: `bridge\gtkb-bridge-automation-status-driver-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Evidence Reviewed

- `bridge/gtkb-bridge-automation-status-driver-001.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/prime-bridge-collaboration-protocol.md`
- `config/agent-control/system-interface-map.toml`
- `groundtruth-kb/src/groundtruth_kb/operating_state.py`
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-006.md`
- `bridge/gtkb-bridge-skill-unified-001-004.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md`

I also checked the current shallow status behavior from the GT-KB project root:

```text
python -m groundtruth_kb status --component bridge --component bridge-dispatch --json
```

Observed result: PASS with `158 bridge thread(s); Prime actionable=44; Loyal Opposition actionable=3` and `2 dispatch recipient(s) tracked`. The output remains shallow as the proposal claims: it reports counts and recipients, not actionable document lists, dispatchability class, stale signature details, or external automation disposition.

## Findings

No blocking findings.

### F1 - Proposal correctly rejects the known VERIFIED-actionability defect

Severity: P1 risk avoided.

Evidence: the proposal requires Prime Builder actionability to be latest `GO` or `NO-GO` only, Loyal Opposition actionability to be latest `NEW` or `REVISED` only, and `VERIFIED` / `WITHDRAWN` to be terminal or non-actionable. This directly addresses the active `gtkb-bridge-skill-unified-001-004.md` NO-GO defect, where a bridge skill taught Prime Builder to process latest `VERIFIED` entries.

Impact: the proposed tests will protect a load-bearing bridge invariant and reduce role-confusion risk in startup, manual `Bridge` checks, and future status surfaces.

Required implementation constraint: preserve this exact actionability rule in code and tests. Do not import the incorrect `VERIFIED`-is-Prime-actionable rule from the current unified bridge skill.

### F2 - Read-only status scope is compatible with retired-poller constraints

Severity: P2 risk controlled.

Evidence: `.claude/rules/bridge-essential.md` identifies the cross-harness event-driven trigger and single-harness dispatcher as the live dispatch substrates, while retired smart-poller and retired OS-poller surfaces must not be restored. The proposal keeps this slice read-only, excludes new recurring automation, and marks external Codex thread automation inventory as external/unverified unless directly inspectable.

Impact: the proposal answers the owner's need for a standard operational driver without expanding runtime authority or creating a third dispatch substrate.

Required implementation constraint: the driver must not call dispatch subprocesses, write dispatch-state, mutate hook files, create scheduled tasks, create Codex or Claude app automations, or recommend retired pollers as fallback.

### F3 - Parser reuse should avoid a second divergent bridge parser

Severity: P3 implementation risk.

Evidence: P1 already added detector/parser surfaces under `groundtruth-kb/src/groundtruth_kb/bridge/`, and the status-driver proposal adds another queue classifier. The proposal is not blocked by this, but a second independent parser could drift from the P1 live-INDEX behavior.

Impact: duplicate parsing logic would increase maintenance risk around live `bridge/INDEX.md` comment blocks, `WITHDRAWN` rows, missing historical files, and line-number diagnostics.

Recommended action: implement the status driver by wrapping or reusing the existing P1 detector where practical. If implementation intentionally uses a separate parser, the report must explain why and include regression coverage for the live INDEX shapes already handled by P1.

## GO Conditions

Implementation is approved within the proposal's stated scope, with these constraints:

- Keep the driver read-only against bridge state and hook/config state.
- Use the live `bridge/INDEX.md` read as authoritative for queue state.
- Lock role-correct actionability in tests: Prime Builder `GO`/`NO-GO`; Loyal Opposition `NEW`/`REVISED`; `VERIFIED`, `WITHDRAWN`, and advisory or unsupported states non-actionable unless a future proposal changes the lifecycle contract.
- Distinguish status visibility from dispatch execution. The status driver is not a replacement runtime for `scripts/cross_harness_bridge_trigger.py` or `scripts/single_harness_bridge_dispatcher.py`.
- Mark external Codex thread automations as external/unverified unless the current runtime can inspect them directly.
- Keep any `gt bridge` command-group work gated or deferred if it conflicts with the unresolved `gtkb-bridge-skill-unified-001` NO-GO.
- Carry forward specification-derived test mapping and observed command results in the implementation report.

## Owner Action

None.
