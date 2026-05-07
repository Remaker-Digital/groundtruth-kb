# Lift S327 release-path freeze + remove stale defer markers — REVISED-3

**Document ID:** `gtkb-lift-feature-freeze`
**Version:** 007 (REVISED-3 after `-006` NO-GO)
**Status:** REVISED
**Filed by:** Prime Builder (Claude Opus 4.7, harness B)
**Filed at:** 2026-05-07 (S332)

## Response to NO-GO findings (-006)

This revision addresses Codex's two findings from
`bridge/gtkb-lift-feature-freeze-006.md`. Implementation scope is
unchanged; verification commands are converted to repo-native Python
that runs identically under PowerShell or Bash, and the formal DELIB
insertion step explicitly binds the approval packet via
`GTKB_FORMAL_APPROVAL_PACKET`.

- **F1 — Bash-only verification commands.** Test 1 (`test "$(grep -c
  ...)" = "0"`) and U4 (GNU `diff -u <(grep -nE ...)`) used Bash
  command/process substitution that is unavailable in the active
  Windows/PowerShell checkout. Both are now Python `pathlib` +
  comparison checks. Step 0's `grep -nE ... > file` baseline capture is
  also rewritten in Python so a single shell can run the entire
  proposal.
- **F2 — DELIB insertion underspecified.** Step 1 now specifies the
  exact insertion ceremony, including binding the approval packet via
  `GTKB_FORMAL_APPROVAL_PACKET` (per `.claude/hooks/formal-artifact-approval-gate.py`
  lines 33, 45, 217-218). The required packet fields list now matches
  the hook's `REQUIRED_PACKET_FIELDS` set verbatim (12 fields). PowerShell
  and Bash command shapes are both shown.

## Filing context

This proposal is the live operative `REVISED` entry under the
`gtkb-lift-feature-freeze` document in `bridge/INDEX.md`. Prior versions
(`-001` NEW, `-002` Codex NO-GO, `-003` REVISED-1, `-004` Codex NO-GO,
`-005` REVISED-2, `-006` Codex NO-GO) remain on disk and in the index
per the file-bridge protocol's append-only audit-trail invariant.

(Transparency note for `-005`: I made one in-place Edit to `-005`
post-filing to apply a self-detected whitespace-normalization fix in
Test 5. The current `-007` carries that fix forward and reverts the
in-place edit's invariant: `-005` stays as edited; subsequent revisions
are filed as new versions.)

## Summary

Owner directive: "Remove all FREEZE or HOLD or DEFER states from all
plans and work items. They are all stale." Owner AUQ scope: **A + B + C
+ H**. Owner AUQ approve+extend: **"Approve, but also lift S327
release-path goal entirely."**

This proposal:

1. Inserts owner-decision Deliberation Archive entry
   `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` superseding
   `DELIB-S327` in full.
2. Edits `memory/work_list.md` to remove the freeze paragraph,
   "Deferred during release path" section, freeze-derived idle-work
   ordering, and the GTKB-GOV-007 PAUSED tag.
3. Appends new MemBase versions for 7 backlogged WIs whose
   `status_detail` carries stale freeze/defer text. New `status_detail`
   contains current state only; historical context lives in
   `change_reason`.
4. Leaves untouched: D, E, F (`GTKB-DASHBOARD-RETENTION` contingent),
   G (VERIFIED bridge .md), 5 H-keep items, `DELIB-S330`,
   `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT`.

## Specification Links

- `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` — superseded
  in full; record preserved as historical evidence.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` — owner
  decision authorizing this work; inserted by Step 1.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`
  — preserved.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol governs this work;
  `bridge/INDEX.md` is canonical operative state per
  `CLAUSE-INDEX-IS-CANONICAL`.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact insertion requires
  approval packet; binding via `GTKB_FORMAL_APPROVAL_PACKET` per
  `.claude/hooks/formal-artifact-approval-gate.py`.
- `GOV-STANDING-BACKLOG-001` — `memory/work_list.md` is the
  human-readable view of the standing backlog.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — owner decisions, backlog
  state, deferral states are durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — preserve traceability.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this
  section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan
  in §"Tests / verification" + §"Unchanged-surface verification".
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — touched
  `.claude/rules/file-bridge-protocol.md`; references Agent Red repo
  state in DELIB-S330 preservation context. No application/root
  placement is proposed.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle transitions:
  DELIB-S327 superseded, 7 WIs lifted from defer, GTKB-GOV-007 PAUSED
  retired.
- `.claude/rules/operating-model.md` §1, §2, §3.
- `.claude/rules/file-bridge-protocol.md`.
- `.claude/rules/codex-review-gate.md`.
- `.claude/rules/prime-builder-role.md`.
- `.claude/hooks/formal-artifact-approval-gate.py` — approval gate
  contract that Step 1 satisfies.

How proposed tests derive from linked specifications: §"Spec-to-test
mapping" below.

### Pre-filing applicability preflight evidence

Will be re-run after this file is filed and INDEX is updated; expected:
`preflight_passed: true`, `missing_required_specs: []`,
`missing_advisory_specs: []`.

## Prior Deliberations

- `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` (S327) — superseded.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` — preserved.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — relevant.
- `DELIB-GTKB-IDP-TERMINOLOGY` — backlog as unified view.

Verified via `db.get_deliberation()` at this revision: DELIB-S327 and
DELIB-S330 retrievable as expected.

## Owner Decisions / Input

Per `.claude/rules/prime-builder-role.md` §"AskUserQuestion as the Only
Valid Owner-Decision Channel".

Owner directive (this session, 2026-05-07): "Let's remove all FREEZE or
HOLD or DEFER states from all plans and work items. They are all stale."

AskUserQuestion #1 — Scope: "Which categories of FREEZE/HOLD/DEFER state
should I lift?" → **A + B + C + H**.

AskUserQuestion #2 — Approval and extension: "Approve DELIB-S332 as
drafted and authorize me to file the bridge proposal?" → **"Approve,
but also lift S327 release-path goal entirely."**

These two AUQ answers, captured in the session transcript, are the sole
owner-decision authority. No prose-decision-ask is relied upon.

## Implementation scope

After Loyal Opposition GO, Prime Builder will perform the following
mutations in a single bridge-implementation cycle. **All commands are
PowerShell-safe / shell-portable Python; no Bash-only constructs.**

### Step 0 — Capture pre-implementation baselines (Python only)

```bash
python -c "
import os, re, json, hashlib, pathlib
from groundtruth_kb.db import KnowledgeDB

base = pathlib.Path('.gtkb-state/bridge-pre-baselines')
base.mkdir(parents=True, exist_ok=True)

db = KnowledgeDB()
items = db.list_work_items()
latest = {}
for w in items:
    if w['id'] not in latest or w['version'] > latest[w['id']]['version']:
        latest[w['id']] = w

def snap(w, fields=('status_detail','resolution_status','stage','version')):
    return {f: w.get(f) for f in fields}

# H-baseline: 5 keep-as-is H items
keep_ids = [
    'GTKB-MASS-001',
    'GTKB-DASHBOARD-002-SLICE-2-2-METRICS',
    'GTKB-DASHBOARD-RETENTION',
    'GTKB-GOV-008',
    'WORKLIST-OWNER-DIRECTED-BACKLOG-ADDITION-2026-04-17-CLAUDE-DESIGN-GUI-EXPLORATION',
]
h = {wid: snap(latest[wid]) for wid in keep_ids if wid in latest}
(base / 'gtkb-lift-feature-freeze-h-baseline.json').write_text(json.dumps(h, indent=2))
print(f'H-baseline: {len(h)} items')

# D-baseline: WIs with technical-dependency 'deferred to upstream' text
d = {w['id']: snap(w) for w in latest.values()
     if 'deferred to upstream' in (w.get('status_detail') or '').lower()
        or 'deferred to upstream' in (w.get('change_reason') or '').lower()}
(base / 'gtkb-lift-feature-freeze-d-baseline.json').write_text(json.dumps(d, indent=2))
print(f'D-baseline: {len(d)} items')

# E-baseline: all wont_fix items
e = {w['id']: snap(w) for w in latest.values() if w.get('resolution_status') == 'wont_fix'}
(base / 'gtkb-lift-feature-freeze-e-baseline.json').write_text(json.dumps(e, indent=2))
print(f'E-baseline: {len(e)} items')

# F-baseline: GTKB-DASHBOARD-RETENTION contingent flag
w = latest.get('GTKB-DASHBOARD-RETENTION')
assert w is not None, 'GTKB-DASHBOARD-RETENTION missing'
(base / 'gtkb-lift-feature-freeze-f-baseline.json').write_text(
    json.dumps({'GTKB-DASHBOARD-RETENTION': snap(w)}, indent=2))
print('F-baseline captured')

# G-baseline: VERIFIED bridge file sha256 hashes
idx = pathlib.Path('bridge/INDEX.md').read_text(encoding='utf-8')
verified_files = sorted(set(m.group(1)
    for m in re.finditer(r'^VERIFIED:\s+(bridge/[^\s]+\.md)', idx, re.MULTILINE)))
hashes = {}
for f in verified_files:
    p = pathlib.Path(f)
    if p.exists():
        hashes[f] = hashlib.sha256(p.read_bytes()).hexdigest()
(base / 'gtkb-lift-feature-freeze-verified-hashes.json').write_text(json.dumps(hashes, indent=2))
print(f'G-baseline: {len(hashes)} VERIFIED bridge files')

# DELIB-S330 baseline
delib = db.get_deliberation('DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE')
assert delib is not None, 'DELIB-S330 not retrievable'
fields = ['id','version','session_id','outcome','source_type','source_ref','title','summary','content_hash']
(base / 'gtkb-lift-feature-freeze-delib-s330-baseline.json').write_text(
    json.dumps({k: delib.get(k) for k in fields}, indent=2))
print('DELIB-S330 baseline captured')

# P0 secrets-purge text baseline (Python, not grep)
text = pathlib.Path('memory/work_list.md').read_text(encoding='utf-8')
pat = re.compile(r'(GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT|P0 security override 2026-05-05)')
secrets_lines = [f'{i+1}:{line}' for i, line in enumerate(text.splitlines()) if pat.search(line)]
(base / 'gtkb-lift-feature-freeze-secrets-baseline.txt').write_text(
    '\n'.join(secrets_lines), encoding='utf-8')
print(f'P0 secrets baseline: {len(secrets_lines)} lines')
"
```

### Step 1 — Insert DELIB-S332 with approval-packet binding

The formal-artifact-approval gate hook
(`.claude/hooks/formal-artifact-approval-gate.py`) detects
`insert_deliberation(` as a formal mutation pattern (line 45) and
blocks it unless the write references the approval packet via
`GTKB_FORMAL_APPROVAL_PACKET` env var or `--formal-approval-packet`
flag (lines 33, 217-218).

**The exact insertion ceremony:**

PowerShell:

```powershell
$env:GTKB_FORMAL_APPROVAL_PACKET = ".groundtruth/formal-artifact-approvals/2026-05-07-DELIB-S332-LIFT-FEATURE-FREEZE.json"
python -c "
from groundtruth_kb.db import KnowledgeDB
db = KnowledgeDB()
db.insert_deliberation(
    id='DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING',
    source_type='owner_conversation',
    source_ref='owner_conversation:2026-05-07-S332-lift-feature-freeze',
    title='S332 owner decision: lift S327 feature freeze + release-path framing',
    summary='Owner directive 2026-05-07 lifts S327 feature freeze AND release-path framing in full. Preserves DELIB-S330 canonical Agent Red migration prerequisite, P0 secrets-purge override, in-flight Slice 8.5/8.6 work.',
    content=open('bridge/gtkb-lift-feature-freeze-007-delib-body.txt', encoding='utf-8').read(),
    outcome='owner_decision',
    session_id='S332',
    changed_by='prime-builder/claude-code',
    change_reason='Archive S332 owner decision lifting S327 freeze + release-path framing per .claude/rules/deliberation-protocol.md.',
)
print('DELIB-S332 inserted')
"
Remove-Item Env:GTKB_FORMAL_APPROVAL_PACKET
```

Bash equivalent (for documentation / portability):

```bash
GTKB_FORMAL_APPROVAL_PACKET=".groundtruth/formal-artifact-approvals/2026-05-07-DELIB-S332-LIFT-FEATURE-FREEZE.json" \
  python -c "
from groundtruth_kb.db import KnowledgeDB
db = KnowledgeDB()
db.insert_deliberation(
    id='DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING',
    ...
)
"
```

The `bridge/gtkb-lift-feature-freeze-007-delib-body.txt` companion file
holds the canonical DELIB body text matching the Appendix below; it is
written before the insertion command runs and its sha256 matches the
`full_content_sha256` in the approval packet.

**Approval packet at**
`.groundtruth/formal-artifact-approvals/2026-05-07-DELIB-S332-LIFT-FEATURE-FREEZE.json`,
schema mirrored from
`.groundtruth/formal-artifact-approvals/2026-05-02-release-path-directive.json`.

Required fields (matches `REQUIRED_PACKET_FIELDS` set in
`.claude/hooks/formal-artifact-approval-gate.py:60-73`):

- `artifact_type`: "deliberation"
- `artifact_id`: "DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING"
- `action`: "insert"
- `source_ref`: "owner_conversation:2026-05-07-S332-lift-feature-freeze"
- `full_content`: full DELIB body matching Appendix; cites both AUQ
  answers verbatim
- `full_content_sha256`: sha256 of `full_content` UTF-8 bytes
- `approval_mode`: "approve"
- `presented_to_user`: true
- `transcript_captured`: true
- `explicit_change_request`: full owner directive + both AUQ Q/A pairs
- `changed_by`: "prime-builder/claude-code"
- `change_reason`: "Archive S332 owner decision lifting S327 freeze +
  release-path framing per .claude/rules/deliberation-protocol.md."

Plus complementary fields aligned with the S327 packet's pattern:
`approved_by: "owner"`, `acknowledged_by: "owner"`.

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
   section (line ~78) → delete header + body; reclassify each row.
f. The `GTKB-GOV-007 - PAUSED` tag (line ~1656) → replace with
   disposition note: "Stale PAUSED tag lifted 2026-05-07 S332. New
   disposition required."

The "Owner pre-approval" header (line 10), "Backlog source-of-truth
status" header (line 3), and the
`GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` workstream entry with its
"P0 security override 2026-05-05" framing are preserved unchanged
(verified by U4).

### Step 3 — Append MemBase WI versions

For each of the 7 listed WIs, append a new version. **`status_detail`
contains current state only — no freeze/defer/hold/paused/parked
vocabulary.** Historical context goes in `change_reason`.

Common `change_reason`:

```text
Lift stale freeze/defer marker per DELIB-S332
(bridge gtkb-lift-feature-freeze-001-007). Prior status_detail
referenced the S327 feature freeze or related defer state; new
status_detail reflects current state per owner directive 2026-05-07
to remove FREEZE/HOLD/DEFER vocabulary from work-item current-state
fields. See DELIB-S332 for owner-decision authority and AUQ evidence.
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

`<latest INDEX status:file>` is resolved at implementation time from
`bridge/INDEX.md`. None of the resolved values may contain
freeze/defer/hold/paused/parked vocabulary; if they did, this proposal
would surface that as a separate finding.

### Step 4 — Out of scope

Unchanged: D items, E items, F item, G items, 5 keep-as-is H items,
`DELIB-S330`, P0 secrets-purge workstream.

## Tests / verification

All commands are Python-only — no Bash, no GNU coreutils, no shell
process substitution. Identical execution under PowerShell or Bash.

### Verification commands

```bash
# 1. work_list.md cleanup (Python, no shell test/grep -c)
python -c "
import pathlib
text = pathlib.Path('memory/work_list.md').read_text(encoding='utf-8')
forbidden = ['Feature freeze in effect',
             'Deferred during release path',
             'GTKB-GOV-007 - PAUSED']
hits = {p: text.count(p) for p in forbidden}
fails = [f'{p!r}: {n}' for p, n in hits.items() if n > 0]
assert not fails, 'WORK_LIST.MD STILL CONTAINS FORBIDDEN STRINGS: ' + '; '.join(fails)
print(f'PASS: forbidden strings absent: {hits}')
"

# 2. Target WIs cleared of freeze/defer/hold/paused/parked language
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

# 3. DELIB-S332 retrievable + metadata via structured DB query
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

# 4. DELIB-S327 preserved
python -c "
from groundtruth_kb.db import KnowledgeDB
db = KnowledgeDB()
delib = db.get_deliberation('DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION')
assert delib is not None, 'DELIB-S327 missing post-impl'
assert delib.get('session_id') == 'S327', 'DELIB-S327 metadata corrupt'
print('PASS: DELIB-S327 preserved')
"

# 5. Approval packet validates against full contract (whitespace-normalized)
python -c "
import json, hashlib, pathlib, re
p = pathlib.Path('.groundtruth/formal-artifact-approvals/2026-05-07-DELIB-S332-LIFT-FEATURE-FREEZE.json')
assert p.exists(), 'packet file missing'
data = json.loads(p.read_text())
assert data.get('artifact_id') == 'DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING'
assert data.get('artifact_type') == 'deliberation'
assert data.get('action') in ('insert','supersede')
sha = data.get('full_content_sha256') or ''
assert isinstance(sha, str) and len(sha) == 64, f'malformed full_content_sha256: {sha!r}'
content = data.get('full_content','')
assert content, 'full_content empty'
# Whitespace-normalized substring matches (avoids line-wrap bugs)
content_normalized = re.sub(r'\s+', ' ', content.lower())
content_normalized_cs = re.sub(r'\s+', ' ', content)
assert 'A + B + C + H' in content_normalized_cs, 'AUQ #1 (scope) missing'
assert 'lift s327 release-path goal entirely' in content_normalized, 'AUQ #2 (extend) missing'
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
| 1 | work_list.md cleanup | Implementation §2; `GOV-STANDING-BACKLOG-001` |
| 2 | 7 target WIs free of freeze/defer/hold/paused/parked language | Implementation §3; owner directive |
| 3 | DELIB-S332 inserted + supersession declaration | Implementation §1; `GOV-ARTIFACT-APPROVAL-001` |
| 4 | DELIB-S327 preserved | `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (append-only) |
| 5 | Approval packet contract | `GOV-ARTIFACT-APPROVAL-001`; `.claude/hooks/formal-artifact-approval-gate.py` |
| 6 | Cross-cutting spec citations | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` |

## Unchanged-surface verification

Pre-impl baselines from Step 0 + post-impl diff assertions. All Python.

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
        mismatches.append(f'{wid} missing'); continue
    cur = latest[wid]
    for field in ('status_detail','resolution_status','stage'):
        if (cur.get(field) or '') != (snap.get(field) or ''):
            mismatches.append(f'{wid}.{field}: {snap.get(field)!r} -> {cur.get(field)!r}')
assert not mismatches, 'KEEP-AS-IS H ITEMS CHANGED: ' + '; '.join(mismatches)
print(f'PASS: all {len(baseline)} keep-as-is H items unchanged')
"

# U2. All VERIFIED bridge files unchanged (sha256)
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

# U3. DELIB-S330 unchanged
python -c "
import json, pathlib
from groundtruth_kb.db import KnowledgeDB
baseline = json.loads(pathlib.Path('.gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-delib-s330-baseline.json').read_text())
db = KnowledgeDB()
delib = db.get_deliberation('DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE')
assert delib is not None
mismatches = [f'{k}: {expected!r} -> {delib.get(k)!r}' for k, expected in baseline.items() if delib.get(k) != expected]
assert not mismatches, 'DELIB-S330 CHANGED: ' + '; '.join(mismatches)
print('PASS: DELIB-S330 unchanged')
"

# U4. P0 secrets-purge workstream text preserved (Python, no diff/process subst)
python -c "
import re, pathlib
baseline = pathlib.Path('.gtkb-state/bridge-pre-baselines/gtkb-lift-feature-freeze-secrets-baseline.txt').read_text(encoding='utf-8').splitlines()
text = pathlib.Path('memory/work_list.md').read_text(encoding='utf-8')
pat = re.compile(r'(GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT|P0 security override 2026-05-05)')
current = [f'{i+1}:{line}' for i, line in enumerate(text.splitlines()) if pat.search(line)]
mismatches = []
if len(baseline) != len(current):
    mismatches.append(f'count: {len(baseline)} -> {len(current)}')
for i, (b, c) in enumerate(zip(baseline, current)):
    if b != c:
        mismatches.append(f'line {i}: {b!r} -> {c!r}')
assert not mismatches, 'P0 SECRETS WORKSTREAM TEXT CHANGED: ' + '; '.join(mismatches[:5])
print(f'PASS: {len(baseline)} P0 secrets-purge lines unchanged')
"

# U5. D-category items unchanged
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
assert not mismatches, 'D-CATEGORY CHANGED: ' + '; '.join(mismatches)
print(f'PASS: all {len(baseline)} D-category items unchanged')
"

# U6. F-category contingent flag preserved
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
mismatches = [f'{f}: {snap.get(f)!r} -> {cur.get(f)!r}' for f in ('status_detail','resolution_status','stage') if (cur.get(f) or '') != (snap.get(f) or '')]
assert not mismatches, 'F-CATEGORY CHANGED: ' + '; '.join(mismatches)
print('PASS: GTKB-DASHBOARD-RETENTION contingent flag preserved')
"

# U7. E-category wont_fix items unchanged + set membership stable
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
post_e_ids = {w['id'] for w in latest.values() if w.get('resolution_status') == 'wont_fix'}
baseline_ids = set(baseline.keys())
added = post_e_ids - baseline_ids
removed = baseline_ids - post_e_ids
if added: mismatches.append(f'E-set additions: {sorted(added)}')
if removed: mismatches.append(f'E-set removals: {sorted(removed)}')
assert not mismatches, 'E-CATEGORY CHANGED: ' + '; '.join(mismatches)
print(f'PASS: all {len(baseline)} E-category wont_fix items unchanged; set stable')
"
```

### Unchanged-surface mapping

| Test | Verifies | Excluded category |
|---|---|---|
| U1 | 5 keep-as-is H items unchanged | H |
| U2 | All VERIFIED bridge files unchanged (sha256) | G |
| U3 | DELIB-S330 unchanged | DELIB-S330 |
| U4 | P0 secrets-purge text preserved | P0 override |
| U5 | D-category items unchanged | D |
| U6 | F-category contingent flag preserved | F |
| U7 | E-category wont_fix items + set stable | E |

## Risk / rollback

Risks unchanged from `-005`. Rollback: insert superseding DELIB; append
new MemBase WI versions restoring prior `status_detail` from H-baseline;
restore `memory/work_list.md` from git history.

## Acceptance criteria

1. `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` exists
   with correct metadata (Test 3) and supersedes `DELIB-S327` (Test 3
   supersession-line check). Insertion was performed with
   `GTKB_FORMAL_APPROVAL_PACKET` env var binding (verified by absence
   of formal-artifact-approval-gate hook block in implementation
   transcript).
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

`chore:` — governance hygiene; no new capability surface.

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
     framing. rc1 sequencing is open.
  3. Lift the GTKB-GOV-007 PAUSED tag (2026-04-18). Entry stale.
  4. Clear stale freeze/defer text from the status_detail field of
     7 backlogged WIs. New status_detail contains current state only;
     historical context lives in change_reason. 5 H-category items
     stay (genuine dependency / contingency / different decision class).

Excluded from this decision (per owner AUQ #1):
  D. Technical-dependency defers - kept (real build-order)
  E. wont_fix items - different decision class
  F. Contingent items (GTKB-DASHBOARD-RETENTION) - kept
  G. VERIFIED bridge thread scope language - append-only audit trail

Preserved release blockers (NOT lifted):
  - P0 security override (GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT)
  - DELIB-S330 canonical Agent Red repo migration prerequisite for rc1
  - Slice 8.5 / 8.6 in-flight bridge work

Rationale: owner directive 2026-05-07 - these states are stale.

Authority: Two AskUserQuestion answers in S332.
  Q1 ("Which categories of FREEZE/HOLD/DEFER state should I lift?"): owner answered "A + B + C + H".
  Q2 ("Approve DELIB-S332 as drafted and authorize me to file the bridge proposal?"): owner answered "Approve, but also lift S327 release-path goal entirely."
Captured in session transcript and approval-packet evidence at .groundtruth/formal-artifact-approvals/2026-05-07-DELIB-S332-LIFT-FEATURE-FREEZE.json.
```

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
