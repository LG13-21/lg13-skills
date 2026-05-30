---
name: doc-polish
description: "Spustí filing pipeline OD PROSTŘEDKA — re-run analýz jen na problémech z předchozího kola + kompletní test suite (přílohy, datumy, §, počty dní, čitelnost, render, OCR, judge sim, compliance, red team) + lock release do TIME_CAPSULE. Trigger: 'polish', 'doc-polish', 'run from middle', 'nova verze hotova', 'zkontroluj novou verzi', 'serie testu', 'pre-ship check', 'lock release'."
version: 1.1.0
status: stable
user-invocable: true
---

# /doc-polish — Mid-pipeline polish loop

## CO DĚLÁ

Filing pipeline od prostředka. Máme hotový dokument (prošel Phase 1 nebo předchozím kolem).
Teď: targeted re-run + full test suite + lock release.

**NE od nuly.** Phase 1 (Build) se neopakuje.
**ANO:** nové kolo verify + specifické checks + render + lock.

---

## QUICK RUN

```bash
# Targeted (jen problémy z prev kola)
python L:/GitHub/legal-ship-2026/scripts/doc_polish.py --file <doc.md>

# Full scope
python L:/GitHub/legal-ship-2026/scripts/doc_polish.py --file <doc.md> --scope full

# S lock release do TIME_CAPSULE
python L:/GitHub/legal-ship-2026/scripts/doc_polish.py --file <doc.md> --release-lock

# S CHANGELOG z předchozího kola (pro targeted scope)
python L:/GitHub/legal-ship-2026/scripts/doc_polish.py \
  --file <doc.md> \
  --prev-changelog CHANGELOG_polish_<TS>.txt
```

**Backing script:** `L:/GitHub/legal-ship-2026/scripts/doc_polish.py`
Volá: `filing_pipeline.py` (attachments/fact-check/law-check/admin-check) + `petit_finder.py` + `capsule_manager.py`

---

## VSTUPY

```
/doc-polish <doc.md>                         — cílový dokument
/doc-polish <doc.md> --prev-changelog <log>  — CHANGELOG z předchozího kola
/doc-polish <doc.md> --scope targeted        — jen problémy z prev kola (default)
/doc-polish <doc.md> --scope full            — plný rerun všech checks
/doc-polish <doc.md> --release-lock          — na konci zapsat lock do TIME_CAPSULE
```

Pokud Tom nezadá vstupy → ptát se: "Který soubor? Mám CHANGELOG z předchozího kola?"

---

## FÁZE 0 — CONTEXT LOAD (povinné, <30s)

```python
# 1. Načti dokument
doc = Path(DOC_PATH).read_text(encoding="utf-8")

# 2. Načti CHANGELOG z předchozího kola (pokud existuje)
changelog_path = PREV_CHANGELOG or find_latest_changelog(DOC_PATH)
prev_issues = parse_changelog_problems(changelog_path)  # CRITICAL + WARNING items

# 3. Zobraz scope
if prev_issues:
    print(f"Targeted scope: {len(prev_issues)} problémů z předchozího kola")
    for i in prev_issues:
        print(f"  [{i.severity}] {i.description}")
else:
    print("Žádný CHANGELOG → full scope")
    scope = "full"
```

---

## FÁZE 1 — TARGETED RE-RUN (~2 min)

Opakuj POUZE kontroly relevantní pro problémy z prev kola.
Pokud prev kolo nenašlo § problémy → § check přeskoč.

```
prev CRITICAL §465a → spustit legal check
prev CRITICAL datum → spustit validation check
prev WARNING délka → spustit readability check
```

Každý check: najde → opraví → zapíše do CHANGELOG.

---

## FÁZE 2 — SPECIFIC CHECKS (série, povinné vždy)

### 2.1 Přílohy — kompletnost

```python
# Každá příloha zmíněná v textu = soubor na disku (a naopak)
# Formát: P01, P02, K00, K01 ...
referenced = re.findall(r'\b(P\d{2}|K\d{2})\b', doc)
on_disk = list_attachments(doc_dir)
missing = set(referenced) - set(on_disk)
extra = set(on_disk) - set(referenced)
# CRITICAL pokud missing; WARNING pokud extra
```

Navíc: správné pořadí (P01 < P02 < ... bez mezer), soubory neprázdné, PDF readable.

### 2.2 Datumy — konzistence

```python
# Najdi všechny datumy v dokumentu
dates = re.findall(r'\d{1,2}\.\s*\d{1,2}\.\s*\d{4}', doc)
# Kontrola:
# - žádná budoucí data pro minulé události
# - žádné relativní ("dnes", "včera", "minulý týden")
# - konzistence (stejná událost = stejné datum všude)
# - OSPOD pohovor = 1. 4. 2026, incident = 29. 1. 2026, atd.
```

### 2.3 § — validita a konzistence

```python
DEPRECATED = {"§ 452": "→ použít § 465j", "§ 76 OSŘ": "→ § 465j ZŘS"}
REQUIRED_FOR_PR = ["§ 909", "§ 858", "§ 888"]
# Kontrola deprecated §
# Kontrola povinných § pro typ podání (PR/PO/MER)
# §869 odst. 1 vs odst. 2 (neplést!)
# Novela z. 268/2025 Sb. — §465a-j
```

### 2.4 Počty dní

```python
# Výpočty: 29.1.2026 → dnes = X dní
# Všechny "X dní" v textu ověřit výpočtem
# "120 dní" vs. "126 dní" vs. aktuální počet
# Fallback lhůty (7 dní, 3 dny, 14 dní) — jsou splnitelné?
from datetime import date
incident = date(2026, 1, 29)
today = date.today()
days = (today - incident).days
# Najdi všechna "N dní" v doc a porovnej s výpočtem
```

### 2.5 Počty elementů (slim structure)

```python
# Max 2-3 MAIN argumenty, zbytek = COMPLEMENTARY nebo příloha
# Hledej sekce: Nové skutečnosti, Právní argumentace, Důkazní návrhy
# Každá sekce: max 3 hlavní body
# Ostatní → přesunout do přílohy nebo sloučit
# VÝROK struktura: max 3 výroky (I, II, III) + fallback
```

### 2.6 Stručnost + přesun do příloh

```python
# Věty delší než 3 řádky → kandidát na zkrácení
# Odstavce delší než 8 řádků → kandidát na přesun do přílohy
# Opakující se argumenty → sloučit
# Emocionální slova → nahradit fakty
SUBJECTIVE = ["cítím", "věřím", "myslím", "jsem přesvědčen", "bohužel", "tragicky"]
EMOTIONAL = ["šokující", "kruté", "nepřijatelné", "záměrně", "záludně"]
# CRITICAL: emocionální slova o protistraně
```

### 2.7 Čitelnost — 3-Second Scan Test

```
Soudce skenuje 3 vteřiny:
- Vidí VÝROK / petit jasně? (musí být v prvních 3 odstavcích nebo v sekci PETIT)
- Vidí sp.zn. a datum? (záhlaví)
- Vidí klíčový argument? (bold nebo tučně)
```

### 2.8 Nadbytečné a duplicitní části

```python
# Najdi odstavce s podobným obsahem (fuzzy match >80%)
# Najdi opakující se fráze (3+ výskyty stejné věty)
# Najdi sekce bez obsahu (jen nadpis, žádný text)
# Záhlaví: jen jednou na začátku
# Podpis: jen jednou na konci
```

---

## FÁZE 3 — RENDER + AUTOMATICKÉ TESTY

### 3.1 Render
```bash
python F18/renderer/render.py <doc.md> --output <doc_polished.pdf>
```
Kontrola: PDF neprázdný, stránky ≥ 2, text selectable (ne obrázek).

### 3.2 OCR sanity
```bash
# Porovnej MD zdroj vs. PDF OCR výstup
# Žádné rozbité znaky (č→c, š→s, ě→e)
# Správná diakritika
```

### 3.3 Fast Read (soudce má 90 vteřin)
```
Přečti celý dokument jako soudce pod časovým tlakem:
- Je jasné CO žádáme? (petit/výrok)
- Je jasné PROČ? (klíčový argument — max 1 věta)
- Je jasné KDY? (datum/lhůta)
- Nic matoucího nebo zavádějícího v prvních 2 stranách?
```

### 3.4 Judge Simulation
Viz filing-pipeline 2.1-2.5 — ale rychle, jen kritické:
- Validation: data, sp.zn., jména ✓
- Compliance: child-first, žádné útoky ✓
- Opposition: hlavní argument obstojí? ✓
- Security: žádné interní markery ✓
- Legal: § správné ✓

### 3.5 Judge Fatigue Check
```
Soudce číst 50+ podání denně. Je naše podání:
- Kratší než 8 stran? (ideál: 4-6)
- Bez zbytečných opakování?
- Petit na začátku nebo jasně označený?
- Font ≥ 12, řádkování ≥ 1.2?
- Odstavce ≤ 6 řádků?
```

### 3.6 Compliance Quick Check
```python
python scripts/legal_compliance_check.py --file <doc.md> --quick
# Score ≥ 85 → PASS
# Score < 85 → FAIL (vypsat problémy)
```

### 3.7 Red Team
```
Mysli jako Mgr. Flaška (advokát protistrany):
- Co napadneš jako první?
- Jaký argument obrátíš?
- Co chybí co by slabinu zakrylo?
Top 3 útoky → mají odpovědi v dokumentu?
```

### 3.8 Total Analysis (petit check)
```bash
# Spustí petit_finder.py na aktuální doc
python scripts/petit_finder.py --single <doc.md> --output petit_check/
# Výstup: enforcement_score per výrok, issues list
# PASS: všechny výroky ≥ 80
# FAIL: výrok < 80 → vypsat problém
```

---

## FÁZE 4 — VERDICT

```python
# Agreguje všechna findings ze Fáze 1-3
criticals = [f for f in all_findings if f.severity == "CRITICAL"]
warnings = [f for f in all_findings if f.severity == "WARNING"]

if criticals:
    verdict = "NO_GO"
elif warnings > 3:
    verdict = "CONDITIONAL_GO"
else:
    verdict = "GO"

# Zapíše CHANGELOG entry
# Vytvoří polish_report.md
```

---

## FÁZE 5 — LOCK RELEASE (pokud --release-lock nebo verdict=GO)

```python
from scripts.capsule_manager import CapsuleManager

capsule = CapsuleManager()
capsule.write_lock(
    instance="legal",          # nebo strat/coder
    status="READY" if verdict == "GO" else "PENDING",
    doc=DOC_PATH,
    checks_passed=[...],
    warnings=[w.description for w in warnings],
    blockers=[c.description for c in criticals],
)

# Kontrola: jsou všechny locks uvolněny?
if capsule.all_locks_ready():
    print("✅ VŠECHNY LOCKS UVOLNĚNY")
    print(f"TIME_CAPSULE: {capsule.capsule_path}")
    print("Tom může spustit CHECK_CAPSULE_LOCKS.bat")
else:
    pending = capsule.pending_locks()
    print(f"⏳ Čeká: {pending}")
```

---

## VÝSTUPY

```
<doc_dir>/
├── <doc>_polished_<TS>.pdf    ← finální PDF
├── CHANGELOG_polish_<TS>.txt  ← co bylo nalezeno a opraveno
├── polish_report_<TS>.md      ← executive summary (GO/NO-GO + top issues)
└── petit_check/               ← petit_finder výstup

TIME_CAPSULE_ISDS_READY/
├── LOCKS/
│   └── lock_<instance>.json   ← tento instance lock
└── (ostatní locks od jiných instancí)
```

---

## PRAVIDLA

- Opravuj přímo v dokumentu (ne "doporučuji") nebo napiš WARNING
- Max 2 průchody per problém (viz filing-pipeline)
- NIKDY nepřepisuj celý dokument kvůli 1 chybě
- CHANGELOG: každá změna musí mít záznam
- Render: vždy před lock release
- STOP #1452: lock release ≠ odeslání; odeslání výhradně Tom přes BAT

---

## RELATED

- `filing-pipeline` — celá pipeline od nuly (Phase 1+2+3)
- `legal-total-analysis` — full pre-flight audit (9 kroků)
- `capsule_manager.py` — TIME_CAPSULE lock management
- `CHECK_CAPSULE_LOCKS.bat` — Tom spouští pro finální check + ISDS
