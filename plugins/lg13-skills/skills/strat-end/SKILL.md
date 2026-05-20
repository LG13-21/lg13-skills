---
name: strat-end
description: "Strat session end — uloží vše, failne rozpracované tasky, aktualizuje CLAUDE.md, report, kontrola fronty + t002 + waiting_for_send."
user-invocable: true
---

# Strat End — Ukončení session pro strat

## PURPOSE

Bezpečně ukončit strategickou session.

---

## EXECUTION

Spusť:

```
python L:/LG13/app/agent/session_manager.py --mode strat-end
```

---

## CO SE STANE

- uloží finální stav
- uzavře rozpracované tasky
- zkontroluje queue
- připraví session report

---

## OUTPUT

- hotovo
- nedokončeno
- waiting_for_send
- důležité pro další session

---

## RULES

- strat neprovádí operace
- pouze ukončuje session
- deleguje vše na python

---

## FINAL

Session končí
