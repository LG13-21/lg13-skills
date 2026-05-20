---
name: session-save
description: "Průběžné uložení stavu session — uloží progress, aktualizuje CLAUDE.md pokud třeba, compact. Trigger: 'save', 'ulož stav', 'checkpoint', '/session-save', 'compact a ulož', nebo automaticky když context window přesáhne 60%. Neukončuje session — jen uloží a pokračuje."
---

# Session Save — Průběžný checkpoint

## PURPOSE

Uložit progress bez ukončení session.

---

## EXECUTION

Spusť:

```
python L:/LG13/app/agent/session_manager.py --mode save --instance <name>
```

---

## CO SE STANE

- uloží aktuální progress
- aktualizuje stav
- připraví krátký checkpoint report

---

## OUTPUT

Stručně:
- co je hotové
- co je rozpracované
- co dál

---

## RULES

- neukončuje session
- nefailuje tasky
- deleguje vše na python

---

## FINAL

→ spusť /compact
