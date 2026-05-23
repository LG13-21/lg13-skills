---
name: skill-picker
description: Use when the user asks "which skill should I use?", "what skill for X?", "help me pick a skill", "skill picker", "skill guide", or when an instance needs to decide which skill to invoke. Returns categorized skill catalog with decision trees for both Tom and all instances (coder/strat/legal).
version: 1.0.0
---

# Skill-Picker — LG13 Skill Catalog & Decision Guide

## PRO KOHO

Tento skill je pro všechny:
- **Tom** — chce vědět jaký skill použít pro daný úkol
- **Strat** — vybírá skill pro dispatch nebo koordinaci
- **Coder** — vybírá skill pro execution nebo monitoring
- **Legal** — vybírá skill pro legal workflow nebo komunikaci

---

## RYCHLÝ VÝBĚR (decision tree)

```
Co chceš udělat?
│
├── KOMUNIKACE
│   ├── Mluvit s jinou instancí → /ping-pong
│   ├── Upozornit Toma → /tom-notify
│   ├── Poslat zprávu přes ChatGPT → /chatgpt-send
│   └── Heartbeat (jsem naživu) → /heartbeat
│
├── SESSION MANAGEMENT
│   ├── Začít session (coder) → /lg13-init
│   ├── Uložit stav session → /lg13-save nebo /save-min
│   ├── Ukončit session → /lg13-end
│   ├── Začít session (strat) → /strat-init → /strat-save → /strat-end
│   └── Autosave průběžně → /autosave
│
├── PLÁNOVÁNÍ & KOORDINACE
│   ├── Team planning před Avengers → /avengers-meeting
│   ├── Spustit Avengers (parallel instances) → /avengers
│   ├── Spustit instances → /team-launcher
│   ├── Zapsat plán do GitHub issue → /plan-to-git
│   └── Odložit nedokončenou práci → /deferred-plans
│
├── LEGAL WORKFLOW
│   ├── Celková analýza dokumentu → /legal-total-analysis
│   ├── Rapid legal review → /lare
│   ├── Filing pipeline (LOCK workflow) → /filing-pipeline
│   ├── LOCK checklist → /locks-workflow
│   └── Tmonkey web ingestion → /tmonkey-web
│
├── HLEDÁNÍ & VYHLEDÁVÁNÍ
│   ├── Hledat v atomech → /atom-search
│   ├── Hledat v tmonkey/git → /git-tmonkey-search
│   ├── Hledat v ChatGPT konverzacích → /chatgpt-search nebo /chatgpt-find
│   ├── RAG search → /rag-search
│   └── Katalog souborů → /file-catalog-search
│
├── MONITORING & STATUS
│   ├── Status všech systémů → /rt
│   ├── RTG (readiness-to-go) → /rtg
│   ├── RTS (readiness-to-ship) → /rts
│   ├── Cockpit dashboard → /cockpit
│   ├── Listen to events (daemon) → /listen-to-the-music
│   ├── Tmonkey status → /tmonkey-diag nebo /tmonkey-monitor
│   └── Web-up check → /web-up
│
├── TOKENY & BUDGET
│   ├── Přečíst token limit → /token-limit-read
│   ├── Spravovat budget → /budget-manager
│   ├── Watchdog pro budget → /budget-watchdog
│   └── Zero-token operace → /zero-tokens
│
├── TMONKEY / CHATGPT
│   ├── Arm tmonkey → /tmonkey-arm
│   ├── Listen tmonkey → /tmonkey-listen
│   ├── Poslat zprávu do ChatGPT → /chatgpt-send
│   ├── Zeptat se ChatGPT → /chatgpt-ask
│   ├── Nutit ChatGPT přečíst → /chatgpt-force-read
│   └── Thread harvest (extrakce konverzací) → /thread-harvest
│
├── UTILITY
│   ├── Screenshot → /prtsc
│   ├── OCR + git → /ocr-git
│   ├── Edge-case check → /edge-check
│   ├── Issue sync → /issue-sync
│   └── Action telemetry → /action-telemetry
│
└── META (o skills samotných)
    ├── Vytvořit nový skill → /skill-creator
    ├── Vybrat správný tool (ne skill) → /tool-picker
    └── Tento katalog → /skill-picker
```

---

## KATALOG PODLE KATEGORIE

### SESSION MANAGEMENT

| Skill | Trigger | Popis | Kdo |
|-------|---------|-------|-----|
| `/lg13-init` | začátek coder session | Inicializace coder workspace, load state | coder |
| `/lg13-save` | uložení coder session | Uložení stavu do remember.md | coder |
| `/lg13-end` | konec coder session | Clean shutdown, handoff note | coder |
| `/strat-init` | začátek strat session | Inicializace strat workspace | strat |
| `/strat-save` | uložení strat session | Uložení stavu strat | strat |
| `/strat-end` | konec strat session | Strat clean shutdown | strat |
| `/save-min` | rychlé uložení | Minimalistické uložení (méně tokenů než /lg13-save) | all |
| `/autosave` | průběžné ukládání | Automatické save každých N kroků | all |

---

### KOMUNIKACE

| Skill | Trigger | Popis | Kdo |
|-------|---------|-------|-----|
| `/ping-pong` | komunikace mezi instancemi | JSON protokol přes filesystem, atomic write | all instances |
| `/tom-notify` | upozornit Toma | Push notifikace nebo zpráva Tomovi | strat |
| `/chatgpt-send` | poslat zprávu do ChatGPT | Odeslat text/task přes tmonkey do ChatGPT | all |
| `/heartbeat` | jsem naživu | 15min heartbeat signal stratu | coder, legal |
| `/slack-listen` | Slack monitoring | Naslouchat Slack událostem | strat |

---

### PLÁNOVÁNÍ & KOORDINACE

| Skill | Trigger | Popis | Kdo |
|-------|---------|-------|-----|
| `/avengers-meeting` | team planning | Synchronizační meeting před Avengers (TEAM_PLAN.md) | strat + all |
| `/avengers` | spustit parallel run | Paralelní execution více instancí | strat |
| `/team-launcher` | spustit instance | Launcher pro coder/legal/strat | strat, Tom |
| `/plan-to-git` | zapsat plán jako issue | Vytvoří GitHub issue s kroky pro guided session | all |
| `/deferred-plans` | odložit nedokončenou věc | Commitne rozpracovaný plán do gitu | all |
| `/terminator` | dokončit plán | Executor pro plány z /plan-to-git | coder |

---

### LEGAL WORKFLOW

| Skill | Trigger | Popis | Kdo |
|-------|---------|-------|-----|
| `/legal-total-analysis` | celková analýza | Komplexní analýza právního dokumentu | legal |
| `/lare` | rapid review | Rychlá právní analýza (light) | legal |
| `/filing-pipeline` | F-cycle pipeline | Celý filing workflow F0→F10 | legal, strat |
| `/locks-workflow` | LOCK checklist | LOCK 1/2/3 workflow (freeze → ISDS) | legal, strat |
| `/tmonkey-web` | web ingestion | Zachytit web obsah přes tmonkey | legal, coder |

---

### HLEDÁNÍ & VYHLEDÁVÁNÍ

| Skill | Trigger | Popis | Kdo |
|-------|---------|-------|-----|
| `/atom-search` | hledat v atomech | FTS search v atomizovaných dokumentech | all |
| `/git-tmonkey-search` | hledat v tmonkey historii | Prohledávání git/tmonkey exportů | all |
| `/chatgpt-search` | hledat v ChatGPT | Vyhledat v ChatGPT konverzacích (tmonkey index) | all |
| `/chatgpt-find` | najít v ChatGPT | Cílenější find v ChatGPT než search | all |
| `/rag-search` | RAG dotaz | Retrieval-augmented search | all |
| `/file-catalog-search` | katalog souborů | Prohledat file catalog | all |

---

### MONITORING & STATUS

| Skill | Trigger | Popis | Kdo |
|-------|---------|-------|-----|
| `/rt` | celkový status | Runtime status všech systémů (jeden přehled) | all |
| `/rtg` | readiness-to-go | Připravenost ke spuštění (go/no-go) | strat, Tom |
| `/rts` | readiness-to-ship | Připravenost k odeslání (shipment check) | strat, legal |
| `/cockpit` | dashboard | Vizuální dashboard stavu systému | Tom, strat |
| `/listen-to-the-music` | event daemon | Démon naslouchající 7 zdrojům (ping-pong, slack, github...) | coder, strat |
| `/tmonkey-monitor` | tmonkey watch | Monitoring tmonkey aktivit | coder |
| `/tmonkey-diag` | tmonkey diagnostika | Diagnostika problémů s tmonkey | coder |
| `/web-up` | web status | Ověřit zda web služby běží | coder |
| `/i-can-hear-u` | echo test | Ověřit že instance slyší | Tom |

---

### TOKENY & BUDGET

| Skill | Trigger | Popis | Kdo |
|-------|---------|-------|-----|
| `/token-limit-read` | přečíst limity | Aktuální token usage a limity | all |
| `/budget-manager` | spravovat budget | Správa a alokace tokenového budgetu | strat |
| `/budget-watchdog` | hlídat budget | Automatický watchdog pro překročení | strat |
| `/zero-tokens` | zero-token ops | Operace bez spotřeby tokenů | all |

---

### TMONKEY / CHATGPT

| Skill | Trigger | Popis | Kdo |
|-------|---------|-------|-----|
| `/tmonkey` | tmonkey main | Hlavní tmonkey skill (arm + listen) | coder |
| `/tmonkey-arm` | arm tmonkey | Aktivace tmonkey listeneru | coder |
| `/tmonkey-listen` | listen tmonkey | Naslouchání tmonkey eventům | coder |
| `/chatgpt-ask` | zeptat ChatGPT | Odeslat dotaz do ChatGPT | all |
| `/chatgpt-send` | poslat do ChatGPT | Odeslat zprávu/task do ChatGPT | all |
| `/chatgpt-force-read` | nutit ChatGPT číst | Vynucení přečtení souboru ChatGPT | coder |
| `/thread-harvest` | extrahovat konverzace | Parser ChatGPT/Claude threadů pro direktivy | coder |

---

### UTILITY

| Skill | Trigger | Popis | Kdo |
|-------|---------|-------|-----|
| `/prtsc` | screenshot | Pořídit screenshot okna/oblasti | Tom |
| `/ocr-git` | OCR + commit | OCR dokumentu a uložit do gitu | coder |
| `/edge-check` | edge-case audit | Kontrola okrajových případů v kódu/dokumentu | coder |
| `/issue-sync` | sync issues | Synchronizace GitHub issues se stavem | strat, coder |
| `/action-telemetry` | telemetrie akcí | Záznam a analýza provedených akcí | all |

---

## INSTANCE-SPECIFIC QUICK REF

### Tom — nejčastěji spouštíš
```
/avengers-meeting   → před každým team spuštěním
/cockpit            → status přehled
/rt                 → rychlý system check
/plan-to-git        → zapsat co chceš udělat
/team-launcher      → spustit instance
/rtg nebo /rts      → go/ship check
```

### Strat — moderátor + koordinátor
```
/avengers-meeting   → zahájit meeting (ty jsi moderátor)
/avengers           → spustit parallel run
/ping-pong          → komunikace s coder/legal
/budget-manager     → drž budget roli
/tom-notify         → eskalovat Tomovi
/deferred-plans     → odložit pending práci
/rtg                → check před launch
```

### Coder — execution worker
```
/lg13-init          → každé ráno
/ping-pong          → odpovědět stratu
/heartbeat          → každých 15 min
/listen-to-the-music → arm event daemon
/tmonkey-arm        → aktivovat tmonkey
/edge-check         → před commitem
/lg13-save          → průběžně
/zero-tokens        → file ops bez LLM
```

### Legal — legal analysis + filing
```
/lare               → rychlá analýza
/legal-total-analysis → hloubkový rozbor
/filing-pipeline    → F-cycle workflow
/locks-workflow     → LOCK 1/2/3
/atom-search        → hledat precedenty
/rts                → check před odesláním
```

---

## ZKRATKY (pro rychlé zadání)

| Co chceš | Zkratka | Plný název |
|----------|---------|------------|
| Komunikovat s instancí | pp | /ping-pong |
| Uložit session | save | /lg13-save |
| Status přehled | rt | /rt |
| Team meeting | am | /avengers-meeting |
| Hledat v atomech | as | /atom-search |
| Budget check | bl | /token-limit-read |

---

## RELATED

- `/tool-picker` — která technická tool použít (Bash vs Read vs Grep atd.)
- `/skill-creator` — jak vytvořit nový skill
- `C:/Users/tom/.claude/plugins/marketplaces/lg13/plugins/lg13-skills/skills/` — adresář všech skills
