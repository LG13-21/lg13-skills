---
name: budget-watchdog
description: Proactive token budget monitoring. Watches weekly/session limits AND GitHub Actions bot runs, sends alerts, enforces thresholds across instances. Triggers: 'budget watchdog', 'watch budget', 'hlidej budget', 'token watchdog', 'spust watchdog'
status: stable
user-invocable: true
---

# budget-watchdog

## PURPOSE

Aktivní hlídač token budgetu. Na rozdíl od `budget-manager` (pasivní — odpovídá na requesty) watchdog **sám sleduje** limit a proaktivně varuje ostatní instance + Toma.

**Dva zdroje dat:**
1. `claude_usage_read.py` — interaktivní session (weekly_all%, session_pct%)
2. GitHub Actions `gh run list` — bot runy (minuty, USD estimate)

**Role:** strat nebo coder.
**Lifetime:** jedno session window (nebo do handoff).

---

## KNOWN DIET FIXES (udělat při první příležitosti)

| Fix | Dopad | Status |
|-----|-------|--------|
| Smazat `L:\GitHub\CLAUDE.md` | -4k tok/turn (legal memory isolation) | ⏳ Tom action |
| `max_turns: 5` + `timeout_minutes: 8` v claude.yml | bot run max ~8 min | ✅ done 2026-05-26 |
| Méně tool calls per turn — batching | -30% overhead | ongoing |
| Loop systémy jen pokud token-efficient | závisí na audit | viz níže |

### Loop audit — co běží a zda se to vyplatí

Aktuálně aktivní procesy (2026-05-26):
```
pl_server.py        ×3 (PID 7120/9400/51684) — CPU: 802/2100/796s — OK, nutný
listen_aggregator   ×4 (coder/strat/legal/t002) — CPU: 411/417/1967/1606s
ntfy_listener.py    ×1 — CPU: 1050s
wake_dispatcher.py  ×1 — CPU: 305s
```

**listen_aggregator**: spouštěj jen pro instance které jsou aktivní v dané session.
Pokud legal session nespuštěna → `listen_aggregator --instance legal` zbytečně žere CPU.

**Pravidlo:** 1 listen_aggregator per aktivní instance. Při session end → kill.

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

me = "<instance>"
state_f = Path("L:/LG13/runtime/ops/budget_watchdog_state.json")
state = {
    "holder": me,
    "since_ts": time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime()),
    "check_interval_s": 300,
    "thresholds": {
        "weekly_all_warn": 80,
        "weekly_all_stop": 95,
        "session_compact": 70,
        "session_critical": 85,
        "bot_cost_warn_usd": 2.0,
        "bot_cost_stop_usd": 5.0
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

INTERVAL = 300
bot_check_counter = 0

while True:
    r = subprocess.run([sys.executable, 'L:/LG13/app/agent/skills/claude_usage_read.py', '--json'],
        capture_output=True, text=True, timeout=5)
    if r.returncode != 0:
        time.sleep(INTERVAL)
        continue

    usage = json.loads(r.stdout)
    weekly = usage.get('weekly_all', 0)
    session = usage.get('session_pct', 0)

    # Bot check každých 15 min (šetří gh API rate limit)
    bot_check_counter += 1
    bot_data = check_bot_runs() if bot_check_counter % 3 == 0 else {"bot_cost_usd": 0, "bot_minutes_today": 0, "per_repo": {}}

    if weekly >= 95:
        fire_alert(level="CRITICAL", weekly=weekly, session=session, bot=bot_data)
    elif weekly >= 80:
        fire_alert(level="WARN", weekly=weekly, session=session, bot=bot_data)

    if bot_data["bot_cost_usd"] >= 5.0:
        fire_alert(level="CRITICAL-BOT", weekly=weekly, session=session, bot=bot_data)
    elif bot_data["bot_cost_usd"] >= 2.0:
        fire_alert(level="WARN-BOT", weekly=weekly, session=session, bot=bot_data)

    if session >= 85:
        fire_compact_signal(session=session)
    elif session >= 70:
        fire_compact_hint(session=session)

    time.sleep(INTERVAL)
```

### 4. Bot run checker

```python
def check_bot_runs():
    import subprocess, json
    from datetime import datetime, timezone

    REPOS = ["LG13-21/lg13-coder", "LG13-21/tmonkey",
             "LG13-21/lg13-strat", "LG13-21/legal-ship-2026"]
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    total_sec = 0
    per_repo = {}

    for repo in REPOS:
        r = subprocess.run(
            ["gh", "run", "list", "--repo", repo, "--workflow", "claude.yml",
             "--limit", "20", "--json", "conclusion,createdAt,updatedAt"],
            capture_output=True, text=True, timeout=15)
        if r.returncode != 0:
            continue
        runs = json.loads(r.stdout)
        repo_sec = 0; repo_count = 0
        for run in runs:
            if run['createdAt'][:10] == today and run['conclusion'] == 'success':
                c = datetime.fromisoformat(run['createdAt'].replace('Z', '+00:00'))
                u = datetime.fromisoformat(run['updatedAt'].replace('Z', '+00:00'))
                repo_sec += int((u - c).total_seconds())
                repo_count += 1
        per_repo[repo.split('/')[1]] = {"count": repo_count, "seconds": repo_sec}
        total_sec += repo_sec

    cost_usd = total_sec / 60 * 0.06
    return {"bot_minutes_today": round(total_sec / 60, 1),
            "bot_cost_usd": round(cost_usd, 2), "per_repo": per_repo}
```

### 5. Alert dispatch

```python
def fire_alert(level, weekly, session, bot):
    import json, time
    from pathlib import Path

    base = Path("L:/LG13/runtime/ops/ping_pong")
    ts = time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime())
    is_critical = "CRITICAL" in level

    body = f"""## ⚠️ BUDGET ALERT — {level}

### Interaktivní session
- weekly_all: **{weekly}%** | session_pct: {session}%

### GitHub Actions boty (dnes)
- Celkem: {bot['bot_minutes_today']} min | ~${bot['bot_cost_usd']:.2f}
"""
    for repo, d in bot.get('per_repo', {}).items():
        if d['count'] > 0:
            body += f"  - {repo}: {d['count']} runů, {d['seconds']//60}min\n"

    body += "\n### Akce:\n"
    if is_critical and "BOT" not in level:
        body += "- **STOP** veškeré nové tasky (P2+)\n- Čekej na reset"
    elif "BOT" in level:
        body += "- Snížit @claude triggery\n- max_turns již nastaven na 5"
    else:
        body += "- Defer P2/P3\n- Žádné Opus subagenty bez Tom GO"

    for target in ["strat", "coder", "legal"]:
        fname = f"watchdog_to_{target}_{ts}.json"
        msg = {
            "from": "watchdog", "to": target, "ts": ts,
            "round": "WATCHDOG", "type": "ping",
            "subject": f"[BUDGET-{level}] weekly={weekly}% bots=${bot['bot_cost_usd']:.2f}",
            "body": body, "decisions": {}, "questions_for_other": [],
            "tokens_spent_estimate": 30, "context_pct": session,
            "compact_signal": session >= 70,
            "priority": "P0" if is_critical else "P1",
            "emergency_broadcast": is_critical
        }
        tmp = base / f".{fname}.tmp"
        tmp.write_text(json.dumps(msg, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(base / fname)
```

---

## THRESHOLDY

| Metrika | Warn | Critical |
|---------|------|----------|
| `weekly_all` | 80% | 95% |
| `session_pct` | 70% (compact hint) | 85% (compact now) |
| `bot_cost_usd/day` | $2.00 | $5.00 |

---

## RULES

- Sleep 5 min, check, sleep — pasivně aktivní
- Bot check každých **15 min** (ne každých 5 — šetří gh API)
- Jeden holder — žádné duplikáty
- Emergency broadcast při weekly >= 95 nebo bot_cost >= $5
- Tom FYI jen při CRITICAL
- Watchdog NEdispatches tasky — jen hlídá

## RELATED

- Skill `budget-manager` — alokace (pasivní partner)
- `L:/LG13/runtime/ops/budget_watchdog_state.json` — holder state
- `L:/LG13/app/agent/skills/claude_usage_read.py` — usage data
- `gh run list` — bot data
