# /rt — RTG + RTS combo report

## PURPOSE

Spocita oba scores (RTG + RTS) a vyda spojeny report s ship-ready verdict.

## EXECUTION

```bash
python L:/LG13/app/agent/skills/rt_score.py rt [short|long|json|text]
```

Default `text` (Tomovi). JSON pro instance volajici raw compute.

### Output examples

**short** — one-liner pro statusbar / ping-pong body:
```
RTG 0.875/0.95 | RTS 0.500/0.98 | NO-SHIP
```

**text** — Tom-friendly s failing conditions a verdiktem:
```
=== RTG ===
Score: 0.875 / 0.95 (7/8 pass)  [GAP]
Failing conditions:
  - lock2_visual

=== RTS ===
Score: 0.500 / 0.98 (1/8 pass)  [GAP]
Failing conditions:
  - rtg_pass
  - zip_package
  ...

Verdict: NOT SHIP-READY
```

**long** — text + full condition checklist (PASS/FAIL per podminka).

**json** — strojove citelny dict pro instance-to-instance volani:
```json
{
  "rtg": {"score": 0.875, "pass": 7, "total": 8, "threshold": 0.95, "ok": false, "failing": [...]},
  "rts": {"score": 0.5, ...},
  "ship_ready": false,
  "state_ts": "...",
  "state_source": "..."
}
```

### Refresh + override

```bash
python L:/LG13/app/agent/skills/rt_score.py rt --refresh
python L:/LG13/app/agent/skills/rt_score.py rt --set rtg.lock2_visual=true --set rts.rtg_pass=true
```

## VOLANI Z INSTANCE

```python
import subprocess, json
r = subprocess.run(
    ["python", "L:/LG13/app/agent/skills/rt_score.py", "rt", "json"],
    capture_output=True, text=True, timeout=10,
)
data = json.loads(r.stdout)
if data["ship_ready"]:
    # ...
```

## SHIP GATE

```
RTG > 0.95 AND RTS > 0.98  =>  ship_ready: true
```

Cokoliv mensiho = report ukaze ktere podminky drzi blocker.

## RELATED

- `/rtg`, `/rts` — single-metric variants
- Skript: `L:/LG13/app/agent/skills/rt_score.py`
- State: `L:/LG13/runtime/state/rt_conditions.json`
- Spec: `docs/orchestration/RTG_RTS_MATRIX.md` v `legal-ship-2026`
