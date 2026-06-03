---
name: diamond-sentry
description: "Autonomní diamond extraction — projde soubory/issues/chaty, detekuje compressed insights, reusable patterns, operational breakthroughs. Ne keyword search, ale emergence detection. Trigger: 'spusť sentry', 'diamond scan', 'najdi diamondy v X', '/diamond-sentry'."
user-invocable: true
---

# Diamond Sentry — Autonomní diamond extraction organism

## CONCEPT

Ne grep. Ne indexer. Ale persistent semi-autonomous reviewer.

Hledá: unusually strong structures, compressed insight, reusable patterns, operational breakthroughs.
**Nepředpokládá, co hledá** — hledá emergence.

## QUICK RUN

```bash
python L:/GitHub/lg13-coder/agent/skills/diamond_sentry.py --target <cesta> --output L:/LG13/runtime/diamonds/
```

### Příklady

```bash
# Scan ChatGPT exportů
python L:/GitHub/lg13-coder/agent/skills/diamond_sentry.py --target L:/GitHub/legal-ship-2026/ChatGPT_export/

# Scan issues + MD soubory
python L:/GitHub/lg13-coder/agent/skills/diamond_sentry.py --target L:/GitHub/legal-ship-2026/ --types md,json

# Full scan všech repo
python L:/GitHub/lg13-coder/agent/skills/diamond_sentry.py --target L:/GitHub/ --recursive --limit 500
```

## PIPELINE (5 stages)

1. **Scan** — projde soubory (MD, JSON, txt, PDF OCR), extrahuje text chunks
2. **Cluster** — seskupí podobné insighty (recurring patterns, repeated abstractions)
3. **Compress** — vytvoří canonical form z clusteru (místo 14 diskuzí → 1 doctrine)
4. **Score** — diamond density: reusability × compression × recurrence × operational impact
5. **Export** → `diamonds.json`, `doctrines.md`, `unresolved_diamonds.md`

## CO JE DIAMOND (vysoké score)

- Pipeline abstraction (jeden pattern vysvětluje celý systém)
- Reusable review loop / lock-release orchestration
- Lex atomic mechanism, slim judge framing
- Operational heuristics (funguje cross-context)
- Recurring patterns rediscovered 3+ krát

## CO NENÍ DIAMOND (nízké score)

- Běžná diskuze, emoční opakování, noise
- One-off rozhodnutí bez přenositelnosti

## OUTPUT FILES

| Soubor | Obsah |
|--------|-------|
| `diamonds.json` | Extrahované diamondy s metadata (score, source, ts) |
| `doctrines.md` | Canonical form — operational doctrines |
| `unresolved_diamonds.md` | Partial diamonds čekající na kompozici |
| `skills.json` | Kandidáti na nové skills |

## RELATED

- `diamond-pick` — Lex Atomic extraction z jednoho souboru (single-shot)
- `atom-search` — search v existující atom databázi
- `deep-read` — čte issues + ChatGPT export po kurzorovém posunu
