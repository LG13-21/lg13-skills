---
name: session-end
description: "Ukončení session — uloží stav, aktualizuje CLAUDE.md, pošle report strat, compact. Trigger: 'session end', 'konec session', 'ukonči session', 'zavíráme', '/session-end', nebo když dochází context window (80%+). Každá instance by měla spustit před ukončením práce."
---

# Session End — Uložení stavu a report

## PURPOSE

Bezpečné ukončení práce instance.

---

## EXECUTION

Vyvolej:

```
python L:/LG13/app/agent/session_manager.py --mode end --instance <name>
```

---

## CO SE STANE

1. Uloží stav rozpracovaných tasků
2. Pošle report do strat
3. Zkontroluje queue
4. Uloží změny
5. Provede cleanup

---

## OUTPUT

Krátký report:
- hotovo
- rozpracováno
- problémy

---

## RULES

- Neřeší detaily — deleguje na python
- Neprovádí změny mimo scope
- Vždy ukončit clean

---

## FINAL

Po dokončení:
→ spusť /compact
