NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: f9e95f49-a164-41e3-8b40-cb2b1f2351b1
author_model: Claude Opus 5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; build activity envelope
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: prime_proposal
Document: gtkb-wi6019-substrate-set-reject-permanence
Version: 001
Work Item: WI-6019
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-AUTHORIZE-WI-6019-IMPLEMENTATION

target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py"]
implementation_scope: source_and_test_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# WI-6019 — Make The Legacy Dispatcher Substrate Permanently Unselectable (SET-Reject, READ-Accept)

## Problem

The owner directive of 2026-08-07 requires the legacy TAFE dispatcher to be **permanently disabled
immediately**. Today it is disabled only by convention plus state:

- `harness-state/bridge-substrate.json` records `{"substrate": "none", "applied_by": "C",
  "applied_at": "2026-08-02T22:59:42Z"}`, clean against HEAD.
- The standing prohibition is archived as `DELIB-20260807-DISPATCHER-DISABLED-MANUAL-BRIDGE-OPERATION`.

Nothing mechanically prevents re-selection. `gt mode set-bridge-substrate` accepts the legacy
value, so "permanently disabled" rests entirely on narrative authority.

**Narrative authority failed twice on 2026-08-07.** A Prime Builder session asserted the dispatcher
daemon was the live canonical bridge path, having read always-loaded rule prose without consulting
the substrate record (`WI-6002`). Separately, a concurrent session deleted the
`harness-bridge-substrate` source-of-truth registration from `config/registry/sot-artifacts.toml`
outright — removing the `owner_only` mutation control and the `forbidden_substitutes` guard — and
hard-blocked governed bridge publication platform-wide (`WI-6014`).

A mechanical SET-rejection survives both failure modes, because it does not depend on the agent
having consulted the correct source-of-truth first.

## Current State (verified)

`groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py`:

- `:27` — `DISPATCHER_DAEMON_SUBSTRATE = "dispatcher_daemon"`
- `:224` — `validate_bridge_substrate(project_root: Path, new_substrate: str, topology: str) -> ValidationResult`

```python
allowed = {"none", DISPATCHER_DAEMON_SUBSTRATE}
if new_substrate not in allowed:
    return _fail(axis, f"unknown bridge substrate {new_substrate!r}")

if new_substrate == DISPATCHER_DAEMON_SUBSTRATE:
    probe = _probe_dispatcher_daemon_readiness(project_root)
    if not probe.get("ok"):
        return _fail(axis, str(probe.get("message") or "dispatcher daemon is not ready"))

return _ok(axis)
```

The legacy substrate is therefore selectable whenever a readiness probe passes.

## Proposed Change

Replace the readiness-probe branch with an unconditional SET-rejection carrying an owner-visible
diagnostic that cites the governing decisions. `"none"` remains the only selectable substrate.
Dispatcher Next receives its own substrate value when it activates; it does not revive this
identifier.

**READ-acceptance is preserved structurally, not by additional code.** The two readers parse
`harness-state/bridge-substrate.json` directly and never call this validator:

- `scripts/dispatcher_runtime.py:5581` / `:5587`
- `scripts/gtkb_dispatcher_daemon.py:291` / `:292`

Historical and existing substrate records therefore continue to load unchanged. The proposed edit
touches only the write path.

## Precedent Being Mirrored

`scripts/harness_roles.py` already implements this exact READ-accept / SET-reject asymmetry for the
legacy role value `acting-prime-builder`, per `GOV-ACTING-PRIME-BUILDER-001` and
`.claude/rules/acting-prime-builder.md` § Compatibility/Provenance Classification. This proposal
reuses that established pattern rather than introducing a second idiom for the same problem.

## Scope Boundary

This work is **machine-readable enforcement**, which `DELIB-20260807011937` places explicitly OUT
of the D3 purge scope. It is deliberately separate from `WI-6018` (purge of live agent-facing
direction) and must not be merged with it. Purging enforcement in the name of purging references is
precisely what produced `WI-6014`.

No agent-facing narrative is edited by this slice. The accepted-substrate-value documentation in
`.claude/rules/operating-role.md` is purge scope and belongs to `WI-6018`, so no protected
narrative artifact and no formal-artifact approval packet is required here.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing requirement is supplied by owner decision
`DELIB-20260807011938` (mechanical block on re-selection, SET-reject with READ-accept, mirroring
the `acting-prime-builder` precedent). No new or revised specification is required before
implementation.

## Specification Links

- `DELIB-20260807011938` — the owner decision selecting mechanical SET-rejection as the enforcement
  mechanism for "permanently disabled".
- `DELIB-20260807-DISPATCHER-DISABLED-MANUAL-BRIDGE-OPERATION` — the standing prohibition this
  change enforces mechanically.
- `DELIB-20260807011937` — D3 purge scope; places machine-readable enforcement out of purge scope,
  establishing this slice's boundary against `WI-6018`.
- `GOV-ACTING-PRIME-BUILDER-001` — the READ-accept / SET-reject compatibility precedent.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — `authority_spec_id` registered for the
  `harness-bridge-substrate` SoT artifact in `config/registry/sot-artifacts.toml`.
- `GOV-PLATFORM-SOT-REGISTRY-001` / `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` — the SoT registration of
  `harness-state/bridge-substrate.json`, unchanged by this slice.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — state claims derive from fresh canonical reads; the failure
  mode this change defends against.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — linkage mandate this proposal satisfies.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — governs the verification below.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail authority.
- `DELIB-20260807011939` — owner standing directive that auditability is second-class during the
  build; relevant to the reviewer note below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance stance; the owner decisions
  governing this slice were preserved as Deliberation Archive records rather than left in session
  context, and this proposal cites them by ID.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development decision underlying that
  stance; the enforcement change is captured as a durable work item plus bridge chain, not as an
  in-session correction.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle triggers; an owner decision selecting a
  mechanical enforcement mechanism is a capture-threshold event, discharged here by
  `DELIB-20260807011938`, `WI-6019`, and this bridge thread.

## Bridge Chain Canonicality

The canonical record for this work is the numbered bridge file chain under `bridge/` for document
`gtkb-wi6019-substrate-set-reject-permanence`, beginning at `-001` (this proposal). Each subsequent
version is appended with a monotonically incremented number and is never rewritten or deleted;
the chain plus its status tokens is the audit trail for this slice, and no aggregate queue artifact
is authoritative for it. Loyal Opposition verdicts and the post-implementation report will be
appended as `-002`, `-003`, … in that chain, per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Specification-Derived Verification Plan

| Requirement | Test | Location |
| --- | --- | --- |
| `DELIB-20260807011938`: legacy substrate is SET-rejected | `validate_bridge_substrate(..., "dispatcher_daemon", ...)` returns a failing `ValidationResult` regardless of daemon readiness | `test_mode_switch_bridge_substrate_validation.py` (new case) |
| `DELIB-20260807011938`: READ remains accepting | reading an existing `bridge-substrate.json` whose value is `dispatcher_daemon` succeeds and does not raise | same file (new case) |
| `"none"` remains selectable | `validate_bridge_substrate(..., "none", ...)` returns ok | existing coverage, re-asserted |
| Unknown values still rejected distinctly | an unrecognized value fails with the existing `unknown bridge substrate` diagnostic, not the new one | same file (new case) |
| Diagnostic is owner-actionable | the rejection message cites the governing decision so a future session reads the reason, not just a refusal | same file (new case) |

Commands to be run at implementation time:

```text
python -m pytest platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py -q --tb=short
python -m pytest platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py -q --tb=short
python -m ruff check <changed.py>
python -m ruff format --check <changed.py>
gt registry validate --json
```

Note for the reviewer: an executed pytest run on 2026-08-07 found the suite **already red at HEAD**
(22 missing governance artifacts, 4 fab05 failures, 1 harness-parity failure). Verification
evidence for this slice is therefore scoped to the named modules plus a before/after comparison,
not a whole-suite green claim.

## Risk / Rollback

- **Risk: Dispatcher Next is blocked later by this rejection.** Mitigated by design — Dispatcher
  Next receives its own substrate value; this change rejects one legacy identifier, not the concept
  of a substrate.
- **Risk: an operational need to re-enable the legacy dispatcher arises.** Accepted deliberately.
  The owner directed permanent disablement; re-enabling would require a fresh owner decision and a
  reverting change, which is the intended cost.
- **Risk: a caller depends on the readiness-probe branch.** Checked — `_probe_dispatcher_daemon_readiness`
  is reached only through this branch of `validate_bridge_substrate`; the doctor check
  `_check_dispatcher_only_bridge_automation` reads substrate state independently.
- **Rollback:** revert one branch in one function plus the added test cases. No state migration, no
  data change, no effect on existing `bridge-substrate.json` content.

## Owner Decisions / Input

- `DELIB-20260807011938` — AskUserQuestion 2026-08-07, session
  `f9e95f49-a164-41e3-8b40-cb2b1f2351b1`: owner selected **"Mechanical block on re-selection"** over
  deleting the substrate mechanism entirely and over relying on the directive alone. The rejected
  alternatives and their rationale are recorded in that deliberation.
- `DELIB-20260807011939` — owner standing directive: auditability is second-class during the build;
  Loyal Opposition `GO` and `VERIFIED` are retained, surrounding ceremony is reduced.
- Owner direction 2026-08-07, same session: "proceed with D3, don't wait for Goose… operate
  autonomously."

## Prior Deliberations

- `DELIB-20260807011938` — the governing enforcement decision (searched and cited above).
- `DELIB-20260807011937` / `DELIB-20260807011940` — D3 purge scope and its three amendments;
  establish that this slice is out of purge scope and separately owned.
- `DELIB-20260807-DISPATCHER-DISABLED-MANUAL-BRIDGE-OPERATION` — the standing prohibition.
- `DELIB-20260806011917` — purge before probative language. Considered and found not to bar this
  change: it governs agent-facing direction, while this is machine-readable enforcement. The
  alternative it would favour — removing the value from the enum entirely — was put to the owner and
  rejected for blast radius; that decision is recorded in `DELIB-20260807011938`.
- `WI-6014` — the same-day registry deletion that removed the substrate's SoT registration,
  motivating mechanical rather than declarative enforcement.

## Reviewer Note — PAUTH Forbidden-Operation Ambiguity

Disclosed rather than left for the reviewer to discover. The cited authorization lists
`dispatcher_mutation` among `forbidden_operations`, while listing `source` and `test` among
`allowed_mutation_classes`. This slice edits validator **source** and adds **tests**; it mutates no
dispatcher runtime, configuration, dispatch state, or scheduled task, and
`dispatcher_or_tafe_mutation_in_scope` is declared `false` above. It also makes the dispatcher
*harder* to activate, which is aligned with the standing prohibition rather than in tension with it.

If the operation-time PAUTH evaluation nevertheless classifies this as `dispatcher_mutation`, the
correct resolution is a scoped owner authorization for this work item, not a re-scoping of the
change. Flagged so the reviewer can rule on it explicitly.

## Recommended Commit Type

- Recommended commit type: `feat:` — adds a new enforcement behavior (a rejection path that did not
  previously exist) plus its regression coverage. Not `fix:`, because nothing was broken; the
  capability was simply unenforced.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
