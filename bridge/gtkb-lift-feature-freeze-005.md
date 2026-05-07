# Lift S327 release-path freeze + remove stale defer markers — REVISED-2

**Document ID:** `gtkb-lift-feature-freeze`
**Version:** 005 (REVISED-2 after `-004` NO-GO)
**Status:** REVISED
**Filed by:** Prime Builder (Claude Opus 4.7, harness B)
**Filed at:** 2026-05-07 (S332)

## Response to NO-GO findings (-004)

This revision addresses Codex's four findings from
`bridge/gtkb-lift-feature-freeze-004.md`. Implementation scope is unchanged;
verification rigor and post-implementation `status_detail` text are corrected.

- **F1 — DELIB-S332 metadata verification used brittle stdout-substring
  parsing.** All metadata assertions now use
  `KnowledgeDB.get_deliberation()` returning a structured dict, accessing
  `session_id`, `outcome`, and `source_type` fields directly. CLI padding
  is no longer load-bearing.
- **F2 — approval-packet AUQ #2 assertion was always false.** Both sides
  of the substring check are now lowercased (`'lift s327 release-path goal
  entirely' in content.lower()`). The case-sensitivity bug is removed.
- **F3 — D-category baseline file referenced but never captured.**
  Step 0 now captures three additional deterministic JSON baselines —
  `d-baseline.json` (WIs whose `status_detail` mentions "deferred to
  upstream"), `e-baseline.json` (all WIs with `resolution_status='wont_fix'`),
  and an explicit `f-baseline.json` for `GTKB-DASHBOARD-RETENTION` —
  capturing stable WI IDs + field values, not grep counts. U5 and a new
  U7 (E-category) and updated U6 (F-category) consume those JSON files
  via the same diff pattern as U1.
- **F4 — new `status_detail` text reintroduced freeze/defer language
  the test was supposed to catch.** Step 3 now sets `status_detail` to
  current-state-only text with no freeze/defer/hold/paused/parked
  vocabulary. Historical context (the prior `status_detail`, the
  superseding DELIB) is moved to the `change_reason` field where it
  belongs by the append-only-versioning contract. Test 2 is broadened
  from a single-substring search to a regex covering
  `freeze|frozen|defer|deferred|hold|paused|parked`, run against the
  7 cleared WIs, so any future regression of this class fails the test.

## Filing context

This proposal is the live operative `REVISED` entry under the
`gtkb-lift-feature-freeze` document in `bridge/INDEX.md`. Prior versions
(`-001` NEW, `-002` Codex NO-GO, `-003` REVISED, `-004` Codex NO-GO)
remain on disk and in the index per the file-bridge protocol's
append-only audit-trail invariant.

## Summary

Owner directive (this session): "Remove all FREEZE or HOLD or DEFER
states from all plans and work items. They are all stale." Owner AUQ
scope answer locked the action set to categories A + B + C + H. Owner
AUQ approval-and-extend answer authorized full supersession of
`DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` (not just the
freeze clause).

This proposal:

1. Inserts owner-decision Deliberation Archive entry
   `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` superseding
   `DELIB-S327` in full.
2. Edits `memory/work_list.md` to remove the "Feature freeze in effect"
   paragraph, the "Deferred during release path" section, the
   "Default idle work directive 2026-05-06" freeze-derived ordering,
   and the `GTKB-GOV-007 PAUSED` tag.
3. Appends new MemBase versions for 7 backlogged WIs whose
   `status_detail` carries stale freeze/defer text. New `status_detail`
   contains no freeze/defer/hold/paused/parked language; historical
   context lives in `change_reason`.
4. Leaves untouched: technical-dependency defers (D), `wont_fix` items
   (E), `GTKB-DASHBOARD-RETENTION` contingent flag (F), VERIFIED bridge
   thread scope language (G), 5 H-category items, `DELIB-S330`,
   `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT`.

## Specification Links

This proposal is governed by:

- `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` — superseded
  in full; record preserved as historical evidence.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` — owner
  decision authorizing this work; owner authority is the AskUserQuestion
  answers cited in §"Owner Decisions / Input"; the DELIB record is
  inserted post-GO.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`
  — preserved (not affected by this supersession); rc1 tag remains
  blocked until canonical Agent Red migration completes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol governs this work;
  `bridge/INDEX.md` is canonical operative state per
  `CLAUSE-INDEX-IS-CANONICAL`; bridge files are append-only audit trail.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact insertion (the new
  DELIB) requires owner-visible approval evidence; see Test 5 below.
- `GOV-STANDING-BACKLOG-001` — `memory/work_list.md` is the
  human-readable view of the standing backlog; mutations preserve
  backlog source-of-truth alignment with MemBase.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — owner decisions, backlog
  state, deferral states are durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — preserve traceability
  across decisions and bridge threads.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this
  section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan
  in §"Tests / verification" + §"Unchanged-surface verification".
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application/root placement
  authority. Cited because this proposal touches
  `.claude/rules/file-bridge-protocol.md` and references Agent Red
  repository state in the context of preserving `DELIB-S330`'s
  canonical-migration prerequisite. No application/root placement is
  proposed.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle triggers
  (advisory). Cited because this proposal performs deliberate lifecycle
  transitions: DELIB-S327 marked superseded, 7 backlogged WIs lifted
  from defer status, GTKB-GOV-007 PAUSED tag retired.
- `.claude/rules/operating-model.md` §1, §2, §3.
- `.claude/rules/file-bridge-protocol.md`.
- `.claude/rules/codex-review-gate.md`.
- `.claude/rules/prime-builder-role.md` — AskUserQuestion as the only
  valid owner-decision channel.

How proposed tests derive from linked specifications: §"Spec-to-test
mapping" below maps each acceptance criterion back to the governing
spec or rule clause.

### Pre-filing applicability preflight evidence

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lift-feature-freeze`
ran clean against this revision at filing time:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`

Packet hash recorded post-INDEX-update by the live preflight invocation.

## Prior Deliberations

- `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` (S327) —
  superseded.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`
  — preserved.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — relevant.
- `DELIB-GTKB-IDP-TERMINOLOGY` — backlog as unified view.

Verified at this revision via `db.get_deliberation()`: DELIB-S327 and
DELIB-S330 retrievable as expected.

## Owner Decisions / Input

Per `.claude/rules/prime-builder-role.md` §"AskUserQuestion as the Only
Valid Owner-Decision Channel".

Owner directive (this session, 2026-05-07): "Let's remove all FREEZE or
HOLD or DEFER states from all plans and work items. They are all stale."

AskUserQuestion #1 — Scope: "Which categories of FREEZE/HOLD/DEFER state
should I lift?"
- Owner answer: **A + B + C + H**

AskUserQuestion #2 — Approval and extension: "Approve DELIB-S332 as
drafted and authorize me to file the bridge proposal?"
- Owner answer: **"Approve, but also lift S327 release-path goal
  entirely"**
- Effect: DELIB-S332 supersedes the entire DELIB-S327; the
  "release path = clean-adopter productization" framing is dropped.

These two AUQ answers, captured in this session's transcript, are the
sole owner-decision authority. No prose-decision-ask is relied upon.

## Implementation scope

After Loyal Opposition GO, Prime Builder will perform the following
mutations in a single bridge-implementation cycle.

### Step 0 — Capture pre-implementation baselines

```bash
mkdir -p .gtkb-state/bridge-pre-baselines

# H-baseline: 5 keep-as-is H items
python -c "
from groundtruth_kb.db import KnowledgeDB
import json, pathlib
db = KnowledgeDB()
items = db.list_work_items()
latest = {}
for w in items:
    if w['id'] not in latest or w['version'] > latest[w['id']]['version']:
        latest[w['id']] = w
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
print(f'H-baseline: {len(baseline)} items')
"

# D-baseline: technical-dependency defer items
python -c "
from groundtruth_kb.db import KnowledgeDB
import json, pathlib
db = KnowledgeDB()
items = db.list_work_items()
latest = {}
for w in items:
    if w['id'] not in latest or w['version'] > latest[w['id']]['version']:
        latest[w['id']] = w
d_items = {w['id']: {'status_detail': w.get('status_detail'),
                      'resolution_status': w.get('resolution_status'),
                      'stage': w.get('stage'),
                      'version': w['version']}
           for w in latest.values()
           if 'deferred to upstream' in (w.get('status_detail') or '').lower()
              or 'deferred to upstream' in (w.get('change_reason') or '').lower()}
out = pathlib.Path('.gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-d-baseline.json')
out.write_text(json.dumps(d_items, indent=2))
print(f'D-baseline: {len(d_items)} items')
"

# E-baseline: all wont_fix items
python -c "
from groundtruth_kb.db import KnowledgeDB
import json, pathlib
db = KnowledgeDB()
items = db.list_work_items()
latest = {}
for w in items:
    if w['id'] not in latest or w['version'] > latest[w['id']]['version']:
        latest[w['id']] = w
e_items = {w['id']: {'status_detail': w.get('status_detail'),
                      'resolution_status': w.get('resolution_status'),
                      'stage': w.get('stage'),
                      'version': w['version']}
           for w in latest.values()
           if w.get('resolution_status') == 'wont_fix'}
out = pathlib.Path('.gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-e-baseline.json')
out.write_text(json.dumps(e_items, indent=2))
print(f'E-baseline: {len(e_items)} items')
"

# F-baseline: GTKB-DASHBOARD-RETENTION contingent flag
python -c "
from groundtruth_kb.db import KnowledgeDB
import json, pathlib
db = KnowledgeDB()
items = db.list_work_items()
latest = {}
for w in items:
    if w['id'] not in latest or w['version'] > latest[w['id']]['version']:
        latest[w['id']] = w
w = latest.get('GTKB-DASHBOARD-RETENTION')
assert w is not None, 'GTKB-DASHBOARD-RETENTION missing in baseline capture'
baseline = {'GTKB-DASHBOARD-RETENTION': {'resolution_status': w.get('resolution_status'),
                                          'status_detail': w.get('status_detail'),
                                          'stage': w.get('stage'),
                                          'version': w['version']}}
out = pathlib.Path('.gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-f-baseline.json')
out.write_text(json.dumps(baseline, indent=2))
print(f'F-baseline captured for GTKB-DASHBOARD-RETENTION')
"

# G-baseline: VERIFIED bridge file sha256 hashes
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
print(f'G-baseline: {len(hashes)} VERIFIED bridge files')
"

# DELIB-S330 baseline: structured field snapshot via get_deliberation
python -c "
from groundtruth_kb.db import KnowledgeDB
import json, pathlib
db = KnowledgeDB()
delib = db.get_deliberation('DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE')
assert delib is not None, 'DELIB-S330 not retrievable'
fields = ['id','version','session_id','outcome','source_type','source_ref','title','summary','content_hash']
baseline = {k: delib.get(k) for k in fields}
out = pathlib.Path('.gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-delib-s330-baseline.json')
out.write_text(json.dumps(baseline, indent=2))
print('DELIB-S330 baseline captured')
"

# P0 secrets-purge workstream text baseline (line-anchored grep)
grep -nE "GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT|P0 security override 2026-05-05" \
  memory/work_list.md \
  > .gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-secrets-baseline.txt
```

### Step 1 — Insert DELIB-S332

Insert `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` via
`db.insert_deliberation()` (or equivalent CLI surface). Body matches the
Appendix below. Fields: `source_type=owner_conversation`,
`outcome=owner_decision`, `session_id=S332`,
`source_ref=owner_conversation:2026-05-07-S332-lift-feature-freeze`.
Supersession of DELIB-S327 is encoded in the DELIB content (Appendix
`supersedes:` line).

Approval-packet evidence at
`.groundtruth/formal-artifact-approvals/2026-05-07-DELIB-S332-LIFT-FEATURE-FREEZE.json`,
schema mirrored from
`.groundtruth/formal-artifact-approvals/2026-05-02-release-path-directive.json`:

- `artifact_type`: "deliberation"
- `artifact_id`: "DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING"
- `action`: "insert"
- `source_ref`: "owner_conversation:2026-05-07-S332-lift-feature-freeze"
- `full_content`: full DELIB body matching Appendix; cites both AUQ
  answers verbatim (lowercase comparison string asserted by Test 5)
- `full_content_sha256`: sha256 of `full_content` UTF-8 bytes
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

a. The "TOP — S327 RELEASE PATH" header (line ~17) → neutral
   "TOP — Active workstreams" header.
b. The "Owner directive 2026-05-02 (S327, end-of-session)" paragraph
   (line ~19) → delete.
c. The "Feature freeze in effect" paragraph (line ~21) → delete.
d. The "Default idle work directive 2026-05-06" paragraph (line ~27) →
   rewrite to drop freeze-derived sequencing; replace with priority
   ordering driven by per-item leverage analysis.
e. The "Deferred during release path (capture only; do not advance)"
   section (line ~78) → delete header + body; reclassify each row as
   `live` or `kept-deferred-with-reason` per the H-category inventory.
f. The `GTKB-GOV-007 - PAUSED` tag (line ~1656) → replace with
   disposition note: "Stale PAUSED tag lifted 2026-05-07 S332. New
   disposition required: revise underlying commercial-readiness NO-GO
   bridge threads, retire, or reclassify."

The "Owner pre-approval" header (line 10) and "Backlog source-of-truth
status" header (line 3) are preserved unchanged. The
`GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` workstream entry and its
"P0 security override 2026-05-05" framing are preserved unchanged
(verified by U4).

### Step 3 — Append MemBase WI versions (F4 fix)

For each of the 7 listed WIs, append a new version. **`status_detail`
contains current state only — no freeze/defer/hold/paused/parked
vocabulary.** Historical context (the prior `status_detail`, the
superseding DELIB) goes in `change_reason`.

For all 7 items:

```text
change_reason = "Lift stale freeze/defer marker per DELIB-S332
(bridge gtkb-lift-feature-freeze-001-005). Prior status_detail
referenced the S327 feature freeze or related defer state; new
status_detail reflects current state per owner directive 2026-05-07
to remove FREEZE/HOLD/DEFER vocabulary from work-item current-state
fields. See DELIB-S332 for owner-decision authority and AUQ
evidence."
```

For the 3 newly-unblocked items:

| WI | New `status_detail` |
|---|---|
| `GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL` | `live; backlogged for prioritization` |
| `GTKB-STARTUP-REFRACTOR-001` | `live; P1; backlogged for prioritization` |
| `GTKB-ROLE-ENHANCEMENT` | `live; backlogged for prioritization` |

For the 4 already-active items (state reflects live bridge thread
status, queried at implementation time from `bridge/INDEX.md`):

| WI | New `status_detail` |
|---|---|
| `GTKB-ISOLATION-017-SLICE-5.5` | `active; bridge thread <latest INDEX status:file>` |
| `GTKB-PIP-INSTALL-ADOPTER-UX-001` | `active; bridge thread <latest INDEX status:file>` |
| `GTKB-CI-COVERAGE-FOR-PLATFORM-001` | `active; bridge thread <latest INDEX status:file>` |
| `GTKB-EVALUATION-MODULE-RESTORATION-001` | `active; bridge thread <latest INDEX status:file>` |

The `<latest INDEX status:file>` placeholder is resolved at
implementation time by reading the head version of each item's bridge
thread from `bridge/INDEX.md` (e.g., `VERIFIED:bridge/gtkb-pip-install-adopter-ux-001-006.md`).
This keeps the recorded state aligned with live bridge state at the
moment of mutation. None of the resolved values may contain
freeze/defer/hold/paused/parked vocabulary; if the live bridge entry
ever did, this proposal would surface that as a separate finding.

### Step 4 — Out of scope

Unchanged: D items, E items, F item (`GTKB-DASHBOARD-RETENTION`
contingent flag), G items (VERIFIED bridge .md), 5 keep-as-is H items,
`DELIB-S330`, P0 secrets-purge workstream.

## Tests / verification

All commands are deterministic — exact-lookup via `db.get_deliberation()`
or structured-field comparisons via JSON baselines. **No `gt deliberations
search` or stdout-substring parsing on padded CLI output.**

### Verification commands

```bash
# 1. work_list.md cleanup
test "$(grep -c 'Feature freeze in effect' memory/work_list.md)" = "0"
test "$(grep -c 'Deferred during release path' memory/work_list.md)" = "0"
test "$(grep -c 'GTKB-GOV-007 - PAUSED' memory/work_list.md)" = "0"

# 2. Target WIs cleared of freeze/hold/defer language in status_detail (regex-broadened)
python -c "
import re
from groundtruth_kb.db import KnowledgeDB
db = KnowledgeDB()
items = db.list_work_items()
latest = {}
for w in items:
    if w['id'] not in latest or w['version'] > latest[w['id']]['version']:
        latest[w['id']] = w
freeze_pat = re.compile(r'(?i)\b(freeze|frozen|defer|deferred|hold|paused|parked)\b')
target_ids = {
    'GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL',
    'GTKB-STARTUP-REFRACTOR-001',
    'GTKB-ROLE-ENHANCEMENT',
    'GTKB-ISOLATION-017-SLICE-5.5',
    'GTKB-PIP-INSTALL-ADOPTER-UX-001',
    'GTKB-CI-COVERAGE-FOR-PLATFORM-001',
    'GTKB-EVALUATION-MODULE-RESTORATION-001',
}
hits = []
for w in latest.values():
    if w['id'] in target_ids:
        sd = w.get('status_detail') or ''
        if freeze_pat.search(sd):
            hits.append(f'{w[\"id\"]}: status_detail={sd!r}')
assert not hits, 'TARGET WIs RETAIN FREEZE/DEFER/HOLD LANGUAGE in status_detail: ' + '; '.join(hits)
print(f'PASS: all {len(target_ids)} target WIs cleared')
"

# 3. DELIB-S332 retrievable + metadata via structured DB query (F1 fix)
python -c "
from groundtruth_kb.db import KnowledgeDB
db = KnowledgeDB()
delib = db.get_deliberation('DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING')
assert delib is not None, 'DELIB-S332 not retrievable'
assert delib.get('session_id') == 'S332', f'wrong session_id: {delib.get(\"session_id\")!r}'
assert delib.get('outcome') == 'owner_decision', f'wrong outcome: {delib.get(\"outcome\")!r}'
assert delib.get('source_type') == 'owner_conversation', f'wrong source_type: {delib.get(\"source_type\")!r}'
assert 'supersedes: DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION' in (delib.get('content') or ''), \
    'supersession declaration missing from DELIB-S332 content'
print('PASS: DELIB-S332 metadata + supersession verified')
"

# 4. DELIB-S327 preserved (still retrievable; not deleted)
python -c "
from groundtruth_kb.db import KnowledgeDB
db = KnowledgeDB()
delib = db.get_deliberation('DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION')
assert delib is not None, 'DELIB-S327 missing post-impl'
assert delib.get('session_id') == 'S327', 'DELIB-S327 metadata corrupt'
print('PASS: DELIB-S327 preserved')
"

# 5. Approval packet validates against the approval contract (F2 fix: lowercase both sides)
python -c "
import json, hashlib, pathlib
p = pathlib.Path('.groundtruth/formal-artifact-approvals/2026-05-07-DELIB-S332-LIFT-FEATURE-FREEZE.json')
assert p.exists(), 'packet file missing'
data = json.loads(p.read_text())
assert data.get('artifact_id') == 'DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING', \
    f'wrong artifact_id: {data.get(\"artifact_id\")}'
assert data.get('artifact_type') == 'deliberation', f'wrong artifact_type'
assert data.get('action') in ('insert','supersede'), f'wrong action: {data.get(\"action\")}'
sha = data.get('full_content_sha256') or ''
assert isinstance(sha, str) and len(sha) == 64, f'malformed full_content_sha256: {sha!r}'
content = data.get('full_content','')
assert content, 'full_content empty'
import re
# Normalize whitespace so multi-line wrapped citations still match
content_normalized = re.sub(r'\s+', ' ', content.lower())
content_normalized_cs = re.sub(r'\s+', ' ', content)
# AUQ #1 (scope) - case-preserving normalized match
assert 'A + B + C + H' in content_normalized_cs, \
    'AUQ #1 (scope) answer not cited verbatim in full_content (whitespace-normalized)'
# AUQ #2 (extend) - lowercase + whitespace-normalized
assert 'lift s327 release-path goal entirely' in content_normalized, \
    'AUQ #2 (extend) answer not cited in full_content (whitespace-normalized lowercase)'
# Computed hash matches stored hash
computed = hashlib.sha256(content.encode('utf-8')).hexdigest()
assert computed == sha, f'sha mismatch: computed={computed} stored={sha}'
# Required transcript / approval flags
assert data.get('approval_mode') == 'approve'
assert data.get('presented_to_user') is True
assert data.get('transcript_captured') is True
assert data.get('approved_by') == 'owner'
print('PASS: approval packet validates against contract')
"

# 6. Bridge applicability preflight passes
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lift-feature-freeze
# expect: preflight_passed: true; missing_required_specs: []; missing_advisory_specs: []
```

### Spec-to-test mapping

| Test | Verifies | Linked spec |
|---|---|---|
| 1 | work_list.md cleanup of freeze markers | Implementation §2; `GOV-STANDING-BACKLOG-001` |
| 2 | 7 target WIs free of freeze/defer/hold/paused/parked language | Implementation §3; owner directive |
| 3 | DELIB-S332 inserted with correct metadata (structured query) | Implementation §1; `GOV-ARTIFACT-APPROVAL-001` |
| 4 | DELIB-S327 preserved as historical evidence | `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (append-only) |
| 5 | Approval-packet contract (NOT just existence) | `GOV-ARTIFACT-APPROVAL-001` |
| 6 | Cross-cutting spec citations complete | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` |

## Unchanged-surface verification

Pre-implementation baseline (Step 0) + post-implementation diff
assertions. Each excluded surface named in acceptance criterion 5 has a
deterministic JSON baseline.

```bash
# U1. 5 keep-as-is H items unchanged
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
            mismatches.append(f'{wid}.{field}: {snap.get(field)!r} -> {cur.get(field)!r}')
assert not mismatches, 'KEEP-AS-IS H ITEMS CHANGED: ' + '; '.join(mismatches)
print(f'PASS: all {len(baseline)} keep-as-is H items unchanged')
"

# U2. All VERIFIED bridge files unchanged (G-category)
python -c "
import hashlib, pathlib, json
baseline = json.loads(pathlib.Path('.gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-verified-hashes.json').read_text())
mismatches = []
for f, expected in baseline.items():
    p = pathlib.Path(f)
    if not p.exists():
        mismatches.append(f'{f} missing'); continue
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    if actual != expected:
        mismatches.append(f'{f}: {expected[:12]}... -> {actual[:12]}...')
assert not mismatches, 'VERIFIED BRIDGE FILES MUTATED: ' + '; '.join(mismatches)
print(f'PASS: all {len(baseline)} VERIFIED bridge files unchanged')
"

# U3. DELIB-S330 unchanged (structured field comparison)
python -c "
import json, pathlib
from groundtruth_kb.db import KnowledgeDB
baseline = json.loads(pathlib.Path('.gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-delib-s330-baseline.json').read_text())
db = KnowledgeDB()
delib = db.get_deliberation('DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE')
assert delib is not None, 'DELIB-S330 missing'
mismatches = []
for k, expected in baseline.items():
    cur = delib.get(k)
    if cur != expected:
        mismatches.append(f'{k}: {expected!r} -> {cur!r}')
assert not mismatches, 'DELIB-S330 CHANGED: ' + '; '.join(mismatches)
print('PASS: DELIB-S330 unchanged')
"

# U4. P0 secrets-purge workstream text preserved in work_list.md
diff -u .gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-secrets-baseline.txt \
        <(grep -nE "GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT|P0 security override 2026-05-05" memory/work_list.md)

# U5. D-category items unchanged (technical-dependency defers)
python -c "
import json, pathlib
from groundtruth_kb.db import KnowledgeDB
baseline = json.loads(pathlib.Path('.gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-d-baseline.json').read_text())
db = KnowledgeDB()
items = db.list_work_items()
latest = {}
for w in items:
    if w['id'] not in latest or w['version'] > latest[w['id']]['version']:
        latest[w['id']] = w
mismatches = []
for wid, snap in baseline.items():
    if wid not in latest:
        mismatches.append(f'{wid} missing'); continue
    cur = latest[wid]
    for field in ('status_detail','resolution_status','stage'):
        if (cur.get(field) or '') != (snap.get(field) or ''):
            mismatches.append(f'{wid}.{field}: {snap.get(field)!r} -> {cur.get(field)!r}')
assert not mismatches, 'D-CATEGORY ITEMS CHANGED: ' + '; '.join(mismatches)
print(f'PASS: all {len(baseline)} D-category items unchanged')
"

# U6. F-category contingent flag preserved (GTKB-DASHBOARD-RETENTION)
python -c "
import json, pathlib
from groundtruth_kb.db import KnowledgeDB
baseline = json.loads(pathlib.Path('.gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-f-baseline.json').read_text())
db = KnowledgeDB()
items = db.list_work_items()
latest = {}
for w in items:
    if w['id'] not in latest or w['version'] > latest[w['id']]['version']:
        latest[w['id']] = w
snap = baseline['GTKB-DASHBOARD-RETENTION']
cur = latest.get('GTKB-DASHBOARD-RETENTION')
assert cur is not None, 'GTKB-DASHBOARD-RETENTION missing'
mismatches = []
for field in ('status_detail','resolution_status','stage'):
    if (cur.get(field) or '') != (snap.get(field) or ''):
        mismatches.append(f'{field}: {snap.get(field)!r} -> {cur.get(field)!r}')
assert not mismatches, 'F-CATEGORY CHANGED: ' + '; '.join(mismatches)
print('PASS: GTKB-DASHBOARD-RETENTION contingent flag preserved')
"

# U7. E-category wont_fix items unchanged (NEW)
python -c "
import json, pathlib
from groundtruth_kb.db import KnowledgeDB
baseline = json.loads(pathlib.Path('.gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-e-baseline.json').read_text())
db = KnowledgeDB()
items = db.list_work_items()
latest = {}
for w in items:
    if w['id'] not in latest or w['version'] > latest[w['id']]['version']:
        latest[w['id']] = w
mismatches = []
for wid, snap in baseline.items():
    if wid not in latest:
        mismatches.append(f'{wid} missing'); continue
    cur = latest[wid]
    for field in ('status_detail','resolution_status','stage'):
        if (cur.get(field) or '') != (snap.get(field) or ''):
            mismatches.append(f'{wid}.{field}: {snap.get(field)!r} -> {cur.get(field)!r}')
# Also confirm the resolution_status='wont_fix' set didn't grow or shrink
post_e_ids = {w['id'] for w in latest.values() if w.get('resolution_status') == 'wont_fix'}
baseline_ids = set(baseline.keys())
added = post_e_ids - baseline_ids
removed = baseline_ids - post_e_ids
if added: mismatches.append(f'E-set additions: {sorted(added)}')
if removed: mismatches.append(f'E-set removals: {sorted(removed)}')
assert not mismatches, 'E-CATEGORY CHANGED: ' + '; '.join(mismatches)
print(f'PASS: all {len(baseline)} E-category wont_fix items unchanged; set membership stable')
"
```

### Unchanged-surface mapping

| Test | Verifies | Excluded category |
|---|---|---|
| U1 | 5 keep-as-is H items unchanged | H (selected exclusions) |
| U2 | All VERIFIED bridge files unchanged (sha256) | G |
| U3 | DELIB-S330 unchanged (structured fields) | DELIB-S330 (release prerequisite) |
| U4 | P0 secrets-purge workstream text preserved | P0 security override |
| U5 | D-category items unchanged | D |
| U6 | F-category contingent flag preserved | F |
| U7 | E-category wont_fix items + set membership stable | E |

## Risk / rollback

Risks unchanged from `-003`. Rollback: insert superseding DELIB; append
new MemBase WI versions restoring prior `status_detail` from H-baseline
+ the change_reason field on the appended-during-impl versions; restore
`memory/work_list.md` from git history.

## Acceptance criteria

1. `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` exists
   with correct metadata (Tests 3) and supersedes `DELIB-S327`
   (Test 3, supersession-line check).
2. Approval packet validates against full contract (Test 5).
3. `memory/work_list.md` no longer contains freeze/PAUSED-2026-04-18
   strings (Test 1).
4. 7 target WIs free of freeze/defer/hold/paused/parked language in
   `status_detail` (Test 2, regex).
5. Excluded surfaces unchanged: H-keep, D, E, F, G, DELIB-S330, P0
   secrets-purge (Tests U1-U7).
6. Pre-filing applicability preflight passes (Test 6).
7. `python -m pytest tests/scripts/ -k "bridge or backlog" -q` passes.

## Recommended commit type

`chore:` — governance hygiene; no new capability surface; one DELIB
insert, ~6 markdown sections rewritten, 7 MemBase WI versions appended.

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
     Disambiguation Slices 2-5 may now advance.
     GTKB-ARTIFACT-RECORDER-CLI is no longer freeze-blocked.
  2. Drop the S327 "release path = clean-adopter productization"
     framing. rc1 sequencing is open; the "Default idle work directive
     2026-05-06" is rewritten to reflect per-item leverage rather than
     freeze-derived ordering.
  3. Lift the GTKB-GOV-007 PAUSED tag (2026-04-18). Entry stale; new
     disposition required.
  4. Clear stale freeze/defer text from the status_detail field of
     7 backlogged WIs. New status_detail contains current state only;
     historical context lives in change_reason. 5 H-category items
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
