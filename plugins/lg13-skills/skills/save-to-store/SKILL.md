---
name: save-to-store
description: "Uloží aktuální session plán/memory do MySQL (přes db_query) + git backup. Triggery: save my memory, save plan to mysql, save to store, uloz plan, uloz memory."
user-invocable: true
---

# save-to-store — Uložení session memory do MySQL + git

## PURPOSE

Uloží aktuální kontext (STAV_NOW.md posledních 40 řádků) do:
- **MySQL** `instance_plans` tabulka přes `db_query.py` (primary)
- **Git** `plans/<instance>_current.md` (backup — verzovaný)

Volej před `/clear`, před zavřením okna, nebo kdykoli chceš zachovat stav.

---

## EXECUTION

```python
import sys, json, time, subprocess
from pathlib import Path

sys.path.insert(0, 'L:/GitHub/lg13-coder/agent/skills')
from db_query import db

# Auto-detect instance z cwd
cwd = Path.cwd()
instance_map = {'lg13-coder': 'coder', 'lg13-strat': 'strat',
                'legal-ship-2026': 'legal', 'tmonkey': 'tmonkey'}
instance = next((v for k, v in instance_map.items() if k in str(cwd)), 'coder')

# Načti STAV_NOW.md (posledních 40 řádků)
stav_paths = [Path(f"L:/GitHub/lg13-{instance}/STAV_NOW.md"), Path("STAV_NOW.md")]
stav = next((p for p in stav_paths if p.exists()), None)
plan_text = '\n'.join(stav.read_text(encoding='utf-8').splitlines()[-40:]) if stav else "(žádný STAV_NOW)"

ts = time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime())

# --- MySQL (primary) přes db_query ---
db("""CREATE TABLE IF NOT EXISTS instance_plans (
    instance VARCHAR(32) PRIMARY KEY, plan_text TEXT,
    saved_at VARCHAR(32), session_ts VARCHAR(32))""")

r = db("INSERT INTO instance_plans (instance, plan_text, saved_at, session_ts) "
       "VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE plan_text=%s, saved_at=%s, session_ts=%s",
       params=[instance, plan_text, ts, ts, plan_text, ts, ts])
if r.get('ok'):
    print(f"[save-to-store] MySQL OK: {instance} @ {ts}")
else:
    print(f"[save-to-store] MySQL chyba: {r.get('error')}")

# --- Git (backup) ---
plans_dir = Path(f"L:/GitHub/lg13-{instance}/plans")
plans_dir.mkdir(exist_ok=True)
pf = plans_dir / f"{instance}_current.md"
pf.write_text(f"# Plan backup — {ts}\n\n{plan_text}", encoding='utf-8')
try:
    subprocess.run(["git", "-C", str(plans_dir.parent), "add", str(pf)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(plans_dir.parent), "commit", "-m", f"chore: save-to-store {ts}"],
        check=True, capture_output=True)
    print(f"[save-to-store] Git OK: plans/{pf.name}")
except Exception as e:
    print(f"[save-to-store] Git chyba: {e}")
```

---

## RELATED

- Skill `load-from-store` — načte plán zpět (párový skill)
- Skill `mysql` — přímé SQL dotazy přes `/mysql q: ...`
- Skill `restart` — volá save-to-store jako první krok
- MySQL tabulka `instance_plans` — sdílený store pro všechny instance
