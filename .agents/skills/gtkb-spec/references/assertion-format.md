# Native assertion definitions and their limits

`gt assert --spec <id> --triggered-by <context> --json` reads the selected current
specification through the native authority and evaluates against the selected
project root. With no `--spec`, it selects active specifications. It returns
observations without writing execution history, changing lifecycle or issuing
an independent verdict. A changed version or status during evaluation invalidates
the observation. An unavailable authority is a refusal, with no local fallback.

The supported executable types are:

| Type | Fields | Observation |
|---|---|---|
| `grep` | `file`, regex `pattern`, optional `min_count` (default 1) | Total matching occurrences meet the minimum |
| `grep_absent` | `file`, regex `pattern` | No matching occurrence in the inspected target |
| `glob` | `pattern`, optional literal `contains` | At least one matching path, or matching file containing the text |
| `file_exists` | `file` | The named path is a file |
| `count` | `file`, regex `pattern`, `operator`, integer `expected` | Match count satisfies `==`, `!=`, `>`, `>=`, `<` or `<=` |
| `json_path` | `file`, dotted `path`, optional `expected` | JSON/TOML path exists; when supplied, its value equals expected |
| `all_of` | Nonempty `assertions` array | Every child passes |
| `any_of` | Nonempty `assertions` array | At least one child passes |

Prefer the explicit fields above over historical aliases. Paths are relative to
the selected project root; absolute paths, parent traversal and resolved escapes
are refused. Grep-style `file` targets may use `*` globs. Regex occurrence counts
do not establish control flow. Keep compositions within three nested operator
levels. Files that cannot be read, including binary or oversized files, cannot
supply positive content evidence. Do not use negative text checks as proof of
absence from code or behavior beyond the files actually inspected.

## Runnable structural example

Given `config/example.toml` containing `[service]` and `port = 8765`, this array
illustrates all eight types. Put it in the native specification's `assertions`
field. Its descriptions deliberately claim only file/configuration observations.

```json
[
  {"type": "file_exists", "file": "config/example.toml", "description": "The configuration file exists"},
  {"type": "glob", "pattern": "config/*.toml", "contains": "[service]", "description": "A TOML file contains the service heading"},
  {"type": "grep", "file": "config/example.toml", "pattern": "port = 8765", "min_count": 1, "description": "The configured port text is present"},
  {"type": "grep_absent", "file": "config/example.toml", "pattern": "external.invalid", "description": "The inspected configuration lacks this hostname text"},
  {"type": "count", "file": "config/example.toml", "pattern": "port =", "operator": "==", "expected": 1, "description": "The inspected file has one port assignment token"},
  {"type": "json_path", "file": "config/example.toml", "path": "service.port", "expected": 8765, "description": "The parsed service port equals 8765"},
  {"type": "all_of", "assertions": [{"type": "file_exists", "file": "config/example.toml"}, {"type": "json_path", "file": "config/example.toml", "path": "service.port", "expected": 8765}], "description": "The file exists and declares the expected port"},
  {"type": "any_of", "assertions": [{"type": "file_exists", "file": "config/example.toml"}, {"type": "file_exists", "file": "config/example.json"}], "description": "One supported configuration filename exists"}
]
```

None of these checks starts a listener or sends a request. Use executable tests
for that behavior and retain its distinct result. When current requirements
need behavioral qualification, `constraints.behavioral_validation_required`
may be set to `true`: the assertion runner reports that unmet evaluation duty
as UNASSESSED, making an otherwise passing structural selection PARTIAL. The
flag does not arrange or execute the behavioral test.

## Interpret the result

PASS means all evaluated required observations passed, within their stated
coverage. FAIL identifies a failed executable check. Unsupported definition
types and unevaluated behavioral duties are UNASSESSED, never fabricated passes;
a mixture of passed and unevaluated duties is PARTIAL. A specification without
assertions or behavioral duties, or one retired/superseded, is NOT_APPLICABLE.
An `any_of` can pass with one successful child; inspect the other children's
results when their observations matter. The command exits successfully only
when its aggregate result is PASS.

`http`, `python` and `exists` are not executable type names in this runner.
Use `file_exists` for a file observation and the actual behavioral test route
for HTTP or program execution. Do not rename such obligations into a grep
check to make them green. Native `assertions` is an array of objects; narrative
requirements belong in the specification's description and explicit test plan.
No result authorizes implementation, retires an obligation or promotes a work
item or specification to verified state.
