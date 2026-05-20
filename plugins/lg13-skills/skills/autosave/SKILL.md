---
name: autosave
description: "Auto-save + auto-compact při 15-25% zbývajícího kontextu. Dokončí rozdělanou věc, uloží stav, pak compact. Save bez compactu nedává smysl — vždy jdou spolu. Trigger: 'autosave', 'auto save', 'ulož a compact', 'save a compact', 'context se plní', 'dochází kontext', nebo automaticky když edge-check vrátí yellow/orange/red zone. Použij jako sloučenou funkci místo ručního save + /compact."
user-invocable: true
---

# Autosave — Save + Compact jako jedna funkce

## PROČ TOHLE EXISTUJE

Save bez compactu je zbytečný — context se neuvolní. Compact bez save = ztráta stavu.
Tenhle skill je sloučená funkce: dokončí, uloží, zkompaktuje — v jednom kroku.

Trigger zone: **15-25% zbývajícího kontextu** (ne přesně na hranici — dokončit co běží, pak spustit).

---

## VARIANTY

### A — Okamžitý save + compact (default)
Použij když: jsi na přirozeném konci tasku, nic kritického neběží.
```
save-min → /compact
```

### B — Save teď, compact po další odpovědi
Použij když: máš ještě 1 krátkou věc k dokončení, pak compact.
Řekni Tomovi: „Uloženo — po další odpovědi /compact."

### C — Save bez compactu (výjimečně)
Použij jen pokud: čekáš na Tom input a compact by přerušil čekání.
Bez compactu context dál roste — použij jen jako přemostění.

---

## EXECUTION

### Krok 1 — Force refresh usage dat + zkontroluj kde jsi

Usage data mohou být stale (TM nerefreshnul). Před rozhodnutím vždy refreshnout:

```python
import subprocess, sys, json
from pathlib import Path
from datetime import datetime, timezone

# Zkontroluj stáří dat
state_file = Path("L:/LG13/runtime/usage_state.json")
if state_file.exists():
    data = json.loads(state_file.read_text(encoding='utf-8'))
    ingested = data.get('ingested_at', '')
    # Pokud starší než 3 min → force refresh přes Playwright Edge
    try:
        from datetime import datetime, timezone
        age_s = (datetime.now(timezone.utc) - datetime.fromisoformat(ingested.replace('Z','+00:00'))).seconds
        stale = age_s > 300  # 5 min threshold
    except:
        stale = True
else:
    stale = True

if stale:
    print("Usage stale — refreshuji přes Playwright...")
    # Naviguj na claude.ai/settings/usage v Edge → TM zachytí a uloží
    subprocess.run([sys.executable, '-c', '''
import asyncio
from playwright.async_api import async_playwright
async def r():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            "C:/Users/tom/AppData/Local/Microsoft/Edge/User Data",
            channel="msedge", headless=True,
            args=["--profile-directory=Default"]
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://claude.ai/settings/usage", timeout=15000)
        await page.wait_for_timeout(4000)
        await ctx.close()
asyncio.run(r())
'''], capture_output=True, timeout=25)
    import time; time.sleep(2)  # TM zapíše

# Přečti aktuální data
r = subprocess.run([sys.executable, 'L:/LG13/app/agent/skills/claude_usage_read.py', '--json'],
    capture_output=True, text=True, timeout=5)
usage = json.loads(r.stdout)
session_pct = usage.get('session_pct', 0)
print(f"session: {session_pct}% (weekly: {usage.get('weekly_all')}%)")
```

Nebo použij `edge-check` skill pro zone + turns_remaining.

### Krok 2 — Rozhodni kdy spustit

**Primární trigger: rate/hr** (Tom directive 2026-05-13 — platí pro Sonnet modely)

| Podmínka | Akce |
|----------|------|
| rate/hr < $1.00 | Pokračuj — kontext normální *(Sonnet)* |
| rate/hr ≥ $1.00 (sustained) | **AUTOCOMPACT** — dokončit aktuální větu, pak spustit *(Sonnet)* |
| rate/hr ≥ $2.00 | Spustit ihned *(Sonnet)* |
| rate/hr ≥ $5.00 | Spustit ihned *(Opus)* |
| Haiku | TBD — zatím jen context % trigger |

"Sustained" = rate drží nad $1 déle než ~2 min (ne peak burst). Jednorázový spike = ignoruj.

**Sekundární trigger: context %** (fallback když rate neznámé)

| session_pct zbývá | Akce |
|-------------------|------|
| >25% zbývá | Ještě čas — pokračuj |
| 15-25% zbývá | **Sweet spot** — dokončit aktuální task, pak autosave |
| <15% zbývá | Spustit ihned, i uprostřed |

Rate/hr čteš z `usage_state.json` → pole `rate_usd_hr` (TM zapisuje). Pokud stale >5 min → fallback na context %.

Nedojdi přesně na hranici — spusť na přirozeném konci: hotový draft, odeslaný ping, checkpoint.

### Krok 3 — Save (save-min)

```bash
# 1. Queue done (pokud máš aktivní task)
python L:/LG13/app/agent/instance_queue.py --done --id <ID> --result "autosave checkpoint"

# 2. STAV_NOW.md append
# Přidej 3 bullety: co se hnulo, co čeká, kde jsme přerušili

# 3. Volitelně: ping strat o stavu (pokud důležitý kontext)
```

### Krok 4 — Compact (automaticky, bez ptání)

Autocompact je nakonfigurován v settings — instance smí spustit `/compact` sama.
Po save rovnou: `/compact`

Neoznamovat, neptát se — jen spustit. Tom to nastavil záměrně.

---

## AUTOMATICKÉ HLÍDÁNÍ

Aby se autosave spouštěl bez ručního triggeru — instance si hlídá kontext průběžně:

- Po každém milníku (odeslán ping, hotový draft, dokončen task) zkontrolovat session_pct
- Pokud 15-25% zbývá a je přirozený konec → spustit autosave
- Nehlídat uprostřed věty nebo rozdělaného tasku — čekat na konec

Toto není polling — je to check na přirozených checkpointech.

---

## PRAVIDLA

- Save a compact jsou neoddělitelné — Varianta C jen výjimečně
- Přirozený konec > přesná hranice — raději 20% než přerušit uprostřed
- Knowledge base přežije compact — context-mode FTS5 zůstane
- Po compactu: STAV_NOW.md + ping_pong history + memory = kontinuita
- Instance spouští /compact sama — autocompact je nakonfigurován v settings

---

## RELATED

- `edge-check` skill — zone + turns_remaining výpočet
- `save-min` skill — detailní save kroky
- `ping-pong` — compact_signal: true když session_pct > 70%
- `budget-manager` — koordinace timing compactu přes instance
