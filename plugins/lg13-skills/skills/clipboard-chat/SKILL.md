---
name: clipboard-chat
description: "Use when running or continuing block-by-block ChatGPT review of F39; or when user says '--done', '--next', '--bootstrap', 'clipboard review', 'zkopiruj revizni prompt', 'dalsi blok', 'oznac blok FROZEN', 'block review F39', 'cb chat', 'CB chat'."
---

# clipboard-chat — Interaktivní blok-po-bloku revize F39 s ChatGPT

## CO SKILL DĚLÁ

Spravuje strukturovanou revizi F39 přes ChatGPT. Workflow:

1. **Bootstrap** — jednou, na začátku: připraví kontext pro nové ChatGPT vlákno. Tom vloží do nového ChatGPT threadu. ChatGPT potvrdí že rozumí.
2. **Blok-po-bloku** — iterace F39-01 až F39-xx:
   - ChatGPT přečte blok a navrhne úpravy
   - Tom řekne svůj názor a instrukci (mě / legal instanci)
   - Legal zapracuje → `--done F39-XX go` → auto-zkopíruje prompt dalšího bloku
3. **Jarvis** — každý verdict se zapíše do MySQL + status JSON

---

## PŘÍKAZY

```bash
# Zobraz stav bloků
python F39/jarvis/clipboard_chat.py --list

# Vygeneruj bootstrap prompt pro nové ChatGPT vlákno (jednou na začátek)
python F39/jarvis/clipboard_chat.py --bootstrap

# Zkopíruj prompt pro DALŠÍ blok (sekvence)
python F39/jarvis/clipboard_chat.py --next

# Zkopíruj prompt pro konkrétní blok
python F39/jarvis/clipboard_chat.py F39-04

# Označ blok jako hotový → auto-zkopíruje prompt dalšího bloku
python F39/jarvis/clipboard_chat.py --done F39-04 go
python F39/jarvis/clipboard_chat.py --done F39-04 warn
python F39/jarvis/clipboard_chat.py --done F39-04 stop
```

---

## WORKFLOW — KOLO PO KOLE

```
KROK 0 (jednou):
  legal:  python clipboard_chat.py --bootstrap  → Ctrl+V do NOVÉHO ChatGPT vlákna
                                                   ChatGPT potvrdí kontext

KROK N (každý blok):
  legal:  python clipboard_chat.py --next       → Ctrl+V do ChatGPT
          ChatGPT: čte blok, navrhuje úpravy
          Tom: říká svůj názor legal instanci
          legal: zapracuje změny do F39/01_navrh_PR_F39.35.md
          legal:  python clipboard_chat.py --done F39-XX go|warn|stop
                  → auto-zkopíruje prompt dalšího bloku → opakuj
```

---

## PROMPT FORMÁTY

### Bootstrap
Vygeneruje kontext pro nové vlákno — případ, klíčové fakty, instrukce jak má ChatGPT postupovat blok-po-bloku.

### Read-prompt (pro každý blok)
```
Jsme v revizi návrhu F39. Přečti tento blok a napiš:
a) Co funguje — co soudce přijme
b) Co bys změnil/doplnil/zkrátil — navrhni konkrétní alternativní znění
c) Co chybí — chybějící důkaz, citace, vazba na petit

--- [obsah bloku] ---

Čekám na Tomův komentář před tím, než navrhnu finální verzi.
```

---

## STAV BLOKŮ

`F39/jarvis/blocks.py` — zdrojová pravda  
`F39/jarvis/block_review_status.json` — JSON pro Jarvis  
MySQL `jarvis_events` — audit log verdiktů

Status: `FROZEN` ❄️ = schváleno | `REVIEW` 🔍 = čeká | `APPROVED` ✅ = finální

---

## POZNÁMKY

- Bootstrap generuj jednou — na začátek nového ChatGPT vlákna
- Každý read-prompt čerpá aktuální obsah ze zdrojového MD (F39.35)
- `--done` označí blok, zapíše do MySQL+JSON, auto-zkopíruje další prompt
- STOP ORDER #1452 aktivní — CB chat = přípravná fáze, ne odeslání
