---
name: rr
description: Use when you need a quick status snapshot — current task, token budget, blockers, ping-pong state. Run before /restart or as regular check-in.
---

# rr — Regular Report

Generuje rychlý status report v ~10 řádcích. Vhodný před /restart, jako heartbeat nebo na Tomovu výzvu.

## EXECUTION

```python
import sys, json, time, subprocess
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

inst = 'coder'  # auto-detect
ts = time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())

# Token budget
try:
    r = subprocess.run([sys.executable, 'L:/LG13/app/agent/skills/claude_usage_read.py', '--json'],
        capture_output=True, text=True, timeout=5)
    u = json.loads(r.stdout)
    budget = f"5h:{u.get('session_pct',0):.0f}% | week:{u.get('weekly_all',0):.0f}%"
except:
    budget = '?'

# Queue
try:
    r2 = subprocess.run([sys.executable, 'L:/LG13/app/agent/instance_queue.py', '--check', '--name', inst],
        capture_output=True, text=True, timeout=5)
    q_out = r2.stdout[:100]
except:
    q_out = '?'

# Last ping-pong
try:
    pp_dir = Path('L:/LG13/runtime/ops/ping_pong')
    recent = sorted(pp_dir.glob(f'*_to_{inst}_*.json'), key=lambda f: f.stat().st_mtime)
    last_pp = recent[-1].name if recent else 'none'
except:
    last_pp = '?'

# Notify file
try:
    nfy = json.loads(Path('L:/LG13/runtime/ops/statusline_notify.json').read_text('utf-8'))
    my = nfy.get(inst, {})
    status = my.get('status','') or '-'
    q_open = my.get('q','') or 'none'
except:
    status = '?'; q_open = '?'

print(f"""
╔══ {inst.upper()} REGULAR REPORT — {ts} ══╗
  Status:   {status}
  Open Q:   {q_open}
  Budget:   {budget}
  Queue:    {q_out.strip()[:60]}
  Last PP:  {last_pp}
╚══════════════════════════════════════╝
""")
```

## KDY POUŽÍT

- Před `/restart` nebo `/clear` — rychlá kontrola stavu
- Při Tomově výzvě "jak jsi na tom?"
- Jako součást save-min (volitelně)
- Každých ~30 min v dlouhé session

## RELATED

- `/lg13-skills:save-min` — ukládá stav (párový skill)
- `/lg13-skills:super-start` — restart sequence
- `/lg13-skills:ping-pong` — heartbeat format
