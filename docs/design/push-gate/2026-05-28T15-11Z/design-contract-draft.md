# Design Contract (Draft)

**Status:** DRAFT pending owner answers to 5 deferred decisions in `open-decisions-and-aauq-plan.md`.
**Authority:** `bridge/gtkb-push-gate-design-governance-review-004.md` (Codex GO on REVISED-3).
**Becomes binding when:** Owner answers 5 AUQs → DA records → `gtkb-push-gate-design-contract-final` thread renames this file to `design-contract.md` and locks the content.

This document specifies the technical architecture for PROJECT-GTKB-PUSH-GATE. Sections that depend on deferred owner decisions are explicitly flagged `(Pending QN)`; those sections remain options-laden until owner answers settle them.

## Architecture Overview

The push gate is a **single canonical CLI** (`gt push-gate`) invoked by two surfaces:

1. **Local pre-push hook** (`.githooks/pre-push`) — invoked on `git push`; blocks the push if any check fails.
2. **GitHub Actions workflow** (`.github/workflows/push-gate.yml`) — invoked on `push` and `pull_request` events to `develop` and `main` (per Q4 recommendation); registered as a required check via branch protection.

Both surfaces invoke the **identical** `gt push-gate run` invocation; the gate logic is shared, not duplicated. This satisfies `SPEC-DSI-CI-GATE-001` § "shared engine path between local hook and CI logic."

### Invocation Shape

```
gt push-gate run [--mode {audit|gate}] [--layers LAYER_GLOBS] [--cache {use|skip|refresh}]
gt push-gate audit [--output-dir PATH]                     # alias for `run --mode audit`
gt push-gate doctor                                        # invariant verification (SPEC-DSI-DOCTOR-CHECK-001)
gt push-gate install                                       # one-time hook installation via core.hooksPath
gt push-gate cache {info|clear|prune}                      # cache lifecycle management
```

Each invocation is read-only against the codebase except `gt push-gate cache clear|prune` (cache directory mutation only) and `gt push-gate install` (registers `core.hooksPath`).

### Layer Composition

Seven layers, executed in order. Any layer FAIL → gate FAIL → push blocked (in `gate` mode). In `audit` mode all layers run regardless of layer-level results; only infrastructure failures stop layer execution.

| Layer | Name | Tools | Output |
|---|---|---|---|
| 1 | Pre-commit hygiene | whitespace, ruff format/check, gitignore-bypass, credential pre-scan | per-file findings JSON |
| 2 | Type + AST | mypy, custom AST (hardcoded-externals, hardcoded SHA, magic-number, import-topology) | per-file findings JSON |
| 3 | Test suites | pytest (with impact analysis per Q5) | pass/fail summary + JUnit XML |
| 4 | Architecture + governance | `gt assert`, `gt project doctor`, applicability preflight, clause preflight, INDEX-vs-files consistency | invariant report JSON |
| 5 | Security audit | bandit, pip-audit, gitleaks, `gt secrets scan` | per-finding severity-tagged JSON |
| 6 | Governance integrity | spec-to-test coverage, DA linkage, doubled-prefix detector, standing-backlog freshness | per-class findings JSON |
| 7 | Release-readiness | `release-candidate-gate` skill (Layer 7 only on PRs to main + tagged releases) | release-readiness verdict JSON |

## Caching Substrate

The cache is **content-addressed** and **checker-version-aware**:

```
Cache key = sha256(layer_id || checker_version || file_sha256_list || layer_inputs_sha256)
Cache value = {result: PASS|FAIL, findings: [...], generated_at_utc: ..., ttl_anchor: ...}
```

- `file_sha256_list` is the sorted list of input-file SHAs (Layer-N considers only the files it would check; e.g., Layer 1 considers all tracked Python files; Layer 3 considers test files + their imports per the impact-analysis chain).
- `checker_version` is the upstream tool version + GT-KB-internal checker version (so a ruff bump or a custom AST checker change invalidates the cache).
- `layer_inputs_sha256` covers configuration inputs (ruff config, mypy config, applicability registry, etc.) so config changes invalidate the cache.

### Cache Invalidation

- **Tool version bump** → cache entries with the old version remain in cache but never match new keys; they're pruned by `gt push-gate cache prune --older-than 30d`.
- **File content change** → file SHA changes → cache key changes → cache miss → layer re-runs that file's portion.
- **Config change** → `layer_inputs_sha256` changes → all entries for that layer re-key → cache miss for that layer.
- **Cross-file dependency change** (test impacted by changed import) → handled by Layer 3's impact-analysis chain (Q5).

### Cache Storage

- **Location:** `.gtkb-state/push-gate/cache/` (gitignored; per-developer).
- **Format:** SQLite database `cache.db` with append-only writes; reads via index on cache key.
- **Lifecycle:** Slice 7 specifies cache lifecycle (TTL, max-size, pruning policy).

### Cache Semantics in `audit` vs `gate` Mode

- `audit` mode: cache reads are advisory; layer always runs and updates cache. Use case: producing canonical inventory; verifying cache correctness.
- `gate` mode: cache hits return PASS without running the layer; cache misses run the layer and update cache.

## Layer 1 — Pre-Commit Hygiene

**Tools:** ruff (format + check), whitespace checker, gitignore-bypass detector, credential pre-scan.

**Scope:** All tracked Python files + non-Python text files for whitespace.

**Inputs:** `pyproject.toml` ruff config; `.gitignore`; `config/secrets/credential-patterns.toml`.

**Output:** Per-file finding list; `result: PASS` if all files clean.

**Failure semantics:** Any ruff finding, whitespace defect, gitignore bypass, or credential-shaped span → layer FAIL.

## Layer 2 — Type + AST

**Tools:** mypy + custom AST checkers in `groundtruth-kb/src/groundtruth_kb/push_gate/ast/`.

**AST Checks:**

- **hardcoded-externals** — detects literal hostnames, URLs, version pins outside `config/`.
- **hardcoded-SHA** — detects SHA256 literals in source code (likely should be in config or test fixtures).
- **magic-number** — detects unnamed numeric constants in operational paths.
- **import-topology** — detects cross-package imports that violate the architecture layering rules.

**Scope:** All tracked Python files.

**Inputs:** `mypy.ini` or `pyproject.toml` mypy config; `config/push-gate/ast-rules.toml` for AST checker config.

**Output:** Per-file finding list with rule-code + severity.

**Failure semantics:** Any mypy error or AST checker finding above its configured severity threshold → layer FAIL.

## Layer 3 — Test Suites

**Tools:** pytest with impact analysis (Q5 decision).

**Impact Analysis (Pending Q5):**

- Option B (recommended): pure-stdlib SHA cache — per-file SHA + import graph from pytest collection; if file is unchanged AND its imports' SHAs are unchanged, skip its tests.
- Option A: pytest-testmon — coverage-traced precise selection.

**Scope:** All discoverable pytest test directories per project config (`tests/`, `platform_tests/`, `groundtruth-kb/tests/`, slice-specific test dirs).

**Output:** Per-test PASS/FAIL/SKIPPED; aggregate counts; JUnit XML.

**Failure semantics:** Any FAIL → layer FAIL. Any unexpected SKIPPED (skip without explicit marker) → layer FAIL.

## Layer 4 — Architecture + Governance Assertions

**Tools:**

- **`gt assert`** — runs MemBase-anchored assertions (spec-attached grep/grep-absent/glob checks).
- **`gt project doctor`** — runs platform-level health invariants per `SPEC-DSI-DOCTOR-CHECK-001`.
- **`bridge_applicability_preflight.py`** — runs against all open bridge entries (NEW/REVISED).
- **`adr_dcl_clause_preflight.py`** — runs against all open bridge entries.
- **INDEX-vs-files consistency** — verifies every bridge file referenced in INDEX exists; every bridge file in `bridge/` is referenced in INDEX.

**Scope:** Bridge state + spec assertions + doctor invariants.

**Output:** Aggregate FAIL/PASS per invariant; doctor produces structured WARN/FAIL with severity.

**Failure semantics:** Any FAIL on `gt assert` or `gt project doctor` (FAIL severity) → layer FAIL. WARN-severity findings → layer PASS with warning.

**Coexistence note:** Layer 4 EXTENDS `SPEC-DSI-DOCTOR-CHECK-001` by adding `push_gate.layer_4_PASS` as one of doctor's invariants.

## Layer 5 — Security Audit

**Tools:**

- **bandit** — Python SAST.
- **pip-audit** — dependency vulnerability scan.
- **gitleaks** — secrets scan on diff + history.
- **`gt secrets scan`** — GT-KB-specific credential scan per `SPEC-SEC-SCANNER-CLI-001`.
- **scanner-safe-writer batch** — re-runs scanner-safe-writer on a batch of files to verify scanner correctness.

**Scope:** Source code (bandit), dependencies (pip-audit), git history (gitleaks), staged + range + path scopes (`gt secrets scan`).

**Mode selection (per `SPEC-SEC-SCANNER-CLI-001`):**

- Pre-push (local): `gt secrets scan --staged && gt secrets scan --range origin/HEAD..HEAD`
- CI: `gt secrets scan --all-ref`

**Output:** Per-finding severity-tagged JSON.

**Failure semantics:** Any HIGH or CRITICAL finding from any tool → layer FAIL. MEDIUM → layer PASS with warning.

**Coexistence note:** Layer 5 WRAPS `SPEC-SEC-SCANNER-CLI-001`'s `gt secrets scan` CLI — does not modify it.

## Layer 6 — Governance Integrity

**Tools:**

- **spec-to-test coverage** — verifies every active spec has at least one attached test per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.
- **DA linkage** — verifies every owner-decision deliberation has a citing bridge or rule file.
- **doubled-prefix detector** — verifies no `project_work_item_memberships` row has a doubled-prefix `PROJECT-PROJECT-*` project_id (per WI-3411 defect class).
- **standing-backlog freshness** — verifies no work_item has been stuck in `unapproved` state > N days without owner attention (N TBD; candidate spec).
- **bridge-protocol invariants** — every `NEW`/`REVISED` filing has corresponding INDEX entry; every `GO`/`NO-GO`/`VERIFIED` references valid prior version.

**Output:** Per-class finding lists; aggregate gov-integrity score.

**Failure semantics:** Any spec-to-test coverage gap, DA linkage gap on owner decision deliberations, or doubled-prefix membership row → layer FAIL. Standing-backlog freshness violations → layer PASS with warning until policy formalized.

**Coexistence note:** Layer 6 is GT-KB-internal governance integrity; COEXISTS-INDEPENDENTLY with the 6 newly-cited specs (none of them govern this layer's check surface).

## Layer 7 — Release-Readiness

**Tool:** `release-candidate-gate` skill per `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`.

**Scope:** Triggered only on:

- PRs to `main` (release-bound).
- Tagged release commits (`v*` tags).
- Direct pushes to `main` (rare; should be hotfix flow).

Not triggered on develop pushes, feature-branch pushes, or PR target != main.

**Output:** Release-readiness verdict (PASS/FAIL + per-check evidence).

**Failure semantics:** FAIL → layer FAIL → push blocked. PASS contributes evidence toward governance-required test evidence per `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`.

**Coexistence note:** Layer 7 WRAPS the existing `release-candidate-gate` skill; does not modify the skill itself.

## Hook Portability Model

Per `SPEC-SEC-HOOK-PORTABILITY-001`:

- Hooks live at **tracked** paths: `.githooks/pre-commit` (pre-existing) and `.githooks/pre-push` (push gate adds this).
- Activation via `core.hooksPath = .githooks` set at `gt push-gate install` time and verified by `gt project doctor` invariant.
- No writes to `.git/hooks/` (which is untracked per-clone state).

The `.githooks/pre-push` script is short:

```bash
#!/usr/bin/env bash
# Tracked hook; invokes the gate CLI.
set -euo pipefail
exec python -m groundtruth_kb push_gate run --mode gate "$@"
```

The hook script itself contains no gate logic; logic lives in the `gt push-gate` CLI module. This keeps the hook portable across platforms and version-stable.

## CI Integration Model

Per `SPEC-DSI-CI-GATE-001` and `SPEC-SEC-GITHUB-POSTURE-001`:

- Workflow file: `.github/workflows/push-gate.yml` (single workflow; not split per layer).
- Triggers: `push` to `develop`/`main`, `pull_request` targeting `develop`/`main` (per Q4 recommendation).
- Platform matrix (Pending Q3): `windows-latest` only (Option A) or `windows-latest` + `ubuntu-latest` (Option B recommended).
- Branch protection: workflow registered as required status check via `gt github security doctor` invariants (per `SPEC-SEC-GITHUB-POSTURE-001`).
- Cache restoration: pull cache from GitHub Actions cache keyed by tool-versions + config-hash.
- Cache persistence: write back updated cache.

Workflow invocation:

```yaml
- name: Run push gate
  run: gt push-gate run --mode gate --cache use
```

## Owner-Override Path (Pending Q2)

The override path's existence and shape depend on Q2 (see `open-decisions-and-aauq-plan.md`):

- **Option A (recommended):** `bridge_kind: gate_bypass_authorization` filings; each authorizes one push to bypass the gate. Audit trail in `bridge/`.
- **Option B:** No override exists; gate is absolute.
- **Option C:** Environment variable escape hatch (not recommended).

This contract section is a placeholder until Q2 is answered.

## § Coexistence (Required per Codex GO-004 P1-001)

For each of the 6 newly-cited specs (per `bridge/gtkb-push-gate-design-governance-review-003.md` Specification Links), explicit WRAPS / EXTENDS / COEXISTS-INDEPENDENTLY relationship:

### `SPEC-DSI-CI-GATE-001` — IMPLEMENTS

The push gate directly **implements** the CI-time-enforcement invariant. Coverage:

- "GitHub Actions job on every pull request and push" → `.github/workflows/push-gate.yml` per Q4.
- "Branch protection requiring the job" → registered via `SPEC-SEC-GITHUB-POSTURE-001` doctor; per Q3 platform matrix.
- "Shared engine path between local hook and CI logic" → identical `gt push-gate run` invocation from both surfaces.

Conflict surfaces: none. This spec PRE-DATED the push gate; the push gate is the implementing surface.

### `SPEC-DSI-DOCTOR-CHECK-001` — EXTENDS

The push gate **extends** doctor's existing invariant set. New invariants:

- `push_gate.hook_installed` — verifies `.githooks/pre-push` exists and `core.hooksPath = .githooks`.
- `push_gate.workflow_present` — verifies `.github/workflows/push-gate.yml` exists.
- `push_gate.cache_db_healthy` — verifies `.gtkb-state/push-gate/cache/cache.db` is openable + indexed.
- `push_gate.layer_4_PASS` — verifies recent push-gate Layer 4 result is PASS (informational; not gating doctor itself).

Existing doctor invariants (smart-poller, bridge-dispatch, scaffold-drift, etc.) unchanged.

### `SPEC-SEC-HOOK-PORTABILITY-001` — WRAPS

The push gate **wraps** the spec's tracked-hooks-via-core.hooksPath invariant by:

- Installing `.githooks/pre-push` at tracked path (consistent with the spec's pattern for `.githooks/pre-commit`).
- Using `core.hooksPath = .githooks` indirection (already required by the spec for `pre-commit`).
- NOT writing to `.git/hooks/` (consistent with spec's untracked-paths-forbidden rule).

Conflict surfaces: none. The push gate inherits the spec's portability properties.

### `SPEC-SEC-SCANNER-CLI-001` — WRAPS

The push gate's Layer 5 **wraps** `gt secrets scan` for security audit. Mode selection per gate phase:

- Pre-push: `--staged` + `--range origin/HEAD..HEAD` (only newly-pushed changes).
- CI: `--all-ref` (full history coverage for branch-protection gating).

The CLI itself is unchanged. Layer 5 invokes it via subprocess; output is parsed into the layer's finding list.

### `SPEC-SEC-GITHUB-POSTURE-001` — COORDINATES (variant of WRAPS)

The push gate **coordinates** with `gt github security doctor` for branch-protection registration:

- Push gate's CI workflow is registered as a required status check via this doctor's existing branch-protection invariants.
- The doctor's existing invariants (workflow coverage, branch protection rules) are unchanged.
- The push gate does NOT modify the doctor; it provides one of the workflows the doctor checks.

The relationship is registration-only, not modification of the doctor's behavior.

### `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — WRAPS

The push gate's Layer 7 **wraps** the `release-candidate-gate` skill. Activation conditions:

- PRs to `main`.
- Tagged release commits.
- Direct pushes to `main` (uncommon).

Layer 7 runs only on these triggers; Layer 7 PASS contributes evidence toward governance-required test evidence per the spec. The spec's other invariants (governed test evidence, owner-approved deferral path) are unchanged.

## Open Items

Items that depend on owner decisions or future slice work, tracked here for visibility:

- **Q1 cleanup-sequencing answer** → affects Slice 3-5 timing.
- **Q2 override path scope** → affects Slice 7 design.
- **Q3 multi-platform CI** → affects Slice 6 workflow matrix.
- **Q4 PR-vs-push gating scope** → affects Slice 6 workflow trigger.
- **Q5 test impact analysis dependency** → affects Slice 1 cache substrate + Slice 3 cleanup.
- **Cache size cap** → defer to Slice 7 hardening.
- **Cache cross-developer sharing** → out of scope; per-developer cache is sufficient for Phase 1.
- **Performance budget per layer** → defer to Slice 4 measurement.
- **Standing-backlog-freshness policy threshold** → candidate spec; defer to dedicated thread.

## Promotion to Binding

This DRAFT is promoted to binding `design-contract.md` (drop "draft" suffix) by the `gtkb-push-gate-design-contract-final` thread once:

1. All 5 deferred owner decisions are answered.
2. Codex VERIFIED on the final-binding thread.
3. The thread's post-impl report renames this file and updates the (Pending QN) sections with the locked answers.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
