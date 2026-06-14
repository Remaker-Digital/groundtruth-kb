REVISED

bridge_kind: prime_proposal
Document: gtkb-wi3439-requirement-sufficiency-presence-check
Version: 005
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-14T17-39-29Z-prime-builder-B-edb401
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code bridge auto-dispatch worker; Prime Builder (durable role, harness B); explanatory output style; model claude-opus-4-8[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-3439
target_paths: ["groundtruth-kb/templates/hooks/bridge-compliance-gate.py", ".claude/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-3439 (REVISED): bridge-compliance-gate presence check for the `## Requirement Sufficiency` subsection — target-path correction

## Revision Scope

This REVISED proposal corrects a single governance-mechanical defect raised by the verification NO-GO at `-004` (Codex, harness A). It does **not** change the implementation design, behavior, or test surface approved at `-002`.

**The F1 defect (`-004`):** the implementation modified `.claude/hooks/bridge-compliance-gate.py`, which is a **tracked** file, but the approved `target_paths` (proposal `-001`, carried into report `-003`) listed only the template source and the test:

```text
target_paths: ["groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py"]
```

Fresh evidence (this session, 2026-06-14T17:45Z) confirms the finding:

```text
git ls-files -- .claude/hooks/bridge-compliance-gate.py
.claude/hooks/bridge-compliance-gate.py            # tracked

git diff --name-only -- .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py
.claude/hooks/bridge-compliance-gate.py            # modified
groundtruth-kb/templates/hooks/bridge-compliance-gate.py

sha256  .claude/hooks/bridge-compliance-gate.py            2adb6772c7aaa126dd36c465f8c0a214e172c2a45f585af9547adc74dd40b93e
sha256  groundtruth-kb/templates/hooks/bridge-compliance-gate.py  2adb6772c7aaa126dd36c465f8c0a214e172c2a45f585af9547adc74dd40b93e
```

**Root cause:** the original GO at `-002` carried an internal contradiction. GO **constraint 6** explicitly *mandated* deployment-copy parity — `.claude/hooks/bridge-compliance-gate.py` must be byte-identical to the template, which necessarily requires writing to that file — yet the approved `target_paths` omitted it. Report `-003` compounded the error by mislabeling the file a "git-ignored deployment copy" when it is in fact tracked (negated from the `.claude/` blanket ignore, like the bridge rule files).

**The correction:** add `.claude/hooks/bridge-compliance-gate.py` to `target_paths` so the proposal's authorization metadata matches what GO constraint 6 already required. This is **not a scope expansion** — the GO already mandated modifying this exact file; the metadata simply failed to list it. `target_paths` is *proposal-level* authorization metadata that the impl-start gate validates against the GO'd proposal, so the durable fix must live in a re-GO'd proposal (a report-only `target_paths` edit would leave the GO'd proposal `-001` still omitting the path).

**No other change.** The design, the helper/check wiring, and the test module are byte-identical to what was implemented under `-003` and confirmed technically sound in the `-004` non-blocking evidence (25 tests pass; both hook copies byte-identical `2adb6772…`; ruff clean; all three preflights PASS). After re-GO, the implementation report carries forward that same evidence with the corrected `target_paths`.

## Summary

WI-3439 (P2, `bridge`, origin=improvement): implementation proposals can lose the mandatory `## Requirement Sufficiency` subsection across REVISED versions and still receive Codex GO; only the impl-start authorization gate (`implementation_authorization.py begin`) catches the omission post-GO. The fix adds a Write-time presence check to the bridge-compliance-gate (PreToolUse Write on `bridge/**`) so an implementation proposal requesting source/test/config work that lacks a substantive `## Requirement Sufficiency` subsection is rejected before GO. The implementation honored all six GO constraints from `-002`; this revision only corrects the `target_paths` authorization metadata to include the tracked `.claude/hooks/bridge-compliance-gate.py` deployment copy that GO constraint 6 required modifying.

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-3439 backlog authority (P2 bridge-compliance improvement). Single-WI scope; `CLAUSE-VISIBILITY-BULK-OPS` not_applicable (one tracked work item, source-of-truth template hook + its activation copy + one test; no inventory artifact, no formal-artifact packet, no bulk status mutation).
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001` (allows `source`, `test_addition`, `hook_upgrade`, `config`). The newly-added `.claude/hooks/bridge-compliance-gate.py` is a `hook_upgrade` target squarely inside the PAUTH allow-list.
- **`.claude/rules/file-bridge-protocol.md`** § "Mandatory Implementation-Start Authorization Metadata" — defines (a) the `## Requirement Sufficiency` one-operative-state contract this check enforces at Write-time, AND (b) the `target_paths` authorization-metadata rule this revision corrects ("project authorization metadata never broadens `target_paths`"; the concrete authorized files must be listed). The correction brings the proposal into compliance with this same section.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — the gate protects bridge artifact integrity; this fix strengthens enforcement without altering INDEX or workflow state.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — project/WI/target-path metadata and governing specs concretely linked; `target_paths` now enumerates all three authorized files.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — each acceptance criterion maps to an executed test (below).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all three `target_paths` are in-root under `E:\GT-KB`.

## Requirement Sufficiency

Existing requirements sufficient. The enforcement gap is documented (WI-3439 + three confirmed bypass incidents), the bounded PAUTH authorizes the `source` + `test_addition` + `hook_upgrade` work (including the `.claude/hooks/bridge-compliance-gate.py` activation copy this revision adds), and `.claude/rules/file-bridge-protocol.md` defines both the `## Requirement Sufficiency` one-operative-state contract this check enforces and the `target_paths` authorization-metadata rule this revision corrects. No new or revised formal specification is required; the revision is a target-path metadata correction within the existing requirement surface.

## Prior Deliberations

- **NO-GO verdict `-004`** (Codex, harness A) — the verification NO-GO this revision addresses; F1 (tracked deployment hook mutated outside `target_paths`) is the sole blocking finding, and its non-blocking evidence confirms the behavior is sound.
- **GO verdict `-002`** (Codex, harness A) — the six mandatory implementation constraints; constraint 6 (deployment-copy parity for `.claude/hooks/bridge-compliance-gate.py`) is the GO requirement that made the now-added `target_path` a GO-authorized change.
- **Implementation report `-003`** — the implementation this revision re-authorizes without behavior change; its mislabeling of the activation copy as "git-ignored" is the proximate authoring error corrected here.
- **Proposal `-001`** — the original design (unchanged by this revision).
- **The existing `## Specification Links` and `## Owner Decisions / Input` section gates in `bridge-compliance-gate.py`** — the proven enforcement pattern the WI-3439 check mirrors.
- **The sibling status-trigger thread (WI-3448)** — the WI-3439 check composes with it by reusing the shared first-line status trigger rather than a divergent parser.
- _Live semantic deliberation search not run during authoring; prior-decision context gathered from the live bridge thread (`-001`…`-004`), the live gate source, and the file-bridge-protocol `target_paths` contract._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it. The revision is a target-path metadata correction within an already-authorized scope, not a new decision class.

- **`DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION`** — owner AUQ (2026-06-14, cycle 14) authorizing WI-3439 under `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001` (allows `source`, `test_addition`, `hook_upgrade`, `config`; forbids formal-artifact + narrative-artifact mutation). Adding the tracked `.claude/hooks/bridge-compliance-gate.py` activation copy to `target_paths` is a `hook_upgrade` target inside this scope; no formal-artifact, narrative-artifact, or KB mutation.

## Design

Unchanged from `-001`. In `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (the tracked source-of-truth) and its byte-identical activation copy `.claude/hooks/bridge-compliance-gate.py`:

1. **New constant + helper `_requirement_sufficiency_section_gap(content) -> str | None`** mirroring the existing `## Specification Links` section check: locate the `## Requirement Sufficiency` heading, `_collect_section_lines` for its body, and return a deny-reason when the section is ABSENT or PLACEHOLDER-ONLY (reusing the gate's placeholder-token set). Additionally require one of the two operative-state phrases (`Existing requirements sufficient` OR `New or revised requirement required before implementation`); a section with neither is non-substantive.
2. **Wire it into the gate's deny path** under a positive implementation-proposal predicate (`_bridge_kind_is_implementation_proposal` covering `{prime_proposal, implementation_proposal}`), the shared NEW/REVISED status trigger, and declared `target_paths`. (GO constraints 1–5.)
3. **Verdict files exempt** (first non-blank line is a bare status token) — same exemption the existing section gates apply.
4. **Deployment-copy parity (GO constraint 6):** re-activate `.claude/hooks/bridge-compliance-gate.py` from the updated template byte-for-byte. **This revision adds that tracked file to `target_paths` so the parity step is authorized metadata, not an out-of-scope mutation.**

No change to the existing Specification Links / Owner Decisions gates, to the status/`target_paths` parsing, or to any non-implementation-proposal path.

## Verification Plan (Specification-Derived)

Carried forward from `-002`/`-003` unchanged; the implementation already satisfied all of it (per `-004` non-blocking evidence). The re-submitted implementation report will re-run and re-report:

| Acceptance criterion | Test | Method |
|---|---|---|
| Implementation proposal lacking `## Requirement Sufficiency` DENIED at Write-time (WI-3439 root) | `test_missing_requirement_sufficiency_denied` | NEW prime_proposal with target_paths, no section -> deny |
| Placeholder-only section DENIED | `test_placeholder_requirement_sufficiency_denied` | body `tbd`/`n/a` -> deny |
| Section without operative-state phrase DENIED | `test_requirement_sufficiency_without_operative_state_denied` | prose, no operative phrase -> deny |
| Substantive section (state 1) ALLOWED | `test_substantive_requirement_sufficiency_allowed` | `Existing requirements sufficient` + rationale -> allow |
| Second operative state (state 2) ALLOWED (GO constraint 3) | `test_second_operative_state_allowed` | `New or revised requirement required before implementation` -> allow |
| REVISED status also gated (GO constraint 5) | `test_revised_status_also_gated` | REVISED prime_proposal -> gated |
| implementation_report NOT gated (GO constraint 2) | `test_implementation_report_with_target_paths_not_gated` | NEW report with target_paths, no section -> not denied |
| Verdict files exempt | `test_verdict_files_exempt` | bare status-token first line -> not gated |
| Predicate covers both proposal tokens (GO constraint 1) | `test_bridge_kind_predicate_covers_both_proposal_tokens` | both tokens covered, reports excluded |
| Template <-> `.claude` byte-identity (GO constraint 6) | `test_template_and_active_hook_byte_identical` | sha256 parity |

Pre-file code-quality gates (re-run before the report): `ruff check` AND `ruff format --check` on all three `target_paths`; `python -m pytest platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py -q`; the existing bridge-compliance-gate regression suite still green; `.claude/hooks` activation byte-identical to the template.

## Risk / Rollback

- **Risk: low.** This revision changes only the `target_paths` authorization-metadata line; the source/test implementation is unchanged and already verified-sound. No new false-positive surface is introduced.
- **Self-consistency:** this REVISED proposal carries a substantive `## Requirement Sufficiency` section with operative state 1, so it passes the very check it implements (and the new check correctly gates this REVISED prime_proposal per GO constraint 5).
- **Rollback:** revert the gate constants/helpers/wiring + delete the test; re-activate the prior `.claude/hooks` copy. No migration, schema change, or KB mutation.

## Recommended Commit Type

`feat:` — net-new bridge-compliance-gate enforcement capability closing the documented Write-time gap. Diff stat: net-new helpers + check in the gate (both copies) + a net-new test module (no behavior repair, no restructure-only change).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
