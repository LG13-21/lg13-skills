---
name: load-from-store
description: "Načte session plán/memory z MySQL (přes db_query) nebo git fallback. Triggery: load from store, remember from mysql, load my memory, nacti plan, obnov memory."
user-invocable: true
---

# load-from-store — Načtení session memory z MySQL nebo git

## PURPOSE

Načte uložený plán z předchozí session. Volej na začátku nové session po `/clear` nebo otevření nového okna.

---

## EXECUTION

```python
import sys
from pathlib import Path

sys.path.insert(0, 'L:/GitHub/lg13-coder/agent/skills')
from db_query import db

# Auto-detect instance z cwd
cwd = Path.cwd()
instance_map = {'lg13-coder': 'coder', 'lg13-strat': 'strat',
                'legal-ship-2026': 'legal', 'tmonkey': 'tmonkey'}
instance = next((v for k, v in instance_map.items() if k in str(cwd)), 'coder')

# MySQL (primary)
r = db("SELECT plan_text, saved_at FROM instance_plans WHERE instance=%s", params=[instance])
if r.get('ok') and r.get('rows'):
    row = r['rows'][0]
    print(f"=== PLAN z MySQL ({row[1]}) ===\n{row[0]}")
else:
    # Git fallback
    pf = Path(f"L:/GitHub/lg13-{instance}/plans/{instance}_current.md")
    if pf.exists():
        print(f"=== PLAN z gitu ===\n{pf.read_text(encoding='utf-8')}")
    else:
        print(f"[load-from-store] Žádný uložený plán pro '{instance}'.")
        print("Tip: spusť /lg13-skills:save-to-store v předchozí session.")
```

---

## RELATED

- Skill `save-to-store` — uloží plán (párový skill)
- Skill `mysql` — přímé SQL dotazy přes `/mysql q: ...`
- Skill `restart` — volá load-from-store jako poslední krok po restartu
