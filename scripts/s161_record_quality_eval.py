"""S161: Record quality evaluation specs, WIs, backlog, design doc in KB.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import sys
sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

db = KnowledgeDB()
SESSION = "S161"
BY = f"claude/{SESSION}"
print("KB connected")