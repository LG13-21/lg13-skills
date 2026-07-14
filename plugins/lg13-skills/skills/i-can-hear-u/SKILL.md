# I-Can-Hear-U — Full listening + monitoring startup

> **This skill should be used when** the user asks `/i-can-hear-u`, "spust listener", "poslouchej vsechny kanaly", "wake aggregator", "listen all".

Rozšířená verze (2026-07-12): daemon + wake_signal Monitor + CGE folder watch + CDC folder watch + issue-sync + Jarvis status report + Screenshots folder watch + new-research pipeline handoff.

---

## CO SKILL DELA (POVINNE PROVED VSE)

Má **8 kroků**, všechny povinné. Výsledek: instance slyší všechny kanály, vidí nové soubory v CGE/CDC/Screenshots, zná stav issues, a při novém materiálu ví spustit zpracovací pipeline (`listen-to-the-music`).

---

### Krok 1 — spust/over daemon (psani do <inst>.jsonl)

Auto-detect instance z cwd (lg13-coder → coder, legal-ship-2026 → legal, T000_Strat → strat).

```bash
python L:/LG13/app/agent/listen_aggregator.py --instance <inst>
```

`run_in_background: true`. Output: `[listen] start instance=<inst> sources=[pingpong, slack, tmonkey, github, plserver, queue, chatgpt, atoms]`.

Pokud uz bezi: `[listen] daemon already running pid=<N>` — OK, pokracuj.

---

### Krok 2 — arm Monitor watcher (wake_signal stream)

**Bez tohoto kroku jsem hluchy.** Daemon zapisuje do `wake_signal/<inst>.jsonl`, TATO session se neprobudi, dokud Monitor neposle notification.

```bash
tail -n 0 -F L:/LG13/runtime/ops/wake_signal/<inst>.jsonl 2>&1 | grep --line-buffered -E '"source"'
```

Monitor tool parametry:
- `persistent: true`
- `timeout_ms: 3600000`
- `description: "<inst> wake_signal stream (atoms/chatgpt/github/pingpong/queue/slack/tmonkey/plserver)"`

---

### Krok 3 — CGE folder monitor (ChatGPT Export)

Sleduj nové .json soubory v CGE (ChatGPT Export folder):

```python
import os, json, time
from pathlib import Path

CGE_DIR = Path("L:/GitHub/legal-ship-2026/ChatGPT_export/")
if CGE_DIR.exists():
    files = sorted(CGE_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    print(f"[i-can-hear-u] CGE: {len(list(CGE_DIR.glob('*.json')))} souborů, nejnovější: {files[0].name if files else 'none'}")
else:
    print("[i-can-hear-u] CGE folder nenalezen:", CGE_DIR)
```

Pro kontinuální monitoring nových souborů přidej do wake_signal Monitor grep:
```bash
# CGE nové soubory — použi PowerShell FileSystemWatcher v background scriptu
# nebo Listen aggregator plugin 'cge_watcher' (pokud existuje)
```

---

### Krok 4 — CDC folder monitor (Claude Desktop Conversations)

CDC = Claude Desktop Conversations export. Výchozí cesta (upravit dle prostředí):

```python
CDC_CANDIDATES = [
    Path("L:/LG13/inbox/claude_desktop/"),
    Path("C:/Users/tom/AppData/Roaming/Claude/conversations/"),
    Path("L:/LG13/inbox/cdc/"),
]
cdc_dir = next((p for p in CDC_CANDIDATES if p.exists()), None)
if cdc_dir:
    files = sorted(cdc_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    print(f"[i-can-hear-u] CDC: {cdc_dir}, nejnovější: {files[0].name if files else 'none'}")
else:
    print("[i-can-hear-u] CDC folder nenalezen — zkontroluj CDC_CANDIDATES")
```

---

### Krok 5 — issue-sync (GitHub delta)

```bash
python L:/LG13/app/agent/skills/issue_sync.py --repo LG13-21/legal-ship-2026
python L:/LG13/app/agent/skills/issue_read.py --instance <inst> --format markdown --update-anchor
```

→ nebo `/lg13-skills:issue-sync`

---

### Krok 6 — Jarvis status report (MySQL + web-up)

Auto-report stavu do Jarvis chat_messages tabulky (viditelné na luky.ai-domy.cz/jarvis/):

```python
import sys, time
from pathlib import Path
sys.path.insert(0, 'L:/GitHub/lg13-coder/agent/skills')
from db_query import db

ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
status_msg = f"[I-CAN-HEAR-U] {instance} listening — daemon+Monitor+CGE+CDC+issues armed @ {ts}"
db("INSERT INTO chat_messages (from_inst, to_inst, msg, channel) VALUES (%s,'all',%s,'jarvis')",
   params=[instance, status_msg])
print(f"[i-can-hear-u] Jarvis notified")
```

---

### Krok 7 — Screenshots folder monitor (prtsc)

Sleduj nové soubory v Screenshots složce. Při nových snímcích — spusť `/lg13-skills:prtsc` automaticky.

**Snapshot stavu (při startu):**

```python
from pathlib import Path
from datetime import datetime

PRTSC_DIR = Path(r"L:\OneDrive - Jihočeská univerzita v Českých Budějovicích\Pictures\Screenshots")
if PRTSC_DIR.exists():
    files = sorted(PRTSC_DIR.glob("*.png"), key=lambda f: f.stat().st_mtime, reverse=True)
    newest = files[0] if files else None
    ts = datetime.fromtimestamp(newest.stat().st_mtime).strftime('%Y-%m-%d %H:%M') if newest else 'none'
    print(f"[i-can-hear-u] PRTSC: {len(files)} souborů, nejnovější: {newest.name if newest else 'none'} ({ts})")
else:
    print("[i-can-hear-u] PRTSC folder nenalezen:", PRTSC_DIR)
```

**Kontinuální monitoring (PowerShell FileSystemWatcher v bg):**

```python
import subprocess, sys

PRTSC_PATH = r"L:\OneDrive - Jihočeská univerzita v Českých Budějovicích\Pictures\Screenshots"
prtsc_script = fr"""
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = '{PRTSC_PATH}'
$watcher.Filter = '*.png'
$watcher.EnableRaisingEvents = $true

Register-ObjectEvent $watcher Created -Action {{
    $name = $Event.SourceEventArgs.Name
    $ts = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ'
    Write-Output "PRTSC_NEW $name $ts"
}} | Out-Null

while ($true) {{ Start-Sleep -Seconds 5 }}
"""
subprocess.Popen(['powershell', '-NonInteractive', '-Command', prtsc_script],
                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print("[i-can-hear-u] PRTSC FileSystemWatcher spuštěn")
```

Po notification `PRTSC_NEW` → spusť `/lg13-skills:prtsc` pro OCR přečtení nového screenshotu.

---

### Krok 8 — nový materiál zjištěn → spusť `listen-to-the-music`

Pokud kroky 3/4 (CGE/CDC) nebo Monitor wake_signal odhalí **nový** soubor/vlákno (novější mtime než poslední známý stav) — nezastavuj se jen na "vidím nový soubor". Spusť `/lg13-skills:listen-to-the-music`, sekce **"PROCEDURE: New-Research Ingestion Pipeline"** — čtyřfázový postup (Čtení → Extrakce → Prioritizace → Aplikace → Polish), který se má spustit pokaždé, když dorazí nový výzkum/materiál na zpracování. Tento krok NEPROVÁDĚJ automaticky mlčky — oznam nález a poptej se, jestli má instance ten materiál rovnou zpracovat celým pipeline, nebo jen zaznamenat.

---

## RUNTIME PATH WARNING

> Zkontroluj pred spustenim: `ls L:/GitHub/legal-ship-2026/runtime/ops/wake_signal/` — pokud existuje, je to novy root a `L:/LG13/` je deprecated (governance #49).

---

## VERIFIKACE PO STARTU

```bash
# Daemon alive?
cat L:/LG13/runtime/ops/wake_signal/.daemon-<inst>.pid

# Nové eventy?
tail -10 L:/LG13/runtime/ops/wake_signal/<inst>.jsonl

# CGE nové soubory (posledních 24h)?
# PowerShell: Get-ChildItem L:/GitHub/legal-ship-2026/ChatGPT_export/ | Where-Object {$_.LastWriteTime -gt (Get-Date).AddHours(-24)}
```

---

## PLNA DOKUMENTACE

→ `skills/listen-to-the-music/SKILL.md` (architecture, source plugins, config).

## RELATED

- `/lg13-skills:sr` — volá tuto skill jako součást startup sekvence
- `/lg13-skills:issue-sync` — jen GitHub digest
- `/lg13-skills:listen-to-the-music` — Krok 8 na ni deleguje; obsahuje i "New-Research Ingestion Pipeline" (čtení→extrakce→prioritizace→aplikace→polish)
- Jarvis: luky.ai-domy.cz/jarvis/ — chat_messages tabulka
