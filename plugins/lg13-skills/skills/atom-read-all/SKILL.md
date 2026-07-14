---
name: atom-read-all
description: Use when receiving any wake event about atoms — enforces reading atom content before any routing decision. Prevents the pattern of skipping atoms with "not for me" or "wrong routing" without reading.
user-invocable: false
---

# Atom Read All — Nikdy neříkej "není pro mě" bez čtení

## PRAVIDLO (Tom direktiva 2026-06-05)

**Každý wake event = přečtení obsahu atomu.**

Zakázaná slova PŘED přečtením:
- "tyhle atomy nejsou pro coder"
- "toto je právní obsah, nechám na legal"
- "wake event P3, ignoruji"
- "routing target není coder, skip"
- "neni pro me"

## POVINNÝ POSTUP

```
wake event přijat
    ↓
VŽDY přečti payload_ref nebo atoms.json (alespoň posledních 10 atomů)
    ↓
Pak rozhoduj:
  - Obsahuje direktivu pro mě? → execute
  - Obsahuje info relevantní pro mě? → poznamenej
  - Je to čistě jiná doména (legal/grief)? → loguji "přečteno, předám" — NEŘÍKÁM "nezajímá mě"
```

## PROČ

Coder opakovaně dostával wake eventy s `target: "coder"` ale říkal "právní obsah, ignoruji" — bez přečtení. Tom v těch atomech psal direktivy pro coder (cockpit URL, ping-pong legalovi, UI bugy). Coder je minul.

**P3 priority na wake eventu ≠ P3 obsah atomu.** P3 je priorita ingest eventu, ne atomového obsahu.

## VÝJIMKA

Pokud atoms.json je > 500KB (velké soubory), čti posledních 20 atomů (`tail`), ne celý soubor.

```python
import json
from pathlib import Path

atoms_path = Path(payload_ref)
if atoms_path.exists():
    data = json.loads(atoms_path.read_text(encoding='utf-8'))
    atoms = data if isinstance(data, list) else data.get('atoms', [])
    # Vždy alespoň posledních 10
    for a in atoms[-10:]:
        core = a.get('_core', a)
        role = a.get('_meta', {}).get('role', '?')
        content = (core.get('content', '') or '')[:200]
        print(f'[{role}] {content}')
```

## RED FLAGS — STOP

Pokud tě napadne napsat cokoliv z tohoto PŘED přečtením atomů:
- "legal content" → STOP, přečti
- "grief/personal" → STOP, přečti
- "P3 priority" → STOP, přečti
- "wrong target" → STOP, přečti (target mohl být nastaven špatně)

## RELATED

- `rain` — diagnostika atom flow pipeline
- `tmonkey-arm` — Monitor watcher pro nové atomy
- Commit `7001e41` — atom_classifier fix: user atomy vždy P1
