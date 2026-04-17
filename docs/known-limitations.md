# Known Limitations

GroundTruth-KB is a developer-preview at version 0.6.0. There are live gaps
we know about and want an adopter to see **before** committing. Honesty
beats marketing.

This page points at the authoritative audit report rather than re-asserting
findings in a place that can drift. When a gap is closed, this page and
the audit report are updated in the same commit.

## 1. `gt project upgrade` — Non-Disruptive Upgrade Gaps

The full audit is at
[Non-Disruptive Upgrade Investigation](reports/non-disruptive-upgrade-audit.md).
Three gaps matter most for an adopter:

### Gap 2.8 — Three rule-file templates are scaffold-copied but unmanaged

Today, `gt project upgrade` cannot restore three `.claude/rules/*.md`
files if an adopter deletes them:

- `.claude/rules/bridge-essential.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/file-bridge-protocol.md`

The scaffold copies these files on `gt project init` but they are not
part of `_MANAGED_RULES`, so the upgrade path cannot detect the absence
and repair it. `gt project doctor` does detect the absence and reports
it, but the fix today is manual.

See audit report §Area 2 Gap 2.8 and §Area 9 rows 30–32.

**Mitigation today:** If doctor reports one of these files missing,
re-run `gt project init --overwrite <filename>` or copy the file from a
fresh scaffold directory. This is tracked by the forthcoming
`gtkb-managed-artifact-registry` child bridge, which will move all
template rows into a single declarative registry so upgrades become
idempotent.

### Gap 6.x — Hook-registration upgrades are unrepairable for 11 of 12 entries

`.claude/settings.json` contains 12 hook registrations that the scaffold
writes at `gt project init` time. Of those, only 1 (the
`scanner-safe-writer` PreToolUse hook) is managed by the upgrade path.
The other 11 are scaffold-only — if an adopter deletes or corrupts them,
`gt project upgrade` cannot restore them.

See audit report §Area 6 and §Area 9 row 39 for the full matrix.

**Mitigation today:** Re-scaffold into a disposable scratch directory
(`gt project init /tmp/fresh`) and diff-merge `.claude/settings.json`
manually. Planned remediation ties into the same managed-artifact registry
that closes Gap 2.8.

### U-class Scaffold Rows — 20 of 55 template files are unmanaged

The audit report's §Area 9 inventory classifies all 55 scaffold/template
files into M (managed), R (repaired), A (append-only), U (unmanaged), and
X (explicitly excluded). 20 rows sit in the U class: present at scaffold
time, unmanaged by upgrade. The full list is at audit report §Area 9.

**Mitigation today:** The inventory is the single source of truth. If you
need one of these files, copy from a fresh scaffold. Do not rely on
`gt project upgrade` to restore a U-class file.

## 2. Web UI (`gt serve`)

The Web UI is **read-plus-limited-write**. An adopter can browse specs,
tests, work items, and deliberations, and can execute governance-gate
runs. Full CRUD for specs and tests is still CLI-only. The UI targets
evaluators and team leads; daily work happens through the CLI and
Python API.

## 3. Deliberation Archive Semantic Search

The `gt deliberations search` command works in two modes:

- **SQLite LIKE fallback:** Ships with the base install. No extras
  required. Returns substring matches only.
- **Semantic search:** Requires `pip install "groundtruth-kb[search]"`,
  which installs ChromaDB. The index is built on demand; the first
  `search` call after a fresh install triggers a one-time rebuild.

ChromaDB is a derived index — if it becomes stale, run
`gt deliberations rebuild-index`.

## 4. Platform Baseline

The install baseline is **Windows + internet access**. Linux and macOS
workstations work in practice (the reference project CI runs on Ubuntu),
but the walkthrough in [Start Here](start-here.md) and the PowerShell
primer both assume Windows. A cross-platform walkthrough is tracked as a
future documentation pass.

## 5. Claude Design Integration

GroundTruth-KB does not integrate with Claude Design
([claude.ai/design](https://claude.ai/design)) today. Claude Design
outputs (HTML prototypes, PPTX, Canva exports) are not registered as
managed artifacts, and there is no review gate that treats a
design-handoff as binding. This is a candidate for a future ADR + child
bridge, not a v0.6.0 capability.

## 6. Deployment Provisioning

GroundTruth-KB is a **local toolkit**. It does not provision cloud
infrastructure, create external accounts (Anthropic, OpenAI, Azure,
GitHub), install OS scheduled tasks, or deploy applications.
Project-specific deployment is the responsibility of the downstream
project, using the CI templates and setup prompts that
`gt project init` scaffolds.

## 7. CTO-Persona Walkthrough — Pending

The [Start Here](start-here.md) rewrite includes an owner-gated
qualitative gate: a cold-read walkthrough by a senior technologist who
has never seen GroundTruth-KB before. As of 2026-04-17, that walkthrough
is PENDING owner sign-off. Adopter feedback collected between this
release and the walkthrough will land in a docs-only follow-up.

---

## Reporting a New Limitation

If you hit a limitation that is not listed here, please open a GitHub
issue tagged `method-feedback`. We especially value reports that include:

- The command or workflow that surprised you.
- What you expected vs. what happened.
- Whether you worked around it, and if so, how.

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
