---
name: diamond-sentry
description: "Use when scanning for key insights (diamonds) from conversations, atoms, or documents. Auto-detects current instance (coder/legal/strat) and uses the correct scoring mode. Trigger: 'spusť sentry', 'diamond scan', 'najdi diamondy', '/diamond-sentry'."
user-invocable: true
---

# Diamond Sentry — Autonomní diamond extraction organism

## CONCEPT

Ne grep. Ne indexer. Emergence detection — hledá unusually strong structures, compressed insights, reusable patterns, operational breakthroughs. **Nepředpokládá, co hledá.**

---

## KROK 1 — Detekuj instanci a mode

```python
from pathlib import Path
cwd = Path.cwd()
INSTANCE_MAP = {
    'lg13-coder':      ('coder', 'ops'),
    'T000_Strat':      ('strat', 'ops'),
    'lg13-strat':      ('strat', 'ops'),
    'legal-ship-2026': ('legal', 'legal'),
}
instance, mode = next(
    ((v, m) for k, (v, m) in INSTANCE_MAP.items() if k in str(cwd)),
    ('coder', 'ops')
)
print(f"[sentry] instance={instance} mode={mode}")
```

| Instance | Mode   | Hledá |
|----------|--------|-------|
| **coder** | `ops`  | Architektura, mechanismy, invarianty, doctrine |
| **strat** | `ops`  | Koordinace, rozhodnutí, operational patterns |
| **legal** | `legal`| Soudní reference, §, data DD.MM.YYYY, právní argumenty |

---

## KROK 2 — Zjisti kontext (pokud nemáš explicitní zadání)

Pokud `/diamond-sentry` nemá argumenty, přečti kontext vlákna:

```python
from pathlib import Path, datetime
# Tail STAV_NOW.md — co řeším teď
stav = Path('L:/GitHub/lg13-coder/STAV_NOW.md')
if stav.exists():
    lines = stav.read_text(encoding='utf-8', errors='replace').splitlines()
    print('\n'.join(lines[-40:]))

# Nejnovější ping-pong pro tuto instanci
import glob, os
pp_dir = 'L:/LG13/runtime/ops/ping_pong/'
files = sorted(glob.glob(f'{pp_dir}*_to_{instance}_*.json'), key=os.path.getmtime, reverse=True)
if files:
    import json
    msg = json.loads(open(files[0], encoding='utf-8').read())
    print('Latest ping:', msg.get('subject', ''))
    print(msg.get('body', '')[:500])
```

Z toho urči:
- **Časové okno** — F-verze (F31, F32) nebo datum (posledních 7 dní)
- **Doménový focus** — legal F31, coding pipeline, konkrétní conv_id

---

## KROK 3 — Spusť sentry (default: CGE + atoms + newest)

Pokud nemáš explicitní `--target`, vždy prohledej:

```python
import subprocess, sys, time

PYTHON = sys.executable
SENTRY = 'L:/GitHub/lg13-coder/agent/skills/diamond_sentry.py'
OUTPUT = 'L:/LG13/runtime/diamonds'
TODAY = time.strftime('%Y-%m-%d')

# Určeno z KROK 1:
# mode = 'ops' nebo 'legal'
# instance = 'coder', 'strat', nebo 'legal'

targets = [
    ('CGE-primary',  'L:/GitHub/legal-ship-2026/ChatGPT_export', f'--around {TODAY}:7d'),
    ('CGE-secondary','L:/LG13/inbox/chatgpt',                    f'--around {TODAY}:7d'),
    ('atoms',        'L:/LG13/atoms/realtime',                   f'--around {TODAY}:3d'),
]

for label, target, around_arg in targets:
    from pathlib import Path
    if not Path(target).exists():
        print(f'[sentry] SKIP {label} — adresář neexistuje')
        continue
    cmd = [
        PYTHON, SENTRY,
        '--target', target,
        '--recursive',
        '--mode', mode,
        '--limit', '40',
        '--output', OUTPUT,
        around_arg.split()[0], around_arg.split()[1],
    ]
    print(f'[sentry] {label}: {" ".join(cmd[-6:])}')
    subprocess.run(cmd, check=False)
```

### Override — pokud máš explicitní zadání

```bash
# Konkrétní adresář:
python L:/GitHub/lg13-coder/agent/skills/diamond_sentry.py \
  --target L:/LG13/dokuments/F31 \
  --recursive --mode legal --limit 50

# F-verze filter:
python L:/GitHub/lg13-coder/agent/skills/diamond_sentry.py \
  --target L:/LG13/ChatGPT_export \
  --recursive --mode legal --around F31:2v --limit 50

# Datum filter:
python L:/GitHub/lg13-coder/agent/skills/diamond_sentry.py \
  --target L:/LG13/ --recursive --mode ops --around 2026-06-01:5d
```

---

## PARAMETRY

| Parametr | Výchozí | Popis |
|----------|---------|-------|
| `--target PATH` | *(CGE+atoms)* | Cílový adresář nebo soubor |
| `--mode ops\|legal` | *z instance* | Scoring mode |
| `--recursive` | true (default pro CGE/atoms) | Procházej podadresáře |
| `--limit N` | 40 | Max diamondů |
| `--around YYYY-MM-DD[:Nd]` | TODAY:7d | Časový filtr (±N dní) |
| `--around F<ver>[:Nv]` | — | Filtr podle F-verze |
| `--output DIR` | L:/LG13/runtime/diamonds | Výstupní adresář |
| `--types md,json,txt` | md,json,txt | Typy souborů |

---

## OUTPUT FILES

| Soubor | Obsah |
|--------|-------|
| `diamonds[_legal]_TS.json` | Diamandy s metadata (score, recurrence, sources) |
| `doctrines[_legal]_TS.md` | Top 10 čitelně |
| `unresolved[_legal]_TS.md` | Borderline (score 1–threshold) |

Threshold: `ops` = 3.0, `legal` = 4.0

---

## PRAVIDLA

- **Nikdy nepouštěj legal mode pro coder** a naopak — mode = instance
- **CGE vždy** — Tom mluví v ChatGPT, CGE je primární zdroj pravdy
- **CGE cesta** — `L:/GitHub/legal-ship-2026/ChatGPT_export/` (262+ JSON souborů, verifikováno 2026-06-05)
- **atoms vždy** — filtrované a klasifikované, málo noise; subdirs v `L:/LG13/atoms/realtime/` každý s `atoms.json`
- **--around pro newest** — bez time filtru skenuje vše (pomalé + stará data)
- Pokud CGE nebo atoms neexistují → SKIP (nevyhoď error, pokračuj)

---

## RELATED

- `diamond-pick` — Lex Atomic triáž z výstupu sentry (KEEP/DROP/REFORMULATE)
- `atom-search` — search v existující atom databázi
- `deep-read` — issues + ChatGPT od posledního kurzoru
