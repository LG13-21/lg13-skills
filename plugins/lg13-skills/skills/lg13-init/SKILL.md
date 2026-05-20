---
name: lg13-init
description: "Inicializace session — načte stav, přečte frontu, tmonkey, pl_stats, vygeneruje briefing. Trigger: 'init', 'start session', 'začínáme', '/session-init', nebo automaticky na začátku každé nové konverzace. Každá instance MUSÍ spustit na začátku práce."
user-invocable: true
---

# Session Init — Start session jakékoliv instance

## PURPOSE

Připravit instanci na práci.

---

## EXECUTION

Spusť:

```
python L:/LG13/app/agent/session_manager.py --mode init --instance <name>
```

---

## CO SE STANE

- načtení nových vstupů (tmonkey)
- kontrola fronty
- načtení stavu
- základní systémové info
- vytvoření briefingu

---

## OUTPUT

Stručný přehled:
- nové vstupy
- pending tasky
- urgentní věci
- blokátory

---

## RULES

- neprovádí rozhodování
- pouze připravuje kontext
- deleguje vše na python

---

## FINAL

Po init:
→ čekej na task
