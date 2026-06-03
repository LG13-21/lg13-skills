---
name: compact-check
description: "Soft/Hard compact range checker. Vrátí zone (green/soft/hard/over) + action + recommendation. Per-instance thresholds. Používej v loop protokolu over 200k."
user-invocable: true
---

# compact-check — Soft/Hard Context Zone Checker

## PURPOSE

Implementuje Tomův loop protokol: **over 200k → remember → team ping-pong → autocompact → continue**.

Každá instance má vlastní thresholds. Skill řekne co dělat teď.

---

## ZONES

| Zone   | Tokeny (strat/legal) | Action        | Urgency |
|--------|----------------------|---------------|---------|
| green  | < 180k               | work          | 0       |
| soft   | 180k – 230k          | plan-compact  | 1       |
| hard   | 230k – 250k          | compact-now   | 2       |
| over   | > 250k               | emergency     | 3       |

**Per-instance thresholds** (strat/legal=180k/230k/250k, coder=160k/210k/230k, ostatní=170k/220k/250k).
Editovatelné přímo ve skriptu: `scripts/compact_check.py` → `INSTANCE_THRESHOLDS`.

---

## EXECUTION

```bash
python C:/Users/tom/.claude/plugins/marketplaces/lg13/plugins/lg13-skills/skills/compact-check/scripts/compact_check.py \
  --ctx-now <N> [--instance <name>] [--json]
```

`--ctx-now` = aktuální počet tokenů (z `/context` nebo `claude_usage_read.py`).
`--instance` = auto-detekuje z CWD pokud chybí.
`--json` = strojový výstup pro loop skripty.

---

## LOOP PROTOKOL (Tom 2026-05-26)

Při každém deep-read batchi nebo pravidelném checku:

```
1. compact-check --ctx-now <N> --json
2. zone == 'green'  → work, žádná akce
3. zone == 'soft'   → /remember + ping-pong strat (compact_signal=True) + dokonči turn
4. zone == 'hard'   → /remember + ping-pong strat + IHNED save-min + nech autocompact spustit
5. zone == 'over'   → P0 ping strat, compact emergency
```

**PreCompact hook** (`C:/Users/tom/.claude/hooks/pre-compact-loop.py`) dělá kroky 3-4 automaticky.

---

## VÝSTUP (--json)

```json
{
  "instance": "strat",
  "ctx_now": 195000,
  "pct": 78.0,
  "zone": "soft",
  "action": "plan-compact",
  "recommendation": "Soft limit. Dokonči aktuální task, pak save-min + ping-pong...",
  "compact_signal": true,
  "urgency": 1,
  "thresholds": { "soft": 180000, "hard": 230000, "window": 250000 },
  "remaining": {
    "to_soft_tokens": 0,
    "to_hard_tokens": 35000,
    "to_window_tokens": 55000,
    "turns_to_soft": 0,
    "turns_to_hard": 7.0,
    "turns_remaining": 11.0
  }
}
```

---

## RULES

- Claude NEpočítá sám — deleguje skriptu
- `--ctx-now` je povinný
- Výsledek `action` je závazný pro loop protokol
- `compact_signal: true` = zahrnout do ping-pong `compact_signal` pole
- `urgency >= 2` = save-min IHNED bez dalšího work

---

## INTEGRACE DO INIT MIN / SAVE MIN

Po každém deep-read batchi (krok 5 init min):

```bash
python compact_check.py --ctx-now $(python claude_usage_read.py --field session_tokens) --instance strat
```

Nebo jednoduše: zavolej skill, přečti `action`, reaguj.

---

## RELATED

- Skill `save-min` — spusť když action=plan-compact nebo hard
- Skill `ping-pong` — odešli s compact_signal=true
- Skill `remember:remember` — handoff note před compactem
- Hook `C:/Users/tom/.claude/hooks/pre-compact-loop.py` — auto při autocompact
- Script `edge_calc.py` — starší per-turn edge (nadále platný pro save/work rozhodnutí)
