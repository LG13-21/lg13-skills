---
name: strat-save
description: "Strat session save — checkpoint s progress reportem, CLAUDE.md update, t002 dohled, waiting_for_send check, compact. Bez ptání."
user-invocable: true
---

# Strat Save — Průběžný checkpoint pro strat

## PURPOSE

Uložit progress bez ukončení session.

---

## EXECUTION

Spusť:

```
python L:/LG13/app/agent/session_manager.py --mode strat-save
```

---

## CO SE STANE

- uloží progress strat
- zkontroluje stav systému (queue, t002, waiting)
- připraví checkpoint report

---

## OUTPUT

Stručně:
- co je hotovo
- co běží
- co čeká
- blokátory

---

## RULES

- strat neprovádí operace
- pouze ukládá stav
- deleguje vše na python

---

## FINAL

→ /compact
