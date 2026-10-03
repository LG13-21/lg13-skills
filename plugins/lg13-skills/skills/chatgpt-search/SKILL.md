---
name: chatgpt-search
description: "Vyhledá text nebo konverzaci v ChatGPT chatech OFFLINE v lokálním exportu (cgpt_find.py, wave search). Bez Edge/CDP. Trigger: 'hledej v chatgpt', 'najdi konverzaci kde jsem říkal', 'chatgpt search', 'kde jsem to říkal chatgpt', 'prohledej moje chaty'. Použij kdykoli Tom chce najít starší konverzaci nebo konkrétní obsah v ChatGPT historii."
user-invocable: true
---

# ChatGPT Search — vyhledávání v historii chatů

## PREREKVIZITY

Žádné. Skill je offline (lokální export). Dřívější Playwright/Edge hledání v sidebaru je ODSTRANĚNO (#770, žádný Edge/CDP).
Hledání dle titulu/obsahu: `python L:/LG13/app/agent/skills/cgpt_find.py "<dotaz>" [--content]` (skill `chatgpt-find`).

---

## EXECUTION

### Wave-filtrované lokální hledání (`--wave`)

Pro "co je nového k aktivní F-vlně" NEPOUŽÍVEJ browser search výše — použij lokální
skript, který prohledá `ChatGPT_export/` proti `L:/LG13/runtime/state/active_filing_wave.json`
(routing_table + keywords per F-číslo). Žádné CDP/Edge, žádné přihlášení, funguje offline.

```bash
python L:/LG13/app/agent/skills/chatgpt_wave_search.py --limit 10
python L:/LG13/app/agent/skills/chatgpt_wave_search.py --json --out L:/LG13/runtime/ops/wave_hits.json
```

Výstup: seznam vláken (`.json/.md/.txt` v ChatGPT_export) seřazený dle mtime, každé s `routed_to`
(nejlépe sedící aktivní F-číslo) a `keyword_hits`. Cache (`L:/LG13/runtime/state/.chatgpt_wave_search_cache.json`,
klíč název+mtime+size) dělá opakované běhy rychlé — první scan ~585 souborů trvá řádově minuty,
další jen sekundy pokud se soubory nezměnily. Pokud `active_filing_wave.json` neexistuje, skript
selže se srozumitelnou chybou (žádná tichá regrese/fallback na starý branding).

### Výběr a čtení konverzace

Po nalezení vlákna čti obsah přes `cge_legal_digest.py --conv-id <id>`.
Nebo `cge_legal_digest.py --conv-id <id>`; dotaz do vlákna přes `gpt-bridge`.

---

## PARAMETRY

| Vstup | Příklad | Co dělá |
|-------|---------|---------|
| `query=<text>` | `query=force read skill tipy` | Vyhledá v historii |
| `project=<P>` | `project=Coding` | Omezí na projekt |
| _(bez parametru)_ | — | Zeptá se co hledat |

---

## BEZ PARAMETRU — dotazník

```
1. "Co hledám v ChatGPT historii?"
2. "V jakém projektu? (Legal / Coding / LG13 / všechny)"
3. "Chceš jen najít URL, nebo rovnou načíst obsah?"
```

---

## NOTES

- Titul+obsah offline: `cgpt_find.py --content`. Starší/neingestované = zeptat se Toma, NIKDY neotevírat Edge.
- Výsledky jsou omezené na konverzace které ChatGPT indexoval (obvykle posledních ~6 měsíců).
