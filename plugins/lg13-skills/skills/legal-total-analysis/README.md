# `legal-total-analysis` skill — staging build (varianta C lean)

**Stav:** Připraveno k uploadu na Tomův web legal approve tool / move do plugin marketplace.
**Datum:** 2026-04-28
**Autor:** legal instance
**Důvod stagingu:** Write permission do `C:\Users\tom\.claude\plugins\marketplaces\lg13\plugins\lg13-skills\skills\` selhává i po restartu CC (BLOKÁTOR — task #2324 P1 ke strat).

## Obsah

```
_total_analysis_skill_build/
├── SKILL.md                          # Skill markdown (lean — 3 unique kroky + reuse)
├── README.md                         # Tento soubor
└── scripts/
    ├── total_analysis.py             # Python helper (~400 řádků)
    └── total_analysis.sh             # Bash wrapper s pre-flight check
```

## Co skill dělá

Pre-flight audit DÁVKY právního podání před F1X.4 capsule build. Verdict GO / CONDITIONAL_GO / NO_GO.

**Lean varianta C** = neopakuje práci jiných skriptů. Reuse signálů z existing `optimize_output_F11/91-99` + `kontrola_*_audit_report.md`. Provede pouze 3 unique kroky:

1. **DON'T grep** — N zákazů z ARE matice × všechny .md ve folderu, lemma stem matching
2. **Cross-check** — porovnání s předchozí F-verzí (petit, datum, dny, sp. zn.)
3. **GO/NO-GO verdict** — sloučení signálů + hard-fail rules → master report

## Smoke test

```bash
python C:/Users/tom/Documents/_total_analysis_skill_build/scripts/total_analysis.py --help
# OK: zobrazí usage
```

Reálný test na F13 odložen do další session (po vyřešení write permission a uploadu).

## Cíl umístění

`C:\Users\tom\.claude\plugins\marketplaces\lg13\plugins\lg13-skills\skills\legal-total-analysis\`

Struktura po finální migraci:
- `SKILL.md` (přesně tento soubor)
- `scripts/total_analysis.py`
- `scripts/total_analysis.sh`

## Upload protokol — TBD se strat

Tom navrhl 2 cesty:
1. **Strat upload na Tomův web legal approve tool** (přes existing API)
2. **Legal upload sám** (pokud má strat přístupy / API klíč)

→ Domluveno se strat přes task queue. Viz task #2325 ke strat (po této session).

## Reference

- `LEGAL_TOTAL_ANALYSIS_SKILL_SPEC.md` (root) — full 9-krok spec, varianta C je její subset
- `LEGAL_NOTES.md` — LARE specifikace (vstup pro budoucí krok 2 ARE coverage, v lean variantě delegováno na `/lare`)
- STOP ORDER #1452 — skill NIKDY neodesílá podání

---

*Lean varianta C dle Tomova architectural decision 2026-04-28 ~22:30.*
