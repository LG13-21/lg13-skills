---
name: tmonkey-arm
description: "Arm Monitor watcher na <inst>_stack.jsonl mtime change → notification → wake instance pro pickup. Bez polling, bez tokenů. Trigger: 'tmonkey arm', 'arm watcher', 'pingpong arm'."
user-invocable: true
---

# Tmonkey-Arm — Stack file Monitor watcher

## PURPOSE

Arm Claude Code Monitor tool s persistent watcher na stack file (`L:/LG13/runtime/stacks/<inst>_stack.jsonl`). Při mtime change → notification → wake instance → pickup nových atomů přes stack_reader. Žádný polling.

---

## EXECUTION

### Arm watcher (single-shot, runs in background until disarm)

```bash
cd /l/LG13/runtime/stacks && last=$(stat -c %Y <inst>_stack.jsonl 2>/dev/null || echo 0)
while true; do
  cur=$(stat -c %Y <inst>_stack.jsonl 2>/dev/null || echo 0)
  if [ "$cur" != "$last" ] && [ "$cur" != "0" ]; then
    echo "STACK_CHANGED <inst> mtime=$(date -u -d @$cur +%H:%M:%SZ)"
    last=$cur
  fi
  sleep 30
done
```

Spustit přes `Monitor tool` s `persistent: true` — každý `STACK_CHANGED` line = task-notification → wake instance.

### Disarm

```
TaskList → najdi running monitor → TaskStop <task_id>
```

---

## CO SE STANE

- Monitor tool spustí while-loop on background
- Každých 30s checkne `stat -c %Y` na stack file
- Při mtime change emit `STACK_CHANGED` line → notification arrives v hostí instanci
- Instance reaguje: spustí stack_reader pickup

---

## OUTPUT

Per change event: `STACK_CHANGED <inst> mtime=<time>` line v Monitor stdout. Background, no immediate user output.

---

## RULES

- **Polling interval ≥30s** — méně = cache thrash + zbytečný I/O
- **Persistent: true** v Monitor — bez toho process dies on first event
- **Disarm při end of session** (Monitor přežije /clear ale ne reload)
- **Per-instance** — coder watcher ≠ legal watcher, separate Monitor task
- Kombinuje s `ping-pong` skill — same notification mechanism, different file pattern

---

## USE CASES

- coder čeká na strat task přes stack → arm tmonkey-arm + idle work
- legal čeká na atom z OSPOD docs → arm + processing previous batch
- post-tmonkey trigger: arm watcher na další iteration stack pickup

---

## RELATED

- `ping-pong` skill — stejný Monitor pattern pro `*_to_<me>_*.json` files
- `tmonkey` skill — manual one-shot stack_reader pickup
- `tmonkey-monitor` skill — diagnostics atom flow health

---

## FINAL

→ Monitor armed → instance může pracovat na jiných tasks → atom arrival auto-wake
