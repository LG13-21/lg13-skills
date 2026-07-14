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

## ZONE TABLE (skutečné prahy z edge_calc.py)

| Zone   | ctx_pct (z window 200k) | action                  | manual_compact_ok |
|--------|--------------------------|-------------------------|-------------------|
| green  | < 95 %                   | work                    | false             |
| yellow | 95 – 98 %                | save_min_at_task_end    | false             |
| orange | 98 – 100 %               | save_min_now            | true              |
| red    | ≥ 100 %                  | let_autocompact_fire    | false             |

**ctx_pct = ctx_now / window × 100** (ne session %, ne weekly %)

Při ctx 40 % → zone=green, action=work. Autocompact threshold je 95 %.

---

## CO SE STANE

- spočítá pct = ctx_now / window (default 200k)
- zařadí do zone dle ZONE TABLE výše (green / yellow / orange / red)
- spočítá turns_remaining (avg 5k tokens/turn)
- vrátí action + manual_compact_ok

---

## OUTPUT

JSON s fields: zone, ctx_pct, action, turns_remaining, manual_compact_ok, tokens_remaining

---

## RULES

- Claude NEpočítá sám — vždy deleguje Pythonu
- bez --ctx-now FAIL fast
- žádný file read, žádná inference

## ⛔ HARD STOP — NEkompaktuj při ctx < 85 %

**NIKDY nespouštěj /compact ani save-min jen kvůli edge-check pokud ctx_pct < 85.**

- ctx 40 % → green → work (NEPŘEMÝŠLEJ O COMPACTU)
- ctx 70 % → green → work
- ctx 85 % → green → work
- compact povolí až orange zone (ctx ≥ 98 %)

Kompaktování při nízkém ctx = cache miss zdarma + ztráta kontextu. Autocompact to udělá sám v 95 %.

---

## DECISION

- **green** (< 95 %) → action=work, **NEcompactovat** — autocompact není blízko
- **yellow** (95-98 %) → action=save_min_at_task_end — blíží se autocompact, dokonči task
- **orange** (98-100 %) → action=save_min_now — autocompact hned po dokončení turnu
- **red** (≥ 100 %) → action=let_autocompact_fire — nesahej, nech autocompact

---

## FINAL

→ instance se rozhodne save / compact / work podle action field
