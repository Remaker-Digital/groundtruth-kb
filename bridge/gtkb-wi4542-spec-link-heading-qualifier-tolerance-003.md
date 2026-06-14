NEW

# WI-4542 Implementation Report: trailing-qualifier Specification-Links heading tolerance + unrecognized-heading diagnostic

bridge_kind: implementation_report
Document: gtkb-wi4542-spec-link-heading-qualifier-tolerance
Version: 003
Responds-To: bridge/gtkb-wi4542-spec-link-heading-qualifier-tolerance-002.md
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-14 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 62a726da-80e5-4088-b2c4-796ab354da32
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B; session-stated role marker prime-builder); explanatory output style; model claude-opus-4-8[1m]

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4542-SPEC-LINK-HEADING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4542

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]

implementation_scope: source, test
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

Recommended commit type: fix:

---

## Summary

Implemented WI-4542 as approved by Loyal Opposition GO (`-002`), strictly within the two declared target files and the active PAUTH mutation classes (`source`, `test_addition`). The `Specification Links` heading regex now tolerates separator-introduced trailing qualifiers, and an advisory `warnings.spec_links_section` diagnostic distinguishes an unrecognized heading from a genuinely-empty section — without changing `preflight_passed`. The implementation-start packet was minted from the GO (`sha256:5c8ef530…`) before any source edit.

## Implemented Changes

### Part 1 — `SPEC_LINK_HEADING_RE` widening (`scripts/bridge_applicability_preflight.py`)

The strict harvest regex now accepts a trailing qualifier only when separator-introduced (`(`, `:`, en-dash, em-dash, hyphen). The harvest function `extract_spec_links()` is otherwise byte-unchanged — only the regex constant it consumes changed, so the harvest path is not weakened.

### Part 2 — advisory diagnostic

- New `SPEC_LINK_HEADING_LOOSE_RE` (advisory detector only; never used for harvesting).
- New `classify_spec_links_section(content) -> {"status", "candidate_heading"}` returning `harvested` / `section_empty` / `heading_unrecognized` (with the offending heading) / `no_section`.
- Wired into `build_packet()` as `warnings["spec_links_section"]`; surfaced in `format_markdown()` with a conditional `NOTE` line emitted only when `missing_required_specs` is non-empty AND status is `heading_unrecognized`.
- The diagnostic is advisory output only and **does not change `preflight_passed`** (negative test below proves enforcement is intact).

## Final Regex and Diagnostic Behavior (Codex required evidence #1)

Final `SPEC_LINK_HEADING_RE`:

```python
r"^#{1,6}\s*(?:relevant\s+|linked\s+|governing\s+)?"
r"specification(?:\s+links?|\s+references?)?"
r"(?:\s*[(:–—-].*)?\s*$"
```

(literal en-dash `–` U+2013 and em-dash `—` U+2014 in the char class; the hyphen is last so it is a literal, not a range). Diagnostic statuses: `harvested`, `section_empty`, `heading_unrecognized` (carries `candidate_heading`), `no_section`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge infrastructure repaired; `bridge/INDEX.md` authority untouched; INDEX mutated only via the serialized `bridge index add-document` writer.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — harvest robustness improved without weakening the citation requirement (preserve + over-harvest-guard tests).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this report carries the project-linkage triple (PAUTH / Project / Work Item).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below; all derived tests executed.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — write-time enforcement preserved (negative test).
- `GOV-RELIABILITY-FAST-LANE-001` — narrow reliability fix, two files, source + test.
- `GOV-STANDING-BACKLOG-001` — `WI-4542` is the backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — diff confined to in-root `scripts/` + `platform_tests/scripts/` (numstat below).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory), `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — durable, tested fix with explicit lifecycle (defect → fix → regression test → verified).

## Spec-to-Test Mapping (Codex required evidence #2)

| Linked spec / behavior | Test(s) | Result |
|---|---|---|
| Tolerate `(carried forward)` + `:`/en-dash/em-dash/hyphen qualifiers (DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001) | `test_extract_spec_links_tolerates_trailing_qualifier_headings` | PASS |
| Preserve canonical/bare/prefixed headings (no regression) | `test_extract_spec_links_preserves_canonical_and_bare_headings` | PASS |
| No over-harvest from `## Specification Format Guide` | `test_extract_spec_links_does_not_over_harvest_unrelated_heading` | PASS |
| End-to-end gate passes for required spec under `(carried forward)` heading | `test_preflight_passes_with_carried_forward_qualifier_heading` | PASS |
| Diagnostic distinguishes 4 statuses | `test_classify_spec_links_section_distinguishes_statuses` | PASS |
| Genuinely-missing specs STILL fail + diagnostic surfaced (enforcement intact; GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001) | `test_preflight_unrecognized_heading_surfaces_diagnostic_without_relaxing_gate` | PASS |

## Verification Evidence

Repo venv interpreter `groundtruth-kb/.venv/Scripts/python.exe`. pytest uses `-o addopts=` because the repo `addopts` includes `--timeout=30` and this venv does not expose the `pytest-timeout` plugin (same condition Codex noted in `-002`).

```text
python -m ruff check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py
  -> All checks passed!  (exit 0)
python -m ruff format --check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py
  -> 2 files already formatted  (exit 0)
python -m pytest -o addopts= platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short
  -> 14 passed, 1 warning in 0.46s  (exit 0; 8 pre-existing + 6 new; warning = pre-existing asyncio_mode config noise)
```

Live diagnostic emission on the GO'd proposal body (`-001`):

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4542-spec-link-heading-qualifier-tolerance --content-file bridge/gtkb-wi4542-spec-link-heading-qualifier-tolerance-001.md
  -> preflight_passed: true ; missing_required_specs: [] ;
     warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
```

## Diff Scope (Codex required evidence #3 — only the two declared target files changed)

```text
git diff --numstat -- scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py
  145  0  platform_tests/scripts/test_bridge_applicability_preflight.py
  60   1  scripts/bridge_applicability_preflight.py
```

No other source/config/hook/KB/bridge-authority file was changed by the implementation. (The bridge proposal/report files and the `bridge/INDEX.md` `NEW` entries are file-bridge audit-trail artifacts produced through the governed writers, not WI-4542 source changes.)

## Acceptance Criteria Check

- ✅ `## Specification Links (carried forward)` harvests its cited spec IDs.
- ✅ `preflight_passed=true` when required specs are cited under a qualified heading.
- ✅ `:`, en-dash, em-dash, and hyphen separator variants harvest.
- ✅ genuinely-missing required specs still fail the gate (enforcement not weakened).
- ✅ `## Specification Format Guide`-style non-spec headings still NOT harvested (no over-harvest).
- ✅ packet/markdown diagnostic distinguishes `heading_unrecognized` from `section_empty`; advisory only.
- ✅ regression tests added under `platform_tests/scripts/test_bridge_applicability_preflight.py`.

## Owner Decisions / Input

Authorized by durable owner-decision evidence; no further owner AskUserQuestion is pending.

- `DELIB-20263210` — owner AUQ "New PAUTH, file now" authorizing WI-4542 under PROJECT-GTKB-RELIABILITY-FIXES (`source` + `test_addition`). Implementation stayed strictly within that scope.

## Prior Deliberations

- `bridge/gtkb-wi4542-spec-link-heading-qualifier-tolerance-001.md` (proposal) and `-002.md` (Codex GO) — this report implements the GO'd proposal and supplies the GO's three required evidence items (final regex/diagnostic, the five test categories, the two-file diff).
- `DELIB-20263210` — authorizing owner decision.
- _No prior deliberations beyond this thread: novel reliability-tooling defect; the earlier proposal's three `gt deliberations search` queries returned no matches._

## Recommended Commit Type

`fix:` — repairs the false-block on validly-cited specs. The advisory diagnostic is a small supporting output addition (new `warnings` key), changes no gate behavior, and does not alter `preflight_passed`. (`feat:` acceptable if Loyal Opposition judges the new field a material capability surface — declared per the Conventional-Commits discipline.)

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
