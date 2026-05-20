---
name: locks-workflow
description: >
  Řídí 5-locks schvalovací workflow pro soudní a formální podání v systému LG13.
  Verze 2 (Tom directive 2026-05-17): LEGAL → STRAT → TIME → TOM → T002.
  Legal max 3 kroky. Strat all control + ChatGPT review povinný. TIME = web up + visual OCR.
  Tom read final → KONEC STOP → T002 send.

  VŽDY použij tento skill, když uživatel zmíní:
  lock strat, lock legal, lock t002, lock tom, lock send, lock status, lock check,
  lock cancel, lock init, 5 locks, schvalovací workflow, zámky podání, meta.json locks,
  STRAT/LEGAL/T002/TOM/CAPSULE check, F10 konvence, S+/L+/O+/T+/C+ notace,
  time capsule podání, forenzní check dokumentu, compliance check souborů,
  visual check, ChatGPT review, total analysis, fast read, web up.
---

# locks-workflow — 5-locks schvalovací workflow (V2)

## POŘADÍ LOCKŮ (V2 — Tom directive 2026-05-17)

```
LEGAL → STRAT → CHATGPT → TIME → TOM → T002
```

**Změna oproti V1:** ChatGPT je samostatný lock (ne součást STRAT). Pořadí: Legal základ, Strat all control + atoms check, ChatGPT nezávislý visual+fast read, TIME = web+OCR, Tom jen "read final", T002 send po KONEC STOP.

```
F17.0_ASAP.md               ← výchozí, žádný lock
F17.1_L+_ASAP.pdf           ← LEGAL PASS
F17.2_L+S+_ASAP.pdf         ← STRAT PASS
F17.3_L+S+G+_ASAP.pdf       ← CHATGPT PASS (G = GPT)
F17.4_L+S+G+I+_ASAP.pdf     ← TIME PASS + web live + OCR (I = tIme)
F17.5_L+S+G+I+T+_ASAP.pdf   ← TOM read final
SENT_F17.5_…_DM{id}.pdf     ← T002 odesláno
```

---

## LOCK 1 — LEGAL (max 3 kroky)

Spouštění: `lock legal [pass|fail]`

### L1 — Právní kontrola
- Paragrafy správné a aktuální (novela 268/2025 Sb.)
- Petit konkrétní, ne abstraktní
- Judikatura citovaná ověřena (III. ÚS 409/23, I. ÚS 3350/22, ESLP Sahin, Süß)
- Žádné interní markery v textu (NEPOSÍLAT, DRAFT, TODO, P1-X, versioning)
- Identifikace stran: jméno, nar., DS všech účastníků
- DM zpětvzetí zmíněno pokud meta.json obsahuje dm_zpětvzetí

### L2 — Total analysis (self-contained check)
- Dokument čitelný bez externích referencí
- Žádné bundle references ("viz Bundle 1", "doporučené pořadí čtení")
- Žádná meta-routing vrstva, žádný framing
- Decision packet: petit str. 1, fakta, proporcionalita, právní opora, přílohy

### L3 — 5 LOCKS check
- Splňuje podmínky tohoto workflowu
- meta.json aktualizován (`locks.legal_check`)
- CHANGELOG.txt append

**LEGAL PASS** → předat STRAT.

---

## LOCK 2 — STRAT (all control)

Spouštění: `lock strat [pass|fail]`

### S1 — Risk assessment
- Matice rizik: RED / AMBER / GREEN
- Co může soudu vadit nebo být zneužito protistranou
- Timing: délka přerušení, přání nezletilého, judikatura ESLP

### S2 — Compliance check
- Formální náležitosti procesního podání
- Žádné nepřiznané informace (nezveřejněná jména, medicínská data)
- Způsobilost k podání přes ISDS

### S3 — Red team
- "Co řekne ZZ / Flaška když tohle dostane?"
- "Co řekne soud při prvním přečtení?"
- "Je tam cokoliv co může být obráceno proti navrhovateli?"

### S4 — Legal strategy + atoms alignment
- Je to vůbec B1 (§ 452 ZŘS)? Splňuje podmínky § 452?
- Je podání v souladu s tím co Tom říkal v ChatGPT vláknech a atomech?
- Je přizpůsobeno cíli (obnovit styk, ne eskalovat konflikt)?
- **POVINNÁ otázka:** "Je to jak Tom chtel a v atomech rikal?" → musí být ANO

**STRAT PASS** → předat CHATGPT.

---

## LOCK 3 — CHATGPT (vlastní lock)

Spouštění: `lock chatgpt [pass|fail]`

Legal spustí ChatGPT total analysis v Legal projektu (skill `chatgpt-ask`):

1. **Total analysis** — argumenty, struktura, věrohodnost, §-koherence
2. **Visual readability** — PDF vypadá jako soudní dokument? Tabulky? Font? Stránkování?
3. **Fast read 30s** — co soudce vidí prvních 30 sekund? Petit okamžitě čitelný?
4. **Red team / oponent** — co by řekla druhá strana (ZZ / Mgr. Flaška)?
5. **Bundle check** — zbytky bundle architektury? Framing? Pořadí čtení?

Výstup: `GO_SHIP` / `CONDITIONAL_GO` (podmínky = blocker před TIME) / `NO_GO`

**ChatGPT podmínky = blocker** — dokud nejsou zapracovány, TIME LOCK nelze udělit.

**CHATGPT PASS** → předat TIME.

---

## LOCK 4 — TIME + WEB UP + OCR

Spouštění: `lock time [pass|fail]`

1. Rebuild PDF (finální verze z MD zdrojů)
2. Web update: `http://localhost:8081` — živý náhled
3. **Visual OCR check**: screenshots / fotky — vypadá to jako dokument k soudu?
4. ZIP sestavit: čistý inventář, pouze `priloha*.pdf` + finální PDF
5. Time capsule: 5 min (ASAP) nebo 60 min (standard)

**TIME PASS kritérium:** PDF OK, web live, visual check PASS.

---

## LOCK 5 — TOM (read final)

Tom přečte finální verzi — PDF nebo web. Žádný formální approval formulář.

Tom říká:
- "OK" / "pošli" / "KONEC STOP" → T002 může odeslat
- Feedback na konkrétní bod → vrátit na příslušný lock (L nebo S)

**TOM PASS:** Explicitní "OK" nebo "KONEC STOP".

---

## LOCK 6 — T002 (send)

Podmínka: Tom KONEC STOP.

1. Sestavit čistý ISDS balíček: `priloha*.pdf` + finální PDF
2. **NIKDY:** `.md`, `.json`, CHANGELOG, interní soubory, risk assessment
3. Odeslat přes ISDS
4. DM ID zaznamenat, meta.json + CHANGELOG aktualizovat

---

## HARD RULES (nezměnitelné)

1. **Pořadí LEGAL → STRAT → CHATGPT → TIME → TOM → T002** — nepředbíhat
2. **Tom musí říct KONEC STOP** explicitně — T002 jinak neodesílá nikdy
3. **Žádné interní markery** v dokumentu pro soud
4. **Visual OCR check povinný** v TIME locku — PDF jako fotky, tabulky, záhlaví, podpis
5. **CHATGPT je samostatný lock** — nelze sloučit se STRAT, GO_SHIP/CONDITIONAL_GO/NO_GO
6. **ChatGPT podmínky = blocker** — dokud nezapracovány, TIME nelze udělit
7. **Legal max 3 kroky** — L1+L2+L3, žádné elaborace navíc
8. **"Je to jak Tom chtel?"** — S4 STRAT musí odpovědět ANO

---

## Co se nesmí opakovat

- Bundle architektura v PO (framing, pořadí čtení, B1/B2 separator)
- Tabulky jako plain text v PDF
- Datum/dní inconsistence
- Interní markery v odeslaném dokumentu (incidenty 15.4., 16.4.2026)
- Fast-ship bez visual check
- STRAT approveuje bez ChatGPT review (S5)

---

## Příkazy (CLI)

```bash
lock legal pass --folder {cesta}        # L1+L2+L3 OK
lock strat pass --folder {cesta}        # S1-S4 OK
lock chatgpt pass --folder {cesta}      # GO_SHIP nebo CONDITIONAL_GO + podmínky zapracovány
lock time pass --folder {cesta}         # PDF rebuilt, web up, OCR visual OK
lock tom submit                          # Dej Tomovi k přečtení
lock send --konec-stop                   # T002 odešle po KONEC STOP
lock status --folder {cesta}            # Stav všech locků
lock cancel --reason "…"               # Zrušit
```

## meta.json schema (V2 key fields)

```json
{
  "stav": "waiting_legal|waiting_strat|waiting_chatgpt|waiting_time|waiting_tom|sending|sent|cancelled",
  "aktualni_verze": "F17.3_L+S+G+_ASAP",
  "locks_v2": {
    "legal":   {"status": null, "ts": null, "notes": ""},
    "strat":   {"status": null, "ts": null, "notes": ""},
    "chatgpt": {"status": null, "ts": null, "verdict": null, "conditions": []},
    "time":    {"status": null, "ts": null, "web_url": null, "ocr_checked": false},
    "tom":     {"status": null, "ts": null, "signal": null}
  }
}
```

## Referenční soubory

- `references/incidents.md` — incidenty 15.4., 16.4.2026
- `L:/GitHub/legal-ship-2026/docs/orchestration/5_LOCKS_WORKFLOW_V2.md` — plný popis V2
- `scripts/forensics.py` — interní markery + inventář příloh
- `scripts/audit.py` — meta.json atomic read/write
