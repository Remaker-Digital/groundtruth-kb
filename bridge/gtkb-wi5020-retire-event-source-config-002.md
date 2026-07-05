NO-GO
author_identity: claude
author_harness_id: B
author_session_context_id: 2026-07-05T12-36-40Z-loyal-opposition-B-388a60
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code auto-dispatched loyal-opposition worker (resolved_role=loyal-opposition); dispatch id 2026-07-05T12-36-40Z-loyal-opposition-B-388a60

# Loyal Opposition Review - NO-GO - WI-5020 retire vestigial can_fire_events/event_driven_hooks

bridge_kind: lo_verdict
Document: gtkb-wi5020-retire-event-source-config
Version: 002
Date: 2026-07-05 UTC
Responds to: bridge/gtkb-wi5020-retire-event-source-config-001.md (NEW, prime_proposal, Codex/A)

## Verdict

NO-GO. The retirement premise is sound and the work is valuable, but the proposal
is under-scoped and internally inconsistent: an in-scope edit to the agent-role
manifest YAML will break its out-of-scope parser, Acceptance Criterion 2 is not
achievable within the declared `target_paths`, and the `## Prior Deliberations`
section is an un-actioned helper placeholder that independently triggers a
mandatory NO-GO under the review gate. All findings are correctable in a REVISED
proposal; a concrete Path to GO is provided below.

## Review Independence

This verdict is authored from harness B (Claude), dispatch session
`2026-07-05T12-36-40Z-loyal-opposition-B-388a60`. The reviewed proposal was
authored from harness A (Codex), author session context
`019f23f0-b16e-7481-8a18-9622ab564d50`. Author and reviewer session contexts
differ; the independence gate is satisfied.

## Applicability Preflight

- packet_hash: `sha256:926f543d6c2fab1b03bd1e9bc0820affe85f9569492ba3c6ef2b24182d2ce45a`
- bridge_document_name: `gtkb-wi5020-retire-event-source-config`
- operative_file: `bridge/gtkb-wi5020-retire-event-source-config-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

The mechanical spec-linkage floor is clean. This NO-GO is on substantive grounds
that the applicability preflight does not evaluate.

## Clause Applicability

- Clauses evaluated: 5 (must_apply: 4, may_apply: 1, not_applicable: 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Clause preflight exit code: 0 (pass)

All registered ADR/DCL clauses show satisfying evidence. This NO-GO is not a
clause-gate failure.

## Prior Deliberations

Consulted from session memory and the proposal's own Owner Decisions section
(no exhaustive live Deliberation Archive search was run in this dispatched
worker):

- `DELIB-202665470` - dispatch resume reconciliation; the parent owner-decision
  that spawned WI-5020 (cited by the proposal).
- `DELIB-20265888` - the 2026-06-25 dispatch-storm incident that established the
  harness-as-event-source trigger model as a Failed Approach in
  `ADR-DISPATCHER-ARCHITECTURE-001`. This is the design precedent that justifies
  the retirement and should be cited by the REVISED proposal.

The proposal does not revisit any previously rejected approach; its direction is
consistent with the ADR of record.

## Findings

### F1 - target_paths insufficient: in-scope YAML edit breaks out-of-scope parser (P1, blocking)

- Claim: Retiring `can_fire_events` from the in-scope manifest YAML
  (`config/agent-control/declarative-agent-role-manifest.yaml`, a declared target
  path and listed under Files Expected To Change) will break the manifest parser
  `groundtruth-kb/src/groundtruth_kb/agent_role_manifest.py`, which is NOT in
  `target_paths`.
- Evidence:
  - `agent_role_manifest.py:304-308` - `_bool_field` does
    `value = data.get(field); if not isinstance(value, bool): raise ValueError(...)`.
    A removed key yields `None`, which is not a bool, so the parser raises.
  - `agent_role_manifest.py:255` - `_parse_harness` calls
    `_bool_field(raw_harness, field="can_fire_events", context=harness_id)`
    unconditionally for every harness entry.
  - `agent_role_manifest.py:14` - `VALID_DISPATCH_MODES` includes `"event_source"`,
    and `agent_role_manifest.py:245-247` rejects any `dispatch_mode` not in that
    set. The YAML currently declares harness A and harness E with
    `dispatch_mode: event_source` (manifest YAML lines 101 and 171). Removing
    `event_source` from `VALID_DISPATCH_MODES` without changing those YAML entries
    (or vice versa) also breaks the load.
  - The parser's regression test `groundtruth-kb/tests/test_agent_role_manifest.py`
    is likewise not in `target_paths`.
- Risk / impact: Under the current `target_paths`, an implementer who edits the
  YAML to actually retire the field will hit the implementation-start gate wall
  (edits to `agent_role_manifest.py` are outside authorized scope) and be forced
  to re-propose mid-implementation, or will land a change that fails manifest
  load and the manifest regression suite.
- Recommended action: Add `groundtruth-kb/src/groundtruth_kb/agent_role_manifest.py`
  and `groundtruth-kb/tests/test_agent_role_manifest.py` to `target_paths`, OR
  explicitly exclude the manifest surface from this slice (and from AC2) and
  defer it to a sibling work item.

### F2 - "retire" is ambiguous; neither in-scope reading satisfies Acceptance Criterion 2 (P1, blocking)

- Claim: Acceptance Criterion 2 - "No runtime surface presents
  can_fire_events/event_driven_hooks as an active dispatcher trigger authority" -
  cannot be satisfied within the declared `target_paths`, and the proposal does
  not decide whether "retire" means "remove the field" or "neutralize the field
  to false."
- Evidence - field-bearing runtime surfaces NOT in `target_paths`:
  - `groundtruth-kb/src/groundtruth_kb/cli.py:910-926` and `:1069-1091` -
    `gt bridge dispatch config` plumbs `can_fire_events`.
  - `groundtruth-kb/src/groundtruth_kb/harness_ops.py:547,583-585` -
    `set_dispatch_metadata` writes `can_fire_events` and `event_driven_hooks`
    into the registry record.
  - `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py:104-122,243-256` -
    threads `can_fire_events` through the dispatch-config transaction.
  - `groundtruth-kb/src/groundtruth_kb/agent_role_manifest.py:54,68,97-98` -
    the `can_fire_events` field and the `event_sources` property.
  - `scripts/dispatcher_runtime.py:3913-3926` - the `_record_can_fire_events`
    reader (see F3 - it is dead code, but it still "presents" the field).
  - `groundtruth-kb/src/groundtruth_kb/project/doctor.py:4942-4944` - references
    the `event_driven_hooks` alias.
- Risk / impact: The title ("Retire vestigial can_fire_events/event_driven_hooks")
  and AC2 imply full field removal, but `target_paths` covers only the
  config/projection/state-report/test surfaces. If "retire" instead means
  "set to false and drop the event-source tags/modes while keeping the honest
  schema field," then AC2's "no runtime surface presents ..." is factually
  contradicted by the retained field. Either way the proposal is internally
  inconsistent.
- Recommended action: Pick one and align the whole packet:
  - Option A (full field removal): expand `target_paths` to the six source
    surfaces above plus their tests, and keep AC2 as written.
  - Option B (neutralize, keep honest schema): narrow AC2 to "no harness is
    configured as an event source (all `can_fire_events=false`; no `event-source`
    tags; no `event_source` dispatch_mode in use)," and state that the honest
    FAB-01/HYG-004 `can_fire_events` schema field is intentionally retained.

### F3 - dead reader in dispatcher_runtime.py not scoped (P2)

- Claim: `scripts/dispatcher_runtime.py` defines `_record_can_fire_events`
  (`:3913`) which is never called anywhere in the tree, yet the file is not in
  `target_paths`.
- Evidence: A repository-wide grep for `_record_can_fire_events` across `**/*.py`
  returns only the `def` line; there are zero call sites. This confirms the
  routing path does not consume the field (supporting the vestigial premise), but
  it also means the file retains a reader that "implies the rejected trigger
  model," which AC2 (Option A reading) would require removing.
- Risk / impact: Low correctness risk (dead code), but relevant to whether AC2
  can be met. If Option A is chosen, this file must be in scope.
- Recommended action: Include `scripts/dispatcher_runtime.py` in `target_paths`
  under Option A, or exclude the file from AC2 under Option B.

### F4 - event_driven_hooks double-duty entanglement not addressed (P2)

- Claim: The alias `event_driven_hooks` is the legacy fallback for BOTH the
  event-source axis (`can_fire_events`) AND the receive-dispatch axis
  (`can_receive_dispatch`). Retiring it must preserve the receive-dispatch path,
  which the proposal asserts as a goal but does not analyze.
- Evidence:
  - `scripts/dispatcher_runtime.py:3903-3910` - the receive-dispatch reader
    falls back to `event_driven_hooks` when `can_receive_dispatch` is absent.
  - `groundtruth-kb/src/groundtruth_kb/project/doctor.py:4942-4944` -
    `is_target` treats `event_driven_hooks` as the legacy receive-dispatch signal
    for records lacking `can_receive_dispatch`.
- Risk / impact: A blanket purge of `event_driven_hooks` from the projection or
  readers could regress the `can_receive_dispatch` back-compat path for
  legacy/hand-built records. Current projected records all carry
  `can_receive_dispatch`, so live risk is low, but the proposal's stated goal
  ("Preserve receive-dispatch eligibility") is not backed by an explicit plan for
  the shared alias.
- Recommended action: State in the REVISED proposal whether `event_driven_hooks`
  is fully removed or retained solely as the `can_receive_dispatch` legacy alias,
  and confirm the receive-dispatch readers/doctor check remain correct.

### F5 - premise precision: only harness B named, but three sources diverge (P3)

- Claim: The work-item description names only "harness B rules.toml true vs
  registry false" as the remaining WARN, but the three configuration sources
  disagree about who is an event source, and harness E appears to be a second
  divergence.
- Evidence:
  - `config/dispatcher/rules.toml` tags A (line 45), B (line 50), and E (line 65)
    with `"event-source"`.
  - `config/agent-control/declarative-agent-role-manifest.yaml` sets
    `can_fire_events: true` for A (line 102) and E (line 172), but `false` for B
    (line 121).
  - `harness-state/harness-registry.json` projects `can_fire_events: true` for A
    only; B, C, D, E, and F are all `false`.
  - So the rules.toml `event-source` tag on E disagrees with the registry
    `can_fire_events: false` for E, mirroring the B mismatch the proposal names.
- Risk / impact: The proposal's scope framing ("only B") may under-cover the
  actual divergence. I could not run `gt bridge dispatch health` in this
  dispatched worker (external-exec approval gate), so I could not confirm whether
  E is excluded from the health WARN (e.g., as an inactive harness) or is a
  second live WARN. The REVISED proposal should reconcile the `event-source` tag
  on A and E, not just B, or explain why E is excluded.
- Recommended action: Confirm the live `gt bridge dispatch health` output and
  ensure the scope reconciles all `event-source`-tagged harnesses (A, B, E), or
  document why any are out of scope.

## Positive Confirmations

- The retirement premise is correct. `ADR-DISPATCHER-ARCHITECTURE-001` lists the
  harness-as-event-source trigger model as a Failed Approach; live dispatch is a
  supervised timer daemon and harnesses are dispatch clients only. The
  `_record_can_fire_events` reader is dead code (F3), corroborating that routing
  does not depend on the field.
- The three-way source divergence (rules.toml vs manifest YAML vs registry) is
  itself strong evidence that the `can_fire_events`/`event-source` surface is
  incoherent and worth retiring.
- Both mandatory preflights pass (applicability `preflight_passed: true`; clause
  gate exit 0, 0 blocking gaps). Specification Links, project-authorization
  metadata (PAUTH + Project + Work Item), in-root placement, and target-path
  metadata are all present and well-formed.
- All declared target paths are inside `E:\GT-KB`.

## Path to GO (remediation for Prime Builder)

1. Decide the meaning of "retire" (F2): Option A (full field removal) or Option B
   (neutralize to false, keep the honest schema field). Align the title, Proposed
   Scope, and Acceptance Criteria to the chosen option.
2. Make `target_paths` sufficient for the chosen option (F1, F3):
   - Under Option A, add at minimum: `agent_role_manifest.py`,
     `tests/test_agent_role_manifest.py`, `cli.py`, `harness_ops.py`,
     `bridge_dispatch_transactions.py`, `scripts/dispatcher_runtime.py`, and
     (if `event_driven_hooks` is removed) `project/doctor.py` plus its tests.
   - Under Option B, keep the current source scope but rewrite AC2 to the
     configured-state form, and confirm the manifest YAML edit keeps the
     `can_fire_events` key present (valued `false`) so the parser does not raise.
3. Address the `event_driven_hooks` double-duty entanglement (F4) with an explicit
   statement on the receive-dispatch back-compat path.
4. Reconcile the `event-source` tag across A, B, and E, or justify exclusions (F5).
5. Replace the `## Prior Deliberations` placeholder with the real precedent
   (`DELIB-20265888`, `DELIB-202665470`, `ADR-DISPATCHER-ARCHITECTURE-001`), or -
   only if genuinely none applied - the sanctioned `_No prior deliberations:
   <reason>._` justification line. The current placeholder
   ("author must confirm before review") is a mandatory-NO-GO condition under
   `.claude/rules/codex-review-gate.md` and `.claude/rules/file-bridge-protocol.md`.

## Methodology Trail

- Files inspected: `bridge/gtkb-wi5020-retire-event-source-config-001.md`,
  `config/dispatcher/rules.toml`, `config/agent-control/declarative-agent-role-manifest.yaml`,
  `harness-state/harness-registry.json`,
  `groundtruth-kb/src/groundtruth_kb/agent_role_manifest.py`,
  `groundtruth-kb/src/groundtruth_kb/harness_ops.py`,
  `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py`,
  `groundtruth-kb/src/groundtruth_kb/cli.py`,
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py`,
  `scripts/dispatcher_runtime.py`.
- Commands run: repository-wide greps for
  `can_fire_events` / `event_driven_hooks` / `event-source` / `_record_can_fire_events`;
  `bridge_applicability_preflight.py --bridge-id gtkb-wi5020-retire-event-source-config`
  (pass); `adr_dcl_clause_preflight.py --bridge-id gtkb-wi5020-retire-event-source-config`
  (exit 0).
- Not run (approval-gated in this dispatched worker): `gt bridge dispatch health`
  and `gt harness roles`. Registry/rules file reads were used in their place; the
  live health WARN for B is file-consistent but was not executed here (see F5).

## Owner Decisions / Input

None required to act on this NO-GO. Prime Builder revises and resubmits as REVISED
per the Path to GO. Scope expansion in the REVISED proposal remains inside the
existing PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION / WI-5020 authorization; no new
owner decision is implicated by the additional target paths.
