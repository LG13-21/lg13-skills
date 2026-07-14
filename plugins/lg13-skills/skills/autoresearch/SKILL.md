---
name: autoresearch
description: Use when you need autonomous iterative research or improvement — argument strengthening, CDC gate progression, judikatura hunting, document quality loops. Goal + metric + loop until done.
---

# Autoresearch

**Principy Karpathy:** constraint + mechanical metric + autonomous iteration = compounding gains.

> *"Nastav GOAL → agent běží LOOP → probudíš se k výsledkům."*

---

## Zákon č. 0 — Tři ingredience před spuštěním

Bez těchto tří věcí neexistuje loop:

| Ingredience | Příklad (legal kontext) |
|-------------|------------------------|
| **GOAL** — co chceme zlepšit | CDC locky F43 z 13/14 na 14/14 |
| **METRIC** — číslo které měříme | počet PASS locků (vyšší = lepší) |
| **VERIFY** — jak ověřit iteraci | spočítat PASS řádky v lock_matrix.md |

---

## Základní loop

```
SETUP (jednou):
  1. Přečti kontext + git historii
  2. Definuj GOAL + METRIC + VERIFY
  3. Nastav BASELINE (iterace #0)
  4. Potvrď a spusť

LOOP (N iterací nebo dokud GOAL splněn):
  1. Přečti aktuální stav + git log + výsledkový log
  2. Vyber JEDNU změnu (co fungovalo, co selhalo, co nebylo zkuseno)
  3. Proveď změnu
  4. Git commit (PŘED verifikací)
  5. Spusť mechanickou verifikaci (VERIFY příkaz)
  6. Zlepšení? → keep. Horší? → git revert. Crash? → oprav nebo přeskoč.
  7. Zaloguj výsledek (TSV format)
  8. Opakuj dokud N iterací nebo GOAL splněn
```

**Každé zlepšení se skládá. Každé selhání se auto-revertuje. Progress logován v TSV.**

---

## 8 kritických pravidel

| # | Pravidlo |
|---|----------|
| 1 | **Ohraničeno defaultně** — každý task má defaultní počet iterací; unlimited = opt-in |
| 2 | **Číst před psaním** — plný kontext před první editací |
| 3 | **Jedna změna na iteraci** — atomické změny; pokud se rozbije, víš proč |
| 4 | **Jen mechanická verifikace** — žádné subjektivní „vypadá dobře"; použij metriku |
| 5 | **Automatický rollback** — selhané změny revertovány okamžitě |
| 6 | **Jednoduchost vítězí** — stejný výsledek + méně textu = keep |
| 7 | **Git je paměť** — čti `git log` + `git diff` před každou iterací |
| 8 | **Stuck? Mysli hlouběji** — přečti znovu, kombinuj téměř-úspěchy, zkus radikální změnu |

---

## Subtypy tasků (legal kontext)

### `/autoresearch plan` — Goal to Config (jednou)
Nejhorší část není loop — je to správně definovat Scope/Metric/Verify.

```
GOAL: Posílit argumentaci sekce II F43 o judikaturní podporu
SCOPE: F43/01_odvolani_EXE_F43.3.md (edit) + judi_library/ (read-only)
METRIC: počet judikátů citovaných v sekci II (vyšší = lepší)
VERIFY: grep -c "ÚS\|NS" F43/01_odvolani_EXE_F43.3.md
DIRECTION: maximize
Iterations: 10
```

### `/autoresearch loop` — Základní iterační smyčka

Klasický Karpathy loop. Pro:
- Zlepšení CDC lock skóre
- Posílení argumentace (diamond picking)
- § citační čistota
- Judikatura coverage

### `/autoresearch debug` — Hledání problémů

Vědecká metoda. Hypotéza → experiment → výsledek.

Pro:
- Proč lock X selhává?
- Kde je chyba v § citaci?
- Proč dokument neprošel A3?

Formát:
```
SYMPTOM: A3 lock FAIL — §§ nejsou ověřeny
SCOPE: F43/01_odvolani_EXE_F43.3.md
Iterations: 10
```

### `/autoresearch fix` — Oprav vše na nulu

Bere broken stav a iterativně opravuje dokud vše neprojde.

Pro:
- Oprava blokujících CDC gates
- Nulování chybových §§
- Vyčištění interních markerů

```
FIX: oprav všechny FAIL locky v F42 lock_matrix.md
Iterations: 15
```

### `/autoresearch research` — Hloubkový výzkum

Multi-round judikatura + argumentační research. Prohledává CGE, judi_library, judi_index.

```
TOPIC: judikatura k zásadě subsidiarity (ultima ratio) při exekuci nemovitosti
SCOPE: judi_library/judi_index.json + ChatGPT_export/ (read-only)
GOAL: najdi 3+ ÚS/NS rozhodnutí relevantní pro F43 sekci II
VERIFY: python scripts/judi_sentry.py search "ultima ratio" --top 5
Iterations: 8
```

### `/autoresearch predict` — Multi-pohled před rozhodnutím

5 různých perspektiv v jednom kole. Bez loop.

Persony pro legal kontext:
- **Soudce** — jak vidí petit a argumentaci
- **Protistrana (Flaška/ZZ)** — co zaútočí
- **OSPOD** — co říká k zájmu Matouše
- **Ústavní soud** — fundamentální právo + proporcionalita
- **Devil's Advocate** — co je nejslabší místo

### `/autoresearch reason` — Adversarial refinement

Pro rozhodnutí kde neexistuje objektivní metrika. Competing kandidáti → kritika → syntéza → blind judges → konvergence.

Pro:
- Která formulace petitu je silnější?
- A nebo B varianta odvolání?
- Jak formulovat klíčový argument sekce I?

---

## Výsledkový log (TSV)

```tsv
iteration	commit	metric	delta	status	description
0	a1b2c3d	13	0	baseline	lock matrix výchozí stav
1	b2c3d4e	13	0	keep	doplnění datumu blokace (C3 partial → full)
2	c3d4e5f	14	+1	keep	fyzická příloha 2 označena jako čekající (C5 PASS)
3	-	13	-1	discard	pokus o přidání § citace — verze neexistuje
```

Analyzuj s: `/autoresearch evals` nebo ručně přes `tail -20 *-results.tsv`.

---

## Ochranná pravidla (lg13 specifická)

| Pravidlo | Důvod |
|----------|-------|
| **STOP ORDER #1452 aktivní** — nevkládej odesílací příkazy do loop | Odesílání jen přes T002 po KONEC STOP |
| **Žádné interní markery** v editovaných dokumentech | ZÁSADNÍ ZÁKAZ — viz Zákon č. 0 v `writing-doc` |
| **CHANGE_MATRIX povinná** pro každý dokument bump | versioning disciplína |
| **Read-only scope pro judi_library** | index = pre-built, nespouštět build |
| **Git je paměť** — commit PŘED verifikací | rollback zachytí čistý stav |

---

## Guard — prevence regresí

Pokud zlepšuješ jednu metriku, loop může rozbít jiné věci.

```
GOAL: zlepšit argument coverage sekce I
VERIFY: grep -c "ÚS\|NS" F43/01_odvolani_EXE_F43.3.md
GUARD: python scripts/forensics.py F43/ --check-markers  # nesmí najít interní markery
```

- **Verify** = zlepšilo se cílová metrika?
- **Guard** = nerozbilo se nic jiného?

Pokud metrika roste ale guard selže → přepracuj změnu (max 2 pokusy).

---

## Rychlé použití

```
# Zlepšení lock skóre (bounded, 10 iterací):
/autoresearch loop
GOAL: F43 z 13/14 na 14/14
SCOPE: F43/01_odvolani_EXE_F43.3.md
METRIC: počet PASS locků v F43/cdc/lock_matrix.md
VERIFY: grep -c "PASS" F43/cdc/lock_matrix.md
Iterations: 10

# Judikatura hunting:
/autoresearch research
TOPIC: judikatura k blokaci bankovního účtu + EP přikázáním pohledávky
Iterations: 8

# Multi-pohled před odesláním:
/autoresearch predict
SUBJECT: F46 návrh PR v6 — soudní perspektiva + red team

# Stuck na looku — hloubkové hledání:
/autoresearch debug
SYMPTOM: A3 selhává přes 3 iterace
Iterations: 5
```

---

## Related

- `lg13-skills:diamond-sentry` — automatická extrakce diamondů z CGE/atoms
- `lg13-skills:diamond-pick` — triáž KEEP/DROP/REFORMULATE
- `lg13-skills:judi-sentry` — judikát search + linking
- `lg13-skills:writing-doc` — § verifikace + CDC gates + no-markers rule
- `lg13-skills:doc-polish` — automatizovaný polish loop (re-run checks + render)
- Vzor: `L:/GitHub/autoresearch` (uditgoenka, v2.2.1) — plná implementace 14 subcommandů
- Karpathy principy: `L:/GitHub/andrej-karpathy-skills/skills/karpathy-guidelines/SKILL.md`
