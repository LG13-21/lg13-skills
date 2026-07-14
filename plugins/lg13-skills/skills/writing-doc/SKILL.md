---
name: writing-doc
description: Use when authoring or editing Czech court filings (návrhy, odvolání, doplnění, podněty, odvolání EXE) — covers mandatory document structure, § citation verification, no-internal-markers rule, CDC gate checklist, and versioning discipline
---

# Psaní soudních podání

## Přehled

Soudní podání musí projít soudem, ne jen autorem. Jedna neexistující § citace nebo interní marker v odeslaném dokumentu poškodí důvěryhodnost nebo podání zneplatní. Tento skill zajišťuje disciplínu při psaní — od první věty po CHANGE_MATRIX.

**Základní princip:** Soud čte artifact, ne knowledge graph. Každý byte, který dorazí na soud, musí být čistý.

---

## Zákon č. 0 — Žádné interní markery

**Absolutní zákaz** v dokumentu určeném soudu:

- DRAFT, HOLD, TODO, NEPOSÍLAT, POZOR
- Versioning: `v2`, `rev3`, `F43.2` v textu dokumentu
- Task IDs: P1-X, #123, issue reference
- HTML komentáře: `<!-- ... -->`
- Instrukce budoucím editorům

Tyto věci patří do `meta.json` a `CHANGELOG.txt`. **Nikam jinam.**

> Incidenty 15. 4. 2026 a 16. 4. 2026 — CHANGE_MATRIX jako lekce: marker „NEPOSÍLAT" přežil render do PDF. Nikdy víc.

---

## Zákon č. 1 — § musí existovat přesně

Před každou § citací ověř:
1. Zákon s tímto číslem/zkratkou existuje
2. § (odstavec, písmeno) v zákoně existuje
3. § upravuje přesně to, co tvrdím

**Nejčastější pasti:**

| Chybná citace | Správná | Proč chybná |
|--------------|---------|-------------|
| § 47 odst. 1 písm. f) ExŘ | § 58 odst. 2 písm. d) ExŘ | § 47 ExŘ = pověření exekutora; hierarchie způsobů = § 58 odst. 2 písm. d) |
| § 55 odst. 5 ExŘ | § 55 odst. 1 písm. a) ExŘ | zastavení z důvodu uspokojení = odst. 1 |
| § 452 ZŘS (obecně) | § 465j ZŘS | novela č. 268/2025 Sb. přečíslovala |
| § 869 odst. 1 OZ | § 869 odst. 2 OZ | odst. 1 = povinnosti; odst. 2 = zákonný důvod pro změnu |

Pokud § nelze ověřit → necituj nebo použij obecnější odkaz na zákon.

---

## Povinná struktura dokumentu

```
1. ZÁHLAVÍ        adresát (tučně), DS, "prostřednictvím" pokud KS přes OS
2. IDENTIFIKACE   Navrhovatel/Odvolatel: jméno, nar., DS
3. SP.ZN.         soudu + exekutora (pokud EXE)
4. ZPŮSOB PODÁNÍ  "Způsob podání: datovou schránkou na OS ČB (DS: ws6abvh)."
                  + "Na vědomí: ..." (exekutor, OSPOD, protistrana)
5. NADPIS         typ podání (h1, tučně)
6. OZNAČENÍ       č.j. usnesení/rozhodnutí, datum vydání, datum doručení, lhůta
7. OSLOVENÍ       "Vážený soude," ← NIKDY "Vážený soudu,"
8. ÚVOD           co napadáme/doplňujeme, návrh jak rozhodnout
9. SEKCE I–N      argumentace (h2 nadpisy číslované)
10. PETIT         jasný, konkrétní, číslovaný a)/b)/c)
11. PODPIS        "S úctou\nVe Včelné dne DD. M. YYYY\n**Ing. Tomáš Kopecký**\n..."
12. PŘÍLOHY       číslovaný seznam (1. Název — popis)
```

**Pole, která NESMÍ zůstat prázdná při commitu:**
- Datum oslovení (`Ve Včelné dne ___`) = C3 STOP gate
- Datum blokace/doručení (pokud je v textu `___. _. 2026`) = C3 STOP gate

Pokud datum ještě není znám → explicitně označ jako čekající v CHANGE_MATRIX, ne v dokumentu.

---

## Petit — jak psát

Petit = nejdůležitější část. Soudce ji čte první.

**Špatně:**
> Navrhuji, aby soud přijal vhodná opatření k ochraně zájmů nezletilého.

**Správně:**
> Navrhuji, aby soud **změnil** usnesení č.j. 34 EXE 1426/2026-26 ze dne 18. 6. 2026 tak, že exekuci prodejem nemovitostí **odkládá** do doby, než bude postaveno najisto, zda je pohledávka uspokojena z EP přikázáním pohledávky z účtu (č.j. 213 EX 31/26-19).

Pravidla:
- Akční sloveso tučně: **změnil**, **zrušil**, **odložil**, **zastavil**, **nařídil**
- Konkrétní č.j. a datum napadeného rozhodnutí
- Konkrétní zákonný důsledek
- Alternativy číslovat: **a)** primární, **b)** subsidiární

---

## Versioning protokol

```
F43.1.md  →  render  →  F43.1.pdf  →  git commit
                                          ↓ změna
CHANGE_MATRIX_F43_v1_to_v2.md  →  F43.2.md  →  F43.2.pdf  →  git commit
                                          ↓ změna
CHANGE_MATRIX_F43_v2_to_v3.md  →  F43.3.md  →  F43.3.pdf  →  git commit
```

**CHANGE_MATRIX obsahuje:**
- Důvod verze (1-2 věty)
- Tabulka změn: `# | Místo (ř.N, sekce) | Před | Po`
- Lock matrix diff: co bylo FAIL → co je PASS
- Položky čekající na autora (datum, přílohy)

Bez CHANGE_MATRIX = žádná nová verze. Přímá editace main dokumentu bez CHANGE_MATRIX = disciplinární selhání.

---

## CDC gate systém (14 locků)

Dokument je **ship-ready** pouze při **14/14 ✅**. C6 = GO/STOP gate.

### A-blok — obsah
| Lock | Otázka |
|------|--------|
| A1 Petit | Petit je konkrétní, soud ví přesně co nařídit? |
| A2 Facts | Skutkový stav kompletní, data konzistentní? |
| A3 Comply | Všechny §§ existují a správně aplikovány? |
| A4 Judikat | Judikatura citována s tezí proč relevantní? |

### B-blok — struktura
| Lock | Otázka |
|------|--------|
| B1 Scan | 3-Second Scan Test: str. 1 = petit + klíčový argument? |
| B2 Flow | Sekce na sebe logicky navazují, žádné repetice? |
| B3 Terms | Zkratky definovány při prvním výskytu? |
| B4 Attach | Přílohy číslované, všechny zmíněné v textu? |

### C-blok — polish + ship
| Lock | Otázka |
|------|--------|
| C1 F.Read | Oslovení „Vážený soude,"? |
| C2 Admin | Způsob podání v záhlaví, DS soudu + exekutora? |
| C3 Dates | Žádné prázdné datum (`___`)? |
| C4 Persons | Tituly správné (Ing./Mgr./Bc.), data nar. správná? |
| C5 Attach | Fyzické přílohy existují nebo explicitně označeny jako čekající? |
| C6 RTS | Žádné interní markery, C1–C5 PASS → GO |

---

## Rationalization table

| Myšlenka | Realita |
|----------|---------|
| „§ to zhruba odpovídá" | § buď existuje přesně, nebo se necituje |
| „HTML komentář soud neuvidí" | Renderery ho mohou zobrazit; PDF source je čitelný |
| „Datum doplním před odesláním" | Šablona s `___` = C3 STOP; doplň teď nebo označ v CHANGE_MATRIX |
| „Je to draft, lze opravit" | Každý soubor v git může být náhodou odeslán; DRAFT patří do meta.json |
| „CHANGE_MATRIX je jen formalita" | CHANGE_MATRIX je audit trail; bez ní nelze rekonstruovat co se změnilo a proč |
| „Přepíšu celý dokument, bude to rychlejší" | NIKDY přepisovat celý dokument kvůli 1 chybě — targeted fix + CHANGE_MATRIX |

---

## Checklist před committem

- [ ] Žádné `___` v datech
- [ ] Žádné interní markery (viz Zákon č. 0)
- [ ] Všechny §§ ověřeny (viz Zákon č. 1)
- [ ] Petit konkrétní s akčním slovesem tučně
- [ ] Oslovení „Vážený soude,"
- [ ] Způsob podání v záhlaví
- [ ] Přílohy číslované (1. … 2. …)
- [ ] CHANGE_MATRIX hotová (pokud verze bump)
- [ ] render → PDF + git commit s MD + PDF + CHANGE_MATRIX

---

## Related

- `lg13-skills:locks-workflow` — 6-lock ship pipeline (LEGAL→STRAT→CHATGPT→TIME→TOM→T002)
- `lg13-skills:doc-polish` — automatizovaný polish loop (re-run checks, render, lock release)
- `lg13-skills:legal-total-analysis` — full 14-lock CDC analýza
- Vzor CHANGE_MATRIX: `F42/cdc/CHANGE_MATRIX_F42_v1_to_v2.md`
- Vzor finálního dokumentu: `F44/01_odvolani_F39_F44.8.md`
