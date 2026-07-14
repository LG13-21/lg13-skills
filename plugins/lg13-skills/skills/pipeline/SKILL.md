---
name: pipeline
description: "Filing pipeline pro soudni podani. Mody: 'pipeline complete' (ph1→ph3), 'pipeline resume phN' (phN→ph3). Freeze guard: LOCK 2+ blokuje complete, povoli jen resume ph3. Token-efektivni: skripty > cteni velkych souboru do kontextu. Trigger: 'pipeline complete', 'pipeline resume ph2', 'pipeline status'."
---

# Pipeline — Filing workflow

## POUZITI

```
pipeline complete              # ph1 → ph2 → ph3 (jen bez LOCK 2+)
pipeline resume ph2            # ph2 → ph3
pipeline resume ph3            # ph3 pouze (5 LOCKS + send)
pipeline status                # aktualni faze + freeze stav
```

---

## FREEZE GUARD (vzdy jako prvni krok)

```bash
python L:/LG13/app/agent/skills/filing_pipeline.py pre-send --draft-id <ID> 2>&1 | head -3
```

| Stav | `complete` | `resume ph2` | `resume ph3` |
|------|-----------|--------------|--------------|
| Bez LOCKu | OK | OK | OK |
| LOCK 1 (Tom) | OK | OK | OK |
| LOCK 2+ (Strat) | **BLOKOVAN** | OK | OK |
| LOCK 3+ (Legal) | **BLOKOVAN** | **BLOKOVAN** | OK |

Pokud `complete` blokovan → sdelej Tomovi aktualni LOCK stav + doporuc spravny `resume` prikaz.

---

## PH1: BUILD (tato instance)

**Cil:** 1 cisty .md, kompletni prilohy, CHANGELOG inicializovan.

```bash
# Zkontroluj prilohy (0 tokenu)
python L:/LG13/app/agent/skills/filing_pipeline.py attachments --file <doc.md> --json

# Admin check (0 tokenu)
python L:/LG13/app/agent/skills/filing_pipeline.py admin-check --file <doc.md> --json
```

**Kroky:**
1. Inventura — identifikuj vsechny drafty, co uz bylo odeslano (neduplicitat)
2. Konsolidace — sluc zdroje, nejsilnejsi formulace z kazdeho, odstran duplicity
3. Struktura — pořadi: hlavicka → uvod → nove skutecnosti → pravni argumentace → dukazy → petit → prilohy
4. Zestihleni — pro KAZDOU vetu: nova info? nutna? safe? ne → ven
5. Prilohy — kazda v textu = soubor na disku (a naopak), cislovane postupne
6. Zaloz `CHANGELOG.txt` + `PREHLED.md`

**Petit test:** Je petit vykonatelny? Soud musi vedet presne co ma udelat.
Vzdy 3 urovne: primarni + subsidiarni + podpurny.

**Vystup PH1 → `resume ph2 --file <hotovy.md>`**

---

## PH2: VERIFY (JINA instance nez PH1!)

**Kriticke pravidlo:** Kdo psal PH1, ten NEDELÁ PH2. Jina session, cisty kontext.

**Flow:** seriove (ne paralelne). Kazda kontrola: najde → opravi → CHANGELOG → dalsi.

```bash
# Regex kontroly (0 tokenu) — spust vzdy
python L:/LG13/app/agent/skills/filing_pipeline.py full --file <doc.md> --json
```

### 2.1 Validation
```bash
python L:/LG13/app/agent/skills/filing_pipeline.py fact-check --file <doc.md> --json
```
Hleda: neplatna data, spatna jmena/sp.zn./DS, TODO/FIXME/DRAFT, chybejici hlavicka/podpis/datum, rozbita diakritika.

### 2.2 Compliance + best interest
AI check celeho textu:
- Child-first — vse pro dite, ne proti matce
- Kazdy argument: musime ho rict? Pomaha petitu? Je safe?
- Hedging ("pravdepodobne") → dokazat nebo vynechat
- Tonalita — zadna emoce, jen fakta

### 2.3 Opposition
Mysli jako Mgr. Flaska:
- Pro kazdy argument: jak ho napada protistrana?
- Slaba tvrzeni bez dukazu → CRITICAL
- Otocitelne argumenty → CRITICAL
- Subsidiarni petit pokud soud odmitne primarni?

### 2.4 Security
```bash
python L:/LG13/app/agent/skills/filing_pipeline.py full --file <doc.md> --json
```
Hleda: interni markery (NEPOSILAT, verze, changelog) v textu, URL/paths/AI zmínky, strategie v textu, PDF metadata.

### 2.5 Legal + Law
```bash
python L:/LG13/app/agent/skills/filing_pipeline.py law-check --file <doc.md> --json
```
Hleda: deprecated § (§452 → §465j, §76 OSR → §465j), novela z. 268/2025 Sb., judikatura validni, petit vykonatelny, spravny soud/sp.zn.

**Severity:**
- CRITICAL = oprav okamzite
- WARNING = zapis do CHANGELOG, Tom rozhodne
- INFO = jen k vedomi, neopravovat

**Max 2 pruchody na kontrolu.** Po 2. pruchodu s CRITICAL → eskaluj Tomovi.

**Vystup PH2 → dokument bez CRITICAL, CHANGELOG aktualizovan → `resume ph3`**

---

## PH3: 5 LOCKS + SEND

```
LOCK 1 TOM   — Tom cte dokument + CHANGELOG. Schvali obsah.
LOCK 2 STRAT — konzistence, Tom notes zapracovany, bez rozporu s odeslanymi
LOCK 3 LEGAL — § platne, judikatura, diskretnost, compliance
LOCK 4 T002  — datumy, prilohy = odkazum, PDF OK, fonty/format
LOCK 5 TIME  — cekaci lhuta (soud 60+ min; ASAP 5 min jen Tom)
```

```bash
# Gate check pred odeslanim
python L:/LG13/app/agent/skills/filing_pipeline.py pre-send --draft-id <ID>
```

**Odeslani:**
- **Matousovo rizeni (sp.zn. 0 P 29/2026)** = Tom odesila OSOBNE, nikdo jiny
- Ostatni rizeni = t002 po vsech 5 locks
- STOP ORDER #1452 — nic se neposila bez Tomova "KONEC STOP"

---

## CHANGELOG format

```
[2026-06-05 14:30] PH2.1 VALIDATION (instance: strat)
  FOUND: Datum 32.4.2026 neexistuje (radek 45)
  FIXED: Opraveno na 30.4.2026

[2026-06-05 14:40] PH2.3 OPPOSITION (instance: legal)
  FOUND: § 909 tvrzeni bez dukazu (radek 156)
  WARNING: Tom — dukaz v prílohách nebo smazat?
```

---

## PRAVIDLA

1. Freeze guard vzdy jako prvni krok
2. PH1 a PH2 = ruzne instance (kdo psal, ten nekontroluje)
3. PH2 seriove — 1 dokument, postupne cistejsi
4. Token-first: skripty (0 tokenu) > cteni velkych souboru do kontextu
5. CRITICAL → zastav, eskaluj Tom; nikdy posilej dokument s CRITICAL
6. Max 2 pruchody na kontrolu
7. STOP ORDER #1452 — checkni pred kazdym send

---

## SKRIPTY (reference)

| Prikaz | Co dela | Tokeny |
|--------|---------|--------|
| `filing_pipeline.py full` | Vsechny regex kontroly | 0 |
| `filing_pipeline.py attachments` | Prilohy check | 0 |
| `filing_pipeline.py fact-check` | Data, jmena | 0 |
| `filing_pipeline.py admin-check` | Hlavicka, sp.zn., podpis | 0 |
| `filing_pipeline.py law-check` | § validace | 0 |
| `filing_pipeline.py pre-send` | Gate check | 0 |
