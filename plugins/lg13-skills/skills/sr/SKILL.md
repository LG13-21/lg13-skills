---
name: sr
description: >
  Kompletní session startup skill. Volej při: nové session, po /clear, po probuzení z idle,
  z launcheru. Provede: load-from-store → remember → i-can-hear-u → issue-sync →
  comm-legal (jen instance legal) → deep-read → ping-pong → brainstorming → writing-plans →
  executing-plans → vlastnak.
  Výsledek: fresh session, poslouchám všechny kanály, plán načten, vlastní goal definován.
---

# sr — Session Startup & Restart

**Launcher implicitně volá tuto skill jako první krok.**

Výsledek: fresh window, no old content — all in last position, ready to continue in online
comm listening team coop mode, continue work from last checkpoint.

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

### 1.5 — remember (načti handoff note)

Přečti `.remember/remember.md` z project root — obsahuje co bylo naposledy rozpracováno.

```bash
cat L:/GitHub/lg13-<inst>/.remember/remember.md 2>/dev/null || echo "(žádný handoff)"
```

→ nebo `/remember:remember`

---

### 2 — i-can-hear-u (daemon + Monitor watchers)

Spusť listen_aggregator daemon + arm Monitor pro wake_signal stream:

```bash
python L:/LG13/app/agent/listen_aggregator.py --instance <inst>
```
`run_in_background: true`.

Arm Monitor watcher:
```bash
tail -n 0 -F L:/LG13/runtime/ops/wake_signal/<inst>.jsonl 2>&1 | grep --line-buffered -E '"source"'
```
`persistent: true`, `timeout_ms: 3600000`.

**Navíc — folder monitors (nové soubory):**

CGE folder (ChatGPT export):
```bash
# Sleduj nové .json soubory v CGE
Get-ChildItem L:/GitHub/legal-ship-2026/ChatGPT_export/ -Filter "*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 3
```

CDC folder (Claude Desktop Conversations — path konfigurovatelný):
```bash
# Výchozí cesta: L:/LG13/inbox/claude_desktop/ — uprav dle prostředí
Get-ChildItem L:/LG13/inbox/claude_desktop/ -Filter "*.json" 2>/dev/null | Sort-Object LastWriteTime -Descending | Select-Object -First 3
```

→ nebo `/lg13-skills:i-can-hear-u`

---

### 3 — issue-sync (GitHub delta digest)

```bash
python L:/LG13/app/agent/skills/issue_sync.py --repo LG13-21/legal-ship-2026
python L:/LG13/app/agent/skills/issue_read.py --instance <inst> --format markdown --update-anchor
```

→ nebo `/lg13-skills:issue-sync`

---

### 3.5 — comm-legal (jen instance legal — ISDS + email dashboard)

Pokud `instance == "legal"`: spusť ISDS/email dashboard (scan nových dokumentů + OCR + evidence sync + dashboard).

```bash
/lg13-skills:comm-legal
```

Zajišťuje, že `Inbox/isds/isds_evidence.json` a MySQL `isds_podani` jsou na startu session aktuální — ne jen jednou za čas. Viz `comm-legal` skill sekci "PRŮBĚŽNÁ AKTUALIZACE" pro pravidlo, kdy skill spouštět i mimo `/sr`.

Pro ostatní instance (coder/strat) tento krok přeskoč.

---

### 4 — deep-read (nové kanály od cursoru)

```bash
python L:/GitHub/lg13-coder/agent/skills/deep_read.py --instance <inst> --limit 200
```

Výstup = checklist ✅/⬜/💎 + direktivy. Cursor se posune automaticky.

---

### 5 — ping-pong heartbeat + Jarvis status report

Pošli stratu heartbeat:
```bash
python L:/LG13/app/agent/instance_queue.py --send --to strat --from-inst <inst> \
  --msg "[HEARTBEAT] <inst> online — <co budu dělat>" --priority P2
```

Auto-report stavu do MySQL + Jarvis chat_messages:
```python
import sys, time
from pathlib import Path
sys.path.insert(0, 'L:/GitHub/lg13-coder/agent/skills')
from db_query import db

ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
status_msg = f"[SR] {instance} online @ {ts} — plan loaded, channels armed"

# Jarvis chat_messages
db("INSERT INTO chat_messages (from_inst, to_inst, msg, channel) VALUES (%s,'all',%s,'jarvis')",
   params=[instance, status_msg])
print(f"[sr] Jarvis notified: {status_msg}")
```

→ nebo `/lg13-skills:ping-pong`

---

### 6 — Queue check + claim

```bash
python L:/LG13/app/agent/instance_queue.py --check --name <inst>
python L:/LG13/app/agent/instance_queue.py --claim-next --name <inst>
```

---

### 7 — Autonomous planning mode

Po načtení plánu + kontextu spusť:

1. `/superpowers:brainstorming` — co je potřeba udělat? Priority?
2. `/superpowers:writing-plans` — napiš konkrétní plán kroků
3. `/superpowers:executing-plans` — prováděj krok po kroku
4. `/lg13-skills:vlastnak` — napiš vlastní session goal + ulož do clipboardu

Tato sekvence = autonomní pracovní mód. Nejen "co mám dělat?" ale "vím co dělám a dělám to."

---

## CHECKPOINT (průběžné ukládání)

Kdykoliv v průběhu session zavolej `/lg13-skills:checkpoint` — uloží snapshot stavu do MySQL + git + Jarvis + remember.md.

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
4. /lg13-skills:sr                ← launcher nebo ručně
```

## VARIANTA — bez /clear (refresh kanálů)

```
1. /lg13-skills:sr               ← rearm kanálů + reload plánu
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

- `/lg13-skills:checkpoint` — průběžný snapshot (save-to-store + remember + Jarvis)
- `/lg13-skills:super-start` — plný bootstrap (zahrnuje navíc fáze B/C/D/E/F)
- `/lg13-skills:save-min` — ulož před restartem
- `/lg13-skills:load-from-store` — jen načtení plánu
- `/lg13-skills:i-can-hear-u` — jen daemon + Monitor
- `/lg13-skills:issue-sync` — jen GitHub digest
- `/lg13-skills:comm-legal` — jen ISDS/email dashboard (legal instance)
- `/lg13-skills:deep-read` — jen nové kanály
- `/lg13-skills:ping-pong` — jen heartbeat
