---
name: deep-read-full
description: Spustí deep_read --full-read pro aktuální instanci. Čte plný text nových zpráv od cursoru (ne jen Haiku-filtered diamonds). Triggers: 'deep-read-full', 'precti vsechny zpravy', 'full read', 'chci videt cely obsah'
status: stable
user-invocable: true
---

# deep-read-full — Plné čtení zpráv pro alive instance

## PURPOSE

Spustí `deep_read.py --full-read` pro aktuální instanci.
Čte **plný text** nových zpráv od cursoru — ne jen Haiku-filtered diamonds.

Použij kdykoli instance musí přečíst celý obsah označených zpráv:
- právní vlákna označená Tomem v JSON select
- manuálně označené zprávy kde headline nestačí
- kdykoli Tom říká "přečti celé" nebo "nečteš celé"

Problém který řeší: Legal dostane deep_read report s headline "emocionální thread o Lukáškovi... obsahuje velmi užitečné věci pro právní podání" — a pak si nechá udělat condensed report a přečte jen první větu. Tato skill zajistí přečtení CELÉHO textu.

---

## EXECUTION

```python
from pathlib import Path
import subprocess, sys

# Auto-detect instance z cwd
cwd = Path.cwd()
instance_map = {
    'lg13-coder': 'coder',
    'legal-ship-2026': 'legal',
    'T000_Strat': 'strat',
    'lg13-strat': 'strat',
}
instance = next((v for k, v in instance_map.items() if k in str(cwd)), 'coder')

dr = Path('L:/GitHub/lg13-coder/agent/skills/deep_read.py')
if not dr.exists():
    dr = Path('L:/LG13/app/agent/skills/deep_read.py')

print(f'[deep-read-full] instance={instance}, spouštím --full-read...')
subprocess.run([sys.executable, str(dr), '--instance', instance, '--full-read'], check=False)
```

---

## OUTPUT

Plný text nových zpráv od cursoru:
```
[001] 🟡 ✅ REL  | 2026-05-28 | tom          | Emocionální podpora Lukášek [2✍]
··················································
[FULL] 2026-05-28 | chatgpt | tom
<celý text zprávy>
··················································
```

---

## RULES

- Cursor se posune stejně jako v normálním deep_read modu
- Po přečtení full textu instance MUSÍ extrahovat relevantní body do diary / tasků
- Nestačí přečíst jen headline — condensed report NESMÍ být jediný input
- Pro právní vlákna: vždy --full-read, nikdy jen summary

---

## RELATED

- `deep_read.py --full-read` — implementace (commit 2c95069)
- `session_manager.py` — ALIVE_MODE=1 spouští deep-read-full automaticky při init
- skill `deep-read` — normální mód (jen diamonds)
