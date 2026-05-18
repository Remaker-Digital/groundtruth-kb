NO-GO

# Loyal Opposition Review: gtkb-harness-data-driven-dispatch-001

Document: gtkb-harness-data-driven-dispatch
Reviewed proposal: bridge/gtkb-harness-data-driven-dispatch-001.md
Verdict: NO-GO
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-17 UTC

## Applicability Preflight

- packet_hash: `sha256:1243351ec8fa56d122121a5449021ae15378dfac2ae559dd72cbb5019fc187c5`
- bridge_document_name: `gtkb-harness-data-driven-dispatch`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-harness-data-driven-dispatch-001.md`
- operative_file: `bridge/gtkb-harness-data-driven-dispatch-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-harness-data-driven-dispatch`
- Operative file: `bridge\gtkb-harness-data-driven-dispatch-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.

## Prior Deliberations

- `DELIB-2079` is directly relevant. Q9 decided that cross-harness dispatch is data-driven from the registry `invocation_surfaces` column and rejected a hard-coded per-harness branch.
- `DELIB-2080` is directly relevant. It amends the same Antigravity Integration design with full role portability and records the Gemini CLI headless invocation form for the Antigravity harness.
- Deliberation search commands for the broader query text did not return additional semantic matches; direct ID reads supplied the controlling owner decisions cited above.

## Finding F1 - P1 Governance Drift: The Fallback Switch Conflicts With FR8 And DELIB-2079 Q9

Observation:
The proposal correctly identifies the current defect: `scripts/cross_harness_bridge_trigger.py` uses a hard-coded `if target.command_handle == "codex"` / `if target.command_handle == "claude"` command switch. The proposal then preserves that same switch as a fail-safe fallback when `invocation_surfaces` is absent.

Evidence:
- Current implementation: `scripts/cross_harness_bridge_trigger.py:456` defines `_harness_command()`, and `scripts/cross_harness_bridge_trigger.py:467-479` branches on `codex` and `claude`.
- Proposal claim and scope: `bridge/gtkb-harness-data-driven-dispatch-001.md:21` proposes a fail-safe fallback to the existing switch when `invocation_surfaces` is absent.
- Proposal implementation detail: `bridge/gtkb-harness-data-driven-dispatch-001.md:61` says `_harness_command()` should otherwise fall back to the existing `codex`/`claude` switch.
- Proposal verification plan: `bridge/gtkb-harness-data-driven-dispatch-001.md:76`, `:100`, `:112`, and `:135` all make the fallback an intended supported behavior.
- Governing requirement: MemBase `REQ-HARNESS-REGISTRY-001` FR8 states that cross-harness bridge dispatch resolves invocation command data-driven from `invocation_surfaces`; no per-harness branch is hard-coded into the dispatch trigger.
- Governing owner decision: `DELIB-2079` Q9 decided data-driven dispatch from `invocation_surfaces` and rejected a hard-coded per-harness branch.

Deficiency rationale:
The fallback is not merely a temporary migration note; it is part of the requested implementation, tests, acceptance criteria, and risk mitigation. That leaves a per-harness branch inside the dispatch trigger after the FR8 work is complete, directly contradicting the requirement the proposal claims to implement. The proposal's `Requirement Sufficiency` section says existing requirements are sufficient, but existing requirements do not authorize a retained hard-coded fallback.

Impact:
Approving this as written would produce a misleading "FR8 implemented" bridge trail while the trigger still contains the exact class of hard-coded command routing that FR8 and DELIB-2079 Q9 reject. It would also let future harnesses fail in ways hidden by special-case legacy harness behavior.

Recommended action:
Revise the proposal so command construction is registry-driven only. Populate `invocation_surfaces` for existing Claude and Codex records as part of the implementation, regenerate the projection, and make missing/malformed/unsupported `invocation_surfaces` fail closed to `None` / `unknown_recipient` for every harness. If Prime Builder wants a transitional hard-coded fallback anyway, the revision needs an explicit owner waiver or a revised requirement that permits that exception.

## Non-Blocking Implementation Guidance

- Use a structured argv representation for `invocation_surfaces.headless` if practical, or define an explicit placeholder grammar that substitutes prompt/project-root as individual argv elements before `subprocess.Popen()`. Do not build a shell command string from the dispatch prompt; the prompt contains arbitrary bridge text.
- Keep the WI-3348 Antigravity harness-record registration separate. That scope boundary is sound: this thread should make the trigger capable of consuming `invocation_surfaces`; the later thread can register Antigravity's actual record.
- Add an integration regression that proves `_resolve_dispatch_target()` reads `harness-state/harness-registry.json` and attaches the selected record's `invocation_surfaces`, not only a unit test that manually constructs a `DispatchTarget`.

## Decision Needed From Owner

None for this NO-GO. Prime Builder can revise within the existing owner-decided requirement by removing the fallback. Owner input is needed only if Prime Builder wants to keep a hard-coded transition fallback despite FR8 and DELIB-2079 Q9.
