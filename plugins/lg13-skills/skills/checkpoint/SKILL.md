---
name: checkpoint
description: >
  Průběžný snapshot stavu session. Uloží plán do MySQL + git, zapíše handoff note,
  reportuje stav do Jarvis. Volej kdykoliv v průběhu práce pro "save point" —
  od checkpointu lze pokračovat v nové session bez ztráty kontextu.
---

# checkpoint — Session Snapshot

Lightweight alternativa k `/save-min`. Rychlý, průběžný, volej i 10× za session.

**Od checkpointu lze pokračovat:** nová session → `/sr` → načte checkpoint → pokračuje přesně tam.

---

## EXECUTION

```python
import sys, time, subprocess
from pathlib import Path

sys.path.insert(0, 'L:/GitHub/lg13-coder/agent/skills')
from db_query import db

# Auto-detect instance
cwd = Path.cwd()
inst_map = {'lg13-coder': 'coder', 'lg13-strat': 'strat',
            'legal-ship-2026': 'legal', 'tmonkey': 'tmonkey'}
instance = next((v for k, v in inst_map.items() if k in str(cwd)), 'coder')

ts = time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime())

# 1. Načti STAV_NOW.md (posledních 40 řádků)
stav_paths = [Path(f"L:/GitHub/lg13-{instance}/STAV_NOW.md"), Path("STAV_NOW.md")]
stav = next((p for p in stav_paths if p.exists()), None)
plan_text = '\n'.join(stav.read_text(encoding='utf-8').splitlines()[-40:]) if stav else "(zadny STAV_NOW)"

# 2. MySQL save
db("""CREATE TABLE IF NOT EXISTS instance_plans (
    instance VARCHAR(32) PRIMARY KEY, plan_text TEXT,
    saved_at VARCHAR(32), session_ts VARCHAR(32))""")
r = db("INSERT INTO instance_plans (instance, plan_text, saved_at, session_ts) "
       "VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE plan_text=%s, saved_at=%s, session_ts=%s",
       params=[instance, plan_text, ts, ts, plan_text, ts, ts])
print(f"[checkpoint] MySQL: {'OK' if r.get('ok') else r.get('error')}")

# 3. Git backup
plans_dir = Path(f"L:/GitHub/lg13-{instance}/plans")
plans_dir.mkdir(exist_ok=True)
pf = plans_dir / f"{instance}_current.md"
pf.write_text(f"# Checkpoint — {ts}\n\n{plan_text}", encoding='utf-8')
try:
    subprocess.run(["git", "-C", str(plans_dir.parent), "add", str(pf)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(plans_dir.parent), "commit", "-m", f"chore: checkpoint {ts}"],
        check=True, capture_output=True)
    print(f"[checkpoint] Git OK")
except Exception as e:
    print(f"[checkpoint] Git: {e}")

# 4. Jarvis status report (chat_messages → viditelné na web-up Jarvis)
status_msg = f"[CHECKPOINT] {instance} @ {ts}"
# Přidej krátký popis co aktuálně děláš (volitelné — doplň dle kontextu)
r2 = db("INSERT INTO chat_messages (from_inst, to_inst, msg, channel) VALUES (%s,'all',%s,'jarvis')",
        params=[instance, status_msg])
print(f"[checkpoint] Jarvis: {'OK' if r2.get('ok') else r2.get('error')}")

print(f"[checkpoint] DONE @ {ts} — od tohoto bodu lze pokracovat v nove session")
```

### 5 — remember (handoff note)

```
/remember:remember
```

Automaticky se zavolá jako poslední krok checkpointu.

---

## KDY VOLAT

- Před `/compact` nebo `/clear` (povinné)
- Po dokončení každého důležitého tasku
- Každých ~30 min při delší práci
- Kdykoliv chceš "save point" od kterého lze navázat

---

## JAK POKRAČOVAT Z CHECKPOINTU

Nová session:
```
1. /lg13-skills:sr      ← načte checkpoint (load-from-store + remember)
2. pokračuj v práci
```

---

## RELATED

- `/lg13-skills:save-min` — těžší varianta (session_manager + save-to-store + remember)
- `/lg13-skills:sr` — načte checkpoint při startu session
- `/remember:remember` — handoff note (volá se automaticky)
- Jarvis: luky.ai-domy.cz/jarvis/ — chat_messages tabulka zobrazuje checkpointy
