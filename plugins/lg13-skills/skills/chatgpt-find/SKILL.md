---
name: chatgpt-find
description: "Vyhledá vlákna v ChatGPT historii přes CDP + Playwright search form. Vrátí seznam threadů s tituly, URL a snippet textem viditelným v search okně. Podporuje wildcard (*), JSON output, filtr projektu. Trigger: 'chatgpt-find', 'najdi v chatgpt vlakna kde', 'chatgpt find ping-pong', 'hledej chatgpt *', 'seznam vlaken v projektu'."
user-invocable: true
---

# ChatGPT Find — thread search přes CDP

## PURPOSE

Prohledá ChatGPT historii vláknem — vloží dotaz do search form, scrape výsledky (tituly + URL + snippet), volitelně filtruje dle projektu. Výsledky vrátí jako text nebo JSON.

**Skript:** `L:/LG13/app/agent/skills/cgpt_find.py`

---

## PARAMETRY

| Parametr | Příklad | Popis |
|----------|---------|-------|
| `query=<text>` | `query=ping-pong` | Hledaný text. `*` = všechna vlákna (sidebar scrape). |
| `project=<P>` | `project=Coding` | Omezí na projekt v sidebaru (Legal / Coding / LG13 / ...) |
| `--limit N` | `--limit 20` | Max výsledků (default 15) |
| `--json` | | JSON výstup na stdout |
| `--out <path>` | `--out L:/LG13/runtime/ops/find.json` | Uloží výsledky do souboru |

### Wildcard

| Pattern | Chování |
|---------|---------|
| `ping-pong` | exact/substring search |
| `ping*pong` | regex contains ping...pong |
| `*goal*` | obsahuje "goal" |
| `*` | všechna vlákna (sidebar, žádný search form) |

---

## EXECUTION

```bash
# Základní search
python L:/LG13/app/agent/skills/cgpt_find.py "ping-pong"

# Wildcard
python L:/LG13/app/agent/skills/cgpt_find.py "ping*pong" --json

# Projekt filter
python L:/LG13/app/agent/skills/cgpt_find.py "ecosystem goals" --project Coding --limit 20

# Všechna vlákna v projektu
python L:/LG13/app/agent/skills/cgpt_find.py "*" --project Legal --limit 10

# Ulož výsledky
python L:/LG13/app/agent/skills/cgpt_find.py "matousek" --out L:/LG13/runtime/ops/find_matousek.json --json
```

---

## OUTPUT FORMAT

```
=== ChatGPT Find: 'ping-pong' (project=all) ===
Found: 3 threads

 1. [6a06b4b5] Legal Strict Sequential Review
     └ ping-pong protokol, inter-instance...
 2. [6a078d80] Ecosystem Goals multi-agent
     └ strat goals framework ping pong...
 3. [abc12345] LG13 cowork ping pong design
```

JSON (`--json`):
```json
{
  "query": "ping-pong",
  "project": null,
  "count": 3,
  "ts": "2026-05-15T21:50:00Z",
  "results": [
    {"title": "...", "url": "https://chatgpt.com/c/...", "snippet": "...", "source": "search"}
  ]
}
```

---

## WORKFLOW S FORCE-READ

```
chatgpt-find query=<text>
    ↓
výsledky → seznam URL
    ↓
chatgpt-force-read url=<URL>   (nebo loop přes všechny)
    ↓
TM ingest → atom → stack → LG13
```

---

## CDP AUTOFIX

Skript automaticky restartuje Edge pokud CDP port 9222 nereaguje.

---

## PREREKVIZITY

- Edge otevřený, přihlášen na chatgpt.com
- `playwright` nainstalován: `pip install playwright`
- CDP port 9222: Edge spuštěn s `--remote-debugging-port=9222`

---

## NOTES

- ChatGPT search hledá v názvech + obsahu konverzací (limitováno indexem ChatGPT, ~6 měsíců)
- Snippety zobrazují text viditelný v search dropdown — závisí na ChatGPT UI verzi
- Pro full-text search starší historie → git-tmonkey-search skill (ingestovaná vlákna v gitu)
- Výsledky se liší dle aktivního projektu v sidebaru — proto `--project` flag

## RELATED

- `chatgpt-force-read` — po nalezení URL: TM ingest obsahu
- `chatgpt-search` — starší skill (bez CDP, bez snippetů) — deprecated, prefer chatgpt-find
- `git-tmonkey-search` — full-text search ingestovaných vláknen (offline, přes git)
