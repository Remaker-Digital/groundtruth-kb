import scripts.gtkb_bridge_writer as w
from pathlib import Path
body = Path('.claude/skills/verify/helpers/seeded_openrouter_timeout_body.txt').read_text(encoding='utf-8-sig')
print(w.write_bridge_file('gtkb-wi5060-openrouter-direct-timeout-retry', 2, body, Path('E:/GT-KB')))
