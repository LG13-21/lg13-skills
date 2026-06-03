# tmonkey-bot — TMonkey channel reader + command sender

> Use when: "tmonkey", "co přišlo z chatgpt", "pošli příkaz do chatgpt", "tmonkey bot", "tmonkey status"

## CO SKILL DĚLÁ

Dva režimy:
1. **read** — přečte nejnovější ingestované zprávy z ChatGPT (přes JSONL inbox)
2. **send** — pošle příkaz do ChatGPT přes executor endpoint (`/pl/chatgpt/commands`)

---

## KROK 1 — Zkontroluj pl_server

```python
import urllib.request, json
try:
    r = urllib.request.urlopen('http://127.0.0.1:8790/pl/chatgpt/ingest/health', timeout=2)
    print('OK:', r.read())
except Exception as e:
    print('pl_server DOWN — spusť: python L:/LG13/app/agent/pl_server.py')
    # bez pl_server nelze ani číst ani posílat
```

---

## KROK 2a — READ: nejnovější zprávy z inboxu

```python
import glob, os, json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

INBOX = Path(r"L:\LG13\inbox\chatgpt\json")

# Najdi nejnovější JSONL soubory
all_jsonl = sorted(INBOX.rglob("*.jsonl"), key=os.path.getmtime, reverse=True)
recent = all_jsonl[:3]  # top 3 konverzace

for jf in recent:
    lines = jf.read_text(encoding='utf-8', errors='replace').splitlines()
    msgs = []
    for ln in lines:
        try:
            msgs.append(json.loads(ln))
        except Exception:
            pass
    print(f"\n=== {jf.name} ({len(msgs)} zpráv) ===")
    for m in msgs[-10:]:  # posledních 10 zpráv
        role = m.get('role', '?')
        text = str(m.get('text', m.get('content', '')))[:300]
        ts = m.get('ts', m.get('created_at', ''))[:16]
        print(f"[{ts}] {role}: {text}")
```

---

## KROK 2b — SEND: příkaz do ChatGPT

```python
import urllib.request, json, time

CMD_URL = 'http://127.0.0.1:8790/pl/chatgpt/commands'

def send_cmd(text: str, conv_id: str = None, priority: int = 5):
    payload = json.dumps({
        "cmd": text,
        "conv_id": conv_id or "",
        "priority": priority,
        "source": "coder",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }).encode('utf-8')
    req = urllib.request.Request(CMD_URL, data=payload,
                                  headers={"Content-Type": "application/json"},
                                  method="POST")
    try:
        r = urllib.request.urlopen(req, timeout=5)
        print("Odesláno:", r.read().decode())
    except Exception as e:
        print("Chyba:", e)

# Příklad: pošli příkaz
send_cmd("Shrň poslední odpověď do 3 bodů.")
```

---

## KROK 3 — Bot watcher (arm Monitor)

Pro kontinuální sledování nových zpráv — arm Monitor na JSONL inbox:

```bash
# Sleduje nové soubory v JSONL inbox
python L:/LG13/app/agent/tmonkey_bot_watcher.py --instance coder
```

Nebo ručně:
```bash
# Windows: watch pro nové soubory
powershell -Command "& {while($true){Get-ChildItem 'L:\LG13\inbox\chatgpt\json' -Recurse -Filter '*.jsonl' | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | ForEach-Object {Write-Output ('NEW: ' + $_.FullName)}; Start-Sleep 10}}"
```

---

## PARAMETRY (při invokaci)

| Parametr | Default | Příklad |
|----------|---------|---------|
| `read` | — | přečíst nové zprávy |
| `send <text>` | — | poslat příkaz |
| `status` | — | jen zkontroluj pl_server |
| `watch` | — | arm watcher daemon |
| `n=<N>` | 10 | počet zpráv |

---

## RULES

- **NIKDY** neposílej přes executor citlivá data (ISDS, hesla, osobní info)
- Executor posílá přes DOM injection — co pošleš, ChatGPT to uvidí
- pl_server musí běžet na :8790 (zkontroluj před send)

---

## RELATED

- `L:/LG13/app/agent/pl_server.py` — server s `/pl/chatgpt/*` endpointy
- `L:/LG13/inbox/chatgpt/json/` — JSONL inbox
- `L:/LG13/app/agent/tmonkey_bot_watcher.py` — bot daemon (viz níže)
- Skill `chatgpt-send` — starší alias pro send
- Skill `chatgpt-force-read` — force read celé konverzace
