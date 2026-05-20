---
name: avengers
description: Team terminator — multiple instances collaborate on shared goal list. Director dispatches, workers execute, sync via ping-pong. Triggers: 'avengers', 'assemble', 'team execute', 'svolat tym', 'team goals', 'multi-instance'
status: experimental
user-invocable: true
---

# avengers

## PURPOSE

Team-version terminator. Víc instancí pracuje na **sdíleném goal listu** paralelně.

Strat = **director** (parsuje goals, rozkládá, dispatchuje).
Coder + Legal = **workers** (berou task, vykonávají, reportují zpět).

Koordinace: ping-pong JSON protokol + `instance_queue.py`.
Strat vidí celkový obraz, Tom vidí progress na issue.

---

## EXECUTION (DIRECTOR — spouští strat)

### 1. Parse master goal list

```bash
gh issue view <NUMBER> --repo <OWNER/REPO> --json body,title,number
```

### 2. Decompose goals → atomic tasks

```python
# Každý goal rozlož na atomic tasks s rolí
tasks = [
    {"id": "T001", "goal": goal_text, "role": "coder", "description": "..."},
    {"id": "T002", "goal": goal_text, "role": "legal", "description": "..."},
    {"id": "T003", "goal": goal_text, "role": "strat", "description": "..."},
]
# Ulož do shared file
Path("L:/LG13/runtime/ops/avengers_tasks.json").write_text(json.dumps(tasks, indent=2))
```

### 3. Dispatch přes ping-pong

```python
# Pro každý task → ping příslušné instanci
for task in tasks:
    send_ping(
        to=task["role"],
        subject=f"[AVENGERS] T{task['id']}: {task['description'][:60]}",
        body=f"## Task {task['id']}\n\n{task['description']}\n\n**Goal:** {task['goal']}\n\n**Expected output:** ...",
        round=f"AV-{task['id']}",
        priority="P1"
    )
```

### 4. Monitor progress

```python
# Čekej na pong (ACK) od workerů
# Při každém ACK: mark task done v avengers_tasks.json
# Při blocker: time-limited question do issue (jako terminator)
```

### 5. Aggregated report

```bash
gh issue comment <NUMBER> --body "## 🦸 [AVENGERS] Progress update

| Task | Role | Status |
|------|------|--------|
| T001 | coder | ✅ done |
| T002 | legal | 🔄 in-progress |

**Director:** strat | **Active workers:** coder, legal"
```

---

## EXECUTION (WORKER — coder/legal)

### 1. Přijmi task ping

```bash
ls -t L:/LG13/runtime/ops/ping_pong/strat_to_<me>_*.json | head -3
```

Rozeznej `[AVENGERS]` prefix v subject.

### 2. Claim task

```bash
python L:/LG13/app/agent/instance_queue.py --claim-next --name <instance>
```

### 3. Execute task

Proveď task popsaný v ping body. Použij tools/subagents dle potřeby.

### 4. Report zpět stratu

```python
send_pong(
    to="strat",
    in_reply_to="<incoming_ping_file>",
    subject=f"[AVENGERS] T{task_id}: DONE — {short_result}",
    body=f"## Result\n\n{result_detail}\n\n## PLAN STATUS\n\n- [x] T{task_id} done",
    round=f"AV-{task_id}"
)
```

---

## TASK LIFECYCLE

```
director → dispatch ping (P1) → worker Monitor detects
worker → claim → in-progress → execute
worker → pong ACK to director
director → mark done → aggregate report
```

---

## EXIT CONDITIONS

- Všechny tasks done (ACK přijaty)
- Tom `STOP AVENGERS` v issue nebo Slack
- Worker hit token budget → director redistribuuje zbývající tasks

---

## RULES

- Director je vždy strat — nikdy coder nebo legal
- Workers nepřeposílají tasky bez director ACK
- Vždy `[AVENGERS]` prefix v subject → snadné filtrování
- Každý task má unikátní ID (T001, T002...) — pro tracking
- Sdílený soubor `avengers_tasks.json` = source of truth pro stav

## RELATED

- Skill `terminator` — single-instance verze (director + worker v jednom)
- Skill `ping-pong` — komunikační protokol
- Skill `team-launcher` — spuštění více instancí najednou
- Skill `heartbeat` — workers posílají heartbeat directoru
- `L:/LG13/app/agent/instance_queue.py` — existující queue infra
