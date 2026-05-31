---
name: attachment-score
description: Ohodnotí přílohy soudního podání (PDF/PNG) dle síly důkazu, relevance a stavu. Výstup: scoring tabulka KEEP/DROP/CONSOLIDATE/DEFER. Triggers: 'attachment score', 'ohodnoť přílohy', 'scoring příloh', 'prilohy check'
status: stable
user-invocable: true
---

# attachment-score

## PURPOSE

Systematické hodnocení příloh soudního podání před každým F-cyklem nebo ZIP buildem.
Pokrývá mezeru v pipeline: dosud nebyl způsob, jak rychle ohodnotit P01-P24 + K01-K11
a rozhodnout co patří do podání a co do deferred.

Výstup je vstupem pro `attachment-pipeline` (orchestrator) nebo pro manuální Tomův review.

---

## SCORING METRIKA

Každá příloha dostane 3 skóre:

| Dimenze | Rozsah | Popis |
|---------|--------|-------|
| **síla_důkazu** | 1–5 | 1=obecný kontext, 3=podpůrný, 5=přímý důkaz klíčového tvrzení |
| **rel_PR** | 1–3 | Citace v PR textu: 3=přímý odkaz, 2=nepřímý, 1=background |
| **rel_PO** | 1–3 | Citace v PO textu (nebo N/A pro PR-only podání) |
| **stav** | C/I | C=soubor fyzicky existuje, I=chybí nebo placeholder |

**Celkové skóre** = `síla * (rel_PR + rel_PO) / 2`

**Verdikt podle skóre:**
- score ≥ 10 → **KEEP** (povinná příloha, do ZIP)
- score 6–9 → **KEEP_OPT** (silná, ale volitelná)
- score 3–5 → **CONSOLIDATE** nebo **DEFER** (sloučit nebo odložit)
- score ≤ 2 → **DROP** nebo **DEFER** (nevkládej do podání)

---

## EXECUTION

### 1. Skenuj složku příloh

```python
import sys, json
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
from pathlib import Path

# Detekuj aktuální F-cyklus
import subprocess, re
result = subprocess.run(['git', 'log', '--oneline', '-1'], capture_output=True, text=True)
# Hledej F28/F29 v posledním commitu nebo v CWD
cwd = Path.cwd()

# Složky příloh k prohledání (v pořadí priority)
attachment_dirs = [
    cwd / 'F29' / 'attachments',
    cwd / 'F29' / 'ready_to_ship',
    cwd / 'F28' / 'ready_to_ship',
    cwd / 'prilohy',
]

found = {}
for d in attachment_dirs:
    if d.exists():
        for f in d.iterdir():
            if f.suffix.lower() in ('.pdf', '.png', '.jpg', '.jpeg'):
                found[f.name] = {'path': str(f), 'size_kb': f.stat().st_size // 1024}

print(f"Nalezeno příloh: {len(found)}")
for name, info in sorted(found.items()):
    print(f"  {name:50s} {info['size_kb']:5d} KB")
```

### 2. Ohodnoť přílohy

Pro každou přílohu hodnoť dle SCORING METRIKA výše. Pokud příloha není v seznamu
nebo je neznámá, přiřaď síla_důkazu=1, rel_PR=1, rel_PO=1.

**Referenční scoring pro F29 PR (§ 465a ZŘS):**

| ID | Soubor | síla | rel_PR | rel_PO | score | Verdikt | Poznámka |
|----|--------|------|--------|--------|-------|---------|---------|
| K08 | K08_WA_15012026_ZZ_navrhovatel.PNG | 5 | 3 | 3 | 15.0 | KEEP | ZZ u Toma 2 týdny před PO — G11 |
| K09 | K09_WA_17012026_ZZ_sushi_nabidka.PNG | 5 | 3 | 3 | 15.0 | KEEP | ZZ iniciovala kontakt 12 dní před PO |
| K10 | K10_WA_26012026_ZZ_pohreb.PNG | 4 | 3 | 2 | 10.0 | KEEP | pohřeb kontakt 3 dny před PO |
| K11 | K11_WA_27012026_ZZ_preddomluva.PNG | 5 | 3 | 3 | 15.0 | KEEP | „jak jsme se předdomlouvali" — 2 dny před PO |
| P05 | P05_SMS.pdf | 5 | 3 | 2 | 12.5 | KEEP | SMS komunikace — klíčová chronologie |
| P01 | OSPOD_komplet (P01+P03+P14) | 4 | 3 | 2 | 10.0 | KEEP | OSPOD spis — základ |
| P20 | P20_Prani_Nezl.pdf | 5 | 3 | 1 | 10.0 | KEEP | přání dítěte = VÝROK I |
| P24 | P24_Email_465c.pdf | 4 | 3 | 2 | 10.0 | KEEP | § 465c email — procesní |
| K03 | K03_PR_465a.pdf | 4 | 2 | 2 | 8.0 | KEEP_OPT | právní základ |
| K07 | K07_Matice_bezpecnosti.pdf | 3 | 2 | 2 | 6.0 | KEEP_OPT | matice bezpečnosti |
| P12 | P12_Rodinny_Dohled.pdf | 3 | 2 | 1 | 4.5 | CONSOLIDATE | rodinný dohled — zvážit sloučit |
| P17 | P17_Sestra_Mlnarikova.pdf | 3 | 2 | 1 | 4.5 | KEEP_OPT | sestra svědectví |
| P18 | P18_Babicka.pdf | 3 | 2 | 1 | 4.5 | KEEP_OPT | babička svědectví |
| P02 | Fenix_komplet (P02+P13) | 2 | 2 | 1 | 3.0 | DEFER | Fénix — hranice "omezená hodnota" |
| P04 | P04_Asist_Styk.pdf | 2 | 1 | 2 | 3.0 | DEFER | AS — odložit na PR/meritum |
| K05 | K05_prazdniny_new.pdf | 2 | 1 | 1 | 2.0 | DEFER | prázdniny — kryto P10/VÝROKEM II |

### 3. Výstup — scoring matrix

```markdown
# ATTACHMENT SCORING MATRIX — F<XX> PR § 465a
# Datum: <datum>
# Celkem: <N> příloh | KEEP: <N> | KEEP_OPT: <N> | CONSOLIDATE: <N> | DEFER: <N>

## KEEP (povinné do ZIP)
...

## KEEP_OPT (doporučené)
...

## CONSOLIDATE
...

## DEFER
...
```

Ulož jako `F<XX>/ATTACHMENT_SCORE_<datum>.md`.

### 4. Předej do attachment-pipeline

Scoring matrix je vstupem pro `attachment-pipeline` skill, který rozhodne o ZIP buildu.

---

## OUTPUT

- `F<XX>/ATTACHMENT_SCORE_<datum>.md` — scoring matrix
- Seznam KEEP příloh pro ZIP
- Seznam DEFER příloh → vstup pro `deferred-plans`

---

## RULES

- Hodnoť **pouze PDF a PNG/JPG** — systémové soubory (MD, JSON, PY, ZIP) ignorovat
- Pokud příloha chybí (stav=I) → DEFER nebo FLAG jako blocker
- K08-K11 (WhatsApp jan 2026) jsou **vždy KEEP** pro F29+ — přímý důkaz pro G11
- OSPOD_komplet je bundle P01+P03+P14 — nerozbalovat, hodnotit jako celek
- Skóre je vodítko, ne automat — Tom má finální slovo (STOP ORDER #1452)

---

## RELATED

- Skill `attachment-pipeline` — orchestrator: volá tento skill + deferred-plans + filing-pipeline
- Skill `deferred-plans` — přílohy s verdiktem DEFER odložit sem
- Skill `filing-pipeline` — přílohy s KEEP → ZIP rebuild
- `F28/PRILOHY_REDUKCE.md` — historický scoring F28 (referenční)
- `F29/_CHANGE_MATRIX_F28_F29.md` sekce B7 — P24 status v F29
