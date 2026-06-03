---
name: uklid-coder
description: Use for coder's regular maintenance duties — skills registry update, queue check, heartbeat, and save-min. Run periodically or before /restart.
---

# uklid-coder — Coder Regular Duties

Pravidelná údržba coderovy instance. Spouštět každých ~60 min nebo při potřebě uklidu.

## EXECUTION

### Krok 1 — Queue check + claim

```bash
python L:/LG13/app/agent/instance_queue.py --check --name coder
python L:/LG13/app/agent/instance_queue.py --claim-next --name coder
```

### Krok 2 — Skills registry update (issue #90)

```bash
python L:/LG13/app/agent/skills/skills_registry.py --format table > /tmp/skills_table.txt
# Pak aktualizuj issue #90 s novým výpisem (diff od posledního update)
```

Nebo use `/lg13-skills:skills-list` a zkontroluj jestli přibyly nové skills.

### Krok 3 — Zkontroluj deprecated skills

```bash
python L:/LG13/app/agent/skills/skills_registry.py --format table | grep -i deprecated
```

Pokud nalezeno: smaž nebo updatuj na redirect.

### Krok 4 — Heartbeat pong stratu

```
Subject: [HEARTBEAT] coder HH:MM — <co dělám>
Body: PLAN STATUS + budget state
```

Viz skill `ping-pong` → 15-MIN HEARTBEAT sekce.

### Krok 5 — Save-min

```
/lg13-skills:save-min
```

## FREKVENCE

- Každých ~60 minut při aktivní práci
- Před /restart nebo /sr
- Pokud Tom zazvoní nebo napíše "jak jsi na tom?"

## RELATED

- `/lg13-skills:save-min` — persistence
- `/lg13-skills:rr` — rychlý report
- `/lg13-skills:skills-list` — přehled skills
- Issue #90: `[REGISTRY] LG13 Skills Registry`
