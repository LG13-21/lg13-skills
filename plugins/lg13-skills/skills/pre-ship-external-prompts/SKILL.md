# pre-ship-external-prompts — External review prompt generator

## PURPOSE

Generuje prompty pro **external pre-ship analýzu** od CDC (Claude Desktop Cowork) a ChatGPT.
Toto je LOCK 3 (external) v pipeline — nezávislý reviewer před TIME a TOM lockem.

Ideálně odešle prompty automaticky (CDC přes Slack/ping-pong, ChatGPT přes GitHub issue).

---

## TRIGGER

Tom napíše: "external prompty", "cdc analýza", "chatgpt pre-ship", "external review", "vygeneruj locky"

Nebo legal instance volá manuálně po LOCK 2 (STRAT PASS).

---

## PIPELINE POZICE

```
LEGAL PASS → STRAT PASS → [EXTERNAL: CDC + ChatGPT] → TIME → TOM → T002
```

CDC a ChatGPT jsou **paralelní** — mohou běžet současně.
Oba musí vrátit GO/CONDITIONAL_GO před TIME lock.

---

## EXECUTION

### Krok 1 — Detekuj aktuální F-cyklus

```python
import json
from pathlib import Path

# Najdi meta.json pro aktivní dokumenty
meta_files = list(Path('.').glob('F*/meta.json'))
active = []
for m in meta_files:
    data = json.loads(m.read_text(encoding='utf-8'))
    stav = data.get('stav', '')
    if 'waiting' in stav or stav == 'ready':
        active.append((m.parent.name, data))
        
print('Aktivní dokumenty:', [a[0] for a in active])
```

### Krok 2 — Ověř vstupní složky F36/F37

```python
required = {
    'F36': Path('F36'),   # = F31 BALIK_B
    'F37': Path('F37'),   # = F34 BALIK_A
}
for name, p in required.items():
    if p.exists():
        pdfs = list(p.glob('*.pdf'))
        print(f'{name}/: {len(pdfs)} PDF - OK')
    else:
        print(f'ERROR: {name}/ chybí - spusť attachment-pipeline nebo rozbal ISDS ZIP')
```

### Krok 3 — Vytvoř output adresáře

```python
for name in ['F36', 'F37']:
    Path(f'cdc/{name}').mkdir(parents=True, exist_ok=True)
    print(f'cdc/{name}/ ready')
```

### Krok 4 — Generuj CDC prompt

Zkopíruj template `cdc/PROMPT_CDC_F36_F37.md` do `ChatGPT_export/` pro automatické čtení:

```python
import shutil
from datetime import date

template = Path('cdc/PROMPT_CDC_F36_F37.md')
target = Path(f'ChatGPT_export/CDC_PROMPT_{date.today().isoformat()}.md')
shutil.copy(template, target)
print(f'CDC prompt → {target}')
```

### Krok 5 — Vytvoř GitHub issue pro ChatGPT prompt

```bash
# GitHub CLI — vytvoří issue s ChatGPT promptem
gh issue create \
  --title "PRE-SHIP: ChatGPT external analysis F36+F37 [$(date +%Y-%m-%d)]" \
  --body-file cdc/PROMPT_CHATGPT_F36_F37.md \
  --label "pre-ship,external-review,F36,F37" \
  --assignee "@me"
```

Issue číslo ulož do `cdc/state.json`:
```json
{
  "chatgpt_issue": <číslo>,
  "cdc_prompt_ts": "<datum>",
  "status": "waiting_external_review"
}
```

### Krok 6 — Ping strat pro CDC dispatch

Pošli ping-pong strat instanci:
```
subject: EXTERNAL_REVIEW_READY
body: CDC prompt připraven v cdc/PROMPT_CDC_F36_F37.md + ChatGPT issue #<N>.
Potřebuju dispatch CDC session pro /total-analysis-all-in-one F36+F37.
Output: cdc/F36/ a cdc/F37/ + LOCK_CDC_*.json
```

### Krok 7 — Čekej na unlock soubory

Monitor na lock soubory:
```python
import time
from pathlib import Path

locks_needed = ['cdc/LOCK_CDC_F36_GO.json', 'cdc/LOCK_CDC_F37_GO.json']
# + ChatGPT lock z GitHub issue nebo manuálně
```

---

## UNLOCK SCHEMA

### CDC lock (generuje CDC instance):
```json
{
  "lock": "CDC",
  "doc": "F36",
  "verdict": "GO",
  "score": 8.5,
  "ts": "2026-06-04T09:00:00Z",
  "analyst": "claude-desktop-cowork",
  "conditions": [],
  "blocking_issues": [],
  "ship_recommendation": "SHIP"
}
```

### ChatGPT lock (generuje Tom nebo ChatGPT přes script):
```json
{
  "lock": "CHATGPT",
  "doc": "F36",
  "verdict": "GO",
  "score": 8.3,
  "ts": "2026-06-04T10:00:00Z",
  "analyst": "chatgpt-4o",
  "conditions": [],
  "issue_ref": "#<číslo>",
  "ship_recommendation": "SHIP"
}
```

---

## TIME CAPSULE INTEGRACE

Po získání všech locků:
```
LOCK_CDC_F36_GO.json + LOCK_CDC_F37_GO.json
LOCK_CHATGPT_F36_GO.json + LOCK_CHATGPT_F37_GO.json
```

→ Tyto 4 soubory + existující LOCK_LEGAL + LOCK_STRAT = kompletní sada pro TIME_CAPSULE.

BAT soubor na ploše `CHECK_CAPSULE_LOCKS.bat` ověří všechny locky a uvolní T002 k odeslání.

---

## FULL LOCK CHAIN (target stav)

```
LOCK 1: LEGAL      → meta.json locks_v2.legal.status = PASS ✅
LOCK 2: STRAT      → meta.json locks_v2.strat.status = PASS (čeká)
LOCK 3: CHATGPT    → cdc/LOCK_CHATGPT_F3X_GO.json (čeká)
LOCK 3b: CDC       → cdc/LOCK_CDC_F3X_GO.json (čeká)
LOCK 4: TIME       → meta.json locks_v2.time.status = PASS (čeká)
LOCK 5: TOM        → "KONEC STOP" explicitně
LOCK 6: T002       → ISDS odeslání (Tom osobně)
```

Tom pak potvrdí přes Gemini app nebo ChatGPT nebo `CHECK_CAPSULE_LOCKS.bat` na ploše.

---

## SOUBORY

```
cdc/
├── PROMPT_CDC_F36_F37.md         ← CDC prompt (generuje tento skill)
├── PROMPT_CHATGPT_F36_F37.md     ← ChatGPT prompt (generuje tento skill)
├── state.json                    ← stav external review
├── LOCK_CDC_F36_GO.json          ← generuje CDC
├── LOCK_CDC_F37_GO.json          ← generuje CDC
├── LOCK_CHATGPT_F36_GO.json      ← generuje Tom/ChatGPT
├── LOCK_CHATGPT_F37_GO.json      ← generuje Tom/ChatGPT
├── F36/                          ← CDC analýza output
│   ├── 01_fast_read.md ... 09_scorecard.md
│   └── go_no_go.json
└── F37/
    ├── 01_fast_read.md ... 09_scorecard.md
    └── go_no_go.json
```

---

## RULES

- Generuj prompty VŽDY po LOCK 2 (STRAT PASS) nebo explicitně
- CDC a ChatGPT jsou paralelní — nečekej na jeden před druhým
- Lock soubory = strojově čitelné — BAT/script může automaticky ověřit
- STOP ORDER #1452 platí absolutně — lock soubory != odeslání
- Tom může override libovolný lock explicitním "OK beru"

---

## RELATED

- `locks-workflow` — 5-LOCKS pipeline (LOCK 3 = CHATGPT/CDC)
- `filing-pipeline` — Phase 3 send
- `CHECK_CAPSULE_LOCKS.bat` — Tom spouští pro finální ověření
- `cdc/PROMPT_CDC_F36_F37.md` — CDC prompt template
- `cdc/PROMPT_CHATGPT_F36_F37.md` — ChatGPT prompt template
