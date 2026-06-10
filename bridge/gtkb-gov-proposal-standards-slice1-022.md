NEW

# GTKB-GOV Proposal Standards — Slice 1 In-Root Reimplementation (body-status-token enforcement)

bridge_kind: prime_proposal
Document: gtkb-gov-proposal-standards-slice1
Version: 022
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-06-01T13-40-00Z-prime-builder-s382
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory; mode=auto

Project Authorization: PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICES-1-4
Project: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS
Work Item: GTKB-GOV-PROPOSAL-STANDARDS

target_paths: [".claude/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py", ".claude/rules/file-bridge-protocol.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal closes out GTKB-GOV-PROPOSAL-STANDARDS Slice 1, which was
phantom-VERIFIED in the S317 INDEX reconciliation (commit `9b5c535b`). The
on-disk `-021` post-implementation report referenced a GO at `-020` that never
existed on disk or in git history, routed implementation to an external
`groundtruth-kb` checkout barred by the current root-boundary directive, and
edited `memory/work_list.md` (deleted at the S377 backlog-source-of-truth
migration). The thread therefore has no valid implementation and no live GO.

Investigation this session established that the **substance** of the original
Slice 1 contract is already delivered in-root by
`.claude/hooks/bridge-compliance-gate.py` (1082 lines, committed `dfd1c56b`),
which has hard-blocked this very session three times on genuine defects
(project-linkage metadata, author audit metadata, KB-mutation target_paths).
The gate, plus the Slice 2 test-claim re-run verifier and the Slice 3 work-item
collision gate, organically superseded the original `-021` design.

The owner (S382 AUQ, captured in `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE`)
chose to **implement the one genuinely-missing real-enforcement piece**: the
body-status-token first-line rule (original `-021` contract item 2). This
proposal adds that enforcement to the existing in-root gate, documents the rule
in `.claude/rules/file-bridge-protocol.md`, and records the supersession so the
phantom-VERIFIED history is closed honestly.

## Original `-021` Contract → Verified Current State

| # | Original `-021` adoption-contract item | Verified tree reality (2026-06-01) | Disposition |
|---|---|---|---|
| 1 | Two managed-hook event model (PreToolUse Write + PostToolUse Edit) | `bridge-compliance-gate.py` registered `PreToolUse` on Write/Edit (`.claude/settings.json:30`); only `Write` carries full `content` (`bridge-compliance-gate.py:1051`) | Functional equivalent present; no change |
| 2 | Body-status-token rule: versioned bridge file body must begin with a canonical status token; heading-first new-file Writes BLOCK; existing non-canonical files grandfathered | NOT enforced — `_first_nonblank_line` (lines 401/450/622/821) routes on the first line but never blocks a non-status first line on a NEW file | **THIS PROPOSAL implements it** |
| 3 | Post-impl discriminator (Test Evidence + executed pytest evidence) | `_has_spec_derived_verification` (line 468) blocks VERIFIED without spec links + spec-to-test heading + command evidence (line 837); Slice 2 verifier re-runs the claims | Delivered + exceeded; no change |
| 4 | `emit_block_post` output helper | Gate uses `emit_deny`/`emit_ask`/`emit_pass` (functional equivalent) | Superseded design detail; no change |
| 5 | Bypass env var + content marker + audit log | Not present — the current gate has no bypass | Intentionally dropped (no-bypass is stronger; owner rejected "verbatim" option) |
| 6 | Codex `.codex` fallback parity | `.codex/gtkb-hooks/bridge-compliance-gate.cmd` + `-apply-patch-adapter` + `-bash-adapter` registered in `.codex/hooks.json` | Delivered; no change |
| 7 | Zero shared-parser drift | Gate imports shared author-metadata/parse helpers read-only | Delivered; no change |

## Design — Body-Status-Token Rule

### Scope and trigger

The rule applies to **versioned bridge files** (`bridge/<slug>-NNN.md`,
matched by the existing `_extract_bridge_id_from_path`). `bridge/INDEX.md` is
excluded by the existing `_is_bridge_markdown_file`. Because the gate only
populates `content` for the `Write` tool (`bridge-compliance-gate.py:1051`;
`Edit` provides `old_string`/`new_string`, so `content==""` and the whole
content-check block is skipped), the rule fires only on `Write` of full file
content. Bridge files are append-only, so the rule's real effect is "a new
bridge-file Write must begin with a canonical status token."

### Canonical status tokens

`NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`, `ADVISORY`, `WITHDRAWN`. The
validity predicate mirrors the gate's EXISTING first-line recognition union so
the rule blocks exactly when downstream routing would fail to recognize a
status, and never false-blocks (it errs toward acceptance):

```python
def _first_line_is_recognized_status(first_line: str) -> bool:
    return (
        first_line == "ADVISORY"
        or first_line == "WITHDRAWN"
        or first_line in PENDING_PREFLIGHT_STATUSES  # {"NEW", "REVISED"}
        or first_line.startswith(("GO", "NO-GO", "VERIFIED"))
    )
```

### Grandfather semantics (per-file, faithful to `-021`)

```python
def _ondisk_first_nonblank_line(file_path: str) -> str | None:
    try:
        path = Path(file_path)
        if not path.is_file():
            return None
        with path.open("r", encoding="utf-8-sig") as handle:
            for raw in handle:
                stripped = raw.strip()
                if stripped:
                    return stripped
        return ""
    except OSError:
        return None


def _body_status_token_violation(file_path: str, content: str) -> bool:
    if _extract_bridge_id_from_path(file_path) is None:
        return False  # not a versioned bridge file
    if _first_line_is_recognized_status(_first_nonblank_line(content)):
        return False  # new content is canonical
    ondisk_first = _ondisk_first_nonblank_line(file_path)
    if ondisk_first is None:
        return True  # new file, non-canonical first line -> block
    if _first_line_is_recognized_status(ondisk_first):
        return True  # was canonical; overwrite must keep it canonical
    return False  # grandfathered: on-disk first line already non-canonical
```

Empirical basis for grandfathering: a scan of all 4725 versioned bridge files
found 1038 (22%) with non-canonical first lines, almost entirely closed legacy
threads (`agent-red-*`, `axe-core-*`). Because the rule fires only on Write and
bridge files are append-only, these historical files are never re-Written and
so are never blocked; the grandfather branch additionally protects the rare
legitimate full-overwrite of a pre-existing non-canonical file.

### Placement and message

The check is the FIRST test inside the existing
`if _is_bridge_markdown_file(file_path) and content:` block in
`_deny_reason_for_content` (before the ADVISORY check at line 822), because a
non-status first line makes the downstream routing unreliable:

```python
if _body_status_token_violation(file_path, content):
    return (
        "[Governance] Versioned bridge files (bridge/<slug>-NNN.md) must begin "
        "with a canonical status token on the first non-blank line: one of "
        "NEW, REVISED, GO, NO-GO, VERIFIED, ADVISORY, WITHDRAWN. The first "
        f"non-blank line was {_first_nonblank_line(content)!r}. Put the status "
        "token on line 1 (headings and prose follow it). Existing files with a "
        "non-canonical first line are grandfathered. (Hard-block per "
        "GTKB-GOV-PROPOSAL-STANDARDS Slice 1 body-status-token rule; see "
        ".claude/rules/file-bridge-protocol.md Body Status-Token Rule.)"
    )
```

A new module-level regex is NOT required — the predicate reuses the gate's
existing `PENDING_PREFLIGHT_STATUSES` constant and `_first_nonblank_line`
helper.

### Documentation

A new "## Body Status-Token Rule" subsection in
`.claude/rules/file-bridge-protocol.md` (after "## Statuses") states the rule
as a forward-looking MUST, names the canonical tokens, and notes the
grandfather clause. This edit is a protected narrative artifact and will be
made under a `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` at implementation time.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 (verified) — `bridge/INDEX.md` is the
  canonical workflow state; the body-status-token rule strengthens the
  self-describing integrity of the versioned files that the INDEX tracks.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified) —
  this proposal cites every governing spec here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified) — the test
  plan below derives tests from the rule's acceptance criteria.
- `GOV-STANDING-BACKLOG-001` v5 (verified) — Slice 1 (WI
  GTKB-GOV-PROPOSAL-STANDARDS) is an active member of
  PROJECT-GTKB-GOV-PROPOSAL-STANDARDS.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (in-root clause) — all touched
  paths are inside `E:\GT-KB`; this proposal explicitly drops the original
  `-021` routing to an external `groundtruth-kb` checkout.

How the tests derive from the specs: the rule operationalizes the
self-describing-file integrity property implied by GOV-FILE-BRIDGE-AUTHORITY-001
and the proposal-standards family; the test plan exercises every branch of
`_body_status_token_violation` (new-file block, grandfather, overwrite-keeps-
canonical, non-versioned skip, each canonical token accepted).

## Prior Deliberations

- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` (v1, this session) — owner
  S382 AUQ decisions authorizing this scope; records the corrected premise
  (the gate already exists in-tree) and the rejected alternatives
  (doc-only close; verbatim `-021` rebuild with bypass).
- `DELIB-1132` / `DELIB-2024` — archived bridge-thread harvest records for the
  original `gtkb-gov-proposal-standards-slice1` family (both empty-body
  harvest stubs reflecting INDEX state, not verification).
- `DELIB-0990`, `DELIB-0991`, `DELIB-0993` — proposal-standards-family review
  precedents requiring mechanical enforcement over optional diagnostics.
- S317 reconciliation commit `9b5c535b` — annotated the phantom-VERIFIED
  `-024` INDEX claim (annotation-only; no file restoration).

## Owner Decisions / Input

This proposal depends on owner approval, supplied via the S382 AskUserQuestion
decisions captured in `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE`:

- **Slice 1 disposition AUQ** — owner chose "Implement the one real gap": add
  the body-status-token first-line BLOCK + regression tests + document the
  rule in `.claude/rules/file-bridge-protocol.md`. This is durable
  owner-decision evidence per `.claude/rules/backlog-approval-state.md` path 1
  (AUQ approval of implementation scope).
- The decision was re-asked after Prime Builder corrected an inaccurate premise
  in the first Slice 1 AUQ (per the interrogative default); the owner's choice
  was made on the corrected understanding that the gate already exists.
- Authorization envelope: `PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICES-1-4`
  (active; allowed mutation classes include `hook_upgrade`, `test_addition`,
  `governance_doc_update`).

The protected narrative edit to `.claude/rules/file-bridge-protocol.md`
additionally requires a per-artifact narrative-artifact-approval packet at
implementation time; that packet is collected separately and does not
substitute for this proposal's bridge review.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing requirements
(`GOV-FILE-BRIDGE-AUTHORITY-001`, the proposal-standards DCL family) already
establish the self-describing-versioned-file integrity property and mechanical
enforcement bias; the body-status-token rule is a concrete enforcement of
existing requirements, not a new requirement. No new or revised specification
is required before implementation.

## Spec-Derived Verification Plan

New regression file
`platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py`,
following the existing `test_bridge_compliance_gate_*` family conventions
(load the hook module via `importlib`, drive `_deny_reason_for_content` /
`_body_status_token_violation` directly):

| Acceptance criterion (spec-derived) | Test |
|---|---|
| New versioned bridge file with non-status first line (heading-first) is blocked | `test_new_file_heading_first_blocked` |
| Each canonical token (NEW/REVISED/GO/NO-GO/VERIFIED/ADVISORY/WITHDRAWN) on line 1 passes | `test_each_canonical_token_accepted` |
| `GO`/`NO-GO`/`VERIFIED` with trailing content on line 1 accepted (mirrors existing `.startswith` tolerance) | `test_verdict_token_with_trailing_content_accepted` |
| Existing on-disk file with non-canonical first line is grandfathered (overwrite allowed) | `test_existing_noncanonical_file_grandfathered` |
| Overwrite of a previously-canonical file with a non-status first line is blocked | `test_overwrite_canonical_to_noncanonical_blocked` |
| Non-versioned `bridge/*.md` (no `-NNN`) is not subject to the rule | `test_non_versioned_bridge_md_skipped` |
| `bridge/INDEX.md` is never subject to the rule | `test_index_md_exempt` |
| Edit-tool calls (empty `content`) do not trigger the rule | `test_edit_tool_empty_content_skipped` |

Execution surface (cross-shell reproducible, per the Slice 2 NO-GO `-009`
lesson):

```text
uv run --with pytest --with pytest-timeout python -m pytest platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py -q --no-header -p no:cacheprovider --basetemp=E:\GT-KB\.gtkb-state\pytest-tmp-slice1
```

Plus `uv run --with ruff python -m ruff check`/`format --check` on the changed
Python files.

## Risk / Rollback

**Risk surface:** the new predicate is additive and short-circuits early for
non-versioned files; it reuses existing helpers/constants. The only behavior
change is that NEW bridge-file Writes whose first non-blank line is not a
recognized status token are denied. The 22%-historical-noncanonical scan
confirms the grandfather branch covers legacy files; append-only discipline
means they are never re-Written anyway.

**False-block analysis:** `_first_line_is_recognized_status` mirrors the gate's
existing recognition union and errs toward acceptance (`.startswith` for
verdicts), so no currently-passing legitimate Write becomes blocked.

**Rollback:** the change is a single deny-branch + two helpers; reverting the
commit restores prior behavior. The rule-doc subsection and test file are
independently revertible.

## Recommended Commit Type

`feat:` — adds a new enforcement capability (body-status-token BLOCK) to the
bridge compliance gate, with accompanying tests and rule documentation.

## Implementation Sequence (post-GO)

1. `python scripts/implementation_authorization.py begin --bridge-id gtkb-gov-proposal-standards-slice1`.
2. Edit `.claude/hooks/bridge-compliance-gate.py` (helpers + deny branch).
3. Add `platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py`.
4. Generate the narrative-artifact-approval packet and edit
   `.claude/rules/file-bridge-protocol.md` (## Body Status-Token Rule).
5. Run the test + ruff surfaces; file the post-implementation report.

## Decision Needed From Owner

None beyond the captured S382 AUQ decisions. The protected-narrative packet is
collected mechanically at implementation time.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
