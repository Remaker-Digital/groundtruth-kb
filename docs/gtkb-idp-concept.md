# GT-KB as an Internal Developer Platform (IDP) — Supplementary Reference

**Status:** Supplementary reference material. Not the canonical terminology
authority.

> The **canonical** local terminology surface for this repo is the concise
> glossary block in `CLAUDE.md` and `AGENTS.md`. Once Agent Red adopts the
> GT-KB managed canonical-terminology artifacts
> (`.claude/rules/canonical-terminology.md` and
> `.claude/rules/canonical-terminology.toml`), those managed artifacts become
> the authoritative source and this file remains a human-readable companion.

This document expands the `CLAUDE.md` glossary entry for IDP with context,
distinctions from related industry terms, and pointers for new adopters.
It does not replace or override the glossary block and does not introduce
new definitions.

## Canonical Definition

**GT-KB (GroundTruth-KB) is an Internal Developer Platform (IDP)** for
individual developers building and maintaining production software with AI
assistance. Like any IDP, it provides shared project infrastructure,
governance artifacts, runtime services, and conventions that applications
consume. Unlike traditional org-scale IDPs, it is sized for a
single-developer context and integrates multiple AI coding harnesses
(Claude Code, Codex) under shared specifications, bridges, and protocols.

## Industry Context

**Platform Engineering** is the established discipline for building
developer platforms that abstract infrastructure, governance, and
operational concerns behind a unified developer experience. An **Internal
Developer Platform (IDP)** is the canonical artifact the discipline
produces: a curated set of tools, templates, services, and conventions
exposed to developers via a consistent interface.

Well-known IDPs at organizational scale include Spotify's Backstage,
Humanitec, and Port. These are typically multi-team and multi-application;
they emphasize self-service provisioning, golden-path templates, and
cross-cutting governance.

GT-KB applies the same shape at individual-developer scale: a single
developer consumes shared infrastructure (bridge protocol, artifact
governance, knowledge database, canonical terminology, runtime services)
while building one or more applications.

## Distinctions From Related Terms

- **Framework** (e.g., Rails, Django, React): code library you extend. GT-KB
  is not primarily a code library you extend; you build *alongside* GT-KB,
  consuming its CLI, services, and conventions.
- **Toolchain** (e.g., Rust, LLVM): a curated collection of tools that work
  together. GT-KB includes a toolchain but also carries governance,
  artifacts, and runtime services beyond tool composition.
- **Scaffold / Generator** (e.g., Yeoman, `create-react-app`): produces a
  starter project then exits. GT-KB persists: it participates in the full
  development-to-maintenance lifecycle through specs, bridges,
  deliberations, and release gates.
- **AI coding harness** (e.g., Claude Code, Codex CLI): a runtime that
  drives an AI model against a project. GT-KB wraps harnesses; it is
  emphatically *not itself* a harness.

## What GT-KB Provides as an IDP

- **Shared specifications** — artifact types, governance rules, canonical
  terminology
- **Runtime services** — bridge protocol, deliberation archive, MemBase
  (knowledge database), dashboard
- **Managed artifacts** — registry-backed rules, hooks, skills, and
  configurations that propagate to adopters via `gt project upgrade`
- **CLI surface** — `gt project init`, `gt project upgrade`,
  `gt project doctor` for adopter lifecycle management
- **Multi-harness integration** — shared conventions and protocols that
  allow Claude Code, Codex, or other AI coding harnesses to participate
  in the same project under unified governance

## First-Mention Convention

When a bridge proposal, report, adopter material, or other document
references GT-KB's role, the first mention in the document should read
"GT-KB (GroundTruth-KB), an Internal Developer Platform" (or a close
variant that preserves all three elements). Subsequent mentions may use
"GT-KB".

## Related Deliberations and Bridges

- `DELIB-GTKB-IDP-TERMINOLOGY` — the owner decision archived for this
  formalization (S305)
- `DELIB-0716`, `DELIB-0722` — prior canonical-terminology governance
  deliberations
- `bridge/gtkb-canonical-terminology-surface-002.md` — governance review
  establishing that canonical terms live in active control surfaces with
  managed-artifact propagation
- `bridge/gtkb-canonical-terminology-surface-implementation-012.md` —
  VERIFIED implementation record for the upstream contract
- `bridge/gtkb-idp-terminology-formalization-*.md` — this thread
- `DELIB-0877` — GTKB-ISOLATION parent decision (adjacent context:
  isolation restructures GT-KB into a parent IDP with applications as
  subdirectories)

## Follow-On Work (Not Part of This Document)

- **`agent-red-canonical-terminology-surface-adoption`** (proposed) — adopt
  GT-KB's managed canonical-terminology artifacts in this repo. After
  that adoption lands, the IDP entry moves into the managed artifact and
  this file can be regenerated or retired.
- **`gtkb-readme-idp-formalization`** (proposed, upstream GT-KB repo) —
  update `groundtruth-kb/README.md` opening paragraph to lead with IDP
  framing.
- **`gtkb-canonical-terminology-idp-entry`** (proposed, upstream GT-KB
  repo) — add IDP to the shipped canonical-terminology surface.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
