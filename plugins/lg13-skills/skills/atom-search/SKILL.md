---
name: atom-search
description: "Vyhledá atomy z konkrétní ChatGPT konverzace (conv_id) nebo dle instance/time window, seřadí ASC dle timestamp. Použij kdykoli instance potřebuje přečíst obsah vlákna z RAG/atom pipeline. Trigger: 'najdi atomy', 'přečti vlákno', 'conv_id', 'atom-search', 'seřaď atomy'."
user-invocable: true
---

# Atom-Search — vyhledání atomů z konverzace

## ÚČEL

Instance má nástroje: RAG, pl_server, atom_dispatcher, JSON lokální soubory.
Tento skill je návod jak je správně použít pro vyhledání obsahu ChatGPT vlákna.

---

## EXECUTION

### 1. Vyhledání dle conv_id (nejpřesnější)

```bash
python L:/LG13/app/agent/atom_lookup.py \
  --instance <name> \
  --conv-id <conv_id> \
  --since 30d \
  --tz cest \
  --format markdown \
  --limit 200
```

Výstup seřadit ASC dle timestamp (nejstarší první = chronologické čtení):

```python
import subprocess, sys, json
sys.stdout.reconfigure(encoding='utf-8')

result = subprocess.run(
    ['python', 'L:/LG13/app/agent/atom_lookup.py',
     '--instance', 'legal',
     '--conv-id', '6a06b4b5-2180-83eb-aedf-8b4b728a5d59',
     '--since', '30d', '--tz', 'cest', '--format', 'json', '--limit', '200'],
    capture_output=True, text=True, encoding='utf-8'
)
atoms = json.loads(result.stdout)
atoms_sorted = sorted(atoms, key=lambda a: a.get('ts', ''))  # ASC
for a in atoms_sorted:
    print(f"[{a['ts']}] {a.get('type','')} — {a.get('content','')[:200]}")
```

### 2. Vyhledání dle instance + time window

```bash
python L:/LG13/app/agent/atom_lookup.py \
  --instance legal \
  --since 48h \
  --tz cest \
  --format markdown \
  --limit 100
```

### 3. Přímý dotaz na pl_server (když stack file chybí)

```bash
curl "http://localhost:8790/pl/atoms?instance=legal&limit=50"
curl "http://localhost:8790/pl/atoms?conv_id=<conv_id>&limit=100"
```

### 4. Lokální JSON (daily atoms)

```bash
python -c "
import json, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
files = sorted(glob.glob('L:/LG13/atoms/daily/*.json'))
for f in files[-3:]:  # posledni 3 dny
    data = json.load(open(f, encoding='utf-8'))
    relevant = [a for a in data if '6a06b4b5' in a.get('conv_id','')]
    for a in sorted(relevant, key=lambda x: x.get('ts','')):
        print(a.get('ts'), a.get('content','')[:150])
"
```

---

## WORKFLOW pro čtení vlákna

1. Zjisti `conv_id` (z URL: `chatgpt.com/c/<conv_id>`)
2. Spusť atom_lookup s `--conv-id` + `--since 30d` + `--format json`
3. Seřaď ASC dle `ts` field
4. Čti chronologicky — první zpráva = kontext, poslední = závěr

---

## PŘÍKLAD: Větev vlákno

```bash
python L:/LG13/app/agent/atom_lookup.py \
  --instance legal \
  --conv-id 6a06b4b5-2180-83eb-aedf-8b4b728a5d59 \
  --since 30d --tz cest --format markdown --limit 200
```

---

## RELATED

- `tmonkey` skill — obecný stack_reader pickup
- `tmonkey-arm` — watcher pro nové atomy
- pl_server: `http://localhost:8790/pl/stats` — celkový stav pipeline
