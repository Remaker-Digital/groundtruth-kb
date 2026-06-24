# Claude Design Intake (`gt design import`)

GroundTruth-KB can register a **local Claude Design handoff** — a `.zip`
archive or a directory of design output — into the Deliberation Archive as
governed, metadata-only evidence. This is the productized form of the
previously script-only Agent Red handoff-intake path
(`scripts/archive_claude_design_handoff.py`, PROC-CD-DA-ARCHIVAL-001).

The intake is deliberately narrow: it preserves design **intent and
evidence**, not production code, and it never opens a bridge bypass
(`GOV-CD-PRESERVATION`).

## What it does

```
# Dry run (default): inspect + validate, no MemBase write
gt design import ./ar-widget-handoff.zip --date 2026-04-18 --session-id S302

# Register one content-hash-idempotent report row into the Deliberation Archive
gt design import ./ar-widget-handoff.zip \
    --date 2026-04-18 \
    --session-id S302 \
    --owner-decision "token-only-candidate + net-new-feature-proposals" \
    --apply
```

The pipeline:

1. **Inspect** — lists files and sizes and (for `.zip`) records the archive
   `sha256`. Raw HTML / JSX / CSS / PNG bytes are **never** read into the
   record.
2. **Validate** — checks `SPEC-CD-HANDOFF-FORMAT-001`'s D1 structural
   assertions (`README.md`, `project/index.html`, a `project/*.css`
   design-token source, and at least one `project/*.{jsx,tsx}` component).
   Missing files become non-fatal warnings.
3. **Format** — produces a deterministic inspection record (stable across
   re-runs for the same inputs).
4. **Archive** (`--apply` only) — redacts the record and inserts one `report`
   Deliberation Archive row, idempotent on `(source_ref, content_hash)`. A
   re-run with identical inputs is skipped rather than duplicated.

`--apply` is always explicit; the default is a dry run that performs no
MemBase mutation.

## Options

| Option | Meaning |
|--------|---------|
| `<handoff_path>` | Local `.zip` file or directory to import. |
| `--date` | Handoff date (ISO), e.g. `2026-04-18`. Required. |
| `--session-id` | Session that inspected the handoff. Required. |
| `--owner-decision` | Triage outcome / owner decision text (becomes a DA section). |
| `--notes` | Owner-supplied inspection notes (redaction-safe free text). |
| `--source-ref` | Override the source ref (default `claude-design-handoff:<date>:<name>`). |
| `--apply` | Register the record. Omit for a dry run. |
| `--json` | Emit machine-readable JSON. |

## Non-goals (separately proposed work)

`gt design import` does **not**:

- Integrate with the live Claude Design API
  ([claude.ai/design](https://claude.ai/design)), OAuth, or browser
  automation.
- Treat Claude Design output (HTML/JSX/PPTX/Canva) as production code.
- Generate context packs.
- Add design-artifact lifecycle tables or new MemBase schema.
- Render design dashboards / Grafana panels.
- Run visual verification (screenshot capture, axe/keyboard checks,
  visual-diff galleries).
- Change Agent Red or any adopter application source or UI.

Each of those, if pursued, requires its own proposal with current-source
review and owner prioritization.

## Relationship to the Agent Red script

`scripts/archive_claude_design_handoff.py` remains as a compatibility /
maintainer wrapper. It shares this package pipeline but targets the Agent
Red-scoped `tools/knowledge-db` Deliberation Archive, preserving its
historical behavior. New work should prefer `gt design import`.

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
