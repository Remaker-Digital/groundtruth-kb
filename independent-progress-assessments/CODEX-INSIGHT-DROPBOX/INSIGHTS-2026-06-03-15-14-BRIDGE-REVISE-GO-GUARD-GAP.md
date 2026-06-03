Specs: GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
WIs: WI-3429

# Loyal Opposition Insight: `gt bridge revise` GO Guard Gap

## Claim

The live bridge thread `gtkb-bridge-revise-cli-slice-1` is no longer Loyal Opposition-actionable because another LO session filed `GO` at `bridge/gtkb-bridge-revise-cli-slice-1-002.md`. However, independent review during this automation run found a material implementation risk in the approved `-001` proposal: the proposed CLI plan does not explicitly require the existing lifecycle transition validator, and its carry-forward test plan does not prove the new `REVISED` file body carries a `REVISED` status token and accurate new-version authorship/provenance.

## Finding P1-001: Proposed `REVISED` writer path can bypass lifecycle and body/provenance invariants

### Observation

The proposal's core mechanism says the CLI will carry forward the latest Prime-authored `NEW` or `REVISED` file byte-identically, apply a fix, bump the version, write via scanner-safe helpers, and prepend a `REVISED` line to `bridge/INDEX.md`.

Evidence:

- `bridge/gtkb-bridge-revise-cli-slice-1-001.md:44` through `bridge/gtkb-bridge-revise-cli-slice-1-001.md:55` defines the seven-step mechanism.
- `bridge/gtkb-bridge-revise-cli-slice-1-001.md:61` through `bridge/gtkb-bridge-revise-cli-slice-1-001.md:62` defines `content_carryforward_only` as byte-identical content.
- `bridge/gtkb-bridge-revise-cli-slice-1-001.md:188` maps the carry-forward test to equality except version line plus provenance.
- `bridge/gtkb-bridge-revise-cli-slice-1-001.md:202` through `bridge/gtkb-bridge-revise-cli-slice-1-001.md:204` repeats that acceptance criterion.
- `bridge/gtkb-bridge-revise-cli-slice-1-001.md:191` tests only that `compose_index_update` prepends a `REVISED` INDEX line.

The existing bridge writer already has the stricter lifecycle rule:

- `scripts/gtkb_bridge_writer.py:342` through `scripts/gtkb_bridge_writer.py:346` allows Prime `REVISED` only when the current latest status is `NO-GO`.
- `.claude/skills/bridge/helpers/revise_bridge.py:275` through `.claude/skills/bridge/helpers/revise_bridge.py:277` requires completed revision content to start with `REVISED`.
- `scripts/bridge_author_metadata.py:3` through `scripts/bridge_author_metadata.py:5` states bridge artifacts must carry accurate author/runtime metadata.
- `scripts/bridge_author_metadata.py:264` through `scripts/bridge_author_metadata.py:266` returns unchanged content when complete metadata already exists, so blind carry-forward of a prior bridge file can preserve stale author metadata unless the CLI explicitly rewrites or supplements revision provenance.

### Deficiency Rationale

`bridge/INDEX.md` is the canonical workflow state, but bridge files remain audit records. A deterministic CLI that writes `REVISED` entries must preserve both:

1. lifecycle validity: `REVISED` only after latest `NO-GO`; and
2. audit validity: the new version's body status and author/provenance must match a new Prime-authored revision, not the carried-forward source artifact.

The current proposal's test plan can pass while the CLI writes a `REVISED` INDEX line for an illegal latest state, or writes a new file whose first nonblank line remains `NEW`, or preserves stale author metadata from the source version. That undercuts `GOV-FILE-BRIDGE-AUTHORITY-001` and the bridge author-metadata contract.

### Proposed Solution / Enhancement

Prime Builder should implement the approved CLI using `scripts.gtkb_bridge_writer.validate_transition(slug, "REVISED", PRIME_ROLE_SLOT, project_root)` or an equivalent single source of truth before any file or INDEX mutation.

The implementation should also add tests proving:

- `gt bridge revise` refuses `REVISED` when latest status is not `NO-GO`.
- the generated file's first nonblank line is `REVISED`.
- carried-forward prior author metadata is not mistaken for the new revision's author metadata; the new file has explicit current-session revision provenance.
- `--dry-run` does not acquire or mutate a live claim/INDEX/file state.

### Option Rationale

Reusing the existing writer validator is lower risk than re-encoding transition rules inside the new CLI. Adding explicit body-token and provenance tests catches the exact failure mode created by byte-identical carry-forward while preserving the proposal's useful deterministic-service goal.

## Prime Builder Implementation Context

Objective: keep the live GO useful while preventing the new CLI from becoming a lower-safety bridge writer.

Expected file touchpoints:

- `groundtruth-kb/src/groundtruth_kb/bridge_revise.py`
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`
- `groundtruth-kb/tests/test_bridge_revise.py`

Suggested implementation sequence:

1. Route all non-dry-run writes through the existing lifecycle validator before composing content or mutating INDEX.
2. Normalize generated revision content so the first nonblank line is `REVISED`.
3. Add or replace revision-specific provenance/author metadata explicitly instead of relying on `ensure_author_metadata` to update existing metadata.
4. Add focused regression tests for illegal latest states, body token, provenance, and dry-run immutability.
5. Run the proposal's existing focused pytest, Ruff check, and Ruff format check before filing the implementation report.

## Commands / Evidence From This Review

```text
python .claude\skills\bridge\helpers\scan_bridge.py --role loyal-opposition --format json
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-bridge-revise-cli-slice-1 --format json --preview-lines 20
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-revise-cli-slice-1
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-revise-cli-slice-1
groundtruth-kb\.venv\Scripts\gt.exe projects authorizations PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json
groundtruth-kb\.venv\Scripts\gt.exe deliberations search --limit 5 "gt bridge revise WI-3429 deterministic services"
```

Mechanical preflights for `-001` passed. This report is not a bridge verdict and does not supersede the live `GO`; it preserves an implementation risk for the Prime Builder before post-implementation verification.

## Owner Decision Needed

None. This is implementation guidance within the already-approved slice. Loyal Opposition should verify these conditions when the post-implementation report is filed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
