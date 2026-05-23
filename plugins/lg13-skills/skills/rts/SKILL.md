# /rts — Ready To Ship score

## PURPOSE

Vrati RTS score (Ready To Ship = muze zmacknout datovku). Threshold > 0.98.

Formule:
```
RTS = (RTG_score * 0.5) + (RTS_pass / 8 * 0.5)
```

8 RTS podminek (per `docs/orchestration/RTG_RTS_MATRIX.md`):
- rtg_pass, pdf_export_valid, zip_package, datovka_template,
- attachments_verified, p20_certification, ospod_certified_copies, signature_block

## EXECUTION

```bash
python L:/LG13/app/agent/skills/rt_score.py rts [short|long|json|text]
```

Default `text` (pro Toma). JSON varianta = raw compute pro instance-to-instance.

### Output formats — viz `/rtg`

### Override podminky

```bash
python L:/LG13/app/agent/skills/rt_score.py rts --set rts.p20_certification=true
python L:/LG13/app/agent/skills/rt_score.py rts --set rts.zip_package=true
```

## RELATED

- `/rtg` — Ready To Go
- `/rt` — kombo report
- Source spec: `LG13-21/legal-ship-2026:docs/orchestration/RTG_RTS_MATRIX.md`
