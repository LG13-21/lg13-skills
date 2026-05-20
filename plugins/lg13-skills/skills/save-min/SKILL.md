---
name: save-min
description: "Token-min save (3 kroky): queue --done + STAV append + save_checkpoint + edge calc. NIKDY /compact bez prior save min."
user-invocable: true
---

# Save-Min — Token-minimal session save

## PURPOSE

Uložit session state minimal-cost cestou. Default save (vs. save full jen na explicit Tom request).

---

## EXECUTION

Spusť (povinně --instance + --ctx-now):

```
python L:/LG13/app/agent/session_manager.py --mode save --instance <name> --ctx-now <N>
```

---

## CO SE STANE

- queue --done aktivní task (≤80 znaků popis)
- STAV_NOW.md append (3 bullety)
- save_checkpoint write (atomic .tmp → replace)
- edge_calc embed → JSON má `edge` blok se zone + action + manual_compact_ok

---

## OUTPUT

Save JSON path + edge blok (zone + action). Tichý, žádné velké výstupy.

---

## RULES

- **HARD:** NIKDY /compact bez prior save min execution (step 0 prerekvizita)
- bez --ctx-now save proběhne ale bez edge bloku → není decision input pro /compact
- atomic writes (.tmp → Path.replace)
- save min = no /clear (ten stále vyžaduje Tom approval)

---

## ANTI-PATTERN (incident 2026-05-10)

Strat dělal /compact po každé zprávě BEZ save min → ztrácel state → R153 retry crossover → Tom: "jako malé děti jste". Fix: tato skill = HARD RULE save-before-compact.

---

## FINAL

→ pokud edge.action=compact → spusť /compact; jinak pokračuj v práci
