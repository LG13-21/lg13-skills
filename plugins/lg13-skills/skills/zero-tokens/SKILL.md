---
name: zero-tokens
description: "Zero-token execution stack: Python, Git, Ollama, context-mode. Kdy co použít, konkrétní snippety. Trigger: 'zero tokens', 'bez tokenů', 'python script', 'ollama query', 'git search', 'context-mode', 'ctx_', 'jak ušetřit tokeny'."
user-invocable: true
---

# Zero-Tokens — Execution Stack bez Claude tokenů

**Principy:** Claude = decision layer. Python/Git/Ollama/context-mode = execution layer. Deleguj cokoliv co jde mimo Claude.

---

## 1. PYTHON — local computation, free

### Kdy
- Zpracování dat (JSON, JSONL, CSV, log files)
- DB queries (MySQL přes `db_proxy.php`, SQLite lokálně)
- API calls (pl_server, queue, stack_reader)
- Jakákoliv opakující se operace

### Pattern
```python
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

# Číst JSONL atom stack
with open("L:/LG13/runtime/stacks/strat_stack.jsonl") as f:
    atoms = [json.loads(l) for l in f if l.strip()]

# Filtrovat, počítat, agregovat — BEZ Claude
new = [a for a in atoms if a.get('status') == 'new']
print(f"New atoms: {len(new)}")
for a in new[:5]:
    print(f"  [{a.get('priority','?')}] {a.get('subject','')[:80]}")
```

### LG13 skripty (token-free)
```bash
python L:/LG13/app/agent/stack_reader.py --instance strat --new --limit 50
python L:/LG13/app/agent/instance_queue.py --check --name strat
python L:/LG13/app/agent/skills/claude_usage_read.py --json
python L:/LG13/app/agent/atom_lookup.py --instance strat --since 2h --tz cest
curl -s http://localhost:8790/pl/stats
```

---

## 2. GIT — search, diff, history

### Kdy
- Hledat v historii tmonkey exportů (`L:/GitHub/lg13-runtime-state/`)
- Najít kdy byl soubor změněn
- Diff pro review bez načtení celého souboru

### Snippety
```bash
# Hledat text v git history (celé repo)
git -C L:/GitHub/lg13-runtime-state log --all -S "hledaný text" --oneline

# Grep přes všechny commity
git -C L:/GitHub/lg13-runtime-state grep "pattern" HEAD

# Historie konkrétního souboru
git -C L:/GitHub/lg13-runtime-state log --follow -p -- "path/to/file.txt"

# Najít soubory v repo podle patternu
git -C L:/GitHub/lg13-runtime-state ls-files "*chatgpt*"

# Diff posledního commitu (bez načítání)
git -C L:/GitHub/lg13-runtime-state diff HEAD~1 HEAD --stat
```

### LG13 tmonkey history search
```bash
# Hledat Tom prompt v atom historii (git-tmonkey-search skill)
git -C L:/GitHub/lg13-runtime-state grep -i "klíčové slovo" -- "inbox/chatgpt/*"
```

---

## 3. OLLAMA — local inference, free

### Kdy
- Klasifikace textu (priority, kategorie, routing)
- Sumarizace atomů (< 2K tokenů)
- CZ language tasks (gemma4:27b)
- Kódové drobnosti (devstral)
- Kdykoli Sonnet/Opus není nutný

### Snippety
```python
import requests, json

def ollama_ask(prompt: str, model: str = "gemma4:27b") -> str:
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": model, "prompt": prompt, "stream": False
    }, timeout=60)
    return r.json()["response"].strip()

# Klasifikace
result = ollama_ask("Je tato zpráva urgentní? Odpověz ANO/NE: " + atom_text, model="gemma4:27b")

# Sumarizace
summary = ollama_ask(f"Shrň v 3 větách: {text[:2000]}", model="devstral")
```

### Doporučené modely (L:/LG13/config/ registry)
| Model | Velikost | Use case |
|-------|----------|----------|
| `gemma4:27b` | 17GB | CZ text, baseline classify |
| `devstral` | 14GB | code, agentic, English |
| `gemma4:9b` | 6GB | rychlé klasifikace, low RAM |

---

## 4. CONTEXT-MODE MCP — search, batch, execute

### Kdy
- Output příkazu >20 řádků (ctx_batch_execute místo Bash)
- Opakovaný search ve stejné session
- Analýza velkých souborů (ctx_execute_file)
- Fetch webové stránky (ctx_fetch_and_index)

### Klíčové tools
```
ctx_batch_execute(commands, queries)   — PRIMARY research, indexuje output
ctx_search(queries, source)            — FTS5 search v indexu
ctx_execute(language, code)            — analýza kódu, data processing
ctx_execute_file(path, language, code) — analýza bez načtení do kontextu
ctx_fetch_and_index(url)               — místo WebFetch
ctx_stats()                            — kolik je toho v indexu
```

### Pattern: research bez floodingu kontextu
```
# ŠPATNĚ — flood kontext
Bash: cat L:/big_file.log    # 5000 řádků v kontextu

# SPRÁVNĚ — 0 řádků v kontextu
ctx_execute_file(
  path="L:/big_file.log",
  language="python",
  code="lines=[l for l in open(path) if 'ERROR' in l]; print(len(lines), lines[:5])"
)
```

### Pattern: batch research (jeden call místo 5)
```
ctx_batch_execute(
  commands=[
    {"label": "queue strat", "command": "python L:/LG13/app/agent/instance_queue.py --check --name strat"},
    {"label": "pl stats", "command": "curl -s http://localhost:8790/pl/stats"},
    {"label": "stack size", "command": "python -c \"import os; print(os.path.getsize('L:/LG13/runtime/stacks/strat_stack.jsonl'))\""}
  ],
  queries=["pending tasks", "atom count today"]
)
```

---

## 5. KOMBINACE — optimální stack

```
Tom otázka
  ↓
ctx_search("co jsem dělal") → memory check (0 tok)
  ↓
ctx_batch_execute([queue, stack, stats]) → batch init (0 tok)
  ↓
Python skript pro zpracování dat (0 tok)
  ↓
Ollama pro klasifikaci/sumarizaci (0 tok)
  ↓
Claude POUZE pro final rozhodnutí / komunikaci s Tomem
```

---

## ANTI-PATTERNS

| Špatně | Správně |
|--------|---------|
| `Bash cat big.log` → flood ctx | `ctx_execute_file` analýza |
| Claude čte 200 atomů | Python filtr → jen relevantní 5 atomů do Claude |
| Spawn Opus pro sumarizaci | Ollama gemma4:27b |
| `Bash grep -r` | Grep tool nebo ctx_search |
| WebFetch url | ctx_fetch_and_index url |
| `Bash ls dir/` | Glob pattern |
| Opakovaný Bash pro stejná data | ctx_batch_execute jednou, ctx_search pak |

---

## RELATED

- Skill `tool-picker` — hierarchie 1-7, decision tree
- Skill `rag-search` — RAG přes atom historii
- Skill `git-tmonkey-search` — git grep v tmonkey exportech
- Memory `feedback_no_bash_ls_for_search.md`
- Policy `L:/LG13/runtime/strategy/save_the_tokens_policy.md`

---

## FINAL

→ Python/Git/Ollama/ctx-mode first → Claude jen pro rozhodnutí a komunikaci
