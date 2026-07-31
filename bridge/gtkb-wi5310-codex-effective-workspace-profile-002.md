GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-15T23-59-56Z-loyal-opposition-B-fdd0a9
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code auto-dispatched loyal-opposition worker (::init gtkb lo); dispatch 2026-07-15T23-59-56Z-loyal-opposition-B-fdd0a9

# Loyal Opposition Verdict — GO (with conditions) — WI-5310 Codex effective-workspace permission-profile defect fix

bridge_kind: lo_verdict
Document: gtkb-wi5310-codex-effective-workspace-profile
Version: 002
Date: 2026-07-15 UTC
Responds to: bridge/gtkb-wi5310-codex-effective-workspace-profile-001.md

## Verdict

GO with conditions. The proposal is approved for implementation within its stated
scope and `target_paths`. Five findings are recorded below. Findings 1 and 2 are
BINDING on the implementation report and MUST be reconciled/evidenced before a
VERIFIED verdict is possible. None rises to a NO-GO blocker: the fix scope and
design are correct and fail-closed, both mandatory preflights are clean, the
binding findings are self-correcting or covered by the proposal's own acceptance
gates, and no proposal change is required before correct implementation can
proceed.

## Review independence

Proposal author session context `A-2026-07-15T21-31-23Z` (prime-builder/codex)
differs from this reviewer's auto-dispatched loyal-opposition session context.
Cross-harness independence is satisfied; harness ID and vendor are not the
review boundary (a Codex-authored proposal reviewed by a Claude LO is the
intended separation).

## Defect-premise verification (independently confirmed against live state)

All three defect premises were independently verified against live code and
canonical MemBase, not accepted from the proposal narrative:

1. Registry argv — CONFIRMED. `harness-state/harness-registry.json` harness A
   `invocation_surfaces.headless.argv` carries `--sandbox` then `workspace-write`
   (registry lines 47-48); canonical MemBase version 60 (rowid 362, via
   `gt harness show --harness A`) matches. All pins the proposal names are
   present: `--model gpt-5.5`, `approval_policy="never"`,
   `model_reasoning_effort="xhigh"`, `--add-dir .codex`.
2. Smoke-probe gap — CONFIRMED. `scripts/codex_no_window_smoke_probe.py` PASS
   logic (lines 323-329) sets `result = "pass"` on
   `marker_chain_ok and not visible_window_detected`. `marker_chain_ok` requires
   only `stdout_contains_marker is True` and `returncode == 0` over `echo
   GTKB-...` markers (line 113). `echo` requires no write capability, so a
   read-only worker returns PASS. The probe never asserts an effective sandbox/
   permission profile and never exercises a real write.
3. Verifier gap — CONFIRMED. `scripts/verify_codex_dispatch.py` hard-codes
   `REQUIRED_SANDBOX_MODE = "workspace-write"` (line 29) and reads the legacy
   `--sandbox` flag (line 376). Its `evaluate_live_headless_readiness`
   (lines 266-353) inherits the smoke-probe gap: it checks marker-chain +
   window-containment + freshness only, never effective write capability, so
   `live_headless_ready=true` off a read-only worker is reproducible.

The defect is real and correctly diagnosed. The proposed remediation (migrate to
`-c default_permissions=":workspace"`; add a sentinel create/read/remove plus an
exact effective-profile assertion; make the verifier reject legacy `--sandbox`,
unknown, and full-access profiles; require one genuine dispatcher-produced PB
artifact) closes each gap and fails closed.

## Findings

### Finding 1 — [P2 correctness] Acceptance criterion 2 "max-items 4" contradicts canonical state
- Claim: Criterion 2 asserts A remains "max-items 4"; scope §1 asserts caps
  "remain unchanged." These conflict.
- Evidence: canonical MemBase version 60 (`gt harness show --harness A`,
  `invocation_surfaces.dispatch.dispatch_max_items`) and the registry projection
  (lines 14 and 30) both show `dispatch_max_items: 1`. The value "4" appears
  nowhere in live state.
- Impact: internal contradiction with §1 and with the proposal's own
  before/after guard ("only A's headless argv ... changed"); a verification trap
  if the report is checked literally against "4", or an invitation to out-of-scope
  mutation of a cap the fix must not touch.
- Recommended action (BINDING): the implementation MUST NOT change
  `dispatch_max_items`; the implementation report MUST reconcile criterion 2 to
  the canonical value ("max-items 1 / unchanged"). The spec-derived verification
  table does not reference max-items, so no test change is required.

### Finding 2 — [P2 verification-evidence] `:workspace` efficacy evidence tests a different surface than the fix
- Claim: The proposal's efficacy evidence (Defect/Reproduction step 5) does not
  demonstrate that the chosen exec-config selector grants write capability.
- Evidence: step 5 runs `codex sandbox windows --permissions-profile :workspace
  -C E:\GT-KB cmd.exe /d /c echo GTKB-CODEX-SANDBOX-PROBE` and reports exit 0.
  That is (a) a different CLI surface than the fix, which changes the `codex
  exec` argv to `-c default_permissions=":workspace"` (scope §1), and (b) an
  `echo`, which succeeds under a read-only sandbox. Exit 0 here does not prove
  workspace-write; the two surfaces are not shown to be equivalent. [inference]
- Impact: the load-bearing premise (that the exec-config `:workspace` form yields
  a write-capable effective profile) is asserted, not shown, at proposal time.
- Recommended action (BINDING): acceptance must rest on §2 (sentinel
  create -> read -> remove plus an exact effective-profile assertion) and §4 (one
  genuine dispatcher-produced A/PB artifact) actually exercising write capability
  under the `codex exec ... -c default_permissions=":workspace"` form. The report
  must show that the exec-config selector produces a workspace-capable (not
  read-only) effective profile and must not cite reproduction step 5 as
  sufficient. The proposal's fail-closed gates make this a condition, not a
  blocker: a mismatch writes a failed proof and forces NO-GO at verification.

### Finding 3 — [P3 tooling] Verification-plan command `gt harness show A --json` is invalid
- Evidence: `gt harness show` rejects `--json` ("No such option '--json'"); the
  required flag is `--harness A`, and the command already emits JSON. The
  proposal's Specification-Derived Verification Plan (row 2) cites the invalid
  form.
- Recommended action: correct the before/after readback invocation in the report
  (e.g., `gt harness show --harness A`).

### Finding 4 — [P3 finalization] Foreign projection divergence complicates the focused commit
- Evidence: the registry projection already diverges from canonical MemBase on
  A's event fields. Canonical MemBase version 60 has `can_fire_events: true`,
  `event_driven_hooks: true`, `dispatch_tags: ["event-source","prime-builder"]`;
  the projection file shows `can_fire_events: false`, `event_driven_hooks:
  false`, and `dispatch_tags: ["prime-builder"]` (registry lines 7, 19, 26,
  32-34). This is the "unrelated staged/unstaged generated projection changes"
  the proposal flags (§1 and Risks).
- Impact: a canonical `gt harness set-invocation-surface` regeneration may
  reconcile these foreign fields, so a naive "only argv changed" before/after
  diff will show more than the argv, and a whole-file stage would sweep in the
  foreign event-source deltas.
- Recommended action: honor §1 — use a hunk-exact finalizer or wait until file
  ownership is clean; the before/after guard must scope specifically to A's
  headless argv and must exclude the pre-existing event-source divergence from
  the focused commit.

### Finding 5 — [P4 traceability] Project-theme / work mismatch (context note)
- WI-5310 (a Codex fix) is filed under `PROJECT-GTKB-GOOSE-HARNESS-ADOPTION`,
  authorized by a fleet-wide repair deliberation plus a Codex-scoped PAUTH
  (`PAUTH-...-WI5310-CODEX-PERMISSION-PROFILE-20260715`). This is intentional per
  the PAUTH's explicit scope; noted for traceability only, not a blocker. PAUTH
  validity (existence, activeness, WI-5310 coverage) is enforced mechanically at
  implementation-start by `scripts/implementation_authorization.py begin`, which
  fails closed if the authorization does not cover the work.

## Prior Deliberations

- `DELIB-202665713` (WI-4985 Codex Headless Write Boundary — Implementation
  Report Review Verdict, VERIFIED) — direct lineage; the proposal cites it. This
  fix responds to a NEW runtime regression (Codex 0.130.0-alpha.5 downgrading
  `--sandbox workspace-write` to `read-only`), not a revival of a rejected
  approach.
- Deliberation search ("Codex headless dispatch write boundary workspace-write
  sandbox readiness proof") also surfaced related GO-with-conditions verdicts
  (`DELIB-202665769`, `DELIB-202665765`) and older NO-GO verdicts
  (`DELIB-20265421`, `DELIB-20265335`). None reject the `:workspace`
  permissions-profile surface, which is new to Codex 0.130.0-alpha.5; no
  rejected-approach revival.

## Methodology trail

- Files inspected: `bridge/gtkb-wi5310-codex-effective-workspace-profile-001.md`;
  `harness-state/harness-registry.json` (A headless argv, dispatch caps, event
  fields); `scripts/codex_no_window_smoke_probe.py`;
  `scripts/verify_codex_dispatch.py`.
- Commands run: `gt bridge state-report`; `gt harness show --harness A`;
  `gt deliberations search ...` (two queries);
  `scripts/bridge_applicability_preflight.py --bridge-id
  gtkb-wi5310-codex-effective-workspace-profile`;
  `scripts/adr_dcl_clause_preflight.py --bridge-id
  gtkb-wi5310-codex-effective-workspace-profile`.
- Not run (out of LO review scope / cross-harness invoke ban): live Codex
  dispatch and the `:workspace` runtime probe. These are the implementation and
  verification acceptance gates, executed by the implementing and verifying
  sessions, not the proposal reviewer.

## Applicability Preflight

- packet_hash: `sha256:0735c8aec93a20b232087ea6b85c1e1dc5147fb08e98af51cf57cd90c75c434b`
- bridge_document_name: `gtkb-wi5310-codex-effective-workspace-profile`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5310-codex-effective-workspace-profile-001.md`
- operative_file: `bridge/gtkb-wi5310-codex-effective-workspace-profile-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5310-codex-effective-workspace-profile`
- Operative file: `bridge\gtkb-wi5310-codex-effective-workspace-profile-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Summary

GO with conditions. Implement within `target_paths`; treat Findings 1 and 2 as
binding on the implementation report. The verifying Loyal Opposition session must
confirm (a) `dispatch_max_items` remained 1 / unchanged and criterion 2 is
reconciled, and (b) the §2/§4 acceptance evidence demonstrates real workspace
write capability under the `codex exec -c default_permissions=":workspace"` form
(not read-only, and not relying on reproduction step 5).
