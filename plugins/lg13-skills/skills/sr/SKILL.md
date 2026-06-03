---
name: sr
description: >
  Kompletní session startup skill. Volej při: nové session, po /clear, po probuzení z idle,
  z launcheru. Provede: load-from-store → i-can-hear-u → issue-sync → deep-read → ping-pong.
  Alias pro super-restart s plným startup flow. Superpowers: brainstorming, writing-plans,
  executing-plans (on-demand dle tasku).
---

# sr — Session Startup & Restart

**Launcher implicitně volá tuto skill jako první krok.**

Zahrnuje všechny kanály + kontext načtení. Není jen alias — je self-contained startup protokol.

---

## EXECUTION (v pořadí)

### 1 — load-from-store (načti předchozí plán)

```python
import sys
from pathlib import Path
sys.path.insert(0, 'L:/GitHub/lg13-coder/agent/skills')
from db_query import db

cwd = Path.cwd()
inst_map = {'lg13-coder': 'coder', 'lg13-strat': 'strat',
            'legal-ship-2026': 'legal', 'tmonkey': 'tmonkey'}
instance = next((v for k, v in inst_map.items() if k in str(cwd)), 'coder')

r = db("SELECT plan_text, saved_at FROM instance_plans WHERE instance=%s", params=[instance])
if r.get('ok') and r.get('rows'):
    row = r['rows'][0]
    print(f"=== PLAN z MySQL ({row[1]}) ===\n{row[0]}")
else:
    pf = Path(f"L:/GitHub/lg13-{instance}/plans/{instance}_current.md")
    print(pf.read_text(encoding='utf-8') if pf.exists() else "[load-from-store] Žádný plán.")
```

→ nebo `/lg13-skills:load-from-store`

---

### 2 — i-can-hear-u (daemon + Monitor watcher)

```bash
python L:/LG13/app/agent/listen_aggregator.py --instance <inst> --status
# daemon_running: false → spusť:
python L:/LG13/app/agent/listen_aggregator.py --instance <inst>
```
`run_in_background: true`.

Pak arm Monitor:
```bash
tail -n 0 -F L:/LG13/runtime/ops/wake_signal/<inst>.jsonl 2>&1 | grep --line-buffered -E '"source"'
```
`persistent: true`, `timeout_ms: 3600000`.
Sources: chatgpt / github / pingpong / queue / slack / tmonkey / plserver / **atoms**

→ nebo `/lg13-skills:i-can-hear-u`

---

### 3 — issue-sync (GitHub delta digest)

```bash
python L:/LG13/app/agent/skills/issue_sync.py --repo LG13-21/legal-ship-2026
python L:/LG13/app/agent/skills/issue_read.py --instance <inst> --format markdown --update-anchor
```

→ nebo `/lg13-skills:issue-sync`

---

### 4 — deep-read (nové kanály od cursoru)

```bash
python L:/GitHub/lg13-coder/agent/skills/deep_read.py --instance <inst> --limit 200
```

Výstup = checklist ✅/⬜/💎 + direktivy. Cursor se posune automaticky.

---

### 5 — ping-pong heartbeat

Pošli stratu heartbeat:
```bash
python L:/LG13/app/agent/instance_queue.py --send --to strat --from-inst <inst> \
  --msg "[HEARTBEAT] <inst> online — <co budu dělat>" --priority P2
```

→ nebo `/lg13-skills:ping-pong`

---

### 6 — Queue check + claim

```bash
python L:/LG13/app/agent/instance_queue.py --check --name <inst>
python L:/LG13/app/agent/instance_queue.py --claim-next --name <inst>
```

---

## SUPERPOWERS (on-demand dle tasku)

| Task | Skill |
|------|-------|
| Nová funkce / nápad | `/superpowers:brainstorming` |
| Mám spec, plánuji | `/superpowers:writing-plans` |
| Mám plán, implementuji | `/superpowers:executing-plans` |
| Bug / neočekávané chování | `/superpowers:systematic-debugging` |
| PR review | `/superpowers:requesting-code-review` |

---

## VARIANTA — s /clear (plný restart)

```
1. /lg13-skills:save-min         ← ulož stav
2. /clear                         ← Tom zadá ručně
3. — nová session —
4. /lg13-skills:sr                ← launcher nebo ručně (load-from-store + restart)
```

## VARIANTA — bez /clear (refresh)

```
1. /lg13-skills:save-min
2. /lg13-skills:sr               ← rearm kanálů + reload plánu
```

---

## KDY POUŽÍT

- Start nové session (launcher volá automaticky)
- Po pádu daemona (listen_aggregator)
- Po /compact nebo přechodu na novou session
- Při "Coder je hluchý" problému
- Jako /restart alias

---

## RELATED

- `/lg13-skills:super-start` — plný bootstrap (zahrnuje navíc fáze B/C/D/E/F)
- `/lg13-skills:save-min` — ulož před restartem
- `/lg13-skills:load-from-store` — jen načtení plánu
- `/lg13-skills:i-can-hear-u` — jen daemon + Monitor
- `/lg13-skills:issue-sync` — jen GitHub digest
- `/lg13-skills:deep-read` — jen nové kanály
- `/lg13-skills:ping-pong` — jen heartbeat
