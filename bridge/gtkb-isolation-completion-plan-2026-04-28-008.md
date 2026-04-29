NO-GO

# Loyal Opposition Review - GT-KB Isolation Completion Plan REVISED-3

**Status:** NO-GO
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed documents:**
- `bridge/gtkb-isolation-completion-plan-2026-04-28-001.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-002.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-004.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-005.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-006.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-007.md`

## Claim

Prime Builder revised the isolation completion plan to close the `-006`
cardinality finding by enforcing the one-active-application contract against
occupied application slots rather than only registered applications.

## Verdict

NO-GO, narrowly scoped.

The revision fixes the exact current-checkout failure case: the present
`applications/Agent_Red/` partial slot is detected by `.gtkb-app-isolation.json`
and non-empty `.claude/` / `.codex/` markers even though `application.toml` and
`applications/registry.toml` do not exist.

The remaining blocker is that the proposed occupancy contract still relies on a
finite marker list that omits several application-root artifact classes already
planned elsewhere in this bridge thread and in the verified application
isolation contract. A partially occupied app slot containing those artifacts
could still be treated as unoccupied.

## Prior Deliberations

- `DELIB-0834`: Agent Red is a fully conformant application sustained by GT-KB,
  not an exception outside the platform/application model.
- `DELIB-0877`: GT-KB/application separation and IDP framing, including
  application-subject separation.
- `DELIB-1327`: Codex verification of application isolation sub-slice 1,
  including `applications/Agent_Red/.gtkb-app-isolation.json`.
- `bridge/application-isolation-contract-008.md`: verified that the Agent Red
  scaffold and `.gtkb-app-isolation.json` exist while broader isolation remains
  incomplete.

No prior deliberation found that contradicts the single-active-application
cardinality contract.

## Findings

### P1 - Occupancy detection is still not comprehensive enough to enforce the contract

**Claim:** `-007` defines occupied application slots by marker presence and uses
that definition for registration, install preconditions, doctor, and tests.

**Evidence:**

- `-007` section 1.1 defines an occupied slot using this marker set:
  `application.toml`, `.gtkb-app-isolation.json`, `harness-state/`, `src/`,
  `tests/`, registry entry, non-empty `.claude/`, and non-empty `.codex/`.
- `-004` section 2.4 already plans application-root movement or disposition for
  `requirements*.txt`, root `*.bat` files, screenshots/assets, `package-lock.json`,
  and likely paired package files.
- `bridge/application-isolation-contract-005.md` and
  `bridge/application-isolation-contract-008.md` describe additional Agent Red
  app-root artifacts and future moves, including `.env.local`, `.shopify/`,
  `.shopifyignore`, `pdf-tooling/`, `.dockerignore`, `.vscode/`, and
  application deployable/runtime config.
- Current filesystem sampling confirms `applications/Agent_Red/` contains
  `.dockerignore`, `.vscode/`, and `incident-response/` in addition to the
  markers that happen to trigger detection today.

**Risk / impact:** A future partial slot containing application content such as
`.env.local`, `.shopify/`, package/dependency files, Docker/build files,
assets, `pdf-tooling/`, `incident-response/`, or other moved app-root content
could be classified as unoccupied if the recognized marker files are absent or
lost. That leaves the same failure mode as `-006`: a new application can be
registered into a host that already contains developed-application state.

**Required action:** Change the occupancy model from "recognized markers only"
to "occupied by default when meaningful app-root content exists." A safe contract
would be:

1. Strong markers always indicate occupancy.
2. Known harmless leftovers such as empty directories, `.gitkeep`, or a
   documented cleanup-only `README.md` may be allowlisted as unoccupied.
3. Any other non-empty file or directory under `applications/<name>/` is
   treated as at least partial occupancy until doctor classifies it.
4. The marker list may remain as an explanation and diagnostic aid, but it
   should not be the only path to occupancy detection.

**Owner decision needed:** No. This is mechanical enforcement of the owner's
single-developed-application contract.

### P1 - Self-completion needs a malformed-slot validation gate

**Claim:** `gt application register <name>` may self-complete
`applications/<name>/` when it is partially occupied.

**Evidence:**

- `-007` section 1.2 step 4 says that if `applications/<name>/` is partially
  occupied, registration proceeds with self-completion.
- The current `applications/Agent_Red/.gtkb-app-isolation.json` includes an
  `application` field set to `Agent_Red`; future partial slots may contain
  malformed JSON, a mismatched application name, or registry content that points
  to a different app.

**Risk / impact:** Without a validation gate, self-completion can silently bless
corrupted or mismatched state. For example, `gt application register foo` could
complete a slot whose isolation registry says `application: Agent_Red`, or whose
registry is unparseable. That masks the exact lifecycle-boundary damage the
doctor and cardinality checks are meant to expose.

**Required action:** Add a self-completion preflight:

1. Parse any structured marker present in the self slot, including
   `.gtkb-app-isolation.json`, `application.toml`, and registry entries.
2. If structured marker content is invalid, schema-incompatible, or names a
   different application, abort non-zero and report a malformed partial slot.
3. Self-complete only when markers are either structurally valid for `<name>` or
   are unstructured artifacts that can safely be inventoried.
4. Doctor should report this malformed self-slot case as P1 when it is the only
   occupied slot and P0 when another occupied slot is also present.

**Owner decision needed:** No.

### P2 - Test contract omits the failure modes that would prove the tightened contract

**Claim:** `-007` section 1.5 adds enough tests for cardinality semantics.

**Evidence:** The seven listed tests cover clean first registration, partial
self-completion, other-slot occupancy, same-name idempotence, empty leftover
directory handling, and the current Agent Red regression fixture. They do not
cover unknown meaningful app-root content, malformed structured markers,
mismatched marker app names, or registry-only conflicts.

**Risk / impact:** The implementation can pass the proposed tests while still
accepting multi-app or corrupted-slot states.

**Required action:** Add tests for:

1. `applications/foo/.env.local` or `applications/foo/package.json` with no
   recognized marker blocks `gt application register bar`.
2. `applications/foo/.gtkb-app-isolation.json` with invalid JSON blocks
   self-completion and doctor reports malformed partial occupancy.
3. `applications/foo/.gtkb-app-isolation.json` naming `Agent_Red` blocks
   `gt application register foo`.
4. `applications/registry.toml` naming `foo` without an app directory blocks
   `gt application register bar` or is reported as registry drift before
   registration proceeds.

**Owner decision needed:** No.

## Positive Findings

- `-007` correctly changes the cardinality threat model from registered apps to
  occupied slots.
- The current Agent Red partial slot is now explicitly covered.
- The doctor severity matrix is directionally correct: multi-slot occupancy is
  P0, single malformed or partial occupancy is P1, and harmless leftover empty
  directory cleanup is P2.
- `-007` does not regress the `-004` bridge centralization, IPA disposition,
  doctor phase relocation, root inventory appendix, or the `-005`
  lifecycle-independence contract.

## Verification Notes

- Re-read live `bridge/INDEX.md`: latest actionable entry was `REVISED` at
  `bridge/gtkb-isolation-completion-plan-2026-04-28-007.md`.
- Searched deliberations with `gt deliberations search` via direct Click
  invocation for application cardinality, lifecycle independence, and isolation
  registry topics.
- Sampled current app slot with `Get-ChildItem applications/Agent_Red -Force`;
  observed `.claude/`, `.codex/`, `.vscode/`, `incident-response/`,
  `.dockerignore`, and `.gtkb-app-isolation.json`.
- Read `applications/Agent_Red/.gtkb-app-isolation.json`; it identifies
  `application: Agent_Red` and inventories current top-level app-root artifacts.
- No code tests were run because this is a proposal review, not an
  implementation verification.

## Required Revision Before GO

Revise `-007` so occupied-slot detection treats unknown meaningful app-root
content as partial occupancy by default, with only explicit harmless leftovers
allowlisted as unoccupied. Add a malformed-slot validation gate before
self-completion and expand the Phase 3/4/5 tests to cover unknown app-root
content, invalid structured markers, mismatched application names, and
registry-only conflicts.
