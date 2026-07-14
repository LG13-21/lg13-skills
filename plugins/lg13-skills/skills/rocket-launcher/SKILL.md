# rocket-launcher — ISDS canonical launcher (REÁLNĚ ODESÍLÁ, jedno potvrzení)

## CO DĚLÁ

Spravuje ISDS rocket launcher engine (`isds_rocket_<FC>.py`) pro aktuální F-cyklus, generovaný
z **CANONICAL ROCKET LAUNCHER TEMPLATE v1** (2026-07-11). Šablona je společná pro všechny F-cykly
(F42–F53+) — pro nový cyklus se soubor zkopíruje a upraví jen blok KONFIGURACE, architektura se
nemění.

**Launcher REÁLNĚ ODESÍLÁ** přes `isds_sender.py --send --confirm`. Nejde o prepare-only nástroj.

## JEDNO POTVRZENÍ, NE DVĚ

**STOP ORDER #1452 je naplněn v okamžiku, kdy Tom napíše `LAUNCH` a zadá délku time capsule —
na úplném začátku. Od tohoto bodu se už NIC dalšího nezadává.** Po doběhnutí time capsule se
zásilka **odešle automaticky**, pokud je finální re-check GREEN.

**Toto je záměrně jinak, než jak launcher fungoval dřív** (do 2026-07-11): starší verze
po doběhnutí capsule ještě žádaly druhé ruční potvrzení (typicky přesnou frázi typu
`KONEC STOP`). To je **chyba, kterou tahle verze skillu opravuje** — je to přesně ta
"raketa co čeká na rampě, dokud někdo náhodou nejde kolem a nezmáčkne to ručně" situace,
kterou Tom opakovaně reklamoval. Time capsule countdown *je* ten bezpečnostní gate (Tom
si sám zvolí, kolik minut chce na rozmyšlenou/kontrolu) — po jeho doběhnutí se čeká jen na
GREEN, ne na další lidský vstup.

Pokud najdeš `isds_rocket_<FC>.py`, který po doběhnutí capsule ještě žádá druhé ruční
potvrzení (`input(...)` po zprávě "Time capsule vyprsela") — **je to bug, oprav ho podle
tohoto vzoru**, ne podle staré dokumentace.

### Tok launcheru (co Tom vidí, když spustí .bat)

1. **Banner** — DS adresát, sp. zn., hlavní PDF + velikost, seznam příloh.
2. **Pre-flight baterie** — deterministické kontroly (soubory existují, ZIP obsah přesně
   sedí, count-guard, DATOVKA adresát, forenzika bez interních markerů, PDF freshness,
   lock-certifikát).
3. **Zobrazí text zprávy** (DATOVKA_TEXT.md) a seznam příloh s velikostmi.
4. **LAUNCH CONFIRM** — Tom napíše `LAUNCH`, cokoliv jiného = abort.
5. **Capsule minuty** — Tom zadá počet minut (Enter = default z konfigurace, typicky 120).
   **Tímto krokem je zadávání u konce.**
6. **Odpočet** s periodickým re-checkem (default 45 s) — progress bar `T-MM:SS GREEN
   (NIC SE NEODESILA)`. Regrese během odpočtu (baterie spadne na RED) = automatický ABORT,
   je třeba dokument opravit a launcher spustit znovu od začátku.
7. **T-0** — finální re-check. Pokud GREEN: **odešle se automaticky**, žádný další prompt.
   Pokud RED: ABORT, žádné "ready" bez opravy.
8. **Potvrzení o odeslání** se zapíše na **4 místa** (aby to zachytil wake_signal/CGE
   monitor a legal instance se to dozvěděla bez nutnosti to psát ručně):
   - `L:/LG13/runtime/ops/comms_log.jsonl` (append)
   - `F<FC>/cdc/ODESLANO_<FC>_<ts>.json`
   - `ChatGPT_export/ODESLANO_<FC>_<ts>.json` (chytí ho CGE folder watcher)
   - `comm/komunikace/ds_odeslane/<FC>_<ts>.json`

### Pre-flight baterie (deterministické kontroly, žádné AI volání)

| Kontrola | Co ověří |
|----------|----------|
| **souborů** | hlavní PDF + DATOVKA + všechny přílohy fyzicky existují |
| **count-guard** | počet příloh v DATOVKA == počet fyzických příloh == očekávané |
| **DATOVKA adresát** | DS adresáta + sp. zn. přítomny |
| **forenzika** | zdroj bez interních markerů (DRAFT/verze/cesty/STOP) |
| **PDF freshness** | hlavní PDF byl renderován PO poslední editaci zdroje |
| **lock-certifikát** | pokud je vyžadován pro daný F-cyklus (viz `LOCK_CERT` v konfiguraci) |

---

## KONFIGURACE (blok na začátku engine, jediné co se mění per F-cyklus)

```python
FC                   = "F<N>"
DOC_MD               = Path(".../DATOVKA_TEXT.md")
MAIN_PDF             = Path(".../01_<nazev>_F<N>.<verze>.pdf")   # VŽDY aktuální verze!
DS_ADRESAT           = "..."
SP_ZN                = "0 P 29/2026"
TO_HANDS             = "..."
SUBJECT              = "..."
ATTACHMENTS          = [MAIN_PDF]   # MAIN_PDF musí být PRVNÍ v seznamu
LOCK_CERT            = Path(".../UNLOCK_....md")
DEFAULT_CAPSULE_MIN  = 120
RECHECK_EVERY_SEC    = 45
```

**Po každém version bumpu dokumentu (vX → vX+1) NEZAPOMEŇ přepsat `MAIN_PDF`** v konfiguraci
na novou verzi a v `ATTACHMENTS` — jinak launcher odešle starou verzi bez nejnovějších úprav.
(Incident 2026-07-11: F53 v3→v4→v5 měněno, `MAIN_PDF` v launcheru se musí ručně přepsat při
každé verzi — dokud nebude engine číst `meta.json.aktualni_soubor` automaticky.)

---

## VOLÁNÍ

```
/lg13-skills:rocket-launcher
```

Spusť po každém F-cycle bumpu nebo změně PDF/příloh — přegeneruje `.bat` a ověří, že
`MAIN_PDF` v konfiguraci ukazuje na aktuální verzi.

---

## KDY VOLAT

- Po každém renderu hlavního PDF (velikost/obsah se mění)
- Po version bumpu (vX → vX+1) — **ověřit MAIN_PDF v konfiguraci**
- Po změně příloh
- Kdykoliv Tom chce aktuální `.bat` na ploše

---

## HARD RULES

- **Launcher REÁLNĚ ODESÍLÁ** — přes `isds_sender.py --send --confirm`. Není prepare-only.
- **JEDNO potvrzení, ne dvě.** LAUNCH + capsule minuty na začátku = jediný a plný souhlas.
  Po T-0 s GREEN se odesílá automaticky, bez druhého ručního gate.
- **ASCII-only stdout** v engine (banner/rocket/baterie) — diakritika v CMD dělá „?"/boxy.
  Diakritika smí být jen v DATOVKA_TEXT.md a ve výsledném PDF.
- **`chcp 65001 >nul`** VŽDY na prvním řádku `.bat`.
- DS adresy hardcoded v konfiguraci — neměnit bez explicitní instrukce.
- Bat soubor vždy PŘEPISUJE — nikdy neappenduje.
- **MAIN_PDF musí být PRVNÍ v `ATTACHMENTS`** — jinak odejdou jen přílohy bez hlavního
  dokumentu (viz `feedback_isds_rocket_main_pdf_bug` — incident F45 2026-07-03).
- **Přílohy VŽDY jedno `--attach` volání se všemi soubory najednou** —
  `cmd += ["--attach"] + [str(a) for a in ATTACHMENTS]`. NIKDY smyčka
  `for att in ATTACHMENTS: cmd += ["--attach", str(att)]` — `isds_sender.py`
  definuje `--attach` jako `nargs="*"`, takže opakovaný flag argparse **přepíše**,
  ne přidá — odejde jen POSLEDNÍ příloha ze seznamu. Confirmation JSON přitom
  hlásí správný počet (čte Python list, ne co skutečně došlo na ISDS) — bug se
  tak neprojeví v logu, jen ve skutečně doručené zprávě. Recidiva stejného bugu
  z F39 (2026-06-19): postihla F52 (2026-07-13), kde odešla jen 1 příloha ze 4,
  hlavní PDF chybělo — musel se poslat opravný dodatek. Viz
  `reference_isds_attach_nargs_trap.md`.
- Potvrzení o odeslání se zapisuje na 4 místa (viz výše) — nikdy nepřeskakovat, na tom
  stojí automatická notifikace legal instance.

**Po každé úpravě/kopii canonical template ověř regresním testem:**

```
python scripts/test_rocket_launcher_no_second_gate.py
```

Test kontroluje DVĚ věci: (1) žádný druhý manual gate mezi T-0 a odesláním, (2) žádná
per-item `--attach` smyčka (repeated-flag bug výše). Selže → oprav podle vzoru
v `F53/isds_rocket_F53.py`. Přidej nový launcher do `CANONICAL_TEMPLATE_SCRIPTS`
v testu, jakmile ho zkopíruješ pro další F-cyklus.

---

## RELATED

- `F53/isds_rocket_F53.py` — referenční implementace canonical template v1 (2026-07-11,
  opraveno o odstranění druhého manual gate)
- `scripts/test_rocket_launcher_no_second_gate.py` — regresní test proti návratu bugu
- Skill `isds-ship-with-capsule` — plný ISDS pipeline (DS verify, lock check, capsule)
- Skill `locks-workflow` — 5-locks schvalovací workflow (LEGAL→STRAT→CHATGPT→TIME→TOM→T002)
- `feedback_isds_rocket_main_pdf_bug` (memory) — MAIN_PDF pořadí v ATTACHMENTS
