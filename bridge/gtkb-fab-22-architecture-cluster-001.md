NEW

bridge_kind: prime_proposal
Document: gtkb-fab-22-architecture-cluster
Version: 001
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-10

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4434
Project Authorization: PAUTH-FAB22-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: e45ccf07-99f6-4ad6-b572-570a76a264a2
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["groundtruth.db", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/project/scaffold.py", "groundtruth-kb/src/groundtruth_kb/project/checks/**", "groundtruth-kb/pyproject.toml", "groundtruth-kb/templates/**", "scripts/**", "config/governance/adr-dcl-clauses.toml", ".claude/rules/file-bridge-protocol.md", ".github/workflows/**", "platform_tests/**"]

KB mutation: YES. HYG-010's disposition creates an ADR (registry-based check/command discovery) — a formal artifact written to `groundtruth.db` under a formal-artifact-approval packet. `groundtruth.db` is therefore included in target_paths. No other finding writes MemBase (HYG-052 adds no assertions in this cluster — interim WARN only).

---

# FAB-22 — Architecture Decisions Cluster (Owner-Heavy)

WI-4434 (FAB-22) of PROJECT-FABLE-INVESTIGATION. The owner-heavy architecture cluster. Findings: HYG-009
(protocol overhead per landed change), HYG-010 (god-modules), HYG-011 (no canonical interpreter), HYG-023
(template-vs-live drift direction), HYG-052 (ADR/DCL machine-enforcement coverage). Source advisory:
`bridge/gtkb-fable-investigation-advisory-001.md`. All five dispositions were collected at grill-me depth.

Common theme: GT-KB's own engineering substrate — the bridge protocol cost, the three god-modules, the
ambiguous interpreter environment, the stale scaffolding templates, and the thin ADR/DCL enforcement surface
— carries recurring structural cost that the platform should engineer down rather than absorb.

## Summary

- **HYG-009 (protocol overhead):** mean 7.2 bridge versions per landed change; 6,014 bridge `.md` files
  (63.8MB); INDEX.md 1,902 lines vs the protocol's own ~200-line threshold (206/237 entries terminal +
  prune-eligible). **Owner: mechanical auto-trim now + a versions-per-landed-change KPI; lightweight-lane
  protocol amendment deferred to grill-me.**
- **HYG-010 (god-modules):** db.py (5,956) / cli.py (5,386) / doctor.py (3,910) lines dominate; db.py carries
  blanket ruff exemptions. **Owner: an ADR for registry-based check/command discovery + on-touch
  decomposition starting doctor.py; db.py last/never.**
- **HYG-011 (interpreter contexts):** three Python contexts, no declared winner; `gt`/`ruff` on no PATH;
  doctor `_check_ruff` false-WARNs; CI 3.12/3.13 vs local 3.14; empty root `.venv` stub. **Owner:
  groundtruth-kb/.venv canonical.**
- **HYG-023 (template drift):** templates are the stale side in every sampled pair (assertion-check 10x);
  scaffold.py ships a self-described-DEPRECATED poller prompt; file-bridge-protocol.md:273 makes a false
  byte-for-byte claim. **Owner: live-is-canonical + release-tag regen + doctor hash-parity + replace the
  deprecated prompt.**
- **HYG-052 (ADR/DCL coverage):** clause registry covers 5/97 artifacts; 35/69 DCLs + 19/28 ADRs
  assertion-less. **Owner: feed the census to the in-flight clause auto-discovery + interim doctor WARN.**

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol + INDEX-is-canonical; the auto-trim is protocol-sanctioned
  and the HYG-023 file-bridge-protocol.md correction restores an accurate authority claim (HYG-009/023).
- `GOV-20` (Architecture Decision Workflow: ADR/DCL) — the god-module decomposition lands as an ADR; the
  ADR/DCL coverage census feeds the clause-enforcement program (HYG-010/052).
- `GOV-06` (specify-on-contact) — on-touch god-module extraction brings each touched seam under control
  (HYG-010).
- `GOV-17` (Quality first; automation-script modification approval) — the regen script, doctor checks, and KPI
  benchmark ride the governed quality/automation path (HYG-009/011/023).
- `GOV-08` (Knowledge Database is the single source of truth) — the ADR is written to canonical MemBase; the
  doctor checks report against canonical state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all FAB-22 changes are in-root; see Isolation Placement
  Compliance below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle for the ADR, KPI, regen, and doctor
  changes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `NEW` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-009/010/011/023/052; FAB-22 is
  the Wave-3 architecture cluster).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions (Q4 = grill-me depth for high-complexity
  findings; all five FAB-22 findings qualify).
- `DELIB-FAB22-REMEDIATION-20260610` — this cluster's 5 owner AUQ decisions (below).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — recurring structural cost is a defect to engineer out (the
  KPI, regen script, and doctor checks operationalize it).
- _HYG-052 couples to the in-flight `gtkb-adr-dcl-clause-auto-discovery` bridge thread (the 3354/3498 items);
  this cluster feeds it the quantified census as acceptance criteria rather than duplicating its work._

## Owner Decisions / Input

Collected via `AskUserQuestion` at grill-me depth on 2026-06-10, persisted to
`DELIB-FAB22-REMEDIATION-20260610`:

1. **HYG-009 = Mechanical trim now + KPI.** Implement the protocol-sanctioned auto-trim of terminal
   (VERIFIED/WITHDRAWN) INDEX entries (the 3364 item; no protocol-text change) and add a
   versions-per-landed-change KPI to the benchmark suite. The lightweight report+verdict lane is DEFERRED to
   a later grill-me and is NOT authorized here.
2. **HYG-010 = ADR + on-touch, doctor.py first.** Create an ADR proposing registry-based check/command
   discovery, then on-touch extraction (GOV-06) starting with doctor.py; db.py last or never. No big-bang
   rewrite.
3. **HYG-011 = groundtruth-kb/.venv canonical.** Put its Scripts on the session PATH, delete the empty root
   `.venv` stub, align `doctor._check_ruff` to venv-first resolution, refresh the editable install (also
   fixes the 0.6.1-vs-0.7.0rc1 dist-info split), add py3.14 to the CI matrix/classifiers.
4. **HYG-023 = live-is-canonical + regen.** Declare live hooks canonical; add a deterministic regen script +
   a doctor check asserting template/live hash parity at release tags; replace the DEPRECATED poller prompt
   in scaffold.py's copy-list with a current setup doc; fix the false byte-for-byte claim at
   file-bridge-protocol.md:273.
5. **HYG-052 = wait for auto-discovery + interim WARN.** Feed the census (5/97 registry coverage, 35
   assertion-less DCLs, 19 assertion-less ADRs) as acceptance criteria to the in-flight clause
   auto-discovery project, and add a cheap doctor WARN on assertion-less DCLs. No mass backfill here.

## Requirement Sufficiency

**Existing requirements sufficient.** The five dispositions are fixed by `DELIB-FAB22-REMEDIATION-20260610`;
the governing specifications (`GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-20`, `GOV-06`, `GOV-17`, `GOV-08`) already
constrain the bridge-protocol, ADR/DCL-workflow, specify-on-contact, quality/automation, and SoT surfaces.
The HYG-010 ADR is itself a new architecture-decision artifact created through the governed approval path —
that is the requirement-capture mechanism GOV-20 prescribes, not a gap in this proposal. No additional
requirement is needed before implementation.

## Backlog Visibility

`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`: FAB-22 performs **no bulk backlog operation** — it
writes one ADR via the formal-artifact-approval packet path and otherwise edits source/config/templates. The
HYG-052 census is fed to the clause-enforcement project as acceptance criteria (a review packet), not a bulk
mutation; no bulk MemBase or backlog write is authorized by this proposal.

## Scope and Boundaries

In scope: the mechanical INDEX auto-trim + versions-per-change KPI; the registry-based-discovery ADR + an
initial on-touch doctor.py seam; the groundtruth-kb/.venv canonicalization (stub deletion, `_check_ruff`
alignment, editable-install refresh, CI py3.14); the live-is-canonical template regen script + doctor
hash-parity check + DEPRECATED-prompt replacement + the file-bridge-protocol.md:273 correction; the ADR/DCL
census-to-acceptance-criteria + interim doctor WARN. Out of scope and explicitly excluded: the lightweight
report+verdict protocol amendment (HYG-009, deferred to grill-me); any big-bang god-module rewrite (HYG-010
is on-touch, doctor.py only, db.py untouched); mass DCL assertion backfill (HYG-052 is interim WARN only); the
broader clause auto-discovery implementation (that is its own in-flight thread); deploy/push. This proposal
absorbs the advisory's FAB-22 overlap (the 3354/3498 items) by describing them here.

## Proposed Implementation

**Area 1 — HYG-009 protocol overhead (mechanical).** Add a deterministic INDEX auto-trim that archives
terminal (VERIFIED/WITHDRAWN) entries below the protocol's `~200-line` threshold (entries + their bridge files
stay on disk for the audit trail) and re-baselines the trigger parse cost; add a versions-per-landed-change
KPI to the benchmark suite (`scripts/benchmarks/`). No file-bridge-protocol.md text change for the trim (it is
already protocol-sanctioned under §Index Maintenance).

**Area 2 — HYG-010 god-module decomposition (ADR + on-touch).** Author and approve an ADR (MemBase, formal
packet) proposing registry-based check/command discovery (doctor checks as registry-discovered modules; cli
command groups as click sub-modules). Land the first on-touch seam in doctor.py (extract one check family into
a `project/checks/` module behind a stable registry) as the worked example; db.py is explicitly untouched.

**Area 3 — HYG-011 canonical interpreter.** Delete the empty root `.venv` stub; align `doctor._check_ruff`
(doctor.py:268-273) to the venv-first, fail-closed resolution `scripts/check_ruff_format.py` already uses
(removing the recurring false WARN); refresh the editable install in groundtruth-kb/.venv (resolving the
0.6.1-vs-0.7.0rc1 dist-info split); add py3.14 to the CI matrix and the pyproject classifiers; document `gt`
invocation (venv Scripts on PATH or the canonical `python -m` form).

**Area 4 — HYG-023 live-is-canonical templates.** Declare live hooks canonical for the GT-KB checkout; add a
deterministic regen script that produces `groundtruth-kb/templates/hooks/` from the live `.claude/hooks/`, plus
a doctor check asserting template/live hash parity at release tags; replace the DEPRECATED
`bridge-os-poller-setup-prompt.md` in scaffold.py's copy-list with a current cross-harness-trigger /
single-harness-dispatcher setup doc; correct the false byte-for-byte activation claim at
file-bridge-protocol.md:273 (protected-narrative packet).

**Area 5 — HYG-052 ADR/DCL coverage.** Record the quantified census (5/97 clause-registry coverage; 35/69
assertion-less DCLs; 19/28 assertion-less ADRs) as acceptance criteria on the in-flight clause auto-discovery
project; add a cheap doctor WARN listing assertion-less DCLs so the gap stays visible without blocking. No
assertions are added to DCLs in this cluster.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all FAB-22 changes are in-root under `E:\GT-KB\` — the doctor/cli/db
source and the new `project/checks/` modules under `groundtruth-kb/src/groundtruth_kb/`, the templates under
`groundtruth-kb/templates/`, the regen/KPI/auto-trim scripts under `scripts/`, the clause registry at
`config/governance/adr-dcl-clauses.toml`, the protocol rule at `.claude/rules/file-bridge-protocol.md`, the CI
under `.github/workflows/`, the ADR row in the in-root `groundtruth.db`, tests under `platform_tests/`, and
this bridge file under `E:\GT-KB\bridge\`. The cluster relocates no application file, touches no
`applications/` subtree, and writes no out-of-root artifact; HYG-011 in fact DELETES an empty in-root `.venv`
stub and consolidates the interpreter story to in-root surfaces.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (HYG-009 trim is non-destructive; HYG-023 protocol claim is accurate) | test: auto-trim removes only terminal INDEX entries, leaves their bridge files on disk, and the trimmed INDEX still round-trips through the parser; the versions-per-landed-change KPI emits a number; file-bridge-protocol.md no longer asserts a false byte-for-byte activation |
| `GOV-20` + `GOV-06` (HYG-010 ADR + on-touch seam) | test: the ADR exists in MemBase with a formal-artifact-approval packet; the extracted doctor check family runs via the registry with identical results to the pre-extraction check; db.py is unchanged |
| `GOV-17` (HYG-011 environment) | test: the empty root `.venv` is gone; `doctor._check_ruff` resolves venv-first and no longer false-WARNs when ruff is present; CI matrix includes py3.14 |
| `GOV-17` + `GOV-08` (HYG-023 regen + parity) | test: the regen script reproduces the template hooks from live byte-for-byte; the doctor hash-parity check FAILs on a seeded template/live drift and passes when synced; scaffold.py no longer copies the DEPRECATED poller prompt |
| `GOV-20` (HYG-052 visibility) | test: the doctor WARN lists the assertion-less DCLs; the auto-discovery project's acceptance criteria record the 5/97 + 35-assertion-less census |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/...`; `ruff check` AND `ruff format --check` on changed Python; the ADR carries its formal packet and the protocol edit its narrative packet |

## Acceptance Criteria

1. **HYG-009:** terminal-entry auto-trim lands (non-destructive, audit trail preserved); the
   versions-per-landed-change KPI is in the benchmark suite. No lightweight-lane protocol change.
2. **HYG-010:** the registry-based-discovery ADR exists with its packet; one doctor check family is extracted
   on-touch with identical behavior; db.py untouched.
3. **HYG-011:** empty root `.venv` deleted; `_check_ruff` venv-first (no false WARN); editable install
   refreshed; CI includes py3.14.
4. **HYG-023:** deterministic regen script + release-tag hash-parity doctor check; DEPRECATED scaffold prompt
   replaced; file-bridge-protocol.md:273 corrected (narrative packet).
5. **HYG-052:** doctor WARN on assertion-less DCLs; census recorded as auto-discovery acceptance criteria.
6. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-22-architecture-cluster-001.md` with a matching `NEW` entry at the top of
`bridge/INDEX.md`; append-only. `GOV-FILE-BRIDGE-AUTHORITY-001` is honored; nothing implements until Loyal
Opposition records `GO`, the HYG-010 ADR additionally requires its formal-artifact-approval packet, and the
HYG-023 protocol edit its narrative-approval packet.

## Risk and Rollback

- **Risk — auto-trim drops a still-actionable entry:** the trim is scoped to terminal (VERIFIED/WITHDRAWN)
  statuses only and leaves all bridge files on disk; a test asserts no non-terminal entry is removed.
  **Rollback:** restore the archived INDEX lines (files were never deleted).
- **Risk — doctor decomposition changes check behavior:** the on-touch extraction is verified to produce
  identical results via the registry; only one check family moves; db.py is untouched. **Rollback:** revert
  the extracted module + registry entry.
- **Risk — interpreter changes break a session/CI surface:** `_check_ruff` aligns to the already-proven
  check_ruff_format resolution; the stub `.venv` is empty (no loss); CI py3.14 is additive. **Rollback:**
  revert the doctor + pyproject + workflow edits.
- **Risk — template regen overwrites an intentional template divergence:** the regen is deterministic from
  live and gated by the hash-parity doctor check at release tags, not silently on every run. **Rollback:**
  revert the regen script + doctor check (one-off behavior unaffected).
- **Risk — the file-bridge-protocol.md edit changes normative meaning:** the edit only corrects a factual
  byte-for-byte claim to match reality; it is packet-gated and narrow. **Rollback:** revert the rule edit.

## Recommended Implementation Routing

**Claude/Codex (governance + ADR + protected-narrative).** HYG-010 creates an ADR (formal packet) and HYG-023
edits file-bridge-protocol.md (narrative packet) — governance-finicky. The doctor/cli decomposition, the
regen+parity machinery, and the env alignment are source work needing equivalence tests. The KPI benchmark and
the doctor WARN are cheap-draftable helpers Opus/Codex finalizes. Couples to the in-flight clause
auto-discovery thread for HYG-052.

## Recommended Commit Type

`refactor:` — the dominant change is structural (registry-based discovery seam, INDEX trim, interpreter
canonicalization, template-sync mechanism) with a net-new `feat:` element (the regen script + KPI + ADR) and a
`fix:` element (the false byte-for-byte claim and the false ruff WARN).
