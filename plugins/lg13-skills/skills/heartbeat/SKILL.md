---
name: heartbeat
description: Keep-alive ping-pong loop + keep-awake clause. Triggers: 'heartbeat', 'keep awake', 'stay alive', 'stuj na nohach', 'keep alive'
status: stable
user-invocable: true
---

# heartbeat

## PURPOSE

Udržuje instanci "awake" přes periodický ping-pong se stratem.

Bez heartbeatu instance umlkne a strat neví jestli pracuje nebo spí.
S heartbeatu: každých 15 min zpráva = jistota že instance žije a co dělá.

**Keep-awake clause:** pokud session ticho > 13 min → instance pošle heartbeat sama sobě (file event v ping-pong dir) → Monitor ji probudí → pokračuje v práci. Žádné čekání na příchozí ping.

Kombinuje `ping-pong` protokol + `tmonkey-listen` Monitor arm pattern.

---

## EXECUTION

### 1. Zjisti vlastní instanci

```python
import os
from pathlib import Path
cwd = Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()))
# lg13-coder → coder | legal-ship-2026 → legal | T000_Strat → strat
```

### 2. Arm Monitor na ping-pong dir

Spusť Monitor tool s tímto příkazem:

```bash
python L:/LG13/app/agent/tmonkey_arm.py --instance <inst> --interval 2 --timeout 86400
```

Monitor zachytí `[TMONKEY_NOTIFY]` a `[PINGPONG_NOTIFY]` events.

### 3. Send initial heartbeat

Pošli první heartbeat ihned:

```python
import json, time
from pathlib import Path

base = Path("L:/LG13/runtime/ops/ping_pong")
me = "<instance>"   # coder / strat / legal
them = "strat"      # heartbeaty jdou vždy stratu
ts = time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime())
fname = f"{me}_to_{them}_{ts}.json"

# Přečti budget
import subprocess, sys
r = subprocess.run([sys.executable, 'L:/LG13/app/agent/skills/claude_usage_read.py', '--field', 'session_pct'],
    capture_output=True, text=True, timeout=5)
ctx_pct = int(r.stdout.strip()) if r.returncode == 0 else 0

msg = {
    "from": me, "to": them, "ts": ts,
    "round": "HEARTBEAT",
    "type": "ping",
    "subject": f"[HEARTBEAT] {me} {time.strftime('%H:%M')} — keep alive",
    "body": f"## PLAN STATUS — {me.upper()}\n\n- [~] heartbeat running\n\n### Budget state\n- session: {ctx_pct}%",
    "decisions": {}, "questions_for_other": [],
    "tokens_spent_estimate": 50,
    "context_pct": ctx_pct,
    "compact_signal": ctx_pct > 70,
    "priority": "P3"
}
tmp = base / f".{fname}.tmp"
tmp.write_text(json.dumps(msg, ensure_ascii=False, indent=2), encoding="utf-8")
tmp.replace(base / fname)
print(f"HEARTBEAT sent: {fname}")
```

### 4. Loop — každých 15 minut

```python
import time

INTERVAL = 15 * 60   # 15 minut
last_hb = time.time()

while True:
    now = time.time()
    if now - last_hb >= INTERVAL:
        # pošli heartbeat (kód z kroku 3)
        send_heartbeat(me, them, current_task)
        last_hb = now
    # zpracuj příchozí ping-pong soubory
    process_incoming_pings(me)
    time.sleep(30)
```

### 5. Keep-awake clause

Pokud session ticho > 13 min (bez Monitor eventu) → pošli heartbeat sám sobě:

```python
# Soubor sám sobě = Monitor event → probudí session
self_ping_fname = f"{me}_to_{me}_{ts}.json"
# body: "[SELF-WAKE] heartbeat keepalive"
```

### 6. Stop condition

Heartbeat se zastaví na:
- Explicitní `STOP HEARTBEAT` v příchozím ping-pongu
- Session end (Monitor arm vypne se sám)
- `context_pct > 90` → `compact_signal: true` + čekej na /compact

---

## OUTPUT

```
[HEARTBEAT] coder 08:15 — implementing skill X
[HEARTBEAT] coder 08:30 — idle, waiting for strat
```

---

## RULES

- Interval: 15 min (nikdy nečekej víc bez oznámení)
- Body: jen PLAN STATUS + budget state — nic víc
- Subject pattern PŘESNÝ: `[HEARTBEAT] <instance> <HH:MM> — <1 řádek>`
- `context_pct` vždy ze skutečného `claude_usage_read.py` — nikdy odhad
- Pokud `compact_signal: true` → zastav heartbeat do /compact + restart

## RELATED

- Skill `ping-pong` — full protokol pro inter-instance dialog
- Skill `tmonkey-listen` — persistent Monitor arm (stejný pattern)
- `L:/LG13/app/agent/heartbeat_writer.py` — existující heartbeat infra
- Memory: `feedback_15min_heartbeat` — proč 15 minut
