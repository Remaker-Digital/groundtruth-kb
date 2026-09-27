# Documentation publication

**Status:** Current owner-selected publication model
**Decision date:** 2026-09-26

The GitHub Wiki is GTKB's customer-facing product-documentation home.

Reviewed source lives in `groundtruth-kb/docs/wiki/` in the main repository.
`scripts/update_wiki_pages.py` compares and copies allowlisted pages and image
assets into a local clone of
`https://github.com/Remaker-Digital/groundtruth-kb.wiki.git`.
The Wiki repository is a publication target, not an independently authored
second manual.

Screenshot source lives in `groundtruth-kb/docs/wiki/assets/`. Each published
image is explicitly allowlisted in the publisher; unrelated local captures are
not copied. Asset comparison uses the original bytes and SHA-256 hashes. The
publisher copies assets unchanged and does not push Git commits.

Pages embed the published Wiki asset URL, so repository previews and the Wiki
use the same image. Retain useful alternative text and a caption with the capture
or receipt date, release/build when known, and the state shown. Identify an
unknown version rather than infer it. Check for credentials, private paths,
customer data, and unrelated browser content before publishing each capture.

## Surface responsibilities

| Surface | Responsibility |
| --- | --- |
| Repository README | Concise product landing page and route to this Wiki |
| GitHub Wiki | Customer installation, learning, operations, and support documentation |
| Repository Wiki source | Reviewable, testable source of published Wiki pages |
| Component READMEs | Maintainer and advanced operator implementation detail |
| CLI help | Exact installed command syntax |

GitHub Pages is not the GTKB documentation home. Older pages or references that
describe the Wiki as a mirror are superseded by this decision.

## Publication checks

Before publication or release:

1. compare repository source with a fresh Wiki clone;
2. validate internal Wiki links and rendered images, including alternative text;
3. scan current pages for retired terminology and forbidden paths;
4. verify commands against the selected release;
5. confirm that historical material is visibly labeled; and
6. inspect the signed-out rendered Wiki.

Direct emergency Wiki corrections must be reconciled into repository source so
the next publication does not erase them.
