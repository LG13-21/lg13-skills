# diamond-pick — Argumentační diamond picking z právních dokumentů

## PURPOSE

Automatizuje to co Tom dělá ručně v ChatGPT: čte drafty, exporty, poznámky →
extrahuje nejsilnější argumenty ("diamonds") → filtruje KEEP/DROP/REFORMULATE →
výstup jako CHANGES_MATRIX.md v Lex Atomic formátu.

Stejný výsledek jako ChatGPT session v g-p-6a0d878891f08191a6bce18ba3fbfc0c,
ale bez ruční práce.

---

## PARAMETRY

| Parametr | Default | Popis |
|----------|---------|-------|
| `src` | povinné | Cesta k zdrojovému dokumentu (MD/PDF) NEBO adresář |
| `notes` | optional | Poznámky / ChatGPT export / Tom poznamky.txt |
| `target` | `CHANGES_MATRIX.md` | Výstupní soubor (append nebo create) |
| `doc-type` | auto-detect | `AS` \| `PO` \| `F` \| `vyjadreni` |
| `issue` | optional | GitHub issue číslo — výsledek se zapíše jako komentář |
| `mode` | `full` | `full` = celá matrix \| `delta` = jen nové oproti existující matrix |

---

## EXECUTION

### 1. Příprava vstupů

```bash
python L:/LG13/app/agent/skills/diamond_pick.py \
    --src "L:/GitHub/legal-ship-2026/F23/src/07_Vyjadreni_AS_Wave1a_F23.md" \
    --notes "L:/GitHub/legal-ship-2026/ChatGPT_export/Tom poznamky.txt" \
    --target "L:/GitHub/legal-ship-2026/F24/CHANGES_MATRIX.md" \
    --issue 46
```

### 2. Co script dělá

1. Přečte zdrojový dokument (`--src`)
2. Přečte poznámky (`--notes`) pokud existují — ChatGPT export nebo plain text
3. Pokud `--issue` — přečte komentáře z issue pro kontext
4. Pošle do Claude (haiku — levný) s tímto promptem:
   - Extrahuj nejsilnější argumenty (diamonds)
   - Pro každý: KEEP / DROP / REFORMULATE + důvod
   - Dodej Lex Atomic formulaci (1 věta, faktická, neútočná, procesní framing)
5. Výstup: CHANGES_MATRIX.md blok + volitelně GitHub issue komentář

### 3. Přímé volání ze skriptu (bez parametrů)

```bash
# Auto-detect: najde nejnovější F* adresář + Tom poznamky.txt
python L:/LG13/app/agent/skills/diamond_pick.py --auto
```

---

## OUTPUT FORMAT (CHANGES_MATRIX.md blok)

```markdown
## DIAMOND MATRIX — [doc-type] [timestamp]

### KEEP — aplikovat do dokumentu

| # | Diamond | Lex Atomic formulace | Síla |
|---|---------|---------------------|------|
| D1 | Absence incidentů | „Za 9 let kontaktu nebyl zaznamenán žádný incident." | ★★★ |
| D2 | Časová asymetrie tvrzení | „Tvrzení se objevují strukturálně až po přerušení kontaktu, nikoli během něj." | ★★★ |

### DROP — vyhodit z dokumentu

| # | Diamond | Důvod vyhození |
|---|---------|---------------|
| X1 | Telefon není náhrada | Nevhodný framing — kontakt blokován, ne jen nedostatečný |

### REFORMULATE — přeformulovat

| # | Původní | Nová formulace | Důvod |
|---|---------|---------------|-------|
| R1 | „plná právní kapacita" | „věkově přiměřená schopnost formulovat přání" | Přestřeleno pro 9leté dítě |
```

---

## LEX ATOMIC PRAVIDLA (per Tom workflow)

- Každý diamond = 1 věta, max 2
- Faktická, ne emocionální
- Procesní framing (soud, zákon, řízení) > osobní útok
- Neútočná — „strukturálně se jeví" > „záměrně lže"
- §§ citovat jen pokud posilují, ne jako berla
- Silná věta stojí sama — nepotřebuje uvozovací komentář

---

## WORKFLOW S ISSUES

```
/diamond-pick src=F23/src/07_... notes=Tom_poznamky.txt issue=46
    ↓
script čte src + notes + #46 komentáře
    ↓
Claude haiku extrahuje diamonds
    ↓
CHANGES_MATRIX.md append
    ↓
gh issue comment #46 s výsledkem (jen pokud --issue)
    ↓
Tom review → GO → aplikace na novou F verzi
```

---

## SKILL EXECUTION (interní — bez skriptu)

Pokud `diamond_pick.py` neexistuje nebo selže, proveď přímo:

1. Přečti `--src` soubor
2. Přečti `--notes` pokud existuje
3. Přečti issue komentáře: `gh issue view <N> --repo LG13-21/legal-ship-2026 --comments`
4. Proveď diamond picking analýzu (viz LEX ATOMIC PRAVIDLA)
5. Zapište do `--target` souboru (append s timestamp blokem)
6. Pokud `--issue`: `gh issue comment <N> --repo LG13-21/legal-ship-2026 --body "..."`

---

## CHATGPT ALTERNATIVA

Pokud chceš diamond picking přes ChatGPT místo Clause:

1. Otevři ChatGPT s `/github` příkazem (dá přístup k legal-ship-2026 repo)
2. Použij hotové prompty z: `skills/diamond-pick/prompts/chatgpt_diamond_pick.md`
3. Vzorové prompty: základní picking, delta picking, PO picking, kompletní session

```
# Rychlý start v ChatGPT:
/github
Přečti https://github.com/LG13-21/legal-ship-2026/blob/main/F24/CHANGES_MATRIX.md
a udělej diamond picking pro [nový soubor nebo URL]
```

---

## RELATED

- Skill `plan-to-git` — vytvoří guided review issue pro výsledky
- Skill `issue-sync` — přečte issue kontext před picking
- `L:/GitHub/legal-ship-2026/F24/CHANGES_MATRIX.md` — vzorový výstup
- ChatGPT vzor: g-p-6a0d878891f08191a6bce18ba3fbfc0c (Tom's diamond GPT)
