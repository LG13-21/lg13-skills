---
name: chatgpt-find
description: "Vyhledá vlákna v ChatGPT historii OFFLINE nad ChatGPT_export/*.json (titul, URL, conv_id, volitelně i obsah zpráv). Bez Edge, bez CDP, bez přihlášení. Podporuje wildcard (*), JSON output, filtr projektu. Trigger: 'chatgpt-find', 'najdi v chatgpt vlakna kde', 'chatgpt find ping-pong', 'hledej chatgpt *', 'seznam vlaken v projektu'."
user-invocable: true
---

# ChatGPT Find — offline thread search

Prohledá exportovaná vlákna (TM/Exporter → `L:/GitHub/legal-ship-2026/ChatGPT_export/*.json`). Žádný prohlížeč, žádný Edge, žádný restart čehokoliv (#770). Pokrytí = co už je exportované; čerstvé vlákno se objeví po TM exportu (wake_signal `chatgpt`).

**Skript:** `L:/LG13/app/agent/skills/cgpt_find.py`

## PARAMETRY

| Parametr | Příklad | Popis |
|----------|---------|-------|
| `query` | `ping-pong` | Hledá v titulu. `*` = všechna vlákna. Wildcardy `*`, `?` |
| `--content` | | Hledá i v textu zpráv (pomalejší) |
| `--project <slug>` | `--project coding` | Slug projektu z odkazu vlákna (coding / legal / lg13 ...) |
| `--limit N` | `--limit 20` | Max výsledků (default 15) |
| `--json` | | JSON výstup |
| `--out <path>` | | Uloží JSON do souboru |

```bash
python L:/LG13/app/agent/skills/cgpt_find.py "ping*pong" --json
python L:/LG13/app/agent/skills/cgpt_find.py "matousek" --content --limit 10
python L:/LG13/app/agent/skills/cgpt_find.py "*" --project legal --limit 10
```

Výstup: `[conv_id8] titul (updated)`; JSON navíc `url`, `file`, `snippet`. Duplicitní re-exporty téhož `conv_id` se slučují (vyhrává nejnovější).

## NÁSLEDNĚ

- Číst obsah: `cge_legal_digest.py --conv-id <conv_id> --range increment` nebo `/lg13-skills:atom-search`.
- Zeptat se vlákna: skill `gpt-bridge` (claude-in-chrome, nikdy Edge).
- Wave-filtr pro aktivní F-vlnu: `python L:/LG13/app/agent/skills/chatgpt_wave_search.py --limit 10` (viz `chatgpt-search`).

## RELATED

- `gpt-bridge` — odeslání dotazu do vlákna
- `chatgpt-search` — wave search + git-tmonkey-search
- `git-tmonkey-search` — full-text ingestovaných vláken přes git
