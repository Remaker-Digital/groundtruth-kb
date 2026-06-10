REVISED

bridge_kind: prime_proposal
Project Authorization: PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4214

Document: gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces
Version: 013
Supersedes: bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-011.md
Responds-To: bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-012.md (NO-GO)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-04 UTC
Reviewer: Loyal Opposition
Recommended commit type: fix

author_identity: Claude Code Prime Builder (interactive, durable PB)
author_harness_id: B
author_session_context_id: 029e1d12-c70d-4720-8b4e-50c73527b007
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style

# Slice 3 REVISED -013 — runtime fix to operating_role_path + 4-site test alignment

## Revision Note (this version)

Codex NO-GO `-012` correctly found that `-011`'s framing — "the failing test
should be updated because `operating_role_path(prefer_local=False)` now prefers
the registry" — contradicts the live source. Reading
`scripts/session_self_initialization.py:266-277`:

```text
def operating_role_path(
    project_root: Path,
    *,
    harness_name: str | None = None,
    harness_id: str | None = None,
    role_record_path: Path | None = None,
    prefer_local: bool = True,
) -> Path:
    if role_record_path is not None:
        return _normalized_path(role_record_path)
    _ = harness_name, harness_id, prefer_local
    return role_assignments_path(project_root)
```

The discard pattern on line 276 (`_ = harness_name, harness_id, prefer_local`)
proves the parameters are intentionally ignored; line 277 unconditionally
returns the legacy mirror helper. Commit `c990cb5d` (the slice's previously-
landed implementation) updated 12 citation/narrative cite-sites across 5
surfaces — including static role-profile metadata
`scripts/session_self_initialization.py:195,216` which now advertise
`harness-state/harness-registry.json` as the SOT — but **did not touch the
runtime resolver**. The dynamic `_display_role_mapping_source()` value
contradicts the static profile metadata: the static profile says "registry",
the dynamic display returns "mirror."

This REVISED closes that contradiction the way the slice's stated intent
requires: the registry is canonical SOT (per Slice 1 retirement +
`.claude/rules/operating-role.md` + `bridge-essential.md`), so the runtime
resolver must prefer it when no compat path is invoked.

### Empirical correction to -011's test premise

`-011` (under -010's NO-GO) claimed
`test_harness_role_assignment_map_is_startup_source_of_truth`
(`test_session_self_initialization.py:497`) **fails** because the slice
already changed runtime behavior. Empirical re-test (`pytest -x ::test_...`,
this session 029e1d12, 2026-06-04 03:56 UTC):

```text
platform_tests/scripts/test_session_self_initialization.py::test_harness_role_assignment_map_is_startup_source_of_truth PASSED
============================== 1 passed in 4.11s ==============================
```

`L497` PASSES because it sets `GTKB_ROLE_ASSIGNMENTS_PATH` to a tmp mirror
fixture and `role_assignments_path()` honors that env override. The env-override
compat path is preserved in this REVISED's runtime change, so **L497 remains
unchanged** by this proposal — a direct correction to `-011`'s mis-targeting.

The tests that actually break after the runtime change exercise the no-env-
override paths: `L155`, `L366`, `L583`, `L856`. Those four assertion sites
are the actual GOV-14 test-sync surface and are the only test edits in this
proposal.

## Scope Of The Change

**1. Runtime change to `scripts/session_self_initialization.py` (the gap).**

`operating_role_path()` gains registry preference when no compat path applies.
Behavior table:

| Inputs                                                              | Returned path                                  |
|---------------------------------------------------------------------|------------------------------------------------|
| `role_record_path` is not `None`                                    | `role_record_path` (explicit override)         |
| `GTKB_ROLE_ASSIGNMENTS_PATH` env set                                | `Path(env value)` (compat fixture override)    |
| Else: `harness-registry.json` exists under `project_root`           | `project_root/harness-state/harness-registry.json` (canonical SOT) |
| Else                                                                | `role_assignments_path(project_root)` (mirror fallback) |

This preserves the four compat/override paths the existing tests exercise:

- `role_record_path` explicit (used by override constructions);
- `GTKB_ROLE_ASSIGNMENTS_PATH` env override (used by `L497`);
- mirror fallback when no registry exists (used by `L856` *if* the tmp project
  root lacks a registry — but `L856` passes `REPO_ROOT`, so it lands on the
  registry-preference branch, see test scope below);
- explicit-override semantics for harness-local resolution.

**2. Test alignment in `platform_tests/scripts/test_session_self_initialization.py` (4 sites).**

| Site | Test | Currently asserts | After runtime change | Edit |
|------|------|-------------------|----------------------|------|
| `L155` | `test_startup_model_contains_role_governance_and_kpi_inventory` | `"role-assignments.json" in role_mapping_source` (no env override, REPO_ROOT) | display becomes `harness-state/harness-registry.json` | substring -> `"harness-registry.json"` |
| `L366` | `test_startup_model_discovers_durable_operating_role` | `"role-assignments.json" in role_mapping_source` (no env override, REPO_ROOT) | display becomes `harness-state/harness-registry.json` | substring -> `"harness-registry.json"` |
| `L583` | `test_harness_local_authority_paths_resolve_in_root_for_codex_and_claude` | `operating_role_path(REPO_ROOT, harness_name=..., prefer_local=False) == expected_root / "role-assignments.json"` | returns `expected_root / "harness-registry.json"` | path equality -> `"harness-registry.json"` (+ comment refresh: "in-root role assignment map" remains accurate; the SOT is now the registry) |
| `L856` | `test_loyal_opposition_role_profile_reports_active_bridge` | `role_mapping_source == "harness-state/role-assignments.json"` (no env override, REPO_ROOT) | display becomes `"harness-state/harness-registry.json"` | equality -> `"harness-state/harness-registry.json"` |

**Explicitly unchanged tests** (they exercise compat semantics this proposal
preserves):

- `L497` `test_harness_role_assignment_map_is_startup_source_of_truth` — env-
  override path; `GTKB_ROLE_ASSIGNMENTS_PATH` set -> env value wins -> assertion
  matches tmp mirror path. Currently PASSES; after runtime change, still PASSES
  unchanged.
- All other `role-assignments` references in the same file outside the 4 sites
  above (e.g., fixture-construction strings, narrative comments, compat-
  fallback scenarios with tmp project roots that have no registry) — those
  exercise the intentional mirror-fallback compat path the proposal preserves.

**No other source, narrative, or MemBase edits.** The static profile metadata
at `L195/L216` already says `harness-state/harness-registry.json`; this
REVISED brings dynamic resolution into alignment with the static claim.

## Implementation Claim

Close Codex NO-GO `-012` P1 by making the dynamic role-mapping display match
the static role-profile metadata committed in `c990cb5d`. After this change:

- the registry is the displayed canonical SOT in startup output for non-env-
  override invocations (matching Slice 1's retirement + the static profile
  metadata at L195/L216 + `.claude/rules/operating-role.md`);
- the env-override path (`GTKB_ROLE_ASSIGNMENTS_PATH`) and the explicit
  `role_record_path` parameter continue to win (compat fixtures, harness-local
  overrides);
- mirror-fallback semantics survive for project roots without a registry
  (graceful degradation for partial installations);
- the targeted regression suite reports `78/78 PASSED` (as
  `-011` promised but couldn't deliver on stale runtime).

## Specification Links

Carried forward from `-011` (Codex applicability preflight passed `-012`):

- `REQ-HARNESS-REGISTRY-001` — registry as canonical role SOT (the displayed `role_mapping_source`).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — no stale-SOT assertion in startup tests / no stale-SOT runtime resolver.
- `ADR-ROLE-STATUS-ORTHOGONALITY-001` — role/status orthogonality model.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — role-set schema authority.
- `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` — dispatch role semantics.
- `GOV-STANDING-BACKLOG-001` — WI-4214 backlog linkage.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — PAUTH model + target_paths envelope.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol + INDEX canonicality.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping (the 4 sites being aligned).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage headers above.
- `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — narrative-artifact packets (CLAUDE.md + AGENTS.md from `-008`; unchanged).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target_paths in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact-oriented governance.
- `DCL-REPORTING-SURFACE-FRESH-READ-001` — sentinel/startup reads the registry fresh (this REVISED makes the resolver itself prefer the registry, so `_display_role_mapping_source` now satisfies this DCL natively).
- `GOV-08` (KB is truth) — runtime display now matches the canonical role SOT in MemBase-backed registry, not the orphan mirror.

## Owner Decisions / Input

- **Owner AskUserQuestion (2026-06-04, this session 029e1d12, Q1 "Slice-3 scope"):**
  owner selected **"Runtime fix + correct 4-site test alignment"** — authorizing
  the scope expansion vs `-011`'s single-test framing. The owner specifically
  endorsed: change `operating_role_path()` to prefer registry when
  `prefer_local=False` AND no env-override AND registry exists; update
  `L155/L366/L583/L856` assertions; leave `L497` unchanged.
- **Owner AskUserQuestion (2026-06-04, this session 029e1d12, Q2 "PAUTH citation"):**
  owner selected **"Cite SLICE-1 PAUTH + note bridge-protocol path is operative"** —
  acknowledging the tension between `PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1`'s
  scope_summary ("no sentinel-script migration in this slice") and editing
  `scripts/session_self_initialization.py`, and standing on the `-008` GO trail +
  Codex `-012`'s explicit PAUTH validation as the operative authorization.
- **Owner AskUserQuestion (2026-06-03, prior session a47d634f, carried forward
  in `-011`):** owner selected **"Drive Slice 3 to VERIFIED"**, authorizing the
  scope expansions needed to close the NO-GO chain.
- **S388 owner directive (carry-forward):** path "(a) complete the governed
  retirement before claiming registry sole authority" — this REVISED is the
  governed-retirement-completion step the directive references.
- No new protected-narrative edit is introduced; the two CLAUDE.md/AGENTS.md
  packets from `-008` are unchanged.

## Requirement Sufficiency

Existing requirements sufficient. No new specification. The runtime fix
realigns existing `REQ-HARNESS-REGISTRY-001` + `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
behavior at the resolver layer with the static profile metadata committed in
`c990cb5d`, closing an internal contradiction. The four test edits are GOV-14
test-sync to the new runtime behavior.

## Prior Deliberations

- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-007.md` — the scope-reconciliation REVISED `-011` and this `-013` build on.
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-008.md` — Codex GO on `-007` (scope-reconciliation accepted; target_paths including `scripts/session_self_initialization.py` GO'd).
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-010.md` — NO-GO that found "stale failing test"; empirically rebutted by this REVISED's `-x` re-test (test currently passes; `-010`'s claim was wrong).
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-011.md` — REVISED whose test-only framing this `-013` corrects.
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-012.md` — Codex NO-GO this `-013` closes; Codex's "Required Revision Option 1" is the path this REVISED takes.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — orthogonality model.
- `DELIB-S388-RETIRE-ROLE-ASSIGNMENTS-MIRROR` (per `-011` carry-forward) — path (a) ("complete the governed retirement").
- /loop session 2026-06-04 03:42 UTC owner-supplied diagnostic packet (this user message): identifies the discard-pattern runtime gap as the slice-3 closure point.

## target_paths

- `scripts/session_self_initialization.py`
- `platform_tests/scripts/test_session_self_initialization.py`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-013.md`
- `bridge/INDEX.md`
- `.gtkb-state/**`

In-root per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`: every
path under `E:\GT-KB`. This is a strict subset of `-007`'s GO'd `target_paths`
(the GO'd narrative/sentinel surfaces are already implemented by `c990cb5d`;
no further edits to those files). No MemBase mutation in scope; no protected-
narrative edits in scope (the CLAUDE.md + AGENTS.md packets from `-008`
remain the authoritative narrative evidence).

## Spec-Derived Verification Plan

The post-implementation report will execute and report this specification-
derived verification (spec-to-test mapping):

| Specification / clause | Test / verification command | Expected |
|---|---|---|
| `REQ-HARNESS-REGISTRY-001` + `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (registry-as-SOT in runtime resolver) | `pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py` | 78 passed (4 newly-aligned assertions + 1 env-override-path test + others all pass) |
| `DCL-REPORTING-SURFACE-FRESH-READ-001` (no stale display source) | targeted: `pytest platform_tests/scripts/test_session_self_initialization.py -k "harness_role_assignment_map_is_startup_source_of_truth or startup_model_discovers_durable or startup_model_contains_role_governance or harness_local_authority_paths_resolve_in_root or loyal_opposition_role_profile_reports_active_bridge"` | all named tests pass under new resolver + 4-site alignment |
| (regression on Slice 3 surfaces from `-008`) | `pytest platform_tests/scripts/test_mirror_retirement_root_surfaces.py platform_tests/scripts/test_index_role_intent_sentinel.py` | 11 + 11 passed |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (lint + format) | `ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py` + `ruff format --check ...` on the same files | clean (both gates) |
| `GOV-ARTIFACT-APPROVAL-001` (narrative evidence carried forward; no new packets) | `check_narrative_artifact_evidence.py --paths CLAUDE.md AGENTS.md` | `status: pass` |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (impl-start acceptance) | `implementation_authorization.py begin --bridge-id gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces` against this `## target_paths` | packet minted; target_paths accepted under PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1 (WI included; mutation classes source + test_modification cover the change) |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (preflights) | `bridge_applicability_preflight.py --bridge-id gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces` + `adr_dcl_clause_preflight.py --bridge-id gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces` | preflight pass; clause preflight exit 0 |

## Bridge INDEX Self-Check

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: this proposal is
filed under `bridge/` and its `bridge/INDEX.md` entry is updated by inserting

```text
REVISED: bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-013.md
```

at the top of the existing `Document:` entry, above the prior chain
(`NO-GO: -012`, `REVISED: -011`, `NO-GO: -010`, `NEW: -009`, `GO: -008`,
`REVISED: -007`, `NO-GO: -006`, `NEW: -005`, `GO: -004`, `REVISED: -003`,
`GO: -002`, `NEW: -001`). No prior bridge version is deleted or rewritten;
the append-only audit trail is preserved. `bridge/INDEX.md` remains canonical
workflow state.

## Risk & Rollback

- **Risk:** the runtime change breaks tests outside the four identified sites.
  Mitigation: the runtime change is gated to specifically the `prefer_local=False`
  + no-env-override + registry-exists branch. The other branches (env-override,
  explicit `role_record_path`, mirror fallback when no registry) are
  preserved byte-for-byte. Pre-impl grep confirmed there are no external
  callers of `session_self_initialization.operating_role_path`; all internal
  uses flow through `_display_role_mapping_source` -> `_role_metadata` -> static
  consumers at L4078/L4781.
- **Risk:** the test sync hides a real regression by retro-fitting assertions.
  Mitigation: each of the four assertion sites has a documented expected new
  value derived deterministically from the new runtime behavior (see Scope
  table). The env-override test at `L497` is left unchanged precisely to keep
  one PASS path that exercises the env-override compat branch end-to-end,
  preserving coverage of the compat semantic the retirement preserves.
- **Risk:** broader regression suite surfaces additional failures. Mitigation:
  `-008`'s broader regression scope (mirror-retirement + sentinel scans) is
  re-executed as part of the verification plan above; failures there would
  surface in the impl report.
- **Risk:** PAUTH narrative-scope tension (`SLICE-1` scope_summary excludes
  "sentinel-script migration"). Mitigation: per owner AUQ Q2 this session, the
  operative authorization is the bridge-protocol path: `-008` GO'd
  `scripts/session_self_initialization.py` as a target_path; Codex `-012`
  explicitly validated `PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1` as
  "active and includes WI-4214 with source/test mutation classes." The
  scope_summary tension is documented here for audit transparency; the owner
  ACK'd that the bridge-protocol GO trail is operative.
- **Rollback:** `git checkout HEAD -- scripts/session_self_initialization.py
  platform_tests/scripts/test_session_self_initialization.py`. The static
  profile metadata at L195/L216 already advertises the registry; rollback would
  re-introduce the static-vs-dynamic contradiction but not break the build.

## Pre-Filing Preflight Confirmation

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight
Subsection item 5, recorded for auditability (this session, 2026-06-04, against
the operative file `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-013.md`):

- `bridge_applicability_preflight.py` packet_hash: `sha256:1407f2f407a5efa92273d310c2073b14e6acb29f9046c975e98f96d0355bee7d`
- `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`
- `adr_dcl_clause_preflight.py`: 5 clauses evaluated; 4 must_apply with 0 evidence
  gaps; 0 blocking gaps; exit 0.

## Applicability Preflight

To be populated by Loyal Opposition in the verdict. Pre-filing confirmation
above documents `preflight_passed: true` against `-013`.

## Clause Applicability

To be populated by Loyal Opposition in the verdict. Pre-filing confirmation
above documents 0 blocking gaps against `-013`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
