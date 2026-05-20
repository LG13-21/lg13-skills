---
name: tmonkey-diag
description: "Diagnostika tmonkey atom flow health — pl/stats, atom_lookup, dispatcher routing, kde se ztrácí APPROVED→DISPATCHED, IGNORED ratio, per-instance feed za 24h. Detekuje regresi (DISPATCHED <2% nebo IGNORED >85%). Trigger: 'tmonkey health', 'proč nechodí tmonkey', 'atom dispatcher check', 'tmonkey diag', 'pl_stats'."
user-invocable: true
---

# Tmonkey Monitor — Atom flow health check

## PURPOSE

Detekovat když atom pipeline (`tmonkey → pl_server → classifier → dispatcher → instance stack`) zasekne, over-IGNORE, nebo zahodí atomy mezi APPROVED a DISPATCHED.

---

## EXECUTION

```bash
# 1. PL_SERVER alive + atom totals
curl -s http://localhost:8790/pl/stats

# 2. Per-instance feed last 24h
python L:/LG13/app/agent/atom_lookup.py --instance <name> --since '24h' --tz cest --format markdown --limit 100

# 3. Per-instance feed last 72h (pro porovnání s 24h)
python L:/LG13/app/agent/atom_lookup.py --instance <name> --since '72h' --tz cest --format markdown --limit 100

# 4. Stack file check
ls -la L:/LG13/runtime/stacks/<name>_stack.jsonl L:/LG13/runtime/stacks/_state/<name>_offset.json

# 5. Recent dispatcher run (pokud existuje log)
tail -50 L:/LG13/runtime/logs/atom_dispatcher.log 2>/dev/null
```

---

## CO SE STANE

- `pl/stats` vrátí JSON: `total`, `by_category`, `by_action_status` (NEW/QUEUED/APPROVED/DISPATCHED/IGNORED/POSTPONED)
- `atom_lookup --since` filtruje atomy routované **na danou instanci** za time window
- Stack JSONL zobrazuje co je ready k pickup; offset.json kde je read pointer

---

## HEALTH METRICS

Z `pl/stats`:

| Metric | Healthy | Warning | Alert |
|--------|---------|---------|-------|
| DISPATCHED / total | >5% | 2-5% | <2% |
| IGNORED / total | <70% | 70-85% | >85% |
| APPROVED − DISPATCHED gap | <5% total | 5-15% | >15% (atomy se ztrácí) |
| atom_lookup --since 24h pro `<name>` | >0 (active inst) | 0 (idle inst) | 0 napříč všemi instance = pipeline down |

---

## OUTPUT

Stručný health summary:

```
PL_SERVER: OK / DOWN
TOTAL ATOMS: <N>
DISPATCHED: <N> (<%>) — <STATUS>
IGNORED: <N> (<%>) — <STATUS>
APPROVED→DISPATCHED gap: <N> (<%>) — <STATUS>

Per-instance 24h feed:
- coder: <N>
- legal: <N>
- strat: <N>
...

ROOT CAUSE HYPOTHESIS (pokud ALERT):
- <one-line>
```

---

## RULES

- Read-only diagnostika — žádný restart, žádné mazání atomů
- Pokud ALERT: notify strat přes `instance_queue.py --send --to strat --priority P1`
- Per dispatcher dedup memory `feedback_classifier_atom_dedup.md` (#2906): po dedup fix DISPATCHED rate může legitimně klesnout 30-40% → check baseline před fix
- **Nedělá auto-recovery** — strat rozhoduje co s tím

---

## RELATED

- Memory: `feedback_classifier_atom_dedup.md` (#2906 dedup incident)
- Memory: `reference_atom_lookup_tz.md` (--tz cest awareness)
- Kernel: `L:/Lukasek/CLAUDE.md` TMONKEY TRIGGER section
- Recipe: `L:/Lukasek/recipes/tmonkey.md`

---

## FINAL

→ summary printed → idle, čekej na strat decision.
