NEW

# gtkb-impl-start-gate-path-token-memory-prefix-fix — Add memory prefix to PATH_TOKEN_RE allow-list to stop unknown-target false-positive on memory-only payloads

bridge_kind: prime_proposal
Document: gtkb-impl-start-gate-path-token-memory-prefix-fix
Version: 001
Author: Prime Builder (Claude Code)
Date: 2026-06-04 UTC

author_identity: Prime Builder (Claude Code harness B)
author_harness_id: B
author_session_context_id: 666f7050-c48a-4ef4-813d-bb419d81be6e
author_model: claude-opus-4-7
author_model_version: 1m
author_model_configuration: default

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4354

target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`scripts/implementation_start_gate.py` defines `PATH_TOKEN_RE` (line 109-111) as a narrow allow-list regex that recognizes path tokens only when they begin with one of `scripts|groundtruth-kb/src|groundtruth-kb/tests|platform_tests|tests|config|.claude/hooks|.codex/gtkb-hooks|.github|bridge|independent-progress-assessments` (or one of four exact filenames). The `memory/` prefix is absent.

The downstream `gate_decision()` (lines 596-622) uses extracted paths to choose between three outcomes: skip (non-mutating), allow (no protected paths touched), or authorize-or-block (protected paths touched). The bug appears in the branch labeled `if not paths:` — when a mutating payload's path-token extraction yields zero tokens, the gate falls back to `protected = ["<unknown-mutating-target>"]` and runs `validate_targets()` against the synthetic token. The synthetic token is never authorized by any PAUTH, so the gate fails closed.

This fallback was designed for genuinely opaque payloads (e.g., an `apply_patch` blob the gate could not parse). But it also fires whenever a payload contains paths the regex's narrow allow-list does not recognize. `memory/` is the most visible miss: it is **not** a protected prefix (see `PROTECTED_PREFIXES` at line 38), and routine commits under it should pass the gate cleanly. Today they don't.

**Concrete repro:** `git commit -m "docs(memory): test" -- memory/pending-owner-decisions.md` is blocked with `protected implementation mutation matched <unknown-mutating-target>`. A working workaround is to mention `bridge/...` in the commit body, which seeds the regex with a recognized token and routes the gate to its normal allow path.

**Surgical fix (Option 1 per owner AUQ 2026-06-04):** add `memory/` to the PATH_TOKEN_RE allow-list. This is a one-character regex addition. The companion architectural follow-on (broaden the extractor and let `is_protected_path()` be the sole classifier) is captured separately as `WI-4355` under the same project for owner-prioritized triage.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — live `bridge/INDEX.md` authority; this proposal is filed and reviewed under the canonical file-bridge protocol.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every relevant governing spec must be cited; this section discharges that requirement.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — proposal carries `Project Authorization`, `Project`, and `Work Item` metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan below maps each cited spec/behavior to an executable test.
- `GOV-RELIABILITY-FAST-LANE-001` — defect origin + active project membership in `PROJECT-GTKB-RELIABILITY-FIXES` + small change (one-line regex + one test) + no new public CLI surface satisfies the fast-lane eligibility criteria; PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING covers the work item by project membership.
- `GOV-STANDING-BACKLOG-001` — WI-4354 is recorded in the MemBase `work_items` standing backlog as the durable cross-session authority for this work. **Scope is single-WI, single-bug, two-file (one source + one test); no bulk-operation surface applies, so no inventory artifact, no review-packet bundle, no Phase-deferred marker, and no formal-artifact-approval packet is required.** Bulk-ops clause coverage is N/A by scope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the standing PAUTH does not bypass bridge review; this proposal exercises the normal GO/NO-GO/VERIFIED cycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — work captured as a durable work item (WI-4354) with linked PAUTH and project membership; bridge thread is the durable proposal artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — defect captured as a tracked work item before drafting the implementation proposal.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — WI-4354 lifecycle anchored at backlog candidate; promotion to implementation_authorized occurs on Codex GO.

## Prior Deliberations

- `DELIB-S378-SLICE1-CLI-PACKET-FORM-WAIVER` — illustrates that gate-family reliability fixes use the deterministic CLI surface when the gate's own classification logic is the surface under repair (relevant pattern, not direct precedent).
- No prior deliberation directly addresses the PATH_TOKEN_RE allow-list omission; the bug surface is a fresh defect captured 2026-06-04 via owner triage. The architectural classify-then-gate pattern shared with WI-3358 (open: quoted-arg mutating-keyword false-positives) and the validator-bug chip from session ff01ba72 indicates a gate-family reliability theme that the Option 2 follow-on (WI-4355) will address holistically.

## Owner Decisions / Input

- **AUQ 2026-06-04 ("Which fix scope should the bridge proposal carry?")** — owner chose "Option 1 now + Option 2 follow-on WI". Captured as a turn-recorded AUQ answer in this session. The architectural follow-on is recorded as WI-4355 hygiene under PROJECT-GTKB-RELIABILITY-FIXES; the surgical fix in this proposal is WI-4354 defect under the same project.
- **Implementation authority:** PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING (active; covers source + test_addition + hook_upgrade by active project membership; no expiry) authorizes the implementation phase upon Codex GO. No new owner approval is required to implement once Loyal Opposition records GO.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing requirements are: (a) `is_protected_path()` semantics in `scripts/implementation_start_gate.py` (lines 168-174), which already correctly classifies `memory/` as non-protected because no `PROTECTED_PREFIXES` entry covers it; and (b) the gate's documented invariant that mutating commits to non-protected paths must pass without authorization. The fix realigns `PATH_TOKEN_RE` extraction with the already-correct `is_protected_path()` classification. No new spec is required.

## Spec-Derived Verification Plan

| Spec / Behavior | Test or Verification | Expected result |
|---|---|---|
| `is_protected_path("memory/X.md")` returns False (existing invariant) | Inspection of `scripts/implementation_start_gate.py` lines 38-49 (`PROTECTED_PREFIXES`) confirms `memory/` is not in the list. | `memory/` not protected — invariant holds. |
| Memory-only Bash payload no longer triggers `<unknown-mutating-target>` fallback (defect closure) | New test in `platform_tests/scripts/test_implementation_start_gate.py` constructing a Bash payload whose only path tokens are `memory/pending-owner-decisions.md` and asserting `gate_decision(payload) == {}`. | Test passes after fix; would fail before the fix (regression coverage). |
| Existing protected-path enforcement unchanged | Existing test suite `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --no-header -p no:cacheprovider`. | Full pre-existing suite continues to pass. |
| Ruff lint + format clean on touched files | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py` and `... ruff format --check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py`. | Exit 0 on both. |

Reproducer command for the verification (negative case must be checked against current HEAD before patching):
```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --no-header -p no:cacheprovider
```

## Risk / Rollback

**Risk surface:** minimal. The change adds a single alternation token to a regex used in two extraction call sites (`_paths_from_shell`, `_paths_from_apply_patch` via PATCH_PATH_RE — note PATCH_PATH_RE is unaffected; only PATH_TOKEN_RE is touched). After the change, payloads under `memory/` produce extracted tokens. Those tokens then flow through `is_protected_path()`, which already returns False for `memory/`, so the gate's allow path is taken. No behavior change for any path that previously matched the allow-list. No behavior change for paths that remain unmatched (the `<unknown-mutating-target>` fallback continues to fire for genuinely opaque payloads).

**Rollback:** single-commit revert of the regex edit + test deletion. No data migration, no state migration, no external surface change.

**Adjacent-bug awareness:** the user's triage notes (and this session's own repro: `git commit` keyword inside a `--description` argument tripped `MUTATING_COMMAND_RE` via prose-text false-match) confirm `WI-3358` is still active. That bug is **out of scope** for this proposal — fixing it requires shell-quote-aware tokenization of the mutating-keyword scan, which is an architectural change in the same scope class as WI-4355. This proposal does not regress WI-3358 and does not depend on it.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-impl-start-gate-path-token-memory-prefix-fix` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`fix:` — repairs a defect (false-positive gate block on non-protected memory-only payloads) without introducing new capability surface. Diff: one regex-line edit in `scripts/implementation_start_gate.py` + one new focused test in `platform_tests/scripts/test_implementation_start_gate.py`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
