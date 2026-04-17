# NO-GO: F6 Project Scaffold Generator Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f6-001.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** NO-GO

## Rationale

GT-KB already has a project scaffolding subsystem. The proposal may be a useful extension, but it currently overlaps that subsystem, conflicts with the existing `ProjectProfile` model name, and leaves generated-spec authority unresolved.

## Findings

### 1. Blocking: Dependencies are unresolved

**Evidence:** F6 depends on F1 and F3 at bridge/gtkb-spec-pipeline-f6-001.md:7. It requires enriched schema and F3 quality validation at bridge/gtkb-spec-pipeline-f6-001.md:28 and bridge/gtkb-spec-pipeline-f6-001.md:107. F1 and F3 are currently NO-GO.

**Risk/impact:** Generated specs cannot reliably populate authority/provisional/testability fields or be quality-validated until those contracts stabilize.

**Required action:** Wait for F1/F3 GO or split F6 into a template-only phase that does not write enriched specs.

### 2. Blocking: Proposed `ProjectProfile` conflicts with existing scaffold profile type

**Evidence:** F6 proposes a new `ProjectProfile` dataclass with platform/deployment/tenancy/auth/data fields at bridge/gtkb-spec-pipeline-f6-001.md:32. Current GT-KB already has `groundtruth_kb.project.profiles.ProjectProfile` with scaffold-layer fields at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/profiles.py:9.

**Risk/impact:** Reusing the same name for different concepts will confuse imports, docs, and public API.

**Required action:** Rename the proposed data model, for example `SpecScaffoldProfile`, or extend the existing profile model intentionally with migration/docs.

### 3. Major: Existing scaffold integration is not specified

**Evidence:** Current `scaffold_project()` already creates project files, initializes the database, and seeds data at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:41 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:86. F6 proposes a separate `ScaffoldGenerator` API at bridge/gtkb-spec-pipeline-f6-001.md:121.

**Risk/impact:** GT-KB can end up with two scaffold paths: one that creates project structure and one that generates spec corpora, with unclear ordering and failure behavior.

**Required action:** Specify whether F6 is integrated into `gt project init`, exposed as a separate command, or only a library helper. Include dry-run/apply behavior and non-empty KB behavior.

### 4. Major: Generated spec authority is an owner decision, not an implementation detail

**Evidence:** F6 says every generated spec uses `authority=stated` at bridge/gtkb-spec-pipeline-f6-001.md:106, but the proposal's open question asks whether generated specs should be `stated` or `inferred` at bridge/gtkb-spec-pipeline-f6-001.md:185.

**Risk/impact:** Marking generated templates as owner-stated can over-authorize generic assumptions before the owner confirms them.

**Required action:** Require owner confirmation before `authority=stated`, or generate as `unknown`/`inferred`/`provisional` until confirmed.

## Conditions For GO

1. Resolve F1/F3 dependencies or decouple the first phase.
2. Avoid `ProjectProfile` naming conflict.
3. Define integration with existing `gt project init` scaffolding.
4. Set a safe authority policy for generated specs.

