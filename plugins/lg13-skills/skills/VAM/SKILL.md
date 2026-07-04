---
name: VAM
description: Use when analyzing document visual attention flow, scoring scan-readability, identifying dead zones, or optimizing court filing layout for first-impression impact
---

# VAM — Visual Attention Map

Mapuje, kam čtenářovo oko putuje při prvním pohledu na dokument. Pro soudní podání: soudce skenuje, nečte. Pokud petit nevidí do 3 sekund — ztraceno.

---

## Kdy použít

- Před CDC gate **B1 Scan** (3-Second Scan Test)
- Kdykoli se ptáš: "Vypadá to dobře?"
- Po strukturálních změnách v dokumentu
- Před finálním renderem (lock TIME)

---

## Principy vizuální pozornosti

### Jak oko čte soudní podání

```
╔═══════════════════════════════╗
║  ZÁHLAVÍ (přeskočí)           ║  ← skipped, znají formát
║  ────────────────────────     ║
║  Nadpis dokumentu    ← STOP   ║  ← první zastavení
║                               ║
║  Úvod ........... .... .....  ║  ← rychlý scan
║  ........... ... .........    ║
║                               ║
║  ## Petit            ← STOP   ║  ← druhé zastavení (zlaté místo)
║  **Navrhuji** aby soud ...    ║  ← akční sloveso = gravity point
╚═══════════════════════════════╝
```

**F-pattern:** Oko skenuje horizontálně nahoře, pak dolů po levém okraji, kratší skenování v polovině.

**Gravity points** = místa kde oko zastaví:
- `## H2 nadpisy` — silný anchor
- `**tučný text**` — stop, přečte
- `| tabulky |` — silný, strukturovaný přehled
- `1. číslované seznamy` — přečte první položku
- `**a) b) c)**` — petit struktura = nejsilnější anchor

**Dead zones** = místa kde oko projede bez zastavení:
- 3+ odstavce čistého textu bez vizuálního kotvy
- Celý odstavec bez bold, bez odrážek, bez zkratek
- Právní argumentace bez § záchytného bodu

---

## Spuštění

```
/VAM <cesta_k_souboru.md>
```

Nebo interaktivně: zadej obsah dokumentu / sekci.

---

## Analýza (5 kroků)

### Krok 1 — Inventář vizuálních prvků

Projdi dokument a spočítej:

| Prvek | Síla pozornosti | Příkaz pro grep |
|-------|----------------|-----------------|
| `## ` nadpisy | ★★★★★ | `grep -c "^## "` |
| `**bold**` | ★★★★ | `grep -c "\*\*"` |
| `\| tabulka \|` | ★★★★★ | `grep -c "^\|"` |
| `1. seznam` | ★★★ | `grep -c "^[0-9]\+\."` |
| `- odrážky` | ★★ | `grep -c "^- "` |
| čistý odstavec | ✗ (dead zone) | — |

### Krok 2 — Mapování sekce po sekci

Pro každou sekci (H2 nadpis → další H2) urči:

```
SEKCE: [název]
  Prvky: [seznam gravity points]
  Dead zones: [počet čistých odstavců za sebou]
  Pozornost: [1-5]
  Problém: [popis pokud < 3]
```

**Škála pozornosti:**
- **5** — tabulka nebo petit blok s tučným akčním slovesem
- **4** — H2 + tučná fráze v prvním odstavci
- **3** — H2 + alespoň 1 bold nebo odrážky
- **2** — H2 + čistý text (skoro dead zone)
- **1** — žádný H2, čistý text = dead zone

### Krok 3 — First-page audit

Povinný pro každý dokument:

```
□ Nadpis dokumentu viditelný okamžitě?
□ Petit (nebo "Navrhuji") v první třetině str. 1?
□ První tučné slovo = akční sloveso (navrhuji/odvolávám/žádám)?
□ Záhlaví netrvá déle než 5 řádků?
□ Žádný čistý text-blok delší než 4 řádky před petitem?
```

### Krok 4 — VAM skóre

```
Celkem bodů: součet pozornosti všech sekcí
Max možné: počet sekcí × 5
VAM% = celkem / max × 100
```

| VAM% | Hodnocení | Akce |
|------|-----------|------|
| ≥ 85 | Výborný | ship-ready (B1 PASS) |
| 70–84 | Dobrý | 1-2 targeted fixes |
| 55–69 | Průměrný | strukturální revize |
| < 55 | Kritický | celkový rework layoutu |

### Krok 5 — Dead zone rescue

Pro každou dead zone (sekce s hodnocením 1-2):

```
PROBLÉM: Sekce III — 4 odstavce čistého textu
RESCUE options (vyber jednu):
  A) Přidej shrnutí argumentu do tabulky (nejsilnější)
  B) První větu sekce obal do **bold**
  C) Extrahuj 3 klíčové body jako číslovaný seznam
  D) Přidej § citaci jako bold inline: (§ 58 odst. 2 písm. d) ExŘ)
```

---

## VAM výstup — formát

```
## VAM REPORT — [název souboru] — [datum]

### First-page audit
[✓/✗] Každá položka s komentářem

### Sekce po sekcích
| Sekce | Gravity points | Dead zones | Score | Fix |
|-------|---------------|------------|-------|-----|
| I. Xxx | ## + bold | 0 | 4/5 | přidej tabulku |
| II. Xxx | ## only | 2 | 2/5 | DEAD ZONE — viz rescue |

### VAM skóre
Celkem: X/Y = XX% → [hodnocení]

### Top 3 priority fixes
1. [nejkritičtější fix]
2. [druhý fix]
3. [třetí fix]

### CDC gate B1
[PASS / CONDITIONAL / FAIL] — [zdůvodnění]
```

---

## Recepty pro nejčastější dead zones

### "Zákonná argumentace" dead zone

Problém: 3 odstavce § citací bez vizuálního kotvy.

Fix:
```markdown
**Klíčové § (shrnutí):**
| § | Obsah | Aplikace |
|---|-------|----------|
| § 58 odst. 2 písm. d) ExŘ | zásada subsidiarity | prodej = ultima ratio |
| nález IV. ÚS 314/09 | obydlí = chráněno | nelze bez ověření EP |
```

### "Skutkový stav" dead zone

Problém: Chronologie jako čistý text.

Fix: přidej odrážkový časový přehled:
```markdown
**Chronologie:**
- **13. 1. 2026** — smrt Lukáše; exekuční návrh 20 dní po pohřbu
- **2. 2. 2026** — EP vydán; celá pohledávka zablokována
- **18. 6. 2026** — soud rozhodl bez ověření aktuálního stavu EP
```

### "Petit je pohřbený" problém

Problém: Petit na straně 3+, zakopán za argumentací.

Fix: Přidej preview petitu hned za "Vážený soude,":
```markdown
**Navrhuji,** aby soud exekuci prodejem nemovitostí **odložil** do doby,
než bude ověřen stav EP přikázáním pohledávky z účtu (č.j. 213 EX 31/26-19).
Důvody jsou rozvedeny níže.
```

---

## Copy-to-Judgment review

Nový review typ (Tom direktiva 2026-07-04). Jeden test, který VAM neměří:

> **Jak snadno lze tuto část zkopírovat do soudního rozhodnutí?**

Soudce většinou petit nepřepisuje — *upravuje*. Čím víc petit připomíná strukturu usnesení, tím menší práci má soudce a tím vyšší pravděpodobnost převzetí.

### Checklist (5 bodů)

```
□ Petit začíná frází shodnou s formulací usnesení?
  ("Navrhovatel navrhuje, aby soud vydal toto / rozhodl, že:")
□ Výroky jsou číslovány I., II., III. jako výroky usnesení?
□ Výroku obsahuje konkrétní jméno, datum, rozsah (ne "přiměřeně", "vhodně")?
□ Subsidiární výrok je zřetelně oddělen od primárního?
□ Vizuální přechod: soudce vidí strukturu PŘED čtením obsahu?
```

### Vizuální přechod — vzor (Lex Atomic princip)

```markdown
Navrhovatel navrhuje, aby soud vydal toto

**P R O Z A T Í M N Í   R O Z H O D N U T Í:**

**I.**
[primární výrok — kdo, co, jak, kdy]

**II.**
[povinnost druhé strany]

*Subsidiárně* k výroku I.: ...
```

**Efekt:** mozek přepne režim ("teď čtu výrok, ne odůvodnění"), oko skočí na I./II. okamžitě, soudce vidí co může převzít.

**Gravitace:** tučný nadpis s mezerami (`P R O Z A T Í M N Í`) = jeden z nejsilnějších vizuálních anchorů v dokumentu.

### Skóre

| Splněno | Hodnocení |
|---------|-----------|
| 5/5 | Copy-ready — soudce může převzít bez přepisu |
| 3–4/5 | Dobré — drobná úprava |
| < 3/5 | Reformat — petit není strukturálně připraven k převzetí |

---

## Integrace s CDC gates

| CDC Gate | VAM návaznost |
|----------|--------------|
| **B1 Scan** | VAM% ≥ 85 → B1 PASS |
| **B2 Flow** | dead zones = flow problem |
| **A1 Petit** | first-page audit: petit viditelný? + Copy-to-Judgment ≥ 3/5 |
| **C6 RTS** | VAM report = součást visual check (TIME lock) |

**Doporučení:** spusť VAM před každým CDC gate checkem B-bloku. Copy-to-Judgment review jako součást A1 Petit gate.

---

## Related

- `lg13-skills:writing-doc` — § verifikace + CDC gates + no-markers rule
- `lg13-skills:doc-polish` — automatizovaný polish loop
- `lg13-skills:legal-total-analysis` — full 14-lock CDC analýza
- `lg13-skills:locks-workflow` — kde VAM vstupuje (B1, TIME lock visual check)
- Vzor B1 PASS: `F44/01_odvolani_F39_F44.8.md` (14/14 ✅)
