# Third-party notices: GT-KB Home

GT-KB Home runs the DeepSeek Harness Web UI.

| Item | Detail |
| --- | --- |
| Package | `@deepseek-ai/dsh` 0.1.2-rc.1 |
| Source | https://github.com/deepseek-ai/deepseek-harness |
| License | MIT License, Copyright (c) 2026 DeepSeek |
| Full license text | `node_modules/@deepseek-ai/dsh/LICENSE` after installation, and in the source repository. |

GT-KB replaces the upstream brand with GT-KB and Remaker Digital branding. The Home states its basis in the interface:
"GT-KB by Remaker Digital · Built on DeepSeek Harness (MIT License)".

GT-KB does not redistribute these packages. `install.py` fetches the pinned tree (585 packages, recorded in
`package-lock.json`) from the npm registry at installation, and each package's own license travels with it inside
`node_modules`.

## Licenses recorded in the lockfile

| License | Packages |
| --- | ---: |
| MIT | 465 |
| Apache-2.0 | 75 |
| BSD-3-Clause | 17 |
| LGPL-3.0-or-later | 10 |
| ISC | 10 |
| Apache-2.0 AND LGPL-3.0-or-later | 3 |
| BSD-2-Clause | 2 |
| Apache-2.0 AND LGPL-3.0-or-later AND MIT | 1 |
| Python-2.0 | 1 |
| 0BSD | 1 |

The LGPL-3.0-or-later entries are the optional, platform-specific libvips binaries of the image library `sharp`
(`@img/sharp-libvips-*`, `@img/sharp-win32-*`, `@img/sharp-wasm32`). npm installs only the one that matches the host.

The Python-2.0 entry is the JavaScript port of `argparse`.

Remaker Digital marks (`plugins/gtkb-home/assets/`) © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All
rights reserved.
