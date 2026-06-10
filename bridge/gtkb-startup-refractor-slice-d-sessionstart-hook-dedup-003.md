REVISED

# GTKB-STARTUP-REFRACTOR-001 Slice D — SessionStart Hook De-Duplication (scope correction)

bridge_kind: prime_proposal
Document: gtkb-startup-refractor-slice-d-sessionstart-hook-dedup
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC
Responds to: bridge/gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-002.md (GO)

author_identity: Claude Code Prime Builder (PAUTH-authorized implementation)
author_harness_id: B
author_session_context_id: 60847c87-b6de-48c1-a2bb-1e2e51c7a7b9
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-GTKB-STARTUP-REFRACTOR-001-SLICES-A-E-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-STARTUP-REFRACTOR-001
Work Item: WI-4272

target_paths: [".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "scripts/session_start_dispatch_core.py", "scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_*session_start*.py", "platform_tests/scripts/test_codex_hook_parity.py", "platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py", "platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py", "platform_tests/hooks/test_session_start_dispatch_role_cache.py", "platform_tests/hooks/test_session_start_marker_invalidation.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Why This Revision (scope correction discovered at implementation-start)

`-001` was GO'd at `-002` with `target_paths` covering only the two dispatcher
hooks, the new shared module, and `platform_tests/scripts/test_*session_start*.py`.
During implementation-start diligence (the GO's own condition 2 — review live
state before editing), a **hard scope gap** was confirmed: the de-duplication
cannot be completed within those `target_paths` without breaking out-of-envelope
governance tests. Per `.claude/rules/file-bridge-protocol.md`, an out-of-scope
edit is a verification NO-GO even when otherwise correct, so the correct Prime
action is this REVISED scope correction rather than implementation.

### The confirmed gap (evidence)

`scripts/check_codex_hook_parity.py::_resolution_table_parity_errors` (lines
655-890) enforces **nine resolution-table parity assertions** by reading the two
dispatcher **source files** and requiring each to textually/AST-contain the
shared primitives:

- Assertion 1 (line 695): `_SESSION_ROLE_MARKER_NAME = "active-session-role.json"` literal.
- Assertion 2 (line 708): `class StartupDecision(Enum)` with the closed five-member vocabulary (AST).
- Assertion 3 (line 719): `_CANONICAL_KEYWORD_RE = re.compile(r"^::init gtkb (pb|lo)$")` literal.
- Assertion 4 (line 728): module-level dict literals `_LABEL_TO_CANONICAL_MODE`, `_MODE_TO_ROLE_PROFILE` (AST-equivalent).
- Assertion 5 (line 752): `def _invalidate_session_role_marker`, `def _session_role_marker_path`, and `main()` call-order (`_invalidate_session_role_marker` before `_bridge_dispatch_keyword_check`).
- Assertion 6 (line 775): `def _bridge_dispatch_keyword_check` + five `StartupDecision.*` references + behavior-table docstring.
- Assertion 7 (line 800): `def _audit_log_misdirected_dispatch` + kind literal + path token.
- Assertion 9 (line 862): `def _write_role_scoped_startup_relay_caches` iterating `_MODE_TO_ROLE_PROFILE`, skipping `primary_mode`, not referencing `_resolve_own_role_set`.

`check_project()` invokes this at line 1252. Three test modules pin the
canonical-pass contract on those exact source files:

- `platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py:81-82` — `assert errors == []` on the canonical tree.
- `platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py:91-92` — `assert errors == []` baseline.
- `platform_tests/scripts/test_codex_hook_parity.py` — `check_project(REPO_ROOT)` consumer assertion.

Slice D's extraction relocates exactly those primitives into the shared module,
which **empties the wrappers** of the enum, the regex, the dict literals, the
marker constant, and five function definitions. Assertions 1-7 and 9 then fail
on the canonical tree, breaking the three tests above. Those files are **outside
`-001`'s `target_paths`**, and the mechanical implementation-start gate
(`scripts/implementation_start_gate.py`) blocks any write to them under the
current packet. Assertion 8 (intentional-difference guard: each wrapper's own
`HARNESS_NAME`/`OUT_DIR`) is the only one a thin wrapper still satisfies.

The de-duplication and the parity-tool relocation are therefore **bidirectionally
coupled** — neither is independently correct — so they belong in one slice with
one `target_paths` envelope.

## Corrected Design

1. **Extract shared logic** into `scripts/session_start_dispatch_core.py`
   (stdlib-light: standard library plus the existing `scripts.harness_identity`
   / `scripts.harness_projection_reader` helpers; no `groundtruth_kb`, DB, or
   third-party imports). The two dispatchers differ today only in the module
   docstring, `OUT_DIR`, `HARNESS_NAME`, and one comment line (confirmed by a
   full diff: all other ~645 lines are character-identical).

2. **Thin wrappers that preserve the existing test contract.** The existing
   dispatcher tests load each wrapper file via `spec_from_file_location` and
   then `monkeypatch.setattr(module, "OUT_DIR", ...)` /
   `monkeypatch.setattr(module, "_bridge_auto_dispatch_context", ...)` and call
   `module.main()` / `module._write_startup_relay_cache(...)` with their current
   signatures (e.g. `test_claude_session_start_dispatcher.py:509`,
   `test_codex_session_start_dispatcher.py:272`,
   `platform_tests/hooks/test_session_start_dispatch_role_cache.py:94-97`). Those
   tests must pass **unchanged**, so the shared functions must execute against
   the wrapper module's globals (late binding). The wrapper therefore imports the
   core module and rebinds the shared functions onto its own module namespace
   (cloning each function with `types.FunctionType(fn.__code__, globals(), ...)`)
   after setting its own `HARNESS_NAME`/`OUT_DIR`. This keeps `module.OUT_DIR`
   monkeypatch observation and `module.<helper>` late binding intact while the
   code is defined exactly once in the core module.

3. **Relocate the parity assertions to the single source of truth.** Redesign
   `_resolution_table_parity_errors` so the anti-drift primitive assertions
   (Assertions 1-7, 9) are checked against `scripts/session_start_dispatch_core.py`
   (the single definition site), and the per-wrapper assertions become: (a) each
   wrapper imports/delegates to the shared core module, and (b) each wrapper
   retains its intentional-difference guard (its own `HARNESS_NAME`/`OUT_DIR`
   assignment and not the other harness's — Assertion 8, unchanged). This
   **preserves the anti-drift intent** at its new location: the two-copies-
   diverge drift class is eliminated by construction (one copy), and a wrapper
   that stops delegating (re-introduces local logic) is caught by the new
   delegation assertion.

4. **Update the three parity tests** so their canonical-pass and drift-class
   cases stage/mutate the shared core module (and the delegation wrappers)
   instead of the dispatcher wrappers, preserving every drift-class regression
   at the new source. `platform_tests/hooks/test_session_start_marker_invalidation.py`
   (which reads dispatcher source text) is updated to read the core module where
   it asserts the marker logic.

This is a **behavior-preserving refactor**: no change to SessionStart decision
logic, role resolution, init-keyword dispatch, the disclosure-relay contract, or
the parity tool's drift-detection guarantee.

## Sequencing

Slice D remains sequenced **last**. The workstream has materially quieted since
`-001`: Slice B is VERIFIED (`-004`), Slice A is VERIFIED, the role-mirror
thread is VERIFIED, and Slice E's in-flight work edits only
`platform_tests/scripts/test_lo_startup_text.py` plus narrative startup text —
all **disjoint** from this slice's dispatcher / core-module / parity files. Slice
C is GO but unstarted and edits protected narrative + startup-payload surfaces,
also disjoint from the dispatch hooks. The implementation report will record the
live dirty-state evidence for the target files immediately before editing.

## Invariants Preserved

- **stdlib-light / fast-import:** core imports only stdlib + the existing
  `scripts.harness_*` helpers; the SessionStart hot path is not slowed. A new
  test asserts the core module imports no `groundtruth_kb`/DB/third-party module.
- **Harness parity:** `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — the parity tool's
  drift guarantee is preserved by relocating its assertions to the shared source
  plus a wrapper-delegation assertion.
- **Role resolution / init-keyword:** `DCL-SESSION-ROLE-RESOLUTION-001`,
  `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`, `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`
  parsing/assertion/marker-lifecycle unchanged.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` — governs the SessionStart dispatch behavior preserved here. PAUTH-linked.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — de-duplication reduces the maintained startup surface.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Claude/Codex hook parity; the parity tool is the mechanical contract being relocated.
- `DCL-SESSION-ROLE-RESOLUTION-001` — the resolution-table contract the parity tool enforces (Slice 4 invariant); behavior unchanged.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — init-keyword syntax the dispatchers parse; unchanged.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — init-keyword assertion; unchanged.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol for this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-linkage compliance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + WI + PAUTH linkage.
- `GOV-STANDING-BACKLOG-001` — WI-4272 linkage.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; all target paths in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory); `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory); `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).

## Prior Deliberations

- `DELIB-20260622` — owner PAUTH decision (covers WI-4272; mutation classes source/test/hook).
- `bridge/gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-002.md` — the GO this revision supersedes; its condition 2 (review live state before editing) is what surfaced the scope gap.
- `bridge/gtkb-startup-refractor-scoping-002.md` — scoping GO defining Slice D as the code-consolidation target sequenced last.
- `bridge/gtkb-startup-refractor-slice-a-startup-control-inventory-004.md` — Slice A VERIFIED; the control map classifies both dispatchers as active de-dup targets.
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-003.md` (GO at `-004`) — established the nine resolution-table parity assertions in `check_codex_hook_parity.py` that pin the shared definitions to the wrapper files. This is the precise contract Slice D must relocate; its drift-class tests are the regression floor the corrected design preserves.

## Owner Decisions / Input

- Implementation authority: project PAUTH (active), owner decision `DELIB-20260622`,
  allowed mutation classes `source`, `hook`, `test`. The expanded `target_paths`
  (adding `scripts/check_codex_hook_parity.py` and the three parity test modules)
  remain within the project's PAUTH mutation classes and the project scope
  (SessionStart parity infrastructure); no new owner content decision is required.
  This is a behavior-preserving refactor.

## Requirement Sufficiency

**Existing requirements sufficient.** The behavior contract is fully specified by
the cited parity/role/init-keyword specs; this slice preserves that contract
(including the parity tool's drift-detection guarantee) while removing duplication.
No new specification is required.

## Spec-Derived Verification Plan

| Specification / Invariant | Spec-to-test mapping | Command | Expected |
|---|---|---|---|
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` + `DCL-SESSION-ROLE-RESOLUTION-001` | relocated parity assertions: canonical tree passes; each drift class still fires against the shared core module | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py platform_tests/scripts/test_codex_hook_parity.py -q -p no:cacheprovider` | PASS |
| `DCL-SESSION-ROLE-RESOLUTION-001` + init-keyword specs | existing SessionStart dispatcher tests (role resolution, init-keyword routing, STRICT_DROP, relay-cache monkeypatch) pass unchanged against the refactored wrappers | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/hooks/test_session_start_dispatch_role_cache.py platform_tests/hooks/test_session_start_marker_invalidation.py platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py platform_tests/scripts/test_session_role_marker_invalidation_both_harnesses.py -q -p no:cacheprovider` | PASS |
| stdlib-light invariant | new test asserts `session_start_dispatch_core` imports only stdlib + `scripts.harness_*` (no `groundtruth_kb`/DB/third-party) | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_session_start_dispatch_drains_pending_before_role_resolution.py platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py -q -p no:cacheprovider` (plus the new stdlib-light test) | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | lint + format on changed Python | `ruff check` and `ruff format --check` on the two dispatchers + core module + parity tool + changed tests | clean |

The implementation report will carry observed pytest + ruff results and the
live dirty-state evidence for the target files captured immediately before editing.

## Risk / Rollback

Highest blast radius in the umbrella (every session start runs these hooks, and
the parity tool is the mechanical drift gate for SessionStart parity). Risk is
mitigated by: behavior-preserving extraction; preserving the existing dispatcher
tests unchanged (monkeypatch contract retained via namespace rebind); relocating
rather than weakening the parity assertions (drift classes preserved at the new
source); the stdlib-light import assertion; and sequencing this slice last.
Rollback is a single-commit revert restoring the two self-contained hooks and the
original parity tool.

## Recommended Commit Type

`refactor` — extracts shared SessionStart logic into one module with thin
delegating wrappers and relocates the parity assertions to the single source;
no behavior change, no new capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
