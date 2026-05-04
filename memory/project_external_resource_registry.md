# Project External Resource Registry

This is the human-readable companion to
`.claude/rules/project-resource-aliases.toml`.

Purpose: AI agents must resolve casual user references such as "the GitHub",
"the repo", "repo", "CI", "PyPI", "SonarCloud", "Azure", "docs site", and
"Shopify" through configured project identities before using external evidence.
Without this mapping, historical Agent Red resources and GroundTruth-KB platform
resources can become entangled.

## Canonical GroundTruth-KB Resources

| Casual reference | Canonical resource | URL / identity |
| --- | --- | --- |
| the GitHub, project GitHub, GitHub, repo, the repo, GitHub repo, GT-KB repo | GroundTruth-KB GitHub repository | https://github.com/Remaker-Digital/groundtruth-kb |
| CI, GitHub Actions, Actions, workflow runs, checks | GroundTruth-KB GitHub Actions | https://github.com/Remaker-Digital/groundtruth-kb/actions |
| issues, issue tracker, GitHub issues | GroundTruth-KB GitHub issues | https://github.com/Remaker-Digital/groundtruth-kb/issues |
| wiki, project wiki, GitHub wiki | GroundTruth-KB GitHub wiki | https://github.com/Remaker-Digital/groundtruth-kb/wiki |
| PyPI, package, pip package, published package | `groundtruth-kb` PyPI package | https://pypi.org/project/groundtruth-kb/ |
| SonarCloud, sonar, quality gate | GroundTruth-KB SonarCloud project | `Remaker-Digital_groundtruth-kb` (URL inferred; verify before release evidence) |
| Remaker, Remaker Digital, the org | Remaker Digital | https://remakerdigital.com |

## Separate Project / Historical Resources

These resources may appear in memory, README text, bridge history, or operational
runbooks. They are not the default target for unqualified GT-KB references.

| Casual reference | Resource | URL / identity | Status |
| --- | --- | --- | --- |
| Agent Red repo, Agent Red GitHub | Agent Red repository | https://github.com/mike-remakerdigital/agent-red | separate project, not GT-KB |
| docs site, public docs, Agent Red docs | Agent Red public docs | https://agentredcx.com | separate project, not GT-KB |
| Shopify, storefront, test store | Agent Red Shopify storefront | https://blanco-9939.myshopify.com/ | separate project, not GT-KB |
| Azure, subscription | Agent Red Azure subscription | `4dce2122-690a-4654-b531-cc647db62331` | separate-project infrastructure; context required |

## Operating Rule

When a local tool default, cached report, README badge, or historical bridge
entry points at a different resource than this registry, treat that as
configuration drift or historical context. Use the configured resource identity
for new checks unless the owner explicitly scopes the task to the other
resource.
