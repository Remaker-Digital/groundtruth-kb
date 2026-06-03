REVISED

bridge_kind: implementation_proposal
Document: gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces
Version: 003
Author: Prime Builder (Claude, harness B; session-stated role via ::init gtkb pb)
Date: 2026-06-03 UTC
Responds to: bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-002.md (GO, by Antigravity LO at harness C)
Recommended commit type: refactor
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Project Authorization: PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1
Work Item: WI-4214
Owner Decision: DECISION-S388-PATH-2-EXPAND-MIGRATION

author_identity: Claude Prime Builder (session-stated)
author_harness_id: B
author_session_context_id: 2026-06-03T17:34:38Z
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI on Windows 11 (harness B, explanatory output style)

target_paths: ["CLAUDE.md", "AGENTS.md", "scripts/session_self_initialization.py", "scripts/check_index_role_intent_sentinel.py", "scripts/single_harness_bridge_dispatcher.py", "bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-003.md", "bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-004.md", "bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-005.md", "bridge/INDEX.md", ".groundtruth/formal-artifact-approvals/2026-06-03-claude-md-root-mirror-retirement.json", ".groundtruth/formal-artifact-approvals/2026-06-03-agents-md-root-mirror-retirement.json", "platform_tests/scripts/test_mirror_retirement_root_surfaces.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# Slice 3 REVISED — Structural Parseability Correction (no scope change from -001 / -002 GO)

## Revision Claim

This REVISED-1 is a **structural-only correction** of the `-001` proposal that
Antigravity GO'd at `-002`. The substantive plan, scope, target_paths, owner
decision basis, and verification plan are unchanged. The only change is the
addition of the **inline `target_paths:` metadata line** that
`scripts/implementation_authorization.py` parses (via the regex at
`scripts/implementation_authorization.py:64`).

The `-001` proposal expressed target_paths only under a `## Target Paths`
markdown heading with a fenced JSON code block. That format passes
applicability + clause preflights and is human-readable, but it is not parsed
by the impl-auth `extract_target_paths()` function — which looks for either
(a) an inline `target_paths:[...JSON-list-on-one-line...]` metadata line, or
(b) a `## Files Expected To Change` / `## target_paths` (lowercase) section
with bullet rows. This caused `python scripts/implementation_authorization.py
begin --bridge-id gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces`
to fail with `"Approved proposal is missing concrete target_paths or Files
Expected To Change"`, blocking impl-start packet minting against the GO.

This REVISED-1 places the same target_paths set as an inline metadata line
above (line 26), so impl-auth can mint a packet against the GO chain. **No
substantive scope change.** No new target paths are added beyond what `-001`
specified, except:

- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-003.md`
  (this REVISED) and a future `-004` / `-005` for the post-impl report and
  any GO/VERIFIED — already implicit in the bridge protocol but now explicit
  in the inline list.
- `platform_tests/scripts/test_mirror_retirement_root_surfaces.py` — the
  windowed-keyword test the Codex `-002` GO conditions step 6 requires; this
  was implicit in `-001`'s § Step 7 prose but not listed in the JSON. Adding
  it explicitly makes the impl-start gate accept the test write.

All other target_paths from `-001` are carried forward verbatim.

## Scope (carried forward from -001 / -002 GO — no change)

(Same 12 cite sites across 5 files plus 2 narrative-artifact-approval packets
plus 1 schema-adapter helper, exactly as approved by Antigravity at `-002`.)

1. **CLAUDE.md:7** — root narrative authority. Repoint `role-assignments.json`
   → `harness-registry.json`; orphan-mark mirror.
2. **AGENTS.md** (4 sites at lines 35, 50, 69, 245) — Codex-side root
   narrative authority. Repoint with compat framing.
3. **scripts/session_self_initialization.py** (3 sites at lines 195, 216,
   6457) — startup generator. Two dict values + one prose string.
4. **scripts/check_index_role_intent_sentinel.py** (3 sites at lines 5, 162,
   326) — INDEX role-intent sentinel. Docstring + comment text + runtime
   read. The runtime read at line 326 requires a `_role_doc_from_registry`
   schema-adapter helper since the registry uses list-of-dicts while
   `build_role_intent_state()` expects dict-keyed-by-id.
5. **scripts/single_harness_bridge_dispatcher.py:333** — single-harness
   dispatcher prose instruction. Repoint to registry.

The mirror file `harness-state/role-assignments.json` remains on disk
(physical deletion deferred to a future minor slice). After Slice 3 lands,
**no live surface treats the mirror as authoritative** — closing Codex
NO-GO `-006 F1` on `gtkb-role-rule-orthogonality-cleanup-claude-pb-switch`.

## Specification Links

(Carry-forward verbatim from `-001`; same 19 concrete spec citations. All
phantom-swept against live MemBase before draft. Reproduced here for inline
parseability per `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`.)

**Slice 1 + Slice 2 chain (carry-forward):**

- `REQ-HARNESS-REGISTRY-001` v3 (specified)
- `ADR-ROLE-STATUS-ORTHOGONALITY-001` v2 (specified)
- `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` v2 (specified)
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v1 (specified)
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3 (specified)

**Project / backlog governance:**

- `GOV-STANDING-BACKLOG-001` v5 (verified)
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v1 (specified)

**Bridge protocol:**

- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 (verified)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified)
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 (specified)

**Artifact governance:**

- `GOV-ARTIFACT-APPROVAL-001` v3 (verified)
- `PB-ARTIFACT-APPROVAL-001` v2 (verified)
- `DCL-ARTIFACT-APPROVAL-HOOK-001` v3 (verified)

**Isolation + advisory:**

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1 (specified)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` v1 (verified)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` v1 (verified)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` v1 (verified)
- `DCL-REPORTING-SURFACE-FRESH-READ-001` v1 (specified)

## Owner Decisions / Input

- **S388 owner directive (2026-06-03):** "(a) complete its governed
  retirement before claiming registry sole authority". This authorized the
  Path-2 migration this proposal carries.
- **AUQ at this session (2026-06-03):** owner answered the four-question
  /loop wrap AUQ on the 4 NO-GO threads with **"Take slice-3 in focused
  session (Recommended)"** for `gtkb-role-rule-orthogonality-cleanup-claude-pb-switch`
  F1 closure. This explicit owner-AUQ direction is the reaffirmation for
  this REVISED-1 of the Slice 3 work.
- No new owner-decision scope is introduced by this REVISED-1; the
  structural correction is a parser-format alignment, not a scope or
  authority change.

## Prior Deliberations

- `DELIB-2799` — owner instruction and Slice-1 PAUTH for WI-4214 umbrella.
- `DELIB-2750` — role-assignments mirror retirement context.
- `DELIB-2556` — registry projection reconciliation verification.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — orthogonality model.
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-008.md` (VERIFIED).
- `bridge/gtkb-retire-role-assignments-mirror-slice-2-rule-and-automation-repoint-007.md` (VERIFIED).
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-006.md` (NO-GO) — the F1 finding this Slice 3 closes.
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-001.md` (NEW; this REVISED's predecessor).
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-002.md` (GO; the verdict this REVISED carries forward).

No prior deliberation rejects the root + startup-surfaces retirement; no
prior deliberation rejects the parser-format alignment correction.

## Requirement Sufficiency

**Existing requirements sufficient.** Same spec carry-forward as Slice 1 +
Slice 2; no new spec creation needed. The structural correction is a
parser-format alignment within the impl-auth gate's accepted formats —
governed by the gate's source (`scripts/implementation_authorization.py:64`),
not by a new requirement. The schema-adapter introduced in
`check_index_role_intent_sentinel.py:326` is non-spec implementation detail
consistent with `REQ-HARNESS-REGISTRY-001` v3.

## Spec-Derived Verification Plan

Same as `-001`. Carried forward:

| Specification / clause | Verification | Expected |
|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (windowed-keyword broader scan per Codex `-006` step 2) | `platform_tests/scripts/test_mirror_retirement_root_surfaces.py` — assert no live citation of `role-assignments.json` as authority across the 5 target files (carve-outs allowed for explicit `orphan` / `compat` framing). | 0 violations. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `git status` after staging — all changed paths under `E:\GT-KB`. | All paths in-root. |
| `GOV-ARTIFACT-APPROVAL-001` (protected narrative) | Narrative-artifact-approval packets at `.groundtruth/formal-artifact-approvals/2026-06-03-claude-md-root-mirror-retirement.json` and `.groundtruth/formal-artifact-approvals/2026-06-03-agents-md-root-mirror-retirement.json`; sha256 of staged blobs matches `body_hash` field; pre-commit narrative-artifact-evidence check passes. | PASS. |
| `REQ-HARNESS-REGISTRY-001` (registry-as-SOT) | Post-edit grep across the 5 target files for `harness-registry.json` authority claims; mirror references retained only with `orphan` or `compat` framing. | All 5 surfaces name registry as SOT. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (ruff lint + format) | `ruff check` + `ruff format --check` on 3 changed .py files. | Clean. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (fresh-read invariant on adapter) | The new `_role_doc_from_registry` helper reads fresh from disk via `load_json(project_root / "harness-state" / "harness-registry.json")` on each invocation; no cache. | Verified by code inspection + adapter unit test. |

## Risk / Rollback

- **Risk: structural revision drift from `-001` scope.** Mitigation: this
  REVISED-1 is a strict superset of `-001`'s `## Target Paths` JSON, with
  only the future bridge versions (-003/-004/-005) and the windowed-test
  path added to the inline parseable form. No scope is removed; no new
  source mutation is authorized beyond what `-002` already approved.
- **Risk: protected-file packet mismatch.** Mitigation: narrative-artifact-
  approval packets will be generated via the canonical CLI after working-
  tree edits complete, using sha256 of STAGED blob (per memory recipe).
- **Rollback:** clean `git revert` of the impl commit restores the 5 source
  files; the bridge artifacts remain as audit trail.

## In-Root Placement Evidence

All paths under `E:\GT-KB` per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.
No `applications/` paths. No out-of-root targets.

## Recommended Commit Type

`refactor` — same as `-001`. Renames the authoritative role-record citation
from the orphan mirror to the canonical registry across root and startup
surfaces. No new capability; no behavior change beyond what the registry-as-
SOT contract already promised.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
