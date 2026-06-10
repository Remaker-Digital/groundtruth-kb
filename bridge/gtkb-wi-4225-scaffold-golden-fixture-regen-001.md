NEW

bridge_kind: governance_advisory
Document: gtkb-wi-4225-scaffold-golden-fixture-regen
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC

author_identity: Claude Code Prime Builder (interactive, session-stated PB)
author_harness_id: B
author_session_context_id: 068e5131-24ab-4f19-ae9d-6015cfd8bb7b
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

Work Item: WI-4225

target_paths: ["groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/**", "groundtruth-kb/tests/fixtures/scaffold_golden/local-only/**"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-4225 — Regenerate scaffold golden fixtures to absorb VERIFIED template drift

## Source / Owner Directive

This proposal implements the golden-fixture-reconciliation portion of **WI-4225**
("Registry and scaffold fixture drift blocks pristine GT-KB test suite",
`origin=regression`). Three committed byte-equality golden-master tests are RED on
`develop` because the scaffold *templates* moved forward through VERIFIED bridge
threads while the committed golden fixtures were never recaptured:

- `groundtruth-kb/tests/test_scaffold_isolation.py::test_tp15_dual_agent_matches_golden_fixture`
- `groundtruth-kb/tests/test_scaffold_isolation.py::test_tp14_local_only_matches_golden_fixture`
- `groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py::test_clean_adopter_byte_matches_golden_fixture`

Each test re-runs `scaffold_project()` into a throwaway in-root sandbox and
byte-compares every output file against the committed fixtures under
`groundtruth-kb/tests/fixtures/scaffold_golden/{dual-agent,local-only}/`, masking
only `groundtruth.toml::created_at`. The remedy is the documented one:
`python scripts/_capture_scaffold_golden.py`.

## Confirmed Drift Inventory (read-only probe; identical scaffold options to the golden)

A read-only probe (`.gtkb-state/_scaffold_drift_probe.py`, operational-tier, mutates
nothing canonical) scaffolded both profiles at the **exact** golden options
(`project_name=_test_golden_<profile>`, `owner=GoldenFixtureOwner`,
`seed_example=False`, `include_ci=False`, `init_git=False`) so `{{PROJECT_NAME}}`
substitution matches the fixtures. Result: **0 missing, 0 extra**; byte-different =
**11 (dual-agent)** and **2 (local-only, a strict subset)**. Every drifted byte
traces to a VERIFIED/landed source change (last-commit provenance via `git log -1`):

| # | Drifted output file | Direction | Governing commit / thread | Change |
|---|---|---|---|---|
| 1 | `.claude/rules/bridge-essential.md` | template→golden (forward) | `79df6c13` / `gtkb-deferred-authority-protocol-alignment` **VERIFIED -011** | "Never reprocess VERIFIED" → "…VERIFIED, ADVISORY, DEFERRED, or WITHDRAWN entries" |
| 2 | `.claude/rules/canonical-terminology.md` | forward | `79df6c13` / same | `bridge` entry statuses `…VERIFIED, ADVISORY.` → `…VERIFIED, ADVISORY, DEFERRED, WITHDRAWN.` |
| 3 | `.claude/rules/file-bridge-protocol.md` | forward | `79df6c13` / same | adds ADVISORY/DEFERRED/WITHDRAWN status rows + `## DEFERRED Status` + skip-notes |
| 4 | `.claude/skills/bridge/helpers/impl_report_bridge.py` | forward | `79df6c13` / same | `_STATUS_LINE_RE` adds `\|DEFERRED` |
| 5 | `.claude/skills/bridge/helpers/revise_bridge.py` | forward | `79df6c13` / same | status-regex adds `\|DEFERRED` |
| 6 | `.claude/skills/bridge/helpers/scan_bridge.py` | forward | `79df6c13` / same | `_STATUS_LINE_RE` adds `\|DEFERRED` |
| 7 | `.claude/skills/bridge/helpers/show_thread_bridge.py` | forward | `79df6c13` / same | `_STATUS_LINE_RE` adds `\|DEFERRED` |
| 8 | `.claude/hooks/bridge-compliance-gate.py` | forward | `f8d74257` / `gtkb-session-id-shared-resolver-unification` **VERIFIED** (WI-4270) | imports `BRIDGE_WORK_INTENT_ORDER` from `scripts.gtkb_session_id` w/ fail-soft fallback that adds `CLAUDE_CODE_SESSION_ID`; adds `.gtkb-state` to the hermetic-scratch set |
| 9 | `.claude/skills/bridge-propose/helpers/write_bridge.py` | forward | `f8d74257` / same (WI-4270) | same session-id resolver refactor |
| 10 | `.claude/hooks/spec-event-surfacer.py` | forward | `28cb7c7a` (2026-04-29, "Slice A REVISED-1 post-impl (-009) — concurrency fix") | `EVENT_FORMAT` long string wrapped across two lines (implicit concat; byte-identical runtime value) — a `ruff`-style line-wrap |
| 11 | `bridge/INDEX.md` | **golden→template (REVERSED)** | `79df6c13` hand-edited the **golden** only; generator `scaffold.py::_generate_bridge_index` NOT updated | golden has ADVISORY/DEFERRED/WITHDRAWN rows + skip-notes the generator never emitted |

local-only drift = files #2 and #8 only (the profile ships no `bridge/` INDEX, no
bridge skill helpers, no `file-bridge-protocol.md`).

Files #1–#10 are clean forward drift: the regen brings the goldens up to the
already-VERIFIED template state. **File #11 is the asymmetric one** and is handled
per owner AUQ below.

## Proposal Kind

`governance_review` — this reconciles committed **test-fixture data** to
already-VERIFIED template state. Per owner AUQ Option A (below) there is **no source
change** (the `_generate_bridge_index` generator is left as-is). No new capability
surface, no runtime behavior change, no KB mutation. Metadata-exempt per
`bridge-compliance-gate` `BRIDGE_KIND_METADATA_EXEMPT`; `Work Item: WI-4225` is cited
for traceability. (WI-4225 has no project/PAUTH; `governance_review` does not require
the project-linkage chain. This mirrors the sibling `gtkb-wi-4279-…` classification,
which touches the same golden files.)

**Cited-vs-declared WI note (collision-warning disambiguation):** the sole *declared*
work item is `WI-4225`. The IDs `WI-4270`, `WI-4279`, and `GTKB-ISOLATION-017` appear
only as **provenance citations** (drift-source threads and the governing test contract)
in the inventory table, Specification Links, and Prior Deliberations — they are not
competing work-item declarations. The bridge-compliance-gate emits a non-blocking
collision warning for these; it is expected and benign here.

## Owner Decisions / Input

Two AskUserQuestion decisions captured 2026-06-03 (this session) are the owner-decision
authority for this proposal:

- **AUQ Q1 — `bridge/INDEX.md` golden disposition → Option A ("Let regen strip the rows").**
  The regen recaptures the golden `bridge/INDEX.md` from the unmodified
  `_generate_bridge_index` generator, which removes the ADVISORY/DEFERRED/WITHDRAWN
  status rows + skip-notes that `79df6c13` hand-added to the golden fixture only.
  Rationale: the scaffolded INDEX is a lightweight queue header; the authoritative
  status table (which this same regen forward-updates to include
  ADVISORY/DEFERRED/WITHDRAWN) lives in the scaffolded `file-bridge-protocol.md`; the
  live GT-KB `bridge/INDEX.md` is itself minimal; avoids duplicating the status table
  in two surfaces. **This AUQ is the explicit owner approval required to remove those
  three golden rows** (Protected-Behaviors removal gate). `test_scaffold_bridge_index.py`
  still passes (it asserts only `NEW`/`GO`/`VERIFIED` rows + `Prime Workflow`/`Codex
  Workflow`, all present in the minimal generator output).

- **AUQ Q2 — Sequencing vs WI-4279 → Option 1 ("Sequence after WI-4279 lands").**
  File this proposal now (Codex may review in parallel), but **gate the actual
  `_capture_scaffold_golden.py` run on WI-4279's template token-fix landing** (see
  Implementation Sequencing below).

## Implementation Sequencing (Precondition Gate)

Sibling thread `gtkb-wi-4279-scaffold-phantom-spec-citation-repoint` re-points the
phantom `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` → `GOV-SPEC-CAPTURE-TRANSPARENCY-001` in
`templates/rules/canonical-terminology.md` + both goldens. A clean regen recaptures
`canonical-terminology.md` from the template; if the template still carried the phantom,
the regenerated golden would re-bless a known-phantom citation.

**Live status (2026-06-03, at filing):** WI-4279 has progressed to
`GO: bridge/gtkb-wi-4279-scaffold-phantom-spec-citation-repoint-002.md`, and a concurrent
session has applied its token fix to the working tree — `rg` confirms the phantom is now
**absent** from `groundtruth-kb/templates/rules/canonical-terminology.md` and from both
golden `canonical-terminology.md` files (token-only; the DEFERRED-line drift this regen
absorbs is untouched). The WI-4279 changes are currently **uncommitted** in the shared
working tree.

**Implementation precondition (hard):** the `_capture_scaffold_golden.py` run MUST be
performed only after WI-4279 is **committed and VERIFIED** — not merely present in the
working tree — so this regen's commit never entangles another session's uncommitted work.
After WI-4279 commits, the regen reproduces the corrected token automatically and
WI-4279's golden edits become a strict subset of this regen's output. The implementation
report will include
`rg -uu --hidden "GOV-CHAT-DERIVED-SPEC-APPROVAL-001" groundtruth-kb/tests/fixtures/scaffold_golden/`
returning zero hits as evidence the precondition held.

## Exact Implementation (post-GO, post-WI-4279)

1. Confirm precondition: `rg -uu "GOV-CHAT-DERIVED-SPEC-APPROVAL-001" groundtruth-kb/templates/rules/canonical-terminology.md` returns no hits.
2. `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi-4225-scaffold-golden-fixture-regen` (impl-start packet scoped to the golden dirs).
3. `python scripts/_capture_scaffold_golden.py` (recaptures both profiles; no source/`scaffold.py` change — Option A).
4. `git diff --stat groundtruth-kb/tests/fixtures/scaffold_golden/` — expect exactly the drift files above to change. For `groundtruth.toml` (both profiles), confirm the ONLY delta is `created_at` and revert those two files (`git checkout -- …/groundtruth.toml`) to avoid a spurious dynamic-field bump (the test masks `created_at`; recapturing a fresh timestamp adds no value and is noise).
5. Secret/dynamic-field audit of the full regenerated diff (no credentials, no unmasked dynamic fields beyond `created_at`).
6. Run the three byte-equality tests → expect green.

## Out of Scope (Explicit)

- **The `_generate_bridge_index` generator is NOT modified** (owner chose Option A over Option B). Future adopters keep the minimal INDEX queue header; deferred-authority status semantics reach them via the scaffolded `file-bridge-protocol.md` + rule files.
- **The registry-snapshot / managed-artifact-coverage portion of WI-4225** (the "missing template registry coverage for hooks/narrative-artifact-approval-gate.py" sub-finding). The current probe shows **0 missing / 0 extra** files, so the file inventory is already consistent and no inventory remediation is in this thread; if a distinct registry-snapshot surface is still red it is a separate slice.
- The WI-4279 token correction itself (sibling thread; this thread depends on it but does not perform it).
- Append-only `bridge/*.md` history that mentions the phantom or pre-DEFERRED status sets.

## Specification Links

- `GTKB-ISOLATION-017` (Slice 3 TP14/TP15 + Slice 5 clean-adopter byte-diff) — the golden-master byte-equality test contract this proposal restores to green; origin `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-004.md` (GO).
- `gtkb-deferred-authority-protocol-alignment` **VERIFIED -011** — authority that the ADVISORY/DEFERRED/WITHDRAWN template additions (drift files #1–#7) are intended.
- `gtkb-session-id-shared-resolver-unification` **VERIFIED** (WI-4270) — authority that the session-id resolver refactor (drift files #8–#9) is intended.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; `bridge/INDEX.md` canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-linkage compliance (this section).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test plan below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; all target paths are in-root under `E:\GT-KB` (`groundtruth-kb/tests/fixtures/...`); the capture sandbox is in-root `applications/_test_golden_<profile>/` and auto-removed.
- `GOV-STANDING-BACKLOG-001` — WI-4225 is the MemBase backlog home; this is the golden-fixture reconciliation slice of it.
- `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — cited for completeness; **non-applicable**: the golden fixtures are unprotected scaffold/test data (`.claude/rules/*.md` protected glob is single-level/repo-root and does not match `…/scaffold_golden/…/.claude/rules/…`), so no per-file approval packets are required. The one removal action (3 golden INDEX rows) is owner-approved via AUQ Q1 above.

## Prior Deliberations

- `bridge/gtkb-wi-4279-scaffold-phantom-spec-citation-repoint-001.md` (NEW) — sibling thread; this regen's precondition. Its proposal §"Out of Scope" explicitly names "broader golden-fixture byte staleness … a separate hygiene WI" — i.e. this thread.
- `gtkb-deferred-authority-protocol-alignment` (chain -001…-011, VERIFIED) — produced drift files #1–#7; `79df6c13`.
- `gtkb-session-id-shared-resolver-unification` (VERIFIED -006/-008, WI-4270) — produced drift files #8–#9; `f8d74257`.
- Commit `28cb7c7a` (2026-04-29) — produced drift file #10 (spec-event-surfacer line-wrap); month-old un-recaptured drift, evidence that golden recapture is not on any routine gate (candidate follow-on: a "golden-freshness" pre-merge check).
- Owner AUQ 2026-06-03 (this session) — INDEX Option A + sequencing Option 1 (recorded in `## Owner Decisions / Input`).
- `gt deliberations search "scaffold golden fixture regenerate byte equality drift"` — no prior deliberation specific to this regen slice beyond the governing threads above.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing contract is the GTKB-ISOLATION-017
golden-master byte-equality test (scaffold output must byte-equal the committed
fixture). The drift sources are all already-VERIFIED template changes. The two open
choices (INDEX disposition; sequencing) are resolved by owner AUQ above. No new
specification is required.

## Spec-Derived Verification Plan

| Specification / Finding | Spec-to-test mapping | Command | Expected |
|---|---|---|---|
| GTKB-ISOLATION-017 byte-equality contract (all 3 tests green) | the three golden-master tests | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_scaffold_isolation.py::test_tp15_dual_agent_matches_golden_fixture groundtruth-kb/tests/test_scaffold_isolation.py::test_tp14_local_only_matches_golden_fixture groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py::test_clean_adopter_byte_matches_golden_fixture -q -p no:cacheprovider` | 3 passed |
| `test_scaffold_bridge_index` still green under Option A (minimal INDEX) | scaffold INDEX content test | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_scaffold_bridge_index.py -q -p no:cacheprovider` | passed |
| WI-4279 precondition held (no phantom re-blessed) | repo sweep over regenerated goldens | `rg -uu --hidden "GOV-CHAT-DERIVED-SPEC-APPROVAL-001" groundtruth-kb/tests/fixtures/scaffold_golden/` | no hits |
| No secret / unexpected dynamic-field leak | manual diff audit of full regen | `git diff --stat groundtruth-kb/tests/fixtures/scaffold_golden/` + per-file review; `groundtruth.toml` delta = `created_at` only (reverted) | only intended drift files changed |
| Drift scope matches this analysis | inventory check | regen `git diff --name-only` vs the 11+2 file list above | exact match |

## Risk / Rollback

Low. Test-fixture data regeneration only; no source/`scaffold.py` change (Option A);
no runtime behavior change; no KB mutation. Every absorbed byte traces to a
VERIFIED/landed source change. The single removal (3 golden INDEX rows) is owner-AUQ
approved. Rollback is a single-commit revert of the `scaffold_golden/` tree. The
WI-4279 precondition gate prevents re-blessing the phantom. The capture sandbox is
in-root and auto-removed.

## Recommended Commit Type

`test` — regenerates committed test-fixture data (golden masters) to track
already-VERIFIED template changes; no source-capability change.

## Bridge Filing (INDEX-Canonical)

Filed under `bridge/` with a `NEW` entry inserted at the top of a new
`gtkb-wi-4225-scaffold-golden-fixture-regen` document list in `bridge/INDEX.md`;
append-only — no prior entry deleted or rewritten. `bridge/INDEX.md` remains canonical
per `GOV-FILE-BRIDGE-AUTHORITY-001`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
