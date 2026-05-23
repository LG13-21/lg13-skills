---
name: avengers-meeting
description: This skill should be used when the user says "avengers meeting", "team planning", "team standup", "team plan", "avengers briefing", "before avengers", "team discussion", or when starting a multi-instance Avengers run and wanting all instances to align on a shared plan first. Runs a structured team planning session — each instance reads goals, writes a mini-plan to a shared file, ping-pong discussion, strat aggregates, Tom approves, then Avengers starts.
version: 1.0.0
---

# avengers-meeting — Team Planning Session před Avengers spuštěním

## PURPOSE

Avengers bez meetingu = instance pracují bez koordinace, duplikují práci, nebo si překáží.

Meeting = 30min synchronizační protokol kde:
1. Všechny instance přečtou cíle a kontext
2. Každá napíše svůj mini-plán do **sdíleného souboru**
3. Ping-pong diskuse (strat moderuje)
4. Strat agreguje → `TEAM_PLAN.md`
5. Tom vidí plán a schválí
6. Teprve pak se spustí `/avengers`

**Tom vidí plán vždy** — v `TEAM_PLAN.md` + GitHub issue comment.

---

## SDÍLENÝ PLAN SOUBOR

```
L:/LG13/runtime/ops/avengers/TEAM_PLAN.md          ← aktuální (přepisuje se per meeting)
L:/LG13/runtime/ops/avengers/TEAM_PLAN_{TS}.md      ← snapshot (archiv každého meetingu)
L:/LG13/runtime/ops/avengers/meeting_log.jsonl      ← audit log (kdo co přidal kdy)
```

Každá instance může soubor **číst i zapisovat**. Strat má finální editorial kontrolu.

---

## ROLE V MEETINGU

| Instance | Role |
|----------|------|
| **strat** | Moderátor — zahájí, agreguje, píše finální TEAM_PLAN |
| **coder** | Worker — přečte cíle, napíše tech scope + odhad |
| **legal** | Worker — přečte cíle, napíše legal scope + rizika |
| **tom** | Schvalovatel — vidí TEAM_PLAN, dá zelenou nebo změny |

---

## EXECUTION (STRAT — spouští meeting)

### Fáze 1: KICK-OFF (strat)

```python
import json, time
from pathlib import Path

AVENGERS_DIR = Path("L:/LG13/runtime/ops/avengers")
AVENGERS_DIR.mkdir(parents=True, exist_ok=True)

ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
team_plan = AVENGERS_DIR / "TEAM_PLAN.md"

# Inicializuj TEAM_PLAN.md
team_plan.write_text(f"""# TEAM PLAN — Avengers Meeting {ts}

**Status:** PLANNING
**Moderator:** strat
**Goal issue:** <issue URL>

---

## GOALS

<seznam goals z issue>

---

## INSTANCE PLANS

### [STRAT]
*(vyplní strat)*

### [CODER]
*(čeká na coder)*

### [LEGAL]
*(čeká na legal)*

---

## FINAL TEAM PLAN
*(agreguje strat po diskusi)*

---

## STATUS
- [ ] strat plan napsán
- [ ] coder plan napsán
- [ ] legal plan napsán
- [ ] strat agregoval FINAL TEAM PLAN
- [ ] Tom schválil
- [ ] Avengers spuštěn
""", encoding="utf-8")

print(f"[meeting] TEAM_PLAN.md initialized: {team_plan}")
```

Pak pošli **ping oběma instancemi** (coder + legal):

```python
# Ping-pong zpráva — viz skill ping-pong
subject = "[AVENGERS-MEETING] Kick-off — napište svůj mini-plan do TEAM_PLAN.md"
body = f"""## Avengers Meeting zahájen

**Moderátor:** strat
**Sdílený plan:** `L:/LG13/runtime/ops/avengers/TEAM_PLAN.md`
**Goals:** <URL issue>

### Tvůj úkol:
1. Přečti goals v issue
2. Doplň sekci `### [{instance}]` v TEAM_PLAN.md:
   - Co budeš dělat (scope)
   - Odhad (tokeny / čas)
   - Rizika nebo blockers
   - Co potřebuješ od ostatních
3. Pošli pong stratu: "PLAN READY"

**Deadline:** 15 minut
"""
```

---

### Fáze 2: INSTANCE PLANS (coder + legal)

Každá instance po přijetí kick-off pingu:

```python
from pathlib import Path
import re, time

TEAM_PLAN = Path("L:/LG13/runtime/ops/avengers/TEAM_PLAN.md")
content = TEAM_PLAN.read_text(encoding="utf-8")

my_instance = "coder"  # nebo "legal"

my_plan = f"""### [{my_instance.upper()}]

**Scope:**
- <co budu dělat>

**Odhad:** <X tasků, ~Y tokenů>

**Potřebuji od ostatních:**
- <závislosti>

**Rizika:**
- <blockers>

**Ready:** {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
"""

# Nahraď placeholder
content = content.replace(
    f"### [{my_instance.upper()}]\n*(čeká na {my_instance})*",
    my_plan.strip()
)
TEAM_PLAN.write_text(content, encoding="utf-8")

# Zaloguj
with open("L:/LG13/runtime/ops/avengers/meeting_log.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "instance": my_instance, "event": "plan_written"}) + "\n")
```

Pak pošli pong stratu: `"[AVENGERS-MEETING] {instance}: PLAN READY"`.

---

### Fáze 3: AGREGACE A FINÁLNÍ PLÁN (strat)

Po přijetí obou PLAN READY pongů strat:

1. Přečte TEAM_PLAN.md (všechny sekce)
2. Identifikuje závislosti, konflikty, duplicity
3. Napíše `## FINAL TEAM PLAN` sekci:

```markdown
## FINAL TEAM PLAN

### Pořadí spuštění
1. coder: T-001 (setup) → T-002 (build)
2. legal: T-010 (paralelně s coder T-002)
3. strat: T-020 (po T-002 done)

### Sdílené závislosti
- coder T-002 output → legal T-010 input
- legal T-010 → strat T-020 review

### Rizika
- <agregovaná rizika>

### Schválení Toma potřeba pro
- <co čeká na Toma>
```

4. Updatuje status checklist v souboru
5. Vytvoří GitHub issue komentář (Tom vidí summary)

```bash
gh issue comment <NUMBER> --repo LG13-21/legal-ship-2026 --body "
## 📋 [AVENGERS-MEETING] TEAM PLAN připraven — čeká na schválení

**Sdílený plan:** \`L:/LG13/runtime/ops/avengers/TEAM_PLAN.md\`

### Summary
- **Coder scope:** <1 řádek>
- **Legal scope:** <1 řádek>
- **Strat scope:** <1 řádek>
- **Závislosti:** <klíčové>
- **Odhadovaný čas:** <celkem>

### ✅ Schválení
Tom — reply \`APPROVE\` nebo uprav cíle. Po schválení spouštím Avengers.
"
```

---

### Fáze 4: TOM SCHVÁLENÍ

Tom odpoví do issue nebo píše přímo do `TEAM_PLAN.md`.

Strat čeká na:
- `APPROVE` v issue komentáři → spustí `/avengers`
- Změny v goals → vrátí se do Fáze 1 (mini-loop)
- Ticho > 30min → strat pošle připomínku + pokračuje s default plánem

---

### Fáze 5: AVENGERS START

```bash
# Strat spustí avengers skill s připraveným task listem
# Tasks jsou odvozeny z FINAL TEAM PLAN sekce v TEAM_PLAN.md
/avengers <issue>
```

TEAM_PLAN.md → archivuj:

```python
import shutil, time
ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
shutil.copy("L:/LG13/runtime/ops/avengers/TEAM_PLAN.md",
            f"L:/LG13/runtime/ops/avengers/TEAM_PLAN_{ts}.md")
```

---

## ULTRATHINK / ULTRAREVIEW INTEGRACE

Pro komplexní goals (legal filing, architekt rozhodnutí):

- **Každá instance** může v Fázi 2 spustit `/plan` (plan mode) pro svůj scope
- **Strat** může před agregací spustit `/ultrareview` nad draft TEAM_PLAN.md
- **Tom** vidí ultrareview output spolu s TEAM_PLAN

```
/avengers-meeting --ultra     # každá instance jde do plan mode
/avengers-meeting --review    # strat spustí ultrareview před finalizací
```

---

## RYCHLÝ MEETING (bez diskuse)

Pokud je scope jasný a Tom chce rychle:

```
/avengers-meeting --quick
```

Přeskočí ping-pong diskusi — každá instance napíše plan přímo, strat agreguje bez iterace, Tom schválí, start.

---

## PRAVIDLA

- **Strat je vždy moderátor** — nikdy coder nebo legal
- **TEAM_PLAN.md je sdílený** — každá instance ho smí číst a do své sekce psát
- **Atomic write** (`.tmp` → `replace()`) při zápisu do TEAM_PLAN.md (race condition)
- **Tom vždy vidí plán** — GitHub issue comment je povinný před startem
- **Archiv per meeting** — TEAM_PLAN_{TS}.md pro audit trail
- **Max meeting délka:** 30 min — pokud instance neodpoví, strat pokračuje bez ní

---

## KDY POUŽÍT

- Před každým `/avengers` spuštěním s >2 instancemi
- Když goals jsou komplexní nebo vzájemně závislé
- Když Tom chce vědět co se bude dělat před spuštěním
- Při re-startu po přerušeném Avengers runu

---

## RELATED

- Skill `avengers` — samotný execution (spouštět AŽ PO meetingu)
- Skill `ping-pong` — komunikační protokol pro Fáze 1–3
- Skill `tom-notify` — notifikace Tomovi že plán čeká na schválení
- `L:/LG13/runtime/ops/avengers/TEAM_PLAN.md` — sdílený plan soubor
- `L:/LG13/runtime/ops/avengers/meeting_log.jsonl` — audit log
