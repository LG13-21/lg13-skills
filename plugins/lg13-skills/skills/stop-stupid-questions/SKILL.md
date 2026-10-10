---
name: stop-stupid-questions
description: Use when about to stop and ask Tom a small question — "mám to commitnout?", "co přesně potřebuješ?", "chceš A nebo B?", "mám pokračovat?" — or when ending a turn with an open follow-up question, or waiting for Tom's approval on a reversible step.
---

# stop-stupid-questions

Vlákno se nezastavuje kvůli drobnostem. Tom je často mimo PC, tým (legal, strat, ChatGPT) je k dispozici přes ping-pong a queue.

**Pravidlo:** Otázka, kterou může zodpovědět tým nebo rozumný default, nejde Tomovi.

## Postup před každou otázkou

1. **Vratné a levné?** (commit lokálně, test, dry-run, zápis stavu, výběr názvu/umístění) → udělej s rozumným defaultem a reportuj výsledek. Žádná otázka.
2. **Obsah / právní stránka / co potřebuje** → ping-pong legal (skill `ping-pong`).
3. **Priorita / architektura / rozsah / task** → queue nebo ping-pong strat (`instance_queue.py --send --to strat`).
4. **Second opinion / review / oponent** → `chatgpt-ask`.
5. **Nic z toho neodpoví a práce se bez odpovědi zastaví** → skill `oq` (zapsat Open Question), vezmi default a jdi na další úkol.
6. **Tomovi napřímo** jen: nevratné nebo ven směřující akce (push do veřejného repa, force, mazání dat, ISDS/email/odeslání, credentials) a situace, kdy tým neodpověděl a čekání je opravdu blokující.

Tým odpovídá asynchronně: pošli dotaz, **pokračuj v práci**, odpověď přijde přes Monitor. Nečekej.

## Red flags — STOP, zeptej se týmu místo Toma

| Myšlenka | Realita |
|---|---|
| "Mám to commitnout / pushnout lokálně?" | Commit je vratný → udělej. Veřejný push → strat. |
| "Co přesně potřebuješ?" | Přečti zadání znovu; zbylou nejasnost pošli legalovi/stratovi. |
| "Chceš A nebo B?" | Vyber doporučenou variantu, zapiš proč, jdi dál. |
| "Mám pokračovat?" | Ano. Pokračuj. |
| "Raději počkám na GO" | GO platí pro jasné vratné tasky. |
| "Tom je přece autorita" | Tom chce být rušen jen u nevratných věcí. |

## Formát reportu místo otázky

Konec odpovědi = co je hotovo + co jsem zvolil a proč (1 věta) + kdo dostal dotaz (pokud nějaký). Žádná závěrečná otázka.

## Výjimky (jediné)

Destruktivní/nevratné akce, odesílání ven, bezpečnostní rozhodnutí, a explicitní Tomův pokyn "zeptej se mě".

Violating the letter is violating the spirit: přeformulovat otázku na "doporučuji X, souhlasíš?" je pořád otázka.
