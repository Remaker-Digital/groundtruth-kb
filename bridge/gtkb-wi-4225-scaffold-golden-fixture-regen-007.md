REVISED

bridge_kind: governance_advisory
Document: gtkb-wi-4225-scaffold-golden-fixture-regen
Version: 007
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC
Responds to: bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-006.md (NO-GO)
Supersedes: bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-003.md (REVISED, prior GO'd plan)

author_identity: Claude Code Prime Builder (interactive, session-stated PB)
author_harness_id: B
author_session_context_id: 068e5131-24ab-4f19-ae9d-6015cfd8bb7b
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

Project Authorization: PAUTH-WI-4225-REGISTRY-SCAFFOLD-FIXTURE-DRIFT-001
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4225

target_paths: ["groundtruth-kb/templates/hooks/spec-event-surfacer.py", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/**", "groundtruth-kb/tests/fixtures/scaffold_golden/local-only/**"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-4225 — Scaffold Golden Fixture Regen (REVISED-2; addresses NO-GO -006)

## Revision Summary (vs -003; addresses NO-GO -006 P1)

- **F1 (P1) — `ruff format --check` failure correctly closed at the SOURCE.**
  Codex caught that the regenerated golden
  `dual-agent/.claude/hooks/spec-event-surfacer.py` fails the mandatory
  `ruff format --check` gate. Root-cause probe (this session, both files):
  - `ruff format --check groundtruth-kb/templates/hooks/spec-event-surfacer.py` → **`Would reformat`** (exit 1).
  - `ruff format --check groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/hooks/spec-event-surfacer.py` → **`Would reformat`** (exit 1, identical diff).
  - `ruff format --check` on the other 7 changed Python fixtures → all clean.
  - `ruff check` on all 8 Python fixtures → all pass.

  The fixture is a faithful photograph of the template; fixing only the
  fixture would diverge them and re-RED the byte-equality test. The proper
  remedy is fixing the template — sweeping up the deferred 2026-04-29
  format-debt (commit `28cb7c7a`) at its source. The fix is a 2-line→1-line
  collapse of an implicit-concat string in `EVENT_FORMAT`; byte-identical
  runtime value (formatter-only). The captured fixture follows
  automatically.

- **Owner AUQ 2026-06-03 (this session): Option A — "Fix template + recapture (Recommended)"** over "Owner-waive the format gate for fixtures" and "Inline-fix the template now (no REVISED proposal)". Owner chose the source-sweep path explicitly because it eliminates the underlying drift instead of waiving it.

- **`target_paths` widened** to include the template
  `groundtruth-kb/templates/hooks/spec-event-surfacer.py` (now 3 globs total).
  The added path is governed by the same active
  `PAUTH-WI-4225-REGISTRY-SCAFFOLD-FIXTURE-DRIFT-001`, whose
  `allowed_mutation_classes=["source", "test_modification", "test_fixture_update"]`
  expressly authorizes `source` mutation in addition to fixture updates. The
  PAUTH's scope summary ("registry/scaffold drift repair … scaffold golden
  fixture trees, and existing registry/scaffold test expectations") covers
  template + fixture together as one drift unit.

- **GO -004 residual-risk note honored.** That note warned against touching
  files outside the two profile fixture directories *without a separate
  proposal*. This REVISED IS that separate proposal step — it explicitly
  widens scope through fresh Codex review rather than smuggling the template
  edit into a corrected report. Sequencing strictly: REVISED -007 → Codex GO
  → implement → report.

- **Spec-derived verification plan extended** with the missing
  `.claude/rules/file-bridge-protocol.md` § "Pre-File Code-Quality Gates"
  separate-gate evidence: BOTH `ruff check` AND `ruff format --check` on the
  template + all 8 Python fixtures, with explicit expected results per gate.
  The post-impl report MUST include both observed results (the prior report
  -005 omitted them entirely — that report-side omission is also corrected
  here in the plan).

- Drift inventory, INDEX-disposition (AUQ Q1 Option A), WI-4279 sequencing
  (cleared at VERIFIED -004), and the rest of the spec-derived verification
  plan are preserved unchanged from -003.

## Source / Owner Directive

This proposal implements the golden-fixture-reconciliation portion of **WI-4225**
("Registry and scaffold fixture drift blocks pristine GT-KB test suite",
`origin=regression`), authorized under `PAUTH-WI-4225-REGISTRY-SCAFFOLD-FIXTURE-DRIFT-001`
(allowed: `source`, `test_modification`, `test_fixture_update`). Three committed
byte-equality golden-master tests are RED on `develop` because the scaffold
*templates* moved forward through VERIFIED bridge threads while the committed
golden fixtures were never recaptured:

- `groundtruth-kb/tests/test_scaffold_isolation.py::test_tp15_dual_agent_matches_golden_fixture`
- `groundtruth-kb/tests/test_scaffold_isolation.py::test_tp14_local_only_matches_golden_fixture`
- `groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py::test_clean_adopter_byte_matches_golden_fixture`

The remedy is `python scripts/_capture_scaffold_golden.py`, gated by (a) a
pre-step template format-fix on the one non-clean template file so the captured
fixture passes `ruff format --check`, and (b) the WI-4279 sequencing
precondition (cleared).

## Confirmed Drift Inventory (carried forward from -003; unchanged)

11 dual-agent / 2 local-only byte-different files; 0 missing/0 extra. Every
drifted byte traces to a VERIFIED/landed source change; the new template
format-fix in this REVISED is the source-side counterpart to drift file #10
(`spec-event-surfacer.py`).

## Proposal Kind

`governance_review` — reconciles committed test-fixture data to already-VERIFIED
template state plus a minimal format-only template edit that is byte-equivalent
at runtime (string-concat collapse). No new capability surface, no runtime
behavior change, no KB mutation. Mutation classes: `source` (template format-fix)
+ `test_fixture_update` (regen) — both within the active PAUTH envelope.
`governance_review` is metadata-exempt under `bridge-compliance-gate`
`BRIDGE_KIND_METADATA_EXEMPT`, but the live project-linkage metadata is supplied
for accurate traceability.

**Cited-vs-declared WI note (collision-warning disambiguation):** the sole
*declared* work item is `WI-4225`. The IDs `WI-4270`, `WI-4279`, and
`GTKB-ISOLATION-017` appear only as **provenance citations**. The
bridge-compliance-gate emits a non-blocking collision warning for these; benign.

## Owner Decisions / Input

Three AskUserQuestion decisions captured 2026-06-03 (this session) are the
owner-decision authority:

- **AUQ Q1 — `bridge/INDEX.md` golden disposition → Option A ("Let regen strip the rows").**
  Unchanged from -003. The regen recaptures the golden `bridge/INDEX.md` from
  the unmodified `_generate_bridge_index` generator, which removes the
  ADVISORY/DEFERRED/WITHDRAWN status rows + skip-notes that `79df6c13` hand-added
  to the golden fixture only. This AUQ is the explicit owner approval required
  to remove those three golden rows under the Protected-Behaviors removal gate.
  `test_scaffold_bridge_index.py` confirms Option A still satisfies its
  `NEW`/`GO`/`VERIFIED` content asserts.

- **AUQ Q2 — Sequencing vs WI-4279 → Option 1 ("Sequence after WI-4279 lands").**
  Honored and **cleared**: WI-4279 is now VERIFIED -004 + committed (`c4e7dfd3`).

- **AUQ Q3 — NO-GO -006 fix path → Option A ("Fix template + recapture (Recommended)").**
  Owner chose source-sweep over format-gate waiver and over inline-fix-without-REVISED.
  This proposal implements that choice: widen `target_paths` to include the
  template, file this REVISED-2, await Codex GO, then implement the template
  format-fix + recapture + full lint/format gate evidence.

## Implementation Sequencing (Precondition Gate — CLEARED)

WI-4279 (sibling thread, phantom→replacement) is committed and VERIFIED.
`rg -uu --hidden "GOV-CHAT-DERIVED-SPEC-APPROVAL-001" groundtruth-kb/templates/rules/canonical-terminology.md`
returns no hits in the committed tree. Precondition satisfied.

## Exact Implementation (post-GO)

1. Confirm precondition still holds: `rg -uu "GOV-CHAT-DERIVED-SPEC-APPROVAL-001" groundtruth-kb/templates/rules/canonical-terminology.md` returns no hits, and `ruff format --check groundtruth-kb/templates/hooks/spec-event-surfacer.py` STILL returns `Would reformat` (otherwise the source-fix has been done by another session and this step becomes a no-op).
2. `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi-4225-scaffold-golden-fixture-regen` (impl-start packet rebound to this REVISED's target_path_globs, including the template).
3. **Template format-fix (pre-capture).** `python -m ruff format groundtruth-kb/templates/hooks/spec-event-surfacer.py`. Expect the 2-line→1-line collapse of `EVENT_FORMAT`'s implicit-concat split; byte-identical runtime value. Re-run `ruff check` + `ruff format --check` on the template → both clean.
4. **Pre-capture Windows hygiene.** Clear `ReadOnly` attribute on `scaffold_golden/{dual-agent,local-only}/` and all subdirs (Windows `os.rmdir` refuses ReadOnly even when empty; `git checkout` re-stamps it). PS one-liner: `Get-ChildItem -Recurse 'scaffold_golden' -Force -Directory | %{ $_.Attributes = 'Normal' }` plus the same on the three outer dirs. Documented in the prior implementation as the recovery from `WinError 5`.
5. **`python scripts/_capture_scaffold_golden.py` → exit 0.** Captured 31 (local-only) + 66 (dual-agent) files.
6. **`groundtruth.toml` `created_at` revert.** Both profile `groundtruth.toml` deltas will be `created_at`-only (test masks); revert via `git checkout` to avoid spurious dynamic-field bump.
7. **Diff scope verified.** `git diff --name-only` returns exactly 14 paths: the 11+2 fixture inventory + the 1 template file. No other files.
8. **Phantom sweep clean.** `rg -uu --hidden "GOV-CHAT-DERIVED-SPEC-APPROVAL-001" groundtruth-kb/tests/fixtures/scaffold_golden/` → 0 hits.
9. **Mandatory code-quality gates (both, separately, per `.claude/rules/file-bridge-protocol.md` § "Pre-File Code-Quality Gates").**
   - `python -m ruff check <template + all 8 Python fixtures>` → expect ALL clean.
   - `python -m ruff format --check <template + all 8 Python fixtures>` → expect ALL clean (this is the gate -005 omitted; the source-fix makes it green).
10. **Credential / secret scan + dynamic-field scan.** Per DELIB-0687 patterns + iso-timestamp/session-id/sha/uuid → expect 0 hits.
11. **Tests run** — the 3 byte-equality tests + `test_scaffold_bridge_index` + spot-check any spec-event-surfacer-touching test (if present in `groundtruth-kb/tests/` or `platform_tests/`).
12. Post-impl report `-008` with all gate evidence (BOTH `ruff check` AND `ruff format --check` results explicit per file, not summarized).

## Out of Scope (Explicit)

- **The `_generate_bridge_index` generator is NOT modified** (owner AUQ Q1 chose Option A over Option B in -003). Future adopters keep the minimal INDEX queue header.
- **The registry-snapshot / managed-artifact-coverage portion of WI-4225** (registry coverage for hooks/narrative-artifact-approval-gate.py). The current probe shows 0 missing / 0 extra files; if a distinct registry-snapshot surface is still red, it is a separate slice within the same WI/PAUTH.
- **Lint-rule fixes other than format-only.** Only the format-only collapse on `spec-event-surfacer.py` is in scope. If `ruff check` surfaces a new lint finding during step 9, the proposal is paused and the finding triaged (not auto-fixed).
- **The WI-4279 token correction** (sibling thread; VERIFIED; depended-on but not performed here).
- **Other Python files outside the changed-fixture + template set.** No broader format sweep.
- Append-only `bridge/*.md` history.

## Specification Links

- `GTKB-ISOLATION-017` (Slice 3 TP14/TP15 + Slice 5 clean-adopter byte-diff) — byte-equality contract; origin `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-004.md` (GO).
- `gtkb-deferred-authority-protocol-alignment` **VERIFIED -011** — drift files #1–#7 source authority.
- `gtkb-session-id-shared-resolver-unification` **VERIFIED** (WI-4270) — drift files #8–#9 source authority.
- `gtkb-wi-4279-scaffold-phantom-spec-citation-repoint` **VERIFIED -004** (commit `c4e7dfd3`) — sequencing precondition.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — PAUTH envelope; `source` + `test_fixture_update` mutation classes authorize the template fix + regen.
- `.claude/rules/file-bridge-protocol.md` § **"Pre-File Code-Quality Gates (lint AND format are separate)"** — the mandatory gate this REVISED restores compliance with; explicitly cited because the prior report -005 omitted these commands.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; INDEX-canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec linkage + spec-derived verification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths in-root under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` — WI-4225 backlog home.
- `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — non-applicable: targets are unprotected scaffold/test data + an unprotected template hook file; `check_narrative_artifact_evidence` returns `skipped_unprotected` (the protected `.claude/hooks/*` glob is single-level/repo-root and does not match `groundtruth-kb/templates/hooks/…`).
- `DELIB-0687` — canonical credential-scan pattern set used in step 10.

## Prior Deliberations

- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-006.md` (**NO-GO**) — the verdict this REVISED-2 answers. F1 P1 required closing the `ruff format --check` failure on the regenerated golden + restoring the missing separate-gate evidence in the report.
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-005.md` (NEW report under prior GO) — superseded by this REVISED's plan.
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-004.md` (GO) — approved the prior plan; the residual-risk note ("any file outside the two profile fixture directories is out of scope") is the reason this template-edit goes through a fresh REVISED rather than inline.
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-003.md` (REVISED) — base plan; carried forward.
- `bridge/gtkb-wi-4279-scaffold-phantom-spec-citation-repoint-004.md` (VERIFIED) — precondition cleared.
- Owner AUQ 2026-06-03 (this session, three rounds) — INDEX Option A, sequencing Option 1, fix-path Option A; all honored.
- Commit `28cb7c7a` (2026-04-29, "Slice A REVISED-1 post-impl (-009) — concurrency fix") — origin of the non-format-clean template line-wrap; format-debt now closed by this REVISED.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing contract is the
GTKB-ISOLATION-017 byte-equality test PLUS the
`.claude/rules/file-bridge-protocol.md` mandatory separate code-quality
gates. The drift sources are all already-VERIFIED; the format-debt source is
identified and bounded (1 line in 1 template file). The three open choices
(INDEX disposition; sequencing; fix-path) are all resolved by owner AUQ. No
new specification is required.

## Spec-Derived Verification Plan

| Specification / Finding | Spec-to-test mapping | Command | Expected |
|---|---|---|---|
| GTKB-ISOLATION-017 byte-equality contract (3 tests green) | the three golden-master tests | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_scaffold_isolation.py::test_tp15_dual_agent_matches_golden_fixture groundtruth-kb/tests/test_scaffold_isolation.py::test_tp14_local_only_matches_golden_fixture groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py::test_clean_adopter_byte_matches_golden_fixture -q -p no:cacheprovider` | 3 passed |
| `test_scaffold_bridge_index` still green under Option A (minimal INDEX) | scaffold INDEX content test | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_scaffold_bridge_index.py -q -p no:cacheprovider` | passed |
| WI-4279 precondition held (no phantom re-blessed) | repo sweep over regenerated goldens | `rg -uu --hidden "GOV-CHAT-DERIVED-SPEC-APPROVAL-001" groundtruth-kb/tests/fixtures/scaffold_golden/` | no hits |
| **Mandatory Python LINT gate (per file-bridge-protocol.md)** | `ruff check` on TEMPLATE + 8 changed Python fixtures | `python -m ruff check groundtruth-kb/templates/hooks/spec-event-surfacer.py <8 fixtures>` | All checks passed |
| **Mandatory Python FORMAT gate (per file-bridge-protocol.md)** | `ruff format --check` on TEMPLATE + 8 changed Python fixtures (SEPARATE gate) | `python -m ruff format --check groundtruth-kb/templates/hooks/spec-event-surfacer.py <8 fixtures>` | 9 files already formatted |
| Template fix is format-only / byte-identical runtime | inspect `ruff format --check --diff` before fix | shows 2-line→1-line collapse of `EVENT_FORMAT` implicit-concat; no semantic change | confirmed pre-fix |
| Diff scope = expected inventory | `git diff --name-only` | 11 dual-agent + 2 local-only + 1 template = **14** paths total | exact match |
| No secret leak | DELIB-0687 canonical pattern scan over 14 diff files | 0 hits | clean |
| No unmasked dynamic-field leak | timestamp/session-id/uuid/sha scan over diff lines | 0 hits | clean (post `created_at` revert) |
| Mutation stays within PAUTH envelope | mutation classes used: `source` (template) + `test_fixture_update` (fixtures); both in `PAUTH-WI-4225-REGISTRY-SCAFFOLD-FIXTURE-DRIFT-001` `allowed_mutation_classes` | verified pre-impl | within envelope |

## Risk / Rollback

Low. Two-mutation scope: a format-only template edit (byte-identical runtime
value; the formatter's own output) + golden-fixture regen (no source-behavior
change). Both within `PAUTH-WI-4225-REGISTRY-SCAFFOLD-FIXTURE-DRIFT-001`'s
`allowed_mutation_classes`. No new capability surface, no KB mutation. The
template fix is reversible by `git revert`; the regen is reversible by
`git checkout` on `scaffold_golden/`. The WI-4279 precondition has already
cleared and committed.

## Recommended Commit Type

`test` — primary intent is bringing 3 byte-equality fixture tests to green;
the accompanying 1-line template format-fix is byte-equivalent at runtime
(no behavior change) and is bundled here only because the regenerated fixture
inherits its bytes from the template, so they MUST land together to satisfy
both the byte-equality and the `ruff format --check` gates simultaneously.
Commit scope: the 14 mutated files + this bridge report's audit chain. No
other working-tree changes staged.

## Bridge Filing (INDEX-Canonical)

Filed under `bridge/` as `REVISED: bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-007.md`
at the top of the existing document version list in `bridge/INDEX.md`;
append-only — NEW -005, NO-GO -006 and the rest preserved. `bridge/INDEX.md`
remains canonical per `GOV-FILE-BRIDGE-AUTHORITY-001`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
