# /rtg — Ready To Go score

## PURPOSE

Vrati RTG score (Ready To Go = muze zacit submission workflow). Threshold > 0.95.

Formule:
```
RTG = pass_conditions / 8
```

8 RTG podminek (per `docs/orchestration/RTG_RTS_MATRIX.md`):
- files_exist, legal_review, atoms_validated, chronology_consistent,
- lock2_visual, evidence_tagging, no_hallucinations, dates_current

## EXECUTION

```bash
python L:/LG13/app/agent/skills/rt_score.py rtg [short|long|json|text]
```

Default `text` (pro Toma). Ostatni instance pouzivaji `json` pro raw compute.

### Output formats

| Format | Pouziti |
|---|---|
| `text` | Tomovi cely report, vc. failing conditions |
| `short` | One-liner: `RTG 0.875/0.95 (7/8) GAP` |
| `long` | Text + condition-by-condition checklist |
| `json` | Raw dict (volat z jine instance) |

### Refresh ze zdrojoveho dokumentu

```bash
python L:/LG13/app/agent/skills/rt_score.py rtg --refresh
```

Stahne `RTG_RTS_MATRIX.md` z `LG13-21/legal-ship-2026` repo a parsuje aktualni pass count.

### Override podminky

```bash
python L:/LG13/app/agent/skills/rt_score.py rtg --set rtg.lock2_visual=true
```

Po LOCK 2 approval — flip podminky, persist do `L:/LG13/runtime/state/rt_conditions.json`.

## RELATED

- `/rts` — Ready To Ship
- `/rt` — kombo RTG+RTS report
- State file: `L:/LG13/runtime/state/rt_conditions.json`
- Source spec: `LG13-21/legal-ship-2026:docs/orchestration/RTG_RTS_MATRIX.md`
