---
name: attachment-pipeline
description: Orchestrator pro přílohy soudního podání — volá attachment-score, deferred-plans, filing-pipeline. Triggers: 'attachment pipeline', 'zpracuj prilohy', 'prilohy pipeline', 'prilohy check full'
status: stable
user-invocable: true
---

# attachment-pipeline

## PURPOSE

Meta-skill orchestrující celý workflow příloh soudního podání:

```
attachment-pipeline (tento skill)
├── → attachment-score       (scoring každé přílohy — síla/relevance/stav)
├── → deferred-plans         (DEFER přílohy → git deferred record)
└── → filing-pipeline        (KEEP přílohy → ZIP rebuild → ISDS ready)
```

Pokrývá mezeru: dosud nebylo single-entry point pro "zpracuj přílohy před podáním".
Běž před každým ZIP buildem nebo F-cyklem finalización.

---

## EXECUTION

### 1. Validate — zjisti aktuální stav

```python
from pathlib import Path

cwd = Path.cwd()
# Detekuj F-cyklus z názvu složky
import subprocess
result = subprocess.run(['git', 'log', '--oneline', '-1'], capture_output=True, text=True)
print(f"Repo: {cwd.name}")
print(f"Last commit: {result.stdout.strip()}")

# Najdi všechny PDF/PNG přílohy
attachment_dirs = [
    cwd / 'F29' / 'attachments',
    cwd / 'F29' / 'ready_to_ship',
    cwd / 'F28' / 'ready_to_ship',
    cwd / 'prilohy',
]
total = 0
for d in attachment_dirs:
    if d.exists():
        files = [f for f in d.iterdir() if f.suffix.lower() in ('.pdf', '.png', '.jpg', '.jpeg')]
        total += len(files)
        print(f"  {d}: {len(files)} příloh")
print(f"CELKEM: {total} příloh k hodnocení")
```

### 2. Spusť attachment-score

```
/lg13-skills:attachment-score
```

Počkej na výstup — scoring matrix s verdikty KEEP/KEEP_OPT/CONSOLIDATE/DEFER.

### 3. Zpracuj DEFER přílohy

Pro každou přílohu s verdiktem DEFER:
```
/lg13-skills:deferred-plans
```
Zapiš do deferred souboru s podmínkou pro zvednutí (např. "zvednout pro meritum F29+" nebo "po ISDS odeslání").

### 4. Konsoliduj CONSOLIDATE přílohy

Pokud jsou přílohy označeny CONSOLIDATE:
- Zjisti zda existuje bundle (např. OSPOD_komplet = P01+P03+P14)
- Pokud bundle neexistuje → navrhni sloučení nebo flaguj jako TODO
- Zapiš do ATTACHMENT_SCORE matrix stav po konsolidaci

### 5. Spusť filing-pipeline pro KEEP přílohy

```
/lg13-skills:filing-pipeline
```

Vstup: seznam KEEP příloh z kroku 2.
Výstup: ZIP rebuild s přílohovým manifested.

### 6. Verify + report

```python
# Ověř že všechny KEEP přílohy jsou v ZIP
import zipfile, pathlib

zip_path = next(pathlib.Path('F29').glob('*.zip'), None) or next(pathlib.Path('F28/ready_to_ship').glob('*.zip'), None)
if zip_path:
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
    print(f"ZIP: {zip_path.name} ({len(names)} souborů)")
    # Cross-check KEEP list vs ZIP contents
else:
    print("ZIP nenalezen — spusť filing-pipeline")
```

---

## OUTPUT

- Stav PŘED: N příloh, žádný scoring
- Stav PO: KEEP=X | KEEP_OPT=Y | DEFER=Z | DROP=W
- Soubory:
  - `F<XX>/ATTACHMENT_SCORE_<datum>.md` — scoring matrix
  - `L:/LG13/runtime/state/plans/deferred_<datum>_attachments-<fcycle>.md` — DEFER record
  - ZIP s KEEP přílohovým manifested (přes filing-pipeline)

---

## RULES

- Vždy validuj PŘED změnou (Krok 1)
- Vždy verifikuj PO změně (Krok 6)
- **STOP ORDER #1452** — ZIP neodesílat bez Tomova KONEC STOP
- Systémové soubory (MD, JSON, PY, ZIP, CSS) IGNOROVAT — hodnotí se jen PDF/PNG/JPG
- K08-K11 jsou vždy KEEP pro F29+ — nepřepisovat jejich verdikt
- Pokud chybí KEEP příloha (stav=I) → FLAG jako blocker před filing-pipeline
- Loguj každé kolo (git commit nebo STAV_NOW bullet)

---

## VNOŘENÉ SKILLS (volané)

| Skill | Kdy | Co vrátí |
|-------|-----|---------|
| `attachment-score` | Krok 2 | Scoring matrix KEEP/DEFER/... |
| `deferred-plans` | Krok 3 | Deferred record v git |
| `filing-pipeline` | Krok 5 | ZIP rebuild |

---

## RELATED

- Skill `attachment-score` — základní scoring krok (Krok 2 tohoto orchestratoru)
- Skill `deferred-plans` — odložení slabých příloh (Krok 3)
- Skill `filing-pipeline` — ZIP build pro KEEP přílohy (Krok 5)
- Skill `diamond-to-matrix` — analogický workflow pro argumenty (ne přílohy)
- `F28/PRILOHY_REDUKCE.md` — historický scoring F28 (referenční)
