NEW

# GTKB-GOV Proposal Standards — Slice 1 Post-Implementation Report (body-status-token enforcement)

bridge_kind: implementation_report
Document: gtkb-gov-proposal-standards-slice1
Version: 026
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-06-01T16-20-00Z-prime-builder-s382
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory; mode=auto

Project Authorization: PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICES-1-4
Project: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS
Work Item: GTKB-GOV-PROPOSAL-STANDARDS

target_paths: ["groundtruth-kb/templates/hooks/bridge-compliance-gate.py", ".claude/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py", "platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py", "platform_tests/hooks/test_bridge_compliance_gate_w4_calibration.py", ".claude/rules/file-bridge-protocol.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Implements: GO at `bridge/gtkb-gov-proposal-standards-slice1-025.md` (REVISED-1 `-024`).

---

## Summary

Implemented the body-status-token first-line BLOCK across the full 6-file scope
approved at `-025`. Versioned bridge files (`bridge/<slug>-NNN.md`) must now
begin with a canonical status token (`NEW`/`REVISED`/`GO`/`NO-GO`/`VERIFIED`/
`ADVISORY`/`WITHDRAWN`) on the first non-blank line; heading-first new-file
Writes are hard-blocked; existing non-canonical files are grandfathered; the
rule fires only on `Write` (full content). The rule landed in the framework
template and was re-activated byte-for-byte to the active hook, with a focused
12-test regression suite, the fixture updates the rule necessitated, and the
rule documentation.

All four `-025` Conditions For Implementation are satisfied (fresh
implementation-start packet created; narrative-artifact packet generated for
the rule-file edit; executed evidence for the expanded test surface + ruff +
hash equality below; all evidence is from the final implemented tree, no stale
pre-GO claims).

## Files Changed (6)

1. **`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`** — added
   `_first_line_is_recognized_status`, `_ondisk_first_nonblank_line`,
   `_body_status_token_violation` helpers and an early deny branch at the top of
   the bridge-markdown block in `_deny_reason_for_content`. This is the
   canonical framework source.
2. **`.claude/hooks/bridge-compliance-gate.py`** — re-activated byte-for-byte
   from the template (identical content; hash equality confirmed below).
3. **`platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py`** —
   new 12-test regression suite.
4. **`platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`** —
   2 Specification-Links calibration fixtures moved to non-versioned bridge
   paths (see "Implementation Deviation" below).
5. **`platform_tests/hooks/test_bridge_compliance_gate_w4_calibration.py`** —
   4 Specification-Links calibration fixtures moved to non-versioned bridge
   paths; added an explanatory rationale comment.
6. **`.claude/rules/file-bridge-protocol.md`** — new "## Body Status-Token Rule"
   subsection (after `## Statuses`). Written under the narrative-artifact
   approval packet at
   `.groundtruth/formal-artifact-approvals/2026-06-01-file-bridge-protocol-body-status-token-rule.json`
   (`full_content_sha256` = `146b7382fe86d7f132aacc5e54ebe9363410665d7e82e37d48c22c6a3826c9f8`;
   on-disk LF-normalized content matches). The subsection makes `WITHDRAWN`
   acceptance explicit per the `-023` non-blocking note.

## Implementation Deviation (from `-024` plan; transparency per `-025` condition 4)

The `-024` proposal planned to "prepend canonical status tokens to the
heading-first fixtures." During implementation this proved incompatible with the
PASS/ASK calibration fixtures: prepending `NEW` subjects a fixture to the
author-metadata gate, the project-linkage gate, AND the pending-applicability-
preflight gate (all keyed on `first_line in {NEW, REVISED}`). The preflight
hard-denies a minimal calibration fixture whose fake bridge id is absent from
`bridge/INDEX.md`, so the PASS/ASK tests could not be made to pass by a status
prepend.

Resolution: the Specification-Links calibration fixtures use **non-versioned**
bridge paths (no `-NNN` suffix). The body-status-token rule is versioned-only,
so it correctly exempts them, while `_is_bridge_markdown_file` still routes them
through the Specification-Links logic under test. This is a cleaner isolation
(it tests one clause without the status-keyed gates interfering), and the
versioned-heading-first BLOCK behavior is covered directly by the new
`test_bridge_compliance_gate_body_status_token.py` suite. The DENY fixtures that
deny on Specification Links before reaching the later gates were left unchanged
in intent; all six now exercise their intended clause. No production behavior
differs from the `-024`/`-022` design; only the test-fixture mechanic changed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 (verified) — the rule strengthens the
  self-describing integrity of versioned bridge files the INDEX tracks.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified).
- `GOV-STANDING-BACKLOG-001` v5 (verified).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (in-root clause; all 6 paths in-root).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory; carried forward).

## Prior Deliberations

- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` (v1) — owner S382 decision.
- `bridge/gtkb-gov-proposal-standards-slice1-025.md` — Codex GO on `-024`
  (4 conditions, all satisfied here).
- `bridge/gtkb-gov-proposal-standards-slice1-023.md` — Codex GO on `-022`
  (WITHDRAWN-explicitness non-blocking note, incorporated).

## Owner Decisions / Input

Authorized by the S382 AUQ decision in
`DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` ("Implement the one real gap")
under `PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICES-1-4` (active; mutation
classes `hook_upgrade`, `test_addition`, `governance_doc_update`). The protected
narrative edit to `.claude/rules/file-bridge-protocol.md` carries its own
narrative-artifact approval packet (path + hash above). No new owner decision
is required.

## Spec-Derived Verification Plan (executed; final-tree evidence)

| Specification | Acceptance criterion | Test / command | Result |
|---|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Versioned bridge files self-describe with a line-1 status token; heading-first new files blocked | `test_new_file_heading_first_blocked`, `test_deny_reason_blocks_heading_first_new_file`, `test_each_canonical_token_accepted`, `test_recognized_status_includes_withdrawn` | PASS (12/12 suite) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Grandfather + overwrite + Edit-skip + exemption branches covered | `test_existing_noncanonical_file_grandfathered`, `test_overwrite_canonical_to_noncanonical_blocked`, `test_edit_tool_empty_content_skipped`, `test_non_versioned_bridge_md_skipped`, `test_index_md_not_a_versioned_file` | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (template parity) | Active hook byte-identical to template | `test_hook_matches_template_or_documented_divergence` + sha256 comparison | PASS; both `72eec18d…` |
| existing gate clauses (no regression) | Spec-links / author-metadata / project-metadata / advisory / w4 calibration unaffected | full `bridge_compliance`/`bridge_author` family | 102 passed |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | all touched paths in-root | path inspection | PASS |

### Executed commands and observed results

New regression suite:

```text
uv run --with pytest --with pytest-timeout python -m pytest platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py -q --no-header
12 passed, 1 warning
```

Full gate family (regression check; includes the new suite, the template-match
test, and all updated fixtures):

```text
uv run --with pytest --with pytest-timeout python -m pytest platform_tests/hooks/ -k "bridge_compliance or bridge_author" -q --no-header
102 passed, 281 deselected, 1 warning
```

Template-match guard test specifically:

```text
uv run --with pytest --with pytest-timeout python -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py::test_hook_matches_template_or_documented_divergence -q --no-header
1 passed, 1 warning
```

Active-hook / template hash equality:

```text
active   72eec18d04005de15462da13518d34cbc9bcc031e23f0808891dfeace2d8ff9d
template 72eec18d04005de15462da13518d34cbc9bcc031e23f0808891dfeace2d8ff9d
MATCH
```

Ruff lint (5 changed Python files):

```text
uv run --with ruff python -m ruff check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/hooks/test_bridge_compliance_gate_w4_calibration.py
All checks passed!
```

Ruff format check:

```text
uv run --with ruff python -m ruff format --check <same 5 files>
5 files already formatted
```

## Recommended Commit Type

`feat:` — adds a new bridge compliance-gate enforcement capability
(body-status-token BLOCK) with template sync, a regression suite, fixture
updates, and rule documentation.

## Acceptance Criteria Check

- [x] Body-status-token BLOCK implemented in the template and re-activated
      byte-for-byte to the active hook (hash MATCH; template-match test passes).
- [x] New 12-test suite passes; full gate family 102/102 (no regression).
- [x] Rule documented in `file-bridge-protocol.md` under a narrative-artifact
      approval packet (hash MATCH); `WITHDRAWN` acceptance explicit.
- [x] ruff lint + format clean on all 5 changed Python files.
- [x] All 6 target paths in-root and within the GO'd `-024`/`-025` target_paths.
- [x] `-025` conditions 1-4 satisfied (packet, narrative packet, executed
      evidence + hash, final-tree results).

## Decision Needed From Owner

None. Standing PAUTH + S382 AUQ.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
