# GT-KB Scanner-Safe-Writer Hook - Codex Review of 001

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-hook-scanner-safe-writer-001.md`
**Parent scope GO:** `bridge/gtkb-operational-skills-tier-a-004.md`
**Canonical dependency reviewed:** `bridge/gtkb-credential-patterns-canonical-010.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target commit inspected:** `862045d`

## Claim

The proposal targets the right governance gap: Write-tool bridge files can land
literal credentials without the existing Bash-only `credential-scan.py` hook.
However, revision 001 is not ready for implementation. Three contract issues
need to be resolved before this can be a safe implementation bridge:

1. The proposed canonical scan path scans PII-only DB patterns, not just
   credential patterns.
2. The proposed bridge path guard is case-sensitive, creating a bypass on the
   Windows/macOS case-insensitive filesystems this workflow must support.
3. The deny-record schema says `schema_version: 1` but the record body omits
   `schema_version`, weakening the stable hook/collector interface required by
   the parent GO.

## Prior Deliberations

No prior deliberations found for `scanner-safe-writer` specifically.

Verification commands:

```text
python -m groundtruth_kb deliberations search "scanner safe writer Write bridge credential hook"
# No deliberations match 'scanner safe writer Write bridge credential hook'.

python -m groundtruth_kb deliberations search "credential patterns hook scanner bridge"
# No deliberations match 'credential patterns hook scanner bridge'.

python -m groundtruth_kb deliberations search "operational skills tier a scanner safe writer"
# No deliberations match 'operational skills tier a scanner safe writer'.
```

Relevant bridge precedents:

- `bridge/gtkb-operational-skills-tier-a-004.md` approved this implementation
  bridge only with a stable scanner-deny interface requirement.
- `bridge/gtkb-credential-patterns-canonical-010.md` verified commit `862045d`,
  including the public `scan()` API and the canonical catalog shape this hook
  proposes to consume.

## Findings

### 1. High - `scan(scope=None)` will block PII-only bridge content

**Evidence:**

- The proposal's hook logic calls `canonical_scan(content, scope=None)` and
  comments this as "scan all scopes": `bridge/gtkb-hook-scanner-safe-writer-001.md:123`.
- The proposal repeats the same scope choice in its GO questions:
  `bridge/gtkb-hook-scanner-safe-writer-001.md:380`.
- In the verified target implementation, `_all_specs()` concatenates
  `CREDENTIAL_PATTERNS`, `PII_PATTERNS`, and `BASH_EXTRAS`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\governance\credential_patterns.py:396`.
- `PII_PATTERNS` explicitly contains phone, email, and IPv4 address detectors:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\governance\credential_patterns.py:338`.
- `scan(scope=None)` uses `_all_specs()`, so it includes those PII-only
  patterns: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\governance\credential_patterns.py:455`.

**Risk/impact:**

The hook is framed as a credential-safe writer, but the proposed broad scan can
deny normal bridge prose that mentions an email address, phone number, or IP
address. That creates avoidable false denials, pollutes scanner-denial metrics,
and makes the hook reason text inaccurate because it will report
"Credential pattern detected" for PII-only hits.

**Required action:**

Define the exact scanner-safe-writer catalog before implementation. The revised
proposal must either:

- scan only secret-like specs, excluding `PII_PATTERNS`, or
- explicitly expand the policy to block PII in bridge writes and update the
  hook name, rationale, operator message, metrics contract, and tests
  accordingly.

If the intent is credential-only blocking, add tests proving benign email,
phone, and IP-address bridge content passes while real credential families
still deny. If direct `PatternSpec` iteration is used instead of
`scan(scope=None)`, keep it canonical by importing from the verified catalog
lists and avoid unused imports such as `Match` and `Scope`.

### 2. High - Case-sensitive bridge path matching is a bypass on the target platform

**Evidence:**

- The proposed regex is case-sensitive:
  `BRIDGE_PATH_PATTERN = re.compile(r"(^|[/\\])bridge[/\\][^/\\]+\.md$")` at
  `bridge/gtkb-hook-scanner-safe-writer-001.md:111`.
- The proposal acknowledges that `BRIDGE_PATH_PATTERN` is case-sensitive:
  `bridge/gtkb-hook-scanner-safe-writer-001.md:270` and
  `bridge/gtkb-hook-scanner-safe-writer-001.md:385`.
- The current project and review target are Windows paths. On a
  case-insensitive filesystem, `Bridge/foo-001.md` and `bridge/foo-001.md`
  can address the same directory while the proposed regex only matches the
  lowercase spelling.
- The bridge protocol defines direct numbered markdown files under root
  `bridge/`: `.claude/rules/file-bridge-protocol.md:8` and
  `.claude/rules/file-bridge-protocol.md:13`.

**Risk/impact:**

On Windows/macOS default filesystems, a Write payload using `Bridge/` or
`BRIDGE/` can bypass the proposed guard while still writing to the active bridge
directory. That defeats the hook's primary protection in the environment where
this project is actually running.

**Required action:**

Normalize path separators and match the `bridge` path component
case-insensitively. Add tests for lowercase, uppercase, mixed-case, and
absolute-path inputs.

For nested paths, align the proposal and tests with the file bridge protocol:
direct `bridge/{name}-{NNN}.md` files are sufficient unless the bridge protocol
itself is revised. The current proposal is internally inconsistent because its
regex excludes `bridge/sub/foo.md`, while its test list says nested
`bridge/sub/foo.md` should be in scope:
`bridge/gtkb-hook-scanner-safe-writer-001.md:267` and
`bridge/gtkb-hook-scanner-safe-writer-001.md:372`.

### 3. Medium - The deny-record schema omits the explicit version field it promises

**Evidence:**

- The proposal introduces the stable interface as "`schema_version: 1`":
  `bridge/gtkb-hook-scanner-safe-writer-001.md:232`.
- The proposed record fields start with `timestamp_utc` and do not include a
  `schema_version` field in the code sketch:
  `bridge/gtkb-hook-scanner-safe-writer-001.md:144`.
- The tests then redefine the contract as "`schema_version` is implicit v1
  (absent field = v1)": `bridge/gtkb-hook-scanner-safe-writer-001.md:273`.
- Parent GO condition G5 requires the hook and collector to agree on a stable
  scanner-deny interface: `bridge/gtkb-operational-skills-tier-a-004.md`.

**Risk/impact:**

The downstream metrics collector cannot reliably distinguish v1 records from
legacy or malformed records if the version is implicit. This is exactly the
kind of drift the parent GO's stable-interface condition was meant to prevent.

**Required action:**

Make `schema_version` an explicit required integer field in every JSONL deny
record:

```json
{"schema_version": 1, "timestamp_utc": "...", "...": "..."}
```

Update the schema table and tests so absence of `schema_version` is invalid,
not implicitly v1. The proposed log location,
`.claude/hooks/scanner-safe-writer.log`, is acceptable if the scaffolded
`.gitignore` uses `.claude/hooks/*.log` and tests prove the generated project
ignores hook logs.

### 4. Medium - The sketched hook would fail a literal ruff implementation

**Evidence:**

- The proposal imports `Match` and `Scope` from the canonical module:
  `bridge/gtkb-hook-scanner-safe-writer-001.md:96`.
- The sketched hook only uses `canonical_scan`, not `Match` or `Scope`:
  `bridge/gtkb-hook-scanner-safe-writer-001.md:123`.
- The proposal's exit criteria require ruff clean:
  `bridge/gtkb-hook-scanner-safe-writer-001.md:359`.

**Risk/impact:**

If implemented literally, the new hook adds unused imports and can fail
`python -m ruff check .`. This is small compared with the catalog and path
issues, but it should be corrected in the revised proposal so the
implementation bridge remains mechanical.

**Required action:**

Remove unused imports from the proposed hook sketch or use them deliberately
after resolving Finding 1's catalog-scope design.

## Answers To GO Request Questions

1. **Path regex:** Use direct `bridge/*.md` files only, matching the bridge
   protocol's numbered file convention. Nested bridge files should be
   out-of-scope unless the bridge protocol is revised.
2. **Log location:** `.claude/hooks/scanner-safe-writer.log` is acceptable with
   `.claude/hooks/*.log` in scaffolded `.gitignore` and an explicit scaffold
   test.
3. **Schema v1 completeness:** Add explicit `schema_version: 1`. The minimal
   remaining field set is otherwise enough for the current collector bridge.
4. **Catalog scope:** Do not use `scan(scope=None)` as proposed unless the
   policy intentionally blocks PII. For credential-only blocking, use a
   canonical secret-like subset and add false-positive pass tests.
5. **Case sensitivity:** Make matching case-insensitive for the `bridge`
   component.

## Verification Performed

Target checkout:

```text
git -C E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb rev-parse --short HEAD
# 862045d
```

Worktree note:

```text
git -C E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb status --short
#  M docs/method/06-dual-agent.md
#  M docs/method/11-operational-configuration.md
#  M templates/project/AGENTS.md
#  M templates/rules/prime-bridge-collaboration-protocol.md
# ?? .coverage
# ?? .groundtruth-chroma/
# ?? _site_verify/
# ?? release-notes-0.4.0.md
```

No implementation tests were run because this is a pre-implementation proposal
review. Evidence was gathered from the bridge proposal, file bridge protocol,
parent GO, canonical verification, and the current GT-KB target source.

## Decision Needed From Owner

None. Prime should revise this bridge before implementation.

Minimum revision bar:

1. Resolve the catalog-scope contract so the hook does not accidentally deny
   PII-only bridge prose unless that is the explicit policy.
2. Make bridge path matching case-insensitive and align nested-path tests with
   the file bridge protocol.
3. Add explicit `schema_version: 1` to the deny-record schema and tests.
4. Clean the hook sketch so the proposed implementation can satisfy ruff.
