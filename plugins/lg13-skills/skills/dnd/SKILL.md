---
name: dnd
description: Use when you need to focus without interruptions — suspends blocker questions for a set time, converts them to open_questions so work continues uninterrupted.
---

# dnd — Do Not Disturb

Nastaví DND mód: po dobu X minut neptat se Toma na blocker questions. Místo toho je zapsat do `open_questions` a pokračovat v práci. Po timeoutu nebo /undnd se seznam zobrazí.

## EXECUTION

### Aktivace

```python
import json, time
from pathlib import Path

mins = 30  # default, Tom může zadat jinak
state = {
    "active": True,
    "until_ts": time.time() + mins * 60,
    "until_str": time.strftime('%H:%M', time.localtime(time.time() + mins * 60)),
    "open_questions": [],
    "set_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
}
Path('L:/LG13/runtime/ops/dnd_state.json').write_text(
    json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"[dnd] DND aktivní do {state['until_str']}. Blocker otázky → open_questions.")
```

### Přidat open question (místo ptání Toma)

```python
import json, time
from pathlib import Path

p = Path('L:/LG13/runtime/ops/dnd_state.json')
if p.exists():
    state = json.loads(p.read_text('utf-8'))
    if state.get('active') and time.time() < state.get('until_ts', 0):
        state['open_questions'].append({
            "ts": time.strftime('%H:%M', time.localtime()),
            "q": "<blocker otázka>",
            "context": "<co jsem dělal>",
        })
        p.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
        print("[dnd] Otázka přidána do open_questions.")
```

### Kontrola + zobrazení po timeoutu (`/undnd`)

```python
import json, time
from pathlib import Path

p = Path('L:/LG13/runtime/ops/dnd_state.json')
if p.exists():
    state = json.loads(p.read_text('utf-8'))
    qs = state.get('open_questions', [])
    print(f"[dnd] Nahromaděné otázky ({len(qs)}):")
    for q in qs:
        print(f"  {q['ts']} — {q['q']}")
    state['active'] = False
    p.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
```

## PARAMETRY

```
/lg13-skills:dnd          # 30 min (default)
/lg13-skills:dnd 60       # 60 minut
/undnd                     # zrušit DND + zobrazit accumulated Q
```

## PRAVIDLA

- DND = jen pro non-critical otázky (STOP ORDER, P0 blocker stále reportovat!)
- Open question = "Mám X problém, neblokuje mě teď, zeptám se až Tom bude v dosahu"
- Po expiraci timeoutu: zobraz všechny open questions + deaktivuj DND
- statusline_notify.json: zapsat `dnd: true` + `until` pro zobrazení ve statusline

## RELATED

- `L:/LG13/runtime/ops/dnd_state.json` — stav DND
- Skill `vlastnak` — nastavit goal (doplňkové)
- Skill `statusline` — DND status v panelu
