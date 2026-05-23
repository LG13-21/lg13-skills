---
name: isds
description: >
  ISDS datová schránka — použij tento skill pokaždé, když má instance odeslat DS, zobrazit přijaté
  zprávy, hledat v přijatých nebo odeslaných DS, nebo stáhnout zprávy z datové schránky.
  Skill pokrývá: odeslání (--send), inbox (--inbox), odeslané (--sent), stažení zprávy (--download).
  VYŽADUJE token: uživatel musí uvést token, jinak skill zastav.
---

# ISDS Skill — Datová schránka

## KROK 0 — INSTANCE CHECK (vždy první, bez výjimky)

Tento skill smí volat **pouze t002 nebo legal**. Pokud jsi jiná instance (strat, coder, main, web, ...):

```
Tento skill je dostupný pouze pro instance t002 a legal.
Požádej t002 (odesílání/inbox) nebo legal (právní kontext) o provedení operace.
```

**Okamžitě zastav. Nevykonávej nic dalšího.**

---

## KROK 1 — AUTORIZACE (vždy druhý, bez výjimky)

**DŮLEŽITÉ (zjištěno 2026-05-20):** `isds_sender.py` má credentials uložené interně v configu — ISDS_TOKEN v env není nutný pro READ operace (inbox, sent, download). Token v env je jen skill-level guard pro SEND operace.

Pravidlo:
- **READ (--inbox, --sent, --download):** ISDS_TOKEN není nutný → spusť přímo
- **SEND (--send --confirm):** vyžaduje Tom explicitní souhlas + STOP ORDER check

```python
import os
token_set = bool(os.environ.get('ISDS_TOKEN', ''))
# READ = vždy OK; SEND = jen s tokenem a Tom GO
```

Token nastavuje Tom: `$env:ISDS_TOKEN = "..."` (PowerShell session) nebo trvale přes System Properties.

---

## SKRIPT + PYTHON

```
C:\Users\tom\AppData\Local\Programs\Python\Python312\python.exe
L:/LG13/app/agent/isds_sender.py [parametry]
```

---

## OPERACE 1 — ODESLAT DS

```python
import subprocess
py = r'C:\Users\tom\AppData\Local\Programs\Python\Python312\python.exe'
subprocess.run([py, 'L:/LG13/app/agent/isds_sender.py',
    '--send', '--confirm',
    '--to',      '<DS_ID>',
    '--subject', '<PŘEDMĚT>',
    '--body',    '<TEXT_NEBO_CESTA_K_SOUBORU>',
    '--attach',  '<PŘÍLOHA>',   # volitelné, opakuj pro více příloh
])
```

Volitelné: `--to-hands`, `--our-ref`, `--your-ref`.
Náhled bez odeslání: `--preview` místo `--send --confirm`.

**Po odeslání:** výstup obsahuje `dm_id`. Zaloguj do `comms_log.jsonl`.
**POZOR:** Platí 5 LOCKS + QUAD LOCK. Bez Tom schválení neposílat.

---

## OPERACE 2 — ZOBRAZIT INBOX (přijaté)

```python
subprocess.run([py, 'L:/LG13/app/agent/isds_sender.py',
    '--inbox',
    # '--from-date', '2026-05-01',  # volitelně od data
])
```

Výstup: seznam zpráv s dm_id, odesílatelem, předmětem, datem.

---

## OPERACE 3 — HLEDAT V PŘIJATÝCH

```python
r = subprocess.run([py, 'L:/LG13/app/agent/isds_sender.py', '--inbox'],
    capture_output=True, text=True, timeout=30)
keyword = "<HLEDANÝ_TEXT>"
for line in r.stdout.splitlines():
    if keyword.lower() in line.lower():
        print(line)
```

---

## OPERACE 4 — HLEDAT V ODESLANÝCH

Přes ISDS:
```python
r = subprocess.run([py, 'L:/LG13/app/agent/isds_sender.py', '--sent'],
    capture_output=True, text=True, timeout=30)
keyword = "<HLEDANÝ_TEXT>"
for line in r.stdout.splitlines():
    if keyword.lower() in line.lower():
        print(line)
```

Nebo přes lokální log (rychlejší):
```python
import json
from pathlib import Path
log = Path('L:/LG13/runtime/ops/comms_log.jsonl')
entries = [json.loads(l) for l in log.read_text(encoding='utf-8').splitlines() if l.strip()]
keyword = "<HLEDANÝ_TEXT>"
for e in entries:
    if keyword.lower() in json.dumps(e, ensure_ascii=False).lower():
        print(e['ts'], e.get('to_name',''), e.get('subject',''), e.get('dm_id',''))
```

---

## OPERACE 5 — STÁHNOUT ZPRÁVY (batch)

```python
import re, subprocess
py  = r'C:\Users\tom\AppData\Local\Programs\Python\Python312\python.exe'
save_base = 'L:/LG13/runtime/ops/ds_messages'

def download_last(mode, count):
    flag    = '--inbox' if mode == 'inbox' else '--sent'
    dl_flag = '--download' if mode == 'inbox' else '--download-sent'
    r = subprocess.run([py, 'L:/LG13/app/agent/isds_sender.py', flag],
        capture_output=True, text=True, timeout=30)
    ids = re.findall(r'\b(\d{8,12})\b', r.stdout)
    for dm_id in ids[:count]:
        subprocess.run([py, 'L:/LG13/app/agent/isds_sender.py',
            dl_flag, dm_id, '--save-to', f'{save_base}/{dm_id}'],
            capture_output=True, text=True, timeout=60)
        print(f"Staženo [{mode}] dm_id={dm_id}")

download_last('inbox', X)   # X = počet přijatých
download_last('sent',  Y)   # Y = počet odeslaných
```

---

## UMÍSTĚNÍ SOUBORŮ

| Soubor | Účel |
|--------|------|
| `L:/LG13/app/agent/isds_sender.py` | Hlavní script |
| `$env:ISDS_TOKEN` | Tajný token (env proměnná, zná jen Tom) |
| `L:/LG13/runtime/ops/comms_log.jsonl` | Log odeslaných zpráv |
| `L:/LG13/runtime/ops/ds_messages/<dm_id>/` | Stažené zprávy + přílohy |

---

## OPERACE 6 — EMAIL (souběžné odeslání emailem)

`isds_sender.py` neumí posílat emaily. Pro odeslání emailem:

### Rychlý draft (.eml soubor — Tom otevře a odešle)
```python
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path

msg = MIMEMultipart()
msg['From'] = 'tomas_kopecky@seznam.cz'
msg['To'] = '<email_adresata>'
msg['Subject'] = '<předmět>'
msg.attach(MIMEText('<text>', 'plain', 'utf-8'))
# Přílohy:
att = MIMEApplication(Path('<soubor.pdf>').read_bytes(), _subtype='pdf')
att.add_header('Content-Disposition', 'attachment', filename='soubor.pdf')
msg.attach(att)
Path('Inbox/draft.eml').write_bytes(msg.as_bytes())
# Tom otevře draft.eml v emailovém klientovi a odešle
```

### Automatické odeslání (vyžaduje SMTP heslo)
Pokud Tom dodá SMTP credentials → coder přidá `email_sender.py` do `L:/LG13/app/agent/`.

---

## POZNÁMKY

- **SSL:** `verify=False` v `isds_sender.py` (certifikát MojeDS neprojde lokálním CA).
- **READ operace:** fungují bez ISDS_TOKEN (credentials interně v configu).
- **Odesílání DS:** výhradně t002 s Tom schválením (5 LOCKS).
- **STOP ORDER #1452:** řízení Matoušek (0 P 29/2026) — odesílá VÝHRADNĚ Tom osobně.
- **Email odeslání:** právní má `.eml` draft workflow; pro plnou automatizaci potřeba coder + SMTP heslo.
