---
name: deferred-plans
description: "Uloží nedokončený nebo odložený plán do gitu, aby ho příští session mohla zvednout. Trigger: 'ulož plán', 'odlož to na příště', 'zapiš co jsme nestihli', 'deferred plan', 'po resetu to doděláme', 'ulož na git'. Použij kdykoli session končí s rozpracovanou věcí která není blocker — lépe uložit než nosit v kontextu."
user-invocable: true
---

# Deferred Plans — Git-based odkládání plánů

## PROČ

Nedokončené plány v kontextu = zbytečná zátěž každé session. Git je správné místo — verzovaný, prohledatelný, přežije /compact i week reset.

---

## KAM UKLÁDAT

Repo: `lg13-runtime-state` (GitHub, LG13-21 org) — složka `plans/`
Lokálně: `L:/LG13/runtime/state/plans/` (synced s repem)

Filename: `deferred_<YYYY-MM-DD>_<slug>.md`

---

## EXECUTION

### 1. Napiš plán

Struktura souboru:

```markdown
# Deferred: <název úkolu>
# Datum: <YYYY-MM-DD>
# Session: <strat|legal|coder|...>
# Priorita: P0-P3
# Lze zvednout po: <reset window | konkrétní datum | hned>

## Co bylo uděláno
<stav při odložení — co funguje, co ne>

## Co zbývá
<konkrétní kroky, ne obecné plány>

## Blocker / proč odloženo
<token limit | čekám na X | nízká priorita>

## Kontext pro příští session
<co si musí přečíst, na co navázat, relevant soubory>
```

### 2. Ulož a commitni

```bash
# Zkopíruj do runtime/state
cp <file> L:/LG13/runtime/state/plans/<filename>

# Commitni
cd L:/LG13/runtime/state
git add plans/<filename>
git commit -m "deferred: <slug> (<priorita>)"
git push origin main
```

### 3. Zapiš do STAV_NOW.md

Přidej bullet do `STAV_NOW.md`:
```
- DEFERRED: <slug> → plans/<filename> (zvednout po <kdy>)
```

---

## ZVEDNUTÍ PLÁNU (příští session)

```bash
# List deferred plánů
ls L:/LG13/runtime/state/plans/

# Nebo prohledej
git -C L:/LG13/runtime/state log --oneline plans/
```

Přečti relevantní soubor a navazuj od "Co zbývá".

---

## PRAVIDLA

- Odložit ≠ zapomenout. Každý deferred plán má **datum nejpozd. zvednutí** — strat hlídá.
- P0/P1 se neodkládají bez Tomova vědomí.
- Po week resetu: strat projde `plans/` a zvedne co je k dispozici.
- Prázdné plány (jen "todo: dělat X") jsou k ničemu — vždy konkrétní stav + kroky.

---

## RELATED

- `STAV_NOW.md` — live sprint, DEFERRED bullet
- `lg13-runtime-state` repo — `plans/` složka
- `budget-manager` skill — week reset = trigger pro zvedání plánů
