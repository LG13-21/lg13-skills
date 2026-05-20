# Dokumentované incidenty — poučení pro forenzní check

Tento soubor obsahuje reálné incidenty z pilotního provozu (2026-04-15/16).
Slouží jako referenční bod: pokud si nejsi jistý proč je nějaké pravidlo tvrdé, tady najdeš proč.

---

## Incident 1 — 2026-04-15 (DM 1680642296)

**Co se stalo:** Bylo odesláno doplnění návrhu se slovy „NEPOSÍLAT" viditelně v hlavičce.
Soud přijal podání. Tom musel obratem odeslat zpětvzetí (DM 1680755033, doručeno 23:42).

**Vzor v dokumentu:**
```
<!-- NEPOSÍLAT — draft pro interní review -->
```

**Proč je to problém:** Soud toto vidí jako součást podání. Interní poznámka odhaluje, že
si Tom nebyl jistý obsahem. Oslabuje důvěryhodnost celého podání.

**Jak forenzika detekuje:** Regex `NEPOSILAT|NEPOSLAT|NEPOSÍLAT` v prvních 30 řádcích.

---

## Incident 2 — 2026-04-16 (verze v8.0)

**Co se stalo:** Ve verzi v8.0 (před opravou strat instance) zůstala v hlavičce věta:
```
„faktická oprava bodu 18 — tělo v ČR, nikoli AT"
```

**Proč je to problém:** Soud by tuto větu přečetl jako: „v předchozím podání jsme napsali
nepravdu a nyní to opravujeme." Přiznání fabrikace. Okamžitě diskredituje Toma jako
navrhovatele. Mohlo vést k zamítnutí i trestnímu oznámení.

**Jak forenzika detekuje:** Regex `faktická oprava|factual correction|faktická korekce|\[OPRAVA\]|\[FIX\]`
v prvních 30 řádcích.

**Opraveno v:** v8.1 — strat instance smazala celou řádku z hlavičky. Věta zůstala
*pouze* v CHANGELOG.txt jako interní poznámka.

**Klíčové pravidlo:** Cokoliv co popisuje historii verzí, opravy chyb, interní stav
patří VÝHRADNĚ do `meta.json.versions[]` nebo `CHANGELOG.txt`. Nikdy do těla dokumentu.

---

## Incident 3 — ZIP balíček s interním obsahem

**Co se stalo:** Soubor `pr_vn_probl_m_p_e_o_d_t.txt` (garblované jméno, ChatGPT tmonkey
export) byl zahrnut do ZIP balíčku připraveného k odeslání soudu. Obsahoval kompletní
interní právní strategii (L01-L12 okruhy, risk assessment, všechny pozice).

**Proč je to problém:** Soud by měl přístup k celé interní strategii. Protistrany advokát
(Mgr. Flaška) by ji mohl použít. Strategická katastrofa.

**Jak forenzika detekuje:** Inventarizace ISDS balíčku — whitelist přístup.
Pouze `priloha*.pdf` a finální `F*.pdf` smí jít do ISDS. Cokoliv jiného = STOP.

---

## Obecné poučení

Všechny tři incidenty mají společného jmenovatele: **nedostatečný forenzní check před odesláním.**

Proto 5-locks workflow vyžaduje:
1. STRAT lock: první forenzní check + strategie
2. LEGAL lock: právní compliance
3. T002 lock: finální forenzní check + inventář balíčku
4. TOM lock: Tomova explicitní kontrola
5. TIME CAPSULE: povinná prodleva (5 min ASAP, 60 min ostatní)

Každý zámek je šance chytit chybu předchozího.
