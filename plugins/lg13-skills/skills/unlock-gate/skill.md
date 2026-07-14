---
name: unlock-gate
description: >
  Multi-step unlock workflow pro soudní podání F-cyklus.
  Spustí automated checks (LOCK 1–4) pro jeden soubor,
  vygeneruje unlock certifikát nebo fix list.
  Tom visual check = LOCK LAST (nikdy ne LOCK 1).
  Proklik na analýzu vždy přiložen k výsledku.

  VŽDY použij tento skill, když uživatel zmíní:
  unlock, lock gate, unlock cert, run checks, fix list, change matrix,
  unlock-gate, zamky F38, lock status file, F38 certifikat.
---

# unlock-gate — Automated LOCK check s certifikátem

## POŘADÍ LOCKŮ (direktiva Toma 2026-06-10)

```
LOCK 1: Formální check (run_checks.py / scripty — 0 tokenů)
LOCK 2: Strat + ChatGPT review (GO_SHIP / CONDITIONAL_GO)
LOCK 3: Total analysis (total-analysis-all-in-one)
LOCK 4: TIME — web up + visual OCR screenshot
LOCK LAST (5): TOM VIZUÁLNÍ CHECK — vždy poslední, nikdy LOCK 1
→ T002: odeslání (po KONEC STOP)
```

**Tom visual check NIKDY není LOCK 1 — je LOCK LAST.** Automated checks jdou první.

---

## SPUŠTĚNÍ

```
/unlock-gate [fcycle=F38] [lock=1|2|3|4|last] [doc=<path>] [file=<id>]
```

Parametry:
- `fcycle` — F-cyklus (default: auto-detect z CWD)
- `lock` — číslo LOCK nebo `last` pro Tom visual; default = nejnižší nesplněný
- `doc` — cesta k dokumentu; default = auto-detect prvního PDF v F<N>/
- `file` — ID souboru v change matrix (např. A2, B3)

---

## EXECUTION

### LOCK 1 — Formální check

```python
import subprocess, json
from pathlib import Path

# Auto-detect F-cyklus
fcycle = "F38"  # nebo z parametru
doc = next(Path(f"L:/GitHub/legal-ship-2026/{fcycle}").glob("*.pdf"), None)

result = subprocess.run(
    ["python", "L:/LG13/app/agent/skills/filing_pipeline.py", "full",
     "--file", str(doc), "--json"],
    capture_output=True, text=True
)
data = json.loads(result.stdout) if result.stdout else {}
critical = data.get("critical", [])
warnings = data.get("warnings", [])

print(f"LOCK 1: {len(critical)} CRITICAL, {len(warnings)} WARNING")
if critical:
    print("BLOCKED — fix list:")
    for c in critical:
        print(f"  - {c}")
```

Výstup: `PASS` (0 CRITICAL) nebo `fix_list` se seznamem problémů.

### LOCK 2 — Strat + ChatGPT

Spusť:
```
/lg13-skills:tmonkey       ← ChatGPT review (GO_SHIP / CONDITIONAL_GO / NO_GO)
```

Pokud `CONDITIONAL_GO`:
- Seber podmínky jako fix list
- Implementuj → nová verze souboru (F38.X+1)
- Rerun LOCK 2

### LOCK 3 — Total analysis

```
/total-analysis-all-in-one doc=<path>
```

Výstup: analýza + unlock verdict. **Odkaz na výstup zapiš do lock tabulky** (viz Proklik pravidlo níže).

### LOCK 4 — TIME: web up + OCR

```bash
# Web rebuild
python L:/LG13/app/agent/skills/web_up.py --fcycle F38

# Visual OCR check
/lg13-skills:prtsc          ← screenshot PDF výstupu, vizuální kontrola
```

Kritérium: PDF OK, web live, vizuální check PASS.

### LOCK LAST (5) — Tom vizuální check

**Teprve po LOCK 1–4 PASS.**

1. Připrav PDF pro Toma (nejčistší verze)
2. Odešli přes ping-pong: "F38.X připraveno k vizuálnímu checku — LOCK LAST"
3. Čekej na Tomovo "OK" / "KONEC STOP"

---

## FIX LIST → CHANGE MATRIX WORKFLOW

Pokud některý LOCK vrátí `fix_list`:

```
1. Seber fix listy ze všech LOCKů pro soubor
2. Slouč do change matrix (viz níže)
3. Nechej si na change matrix udělat solo analýzu
4. Implementuj změny → nová verze souboru (F38.X)
5. Zkontroluj: lze předchozí PASS locky zachovat, nebo musí být obnoveny?
6. Rerun LOCKů od nejnižšího zasaženého
7. Opakuj dokud LOCK LAST PASS
```

### Change matrix formát

```markdown
# CHANGE MATRIX — <fcycle> <soubor_id> — verze <X> → <X+1>

| # | Typ | Popis změny | Zdroj (LOCK N) | Analýza | Status |
|---|-----|-------------|----------------|---------|--------|
| 1 | FIX | ... | LOCK 1 | [analýza](path/to/analysis.md) | ☐ |
| 2 | FIX | ... | LOCK 3 | [total-analysis](path/to/ta.md) | ☐ |
```

---

## PROKLIK PRAVIDLO (direktiva Toma 2026-06-10)

**Pokud existuje analýza pro odemknutí zámku, MUSÍ být v lock tabulce proklik.**

Formát v tabulce:
```
| LOCK 3 | ☑ PASS | [total-analysis 2026-06-10](F38/analysis_cdc/ta_20260610.md) |
| LOCK 3 | ☐ FIX  | [fix list](F38/CHANGE_MATRIX_v1_v2.md) |
```

Nikdy nezanech lock řádek bez odkazu pokud analýza existuje.

---

## HISTORICKÉ VERZE V TABULCE (direktiva Toma 2026-06-10)

Lock tabulka musí obsahovat sloupec s verzemi:

```markdown
| Soubor | Aktuální | Verze | LOCK 1 | LOCK 2 | LOCK 3 | LOCK 4 | LOCK LAST |
|--------|----------|-------|--------|--------|--------|--------|-----------|
| 04_navrh_vyjadreni_F38 | [F38.3](path) | [F38.1](p) [F38.2](p) [F38.3](p) | ✅ | ✅ | ☐ | ☐ | ☐ |
```

- **Aktuální** = nejnovější verze s proklikem
- **Verze** = seznam historických verzí s proklikem na každou

---

## VERZOVÁNÍ SOUBORŮ

```
F38.0  → výchozí (žádný lock)
F38.1  → LOCK 1 PASS
F38.2  → LOCK 2 PASS
F38.3  → LOCK 3 PASS
F38.4  → LOCK 4 PASS (TIME)
F38.5  → LOCK LAST PASS (Tom)
F38    → finální odesílaná verze (bez sub-verze v názvu)
```

Různé soubory mohou mít různé aktuální sub-verze (A = F38.3, B = F38.9) — to je OK.

---

## UNLOCK CERTIFIKÁT

Výstup do `F<N>/UNLOCK_CERT_LOCK<N>_<TS>.md`:

```markdown
# UNLOCK CERTIFIKÁT — LOCK <N> — <fcycle>
**Datum:** <YYYY-MM-DD HH:MM UTC>
**Dokument:** <filename> (<verze>)
**Instance:** <legal|strat|coder|time>

## Výsledek kontrol
- LOCK 1 Formální: PASS ✅ / BLOCKED ❌ (<N> CRITICAL)
- LOCK 2 ChatGPT: GO_SHIP ✅ / CONDITIONAL_GO ⚠️ / NO_GO ❌
- LOCK 3 Total analysis: PASS ✅ / FAIL ❌ → [analýza](path)
- LOCK 4 TIME+OCR: PASS ✅ / FAIL ❌

## Verdict
UNLOCK ✅ / BLOCKED ❌

## Podmínky (pokud CONDITIONAL_GO)
- [ ] Podmínka 1
- [ ] Podmínka 2

## Podpis
Certifikát vydán instancí <instance> dne <datum>.
**STOP ORDER #1452 zůstává aktivní — certifikát není GO pro odeslání.**
```

---

## HARD RULES

1. **Tom visual check = LOCK LAST** — nikdy LOCK 1, vždy až po automated checks
2. **Proklik povinný** — každý splněný/nesplněný lock s analýzou má mít odkaz
3. **Historické verze** — tabulka zobrazuje aktuální i historické verze souboru
4. **Fix list → change matrix** — nesloučené fix listy nejsou vstupem pro implementaci
5. **Solo analýza na change matrix** před implementací
6. **Ověř předchozí locky** po každé nové verzi souboru
7. **STOP ORDER #1452** — certifikát není GO pro odeslání; jen Tom "KONEC STOP"

---

## RELATED

- Skill `locks-workflow` — 5-locks systém (pořadí LEGAL→STRAT→CHATGPT→TIME→TOM→T002)
- Skill `total-analysis-all-in-one` — pokrývá velkou část LOCK 3 požadavků
- Skill `pipeline` — run_checks.py pro LOCK 1
- Skill `attachment-pipeline` — orchestrator příloh
- `F38/UNLOCK_GATE_SKILL_PROMPT.md` — originální spec (9. 6. 2026)
- `F38/PLAN_F38_FINALIZE.md` — aktuální stav F38
- MySQL `ship_discipline` — lock status sync
