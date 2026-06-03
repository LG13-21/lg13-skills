---
name: rain
description: Diagnóza + oprava toku atomů z TM ingesta do monitor-arm instancí. Triggery: 'rain', 'neteče', 'nepršelo', 'atomy netečou', 'atom flow', 'TM ingest', 'i-can-hear-u check'
status: stable
user-invocable: true
---

# rain — Atom Flow Diagnostics

## PURPOSE

Zkontroluje celý pipeline od TM ingesta až po probuzení monitor-arm instancí.
Najde kde se tok zastavil a pokusí se ho obnovit.

Pipeline: TMonkey → pl_server(8790) → parking_lot → atom_dispatcher → stacks → wake_signal → monitor-arm

---

## EXECUTION

Spusť kroky **v pořadí**. Každý krok reportuj jedním řádkem. Na konci shrnutí.

---

### KROK 1 — i-can-hear-u: listen_aggregator status

```python
import subprocess, json, sys
sys.path.insert(0, 'L:/GitHub/lg13-coder/agent/skills')
from db_query import db

# Zkontroluj daemon
r = subprocess.run(
    ['python', 'L:/LG13/app/agent/listen_aggregator.py', '--instance', 'coder', '--status'],
    capture_output=True, text=True, timeout=10
)
print(r.stdout.strip() or r.stderr.strip())
```

**Co hledat:** `daemon_running: true` + PID přítomen + `signal_events` roste.

Pokud `daemon_running: false` → spusť daemon:
```bash
python L:/LG13/app/agent/listen_aggregator.py --instance coder &
python L:/LG13/app/agent/listen_aggregator.py --instance strat &
python L:/LG13/app/agent/listen_aggregator.py --instance legal &
```

---

### KROK 2 — pl_server: je živý a přijímá atomy?

```bash
curl -s http://localhost:8790/pl/stats
```

**Co hledat:**
- HTTP 200 → pl_server běží
- `by_action_status.NEW` nebo `QUEUED` > 0 → atomy čekají na dispatch
- `by_action_status.DISPATCHED` roste → dispatch funguje

Pokud timeout/connection refused:
```bash
# Zkontroluj proces
python -c "
import subprocess
r = subprocess.run(['tasklist'], capture_output=True, text=True)
lines = [l for l in r.stdout.splitlines() if 'pl_server' in l.lower() or 'python' in l.lower()]
print('\n'.join(lines[:10]))
"
# Spusť pl_server pokud mrtvý:
# python L:/LG13/app/agent/pl_server.py &
```

---

### KROK 3 — parking_lot: zaseknuté atomy?

```python
import json
from pathlib import Path

pl = Path('L:/LG13/runtime/ops/parking_lot.json')
if not pl.exists():
    print('MISSING: parking_lot.json neexistuje')
else:
    data = json.loads(pl.read_text(encoding='utf-8'))
    items = data.get('items', [])
    from collections import Counter
    counts = Counter(i.get('action_status','?') for i in items)
    print(f'Celkem atomů: {len(items)}')
    for status, cnt in sorted(counts.items()):
        print(f'  {status}: {cnt}')
    # Ukáž nejstarší zaseknuté
    stuck = [i for i in items if i.get('action_status') in ('NEW','QUEUED','APPROVED')]
    if stuck:
        oldest = min(stuck, key=lambda x: x.get('created_at',''))
        print(f'Nejstarší stuck: {oldest.get("created_at")} — {oldest.get("content","")[:80]}')
```

**Co hledat:** APPROVED atomy bez posunu → atom_dispatcher neteče. NEW/QUEUED → dispatcher neapprove.

---

### KROK 4 — atom_dispatcher: běží a dispatche?

```python
import subprocess, sys
from pathlib import Path

# Kontrola procesu
r = subprocess.run(['tasklist', '/fi', 'imagename eq python.exe'], capture_output=True, text=True)
lines = r.stdout.lower()
print('atom_dispatcher v procesech:', 'atom_dispatcher' in lines)

# Poslední log
log = Path('L:/LG13/runtime/agent_ledger/atom_dispatcher.log')
if log.exists():
    lines_log = log.read_text(encoding='utf-8', errors='ignore').splitlines()
    print(f'Log ({len(lines_log)} řádků), posledních 10:')
    for l in lines_log[-10:]:
        print(' ', l)
else:
    print('LOG MISSING: atom_dispatcher.log nenalezen')
```

Pokud dispatcher neteče:
```bash
python L:/LG13/app/agent/atom_dispatcher.py &
# nebo
python L:/GitHub/lg13-coder/agent/atom_dispatcher.py &
```

---

### KROK 5 — instance stacks: dostávají atomy?

```python
from pathlib import Path
import os

stacks_dir = Path('L:/LG13/runtime/stacks')
if not stacks_dir.exists():
    print(f'MISSING: {stacks_dir}')
else:
    for f in sorted(stacks_dir.glob('*_stack.jsonl')):
        stat = f.stat()
        size = stat.st_size
        mtime = stat.st_mtime
        import time
        age_min = (time.time() - mtime) / 60
        lines = sum(1 for _ in f.open(encoding='utf-8', errors='ignore'))
        print(f'{f.name}: {lines} atomů, {size/1024:.0f}KB, poslední zápis {age_min:.0f} min zpět')
```

**Co hledat:** stacks by měly růst když TM posílá atomy. Pokud jsou prázdné nebo staré → dispatcher neposílá.

---

### KROK 6 — wake_signal: probouzí instance?

```python
from pathlib import Path
import time

wake_dir = Path('L:/LG13/runtime/ops/wake_signal')
if not wake_dir.exists():
    print(f'MISSING: {wake_dir}')
else:
    for f in sorted(wake_dir.glob('*.jsonl')):
        stat = f.stat()
        age_min = (time.time() - stat.st_mtime) / 60
        lines = sum(1 for _ in open(f, encoding='utf-8', errors='ignore'))
        flag = '⚠️ STALE' if age_min > 10 else '✅'
        print(f'{flag} {f.name}: {lines} events, {age_min:.0f} min starý')
```

**Co hledat:** wake_signal/*.jsonl by měly být čerstvé (< 2 min od posledního TM aktualizace). Pokud stale → listen_aggregator nepíše wake eventy.

---

### KROK 7 — TMonkey vstup: posílá vůbec soubory?

```python
from pathlib import Path
import time

tm_dir = Path('L:/LG13/runtime/ops/tmonkey')
if not tm_dir.exists():
    print(f'MISSING: {tm_dir}')
else:
    files = sorted(tm_dir.glob('*.json'), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        print('PRÁZDNO: žádné TM soubory — TM browser session neposílá atomy')
    else:
        for f in files[:5]:
            age_min = (time.time() - f.stat().st_mtime) / 60
            print(f'{f.name}: {age_min:.0f} min starý, {f.stat().st_size} B')
```

**Co hledat:** pokud adresář prázdný nebo soubory starší než 5 min → TM browser session není aktivní nebo TM script neteče.

---

### KROK 8 — SOUHRN + AKCE

Na konci vypiš:

```
=== RAIN REPORT ===
listen_aggregator: ✅/❌
pl_server:         ✅/❌ (N atomů waiting)
parking_lot:       ✅/❌ (NEW=X QUEUED=X APPROVED=X DISPATCHED=X)
atom_dispatcher:   ✅/❌
stacks:            ✅/❌ (coder=Nmin legal=Nmin strat=Nmin)
wake_signal:       ✅/❌ (coder=Nmin)
tm_input:          ✅/❌ (nejnovější soubor Nmin zpět)

BLOCKER: <kde se tok zastavil>
AKCE:    <co spustit/opravit>
```

---

## COMMON FIXES

| Symptom | Fix |
|---------|-----|
| listen_aggregator dead | `python L:/LG13/app/agent/listen_aggregator.py --instance coder` |
| pl_server nereaguje | `python L:/LG13/app/agent/pl_server.py` |
| atom_dispatcher mrtvý | `python L:/LG13/app/agent/atom_dispatcher.py` |
| parking_lot zaseknutý | zkontroluj `APPROVED` → dispatcher log; nebo `pipeline_watchdog.py` |
| TM nepíše soubory | TM browser session musí běžet; `/tmonkey-arm` pro monitor |
| wake_signal stale | listen_aggregator nečte stacks → restart aggregatoru |
| stacks prázdné | dispatcher nerouting → zkontroluj INSTANCE_KEYWORDS v dispatcher |

---

## RELATED

- `i-can-hear-u` (A1 krok v super-start) — daemon status
- `tmonkey-listen` — Monitor arm pro TM wake eventy
- `pipeline_watchdog.py` — auto-restart mrtvých daemonů
- `REFERENCE_RUNTIME.md` — runtime architektura

---

## NOTES

- TM ingest funguje jen pokud je aktivní browser session s ChatGPT (Windows)
- listen_aggregator musí běžet per-instance (coder/strat/legal samostatně)
- parking_lot lock: pokud pl_server i dispatcher čtou současně → race condition → restart obou
- wake_signal/*.jsonl: listen_aggregator PŘIDÁVÁ řádky, instance ČTE a posunuje kurzor
