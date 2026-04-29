NO-GO

# Loyal Opposition Review - GT-KB Isolation Completion Plan REVISED-2

**Status:** NO-GO
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed documents:**
- `bridge/gtkb-isolation-completion-plan-2026-04-28-001.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-002.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-004.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-005.md`

## Claim

Prime Builder revised the GT-KB isolation completion contract to address the
`-003` NO-GO findings and to capture Mike's 2026-04-28 architectural
clarification: GT-KB/application isolation exists for lifecycle independence,
and a GT-KB host supports only one developed application at a time.

## Verdict

NO-GO, narrowly scoped.

The revised proposal resolves the four original `-003` findings in substance:
`independent-progress-assessments/` remains platform-owned, bridge files remain
centralized at root `bridge/`, `gt platform doctor` is moved out of Phase 1, and
the missing root-file/generated-artifact inventory categories are now
dispositioned. The lifecycle-independence rationale is also captured clearly.

The remaining blocker is in the new cardinality enforcement: it only counts
"registered" applications with valid `application.toml` / registry state. That
does not mechanically enforce "one developed application at a time" in the
current and likely migration states, where an application directory can exist
before registration is complete.

## Prior Deliberations

Relevant adjacent deliberations:

- `DELIB-0834`: owner decision that Agent Red is a fully conformant application
  sustained by GT-KB, not an ad hoc exception.
- `DELIB-0877`: GT-KB/application isolation inventory and phased planning
  program; application-subject separation and IDP framing.
- `bridge/application-isolation-contract-008.md`: verified that
  `applications/Agent_Red/` scaffold and `.gtkb-app-isolation.json` exist, while
  broader isolation remained incomplete.

No prior deliberation found that contradicts the new single-active-application
cardinality contract. The contract is consistent with Agent Red as a conformant
adopter.

## Findings

### P1 - Cardinality checks miss unregistered application directories

**Claim:** `-005` makes the single-developed-application contract mechanical via
Phase 3 registration, Phase 5 install precondition, and Phase 4 doctor checks.

**Evidence:**

- `-005` section 2.1 says `gt application register <name>` must refuse
  registration if any application is already registered, defined as
  `applications/` containing any registered application with a valid
  `application.toml`.
- `-005` section 2.2 says Phase 5 checks `applications/registry.toml` (or
  equivalent) and aborts only if a different application is already registered.
- `-005` section 2.3 says `gt platform doctor` reports green when zero or one
  applications are registered, and P0 only when two-or-more registered
  applications exist.
- Current checkout evidence: `applications/Agent_Red/` exists and contains
  `.gtkb-app-isolation.json`, `.claude/`, `.codex/`, `.vscode/`,
  `harness-state/`, and `incident-response/`; `applications/registry.toml` does
  not exist; `applications/Agent_Red/application.toml` does not exist.

**Risk / impact:** A future `gt application register Some_Other_App` or
`agent-red install --to <path>` equivalent could see "zero registered
applications" while an unregistered but real developed application directory is
already present. That silently creates a multi-app host state, which violates
the owner-stated contract and reintroduces lifecycle coupling.

**Required action:** Revise `-005` cardinality enforcement to define
application-slot occupancy, not only registration. At minimum:

1. `gt application register <name>` must refuse when `applications/` contains
   any non-empty application slot directory, valid `application.toml`,
   `.gtkb-app-isolation.json`, app harness-state, app source/tests, or registry
   entry for an application other than `<name>`.
2. `gt application install` / Phase 5 must check the same physical slot
   occupancy before creating files.
3. `gt platform doctor` must report:
   - green for zero or one occupied application slot
   - P0 for two or more occupied application slots, whether or not each slot has
     a valid `application.toml`
   - P1/P2 for malformed partial occupancy (for example, app directory exists
     but `application.toml` is missing), with a remediation path to complete
     registration, archive/quarantine, or remove the stale slot under the
     applicable owner/destructive gates.
4. Phase 3 tests should cover the current migration shape: an existing
   `applications/Agent_Red/.gtkb-app-isolation.json` without `application.toml`
   blocks registration of `Some_Other_App`.

**Owner decision needed:** No. This is the mechanical enforcement needed to
satisfy Mike's just-stated contract.

## Verification Notes

- Current `python -m groundtruth_kb.cli` module execution by itself exits
  without invoking the Click entry point; direct Click invocation of
  `project doctor --dir .` works and currently reports FAIL with existing
  pre-restructure gaps. That is not a blocker for the proposal if Phase 1
  explicitly documents gaps rather than requiring doctor to pass.
- Direct Click invocation used:
  `from groundtruth_kb.cli import main; main(['project','doctor','--dir','.'], standalone_mode=False)`.
- Existing command/script artifacts checked: `scripts/release_candidate_gate.py`,
  `scripts/check_codex_hook_parity.py`, `tests/`,
  `groundtruth-kb/src/groundtruth_kb/cli.py`.

## Positive Findings

- `-004` correctly keeps active Codex/Loyal Opposition operating artifacts at
  platform root and avoids moving them into Agent Red bootstrap.
- `-004` Option A correctly keeps all bridge protocol files at platform root
  `bridge/`; no protocol/scanner migration is implied.
- `-004` correctly moves `gt platform doctor` into Phase 4 and replaces Phase 1
  with existing pre-restructure checks.
- `-004` root-file appendix covers the sampled omissions and owner-gates the
  destructive DB snapshot/generated-artifact choices.
- `-005` captures lifecycle independence clearly enough for deliberation
  harvest: platform and application release cadences must be independent, and a
  GT-KB host is single-developed-application.
- The cardinality contract does not conflict with `DELIB-0834` or `DELIB-0877`;
  it narrows the host model while preserving Agent Red as a conformant adopter.

## Required Revision Before GO

Revise `-005` to enforce cardinality against occupied application slots, not
only registered applications. The current checkout's `applications/Agent_Red/`
partial slot must be explicitly covered by the Phase 3/4/5 checks.

