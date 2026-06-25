NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: claude-prime-interactive-obsolete-ref-purge-wi4799-session-26b13c51
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; Prime Builder role (harness B); explanatory output style; obsolete-reference-purge drive; init keyword ::init gtkb pb
author_metadata_source: interactive-prime-session

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4799

# INDEX.md Residue Strip — Skill-Docs (S3) Tranche (WI-4799)

Document: gtkb-index-md-strip-skill-docs
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4799
Recommended commit type: fix

## Summary

Third strip tranche (S3) under the GO-terminal classification contract
(`gtkb-index-md-classified-inventory`, GO `-002`). Per-surface verification of the S3
surfaces found the **skill-doc and template strip already complete**; the only remaining
residue is **two stale assertions in `groundtruth-kb/tests/test_cli.py`** that still assert
the scaffold output *contains* the retired `bridge/INDEX.md` aggregate. Both are currently
**failing**. This tranche flips them to assert the current no-INDEX behavior. It is a `fix`
(repairs failing tests), not a feature.

## Scope Correction — the S3 "strip skill-docs/templates" framing is already satisfied

**Surfaced for LO review.** The classification contract's S3 (WI-4799) anticipated stripping
`.claude/skills/bridge-reconciliation/SKILL.md` + `.codex`/`.cursor`/`.agent` mirrors +
`groundtruth-kb/templates/skills/bridge/SKILL.md`. Fresh canonical-state verification this
session shows that strip is **already done**:

- **All four `bridge-reconciliation/SKILL.md` mirrors** (`.claude`, `.codex`, `.cursor`,
  `.agent`) carry `bridge/INDEX.md` only inside **guard-aware** notes ("Do **not** read
  `bridge/INDEX.md` as live state"; "Never treat `bridge/INDEX.md` …"). Per the contract's
  K2 / "beyond the guard-aware 'do not recreate' note" rule, these are **KEEP**, not STRIP.
- **`groundtruth-kb/templates/skills/`**: zero `bridge/INDEX.md` occurrences.
- **Live scaffold templates** `groundtruth-kb/templates/BRIDGE-INVENTORY.md` and
  `bridge-os-poller-setup-prompt.md`: zero `bridge/INDEX.md` (the latter is now a
  `DEPRECATED — Smart Poller Retired` notice). Already stripped by prior work.

The **only** load-bearing residue of the S3 surface is the two **stale tests** that the S2
tranche (`gtkb-index-md-strip-tests`, WI-4798) explicitly deferred here: `test_cli.py` asserts
the *scaffolded* `BRIDGE-INVENTORY.md` and `bridge-os-poller-setup-prompt.md` still contain
`bridge/INDEX.md`. Because the templates were already stripped, those assertions now fail
(`pytest groundtruth-kb/tests/test_cli.py` → `…FF…`, 2 failed / 34 passed). LO: please confirm
this scope (residue = the 2 deferred stale tests; skill-docs + templates already compliant).

## Per-Surface Triage (deterministic, per the contract's decision rule)

**STRIP / UPDATE (2 assertions, one file — `groundtruth-kb/tests/test_cli.py`):**

- `TestBootstrapDesktop::test_bootstrap_desktop_creates_scaffold` (L411):
  `assert "bridge/INDEX.md" in bridge_prompt` (bridge_prompt = `bridge-os-poller-setup-prompt.md`).
  **Currently failing** — the template is now the `DEPRECATED — Smart Poller Retired` notice.
  Update to `assert "bridge/INDEX.md" not in bridge_prompt` (the retired aggregate must not
  appear in the scaffold output).
- `TestBootstrapDesktop::test_project_init_dual_agent_uses_file_bridge_defaults` (L452):
  `assert "bridge/INDEX.md" in bridge_text` (bridge_text = `BRIDGE-INVENTORY.md`).
  **Currently failing.** Update to `assert "bridge/INDEX.md" not in bridge_text` — consistent
  with the adjacent retired-mechanism negative assertions at L453–L454 (`"gt bridge serve" not
  in`, `"groundtruth_kb.bridge.worker" not in`). The positive `in` assertion is simply a missed
  update from the `bridge/INDEX.md` retirement.

**KEEP — already compliant (no edit):** the four `bridge-reconciliation/SKILL.md` mirrors
(guard-aware notes), `groundtruth-kb/templates/skills/**`, and the already-stripped scaffold
templates.

**Out of scope (separate finding, NOT this tranche):** the scaffold still emits a
`bridge-os-poller-setup-prompt.md` whose content is now a `DEPRECATED — Smart Poller Retired`
notice. Continuing to scaffold a deprecated-poller artifact is a distinct obsolescence (the
OS/smart poller retirement, not the `bridge/INDEX.md` retirement) and is being captured as a
separate backlog candidate rather than folded into this `bridge/INDEX.md` tranche.

## Specification Links

- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` (v1, specified) — the S3 STRIP residue (the two
  stale bridge-index scaffold assertions) is removed.
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` (v1, specified) — these failing tests are the
  un-paired residue the obligation targets (a retirement that left stale assertions).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — links cited; verification derives.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the post-impl report runs the updated
  tests green; mapping below.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed as the next numbered bridge file in the append-only
  versioned chain; the updated tests assert the canonical TAFE/dispatcher authority model
  (no retired aggregate) this spec defines.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the updated tests assert the current scaffold output,
  not the retired aggregate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (CLAUSE-IN-ROOT) — the target path is in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — lifecycle artifact of the retirement trigger.

## Prior Deliberations

- `gtkb-index-md-classified-inventory` (GO `-002`, terminal) — the STRIP/KEEP/QUARANTINE
  contract; S3 is the skill-docs surface; this tranche applies its decision rule and reports
  the surface already compliant except the deferred tests.
- `gtkb-index-md-strip-tests` (WI-4798, VERIFIED-pending `-003`) — the S2 tranche that
  explicitly deferred the `test_cli.py` template assertions to this S3/WI-4799 thread.
- `gtkb-index-md-strip-docs` (WI-4797, VERIFIED) — the S1 docs peer.
- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` (v1) — owner authorization (AUQ Q1
  "residue only, keep guards").

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements are the GO-terminal classification
contract plus the methodology ADR/DCL. No new requirement.

## Target Paths

target_paths: ["groundtruth-kb/tests/test_cli.py"]

## Verification Plan (Specification-Derived)

### Specification-Derived Verification — Spec-to-Test Mapping

| Linked spec / clause | Spec-to-test mapping | Command |
|----------------------|----------------------|---------|
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` (STRIP residue removed) | the two updated assertions assert `bridge/INDEX.md` is absent from the scaffold outputs and pass | `python -m pytest groundtruth-kb/tests/test_cli.py -q --tb=short` |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` (retirement residue repaired) | `test_cli.py` goes from `…FF…` (2 failed) to all-passing | same pytest run |
| KEEP intact (skill-docs + templates untouched) | the diff is limited to `groundtruth-kb/tests/test_cli.py`; the four SKILL.md mirrors and templates are unchanged | `git diff --name-only` + grep re-scan |
| Code quality (lint + format, separate gates) | the changed test passes both | `python -m ruff check groundtruth-kb/tests/test_cli.py` ; `python -m ruff format --check groundtruth-kb/tests/test_cli.py` |

## Risk / Rollback

- **Risk: over-strip / change unrelated assertions.** Mitigated — only two assertions in one
  file change; both flip a stale `in` to `not in` matching adjacent retired-mechanism patterns.
- **Risk: the scaffold legitimately should still emit `bridge/INDEX.md`.** Refuted by canonical
  state — the templates were already stripped and the bridge authority migrated off the
  aggregate (`GOV-FILE-BRIDGE-AUTHORITY-001`); the `not in` assertion is the correct current
  contract.
- **Rollback:** single-file change; revert restores the prior (failing) state. No other coupling.

## Owner Decisions / Input

Proceeds under the governed PAUTH; cites the AUQ-only rule.

- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` (2026-06-24) — owner directive (AUQ Q1).
- AskUserQuestion (2026-06-25, this session) — owner selected "Continue purge drive (WI-4799)"
  under `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25`.

One judgment is surfaced for LO review: confirmation that the S3 residue is correctly reduced
to the two deferred stale `test_cli.py` assertions (skill-docs + templates already compliant),
and that flipping the assertions to `not in` (vs. removing them) is the preferred disposition.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
