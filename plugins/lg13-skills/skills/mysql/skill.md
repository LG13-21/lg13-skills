---
name: mysql
description: MySQL dotaz přes luky.ai-domy.cz/api/db_proxy.php. Trigger: "/mysql q: SELECT ...", "/mysql q: path/to/query.sql", "spusť SQL", "dotaz do DB", "co je v tabulce X", "mysql select", "mysql insert", "ukaž tabulky". Podporuje inline SQL nebo cestu k .sql souboru. Bezpečný — blokuje DROP DATABASE, DROP TABLE, TRUNCATE.
version: 1.1.0
---

# mysql — MySQL dotaz přes db_proxy

## SPUŠTĚNÍ

```
/mysql q: SHOW TABLES
/mysql q: SELECT * FROM avengers_tasks

# Nebo přes skill_io (request/response JSON + denní log):
python skill_io.py --run mysql "SELECT * FROM work_items"
python skill_io.py --log-tail 10
/mysql q: SELECT * FROM work_items WHERE status='OPEN'
/mysql q: DESCRIBE avengers_tasks
/mysql q: ../scripts/sql_q_select_legal.sql
/mysql q: INSERT INTO parking_lot (item, prio) VALUES ('fix X', 50)
```

## IMPLEMENTACE

```python
import sys, re
from pathlib import Path

sys.path.insert(0, 'L:/GitHub/lg13-coder/agent/skills')
from db_query import db, print_table

raw = """<USER_ARGS>"""
m = re.match(r'q:\s*(.+)', raw.strip(), re.DOTALL | re.IGNORECASE)
if not m:
    print("Použití: /mysql q: SELECT ... nebo /mysql q: path/to/query.sql")
    sys.exit(1)

query_arg = m.group(1).strip()

if query_arg.endswith('.sql') and Path(query_arg).exists():
    sql = Path(query_arg).read_text(encoding='utf-8').strip()
    print(f"[mysql] Spouštím soubor: {query_arg}")
else:
    sql = query_arg

print(f"[mysql] SQL: {sql[:120]}{'...' if len(sql)>120 else ''}")
result = db(sql)

if not result.get('ok'):
    print(f"ERROR: {result.get('error')} — {result.get('msg','')}")
    sys.exit(1)

rows = result.get('rows') or []
if rows:
    print_table(rows)
    print(f"\n({len(rows)} řádků)")
else:
    print(f"OK — rowcount={result.get('rowcount',0)}" +
          (f", insert_id={result.get('insert_id')}" if result.get('insert_id') else ""))
```

## KONFIGURACE A CREDENTIALS

Proxy URL a API key jsou hardcoded v `agent/skills/db_query.py`:

```python
DB_PROXY_URL = "https://luky.ai-domy.cz/api/db_proxy.php"
API_KEY      = "074a31ade09eb1348298daf5cb720d9e5854de0e98e15426ba85e1de478bf12b"  # telemetry_key
```

DB secrets (jen pro referenci): `L:/LG13/runtime/secrets/db_secrets.json`
- Host: `a068um.forpsi.com` | DB/User: `f198638` | Pass: viz secrets

**DŮLEŽITÉ:** Přímé připojení k MySQL přes Python není možné — server povoluje přístup jen z vlastní IP (PHP server). Vždy použij `db_proxy.php` jako prostředníka.

Pokud db_proxy selže s `db_connect_failed`:
1. Zkontrolovat `/subdoms/luky/config.php` na serveru (FTP)
2. Porovnat s `L:/LG13/runtime/secrets/db_secrets.json`
3. Případně nahrát nový config přes `/ftp upload`

## TABULKY V DB (aktuální stav 2026-05-26)

| Tabulka | Popis |
|---------|-------|
| `avengers_missions` | Avengers mise |
| `avengers_tasks` | Avengers tasky |
| `chat_messages` | Chat zprávy |
| `document_states` | Stav dokumentů |
| `jarvis_events` | JARVIS eventy |
| `pingpong_log` | Ping-pong log |
| `session_budget` | Session budget |
| `skills` | Skills registry |

## BEZPEČNOST

Proxy blokuje: `DROP DATABASE`, `DROP TABLE`, `TRUNCATE`. Ostatní DML (INSERT, UPDATE, DELETE) povoleno.
