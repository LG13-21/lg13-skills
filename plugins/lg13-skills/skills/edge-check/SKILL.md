---
name: edge-check
description: "Edge-to-autocompact zone check. Spočítá zone (green/yellow/orange/red) + action + turns_remaining z /context tokens. Token-free, deleguje Pythonu."
user-invocable: true
---

# Edge-Check — Zone awareness pro save/compact rozhodnutí

## PURPOSE

Spočítat aktuální edge-to-autocompact zone z /context tokens. Rozhodne kdy save min vs. /compact vs. work.

---

## EXECUTION

Spusť (povinně --ctx-now z /context output):

```
python L:/LG13/app/agent/skills/edge_calc.py --ctx-now <N>
```

---

## CO SE STANE

- spočítá pct = ctx_now / window (default 200k)
- zařadí do zone: green (<70%), yellow (70-80%), orange (80-90%), red (≥90%)
- spočítá turns_remaining (avg 5k tokens/turn)
- vrátí action: work / save / compact
- vrátí manual_compact_ok (true jen pro orange+)

---

## OUTPUT

JSON s fields: zone, pct, action, turns_remaining, manual_compact_ok, tokens_remaining

---

## RULES

- Claude NEpočítá sám — vždy deleguje Pythonu
- bez --ctx-now FAIL fast
- žádný file read, žádná inference

---

## DECISION

- **green/yellow** → action=work, NEcompactovat (cache 5min TTL plýtvání)
- **orange** → action=save (manual_compact_ok=true, ale stále preferuj work)
- **red** → action=compact (auto-compact se brzy spustí, save first)

---

## FINAL

→ instance se rozhodne save / compact / work podle action field
