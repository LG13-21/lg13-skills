---
name: consistency-check
description: Use when a legal filing document may have stale dates, wrong day counts, or paragraph inconsistencies before render or ship. Triggers: 'consistency check', 'zkontroluj konzistenci', 'datum check', 'dnu check', 'před renderem', 'before ship check'
status: stable
user-invocable: true
---

# consistency-check

## PURPOSE

Automatický konzistentní check právního MD dokumentu před renderem nebo podáním.
Zachytí triviální chyby, které způsobují restart 20+ hodinového cyklu.

**Baseline evidence (TDD RED — LOCK 1 audit F29 31.5.2026):**
- Datum v hlavičce: "30. 5. 2026" ale dnes 31.5. → stale o 1 den
- "121 dní" v textu ale 29.1.→31.5. = 122 dní
- "137 dní od tragické smrti" ale 13.1.→31.5. = 138 dní
- Tyto chyby prošly celým F-cyklem a zachytil je až LOCK 1

---

## EXECUTION

### 1. Detekuj referenční datum

```python
import re
from pathlib import Path
from datetime import date, timedelta

doc_path = Path("F29/src/04_navrh_PR_F29.md")  # nebo arg
text = doc_path.read_text(encoding='utf-8')

# Extrahuj datum podání z hlavičky
datum_match = re.search(r'Ve Včelné dne (\d+)\.\s*(\d+)\.\s*(\d+)', text)
if datum_match:
    d, m, y = int(datum_match.group(1)), int(datum_match.group(2)), int(datum_match.group(3))
    datum_podani = date(y, m, d)
    print(f"Datum podání v doc: {datum_podani}")
else:
    datum_podani = date.today()
    print(f"Datum podání nenalezeno, použij dnes: {datum_podani}")

print(f"Dnes: {date.today()}")
print(f"Rozdíl: {(date.today() - datum_podani).days} dní stale")
```

### 2. Ověř počty dní

Pro F29 PR (§465a ZŘS) jsou klíčové referenční datumy:

| Událost | Datum | Proměnná |
|---------|-------|---------|
| Přerušení kontaktu (PO ZZ) | 29. 1. 2026 | `d_preruseni = date(2026,1,29)` |
| Smrt Lukáše Kopeckého | 13. 1. 2026 | `d_smrt = date(2026,1,13)` |

```python
d_preruseni = date(2026, 1, 29)
d_smrt = date(2026, 1, 13)

# Spočítej očekávané počty dní k DATU PODÁNÍ
dni_preruseni = (datum_podani - d_preruseni).days
dni_smrt = (datum_podani - d_smrt).days

print(f"\nOčekávané počty k datu podání ({datum_podani}):")
print(f"  Přerušení kontaktu: {dni_preruseni} dní (od {d_preruseni})")
print(f"  Od smrti Lukáše: {dni_smrt} dní (od {d_smrt})")

# Grep všechny "N dní" z textu
found_days = re.findall(r'(\d+)\s*dní', text)
print(f"\nNalezené počty dní v textu: {sorted(set(int(x) for x in found_days))}")

# Zkontroluj shodu
issues = []
for n in found_days:
    n = int(n)
    if n in (dni_preruseni - 1, dni_preruseni, dni_preruseni + 1):
        continue  # OK range
    if n in (dni_smrt - 1, dni_smrt, dni_smrt + 1):
        continue  # OK range
    if n > 100:  # Pravděpodobně počet dní přerušení/smrt
        issues.append(f"  ⚠️ {n} dní — neodpovídá ani {dni_preruseni} ani {dni_smrt}")

if issues:
    print("\nKONZISTENCE CHYBY (dny):")
    for i in issues:
        print(i)
else:
    print(f"\n✅ Počty dní konzistentní ({dni_preruseni} / {dni_smrt})")
```

### 3. Zkontroluj §§ konzistenci

```python
# Detekuj §452 vs §465a — v PR dokumentu by neměly být §452 jako základ
par452 = re.findall(r'§\s*452(?!\s*odst\.\s*1\s*písm)', text)  # §452 mimo VÝROK III citaci
par465a = re.findall(r'§\s*465a', text)

print(f"\nReference §452 (neočekávané): {len(par452)}")
print(f"Reference §465a: {len(par465a)}")

if len(par452) > 2:  # Více než 2 = problem (disclaimer + VÝROK III jsou OK)
    # Najdi řádky
    for i, line in enumerate(text.split('\n'), 1):
        if '§ 452' in line and 'odst. 1 písm.' not in line and 'nepředstavuje' not in line:
            print(f"  ⚠️ L{i}: {line[:100]}")
```

### 4. Detekuj interní markery

```python
markers = ['NEPOSÍLAT', 'DRAFT', 'TODO', 'P1-', 'P2-', 'HOLD', 'FIXME', 'XXX']
print("\nInterní markery:")
for marker in markers:
    if marker in text.upper():
        lines = [f"  L{i}: {l.strip()}" for i, l in enumerate(text.split('\n'), 1)
                 if marker in l.upper()]
        for l in lines[:3]:  # max 3 příklady
            print(f"  ⚠️ [{marker}] {l}")

# Zkontroluj datum konzistenci
if datum_podani != date.today():
    days_stale = (date.today() - datum_podani).days
    print(f"\n⚠️ DATUM STALE: dokument je datován {datum_podani}, dnes je {date.today()} (+{days_stale} dní)")
    print(f"   Opravit: {datum_podani.day}. {datum_podani.month}. {datum_podani.year} → {date.today().day}. {date.today().month}. {date.today().year}")
    print(f"   Počty dní se změní: {dni_preruseni} → {(date.today() - d_preruseni).days}")
```

### 5. Výstup — CONSISTENCY REPORT

```
CONSISTENCY CHECK — F<XX> PR §465a
Dokument: <path>
Datum v doc: <datum_podani> | Dnes: <today>

STAV: ✅ OK / ⚠️ AMBER / ❌ BLOCKER

Počty dní:
  Přerušení: <X> dní k datu podání (<Y> ke dni spuštění)
  Smrt: <X> dní k datu podání (<Y> ke dni spuštění)

§§ konzistence:
  §452 neočekávané reference: <N>
  §465a reference: <N>

Interní markery: <PASS/FAIL>

Datum: <PASS/AMBER/STALE>

DOPORUČENÍ: Opravit datum + dny na <today> před renderem
```

---

## RULES

- Pokud `datum_podani != date.today()` → **vždy** hlásit AMBER (datum stale)
- Pokud počet dní nesedí na ±1 toleranci → hlásit BLOCKER
- §452 neočekávané reference (>2) → hlásit BLOCKER
- Interní markery v textu → hlásit BLOCKER
- Skill je **read-only** — nikdy neupravuje dokument sám, jen reportuje
- Tom / legal instance aplikuje opravy ručně (nebo s Tom T1 GO)

---

## KDY VOLAT

- Vždy před renderem PDF (zejm. po půlnoci = nový den)
- Před každým LOCK 1 auditem (jako přípravný krok)
- Při přechodu F-cyklu na nový den (datum stale detection)
- Automaticky jako součást `attachment-pipeline` kroku 0

---

## RELATED

- `attachment-pipeline` — orchestrator: může volat tento skill jako krok 0 před ZIP
- `locks-workflow` — LOCK 1 L1 zahrnuje datum/dny konzistenci
- `doc-polish` — aplikuje opravy po konzistency reportu (po Tom GO)
- `F29/_CHANGE_MATRIX_F28_F29.md` sekce F — ship checklist kde LOCK 1 používá tento výstup
