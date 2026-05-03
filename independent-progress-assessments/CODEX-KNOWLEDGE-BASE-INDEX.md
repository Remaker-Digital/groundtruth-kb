# Codex Knowledge Base Index - GroundTruth-KB

Purpose: index of Loyal Opposition artifacts maintained for Codex and Prime Builder handoff.

## Active Artifacts

- `CODEX-SESSION-BOOTSTRAP.md`
- `CODEX-SESSION-PROMPT-EXTENSIBILITY.md`
- `CODEX-STANDING-PRIORITIES.md`
- `GROUNDTRUTH-KB-VISION.md`
- `CODEX-WAY-OF-WORKING.md`
- `CODEX-REVIEW-OPERATING-CONTRACT.md`
- `CODEX-LOYAL-OPPOSITION-RUNBOOK.md`
- `CODEX-KNOWLEDGE-BASE-INDEX.md` (this file)
- `CODEX-DECISION-LEDGER.md`
- `CODEX-DEAD-ENDS-AND-FALSE-POSITIVES.md`
- `CODEX-REVIEW-CHECKLISTS.md`
- `TEMPLATE-CODE-REVIEW.md`
- `TEMPLATE-DECISION-MEMO.md`
- `CODEX-INSIGHT-DROPBOX/` (active report dropbox)
- `LOYAL-OPPOSITION-LOG.md` (existing running log)
- `KNOWLEDGE-PROJECT.md` (existing recurring project risks and decisions)
- `KNOWLEDGE-MIKE.md` (existing owner preference context)

## Startup-Loaded Artifact

- Project root `AGENTS.md` defines default Loyal Opposition operating contract.
- `.claude/rules/canonical-terminology.md` is the live canonical glossary and
  must be loaded at startup for both Prime Builder and Loyal Opposition roles.
- `CODEX-SESSION-BOOTSTRAP.md` is the one-file deterministic startup guide for restart behavior and review-mode flags.
- `CODEX-STANDING-PRIORITIES.md` defines persistent Prime-review and bridge-reliability priorities loaded at startup.
- `GROUNDTRUTH-KB-VISION.md` records the owner-stated GroundTruth KB software-factory vision and owner-burden decision filter.
- `CODEX-REVIEW-OPERATING-CONTRACT.md` defines Codex-first review and investigation behavior.

## Legacy Cursor Artifact Location

Legacy Cursor artifacts were moved (not deleted) to:

- `archive/cursor-legacy/CURSOR-KNOWLEDGE-BASE-INDEX.md`
- `archive/cursor-legacy/CURSOR-LOYAL-OPPOSITION-ROLE.md`
- `archive/cursor-legacy/CURSOR-WAY-OF-WORKING.md`
- `archive/cursor-legacy/CURSOR-INSIGHT-DROPBOX/`

## Update Convention

- Keep legacy files immutable unless owner explicitly requests edits.
- Create new assessments in `CODEX-INSIGHT-DROPBOX/`.
- Update this index when new Codex-standard artifacts are introduced.
- Keep review memory artifacts focused on process memory, not canonical project facts already owned by the KB.
