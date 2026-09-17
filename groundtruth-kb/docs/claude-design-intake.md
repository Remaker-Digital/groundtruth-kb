# Claude Design Handoff Inspection (`gt design inspect`)

GroundTruth-KB can inspect a **local Claude Design handoff** — a `.zip`
archive or a directory of design output — and report what it contains as
metadata-only evidence. The inspection is read-only: it lists files and
sizes, records the archive `sha256`, checks the handoff format and prints a
deterministic, redacted inspection record. It publishes nothing. The former
automatic publication of the record into the deliberation archive is retired
with that archive's live workflow; the operator decides what to do with the
report.

The inspection is deliberately narrow: it preserves design **intent and
evidence**, not production code, and it never opens a bridge bypass
(`GOV-CD-PRESERVATION`).

## What it does

```
# Text report
gt design inspect ./ar-widget-handoff.zip --date 2026-04-18 --session-id S302

# Complete report as canonical JSON
gt design inspect ./ar-widget-handoff.zip \
    --date 2026-04-18 \
    --owner-decision "token-only-candidate + net-new-feature-proposals" \
    --json
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
4. **Redact** — replaces credential and PII matches from the canonical
   pattern catalog with `[REDACTED:<name>]` markers and reports what was
   redacted; the `content_hash` is computed over the redacted record.

Nothing is stored. Identical inputs reproduce the same `content_hash`, so an
operator who keeps reports can recognise a repeat inspection.

## Options

| Option | Meaning |
|--------|---------|
| `<handoff>` | Local `.zip` file or directory to inspect. A missing path is a usage error; any other kind of path is refused. |
| `--date` | Handoff date (ISO), e.g. `2026-04-18`. Today's date when omitted. |
| `--session-id` | Session that inspected the handoff, when one is bound. Omitted from the record otherwise. |
| `--owner-decision` | Triage outcome / owner decision text (becomes a record section). |
| `--notes` | Inspection notes (free text; redacted like the rest of the record). |
| `--json` | Emit the complete report as canonical JSON (`source_path`, `source_kind`, `sha256`, `total_bytes`, `file_count`, `entries`, `warnings`, `content`, `content_hash`, `redaction_notes`). |

## Non-goals (separately proposed work)

`gt design inspect` does **not**:

- Integrate with the live Claude Design API
  ([claude.ai/design](https://claude.ai/design)), OAuth, or browser
  automation.
- Treat Claude Design output (HTML/JSX/PPTX/Canva) as production code.
- Generate context packs.
- Store the inspection record anywhere, or add design-artifact lifecycle
  tables or schema.
- Render design dashboards / Grafana panels.
- Run visual verification (screenshot capture, axe/keyboard checks,
  visual-diff galleries).
- Change Agent Red or any adopter application source or UI.

Each of those, if pursued, requires its own proposal with current-source
review and owner prioritization.

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
