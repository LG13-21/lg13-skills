---
name: cti-cele
description: "Přečte celý long soubor (ChatGPT export, JSON, TXT, MD) v iteracích a extrahuje diamonds/legal facts/CHANGE_MATRIX candidates. Triggers: '/cti-cele', 'přečti celé', 'přečti celý export', 'celý long message', 'need u to read this', 'i need u to read', 'přečti to celé', 'přečti celý soubor', 'cti-cele'"
status: stable
user-invocable: true
---

# /cti-cele — Čtení celého long souboru

## ÚČEL

Přečte velký soubor (ChatGPT export, právní vlákno, TXT) v iteracích po blocích
a extrahuje strukturovaný přehled:

- **Diamonds** (silné argumenty, insighty, klíčové formulace) — scored 1–10
- **Legal facts** (datumy, jména, § citace, důkazy, fakta)
- **CHANGE_MATRIX candidates** — konkrétní návrhy úprav do F-cyklu
- **Citace** — doslova citovatelné věty

**Problém který řeší:** Tom pošle ChatGPT vlákno o 162 zprávách. Claude přečte
headline a dělá summaries ze summarií. Tento skill zajistí čtení CELÉHO obsahu
bez výjimky.

---

## ARGUMENTY

```
/cti-cele <cesta>              — přečte jeden soubor
/cti-cele <cesta1> <cesta2>   — více souborů postupně
/cti-cele <cesta> --focus legal  — filtruje jen právní obsah
/cti-cele <cesta> --output <out.md>  — uloží report do souboru
```

Pokud cesta není zadána: použij poslední soubor z `ChatGPT_export/` nebo se zeptej.

---

## EXECUTION

### Krok 1 — detect a načti

```python
import json, re
from pathlib import Path

path = Path(ARGS)  # z argumentu
ext = path.suffix.lower()

# JSON export (ChatGPT format)
if ext == ".json":
    data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    # ChatGPT export: list of messages or mapping
    if isinstance(data, dict) and "mapping" in data:
        messages = [
            v["message"]["content"]["parts"][0]
            for v in data["mapping"].values()
            if v.get("message") and v["message"].get("content")
            and v["message"]["content"].get("parts")
            and isinstance(v["message"]["content"]["parts"][0], str)
        ]
    elif isinstance(data, list):
        messages = [m.get("content", "") for m in data if isinstance(m.get("content"), str)]
    else:
        messages = [str(data)]
    text = "\n\n---\n\n".join(messages)
else:
    text = path.read_text(encoding="utf-8", errors="ignore")
```

### Krok 2 — chunk iterace

Rozdělí na bloky ~4000 znaků (s překrytím 200 znaků pro kontext).
Pro každý blok extrahuj:

```
DIAMONDS — právní insighty, silné argumenty, reusable patterns
  Format: [score 1-10] text | zdroj
  Hledej: neobvyklé insighty, silná formulace, opakující se vzory

LEGAL FACTS
  Format: [TYP] hodnota (TYP: DATUM|JMÉNO|§|DŮKAZ|FAKT)
  Hledej: konkrétní datumy, jména, § citace, čísla, fakta

CHANGE_MATRIX — kandidáti na úpravu podání
  Format: [PRIORITA] co → kam (PRIORITA: P0|P1|P2)
  Hledej: návrhy změn, nové argumenty, formulace k přebrání

CITACE — přímé citace vhodné do podání
  Format: "text citace" (kontext)
```

### Krok 3 — aggregate a output

Po přečtení všech bloků:
1. Dedupuj diamonds (stejný insight z více bloků = 1 entry, vyšší score)
2. Seřaď diamonds dle score (desc)
3. Napiš report do `F29/analysis_cdc/auto/cti_cele_<filename>_<TS>.md`
4. Prezentuj Tomovi TOP 10 diamonds + count per kategorie

---

## IMPLEMENTACE PŘES CTX_EXECUTE_FILE

Použij `mcp__plugin_context-mode_context-mode__ctx_execute_file` pro zpracování:

```python
# V ctx_execute_file kódu:
CHUNK_SIZE = 4000
OVERLAP = 200

chunks = []
for i in range(0, len(text), CHUNK_SIZE - OVERLAP):
    chunks.append(text[i:i+CHUNK_SIZE])

print(f"Soubor: {len(text)} znaků → {len(chunks)} bloků")
print(f"Typ: {'JSON' if ext == '.json' else 'TEXT'}")
print("\n--- FIRST 3 CHUNKS PREVIEW ---")
for i, chunk in enumerate(chunks[:3]):
    print(f"\n[CHUNK {i+1}/{len(chunks)}]")
    print(chunk[:500])
```

Pak pro každý chunk Claude (tento model) sám extrahuje diamonds — neposílej na API,
zpracuj lokálně v kontextu.

---

## VÝSTUPNÍ FORMÁT

```markdown
# /cti-cele: <filename>
*<N> znaků, <M> bloků, přečteno <TS>*

## TOP DIAMONDS

| # | Score | Diamond | Zdroj blok |
|---|-------|---------|-----------|
| 1 | 9/10  | text insightu | blok 4 |
| 2 | 8/10  | ... | blok 12 |

## LEGAL FACTS

- **DATUM** 29.1.2026 — incident v bytě ZZ
- **§** § 909 OZ — návrh na změnu péče
- ...

## CHANGE_MATRIX CANDIDATES

| Priorita | Co | Kam v F29 |
|----------|-----|-----------|
| P0 | text návrhu | § 3 odůvodnění |

## PŘÍMÉ CITACE

> "přesná citace pro podání"  *(kontext: blok 7)*

## STATS

- Přečteno: N znaků, M bloků
- Diamonds: X (P0: Y, P1: Z)
- Legal facts: N
- Zpráv (JSON): M
```

---

## RULES

- **NIKDY nečti jen headline** — každý blok musí být reálně zpracován
- Pro právní vlákna: hledej i emoční obsah — Tom tam občas schová právní fakt
- Po dokončení: uložit report, pak prezentovat summary
- Pokud soubor > 500KB: varuj uživatele + opt-in (bude trvat ~5 minut)
- JSON ChatGPT export s prázdnými `content`: oznámit, přeskočit prázdné zprávy
- STOP #1452: výsledky pouze zaznamenat, neaplikovat bez Tom GO

---

## TRIGGER PŘÍKLADY

```
/cti-cele L:\GitHub\legal-ship-2026\ChatGPT_export\google4.txt
/cti-cele ChatGPT_export\ChatGPT-Strach\ z\ návratu\ tátovství.md
/cti-cele F28/_deep_read_full_legal_20260530T045829.txt --focus legal
```

---

## RELATED

- `deep-read-full` — čtení přes LG13 queue (pro zprávy v pipeline)
- `diamond-sentry` — autonomní diamond extraction organism (batch scan)
- `diamond-pick` — single-shot extraction z jednoho souboru
- `/cti-cele` vs `deep-read-full`: tato skill = lokální soubory; deep-read = queue msgs
