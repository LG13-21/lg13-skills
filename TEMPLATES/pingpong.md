---
name: {{name}}
description: {{description}}. Triggers: '{{trigger1}}', '{{trigger2}}'
status: experimental
user-invocable: true
---

# {{name}}

## PURPOSE

{{purpose}}

Inter-instance communication přes ping-pong JSON protocol (`L:/LG13/runtime/ops/ping_pong/`).

---

## EXECUTION

### 1. Read incoming ping

```bash
ls -t L:/LG13/runtime/ops/ping_pong/{{sender}}_to_{{receiver}}_*.json | head -3
python -c "import json,sys; print(json.dumps(json.load(open(sys.argv[1],encoding='utf-8-sig')),ensure_ascii=False,indent=2))" <file>
```

### 2. Process + write pong (atomic)

```python
import json, time
from pathlib import Path

base = Path("L:/LG13/runtime/ops/ping_pong")
ts = time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime())
me = "{{receiver}}"
them = "{{sender}}"
fname = f"{me}_to_{them}_{ts}.json"

msg = {
    "from": me, "to": them, "ts": ts,
    "round": "R{{round}}",
    "type": "pong",
    "in_reply_to": "<incoming_file>",
    "subject": "{{subject}}",
    "body": "{{body}}",
    "decisions": {},
    "questions_for_other": [],
    "tokens_spent_estimate": 0,
    "context_pct": 0,   # fill from claude_usage_read.py --field session_pct
    "compact_signal": False,
    "priority": "P2"
}
tmp = base / f".{fname}.tmp"
tmp.write_text(json.dumps(msg, ensure_ascii=False, indent=2), encoding="utf-8")
tmp.replace(base / fname)
print(f"SENT: {fname}")
```

### 3. Arm Monitor watcher

```
Monitor: watch L:/LG13/runtime/ops/ping_pong/*_to_{{receiver}}_*.json
On new file → wake → goto step 1
```

---

## RULES

- Atomic write vždy (`.tmp` → `replace()`)
- `context_pct` vždy skutečná hodnota z `claude_usage_read.py --field session_pct`
- `compact_signal: true` pokud context_pct > 70

## RELATED

- Skill `ping-pong` — full protocol spec
- Skill `tmonkey-listen` — Monitor arm pattern
