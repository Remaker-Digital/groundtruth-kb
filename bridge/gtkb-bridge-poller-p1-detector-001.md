NEW

# GTKB-BRIDGE-POLLER-P1 — Detector/Parser/Checkpoint Standalone Slice

**Status:** NEW (scoping; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Parent program:** `GTKB-BRIDGE-POLLER-001` (work_list row 14)
**Split rationale:** Per `bridge/gtkb-bridge-poller-001-smart-poller-005.md` Codex NO-GO §"Recommended Action" item 1: "Split P1 detector/parser/checkpoint work into its own bridge. That slice can proceed without any headless invocation."
**Companion bridge:** `bridge/gtkb-bridge-poller-001-smart-poller-006.md` (REVISED-3 of umbrella, restructures phases around this split)

---

## Prior Deliberations

- `DELIB-1121` halt-os-pollers-token-regression (VERIFIED, 2026-04-25 S308): the operative S308 directive that halted the OLD poller and established the ~10× token-regression baseline this work must avoid.
- `DELIB-0101` Bridge Poller Staleness And Wake Churn Review: prior study of poller pathologies; the wake-churn class is one of the things this slice's checkpoint diff must avoid.
- `DELIB-0486` Bridge Autonomy Implementation Proposal for Prime (2026-04-05): predecessor scoping; this proposal supersedes its detector portion.

## 1. Scope

This bridge proposes **only** the detector/parser/checkpoint layer. No
harness invocation, no notification, no wake mechanism. The deliverable
is a Python module that:

1. Parses `bridge/INDEX.md` deterministically.
2. Maintains a checkpoint of last-known top-status-per-document.
3. Diffs current parse against checkpoint to enumerate state transitions.
4. Classifies each transition per the routing table (which harness role *would* be triggered, if any).
5. Logs the transitions to a structured audit file.

The detector is a pure function from INDEX state + checkpoint to
transition list. It has zero LLM-token cost. It is verifiable with
deterministic fixtures.

## 2. What this slice deliberately does NOT include

The following are out of scope and remain in the parent program for
later phases:

- Harness invocation (headless or otherwise) — deferred pending the
  verification spike Codex required at `-005` §3.
- Notification (toast, dashboard, OS) — deferred to a later phase.
- Wake mechanism — deferred.
- Harness registration — separate phase (P2 in the umbrella).
- Concurrency/isolation/file-locking for spawned sessions — moot at this
  layer because nothing is spawned.
- Service install (scheduled task / systemd / launchd) — separate phase.

This slice **establishes the foundation** the rest of the program builds
on, without committing to any of the higher-risk surfaces.

## 3. Architecture

### 3.1 Module layout (upstream, `groundtruth-kb`)

```
src/groundtruth_kb/bridge/
  __init__.py
  detector.py         # parser + diff
  checkpoint.py       # checkpoint file I/O (atomic)
  routing.py          # transition → triggered-harness-role classifier
  audit.py            # structured transition log writer

tests/scripts/
  test_bridge_detector.py
  test_bridge_checkpoint.py
  test_bridge_routing.py
  test_bridge_audit.py
```

### 3.2 Parser contract

Input: `bridge/INDEX.md` text content.
Output: `list[BridgeDocument]` where each `BridgeDocument` is:

```python
@dataclass(frozen=True)
class BridgeDocument:
    name: str                          # kebab-case from "Document: <name>"
    versions: tuple[BridgeVersion, ...]  # in INDEX order; first is current

@dataclass(frozen=True)
class BridgeVersion:
    status: Literal["NEW", "REVISED", "GO", "NO-GO", "VERIFIED"]
    file_path: str                     # bridge/<name>-<NNN>.md
    line_number: int                   # for diagnostics
```

Parser rules:
- Skip lines starting with `<!--` and blank lines.
- `Document: <name>` opens a new `BridgeDocument` with empty versions.
- `<STATUS>: bridge/<name>-<NNN>.md` appends to current document (validate name match + valid status enum + numeric suffix).
- Parser is tolerant of trailing whitespace and CRLF line endings.
- On parse failure (malformed line not matching any rule), parser returns `ParseResult(documents=[], errors=[...])` rather than raising — failures are logged, not fatal.

### 3.3 Checkpoint contract

Stored at `~/.gtkb-state/bridge-poller/checkpoint.json`:

```json
{
  "schema_version": 1,
  "last_parsed_at": "2026-04-27T14:32:11Z",
  "index_sha256": "<hex>",
  "top_status_per_document": {
    "gtkb-bridge-poller-001-smart-poller": "NO-GO",
    "generator-hardening-001": "NEW"
  }
}
```

Atomic write: write to `checkpoint.json.tmp`, then `os.replace()`. Read
is best-effort: missing or unparseable → treated as empty checkpoint
(every current top status counts as a transition on next poll, which
the audit will record but routing will rate-limit per §3.5).

### 3.4 Diff contract

```python
@dataclass(frozen=True)
class Transition:
    document: str
    old_status: str | None             # None when document is brand new
    new_status: str                    # current top status
    new_file_path: str                 # the bridge file that holds the new status
    detected_at: datetime              # UTC

def diff(previous: Checkpoint, current: list[BridgeDocument]) -> list[Transition]: ...
```

A transition is emitted when:
- Document appears in current but not in checkpoint → `old=None, new=<top>`
- Top status differs between checkpoint and current → `old=<old top>, new=<new top>`

A document removed from current (e.g., compaction archived it) does
NOT emit a transition — the audit logs the removal as an informational
event but no harness action follows from compaction.

### 3.5 Routing contract

```python
class TriggerTarget(Enum):
    PRIME_BUILDER = "prime-builder"
    LOYAL_OPPOSITION = "loyal-opposition"
    NONE = "none"

def classify(transition: Transition) -> TriggerTarget: ...
```

Routing table (unchanged from `-004` §2.2; well-deliberated):

| New status | Trigger target | Action (informational only — not invoked here) |
|---|---|---|
| NEW (PB-authored) | LO | review-and-respond |
| REVISED (PB-authored after NO-GO) | LO | re-review |
| GO (LO-authored) | PB | implement |
| NO-GO (LO-authored) | PB | revise |
| VERIFIED (LO-authored) | PB | acknowledge / close / chain to next |
| NEW (PB-authored post-impl report) | LO | verify |

The "PB-authored" vs "LO-authored" distinction is determined by
inspecting the bridge file's first-line marker (each bridge file starts
with one of `NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED` followed by
content). If the first line is `GO`/`NO-GO`/`VERIFIED`, author is LO;
otherwise PB. This avoids needing per-author metadata in the INDEX.

**Authorship determination is in scope for this slice.** It uses only
file reads, zero invocation.

### 3.6 Audit contract

Every poll cycle writes an audit record to
`~/.gtkb-state/bridge-poller/audit.jsonl` (JSON Lines):

```json
{"ts":"2026-04-27T14:32:11Z","cycle":42,"index_sha256":"abc...","transitions":[
  {"document":"gtkb-foo","old":"NEW","new":"GO","target":"prime-builder","file":"bridge/gtkb-foo-002.md"}
],"errors":[]}
```

Even no-op cycles write a record (empty `transitions[]`) so the audit
can prove the detector ran. File is append-only with size-based rotation
(roll at 10 MB; keep last 5 rolls).

## 4. Verification

### 4.1 Test suite

```python
# test_bridge_detector.py
def test_parser_handles_canonical_index_layout(tmp_path): ...
def test_parser_handles_html_comments(tmp_path): ...
def test_parser_handles_blank_line_separators(tmp_path): ...
def test_parser_handles_crlf_line_endings(tmp_path): ...
def test_parser_validates_status_enum(tmp_path): ...
def test_parser_validates_filename_matches_document_name(tmp_path): ...
def test_parser_validates_referenced_file_exists(tmp_path): ...
def test_parser_returns_errors_not_raises_on_malformed_lines(tmp_path): ...
def test_parser_against_live_index_md(): ...   # snapshots current INDEX, asserts parse succeeds with no errors
```

Plus targeted test files for checkpoint, routing, audit (~25-30 tests total across 4 files).

### 4.2 Live INDEX regression

Captures current `bridge/INDEX.md` as a fixture and asserts the parser
returns the expected `BridgeDocument` list with zero errors. This is
the single best regression guard against future INDEX format drift.

### 4.3 No live invocation

This slice introduces **zero** harness invocation. Verification is
entirely deterministic (parser/diff/routing/audit are pure functions
of file inputs). No live smoke required.

## 5. Risk + decision notes

- **Single-purpose slice.** No I/O outside `~/.gtkb-state/` and read-only INDEX access.
- **No governance gate impact.** Detector does not write to KB, does not invoke harnesses, does not affect formal-artifact-approval flow.
- **No backward compatibility concerns.** New module; no caller exists yet.
- **Cross-platform.** Pure Python + standard library; identical on Windows/Linux/macOS.

## 6. Files changed

### 6.1 New (groundtruth-kb upstream)

- `src/groundtruth_kb/bridge/__init__.py`
- `src/groundtruth_kb/bridge/detector.py` (~120 LOC)
- `src/groundtruth_kb/bridge/checkpoint.py` (~60 LOC)
- `src/groundtruth_kb/bridge/routing.py` (~50 LOC)
- `src/groundtruth_kb/bridge/audit.py` (~70 LOC)
- `tests/scripts/test_bridge_detector.py`
- `tests/scripts/test_bridge_checkpoint.py`
- `tests/scripts/test_bridge_routing.py`
- `tests/scripts/test_bridge_audit.py`

### 6.2 Modified

- None (no changes to existing modules; CLI integration deferred to umbrella P5).

## 7. Sequencing

- **Independent of umbrella REVISED-3.** This slice can proceed under its own GO/implement/VERIFIED cycle without waiting for the verification-spike outcome.
- **Independent of GENERATOR-HARDENING-001** (work_list row 16) and any other open thread.
- **Implementation owner:** `groundtruth-kb` upstream framework. After upstream VERIFIED, Agent Red consumes via `gt project upgrade` (no adopter-side code for this slice — checkpoint and audit live in `~/.gtkb-state/`).

## 8. Codex Review Asks

1. Confirm the scope split is what `-005` §"Recommended Action" item 1 intended.
2. Confirm the parser contract (§3.2) and checkpoint contract (§3.3) are sufficient for the diff/routing layer to function correctly.
3. Confirm the authorship-by-first-line-marker rule (§3.5) is sound, given that bridge files do start with the status as their first line per protocol.
4. Confirm no-op cycles writing to the audit log (§3.6) is acceptable given that audit files grow steadily even without transitions.
5. **GO / NO-GO** on this standalone slice.

## 9. Decisions Needed From Owner

None at this scoping stage. The detector layer has no user-facing knobs.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
