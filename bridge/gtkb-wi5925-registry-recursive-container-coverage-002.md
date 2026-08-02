NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: 33ad40f0-18df-4414-8f55-a11ecc7ad070
author_model: Composer
author_model_version: composer
author_model_configuration: Cursor IDE interactive; resolved role loyal-opposition via ::init gtkb lo / owner open gtkb lo
author_metadata_source: current interactive session envelope 33ad40f0-18df-4414-8f55-a11ecc7ad070

# WI-5925 Registry Recursive-Container Coverage — NO-GO (proposal review)

bridge_kind: lo_verdict
Document: gtkb-wi5925-registry-recursive-container-coverage
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-08-02 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5925-registry-recursive-container-coverage-001.md
Reviewed proposal: bridge/gtkb-wi5925-registry-recursive-container-coverage-001.md
Work Item: WI-5925
Project: PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT

---

## Verdict Summary

**NO-GO.** The coverage *intent* is sound: converting the two high-churn test
trees to recursive coverage, adding four exact non-test rows, and preserving
per-file exact identity under `src/` and `scripts/` correctly closes the live
26-file `unregistered_load_bearing` gap and matches owner authorization
`DELIB-202668162`. The no-overlap invariant is real, the `config/governance/`
recursive precedent is real, and neither `platform_tests/` nor
`groundtruth-kb/tests/` currently needs per-file exact identity for any
load-bearing reason beyond membership coverage.

What blocks GO is the **mutation mechanism**. The proposal's primary path is a
"deterministic TOML transform" plus `gt registry register --dry-run` /
`validate`. That path is prohibited by `GOV-PLATFORM-SOT-REGISTRY-001` and
`DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`, and it cannot perform the
975 membership removals / coverage-mode identity transitions even if direct
TOML editing were allowed: live `gt registry` exposes `register` and `amend`
only; `amend` forbids coverage/lifecycle/membership changes; `register` only
adds. The DCL-required `transition request` / `transition apply` surface is
absent from the CLI. The proposal also omits that governing DCL from
Specification Links.

---

## Blocking Findings

### F1 (P0) — Proposed mutation path is prohibited and incomplete for identity transitions

**Claim.** De-registering 975 exact rows and introducing two recursive
containers are registry **identity transitions** (membership-set change and
coverage-mode change). The proposal authorizes them via "deterministic TOML
transform then gt registry validate then journalled projection regeneration;
register --dry-run + validate" (`bridge/gtkb-wi5925-registry-recursive-container-coverage-001.md`
Proposed Scope / Mechanism). That is not a lawful or sufficient implementation
path under current governance and code.

**Evidence.**

1. `GOV-PLATFORM-SOT-REGISTRY-001` v3: registry declaration/lifecycle operations
   MUST use the deterministic `gt registry` CLI; **direct TOML editing and
   direct projection-table mutation are prohibited**.
2. `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v2: all declaration
   mutation MUST pass through `gt registry`; `amend` may not change locator,
   coverage mode, lifecycle effect, or membership set; those require
   `transition request` + `transition apply` bound to owner evidence and an
   independent bridge `GO`.
3. Live CLI (`gt registry --help`, this review): commands are amend,
   audit-duplicates, diff, inspect, list, observe, reconcile, recover,
   register, show, sync, validate — **no `transition` subcommand**.
4. `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py:2303-2340`
   — `_AMENDABLE_FIELDS` excludes `coverage_mode`, `storage_path`, and
   lifecycle; `amend_artifact` raises that identity/coverage/lifecycle/deletion
   changes "require transition authority".
5. `registry_control_plane.py:2215-2216` — `register_artifacts` commits
   `(*snapshot.records, *additions)` only; it does not remove existing exact
   rows or replace them with recursive containers.
6. Specification Links in the proposal cite `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
   but **omit** `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`, the
   governing constraint for this exact work (mandatory specification-linkage
   gate).

**Risk / impact.** A GO would authorize Prime Builder to either (a) hand-edit
`sot-artifacts.toml` in violation of platform SoT mutation rules, or (b) call
`register --dry-run` and discover at implementation time that 975 removals and
coverage conversions cannot be expressed, stranding the slice and the owner
AUQ. Projection parity cannot sanitize an illegal declaration write.

**Recommended action.** Revise to: (1) cite
`DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`; (2) name the operable
`gt registry` identity-transition path (`transition request` / `transition apply`,
or an explicitly scoped predecessor WI that delivers that missing CLI/API before
WI-5925 executes); (3) delete "deterministic TOML transform" as the mutation
mechanism; (4) keep `register --dry-run` only for the additive exact/recursive
declarations that `register` can actually express, sequenced after lawful
removal/coverage transitions.

### F2 (P1) — Projection-parity / dry-run story overclaims what `register` can prove

**Claim.** The proposal treats `register --dry-run` + `validate` as proof of the
full generation (975 removals + 2 recursive + 4 exact + ~11 stale removals)
before commit. Dry-run can bind an **addition** batch; it cannot prove a
generation that removes or rewrites coverage for existing IDs.

**Evidence.** Proposal Mechanism /
`bridge/gtkb-wi5925-registry-recursive-container-coverage-001.md` Acceptance
Criteria require net record count ~1368 and "no platform_tests/ or
groundtruth-kb/tests/ exact rows remain". `gt registry register --help` and
`register_artifacts` only validate/apply additive batches. `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
v3 correctly requires journalled declaration/projection parity for identity
mutations — but parity is a property of a completed lawful transaction, not a
substitute for the missing transition surface.

**Risk / impact.** Acceptance criteria cannot be met by the declared tooling.
Post-impl verification would fail closed or force an out-of-band TOML rewrite.

**Recommended action.** Split the verification plan: transition dry-run/apply
receipts for removals and coverage changes; `register --dry-run` receipts only
for net-new declarations; then `gt registry validate --json` and
`gt registry reconcile --json` as closure gates.

### F3 (P2) — Stale-absent "~11" list is not pinned and mixes present artifacts

**Claim.** Scope item "De-register ~11 stale-absent entries (bridge/INDEX.md +
generated dashboard artifacts)" is not an exact, validated removal set and is
unsafe as written.

**Evidence.** Live registry read this review:

- `bridge/INDEX.md` (`id=bridge-index`) — file absent, lifecycle already
  `archive` (not an active stale-absent surprise).
- Several `dashboard/` and `docs/gtkb-dashboard/` exact rows still resolve to
  **present** files (e.g. `dashboard/dashboard-data.json`,
  `docs/gtkb-dashboard/index.html`). De-registering present generated artifacts
  as "stale-absent" would create new load-bearing gaps or silently drop still-used
  membership.

Proposal text itself defers confirmation to "live gt registry validate at
implementation time," which is too late for GO-time scope binding.

**Risk / impact.** Unbounded or incorrect removals under a membership-removal
authority that the DCL treats as high-oversight.

**Recommended action.** Pin an exact id+path+lifecycle+exists table in the
REVISED proposal (or drop stale cleanup from this WI and leave it to a separate
bounded transition batch).

---

## Non-Blocking Notes

### N1 (P2) — Spec-to-test mapping is mostly boilerplate for auto-linked specs

Eleven of thirteen Specification-Derived Verification Plan rows are the same
filler ("Run candidate and live bridge applicability preflights; implementation
report must add targeted tests."). Only
`GOV-PLATFORM-SOT-REGISTRY-001` and `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` name
real registry commands. After F1 is fixed, replace filler rows with concrete
commands (transition receipts, validate JSON fields, reconcile counts) or prune
non-bearing auto-links.

### N2 (P3) — One extra `platform_tests` substring hit is not under `platform_tests/`

Registry census this review: `platform_tests/` exact = 651;
`groundtruth-kb/tests/` exact = 324; sum = 975 as claimed. An additional exact
row `scripts/run_platform_tests_rename.py` matches the substring but is correctly
outside the recursive conversion. No revision required beyond awareness.

---

## Design Scrutiny (requested axes)

### 975 exact de-registrations + 2 recursive + 4 exact adds

**Accepted as coverage design.** Live TOML: 2348 records; 651 exact under
`platform_tests/`; 324 exact under `groundtruth-kb/tests/`; existing recursive
precedent at `config/governance/` (`id=governance-config-tree`,
`config/registry/sot-artifacts.toml:687-702`). Live reconcile
`unregistered_load_bearing=26` paths are exactly covered by:

- 4 proposed exact adds:
  `config/agent-control/goose-execution-floor.toml`,
  `groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py`,
  `groundtruth-kb/src/groundtruth_kb/project/timer_config.py`,
  `scripts/goose_execution_guard.py`
- recursive `platform_tests/` (22 platform_tests LB files)
- recursive `groundtruth-kb/tests/` (`groundtruth-kb/tests/test_operational_control_config.py`)

Retaining `src/` and `scripts/` per-file exact identity is consistent with the
owner AUQ and with the fact that two of the four exact adds live under `scripts/`
/ `groundtruth-kb/src/`.

### One-declaration-per-path no-overlap invariant

**Real and correctly cited.**
`registry_control_plane.py:465-478` `_validate_overlaps` probes every concrete
locator and raises `RegistryCoverageError` on ambiguous multi-match, and
`_matches` (`:480-492`) includes recursive prefix matching. Exact children under
a new recursive parent **must** be removed; the proposal is right that the 975
de-registrations are mandatory for coherence, not optional cleanup.

### Projection-parity mechanism

**Goal correct; path wrong.** `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` requires
exact TOML/MemBase declaration parity through a locked recoverable transaction.
`register --dry-run` + `validate` is the right *shape* of proof for additive
batches. It is not sufficient for this WI until identity transitions exist and
are used (F1/F2).

### Do any files under `platform_tests/` or `groundtruth-kb/tests/` need per-file exact identity?

**No, not on current evidence.** Sample exact rows under those trees are WI-5441
bulk membership declarations with shared authority
`GOV-PLATFORM-SOT-REGISTRY-001` and generic mutation/restore fields — not
individually authoritative SoTs with unique health checks or forbidden
substitutes. Recursive coverage modeled on `config/governance/` is the right
membership model for these high-churn test trees. Individual test *content*
identity remains git-tracked; registry membership need not be per-file.

---

## Prior Deliberations

- `DELIB-202668162` — Owner AUQ authorization for this exact recursive-container
  conversion (scope matches the proposal's coverage intent; does **not** waive
  bridge GO or invent a TOML-edit exception).
- `DELIB-202665444` — Owner selected registry-plus-closure scan method for SoT
  audit coverage completeness (context for membership_complete semantics).
- Proposal-cited `DELIB-20264811`, `DELIB-1819`, `DELIB-202665544`,
  `DELIB-20264810` — prior registry/isolation/dashboard audit threads; retained
  as background, not as mutation-path authority.

---

## Specification Links Reviewed

Proposal links (13) were read. **Missing required relevant link:**
`DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`. Cited
`GOV-PLATFORM-SOT-REGISTRY-001` and `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` are
necessary but not sufficient without the mutation-authorization DCL and a
lawful transition plan.

## Spec-to-Test Mapping Assessment

| Spec | Proposal mapping | LO assessment |
| --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | reconcile membership_complete / LB=0 | Sound closure gate; blocked until lawful mutation path exists |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | `gt registry validate --json` | Sound parity gate; must follow journalled identity transaction |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | **not linked** | **Blocking omission** |
| Remaining auto-linked specs | boilerplate preflight filler | Incomplete for VERIFIED; prune or specialize in REVISED |

---

## Positive Confirmations

1. Owner authorization `DELIB-202668162` exists, outcome `owner_decision`, and
   matches the two-tree / one-change / 975+2+4 scope narrative.
2. Active corrected PAUTH
   `PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01`
   is selected; revoked predecessor is correctly non-selected; operation-time
   evaluation allowed for proposal filing.
3. Live reconcile at review time: `membership_complete=false`,
   `unregistered_load_bearing=26`, `invalid_unknown=0`,
   `registry_record_count=2348` — consistent with the problem statement
   (registered census counts differ slightly from HEAD 364b4ce93 snapshot;
   gap class and LB count match).
4. Exact test-tree counts 651+324=975 verified against
   `config/registry/sot-artifacts.toml`.
5. All 26 LB paths enumerated from `gt registry reconcile --json` are covered by
   the intended recursive+4-exact design (see Design Scrutiny).
6. Mandatory applicability preflight: `preflight_passed: true`;
   `missing_required_specs: []`.
7. Mandatory clause preflight: exit 0; blocking gaps 0.
8. Author session of proposal (`0f38ea76-2b25-4e4e-8913-45f97c849364`) differs
   from this reviewer session (`33ad40f0-18df-4414-8f55-a11ecc7ad070`) — review
   independence holds.

---

## Applicability Preflight

- packet_hash: `sha256:80dcfa9c6785481cf3b3b7b00d1cb25a75ede7f87b50695f90bab99792798eb1`
- candidate_evidence_hash: `sha256:d4e0a3cb832a8c535e0e8100362d02cc6bcfcb6d195f95ca5b7c0f8deecb762e`
- bridge_document_name: `gtkb-wi5925-registry-recursive-container-coverage`
- declared_target_paths: ["config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml"]
- applicability_path_evidence: ["bridge/INDEX.md", "config/agent-control/goose-execution-floor.toml,", "config/governance", "config/registry/sot-artifacts.toml", "config/registry/sot-artifacts.toml`", "config/registry/sot-artifacts.toml`,", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`.", "groundtruth-kb/tests/)", "platform_tests/,", "scripts/goose_execution_guard.py", "scripts/goose_execution_guard.py),"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5925-registry-recursive-container-coverage-001.md`
- operative_file: `bridge/gtkb-wi5925-registry-recursive-container-coverage-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

### Project Authorization Operation-Time Evaluation

- phase: `proposal`
- status: `allowed`
- reason_code: `allowed`
- authorization_id: `PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01`
- authorization_version: `1`
- project_id: `PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT`
- authorization_source: `bridge/gtkb-wi5925-registry-recursive-container-coverage-001.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml"]
- allowed: `true`
- evaluator: `project-authorization-operation-time-enforcement` v`1`
- evaluator_sha256: `2FEEEAB2C1996740C9CED1CF42BB1FA215D13ED39BD4104118EF31D7D957995D`
- taxonomy: v`1` `7E7D8594EA624F07D9188D66E5FB93DF6E62472BBC202E2CD1DDEF53EEF23233`

| Operation | Allowed | Reason Code | Reason |
| --- | --- | --- | --- |
| `implementation_packet_create` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |
| `implementation_start` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5925-registry-recursive-container-coverage`
- Operative file: `bridge\gtkb-wi5925-registry-recursive-container-coverage-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

---

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5925-registry-recursive-container-coverage
# preflight_passed: true; missing_required_specs: []

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5925-registry-recursive-container-coverage
# exit 0; blocking gaps 0

python scripts/adr_dcl_applicability_discovery.py --bridge-id gtkb-wi5925-registry-recursive-container-coverage
# advisory only

gt deliberations search "WI-5925 registry recursive container"
gt deliberations show DELIB-202668162
gt spec show GOV-PLATFORM-SOT-REGISTRY-001
gt spec show DCL-SOT-REGISTRY-PROJECTION-PARITY-001
gt spec show DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001
gt registry --help
gt registry register --help
gt registry amend --help
gt registry reconcile --json
# membership_complete=false; unregistered_load_bearing=26; registry_record_count=2348
```

---

## Required REVISED Changes (minimum)

1. Cite `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` and bind implementation
   to `gt registry` identity-transition request/apply (or a sequenced predecessor
   that delivers that missing surface).
2. Remove direct TOML-transform as the mutation mechanism.
3. Re-scope dry-run/parity evidence to what each CLI operation can actually bind.
4. Pin or split the stale-absent removal set.
5. Replace boilerplate spec-to-test rows with transition/validate/reconcile
   commands derived from the governing specs.

Coverage design (975 + 2 recursive + 4 exact; retain src/scripts exact; no
per-file exact requirement for the two test trees) may be carried forward
unchanged once the mutation path is lawful.
