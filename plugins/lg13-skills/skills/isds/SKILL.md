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

Uživatel musí uvést token v promptu (např. "token: xyz" nebo "--token xyz").
Porovnej ho s `$env:ISDS_TOKEN`:

```python
import os, sys
provided = "<TOKEN_KTERÝ_UVEDL_UŽIVATEL>"   # extrahuj z promptu
stored   = os.environ.get('ISDS_TOKEN', '')
if not provided or provided != stored:
    print("CHYBA: Nesprávný nebo chybějící token. ISDS skill zastaven.")
    sys.exit(1)
```

**Pokud token chybí nebo nesouhlasí → okamžitě zastav. Nevykonávej nic dalšího.**
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

## POZNÁMKY

- **SSL:** `verify=False` v `isds_sender.py` (certifikát MojeDS neprojde lokálním CA).
- **Odesílání:** výhradně t002 s Tom schválením (5 LOCKS).
- **STOP ORDER #1452:** řízení Matoušek (0 P 29/2026) — odesílá VÝHRADNĚ Tom osobně.
