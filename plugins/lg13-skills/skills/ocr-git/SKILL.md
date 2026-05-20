---
name: ocr-git
description: "OCR pipeline pro court/AT/OSPOD evidence — scan + index + search. Wrapper kolem legal_ocr_catalogue.py. Trigger: 'ocr', 'scan PDF', 'ocr search', 'ocr stats'."
user-invocable: true
---

# OCR-Git — Legal OCR Catalogue

## PURPOSE

OCR pipeline pro legal/court/AT/OSPOD scan dokumenty. Scan + index + searchable catalogue. Background-able pro batch processing.

---

## EXECUTION

### Scan + index nových souborů

```bash
python L:/LG13/app/agent/skills/legal_ocr_catalogue.py --scan
```

### Force re-process (např. po update OCR engine)

```bash
python L:/LG13/app/agent/skills/legal_ocr_catalogue.py --scan --force
```

### Search v indexed catalogue

```bash
python L:/LG13/app/agent/skills/legal_ocr_catalogue.py --search "<query>"
```

### Statistics (count, indexed, errors)

```bash
python L:/LG13/app/agent/skills/legal_ocr_catalogue.py --stats
```

---

## CO SE STANE

- **--scan**: walk source dirs (court docs / AT submissions / OSPOD scans), OCR via Tesseract, index do catalogue DB
- **--force**: re-process i už indexed soubory
- **--search**: full-text query v OCRed obsahu
- **--stats**: souhrn (total, indexed, failed, last_run)

---

## OUTPUT

- `--scan`: progress per file + summary (N nové, M skipped, K errors)
- `--search`: matching documents s context snippet
- `--stats`: JSON / table s catalogue health

---

## RULES

- Read-only OCR (žádné modifikace originálů)
- Tesseract Czech jazyk packs required
- Long-running pro velké batches → spustit `Start-Process` background nebo Bash `run_in_background: true`
- **Output do strat queue** pokud nové AT/OSPOD evidence detected → `[OCR_NEW_DOC P1]`
- **Legal scope** — pouze legal instance má authority spustit scan; coder může assistovat na helper code

---

## USE CASES

- Lik (legal) dostane sken poštou → uloží do source dir → `--scan` indexuje
- Hledat citace v evidence: `--search "§ 909a"` → list documents s context
- Před soudním podáním: `--stats` ověří že všechny supporting docs jsou indexed

---

## RELATED

- `file-catalog-search` skill — librarian queue pro find-by-name (komplementární)
- `filing-pipeline` skill — pre-send evidence assembly
- Memory: legal evidence storage cesty v `L:/LG13/config/REFERENCE.md`

---

## FINAL

→ catalogue updated → strat notified pokud nové legal-relevant evidence
