# Changelog

All notable changes to the **GroundTruth KB (GT-KB)** platform are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project aims to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The version source of truth is [`groundtruth-kb/src/groundtruth_kb/__init__.py`](groundtruth-kb/src/groundtruth_kb/__init__.py).

## [Unreleased]

Active development happens on the `develop` branch. See [`bridge/INDEX.md`](bridge/INDEX.md)
for in-flight implementation proposals and reviews, and the standing backlog
(`gt backlog list`) for planned work.

## [0.7.0-rc1]

First release candidate of the GT-KB platform. Establishes the full
specification-driven, dual-agent operating model end to end.

### Core platform

- **MemBase** — append-only, versioned knowledge database (`groundtruth.db`)
  for specifications, tests, work items, procedures, documents, and environment
  configuration. Every mutation records `changed_by`, `changed_at`, and
  `change_reason`; current state is the latest version per ID.
- **Deliberation Archive** — searchable record of decisions, reviews, and
  rejected alternatives, with semantic indexing, so future sessions inherit the
  project's reasoning.
- **File-bridge protocol** — versioned Prime Builder ↔ Loyal Opposition
  coordination under `bridge/` with `bridge/INDEX.md` as canonical workflow
  state (`NEW` / `REVISED` / `GO` / `NO-GO` / `VERIFIED`, plus `ADVISORY` /
  `DEFERRED` / `WITHDRAWN`).
- **`gt` CLI** — `gt project init`, `gt summary`, `gt assert`, `gt backlog`,
  `gt deliberations`, `gt project doctor`, and `gt project upgrade`.

### Governance & quality gates

- Mandatory specification linkage and specification-derived verification gates
  on bridge proposals and reports.
- Formal-artifact-approval and narrative-artifact-approval evidence gates for
  governed artifact creation.
- Credential-scan, bridge-compliance, and implementation-start gates enforced at
  write/commit time.
- Standing backlog as the single MemBase-backed work authority (`work_items`).
- `AskUserQuestion` as the sole owner-decision channel for approvals, waivers,
  priority choices, and clarifications.

### Multi-harness & dispatch

- Portable Prime Builder / Loyal Opposition roles that attach to AI coding
  harnesses by owner assignment.
- Cross-harness event-driven bridge dispatch (PostToolUse + Stop hooks) and a
  single-harness dispatcher for single-harness installs.

### Adoption

- `gt project init` scaffolding: governance rules, canonical terminology, MemBase
  initialization, and the project-root-boundary contract under the adopter root.
- Dashboard surfaces for governance, release-readiness, drift, and bridge state
  (optional Grafana integration; core surfaces via the CLI).

## Earlier releases

Versions **0.2.1 through 0.6.1** were earlier development releases that
incrementally built the MemBase store, the file-bridge protocol, the `gt` CLI,
the Deliberation Archive, scaffolding, and the governance gate stack. Full
per-change history is available in the git log and the corresponding version
tags (`v0.2.1` … `v0.6.1`).

[Unreleased]: https://github.com/Remaker-Digital/groundtruth-kb/compare/v0.7.0-rc1...develop
[0.7.0-rc1]: https://github.com/Remaker-Digital/groundtruth-kb/releases/tag/v0.7.0-rc1
