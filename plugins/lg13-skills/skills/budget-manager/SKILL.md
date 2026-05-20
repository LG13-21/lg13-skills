---
name: budget-manager
description: "Řízení token budgetu napříč LG13 instancemi. Instance s touto rolí čte aktuální spotřebu, alokuje kapacitu ostatním, varuje před limitem a předává roli dál. Trigger: 'budget manager', 'kdo řídí budget', 'předej budget management', 'jak jsme na tokenech', 'zkontroluj budget'."
user-invocable: true
---

# Budget Manager — Token řízení pro LG13

## ROLE

Jedna instance drží roli **budget managera** pro daný token window (5h reset nebo week).
- **Čte** spotřebu za všechny instance
- **Alokuje** kapacitu na tasky (žádosti přes ping-pong)
- **Varuje** ostatní při blížícím se limitu
- **Předává** roli jiné instanci pokud má sama málo kontextu

Aktuální holder: uložen v `L:/LG13/runtime/ops/budget_manager_state.json`

---

## ČTENÍ STAVU

```python
import subprocess, sys, json

r = subprocess.run([sys.executable, 'L:/LG13/app/agent/skills/claude_usage_read.py', '--json'],
    capture_output=True, text=True, timeout=5)
usage = json.loads(r.stdout)

print(f"session: {usage.get('session_pct')}%")
print(f"weekly_all: {usage.get('weekly_all')}%")
print(f"plan: {usage.get('plan')}")
print(f"resets_in: {usage.get('resets_in')}")
```

---

## FREKVENCE HLÍDÁNÍ

| Situace | Frekvence čtení |
|---------|----------------|
| Těžká práce (F-cyklus, Opus subagenti, paralelní tasky) | každé ~3 kola ping-pong |
| Normální práce (reasoning, drafty) | každých ~7 kol |
| Idle / FYI pony | každých ~15 kol nebo na žádost |
| Vždy | před spuštěním Opus subagenta nebo batch jobu |

---

## ALOKACE

Ostatní instance žádají kapacitu přes ping-pong:

```
subject: BUDGET_REQUEST — <task name> ~<odhad tokenů>K
body: Co potřebuji udělat, proč, urgency P0-P3
```

Budget manager odpoví:
- `APPROVED <Xk tokens>` — pokračuj
- `DEFER — weekly >90%, počkej na reset <datum>`
- `REDUCE — udělej jen <scope>, max <Xk>`

---

## THRESHOLDY

| weekly_all | Akce |
|------------|------|
| <80% | normální provoz |
| 80-90% | upozornit aktivní instance, defer P2/P3 |
| >90% | pouze P0/P1, žádné Opus subagenty bez explicitního Tom GO |
| >95% | STOP veškeré nové tasky, dokončit jen co běží |

| session_pct | Akce |
|-------------|------|
| >70% | compact_signal v pongu |
| >85% | doporučit /compact Tomovi |

---

## PŘEDÁNÍ ROLE

Předej roli pokud:
- Tvůj session_pct > 60% (blíží se compact)
- Jiná instance dělá hlavní práci v tomto window

```python
import json, time
from pathlib import Path

state_file = Path("L:/LG13/runtime/ops/budget_manager_state.json")
state = {
    "holder": "<new_instance>",
    "since_ts": time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime()),
    "handoff_from": "<me>",
    "reason": "<proč předávám>"
}
state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
```

Pak pingni nového holdera: `subject: BUDGET_HANDOFF — přebíráš budget management`

---

## KDO DRŽÍ ROLI TEĎ

```python
import json
from pathlib import Path

f = Path("L:/LG13/runtime/ops/budget_manager_state.json")
if f.exists():
    s = json.loads(f.read_text(encoding="utf-8"))
    print(f"Holder: {s['holder']} (od {s['since_ts']})")
else:
    print("Stav neexistuje — výchozí holder: strat")
```

---

## PRAVIDLA

- Tom **nedozoruje** — budget manager sám čte a alokuje
- Tom dostane FYI jen pokud weekly >90% nebo P0 blocker
- Role se **předává** — není fixní na strat
- Instance bez role **nečtou samy** — žádají budget managera

---

## PO WEEK RESETU

Reset = příležitost zvednout deferred plány. Budget manager po resetu:
1. Přečte `plans/` v `lg13-runtime-state` (viz skill `deferred-plans`)
2. Posoudí co je P0/P1 a má smysl zvednout
3. Pošle instance BUDGET_APPROVED s kapacitou na zvednuté tasky

## TOM FYI FORMÁT

Pokud weekly >90% nebo P0 blocker, pošli Tomovi stručně:

```
Budget alert: weekly <X>% (<plan>)
Blocked: <co nejde>
Návrh: <počkej na reset <datum> | redukuj scope na X>
```

Žádné dlouhé zprávy — Tom chce jen číslo + akci.

## RELATED

- `ping-pong` skill — komunikační kanál pro žádosti
- `token-limit-read` skill — čtení hodnot
- `L:/LG13/runtime/ops/budget_manager_state.json` — aktuální holder
