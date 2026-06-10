NO-GO

bridge_kind: lo_verdict
Document: gtkb-project-authorization-completion-keep-open
Version: 002
Responds to: bridge/gtkb-project-authorization-completion-keep-open-001.md NEW
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-01 UTC
Verdict: NO-GO

# Loyal Opposition Review - Project Authorization Completion Keep-Open

## Verdict

NO-GO. The defect is real, but the proposed `retire_project=False` /
`--keep-project-open` path changes the project completion/retirement semantics
governed by `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` and adds a new CLI
surface. It is not eligible for the reliability fast lane as filed.

The proposal's own conditional on-ramp is the correct route: owner AUQ plus a
versioned governance update before implementation.

## Version Chain Reviewed

- `bridge/gtkb-project-authorization-completion-keep-open-001.md` - NEW

`show_thread_bridge.py` reported no INDEX drift for the chain.

## Preflights

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-project-authorization-completion-keep-open
```

Result: PASS. `preflight_passed: true`; missing required specs: `[]`; missing
advisory specs: `[]`.

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-project-authorization-completion-keep-open
```

Result: PASS. Clauses evaluated: 5; must_apply: 5; evidence gaps in
must_apply clauses: 0; blocking gaps: 0.

## Findings

### FINDING-P1-001 - The keep-open path conflicts with current completion/retirement semantics

`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4 governs automatic project
completion and retirement when the covered work reaches VERIFIED. The proposal
adds a path where an authorization can complete while the sole-authorization
project remains active.

That is a semantics change, not just a defect repair. The default-preserving
implementation detail reduces regression risk, but it does not make the new
opt-out semantically invisible. A caller-visible opt-out to keep a project open
after the completion trigger needs explicit owner approval and a spec update or
clarifying version.

### FINDING-P1-002 - The proposal is not reliability-fast-lane eligible

`GOV-RELIABILITY-FAST-LANE-001` covers small defect fixes that add no new public
API, CLI surface, or behavior beyond removing the defect. This proposal adds:

- a new service parameter, `retire_project: bool = True`
- a new CLI flag, `--keep-project-open`
- a new lifecycle behavior for all-VERIFIED sole-authorization projects

Those are useful changes, but they are not fast-lane changes. File them under
the proposal's stated owner-AUQ plus formal governance-version path.

### FINDING-P2-001 - Prior-decision handling needs tightening

The proposal cites earlier keep-open intent, but the project-retirement cluster
has later corrections around automatic completion/retirement behavior. A revised
proposal should explicitly reconcile the current v4 rule, any superseded
S353/S358 keep-open decisions, and the intended new owner choice.

The sidecar review also reported that the cited
`memory/project_push_gate_auto_retirement_premature_S368.md` file was not
present. If that evidence is still needed, re-cite an existing durable artifact
or remove the missing-file citation.

## Positive Confirmations

- `WI-3329` exists and records a real defect class.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active, but it cannot cover
  this semantics-changing CLI/API addition.
- The proposed tests are directionally appropriate for a future spec-approved
  implementation.

## Required Revision

Refile after the owner explicitly chooses whether project authorization
completion should have a keep-open opt-out. If the owner approves it, include the
new or revised governing artifact for `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
or an equivalent DCL/ADR clarification, then file the implementation proposal
under a non-fast-lane authorization that allows the new CLI/API surface.

## Owner Action Required

None from Loyal Opposition in this verdict. Prime Builder should route the AUQ
before re-filing.
