ADVISORY

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 0d69ab41-3cfc-482d-b5b6-8e2d619eb024
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Advisory - No mechanical gate detects bridge lifecycle/status-semantics misuse

bridge_kind: governance_advisory
Document: gtkb-lo-bridge-lifecycle-semantics-gate-gap-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC

---

## Source

Observed while reviewing
`bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-001.md` during a
scheduled Loyal Opposition worker run on 2026-07-28. The verdict is filed at
`bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-002.md` (NO-GO);
its FINDING-P0-001 is the concrete instance that exposed this gap. This advisory
is scoped to the *missing gate*, not to the WI-5659 substance.

## Claim

**A bridge proposal can declare a structurally impossible lifecycle and pass
every mechanical gate the protocol currently runs.**

The `-001` proposal declared its target lifecycle as:

```text
NEW -001 -> GO -002 -> NO-ACTION -003 -> VERIFIED -004
```

`NO-ACTION` is defined by `DCL-NO-ACTION-STATUS-SEMANTICS-001` and owner decision
`DELIB-HARNESS-OPS-NO-ACTION-LO-REAUTHORIZATION-PATH-20260702` as a Prime Builder
rejection of a defective Loyal Opposition verdict. Its routing
(`groundtruth-kb/src/groundtruth_kb/bridge/disposition.py:126-127`) returns
`("lo_no_action_review_required", "review_no_action")`, whose defined output is a
corrected `GO` — not `VERIFIED`. The declared step 4 is therefore unreachable by
the routing the proposal itself selects, and the `-003` entry would permanently
assert in an append-only chain that the `-002` `GO` was governance-non-compliant
when it was not.

Both mandatory preflights passed cleanly on that proposal:

- `scripts/bridge_applicability_preflight.py` — exit 0,
  `preflight_passed: true`, `missing_required_specs: []`,
  `missing_advisory_specs: []`.
- `scripts/adr_dcl_clause_preflight.py` — exit 0, 5 clauses evaluated,
  `must_apply: 3` all with evidence, **0 blocking gaps**.

**Why both passed.** The applicability preflight asks *which cross-cutting specs
are triggered and are they cited*. The clause preflight asks *for each registered
clause, is there evidence in the text*. Neither asks *is the declared sequence of
status tokens a legal walk of the lifecycle graph*. `DCL-NO-ACTION-STATUS-SEMANTICS-001`
is not among the five clauses registered in
`config/governance/adr-dcl-clauses.toml` for this path, so no clause fired; and
even had it fired, the evidence test is presence-based, not semantics-based.

Only human-equivalent reviewer judgment caught it. That is precisely the class of
check the two-layer defense-in-depth model in
`GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` exists to mechanize.

**Severity: P2 (capability overclaim).** The gates are advertised as the
mechanical floor for bridge correctness, and a reviewer who trusts a clean
double-preflight as evidence of lifecycle validity will approve an unexecutable
sequence. The defect is latent rather than active: it produces a bad artifact
only when a proposal declares a lifecycle, which not all do.

**Scope note.** The lifecycle graph is already encoded in code and is machine-
checkable today — `disposition.py` (`PRIME_ACTIONABLE_STATUSES`,
`LOYAL_OPPOSITION_ACTIONABLE_STATUSES`, `TERMINAL_OR_CLOSED_STATUSES`),
`routing.py` (`_PRIME_STATUSES` / `_CODEX_STATUSES`), and
`scripts/gtkb_bridge_writer.py` (`_validate_provider_transition`). What is
missing is any consumer that applies that graph to a *declared future* lifecycle
in proposal prose, as opposed to validating one *actual* transition at
publication time. `_validate_provider_transition` would have rejected the
`NO-ACTION -> VERIFIED` step at `-004`, but only after `-003` had already been
written into the permanent chain.

This is a genuine gap, not a duplicate of
`bridge/gtkb-lo-verdict-filing-path-advisory-001.md`, which concerns the
Claude-side verdict *filing path* rather than lifecycle validation.

## Prior Deliberations

- `DELIB-HARNESS-OPS-NO-ACTION-LO-REAUTHORIZATION-PATH-20260702` — owner decision
  establishing the `NO-ACTION` semantics that the observed proposal violated.
- `DELIB-HARNESS-OPS-NO-ACTION-FIRST-CLASS-BRIDGE-STATUS-20260702` — owner
  decision establishing `NO-ACTION` as a first-class PB-authored status token.
- `DELIB-202666040` — VERIFIED verdict on
  `gtkb-wi5081-document-no-action-semantics`; documented the semantics on two
  authority surfaces and added a *presence*-regression test, which is exactly the
  test shape that cannot catch this misuse.
- `DELIB-202666567` — `review_no_action` corrected-verdict precedent showing the
  path's actual output is a corrected `GO`.

## Owner Decision Needed

None to record this advisory. It requests no approval, waiver, priority choice,
deployment, or destructive action.

Before Prime Builder files a derived implementation proposal, durable
AskUserQuestion-recorded answers are required to:

1. Should lifecycle validation be added as a **new registered clause** under
   `DCL-NO-ACTION-STATUS-SEMANTICS-001` in `config/governance/adr-dcl-clauses.toml`
   (cheap, reuses the existing clause-preflight surface, but limited to
   pattern-shaped evidence), or as a **dedicated lifecycle-walk check** in
   `scripts/bridge_applicability_preflight.py` or a new preflight that parses
   declared status sequences and validates them against the routing graph
   (costlier, but actually semantic)?
2. Should a declared-lifecycle block become a **required, machine-readable
   section** in proposals that declare one (for example a fenced
   `lifecycle:` block), so the check has an unambiguous parse target rather than
   scraping prose? This is the main cost driver and the main reliability driver.
3. Should the check be **blocking or advisory on first landing**? The
   clause-preflight precedent (Slice 1 advisory, Slice 2 mandatory) suggests a
   staged rollout, but a false-negative here writes a permanently wrong entry
   into an append-only chain.
4. Is the narrower fix sufficient — extend `_validate_provider_transition` to
   reject a `NO-ACTION` whose thread has **no prior LO verdict to correct**,
   catching the structural precondition at publication time even when the
   declared lifecycle is not parsed at all?

## Recommended Prime Action

File an implementation proposal covering, in priority order:

1. **Publication-time precondition check (narrowest, highest value).** Extend
   `_validate_provider_transition` in `scripts/gtkb_bridge_writer.py` so a
   `NO-ACTION` publication fails closed unless the immediately-prior version is a
   Loyal Opposition `GO` or `NO-GO`. This directly enforces condition 2 of the
   "well-formed NO-ACTION" definition in
   `.claude/rules/file-bridge-protocol.md` and would have blocked the observed
   `-003` before it entered the chain, independent of whether any proposal-time
   lifecycle parsing is ever built. Add a regression test asserting the rejection.
2. **Declared-lifecycle validation (broader).** Subject to owner answers 1-3,
   add a check that extracts declared status sequences from proposal bodies and
   validates each transition against the routing graph in `disposition.py` /
   `routing.py`, reporting any illegal edge. Reuse the existing graph; do not
   restate it, or the check becomes its own drift surface.
3. **Clause registration.** Register `DCL-NO-ACTION-STATUS-SEMANTICS-001` in
   `config/governance/adr-dcl-clauses.toml` for bridge-path proposals so the
   clause preflight at minimum surfaces the DCL as applicable, even before
   semantic validation exists.
4. **Documentation.** Note in `.claude/rules/file-bridge-protocol.md` that a
   clean applicability + clause preflight is *not* evidence of lifecycle
   validity, so reviewers do not over-trust a green double-preflight.

Item 3 touches `config/governance/`; item 4 touches a protected narrative
artifact under `.claude/rules/` and therefore carries formal-artifact approval
requirements per `GOV-ARTIFACT-APPROVAL-001`.

Governing specifications: `GOV-FILE-BRIDGE-AUTHORITY-001` (bridge audit-trail
integrity and lifecycle authority), `DCL-NO-ACTION-STATUS-SEMANTICS-001` (the
violated contract), `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
(two-layer mechanical enforcement of cross-cutting requirements),
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (a wrong status token becomes permanent
append-only evidence), and `GOV-STANDING-BACKLOG-001` (backlog capture).

## Classification Slot

Classification: **adapt**.

The gap is real and the narrowest remediation (item 1) is well-bounded and
clearly correct. But the broader shape — whether GT-KB should parse declared
lifecycles from proposal prose at all, and at what enforcement severity — is a
Prime Builder and owner decision with real cost and false-positive tradeoffs, not
a Loyal Opposition prescription. This advisory does not authorize implementation;
it requests the owner-grilling pass enumerated under "Owner Decision Needed"
before any derived proposal is filed, per
`GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
