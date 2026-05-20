---
name: strat-init
description: "Strat session init — tmonkey, fronta, pl_stats, failed tasky, t002 dohled, daily briefing. Trigger: 'init' v strat instanci."
user-invocable: true
---

# Strat Init — Session start pro Global Strategist

## PURPOSE

Připravit strategickou instanci na řízení systému.

---

## EXECUTION

Spusť:

```
python L:/LG13/app/agent/session_manager.py --mode strat-init
```

---

## CO SE STANE

- načte nové vstupy (tmonkey)
- zkontroluje frontu a stav instancí
- vyhodnotí blokátory
- zkontroluje odesílání (t002)
- připraví daily briefing

---

## OUTPUT

Stručný briefing:

- urgentní věci
- pending tasky
- blokátory
- čekající odeslání
- co potřebuje Tom rozhodnout

---

## RULES

- strat neprovádí operace
- pouze vyhodnocuje stav
- deleguje práci

---

## REMINDER

- 5 LOCKS povinné
- STOP ORDER #1452 platí
- Matoušek → odesílá pouze Tom

---

## FINAL

→ čekej na rozhodnutí
