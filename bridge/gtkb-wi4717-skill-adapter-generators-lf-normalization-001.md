NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 3972336c-f3d6-47b7-bc56-051c146e2f7c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude interactive Prime Builder auto-process

# Implementation Proposal: WI-4717 normalize skill-adapter generators to LF (antigravity + api)

Document: gtkb-wi4717-skill-adapter-generators-lf-normalization
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Project: PROJECT-GTKB-SKILL-MODERNIZATION
Work Item: WI-4717
Project Authorization: PAUTH-PROJECT-GTKB-SKILL-MODERNIZATION-WI-4717-ADAPTER-GENERATOR-LF-NORMALIZATION

target_paths: ["scripts/generate_antigravity_skill_adapters.py", "scripts/generate_api_skill_adapters.py", "platform_tests/scripts/test_generate_antigravity_skill_adapters.py", "platform_tests/scripts/test_generate_api_skill_adapters.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py"]

## Summary

The skill-adapter generators write generated adapters/manifests/registry via
`path.write_text(content, encoding="utf-8")`. With the default `newline=None`,
`Path.write_text` translates `\n` to `os.linesep` (`\r\n`) on Windows, so every
generated line gets a trailing CR. `git diff --check` then flags trailing CR on
every generated line, repeatedly blocking the VERIFIED commit-finalization gate
for any adapter-touching bridge work (observed across WI-4237). The fix is to
write with explicit `newline="\n"` (LF) at every generator write site and guard
generated content against trailing whitespace, with per-generator regression
tests asserting no CR bytes in the generated output.

### Scope correction vs the WI-4717 description (verified live)

The WI-4717 description states all three generators emit CRLF. Live inspection
shows that is now partially stale: `scripts/generate_codex_skill_adapters.py`
ALREADY writes LF — both its write sites use `write_text(..., newline="\n")`
(`_write_if_changed` and `update_registry`). The two generators that still emit
platform-default line endings are:

- `scripts/generate_antigravity_skill_adapters.py` — `update_registry` write
  (currently around line 243) uses `write_text(updated, encoding="utf-8")` with
  no `newline`.
- `scripts/generate_api_skill_adapters.py` — its `_write_if_changed` (currently
  around line 203) uses `write_text(content, encoding="utf-8")` with no
  `newline`.

This proposal therefore scopes the SOURCE fix to the two still-defective
generators (antigravity, api) and audits each for all write sites; the codex
generator source is already correct and is NOT in the source target set. All
three generators' TEST files are in scope so each gets a no-CR-bytes regression
guard (the codex generator gets the guard test even though its source is already
correct), satisfying the WI acceptance "per-generator no-CR-bytes tests green."
The earlier concurrent codex-only attempt referenced in the WI (2026-06-21,
reverted) left no working-tree residue; the three generators are git-clean at the
current commit.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — this work removes a recurring blocker of the
  VERIFIED commit-finalization gate (`git diff --check` failing on trailing CR);
  this proposal is also a bridge artifact under the canonical append-only
  numbered-file chain.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites
  every relevant governing specification and derives its tests from them.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the verification plan maps
  each behavioral clause to an executed test before VERIFIED.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — all touched paths are GT-KB platform
  source/tests in-root under `E:\GT-KB`; no out-of-root dependency.
- GOV-STANDING-BACKLOG-001 — WI-4717 is the canonical backlog record for this
  work. Its CLAUSE-VISIBILITY-BULK-OPS does not apply: this is a targeted
  two-generator defect fix, not a bulk backlog operation, so it produces no
  inventory artifact or review-packet and needs no bulk-action
  formal-artifact-approval packet.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — the LF requirement
  is enforced by per-generator no-CR-bytes regression tests.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — advisory; durable code + test artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory; adds code + tests and advances
  WI-4717 toward verified.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — advisory; work item + owner decision +
  spec linkage preserved as durable artifacts.

## Prior Deliberations

- DELIB-20266194 (owner_conversation / owner_decision) — owner AUQ 2026-06-26
  authorizing the NEW-implementation-proposal generation loop over the whole
  backlog (PB picks); basis for the covering PAUTH.
- WI-4237 — the adapter-touching bridge work whose VERIFIED commit was
  repeatedly blocked by the trailing-CR `git diff --check` failure this WI fixes.
- WI-4722 — the related CRLF re-do follow-on for the codex adapter generator;
  this proposal records that the codex generator source is now already LF.
- No prior deliberation rejects normalizing the generators to LF.

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001 already requires
a clean commit-finalization (the VERIFIED gate fails on `git diff --check`
violations); this WI makes the generators conform by default. No new or revised
requirement is needed; no formal spec/governance mutation is in scope.

## Design

Source fixes confined to the two still-defective generators, plus regression
tests across all three generators' test files:

1. `scripts/generate_antigravity_skill_adapters.py`: change every write site that
   currently omits `newline` to `write_text(..., encoding="utf-8", newline="\n")`
   (the `update_registry` write around line 243, and any adapter/manifest write
   sites local to this module), matching the codex generator's already-correct
   pattern.

2. `scripts/generate_api_skill_adapters.py`: same change to every write site
   (the `_write_if_changed` write around line 203 and any registry/manifest write
   sites).

3. Trailing-whitespace guard: ensure rendered content has no per-line trailing
   whitespace before writing (so `git diff --check` is clean on both CR and
   trailing-whitespace grounds). Implemented as a small normalization in the
   shared render/write path of the two generators.

4. Regression tests (one per generator test file): run the generator into a temp
   project root and assert the generated adapters/manifest/registry contain no
   `\r` (CR) bytes and no trailing whitespace before newlines. The existing
   `test_codex_and_antigravity_registry_updates_converge` convergence test must
   remain green.

No change to the bridge gates, the codex generator source, or any
governed-record/narrative artifact is in scope.

## Test Plan (spec-to-test mapping)

| Specification clause | Test | File |
|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 (antigravity generated output has no CR bytes / trailing whitespace) | test_antigravity_generated_output_is_lf_no_trailing_ws | platform_tests/scripts/test_generate_antigravity_skill_adapters.py |
| GOV-FILE-BRIDGE-AUTHORITY-001 (api generated output has no CR bytes / trailing whitespace) | test_api_generated_output_is_lf_no_trailing_ws | platform_tests/scripts/test_generate_api_skill_adapters.py |
| GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 (codex generated output has no CR bytes — guard for the already-fixed generator) | test_codex_generated_output_is_lf_no_trailing_ws | platform_tests/scripts/test_generate_codex_skill_adapters.py |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (codex/antigravity registry updates still converge after the LF change) | test_codex_and_antigravity_registry_updates_converge (existing; must continue to pass) | platform_tests/scripts/test_generate_antigravity_skill_adapters.py |

Commands (run against changed files before the post-implementation report):

```text
python -m pytest platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py platform_tests/scripts/test_generate_api_skill_adapters.py -q --tb=short
python -m ruff check scripts/generate_antigravity_skill_adapters.py scripts/generate_api_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py platform_tests/scripts/test_generate_api_skill_adapters.py platform_tests/scripts/test_generate_codex_skill_adapters.py
python -m ruff format --check scripts/generate_antigravity_skill_adapters.py scripts/generate_api_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py platform_tests/scripts/test_generate_api_skill_adapters.py platform_tests/scripts/test_generate_codex_skill_adapters.py
```

## Risk / Rollback

- Risk: changing write newline could perturb the convergence between the codex
  and antigravity registries. Mitigation: both generators end up emitting LF
  (codex already does); the convergence test is required to stay green and is in
  the test command set.
- Risk: a trailing-whitespace guard could alter intended content. Mitigation: the
  guard strips only per-line trailing whitespace before the newline, which
  `git diff --check` would flag anyway; tests assert the generated content is
  byte-clean.
- Rollback: changes are confined to two generator modules and three test files;
  reverting them restores prior behavior. No schema, governed-record, or
  narrative change is involved.

## Bridge Filing Discipline

This proposal is filed as the next numbered bridge file
(`bridge/gtkb-wi4717-skill-adapter-generators-lf-normalization-001.md`) under the
canonical append-only numbered-file chain; revisions and verdicts are added as
new numbered files so the chain remains the canonical audit trail per
GOV-FILE-BRIDGE-AUTHORITY-001.

## Owner Decisions / Input

- DELIB-20266194 — owner AUQ (2026-06-26) authorized the NEW-implementation-proposal
  generation loop over the whole backlog (PB picks), under which WI-4717 was
  re-homed to the active PROJECT-GTKB-SKILL-MODERNIZATION and its covering PAUTH
  (PAUTH-PROJECT-GTKB-SKILL-MODERNIZATION-WI-4717-ADAPTER-GENERATOR-LF-NORMALIZATION;
  allowed mutation classes source + test_addition; linked spec
  GOV-FILE-BRIDGE-AUTHORITY-001) was minted. No further owner decision is
  required to review this proposal.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
