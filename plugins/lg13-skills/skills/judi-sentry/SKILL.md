---
name: judi-sentry
description: Use when searching for relevant Czech court judgments (ÚS/NS), linking diamond findings to specific cases, or building/querying the judikát index from RTF files in ChatGPT_export/.
---

# judi-sentry — Judikát index + search + diamond linker

## CO DĚLÁ

Indexuje 68 RTF judikátů z `ChatGPT_export/` → prohledatelný JSON index.
Linkuje diamond findings na konkrétní ÚS/NS rozhodnutí.

**Index:** `judi_library/judi_index.json` (3.9 MB, 68 entries, pre-built)
**Script:** `scripts/judi_sentry.py`

---

## PŘÍKAZY

### Build index (jen při přidání nových RTF)

```bash
python scripts/judi_sentry.py build
```

### Search

```bash
python scripts/judi_sentry.py search "asistovaný styk" --top 5
python scripts/judi_sentry.py search "nejlepší zájem dítěte" --top 3
python scripts/judi_sentry.py search "§ 867" --case 3-2271
```

### Show judikát

```bash
python scripts/judi_sentry.py show 3-2271-25
python scripts/judi_sentry.py show 3-2271-25 --full
```

### Link diamonds

```bash
python scripts/judi_sentry.py link L:/LG13/runtime/diamonds/diamonds_legal_<TS>.json
```

Output: `judi_library/judiamonds_<TS>.json`

---

## KLÍČOVÉ JUDIKÁTY

| ID | Případ | Relevance |
|----|--------|-----------|
| 3-2271-25 | III. ÚS 2271/25 (29.10.2025) | Styk rodiče odmítaného dítětem; §2b/F38 bod 23 |
| 2-2469-25 | II. ÚS 2469/25 | Nejlepší zájem dítěte — principy |
| 2-2960-19 | II. ÚS 2960/19 | Asistovaný styk — rozsah a formy |
| 1-2891-24 | I. ÚS 2891/24 | Čl. 3 ÚMLD participační práva dítěte |

---

## PIPELINE POZICE

```
ChatGPT_export/*.rtf  →  judi-sentry build  →  judi_index.json
                                                     ↓
diamonds_legal_*.json  →  judi-sentry link  →  judiamonds_*.json
                                                     ↓
                                          diamond-to-matrix / F38 §4 citace
```

---

## PRAVIDLA

- Index je pre-built — **nespouštěj build** pokud nepřibyly nové RTF
- Search je case-insensitive substring (CZ locale aware přes striprtf)
- `find_case_refs_in_text` normalizuje: "III. ÚS 2271/25" → "3-2271-25"
- STOP #1452 — výstupy jsou READ-ONLY návrhy; aplikovat jen po Tom GO

## KONVENCE SLOŽEK (per-dokument, Tom direktiva 2026-07-08)

Pro každý F-dokument, který cituje judikaturu, drž RTF ve dvou oddělených složkách vedle sebe (např. `F50/`):

- **`<F>/judi_to_study/`** — všechny stažené/rešeršované RTF k danému dokumentu (research corpus, nemusí být použity)
- **`<F>/used_judi/`** — jen RTF těch judikátů, které dokument skutečně cituje ve finálním textu. Doplň při každé verzi, kde přibyla/ubyla citace. Volitelně zabal do `<F>/used_judi_<F>.zip` pro předání advokátovi spolu s PDF/MD/TXT.

Starší dokumenty mohou mít jen `<F>/judi/` (bez rozlišení) — při další práci na nich zvaž přejmenování na `judi_to_study/` a založení `used_judi/`, ale nepřejmenovávej za běhu bez potřeby (rozbiješ relativní odkazy ve starých verzích).

---

## RELATED

- `diamond-sentry` — generuje diamonds.json (vstup pro `link`)
- `diamond-to-matrix` — spotřebuje judiamonds → CHANGE_MATRIX
- `scripts/tests/test_judi_sentry.py` — 14 testů, vše passing
- `judi_library/judi_index.json` — pre-built index (68 judikátů)
