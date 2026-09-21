# Harness projection and shared instructions

GT-KB authors instructions once and projects only what an installed host needs
to locate or execute them. A projection is derived output. Change its authored
source and regenerate through the supported projector.

## Authored sources

| Source | Purpose |
| --- | --- |
| Root `AGENTS.md` | Shared session instructions, authored and tracked; no second rendered copy |
| Root `CLAUDE.md` and `.goosehints` | Tracked root pointers whose exact bytes are declared in the profiles |
| `.agents/skills/<name>/SKILL.md` and its resources | One shared Agent Skills tree |
| `.harness-baseline-configuration/rules` | Focused rules read on demand |
| `.harness-baseline-configuration/hooks` and `hooks/manifest.toml` | Shared hook implementations and event contract |
| `.harness-baseline-configuration/routing.toml` | Shared API-harness routing configuration |
| `scripts/harness_projection/profiles.toml` | Host adaptation, root pointer bytes and declared outputs |

Read current formal requirements and work state through the native CLI. Root
instructions, a skill, a host registration and a projection do not replace the
current domain source of truth. Bind the actual native context using the exact
supplied init line, follow the separately supplied activity, and read the exact
assigned work and bridge item. No host name supplies a role.

## Declared output classes

| Class | Allowed content |
| --- | --- |
| `REGISTRATION` | Required native settings or hook/configuration registration |
| `POINTER` | A host-required reference to a shared authored source |
| `OWNERSHIP` | Projector path bookkeeping, currently its manifest; no agent instruction authority |

Retired outputs include copied rules, copied hook implementations, copied skill
bodies/resources and per-provider copies of shared routing. Each declared
output is checked against the current profile; counts are measured from that
profile and its manifest, rather than pinned to an earlier installation census.
Unmanaged files require explicit reconciliation and are not excused by a clean
managed-output check. Do not delete a neighboring file or empty directory outside
the selected projection's bounded ownership.

Skills that require host-local discovery use a `SKILL.md` pointer stub. Its
source YAML frontmatter is preserved verbatim, its body points to the shared
skill, and the source digest covers frontmatter only. Skill resources remain
under the shared tree. Hosted-application stubs point to
`../../.agents/skills/<name>/SKILL.md`; they do not create a per-application skill
body. Adapter-based hook targets resolve inside the host root without `..`;
redirect and containment refusals remain in force.

## Eight profiles and nine actual hosts

| Profile | Configuration root | Instruction/skill route |
| --- | --- | --- |
| `codex` | `.codex` | Shared root and skills; native registration |
| `claude` | `.claude` | `CLAUDE.md` import of root; skill pointer stubs |
| `cursor` | `.cursor` | Shared root; skill pointer stubs |
| `goose` | `.goose` | Root pointer; skill pointer stubs |
| `antigravity` | `.agent` | Shared root with retained rules pointer; skill pointer stubs |
| `openrouter` | `.api-harness/openrouter` | Runtime reads shared sources and baseline routing directly |
| `ollama` | `.api-harness/ollama` | Runtime reads shared sources and baseline routing directly |
| `alibaba-cloud-studio` | `.api-harness/alibaba-cloud-studio` | Runtime reads shared sources and baseline routing directly |

The official DeepSeek SDK is a ninth actual host with its private runtime and
native CLI launcher; it is not a ninth projection profile. A registered or
suspended host is not activated by projection. Preserve the current registration
status and the owner's selected provider/model when diagnosing or qualifying it.

## Refresh and inspect

```text
gt --config <selected-project>/groundtruth.toml harness project <profile> --dry-run
gt --config <selected-project>/groundtruth.toml harness project <profile>
gt --config <selected-project>/groundtruth.toml harness project <profile> --check
```

Dry-run exposes planned paths; the ordinary invocation materializes the selected
profile; check compares declared output. Use the existing profile and canonical
sources, never a generated directory as an input baseline. Configuration type,
redirect or token errors refuse application. Preserve unrelated local settings
and foreign work. Never repair generated output by hand.

## Actual-host loading and trust

Projector and source tests do not prove native host loading. Record the actual
installed build, final source and registration hashes, native context, observed
instruction/skill/rule load and executed hook behavior. Preserve pointers until
the applicable version-pinned native evidence supports their forward retirement.

Codex requires the owner's trust action for the exact final hook-registration
bytes, followed by an executed protected-event check. Antigravity uses the actual
supported `context.fileName` setting for `AGENTS.md`; retain its rules pointer
until its native-load case is proven. A `GEMINI.md` wrapper is considered only
when an actual host observation requires it. No vendor compatibility is inferred
from a directory or a historical version label.

Qualification covers fresh contexts, positive delivery, useful refusals,
mid-turn revalidation, interrupted delivery, independent successors, authorized
close/wrap, cross-host continuation and a bounded permanent-authority action.
Bind evidence to the exact installed bytes; a later material change requires
the affected qualification again.

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
