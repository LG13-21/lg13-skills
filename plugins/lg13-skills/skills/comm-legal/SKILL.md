---
name: comm-legal
description: Use when checking ISDS and email communication status for sp. zn. 0 P 29/2026, scanning for new documents, running OCR on attachments, updating evidence catalog (JSON + MySQL isds_podani), or getting a dashboard of what arrived, what was sent, and what's pending. Also use PROACTIVELY mid-session whenever a new ISDS fact emerges (sent confirmation, new inbox item, resolved alert) — don't defer the evidence update to the next explicit invocation.
---

# comm-legal — ISDS + Email Communication Dashboard

## Overview

Spravuje veškerou ISDS a email komunikaci pro sp. zn. 0 P 29/2026. Skenuje nové dokumenty, spouští OCR, aktualizuje evidenci JSON a zobrazuje dashboard.

**Legal instance = ISDS správce od 13.1.2026.** Volat při každém super-start.

## When to Use

- Super-start init — automaticky spustit po A3 (deep-read); i `/lg13-skills:sr` volá tuto skill v Kroku 3.5
- Přišel signál o novém ISDS dokumentu
- Před odesláním — ověř stav fronty + STOP ORDER
- Tom ptá: "co nám přišlo?", "co jsme poslali?", "co čeká?"
- Po přidání nového souboru do `Inbox/isds/`
- **PRŮBĚŽNĚ, kdykoli v session zjistíš cokoli z ISDS** — viz sekce "PRŮBĚŽNÁ AKTUALIZACE" níže (Tom direktiva 2026-07-13)

## PRŮBĚŽNÁ AKTUALIZACE (Tom direktiva 2026-07-13)

Evidence (JSON i MySQL) nesmí zůstat pozadu za skutečností. Pokud během session — mimo formální spuštění tohoto skillu — zjistíš cokoli, co patří do ISDS evidence, **aktualizuj ji hned, ne až při příštím `/comm-legal`**:

- odešleš/potvrdíš odeslání podání (nový `dm_id`) → přidej do `isds_evidence.json` sekce `sent` I do MySQL `isds_podani`
- zkontroluješ inbox a najdeš novou přijatou zprávu → přidej do `received`
- zjistíš, že alert byl vyřešen (např. odvoláním, doplněním) → aktualizuj `status`/`action_required` v `alerts`
- zjistíš rozpor mezi JSON a MySQL (jako 2026-07-13: MySQL `isds_podani` byla 2 měsíce pozadu za JSON) → sesynchronizuj OBA směry, ne jen jeden

Nečekej na explicitní "spusť comm-legal" příkaz — pokud práce v session (např. psaní/odesílání podání, kontrola inboxu) přirozeně produkuje nový ISDS fakt, zápis do evidence je součástí té práce, ne samostatný úkol na později.

## Execution

### Krok 1 — Skenování nových dokumentů + OCR

```python
import sys, json, os, subprocess, urllib.request, base64, time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

ISDS_DIR = Path(r"L:\GitHub\legal-ship-2026\Inbox\isds")
EVIDENCE_FILE = ISDS_DIR / "isds_evidence.json"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OCR_MODEL = "glm-ocr:latest"
PDF_EXTS = {".pdf", ".PDF"}

# Načti evidence
ev = json.loads(EVIDENCE_FILE.read_text(encoding='utf-8')) if EVIDENCE_FILE.exists() else {"received": [], "sent": [], "pending": [], "alerts": []}
known_files = {r["filename"] for r in ev.get("received", [])}

# Najdi všechny PDFs
all_pdfs = [f for f in ISDS_DIR.iterdir() if f.suffix in PDF_EXTS]
new_files = [f for f in all_pdfs if f.name not in known_files]
no_ocr = [f for f in all_pdfs if not (ISDS_DIR / (f.name + ".ocr.txt")).exists()]

print(f"[comm-legal] Skenování: {len(all_pdfs)} PDF, {len(new_files)} nových, {len(no_ocr)} bez OCR")

# OCR chybějících (přes glm-ocr via Ollama)
def ocr_pdf_pages(pdf_path: Path) -> str:
    """Konvertuje PDF stránky na obrázky a OCRuje přes glm-ocr."""
    try:
        import subprocess
        # Zkus přes pdfplumber (text extraction) nejdřív — rychlejší
        try:
            import pdfplumber
            with pdfplumber.open(str(pdf_path)) as pdf:
                text = "\n".join(p.extract_text() or "" for p in pdf.pages[:10])
            if len(text.strip()) > 200:
                return text
        except Exception:
            pass

        # Fallback: glm-ocr přes Ollama (pro skeny)
        # Konvertuj první stránku na PNG přes poppler nebo pillow
        png_path = Path(str(pdf_path) + "_p0.png")
        subprocess.run(
            ["pdftoppm", "-r", "150", "-l", "1", "-png", str(pdf_path),
             str(pdf_path) + "_p"],
            capture_output=True, timeout=60
        )
        if not png_path.exists():
            return "(OCR failed — pdftoppm not available)"

        img_data = base64.b64encode(png_path.read_bytes()).decode()
        payload = {"model": OCR_MODEL, "prompt": "Extract all text from this document image. Output plain text only.", "images": [img_data], "stream": False}
        req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=240) as resp:
            return json.loads(resp.read())["response"]
    except Exception as e:
        return f"(OCR error: {e})"

for pdf in no_ocr:
    ocr_txt = ISDS_DIR / (pdf.name + ".ocr.txt")
    print(f"  OCR: {pdf.name} ...", end=" ", flush=True)
    text = ocr_pdf_pages(pdf)
    ocr_txt.write_text(text, encoding='utf-8')
    print(f"✓ ({len(text)} znaků)")
```

### Krok 2 — Přidat nové soubory do evidence

```python
# Přidej nové PDF do evidence jako nezpracované
for pdf in new_files:
    ocr_path = ISDS_DIR / (pdf.name + ".ocr.txt")
    ocr_text = ocr_path.read_text(encoding='utf-8')[:500] if ocr_path.exists() else ""
    
    new_entry = {
        "id": f"recv_{len(ev['received'])+1:03d}",
        "filename": pdf.name,
        "from_institution": "unknown",
        "subject": "(načíst z OCR)",
        "date_approx": "2026",
        "ocr": ocr_path.exists(),
        "processed": False,
        "priority": "P2",
        "notes": f"AUTO: {ocr_text[:200]}"
    }
    ev["received"].append(new_entry)
    print(f"  + evidence: {pdf.name}")

# Ulož aktualizovanou evidenci
EVIDENCE_FILE.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding='utf-8')
```

### Krok 3 — Dashboard výstup

```python
# Dashboard
print("\n" + "="*65)
print("  ISDS + EMAIL DASHBOARD | 0 P 29/2026 | legal instance")
print("="*65)

# ALERTS
alerts = [a for a in ev.get("alerts", [])]
if alerts:
    print(f"\n🔴 ALERTY ({len(alerts)}):")
    for a in alerts:
        sev = "CRITICAL" if a["severity"] == "CRITICAL" else "HIGH" if a["severity"] == "HIGH" else "MED"
        print(f"  [{sev}] {a['subject']}")
        print(f"         → {a.get('action_required','')}")

# PENDING (čeká na odeslání)
pending = ev.get("pending", [])
if pending:
    print(f"\n⏸️  ČEKÁ NA ODESLÁNÍ ({len(pending)}) — STOP ORDER #1452:")
    for p in sorted(pending, key=lambda x: x.get("send_order", 99)):
        print(f"  [{p['send_order']}] {p['subject']}")
        print(f"      ZIP: {p.get('zip','?')} | Status: {p['status']}")

# RECEIVED — nezpracované P0/P1
unprocessed = [r for r in ev.get("received", []) if not r.get("processed") and r.get("priority","P2") in ("P0","P0_ALERT","P1")]
if unprocessed:
    print(f"\n📥 PŘIJATO — NEZPRACOVÁNO ({len(unprocessed)}):")
    for r in sorted(unprocessed, key=lambda x: x.get("priority","P2")):
        print(f"  [{r['priority']}] {r['filename']}")
        print(f"      {r['subject']}")

# SENT — přehled
sent = ev.get("sent", [])
print(f"\n📤 ODESLÁNO: {len(sent)} zásilek")
for s in sent:
    print(f"  [{s.get('wave','?')}] {s['subject']} ({s.get('date','?')})")

print(f"\n📊 Celkem: {len(ev.get('received',[]))} přijato | {len(sent)} odesláno | {len(pending)} čeká")
print("="*65)
```

### Krok 4 — MySQL sync (isds_podani)

JSON evidence (`isds_evidence.json`) a MySQL tabulka `isds_podani` musí obsahovat stejná podání. Po Kroku 2/3 (nebo při průběžné aktualizaci) zkontroluj rozdíl a dorovnej:

```python
import sys
sys.path.insert(0, 'L:/GitHub/lg13-coder/agent/skills')
from db_query import db

# Zjisti, které 'wave'/'verze' z JSON sent[] už jsou v MySQL
r = db("SELECT DISTINCT vlna FROM isds_podani")
known_vlny = {row[0] for row in r.get('rows', [])}

sent = ev.get("sent", [])
missing = [s for s in sent if s.get("verze", s.get("wave", s.get("id",""))) not in known_vlny]

for s in missing:
    vlna = s.get("verze", s.get("wave", s.get("id","?")))
    dm = s.get("dm_id","")
    poznamka = f"dm={dm} {s.get('note','')}"[:250]
    db("INSERT INTO isds_podani (vlna, datum_odeslani, predmet, soubor, je_v_soudnim_spisu, poznamka) VALUES (%s,%s,%s,%s,%s,%s)",
       params=[vlna, s.get("date","?"), s.get("subject","")[:250], (s.get("files") or ["-"])[0], 0, poznamka])
    print(f"  MySQL + {vlna}")

if not missing:
    print("  MySQL isds_podani je synchronizovana s JSON.")
```

Pokud najdeš záznam v MySQL, který v JSON chybí (opačný směr) — dopiš ho i do `isds_evidence.json`, ne jen nahlas.

## Email seznam.cz

Pro email komunikaci zkontroluj `/lg13-skills:email-read`. Filtruj:
- Odesílatel/adresát: `@c-budejovice.cz`, `@kraj-jihocesky.cz`, `@euceb.cz`, `@akjudrflaska.com`
- Předmět: `0 P 29/2026`, `Kopecký`, `Matouš`

## Evidence soubory

| Soubor | Účel |
|--------|------|
| `Inbox/isds/isds_evidence.json` | Primární evidence — received/sent/pending/alerts |
| `Inbox/isds/*.ocr.txt` | OCR text každého PDF |
| `L:\LG13\legal_docs_catalogue\` | Globální katalog všech legal docs |

**OCR katalogizace hromadně:**
```bash
python L:\LG13\app\agent_pre_junction_backup\skills\legal_ocr_catalogue.py --scan
```

## Institutions DS

| Instituce | DS | Role |
|-----------|-----|------|
| OS České Budějovice | ws6abvh | soud |
| Mgr. Jan Škorpil, EU ČB | hvknnv7 | exekutor |
| Jihočeský kraj OSPOD | kdib3rr | nadřízený OSPOD |
| Tom Kopecký | vprwiuq | my DS |

## Common Mistakes

- Zapomenout spustit OCR před katalogizací → `no_ocr` list pokaždé zkontrolovat
- Označit dokument jako processed bez skutečné analýzy → `processed: true` jen po Tom GO
- Přehlédnout P0_ALERT priority → vždy zobrazit první
