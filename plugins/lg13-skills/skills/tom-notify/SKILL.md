---
name: tom-notify
description: This skill should be used when any instance needs to notify Tom urgently, send him a question, escalate a blocker, request a review, or wake him up. Use for "notify Tom", "send urgent", "BLOCKER escalate", "wake Tom", "ask Tom", "/tom-notify". Also describes the GDRV/IFTTT filesystem notification protocol for all instances.
version: 1.0.0
---

# tom-notify — GDRV/IFTTT Human Notification Protocol

## PURPOSE

Google Drive folder (`G:\IFTTT\inbox\`) = filesystem message queue.
Jakýkoliv **nový soubor** → IFTTT trigger → okamžitá push notification na Tomův iPhone (title souboru = zpráva).

**CREATE = notify. MODIFY = silent.**

Jedna instance dopíše do existujícího threadu — bez dalšího spam notification.

---

## CESTY

```
G:\IFTTT\           = Google Drive sync (L:\GitHub\G_drw\IFTTT\)
  inbox\            ← SEM PSÁT nové zprávy (trigger notification)
  active\           ← přesunout pokud Tom reagoval, řešíme
  resolved\         ← hotové (TTL 7 dní → archive)
  archive\          ← starší resolved
  urgent\           ← BLOCKER/URGENT (přímý trigger, vždy inbox)
```

Fallback path pokud G: nedostupný: `L:\GitHub\G_drw\IFTTT\inbox\`

---

## NAMING POLICY

```
{PREFIX}_{TOPIC}_{YYYYMMDD-HHMM}.txt
```

### Priority prefixes

| Prefix | Kdy použít |
|--------|-----------|
| `INFO_` | FYI, žádná akce |
| `TASK_` | Tom musí něco udělat |
| `REVIEW_` | potřebuje zhlédnout/schválit |
| `URGENT_` | blokuje práci, čeká se |
| `BLOCKER_` | kritický stopper, přeruš vše |

### Příklady

```
URGENT_LOCK2_VISUAL_CHECK_20260523-1930.txt
BLOCKER_ISDS_CREDENTIALS_NEEDED_20260523-2100.txt
TASK_REVIEW_VDR_F19_20260523-1800.txt
INFO_SKILLS_REGISTRY_DONE_20260523-1920.txt
```

---

## EXECUTION

### 1. Zkontroluj existující thread (anti-spam)

Před vytvořením nového souboru zkontroluj `inbox/` a `active/`:

```python
from pathlib import Path
import os

INBOX = Path("G:/IFTTT/inbox")  # nebo L:/GitHub/G_drw/IFTTT/inbox
if not INBOX.exists():
    INBOX = Path("L:/GitHub/G_drw/IFTTT/inbox")

# Existuje thread ke stejnému tématu?
existing = list(INBOX.glob(f"*{topic_keyword}*.txt"))
```

- Pokud **existuje** → dopis do existujícího souboru (bez nové notifikace)
- Pokud **neexistuje** → vytvoř nový soubor (trigger notification)

### 2. Vytvoř nový soubor (nová notifikace)

```python
import time
from pathlib import Path

INBOX = Path("G:/IFTTT/inbox")
if not INBOX.exists():
    INBOX = Path("L:/GitHub/G_drw/IFTTT/inbox")
INBOX.mkdir(parents=True, exist_ok=True)

ts = time.strftime("%Y%m%d-%H%M")
prefix = "URGENT"   # INFO / TASK / REVIEW / URGENT / BLOCKER
topic = "LOCK2_CHECK"
fname = f"{prefix}_{topic}_{ts}.txt"

content = f"""[STATUS] OPEN
[OWNER] coder
[CREATED] {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
[INSTANCE] coder

---

{message_body}

---
[REPLIES]
"""
(INBOX / fname).write_text(content, encoding="utf-8")
print(f"NOTIFY sent: {fname}")
```

### 3. Dopis do existujícího threadu

```python
import time

thread_file = existing[0]  # nejnovější matching soubor
with open(thread_file, "a", encoding="utf-8") as f:
    f.write(f"\n[UPDATE {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] [coder]\n{message}\n")
print(f"Appended to: {thread_file.name}")
```

### 4. Po vyřízení → přesunout

```python
import shutil
resolved_dir = thread_file.parent.parent / "resolved"
resolved_dir.mkdir(exist_ok=True)
shutil.move(str(thread_file), str(resolved_dir / thread_file.name))
```

---

## FILE FORMAT (standard)

```
[STATUS] OPEN | ACTIVE | WAITING | BLOCKED | RESOLVED
[OWNER] coder | legal | strat | human | gpt
[CREATED] 2026-05-23T19:30:00Z
[INSTANCE] coder

---

<zpráva / dotaz / blocker popis>

---
[REPLIES]
<Tom nebo jiná instance dopisuje sem>
```

---

## ANTI-SPAM PRAVIDLA

1. **Jedno téma = jeden soubor** — dopisuj, nevytvárej nový
2. **CREATE = notify, MODIFY = silent** — IFTTT trigger jen na nový soubor
3. **Max 1 soubor na urgentní téma za 30 min** — pokud Tom nereagoval, počkej
4. **INFO_ a TASK_** — nevytvářej více než 3 najednou
5. **BLOCKER_** — smí kdykoliv, žádný limit

---

## TTL POLICY

| Stav | Akce |
|------|------|
| OPEN > 24h bez odpovědi | přidej `[REMINDER]` řádek (bez nového souboru) |
| RESOLVED | přesunout do `resolved/` |
| resolved/ > 7 dní | přesunout do `archive/` |

---

## SCÉNÁŘE

### Urgentní dotaz Tomovi
```python
prefix = "URGENT"
topic = "LOCK2_VISUAL_CHECK"
body = "Potřebuji vizuální potvrzení PDF balíku. Je v staging: L:/LG13/runtime/ops/filing_16_4_output/"
```

### Blocker — čekám na credentials
```python
prefix = "BLOCKER"
topic = "ISDS_TOKEN_NEEDED"
body = "ISDS upload blokován — chybí token. Prosím dodej nebo potvrď platnost."
```

### Informace / FYI
```python
prefix = "INFO"
topic = "SKILLS_REGISTRY_COMMITTED"
body = "skill_registry.db (48 skills) commitnuto do lg13-skills. Žádná akce potřeba."
```

---

## KDY POUŽÍT GDRV vs. NTFY vs. PING-PONG

| Kanál | Kdy |
|-------|-----|
| **GDRV/IFTTT** | Urgentní zpráva Tomovi, blocker, review request |
| **ntfy.sh** | Programatická push notifikace (priority 5=urgent), bez souboru |
| **ping-pong** | Inter-instance dialog (coder↔strat↔legal), NE pro Toma |
| **GitHub issue** | Canonical state, hlasování, rozhodnutí |

GDRV = nejlepší pro **human-in-the-loop interrupts** kde Tom potřebuje otevřít soubor nebo odpovědět.

---

## NTFY RYCHLÝ FALLBACK

Pokud GDRV není dostupný (G: offline):

```python
import sys, subprocess
subprocess.run([sys.executable,
    "L:/LG13/app/agent/ntfy_push.py",
    "--title", f"[{prefix}] {topic}",
    "--message", body,
    "--priority", "5"  # urgent
])
```

---

## RELATED

- `ntfy_push.py` — `ntfy.sh/tomkopecky-lg13`, priority 1-5
- `G:\IFTTT\` = Google Drive sync folder (L:\GitHub\G_drw\IFTTT\)
- Skill `ping-pong` — inter-instance (NE pro Toma)
- Issue #50 — pipeline notifications reference
