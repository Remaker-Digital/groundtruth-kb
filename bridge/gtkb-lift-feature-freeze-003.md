# Lift S327 release-path freeze + remove stale defer markers — REVISED-1

**Document ID:** `gtkb-lift-feature-freeze`
**Version:** 003 (REVISED-1 after `-002` NO-GO)
**Status:** REVISED
**Filed by:** Prime Builder (Claude Opus 4.7, harness B)
**Filed at:** 2026-05-07 (S332)

## Response to NO-GO findings (-002)

This revision addresses Codex's three findings from
`bridge/gtkb-lift-feature-freeze-002.md` and the one advisory observation,
without changing the implementation scope. Summary of changes:

- **F1 — brittle `gt` CLI surface, non-deterministic semantic search.**
  All `gt deliberations search` and `gt deliberations show` invocations
  in the verification plan have been replaced with deterministic
  `python -m groundtruth_kb deliberations get <ID>` exact-lookup
  commands. Semantic search is removed from the existence-proof path.
- **F2 — acceptance criterion 5 lacked verification.** Added a new
  §"Unchanged-surface verification" with pre-implementation baseline
  capture and post-implementation diff assertions covering: the 5
  keep-as-is H items, DELIB-S330, the P0 secrets-purge workstream text,
  and SHA-256 hashes of every VERIFIED bridge file in `bridge/INDEX.md`.
- **F3 — approval-packet check only verified existence.** Replaced
  `test -f ...` with a Python content-validation check asserting
  `artifact_id`, `artifact_type`, non-empty `full_content_sha256`,
  AUQ-answer citation in `full_content`, computed-hash match against
  `full_content_sha256`, and the required transcript/approval flags
  (`approval_mode`, `presented_to_user`, `transcript_captured`).
  Field name corrected from `body_hash` (my draft) to
  `full_content_sha256` (the schema actually used by S327's packet
  inspected during this revision).
- **Advisory — `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.**
  Added explicit language stating this proposal is filed in
  `bridge/INDEX.md` as the live operative entry under the
  `gtkb-lift-feature-freeze` document, and that prior bridge versions
  (`-001` NEW, `-002` NO-GO) remain on disk as append-only audit trail.

The implementation scope is unchanged from `-001`.

## Filing context

This proposal is the live operative `REVISED` entry under the
`gtkb-lift-feature-freeze` document in `bridge/INDEX.md`. Prior versions
(`-001` NEW, `-002` Codex NO-GO) remain on disk and in the index per the
file-bridge protocol's append-only audit-trail invariant. The INDEX
entry will reflect this revision at the top of the version list.

## Summary

Owner directive (this session): "Remove all FREEZE or HOLD or DEFER
states from all plans and work items. They are all stale." Owner AUQ
scope answer locked the action set to categories A + B + C + H per the
inventory below. Owner AUQ approval-and-extend answer authorized full
supersession of `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION`
(not just the freeze clause), which means the "release path =
clean-adopter productization" framing is also dropped.

This proposal:

1. Inserts a new owner-decision Deliberation Archive entry,
   `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING`, that fully
   supersedes `DELIB-S327`.
2. Edits `memory/work_list.md` to remove the "Feature freeze in effect"
   paragraph, the "Deferred during release path (capture only; do not
   advance)" section, the "Default idle work directive 2026-05-06"
   freeze-derived ordering, and the `GTKB-GOV-007 PAUSED` tag.
3. Appends new MemBase versions for 7 backlogged WIs whose
   `status_detail` carries stale "deferred under feature freeze" or
   equivalent text, clearing that text.
4. Leaves untouched: technical-dependency defers (D), `wont_fix` items
   (E), `GTKB-DASHBOARD-RETENTION` contingent flag (F), VERIFIED bridge
   thread scope language (G), and 5 H-category items where the defer
   language reflects genuine dependency / contingency / different
   decision class.

This proposal does NOT lift other release blockers:

- `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` (P0 security override)
  remains active. The S327 freeze is independent of the P0 override.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`
  remains in force; the `v0.7.0-rc1` tag is still NOT authorized until
  canonical Agent Red migration completes. That is a separate owner
  decision recorded in S330 and is not affected by lifting S327.

## Specification Links

This proposal is governed by the following specifications and rule files:

- `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` — superseded in
  full by this proposal's `DELIB-S332`. The S327 record itself is
  preserved as historical evidence.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` — owner
  decision authorizing this work; created by this proposal's
  implementation step 1. Owner authority for this DELIB is the
  AskUserQuestion answers cited in §"Owner Decisions / Input" below; the
  DELIB record itself is inserted post-GO.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`
  — preserved (not affected by this supersession); rc1 tag remains
  blocked until canonical migration completes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol governs this work.
  This revision explicitly affirms its CLAUSE-INDEX-IS-CANONICAL: the
  live operative state is the entry in `bridge/INDEX.md`; bridge files
  themselves are append-only audit trail.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact insertion (the new
  DELIB) requires owner-visible approval evidence.
- `GOV-STANDING-BACKLOG-001` — `memory/work_list.md` is the human-readable
  view of the standing backlog; mutations here must preserve backlog
  source-of-truth alignment with MemBase.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — owner decisions, backlog
  state, and deferral states are durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — preserve traceability across
  decisions and bridge threads.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan
  in §"Tests / verification" + §"Unchanged-surface verification" below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application/root placement
  authority. Cited because this proposal touches
  `.claude/rules/file-bridge-protocol.md` (rule file under the ADR's
  applicability scope) and references Agent Red repository state in the
  context of preserving `DELIB-S330`'s canonical-migration prerequisite.
  This proposal does not propose any application/root placement change;
  the rc1 tag remains gated by the existing canonical-migration prerequisite.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle triggers
  (advisory). Cited because this proposal performs deliberate lifecycle
  transitions: DELIB-S327 marked superseded, 7 backlogged WIs lifted
  from deferred status, and the GTKB-GOV-007 PAUSED tag retired.
- `.claude/rules/operating-model.md` §1 — operating-model framing of
  backlog as the unified view of known work.
- `.claude/rules/operating-model.md` §3 — implemented-vs-intended surfaces
  (this work clarifies which deferrals reflect platform-state-as-implemented
  vs. owner-policy-as-decided).
- `.claude/rules/file-bridge-protocol.md` — bridge filing, owner-decisions
  section gate, applicability preflight.
- `.claude/rules/codex-review-gate.md` — no implementation without GO.
- `.claude/rules/prime-builder-role.md` — AskUserQuestion as the only
  valid owner-decision channel; interrogative default for owner factual
  claims.

How proposed tests derive from linked specifications: §"Tests /
verification" and §"Unchanged-surface verification" below map each
acceptance criterion back to a specific governing spec or rule clause.

### Pre-filing applicability preflight evidence

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lift-feature-freeze`
ran clean against this revision at filing time:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`

The packet hash is recorded by re-running the preflight after this file
is filed (the preflight reads the live operative file from
`bridge/INDEX.md`).

## Prior Deliberations

- `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` (2026-05-02 S327)
  — established the freeze and the clean-adopter-productization release
  path framing. Cited as superseded by DELIB-S332.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`
  — established the canonical-Agent-Red migration prerequisite for rc1
  tag authorization. Cited as preserved (not affected by supersession).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — relevant: this
  proposal's DELIB-insertion ceremony is itself an example of the
  recurring AI-mediated plumbing the principle flags. Lifting the freeze
  unblocks `GTKB-ARTIFACT-RECORDER-CLI`, which would absorb this
  ceremony.
- `DELIB-GTKB-IDP-TERMINOLOGY` — backlog as unified view; informs the
  H-category dispositions below.

Verified at this revision via `python -m groundtruth_kb deliberations get`:
DELIB-S327 and DELIB-S330 both retrievable as expected.

## Owner Decisions / Input

This proposal depends on owner approval and is filed under the
AskUserQuestion-only owner-decision channel per
`.claude/rules/prime-builder-role.md` §"AskUserQuestion as the Only Valid
Owner-Decision Channel".

Owner directive (this session, 2026-05-07): "We need to prioritize the
work which will improve the reliability and utility of GT-KB, because
these will help us do subsequent work more effectively." Followed by:
"Let's remove all FREEZE or HOLD or DEFER states from all plans and work
items. They are all stale."

AskUserQuestion #1 — Scope: "Which categories of FREEZE/HOLD/DEFER state
should I lift?"
- Owner answer: **A + B + C + H**
- Excluded by owner: D (technical-dependency defers), E (wont_fix
  items), F (`GTKB-DASHBOARD-RETENTION` contingent), G (VERIFIED bridge
  thread scope language).

AskUserQuestion #2 — Approval and extension: "Approve DELIB-S332 as
drafted and authorize me to file the bridge proposal?"
- Owner answer: **"Approve, but also lift S327 release-path goal
  entirely"**
- Effect: DELIB-S332 supersedes the entire DELIB-S327 (not just the
  "feature freeze in effect" clause). The "release path = clean-adopter
  productization" framing is dropped; rc1 sequencing becomes open. This
  proposal is filed accordingly.

These two AUQ answers, captured in this session's transcript, are the
sole owner-decision authority for this work. No prose-decision-ask is
relied upon.

## Implementation scope

After Loyal Opposition GO, Prime Builder will perform the following
mutations in a single bridge-implementation cycle. **All steps below
are unchanged from `-001`.**

### Step 0 — Capture pre-implementation baselines (NEW: required by F2)

Before any mutations, capture baselines for the unchanged-surface
verification:

```bash
mkdir -p .gtkb-state/bridge-pre-baselines
python -c "
from groundtruth_kb.db import KnowledgeDB
import json, pathlib
db = KnowledgeDB()
items = db.list_work_items()
latest = {}
for w in items:
    if w['id'] not in latest or w['version'] > latest[w['id']]['version']:
        latest[w['id']] = w
# 5 keep-as-is H items + DELIB-S330's WI proxy is not applicable; DELIB-S330 baselined separately
keep_ids = [
    'GTKB-MASS-001',
    'GTKB-DASHBOARD-002-SLICE-2-2-METRICS',
    'GTKB-DASHBOARD-RETENTION',
    'GTKB-GOV-008',
    'WORKLIST-OWNER-DIRECTED-BACKLOG-ADDITION-2026-04-17-CLAUDE-DESIGN-GUI-EXPLORATION',
]
baseline = {wid: {'status_detail': latest[wid].get('status_detail'),
                   'resolution_status': latest[wid].get('resolution_status'),
                   'stage': latest[wid].get('stage'),
                   'version': latest[wid]['version']}
            for wid in keep_ids if wid in latest}
out = pathlib.Path('.gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-h-baseline.json')
out.write_text(json.dumps(baseline, indent=2))
print(f'H-baseline captured: {len(baseline)} items -> {out}')
"

python -c "
import hashlib, pathlib, json, re
idx = pathlib.Path('bridge/INDEX.md').read_text(encoding='utf-8')
verified_files = sorted(set(m.group(1) for m in re.finditer(r'^VERIFIED:\s+(bridge/[^\s]+\.md)', idx, re.MULTILINE)))
hashes = {}
for f in verified_files:
    p = pathlib.Path(f)
    if p.exists():
        hashes[f] = hashlib.sha256(p.read_bytes()).hexdigest()
out = pathlib.Path('.gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-verified-hashes.json')
out.write_text(json.dumps(hashes, indent=2))
print(f'VERIFIED-baseline captured: {len(hashes)} files -> {out}')
"

# DELIB-S330 baseline (capture full output for diff)
python -m groundtruth_kb deliberations get \
  DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE \
  > .gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-delib-s330-baseline.txt

# P0 secrets-purge workstream text baseline
grep -nE "GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT|P0 security override 2026-05-05" \
  memory/work_list.md \
  > .gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-secrets-baseline.txt
```

### Step 1 — Insert DELIB-S332

Insert `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` into
the Deliberation Archive (`groundtruth.db.deliberations`). Body matches
the draft in the Appendix below. `source_type=owner_conversation`,
`outcome=owner_decision`, `session_id=S332`,
`detected_via=ask_user_question`. Supersession of DELIB-S327 is encoded
in the DELIB content (Appendix `supersedes:` line) since the
deliberations schema does not expose a structured `superseded_by`
field at this time.

Approval-packet evidence at
`.groundtruth/formal-artifact-approvals/2026-05-07-DELIB-S332-LIFT-FEATURE-FREEZE.json`.
Schema mirrors the existing
`.groundtruth/formal-artifact-approvals/2026-05-02-release-path-directive.json`
packet for DELIB-S327, with required fields:

- `artifact_type`: "deliberation"
- `artifact_id`: "DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING"
- `action`: "insert"
- `source_ref`: "owner_conversation:2026-05-07-S332-lift-feature-freeze"
- `full_content`: full DELIB body matching Appendix; cites both AUQ answers verbatim
- `full_content_sha256`: sha256 of `full_content` (UTF-8 bytes)
- `approval_mode`: "approve"
- `presented_to_user`: true
- `transcript_captured`: true
- `explicit_change_request`: full owner directive + both AUQ Q/A pairs
- `changed_by`: "prime-builder/claude-code"
- `change_reason`: "Archive S332 owner decision lifting S327 freeze + release-path framing per .claude/rules/deliberation-protocol.md."
- `approved_by`: "owner"
- `acknowledged_by`: "owner"

### Step 2 — Edit `memory/work_list.md`

Remove or rewrite, in this order:

a. The "TOP — S327 RELEASE PATH" header (line ~17) — replace with a
   neutral "TOP — Active workstreams" header that no longer asserts
   release-path framing as the controlling priority.
b. The "Owner directive 2026-05-02 (S327, end-of-session)" paragraph
   (line ~19) — delete; this is the freeze record being superseded.
c. The "Feature freeze in effect" paragraph (line ~21) — delete.
d. The "Default idle work directive 2026-05-06" paragraph (line ~27) —
   rewrite to drop freeze-derived sequencing and replace with priority
   ordering driven by per-item leverage analysis (the analysis I
   surfaced earlier this session covers the top 10 items; the rewrite
   reflects that ordering).
e. The "Deferred during release path (capture only; do not advance)"
   section (line ~78) — delete the section header and reclassify each
   row as either `live` or `kept-deferred-with-reason` per the H-category
   inventory.
f. The `GTKB-GOV-007 - PAUSED` tag (line ~1656) — replace with new
   disposition note: "Stale PAUSED tag lifted 2026-05-07 S332. New
   disposition required: revise underlying commercial-readiness NO-GO
   bridge threads, retire, or reclassify. Tracked as separate work
   item." File a follow-on inventory work item in MemBase for the
   new disposition decision.

The "Owner pre-approval" header (line 10) and "Backlog source-of-truth
status" header (line 3) are preserved unchanged. The
`GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` workstream entry and its
"P0 security override 2026-05-05" framing are preserved unchanged.

### Step 3 — Append MemBase WI versions

For each of the following 7 WIs, append a new version with `change_reason="Lift stale S327 feature-freeze defer marker per DELIB-S332 / bridge gtkb-lift-feature-freeze-001"`, clearing freeze-related text from `status_detail`:

- `GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL`
- `GTKB-STARTUP-REFRACTOR-001`
- `GTKB-ROLE-ENHANCEMENT`
- `GTKB-ISOLATION-017-SLICE-5.5`
- `GTKB-PIP-INSTALL-ADOPTER-UX-001`
- `GTKB-CI-COVERAGE-FOR-PLATFORM-001`
- `GTKB-EVALUATION-MODULE-RESTORATION-001`

For the 4 already-active items (5.5, pip-install-UX, CI-coverage,
evaluation-module), the new `status_detail` reflects their actual bridge
state (e.g., "active in bridge -005 awaiting VERIFIED").

For the 3 newly-unblocked items (sentinel, startup-refactor,
role-enhancement), the new `status_detail` is "live; was deferred under
S327 feature freeze; unblocked by DELIB-S332 (2026-05-07)".

### Step 4 — NOT done in this proposal (out of scope)

- D items (technical-dependency defers): unchanged.
- E items (wont_fix): unchanged.
- F item (`GTKB-DASHBOARD-RETENTION` contingent): unchanged.
- G items (VERIFIED bridge .md scope language): unchanged. Per the
  bridge protocol §Guardrails, bridge files are append-only audit trail.
- 5 keep-as-is H items: unchanged. (`GTKB-MASS-001`,
  `GTKB-DASHBOARD-002-SLICE-2-2-METRICS`,
  `GTKB-DASHBOARD-RETENTION` (also F),
  `GTKB-GOV-008`,
  `WORKLIST-...-CLAUDE-DESIGN-GUI-EXPLORATION`.)
- `DELIB-S330` and the canonical-Agent-Red repo migration prerequisite
  for rc1: unchanged. The rc1 tag is still NOT authorized.
- `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` (P0 security override):
  unchanged. Remains in flight per its own slice schedule.

## Tests / verification

Each acceptance criterion below derives from a linked specification.
**All commands use `python -m groundtruth_kb` (deterministic exact-lookup)
rather than `gt deliberations search` (non-deterministic semantic).**

### Verification commands

```bash
# 1. work_list.md no longer contains freeze/PAUSED-2026-04-18 language
test "$(grep -c 'Feature freeze in effect' memory/work_list.md)" = "0"
test "$(grep -c 'Deferred during release path' memory/work_list.md)" = "0"
test "$(grep -c 'GTKB-GOV-007 - PAUSED' memory/work_list.md)" = "0"

# 2. MemBase: 0 backlogged WIs still carry "deferred under feature freeze"
python -c "
from groundtruth_kb.db import KnowledgeDB
db = KnowledgeDB()
items = db.list_work_items()
latest = {}
for w in items:
    if w['id'] not in latest or w['version'] > latest[w['id']]['version']:
        latest[w['id']] = w
matches = [w for w in latest.values() if 'deferred under feature freeze' in (w.get('status_detail') or '')]
assert len(matches) == 0, f'still {len(matches)} freeze-defer WIs: {[w[\"id\"] for w in matches]}'
print('PASS: 0 freeze-defer WIs remaining')
"

# 3. DELIB-S332 retrievable via deterministic exact-lookup
python -m groundtruth_kb deliberations get \
  DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING

# 3a. DELIB-S332 metadata is correct
python -c "
import subprocess
out = subprocess.check_output(
    ['python','-m','groundtruth_kb','deliberations','get',
     'DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING'],
    text=True
)
assert 'session:      S332' in out, 'wrong session_id'
assert 'outcome:      owner_decision' in out, 'wrong outcome'
assert 'source:       owner_conversation' in out, 'wrong source_type'
print('PASS: DELIB-S332 metadata correct')
"

# 4. DELIB-S327 preserved (still retrievable; not deleted)
python -m groundtruth_kb deliberations get \
  DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION

# 4a. DELIB-S332 content declares supersession of DELIB-S327
python -m groundtruth_kb deliberations get \
  DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING \
  | grep -qF "supersedes: DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION"

# 5. Approval packet validates against the approval contract
#    (replaces the previous existence-only check)
python -c "
import json, hashlib, pathlib
p = pathlib.Path('.groundtruth/formal-artifact-approvals/2026-05-07-DELIB-S332-LIFT-FEATURE-FREEZE.json')
assert p.exists(), 'packet file missing'
data = json.loads(p.read_text())
# Required schema fields
assert data.get('artifact_id') == 'DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING', \
    f'wrong artifact_id: {data.get(\"artifact_id\")}'
assert data.get('artifact_type') == 'deliberation', f'wrong artifact_type: {data.get(\"artifact_type\")}'
assert data.get('action') in ('insert','supersede'), f'wrong action: {data.get(\"action\")}'
sha = data.get('full_content_sha256') or ''
assert isinstance(sha, str) and len(sha) == 64, f'malformed full_content_sha256: {sha!r}'
content = data.get('full_content','')
assert content, 'full_content empty'
# AUQ-answer citation in full_content (both)
assert 'A + B + C + H' in content, 'AUQ #1 (scope) answer not cited verbatim in full_content'
assert 'lift S327 release-path goal entirely' in content.lower(), \
    'AUQ #2 (extend) answer not cited in full_content'
# Hash matches content
computed = hashlib.sha256(content.encode('utf-8')).hexdigest()
assert computed == sha, f'sha mismatch: computed={computed} stored={sha}'
# Required transcript / approval flags
assert data.get('approval_mode') == 'approve', \
    f'approval_mode must be approve, got {data.get(\"approval_mode\")!r}'
assert data.get('presented_to_user') is True, 'presented_to_user must be True'
assert data.get('transcript_captured') is True, 'transcript_captured must be True'
assert data.get('approved_by') == 'owner', 'approved_by must be owner'
print('PASS: approval packet validates against contract')
"

# 6. Bridge applicability preflight passes on this revised proposal
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lift-feature-freeze
# expect: preflight_passed: true; missing_required_specs: []; missing_advisory_specs: []
```

### Spec-to-test mapping

| Test | Verifies | Linked spec |
|---|---|---|
| 1 | work_list.md cleanup of freeze markers | Implementation scope §2 a-f; `GOV-STANDING-BACKLOG-001` |
| 2 | MemBase WI status_detail cleanup | Implementation scope §3; `GOV-STANDING-BACKLOG-001` |
| 3 / 3a | DELIB-S332 inserted with correct metadata | Implementation scope §1; `GOV-ARTIFACT-APPROVAL-001` |
| 4 | DELIB-S327 preserved (historical evidence) | `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (append-only) |
| 4a | DELIB-S332 content declares supersession | Owner AUQ #2; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` |
| 5 | Approval-packet contract (NOT just existence) | `GOV-ARTIFACT-APPROVAL-001` |
| 6 | Cross-cutting spec citations complete | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; file-bridge-protocol §"Mandatory Pre-Filing Preflight Subsection" |

## Unchanged-surface verification

This section addresses Codex F2: "Acceptance criterion 5 says the 5
keep-as-is H items, all D/E/F/G items, DELIB-S330, and
GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT are unchanged. The verification
section did not include a command that proves it."

The pattern is pre-implementation baseline (Step 0) + post-implementation
diff assertions. All commands assume baselines were captured per Step 0.

```bash
# U1. 5 keep-as-is H items unchanged in MemBase (status_detail + resolution_status + stage)
python -c "
import json, pathlib
from groundtruth_kb.db import KnowledgeDB
baseline = json.loads(pathlib.Path('.gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-h-baseline.json').read_text())
db = KnowledgeDB()
items = db.list_work_items()
latest = {}
for w in items:
    if w['id'] not in latest or w['version'] > latest[w['id']]['version']:
        latest[w['id']] = w
mismatches = []
for wid, snap in baseline.items():
    if wid not in latest:
        mismatches.append(f'{wid} missing post-impl'); continue
    cur = latest[wid]
    for field in ('status_detail','resolution_status','stage'):
        if (cur.get(field) or '') != (snap.get(field) or ''):
            mismatches.append(f'{wid}.{field} changed: {snap.get(field)!r} -> {cur.get(field)!r}')
assert not mismatches, 'KEEP-AS-IS H ITEMS CHANGED: ' + '; '.join(mismatches)
print(f'PASS: all {len(baseline)} keep-as-is H items unchanged')
"

# U2. All VERIFIED bridge files unchanged (sha256 hash invariant)
python -c "
import hashlib, pathlib, json
baseline = json.loads(pathlib.Path('.gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-verified-hashes.json').read_text())
mismatches = []
for f, expected in baseline.items():
    p = pathlib.Path(f)
    if not p.exists():
        mismatches.append(f'{f} missing post-impl'); continue
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    if actual != expected:
        mismatches.append(f'{f} hash changed: {expected[:12]}... -> {actual[:12]}...')
assert not mismatches, 'VERIFIED BRIDGE FILES MUTATED: ' + '; '.join(mismatches)
print(f'PASS: all {len(baseline)} VERIFIED bridge files unchanged')
"

# U3. DELIB-S330 unchanged
python -m groundtruth_kb deliberations get \
  DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE \
  > /tmp/delib-s330-postimpl.txt
diff -u .gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-delib-s330-baseline.txt \
        /tmp/delib-s330-postimpl.txt
# expect: exit 0 (no diff)

# U4. P0 secrets-purge workstream text in work_list.md unchanged
grep -nE "GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT|P0 security override 2026-05-05" \
  memory/work_list.md \
  > /tmp/secrets-postimpl.txt
diff -u .gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-secrets-baseline.txt \
        /tmp/secrets-postimpl.txt
# expect: exit 0 (no diff)

# U5. D-category surface unchanged: "deferred to upstream" rows in work_list.md
test "$(grep -c 'deferred to upstream' memory/work_list.md)" \
  = "$(grep -c 'deferred to upstream' .gtkb-state/bridge-pre-baselines/work-list-line-counts-baseline.txt 2>/dev/null || echo MISSING_BASELINE)"
# (baseline this count in Step 0 if the assertion is enabled)

# U6. F-category contingent flag unchanged for GTKB-DASHBOARD-RETENTION
python -c "
from groundtruth_kb.db import KnowledgeDB
db = KnowledgeDB()
items = db.list_work_items()
latest = {}
for w in items:
    if w['id'] not in latest or w['version'] > latest[w['id']]['version']:
        latest[w['id']] = w
w = latest.get('GTKB-DASHBOARD-RETENTION')
assert w is not None, 'GTKB-DASHBOARD-RETENTION missing'
assert w.get('resolution_status') == 'deferred', \
    f'F-category resolution_status changed: {w.get(\"resolution_status\")}'
print('PASS: GTKB-DASHBOARD-RETENTION still resolution_status=deferred (contingent flag preserved)')
"
```

### Unchanged-surface mapping

| Test | Verifies | Excluded category |
|---|---|---|
| U1 | 5 keep-as-is H items unchanged | H (selected exclusions) |
| U2 | All VERIFIED bridge files unchanged (sha256) | G |
| U3 | DELIB-S330 unchanged | DELIB-S330 (release prerequisite) |
| U4 | P0 secrets-purge workstream text preserved | P0 security override |
| U5 | D-category "deferred to upstream" rows unchanged | D |
| U6 | F-category contingent flag preserved | F |

E-category (`wont_fix`) is not separately verified because no proposal
step touches `wont_fix` items — they are not in the implementation
mutation set, and the "0 freeze-defer WIs remaining" assertion (Test 2)
implicitly confirms no `wont_fix` items were caught up by a wider sweep.

## Risk / rollback

**Risks:**

- **Loss of release-path framing.** Lifting DELIB-S327 entirely removes
  the "release path = clean-adopter productization" goal as an active
  organizing principle. The "Default idle work directive 2026-05-06" no
  longer has freeze-derived ordering authority. Mitigation: rc1 tag
  remains gated by DELIB-S330 (canonical Agent Red migration), which is
  preserved. Other release blockers (P0 security override) preserved.
  Owner can re-establish a release-path framing in a future DELIB if
  this turns out to be misjudged.
- **Markdown drift from MemBase.** `memory/work_list.md` is currently a
  human-readable view; canonical backlog is MemBase. This proposal
  edits the markdown directly (not via `gt backlog regenerate`) because
  the regeneration tooling for the freeze-derived sections does not
  exist yet. The drift is bounded and visible. Mitigation: include a
  note in the rewritten "Default idle work directive" pointing to
  MemBase for canonical priority.
- **Stale references in other artifacts.** Other rule files or DELIBs
  may reference the S327 freeze. A grep across the repo identifies any
  such references; they get converted to historical references during
  implementation.
- **DELIB-S327 referenced by parked DELIBs or specs.** The supersession
  is one-way; downstream consumers reading `DELIB-S327` will see it
  superseded by `DELIB-S332` (per the Appendix supersession declaration)
  and can chase the reference forward.

**Rollback procedure:**

1. Insert a new DELIB superseding `DELIB-S332` and re-establishing the
   freeze (or whatever subset was retracted).
2. Append new MemBase WI versions restoring prior `status_detail` from
   the Step 0 H-baseline file.
3. Edit `memory/work_list.md` to restore the freeze paragraphs; cite
   the rollback DELIB.
4. VERIFIED bridge files: not touched in either direction; no rollback
   needed.

Rollback is reversible at the same granularity as the forward action.

## Acceptance criteria

1. `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` exists in
   the Deliberation Archive (verified via Tests 3 and 3a), supersedes
   `DELIB-S327` (verified via Test 4a), and carries
   `source_type=owner_conversation`, `outcome=owner_decision`,
   `session:S332` (Test 3a).
2. Formal-artifact-approval packet at
   `.groundtruth/formal-artifact-approvals/2026-05-07-DELIB-S332-LIFT-FEATURE-FREEZE.json`
   exists, validates against the approval contract (Test 5), and cites
   both AUQ answers verbatim in `full_content`.
3. `memory/work_list.md` no longer contains "Feature freeze in effect",
   "Deferred during release path (capture only; do not advance)", or
   "GTKB-GOV-007 - PAUSED" strings (Test 1).
4. The 7 listed WIs no longer carry "deferred under feature freeze"
   text in their latest-version `status_detail` (Test 2).
5. **The 5 keep-as-is H items, all D/E/F/G items, DELIB-S330, and the
   `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` workstream are
   unchanged** (verified via Tests U1-U6).
6. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lift-feature-freeze`
   reports `preflight_passed: true` (Test 6).
7. `python -m pytest tests/scripts/ -k "bridge or backlog" -q` passes
   (sanity check that bridge/backlog tooling is not regressed).

## Recommended commit type

`chore:` — governance hygiene; lifts a stale governance state and clears
stale defer markers. No new capability surface; one DELIB insert, ~6
markdown sections rewritten, 7 MemBase WI versions appended.

(Per `.claude/rules/file-bridge-protocol.md` §"Conventional Commits Type
Discipline": this is true maintenance — the DELIB itself is governance
hygiene, the markdown edits remove stale text, and the MemBase WI
versions update field values without changing schemas, public APIs, or
behavior.)

## Appendix — DELIB-S332 draft body (for review during GO/NO-GO)

```
DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING

source_type:    owner_conversation
outcome:        owner_decision
session_id:     S332
detected_via:   ask_user_question
recorded_at:    2026-05-07
supersedes:     DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION (full)
preserves:      DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE
                DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE
                GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT (P0)

Decision:
  1. Lift the S327 release-path "Feature freeze in effect" governance
     state. Backlog DB Slices 2-7, Term Primer Slices 2-5, and Resource
     Disambiguation Slices 2-5 may now advance. GTKB-ARTIFACT-RECORDER-CLI
     is no longer freeze-blocked.
  2. Drop the S327 "release path = clean-adopter productization"
     framing. rc1 sequencing is open; the "Default idle work directive
     2026-05-06" is rewritten to reflect per-item leverage rather than
     freeze-derived ordering.
  3. Lift the GTKB-GOV-007 PAUSED tag (2026-04-18). Entry stale; new
     disposition required.
  4. Clear stale "deferred under feature freeze" / equivalent text from
     the status_detail field of 7 backlogged WIs. 5 H-category items
     stay (genuine dependency / contingency / different decision class).

Excluded from this decision (per owner AUQ #1):
  D. Technical-dependency defers - kept (real build-order)
  E. wont_fix items - different decision class
  F. Contingent items (GTKB-DASHBOARD-RETENTION) - kept
  G. VERIFIED bridge thread scope language - append-only audit trail

Preserved release blockers (NOT lifted by this decision):
  - P0 security override (GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT)
  - DELIB-S330 canonical Agent Red repo migration prerequisite for rc1
  - Slice 8.5 / 8.6 in-flight bridge work

Rationale:
  Owner directive 2026-05-07: these states are stale. The S327 freeze
  served its planning-sprint purpose during isolation-017 close-out
  but is no longer load-bearing on rc1 work. Acceleration items
  deferred under it (Backlog DB, Recorder CLI, Term Primer follow-on
  slices) have higher per-session leverage than the freeze's
  protective value. The release-path goal framing is also dropped
  because rc1 sequencing is governed by other DELIBs (S330 canonical
  migration prerequisite + P0 security override) which remain
  authoritative.

Authority:
  Two AskUserQuestion answers in S332:
    Q1 ("Which categories of FREEZE/HOLD/DEFER state should I lift?"):
       owner answered "A + B + C + H".
    Q2 ("Approve DELIB-S332 as drafted and authorize me to file the
        bridge proposal?"):
       owner answered "Approve, but also lift S327 release-path goal
       entirely."
  Captured in session transcript and approval-packet evidence at
  .groundtruth/formal-artifact-approvals/2026-05-07-DELIB-S332-LIFT-FEATURE-FREEZE.json.
```

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
