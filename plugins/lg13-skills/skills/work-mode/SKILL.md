---
name: work-mode
description: "Self-paced heartbeat loop — team nebo solo work mode. Bootstrap: Monitor arm + ScheduleWakeup fallback + read-react-report cyklus. Trigger: 'work mode', '/work-mode', 'work mode team', 'work mode solo', 'nastav loop', 'spusť heartbeat loop'."
user-invocable: true
---

# work-mode — Self-paced heartbeat loop

## VARIANTY

```
/work-mode solo    ← 1 instance, solo loop bez koordinace
/work-mode team    ← 3 instance, avengers-meeting + heartbeat na každé
```

Default bez arg = **solo**.

---

## TOKEN BUDGET

| Operace | Tokeny |
|---------|--------|
| Ping-pong pong | ~100 |
| Issue-sync delta | ~200 |
| ScheduleWakeup | ~50 |
| Monitor arm | ~50 |
| Per-iterace celkem | ~400 |

**Cíl:** < 500 tokenů/iterace. Nečti velké soubory. Grep místo Read.

---

## SOLO MODE

### Bootstrap (jednou na začátku)

**Krok 1 — Arm Monitor** na ping-pong dir:

```bash
python L:/LG13/app/agent/tmonkey_arm.py --instance <inst> --interval 2 --timeout 86400
```

**Krok 2 — ScheduleWakeup fallback** (270s = cache-warm, ne 300s):

Volej `ScheduleWakeup` tool s:
- `delaySeconds: 270`
- `prompt: /lg13-skills:work-mode solo`
- `reason: heartbeat loop fallback — cache warm`

**Krok 3 — Initial pong** stratu (PLAN STATUS, < 100 tokenů):

```python
import json, time
from pathlib import Path

ts = time.strftime('%Y-%m-%dT%H%M%SZ', time.gmtime())
pong = {
    'from': '<inst>', 'to': 'strat', 'ts': ts,
    'round': 'HB', 'type': 'ping',
    'subject': '[HB] <inst> alive — work-mode solo',
    'body': '## PLAN STATUS\n- loop: active\n- task: <current>\n- zone: green',
    'priority': 'P3', 'context_pct': <ctx>, 'compact_signal': False,
    'emergency_broadcast': False, 'emergency_subject': ''
}
Path(f'L:/LG13/runtime/ops/ping_pong/<inst>_to_strat_{ts}.json').write_text(
    json.dumps(pong, ensure_ascii=False), encoding='utf-8')
```

### Per-iterace (každý wake event)

1. **Přečti ping-pong** — jen nové soubory od posledního wake:
   ```bash
   python -c "
   from pathlib import Path; import os
   files = sorted(Path('L:/LG13/runtime/ops/ping_pong/').glob('*_to_<inst>_*.json'),
                  key=lambda f: f.stat().st_mtime, reverse=True)
   for f in files[:3]: print(f.name)
   "
   ```

2. **Reaguj** — jen pokud přišel P1/P0 ping. P2/P3 ignoruj.

3. **Report** — po každém tasku krátký pong (< 5 řádků).

4. **ScheduleWakeup znovu** — 270s fallback pro příští iteraci.

### Exit podmínky

- Tom napíše STOP
- `context_pct > 80` → `/lg13-skills:save-min` → `/compact`
- Task queue prázdná → sleep (neplánuj ScheduleWakeup)

---

## TEAM MODE

```
/work-mode team
```

= Zkratka pro:

1. `/lg13-skills:avengers-meeting` — quick sync (5 min max)
2. Každá instance spustí `/work-mode solo` po meetingu
3. Strat koordinuje přes ping-pong, ostatní reagují

**Coder v team mode:**
- čeká na task od stratu
- reportuje DONE/FAIL přes pong
- heartbeat každých 15 min

---

## KEEP-AWAKE CLAUSE

Pokud session ticho > 13 min a Monitor nevzbudí → ScheduleWakeup 270s funguje jako backup.

Nikdy nespouštěj ScheduleWakeup pod 60s — cache miss + zbytečné náklady.

---

## RELATED

- `heartbeat` — jednoduchší varianta (jen pong, bez loop logiky)
- `avengers-meeting` — team koordinace (team mode základ)
- `loop` (bundled) — generický loop bez LG13 kontextu
- `ping-pong` — protokol pro inter-instance komunikaci
