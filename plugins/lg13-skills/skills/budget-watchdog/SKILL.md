---
name: budget-watchdog
description: Proactive token budget monitoring. Watches weekly/session limits, sends alerts, enforces thresholds across instances. Triggers: 'budget watchdog', 'watch budget', 'hlidej budget', 'token watchdog', 'spust watchdog'
status: experimental
user-invocable: true
---

# budget-watchdog

## PURPOSE

Aktivní hlídač token budgetu. Na rozdíl od `budget-manager` (pasivní — odpovídá na requesty) watchdog **sám sleduje** limit a proaktivně varuje ostatní instance + Toma.

**Role:** strat nebo coder (domluvte se — viz COORDINATION sekce).
**Lifetime:** jedno session window (nebo do handoff).

---

## EXECUTION

### 1. Zjisti kdo je watchdog

```python
from pathlib import Path
import json

state_f = Path("L:/LG13/runtime/ops/budget_watchdog_state.json")
if state_f.exists():
    s = json.loads(state_f.read_text(encoding='utf-8'))
    print(f"Watchdog holder: {s['holder']} since {s['since_ts']}")
else:
    print("No watchdog active — default to strat")
```

### 2. Claim watchdog role

```python
import time, json
from pathlib import Path

me = "<instance>"   # coder nebo strat
state_f = Path("L:/LG13/runtime/ops/budget_watchdog_state.json")
state = {
    "holder": me,
    "since_ts": time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime()),
    "check_interval_s": 300,   # kontrola každých 5 minut
    "thresholds": {
        "weekly_all_warn": 80,
        "weekly_all_stop": 95,
        "session_compact": 70,
        "session_critical": 85
    }
}
tmp = state_f.with_suffix('.tmp')
tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
tmp.replace(state_f)
print(f"Watchdog claimed: {me}")
```

### 3. Watch loop (každých 5 minut)

```python
import subprocess, sys, json, time

INTERVAL = 300   # 5 minut

while True:
    r = subprocess.run([sys.executable, 'L:/LG13/app/agent/skills/claude_usage_read.py', '--json'],
        capture_output=True, text=True, timeout=5)
    if r.returncode != 0:
        time.sleep(INTERVAL)
        continue
    
    usage = json.loads(r.stdout)
    weekly = usage.get('weekly_all', 0)
    session = usage.get('session_pct', 0)
    
    # Thresholdy
    if weekly >= 95:
        fire_alert(level="CRITICAL", weekly=weekly, session=session)
    elif weekly >= 80:
        fire_alert(level="WARN", weekly=weekly, session=session)
    
    if session >= 85:
        fire_compact_signal(session=session)
    elif session >= 70:
        fire_compact_hint(session=session)
    
    time.sleep(INTERVAL)
```

### 4. Alert dispatch

```python
def fire_alert(level, weekly, session):
    """Pošli alert přes ping-pong broadcast (strat + coder + Tom FYI)."""
    import json, time
    from pathlib import Path
    
    base = Path("L:/LG13/runtime/ops/ping_pong")
    ts = time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime())
    
    body = f"""## ⚠️ BUDGET ALERT — {level}

- weekly_all: **{weekly}%**
- session_pct: {session}%

### Akce dle thresholdu:
"""
    if weekly >= 95:
        body += "- **STOP** veškeré nové tasky (P2+)\n- Dokončit jen co běží\n- Čekej na weekly reset"
    elif weekly >= 80:
        body += "- Defer P2/P3 tasky\n- Žádné Opus subagenty bez Tom GO\n- Notify aktivní instance"
    
    for target in ["strat", "coder", "legal"]:
        fname = f"watchdog_to_{target}_{ts}.json"
        msg = {
            "from": "watchdog", "to": target, "ts": ts,
            "round": "WATCHDOG",
            "type": "ping",
            "subject": f"[BUDGET-{level}] weekly={weekly}% session={session}%",
            "body": body,
            "decisions": {},
            "questions_for_other": [],
            "tokens_spent_estimate": 30,
            "context_pct": session,
            "compact_signal": session >= 70,
            "priority": "P0" if level == "CRITICAL" else "P1",
            "emergency_broadcast": level == "CRITICAL"
        }
        tmp = base / f".{fname}.tmp"
        tmp.write_text(json.dumps(msg, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(base / fname)
```

### 5. Compact signal pro vlastní instanci

```python
def fire_compact_signal(session):
    """Zapíše compact signal do ping_pong pro sebe."""
    # Heartbeat format — receiver ví že watchdog potřebuje compact
    pass  # viz heartbeat skill
```

### 6. Handoff při session end

```python
def handoff_watchdog(new_holder):
    """Předej watchdog roli jiné instanci."""
    # Update state file + ping nového holdera
    state["holder"] = new_holder
    state["handoff_from"] = me
    # ... (viz budget-manager handoff pattern)
```

---

## COORDINATION — Kdo drží roli?

**Výchozí:** strat drží watchdog roli (má nejvyšší přehled).
**Alternativa:** coder drží, pokud strat je busy nebo spí.

Koordinace:
1. Při session startu: zkontroluj `budget_watchdog_state.json` — je holder?
2. Pokud ne → strat si nárokuje automaticky (nebo coder pokud strat není aktivní)
3. Pokud holder spí >30 min → coder převezme (`takeover_watchdog()`)
4. Tom může kdykoli přidat `watchdog: <instance>` do #lg13

**Ping strat pro koordinaci** (coder toto pošle):
```
subject: [COORDINATION] budget-watchdog — kdo drží roli?
body: Tom přidal budget-watchdog skill. Kdo bere? Navrhuji: strat primární, coder fallback.
```

---

## THRESHOLDY (default, konfigurovatelné)

| Metrika | Warn | Stop | Compact |
|---------|------|------|---------|
| `weekly_all` | 80% | 95% | — |
| `session_pct` | 70% (hint) | 85% (critical) | 70% |

---

## RULES

- Watchdog je **pasivně aktivní** — sleep 5 min, check, sleep
- Jeden holder v jednom okamžiku — žádné duplikáty
- Při alert: vždy broadcast na všechny aktivní instance
- `emergency_broadcast: true` při weekly >= 95
- Tom dostane FYI jen při CRITICAL (ne každý warn)
- Watchdog NEdispatches tasky — jen hlídá a varuje

## RELATED

- Skill `budget-manager` — alokace (pasivní partner)
- Skill `heartbeat` — posílá `context_pct` každých 15 min → watchdog nemusí číst za jiné instance
- `L:/LG13/runtime/ops/budget_watchdog_state.json` — aktuální holder
- `L:/LG13/app/agent/skills/claude_usage_read.py` — zdroj dat
