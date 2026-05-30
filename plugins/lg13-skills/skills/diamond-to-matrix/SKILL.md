---
name: diamond-to-matrix
description: "Převede diamonds.json (z diamond-sentry nebo diamond-pick) na prioritizovanou CHANGE_MATRIX. Missing pipeline piece mezi diamond extraction a aplikací změn. Triggers: 'diamond-to-matrix', 'build matrix', 'diamonds na matrix', 'prioritizuj diamonds', 'change matrix z diamonds'."
version: 1.0.0
status: stable
user-invocable: true
---

# /diamond-to-matrix — Diamonds → CHANGE_MATRIX

## CO DĚLÁ

Chybějící pipeline článek mezi:
```
diamond-sentry/diamond-pick  →  ???  →  CHANGE_MATRIX → apply
```

Vezme `diamonds.json`, ohodnotí každý diamond prioritou P0/P1/P2,
matchuje ho na sekci dokumentu a emituje `CHANGE_MATRIX_<ts>.md`.

---

## VSTUPY

```
/diamond-to-matrix                              — použij nejnovější diamonds.json
/diamond-to-matrix --diamonds <path>            — konkrétní diamonds.json
/diamond-to-matrix --latest                     — explicitně nejnovější
/diamond-to-matrix --doc <doc.md>               — cílový dokument (pro section matching)
/diamond-to-matrix --output <matrix.md>         — výstupní soubor
/diamond-to-matrix --min-score 10               — filtr (min score)
```

---

## EXECUTION

```bash
python L:/GitHub/legal-ship-2026/scripts/diamond_to_matrix.py --latest --doc <doc>
```

Nebo konkrétní soubor:
```bash
python L:/GitHub/legal-ship-2026/scripts/diamond_to_matrix.py \
    --diamonds L:/LG13/runtime/diamonds/diamonds_legal_<TS>.json \
    --doc F29/src/04_navrh_PR_F29.md \
    --output F29/analysis_cdc/auto/CHANGE_MATRIX_<TS>.md
```

---

## SCORING LOGIKA

Diamond score range (diamond_sentry): cca 4–21, medián ~7.5.

| Priorita | Score | Podmínka | Popis |
|----------|-------|----------|-------|
| P0 🔴 | ≥ 15 | nebo score ≥ 9 && recurrence ≥ 4 | Apply ASAP — blocker pro LOCK |
| P1 🟡 | ≥ 9 | nebo score < 9 && recurrence ≥ 4 | Apply v příštím F-cycle |
| P2 🟢 | < 9 | — | Backlog — DEFERRED.md |

**recurrence bonus:** ≥ 4 výskytů = upgrade o 1 úroveň (P2→P1, P1→P0).

---

## VÝSTUPNÍ FORMÁT

```markdown
# CHANGE_MATRIX — Diamond → Action

## P0 — APPLY ASAP (blocker)
| ID | Score | Výsk. | Kde | Akce |
...

## P1 — Příští F-cycle
...

## P2 — Backlog
...
```

---

## PRAVIDLA

- **STOP #1452** — matrix je READ-ONLY návrh; aplikovat jen po Tom GO
- P0 ≠ automatická aplikace — P0 = Tom musí rozhodnout prioritně
- Matrix nenahrazuje LARE/CHANGE_MATRIX workflow — doplňuje ho
- Po vygenerování: uložit do `F29/analysis_cdc/auto/` nebo vedle dokumentu

---

## RELATED

- `diamond-sentry` — generuje diamonds.json (5-stage pipeline, emergence detection)
- `diamond-pick` — single-shot extraction z jednoho souboru → diamonds.json
- `doc-polish` — spotřebuje CHANGE_MATRIX a aplikuje changes (fáze 1 targeted re-run)
- `scripts/diamond_to_matrix.py` — backing script (L:/GitHub/legal-ship-2026/scripts/)
- `CHANGE_MATRIX_*.md` — výstup v `F29/analysis_cdc/auto/` nebo vedle dokumentu

---

## PIPELINE POZICE

```
INPUT                →  EXTRACTION         →  SCORING        →  APPLICATION
ChatGPT/docs/repo       diamond-sentry         diamond-to-matrix   doc-polish
                        diamond-pick       →   CHANGE_MATRIX   →  (po Tom GO)
                        cti-cele
```
