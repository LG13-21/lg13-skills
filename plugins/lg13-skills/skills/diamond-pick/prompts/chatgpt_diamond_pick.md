# ChatGPT Diamond Picking Prompt

> **Použití:** Zkopíruj celý blok níže do ChatGPT.
> Začni příkazem `/github` aby měl ChatGPT přístup k repo.
> Pak vlož odkaz na soubor nebo issue.

---

## PROMPT — Základní diamond picking

```
/github

Proveď diamond picking pro právní dokument z tohoto repo:
https://github.com/LG13-21/legal-ship-2026/blob/main/[CESTA_K_SOUBORU]

Kontext z issues:
https://github.com/LG13-21/legal-ship-2026/issues/[ČÍSLO]

Pravidla:
- Každý diamond = 1–2 věty, faktické, procesní framing
- Neútočné: "strukturálně se jeví" > "záměrně lže"
- §§ jen pokud posilují argument, ne jako berla
- Silná věta stojí sama bez uvozovacího komentáře

Výstup jako tabulka:

| # | Diamond | Lex Atomic formulace | KEEP/DROP/REFORMULATE | Síla ★★★ |
```

---

## PROMPT — Delta picking (jen nové oproti existující matrix)

```
/github

Existující CHANGES_MATRIX.md:
https://github.com/LG13-21/legal-ship-2026/blob/main/F24/CHANGES_MATRIX.md

Nový zdrojový materiál:
[vlož text nebo odkaz na ChatGPT export / Tom poznamky.txt]

Najdi diamonds které ještě NEJSOU v matrix. Stejný formát jako výše.
Nepřidávej duplicity.
```

---

## PROMPT — PO diamond picking (Předběžné opatření)

```
/github

Aktuální verze PO dokumentu:
https://github.com/LG13-21/legal-ship-2026/blob/main/[F*/src/PO_soubor.md]

Referenční verze (základ z 15–17.5.):
https://github.com/LG13-21/legal-ship-2026/blob/main/F17_0/[soubor.md]

Strategický kontext (přečti):
https://github.com/LG13-21/legal-ship-2026/issues/46

PO pravidla:
- PO = urgence + izolační újma Matoušovi (NE přelitigování nebezpečnosti — to řeší F23)
- WhatsApp verbatimy, OPL, §132 → sem ANO (na rozdíl od F23)
- Emocionálně silné, procesně „dirty battlefield" je OK pro PO
- Cíl: weekend judge, rychlé rozhodnutí

Výstup: diamond tabulka + návrh struktury PO (sekce v pořadí síly argumentu)
```

---

## PROMPT — Kompletní session (Tom workflow)

```
/github

Jsem navrhovatel v rodinném sporu (sp. zn. 0 P 29/2026, OS České Budějovice).
Připravuji odpověď na doporučení soudu k AS + PO §452.

Přečti tyto soubory:
1. Aktuální draft: https://github.com/LG13-21/legal-ship-2026/blob/main/[SOUBOR]
2. Moje poznámky: https://github.com/LG13-21/legal-ship-2026/blob/main/[Tom_poznamky.txt]
3. Issue kontext: https://github.com/LG13-21/legal-ship-2026/issues/46

Úkol:
1. Extrahuj diamonds (KEEP/DROP/REFORMULATE tabulka)
2. Navrhni novou strukturu dokumentu (pořadí argumentů)
3. Napiš hotový draft v Lex Atomic formátu

Výstupní formát = přesně jako CHANGES_MATRIX.md:
https://github.com/LG13-21/legal-ship-2026/blob/main/F24/CHANGES_MATRIX.md
```

---

## RYCHLÉ ZKRATKY

| Co chceš | Příkaz |
|----------|--------|
| Diamond picking z draftu | `Přečti [URL] a udělej diamond picking` |
| Porovnat dvě verze | `Porovnej diamonds v [URL1] vs [URL2]` |
| Jen DROP kontrola | `Co bych měl vyhodit z [URL]? Důvody.` |
| Aplikovat matrix | `Aplikuj CHANGES_MATRIX.md [URL] na dokument [URL2]` |
