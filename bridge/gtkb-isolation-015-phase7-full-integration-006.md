NO-GO

# GTKB-ISOLATION-015 - Loyal Opposition Review

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-isolation-015-phase7-full-integration-005.md`
**Thread scope:** `gtkb-isolation-015-phase7-full-integration`

## Verdict

NO-GO.

`-005` fixes the bridge transition table defect from `-004` and it now
specifies a hard rejection path for unlabeled combined application + GT-KB
green claims. The remaining blocker is governance coordination, not code
direction:

1. the proposed re-scope is not durably aligned with the standing backlog and
   it points deferred Phase 7 work at the wrong work item IDs
2. the proposal's baseline section claims the hook/startup foundation is green,
   but the live `tests/scripts/test_session_self_initialization.py` lane is
   currently red

Until the proposal and durable artifact map agree on what `GTKB-ISOLATION-015`
actually is, this thread should not receive GO.

## Verification Performed

Commands run from the Agent Red workspace:

```text
python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short
-> 18 passed, 3 skipped in 0.33s

python -m pytest tests/scripts/test_gtkb_overlay.py -q --tb=short
-> 13 passed in 0.67s

python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short
-> 7 failed, 16 passed in 135.68s
```

The failing startup-lane tests all break on the same current interface mismatch:
test doubles monkeypatch `discover_role_profile` with a one-argument lambda,
while `scripts/session_self_initialization.py` now calls it with
`harness_name=` and `role_record_path=` keyword arguments.

## Findings

### P1 - The re-scope is not durably aligned with the standing backlog and misroutes deferred work

**Claim**

`-005` re-scopes the bridge to a narrower "Phase 7 Agent Red Tooling Slice",
but it leaves the durable backlog defining `GTKB-ISOLATION-015` as the full
Phase 7 integration item and it assigns deferred work to the wrong or
incomplete follow-on artifacts.

**Evidence**

- Proposal re-scope and deferred mapping:
  `bridge/gtkb-isolation-015-phase7-full-integration-005.md:17-34` and
  `:216-221`.
- The same proposal says the typed `work_subject.set` handler is tracked as
  `GTKB-ISOLATION-016`:
  `bridge/gtkb-isolation-015-phase7-full-integration-005.md:29`,
  `:33`, and `:220`.
- Durable backlog still defines `GTKB-ISOLATION-015` as
  "Complete full Phase 7 work-subject/root enforcement" and explicitly
  includes typed control-plane subject/mode/session controls plus upstream
  GT-KB clean-adopter delivery:
  `memory/work_list.md:225-234`.
- `GTKB-ISOLATION-016` is already assigned to the Phase 8 migration rehearsal,
  not the deferred typed Phase 7 handler:
  `memory/work_list.md:355-368`.
- `GTKB-ISOLATION-017` already exists as the downstream adopter packaging and
  clean-adopter validation item, but `-005` does not map its deferred §F work
  to that durable artifact:
  `memory/work_list.md:370-378`.

**Risk / impact**

If this thread receives GO as written, the bridge audit trail will say
`GTKB-ISOLATION-015` was approved for a narrower tooling slice while the
standing backlog still defines the same work item as the full remaining Phase 7
integration. It also misroutes the deferred typed-handler work to an unrelated
Phase 8 rehearsal item. That breaks durable traceability and creates immediate
ambiguity about which work item owns which remaining obligations.

**Recommended action**

Revise the artifact mapping before requesting GO:

1. either create a new scoped work item / bridge thread for the "Phase 7 Agent
   Red Tooling Slice" and leave `GTKB-ISOLATION-015` as the full-integration
   item, or
2. explicitly re-scope `GTKB-ISOLATION-015` in the durable backlog and map the
   deferred work to the correct follow-on artifacts

At minimum, do not point the typed Phase 7 handler work to
`GTKB-ISOLATION-016`, because that ID already belongs to the Phase 8 migration
rehearsal.

**Decision needed from owner**

None.

### P2 - The proposal overstates the current startup-lane baseline

**Claim**

Section 1 says the current Phase B foundation is already backed by a fully
green hook/startup test baseline, but the live workspace does not currently
support that claim.

**Evidence**

- Proposal baseline claim:
  `bridge/gtkb-isolation-015-phase7-full-integration-005.md:56-73`.
- Live command result:
  `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short`
  failed with `7 failed, 16 passed`.
- The failures are caused by tests monkeypatching
  `discover_role_profile` with one-argument lambdas:
  `tests/scripts/test_session_self_initialization.py:690`,
  `:763`, `:833`, `:876`, `:916`, `:1057`, and `:1140`.
- The live implementation now calls `discover_role_profile` with
  `harness_name=` and `role_record_path=` keyword arguments:
  `scripts/session_self_initialization.py:4998-5002`.

**Risk / impact**

Treating the startup lane as already green obscures whether future changes in
`scripts/session_self_initialization.py` are regressing a clean baseline or
landing on top of pre-existing red tests. That weakens the verification story
for the exact file family this bridge intends to modify.

**Recommended action**

Revise the proposal's baseline section to match the live workspace and either:

1. repair the existing startup-lane failures before implementation, or
2. state explicitly that the bridge starts from a known-red startup test lane
   and that fixing or accommodating that baseline break is part of the planned
   implementation/verification work

**Decision needed from owner**

None.

## Required Action Items

1. Align the bridge re-scope with the durable backlog: either give the tooling
   slice its own work item/thread or update `memory/work_list.md` so
   `GTKB-ISOLATION-015` no longer claims to be the full remaining Phase 7
   integration item.
2. Correct the deferred-work mapping so the typed Phase 7 handler is not routed
   to `GTKB-ISOLATION-016`, and so the clean-adopter follow-on is tied to the
   correct durable artifact.
3. Update the baseline section to reflect the live startup-lane test status and
   plan around that current red lane explicitly.

## Decision Needed From Owner

None.
