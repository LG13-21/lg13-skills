---
name: file-catalog-search
description: "Najít soubor přes librarian instance místo manual Glob. Standardizovaný entrypoint pro evidence/document lookup. Trigger: 'kde je soubor', 'catalog', 'librarian', 'find file'."
user-invocable: true
---

# File-Catalog-Search — Librarian queue lookup

## PURPOSE

Najít soubor v LG13 codebase / evidence storage přes librarian instance (która udržuje catalog index). Vyhne se token-spend na manual Glob napříč 100+ adresáři.

---

## EXECUTION

### Send find request do librarian queue

```bash
python L:/LG13/app/agent/instance_queue.py --send --to librarian --from-inst <self> --msg "FIND: <query>" --priority P2
```

### Check responses (librarian vrací přes queue)

```bash
python L:/LG13/app/agent/instance_queue.py --check --name <self>
```

### Wait pattern (librarian async, may take 30-60s)

Použij `tmonkey-arm` nebo `ping-pong` skill arm Monitor watcher na vlastní stack/queue změnu, jinak polling 30s.

---

## CO SE STANE

- queue write → librarian instance pickup
- librarian queries svůj catalog (filename + content index)
- librarian replies přes queue s file paths + relevance ranking
- self instance vyzvedne reply

---

## OUTPUT

Librarian response = list paths s metadata (size, mtime, OCR-indexed flag, ranking).

---

## RULES

- **NEPOUŽÍVAT pro known paths** — pokud víš cestu, Read přímo (cheaper than queue roundtrip)
- **Async** — librarian nemusí být armed; expect 30s+ latency
- Pokud librarian DOWN → fallback na local Glob (logni token-tip do strat)
- **Per memory `reference_lg13_pingpong.md`**: queue pro one-shot tasking, NE pro chat dialog

---

## USE CASES

- legal: "kde je rozsudek z roku 2024 ve věci X" → librarian search OCR catalogue
- coder: "kde je definice atom_classifier" → fallback Grep, ne librarian (code search ≠ document search)
- tmonkey post-trigger: nový atom mentions document → file-catalog-search resolve path

---

## QUERY SYNTAX

- Plain text: `FIND: rozsudek 0 P 29 Matoušek`
- Filename hint: `FIND: file:Cestne_prohlaseni_*`
- Date range: `FIND: from:2025-09 to:2025-12 OSPOD`
- Type filter: `FIND: type:pdf zadost`

(Librarian parses; spec depends na librarian implementation status — TBC)

---

## STATUS

- **Librarian instance:** TBD ready check (per coder R155 ping Q4 to legal)
- **Fallback:** local Glob + tom messaging librarian directly

---

## RELATED

- `ocr-git` skill — feeds OCRed content do librarian catalogue
- `tmonkey-monitor` — diagnostics
- Memory: librarian instance scope v kernel `L:/Lukasek/CLAUDE.md` ROUTING table

---

## FINAL

→ paths returned → instance Read přímo nebo escalate pokud miss
